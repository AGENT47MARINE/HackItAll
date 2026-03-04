# Use the official Microsoft Playwright image based on Ubuntu Jammy
# This image comes pre-installed with all necessary C++ dependencies and browser binaries
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy only the requirements first to cache the layer
COPY requirements.txt .

# Install Python dependencies
# Adding playwright-stealth explicitly to ensure it is installed if not yet in requirements.txt
RUN pip install -r requirements.txt && pip install playwright-stealth

# Ensure the Playwright browsers are properly installed (the base image usually handles this, but it's safe to enforce)
RUN playwright install chromium

# Copy the entire backend application into the container
# Note: Ensure .dockerignore is configured to ignore the /web frontend, /venv, and local SQLite DBs
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Set Environment Variables
# In production on AWS, you should pass AI_PROVIDER=bedrock during container startup
ENV PYTHONUNBUFFERED=1
ENV AI_PROVIDER=ollama 

# Start the Uvicorn ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
