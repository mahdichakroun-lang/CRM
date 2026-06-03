# ── Backend Dockerfile ──
# Python 3.11 slim image for FastAPI + SQLAlchemy + MySQL
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for MySQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
