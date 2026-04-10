---
title: Fake News Detection Tool
emoji: 🛡️
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
---

# Fake News Detection and Verification Tool

A complete Minimum Viable Product (MVP) resolving Infosys Springboard Internship Milestone 4. This tool analyzes news articles, flags potential fake news leveraging AI (DistilBERT), extracts checkable claims via NLP (spaCy), highlights suspicious phrasing for explainability, and verifies claims utilizing the Google Fact Check API.

## Features
- **AI Prediction**: Classifies article as `REAL` or `FAKE`.
- **Claim Extraction**: Uses NLP to securely extract meaningful claims.
- **Explainability module**: Spots and highlights suspicious terminology (`"miracle"`, `"secret cure"`).
- **Fact checking API**: Integrates dynamically with Google Fact Check API.
- **Admin Dashboard**: Manages trusted sources securely via JSON and displays simulated platform metrics.

## Setup Locally

1. **Clone the repository.**
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Environment setup:** Copy `.env.example` to `.env` and verify the `GOOGLE_FACTCHECK_API_KEY`.
4. **Run via Flask:** 
```bash
python app.py
```
> *(Port defaults to 5000 if using flask debug, 7860 using docker)*

5. **Run via Streamlit (Fallback if needed):**
```bash
streamlit run app.py --server.port 7860
```

## Setup via Docker

1. **Build the container:**
```bash
docker build -t fakenews-app .
```
2. **Run the container:**
```bash
docker run -p 7860:7860 --env-file .env.example fakenews-app
```
*(Or use `docker-compose up -d`)*

## Hugging Face Spaces / Streamlit Cloud

This repository is optimized for deployment to Hugging Face Spaces using the Docker SDK. The `app_port` is mapped to `7860` in the Dockerfile and Gunicorn setup, meeting the environment requirements. To deploy:
1. Create a HF Space (Select Docker)
2. Push all files.
3. Add `GOOGLE_FACTCHECK_API_KEY` to repository secrets. 

## Included Tech-Stack
* Python
* Flask / Streamlit (Dual-App Mode)
* Hugging Face Transformers (`distilbert-base-uncased-finetuned-sst-2-english`)
* SpaCy (`en_core_web_sm`)
* HTML5 / CSS3 / Bootstrap 5 / Vanilla JS
* Docker / Gunicorn
