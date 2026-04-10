FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Pre-download and cache the HuggingFace model at build time
# This avoids the slow first-run download when user clicks Analyze
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='jy46604790/Fake-News-Bert-Detect')"

# Copy the entire project
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
