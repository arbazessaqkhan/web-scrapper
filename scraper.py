import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import logging
import json
import time
import os
import re

# Setup logging
logging.basicConfig(
    filename='scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

try:
    import streamlit as st
except ImportError:
    st = None

def load_config():
    # Priority 1: Streamlit Secrets (for Cloud Deployment)
    try:
        if st is not None and hasattr(st, 'secrets') and 'API_KEY' in st.secrets:
            return st.secrets
    except Exception:
        pass # Fallback to local config if secrets are not found/configured
    
    # Priority 2: Local config.yaml
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
            
    # Fallback
    return {}

CONFIG = load_config()

def get_llm_enrichment(tender_text):
    """
    Enrich tender data using Llama 3.2 via OpenRouter.
    """
    prompt = f"""
    Extract structured data from the following tender description.
    Return ONLY a valid JSON object with these keys:
    - sector: One of [Transport, Water, Health, Education, IT/Digital, Energy, Building, Other]
    - estimated_value_inr: Number (or null if not found)
    - location_state: Indian state name or "All India"
    - contract_type: One of [Works, Goods, Services, null]

    Tender Text:
    {tender_text}
    """

    headers = {
        "Authorization": f"Bearer {CONFIG['API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "TenderScraper"
    }
    
    data = {
        "model": CONFIG['MODEL'],
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # Rate limit handling (simple sleep)
        time.sleep(1) 
        
        response = requests.post(
            CONFIG['OPENROUTER_URL'],
            headers=headers,
            data=json.dumps(data),
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            # Attempt to clean markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
            
            return json.loads(content)
        elif response.status_code == 429:
            logging.warning("Rate limit hit. Waiting 5 seconds...")
            time.sleep(5)
            return None # Skip for now or retry logic could be added
        else:
            logging.error(f"LLM API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"LLM Exception: {e}")
        return None

def scrape_tenders():
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://eprocure.gov.in',
        'Referer': 'https://eprocure.gov.in/eprocure/app?page=FrontEndListTendersbyDate&service=page'
    }

    try:
        logging.info("Initializing session...")
        # 1. Visit page to get cookies and tokens
        url = "https://eprocure.gov.in/eprocure/app?page=FrontEndListTendersbyDate&service=page"
        response = session.get(url, headers=headers)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract hidden fields
        form = soup.find('form', {'id': 'ListTendersbyDate'})
        if not form:
            logging.error("Form 'ListTendersbyDate' not found.")
            return

        data = {}
        for input_tag in form.find_all('input', {'type': 'hidden'}):
            name = input_tag.get('name')
            value = input_tag.get('value')
            if name:
                data[name] = value
        
        # Simulate clicking "Closing within 7 days"
        data['submitmode'] = 'submit'
        data['submitname'] = 'LinkSubmit_0'
        
        logging.info("Fetching tenders (Closing within 7 days)...")
        post_url = "https://eprocure.gov.in/eprocure/app"
        resp2 = session.post(post_url, data=data, headers=headers)
        
        if resp2.status_code != 200:
            logging.error(f"Failed to fetch tenders. Status: {resp2.status_code}")
            return

        soup2 = BeautifulSoup(resp2.content, 'html.parser')
        
        # Find the data table
        # It usually has class 'list_table' and contains "Title and Ref.No"
        target_table = None
        for table in soup2.find_all('table', {'class': 'list_table'}):
            if "Title and Ref.No" in table.get_text():
                target_table = table
                break
        
        if not target_table:
            logging.error("Could not find tender table in response.")
            return

        tenders = []
        rows = target_table.find_all('tr')
        
        logging.info(f"Found {len(rows)} rows in table (including headers). Processing...")
        
        count = 0
        for row in rows:
            # Skip rows that don't look like data rows (e.g. headers, footers)
            # Data rows usually have a class like 'even' or 'odd' or just specific cells
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
                
            # Check if this is a header row
            if "Title and Ref.No" in row.get_text():
                continue
                
            # Extract fields
            # 0: S.No
            # 1: e-Published Date
            # 2: Bid Submission Closing Date
            # 3: Tender Opening Date
            # 4: Title and Ref.No./Tender ID
            # 5: Organisation Chain
            
            try:
                closing_date = cols[2].get_text(strip=True)
                
                title_cell = cols[4]
                title_link = title_cell.find('a')
                if title_link:
                    title = title_link.get_text(strip=True)
                    # Ref no is text after link
                    full_text = title_cell.get_text(strip=True)
                    # Remove title from full text to get ref no
                    ref_no = full_text.replace(title, "").strip()
                else:
                    title = title_cell.get_text(strip=True)
                    ref_no = "N/A"
                
                ministry = cols[5].get_text(strip=True)
                
                tender_data = {
                    "title": title,
                    "reference_number": ref_no,
                    "ministry": ministry,
                    "closing_date": closing_date
                }
                
                logging.info(f"Processing tender: {title[:50]}...")
                
                # LLM Enrichment
                description_proxy = f"Title: {title}. Ministry/Organisation: {ministry}."
                
                enrichment = get_llm_enrichment(description_proxy)
                if enrichment:
                    tender_data.update(enrichment)
                else:
                    tender_data.update({
                        "sector": None,
                        "estimated_value_inr": None,
                        "location_state": None,
                        "contract_type": None
                    })
                
                tenders.append(tender_data)
                count += 1
                
                if count >= 10: # Limit for demo
                    break
                    
            except Exception as e:
                logging.warning(f"Error parsing row: {e}")
                continue
        
        # Save to CSV
        if tenders:
            os.makedirs('output', exist_ok=True)
            df = pd.DataFrame(tenders)
            df.to_csv('output/tenders_clean.csv', index=False)
            logging.info(f"Successfully saved {len(tenders)} tenders to output/tenders_clean.csv")
        else:
            logging.warning("No tenders extracted.")

    except Exception as e:
        logging.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    scrape_tenders()
