FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt




# Copy the entire project
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
