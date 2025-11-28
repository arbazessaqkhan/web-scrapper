# Indian Government Tender Scraper

This project scrapes active tenders from the [Central Public Procurement Portal](https://eprocure.gov.in/cppportal/staticContent/ActiveTenders.jsp) and enriches the data using the Meta Llama 3.2 LLM via OpenRouter.

## Overview

The tool fetches the latest active tenders, extracts key details (Title, Reference Number, Ministry, Closing Date), and uses an LLM to categorize them into sectors and extract estimated values and contract types. This structured data is valuable for analyzing public infrastructure trends and opportunities.

## Features

- **Automated Scraping**: Fetches active tenders from `eprocure.gov.in`.
- **Session Handling**: Manages cookies and sessions to access dynamic pages.
- **AI Enrichment**: Uses Llama 3.2 (via OpenRouter) to extract:
    - **Sector**: (e.g., Transport, Health, IT)
    - **Estimated Value**: (in INR)
    - **Location**: (State)
    - **Contract Type**: (Works, Goods, Services)
- **Robustness**: Handles API rate limits and missing data gracefully.
- **Output**: Saves clean, structured data to `output/tenders_clean.csv`.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Ensure `config.yaml` is present with your OpenRouter API key:
    ```yaml
    API_KEY: "your_api_key_here"
    BASE_URL: "https://eprocure.gov.in/eprocure/app"
    # ... other settings
    ```

3.  **Run the Scraper**:
    ```bash
    python scraper.py
    ```

## Output

The script generates `output/tenders_clean.csv` with the following columns:
- `title`
- `reference_number`
- `ministry`
- `closing_date`
- `sector`
- `estimated_value_inr`
- `location_state`
- `contract_type`

## UI Dashboard (Showcase)

To view the data in an interactive dashboard:

```bash
streamlit run app.py
```

This will launch a web interface where you can:
- View key metrics (Total Value, Top Sectors).
- Visualize data with charts.
- Trigger a new scrape directly from the UI.

## Logs

Check `scraping.log` for execution details and any errors.
