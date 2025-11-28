# Deployment Guide

The easiest way to deploy this Streamlit app for free is using **Streamlit Cloud**.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account.
2.  **Push Code**: Push this project to a new GitHub repository.

## Steps to Deploy on Streamlit Cloud

1.  **Upload to GitHub**:
    - Create a new repository on GitHub (e.g., `tender-scraper-showcase`).
    - Upload all files (`app.py`, `scraper.py`, `requirements.txt`, `config.yaml`, `README.md`) to this repository.
    - *Note*: Be careful with `config.yaml` if it contains your private API Key. For production, it's better to use **Secrets** (see below).

2.  **Sign up for Streamlit Cloud**:
    - Go to [share.streamlit.io](https://share.streamlit.io/).
    - Sign in with your GitHub account.

3.  **Create App**:
    - Click **"New app"**.
    - Select your GitHub repository (`tender-scraper-showcase`).
    - Select the branch (usually `main`).
    - Select the main file path: `app.py`.
    - Click **"Deploy!"**.

4.  **Configure Secrets (Crucial for API Key)**:
    - Once deployed, the app might fail because it can't find the API key if you didn't upload `config.yaml` (which is good practice).
    - Go to your App Dashboard on Streamlit Cloud.
    - Click the **Settings** menu (three dots) -> **Settings** -> **Secrets**.
    - Add your secrets in TOML format:
      ```toml
      API_KEY = "your-openrouter-api-key-here"
      BASE_URL = "https://eprocure.gov.in/eprocure/app"
      OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
      MODEL = "meta-llama/llama-3.2-3b-instruct:free"
      ```
    - *Code Update*: You might need to slightly modify `scraper.py` to read from `st.secrets` if `config.yaml` is missing, or ensure `config.yaml` is uploaded.
    
    **Quick Fix for Demo**: 
    If you just want to show it quickly, you can upload `config.yaml` to GitHub. Just remember to **delete the repo or revoke the key** after the interview/demo.

## Alternative: Render.com

1.  Create a new **Web Service** on [Render](https://render.com/).
2.  Connect your GitHub repo.
3.  Build Command: `pip install -r requirements.txt`
4.  Start Command: `streamlit run app.py --server.port $PORT`
5.  Add Environment Variables for your API keys.
