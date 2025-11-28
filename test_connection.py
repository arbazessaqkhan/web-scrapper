import requests
from bs4 import BeautifulSoup

def test_post_request():
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://eprocure.gov.in',
        'Referer': 'https://eprocure.gov.in/eprocure/app?page=FrontEndListTendersbyDate&service=page'
    }
    
    try:
        print("Visiting page to get cookies and tokens...")
        url = "https://eprocure.gov.in/eprocure/app?page=FrontEndListTendersbyDate&service=page"
        response = session.get(url, headers=headers)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract hidden fields
        form = soup.find('form', {'id': 'ListTendersbyDate'})
        if not form:
            print("Form not found!")
            return

        data = {}
        for input_tag in form.find_all('input', {'type': 'hidden'}):
            name = input_tag.get('name')
            value = input_tag.get('value')
            if name:
                data[name] = value
        
        # Add the submit button simulation
        # The link is: javascript:tapestry.form.submit('ListTendersbyDate', 'LinkSubmit_0');
        # This usually sets 'submitname' to 'LinkSubmit_0' (or similar mechanism in Tapestry)
        # In standard Tapestry 4, it might be just the event parameter.
        # Let's try setting 'submitname' or just passing the button name if it were a submit input.
        # But here it's a link.
        # Based on the form hidden fields:
        # <input type="hidden" name="submitmode" value="" />
        # <input type="hidden" name="submitname" value="" />
        
        data['submitmode'] = 'submit'
        data['submitname'] = 'LinkSubmit_0'
        
        print("Sending POST request...")
        post_url = "https://eprocure.gov.in/eprocure/app" 
        # The action is /eprocure/app
        
        resp2 = session.post(post_url, data=data, headers=headers)
        print(f"POST Status: {resp2.status_code}")
        
        with open("debug_post_result.html", "wb") as f:
            f.write(resp2.content)
        print("Saved debug_post_result.html")
        
        # Check for tenders
        soup2 = BeautifulSoup(resp2.content, 'html.parser')
        if "No Tenders found" in soup2.get_text():
            print("Still no tenders found.")
        else:
            print("Success? Checked for 'No Tenders found' and didn't find it (or found tenders).")
            tables = soup2.find_all('table', {'class': 'list_table'})
            print(f"Found {len(tables)} list_tables.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_post_request()
