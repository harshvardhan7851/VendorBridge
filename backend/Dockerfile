# =============================================================================
# VendorBridge Backend - Dockerfile
# Base Image: Python 3.11 slim
# =============================================================================

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for psycopg2/asyncpg and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# (In development, this is overridden by the volume mount in docker-compose.yml)
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Default command — overridden in docker-compose.yml for development (--reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
