FROM python:3.11-slim

WORKDIR /app

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
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://foodflow:password@db:5432/foodflow
ENV REDIS_URL=redis://redis:6379/0

# Expose ports
EXPOSE 8200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8200/health || exit 1

# Default command (FastAPI server)
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8200", "--reload"]