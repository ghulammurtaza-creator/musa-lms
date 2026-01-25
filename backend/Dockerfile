# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint scripts executable
RUN chmod +x /app/docker-entrypoint.sh /app/fly-entrypoint.sh

# Expose port
EXPOSE 8000

# Use fly-entrypoint for production (handles migrations)
# For local development, docker-compose overrides this
CMD ["/app/fly-entrypoint.sh"]
