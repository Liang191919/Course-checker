# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY app/ ./app/

# Environment variables should be passed at runtime:
# docker run --env-file .env course-checker

# Run the bot with unbuffered output
CMD ["python", "-m", "app.main"]
