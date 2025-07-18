# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
