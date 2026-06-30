---
title: Fake News Detection Tool
emoji: 🛡️
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 8501
---

# Fake News Detection and Verification Tool

A complete tool for analyzing news articles, flagging potential fake news leveraging AI (Heuristic Rule-Based NLP), extracting checkable claims via NLP (spaCy), highlighting suspicious phrasing for explainability, and verifying claims utilizing the Google Fact Check API. 

## Features
- **AI Prediction**: Classifies article as `REAL` or `FAKE`.
- **Claim Extraction**: Uses NLP to securely extract meaningful claims.
- **Explainability module**: Spots and highlights suspicious terminology (`"miracle"`, `"secret cure"`).
- **Fact checking API**: Integrates dynamically with Google Fact Check API.
- **Admin Dashboard**: Manages trusted sources securely via JSON and displays analytics.
- **User Feedback**: Collects and stores user feedback on prediction accuracy.

## Setup Locally

1. **Clone the repository.**
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Environment setup:** Copy `.env.example` to `.env` and set your `GOOGLE_FACTCHECK_API_KEY`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD`.
   - Alternatively, add your Google Fact Check API key in `.streamlit/secrets.toml`.
4. **Run via Streamlit:**
```bash
streamlit run app.py
```

## Setup via Docker

1. **Build the container:**
```bash
docker build -t fakenews-app .
```
2. **Run the container:**
```bash
docker run -p 8501:8501 --env-file .env.example fakenews-app
```
*(Or use `docker-compose up -d`)*

## Testing

Run the test suite using pytest:
```bash
python -m pytest tests/ -v
```

## Included Tech-Stack
* Python
* Streamlit
* Fast Heuristic NLP logic
* SpaCy (`en_core_web_sm`)
* Docker
