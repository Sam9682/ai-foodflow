FROM python:3.11-slim

WORKDIR /app

# Set environment variables to prevent debconf errors
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for logs, images, and temp files
RUN mkdir -p /app/logs /app/images /tmp

# Set environment variables
ENV PYTHONPATH=/app/src
ENV DATABASE_URL=postgresql://foodflow:password@db:5432/foodflow
ENV REDIS_URL=redis://redis:6379/0

# Expose ports
EXPOSE ${HTTPS_PORT:-6999}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${HTTPS_PORT:-6999}/health || exit 1

# Default command (FastAPI server with SSL support)
CMD uvicorn app.api.main:app --host 0.0.0.0 --port ${HTTPS_PORT:-6999} --ssl-keyfile=${SSL_KEYFILE:-} --ssl-certfile=${SSL_CERTFILE:-} --reload