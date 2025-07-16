# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_cloud.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_cloud.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for Streamlit
EXPOSE 8501

# Set the default command
CMD ["streamlit", "run", "streamlit_cloud_app.py", "--server.port=8501", "--server.address=0.0.0.0"] 