# Minimal Dockerfile for SkillBridge app (for local testing)
FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
# Copy application code
COPY . /app

# Create non-root user for better security
RUN useradd --create-home appuser && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expose app port and optional Prometheus port
EXPOSE 5000 8000

USER appuser

# Use python entry directly; in production consider using gunicorn
CMD ["python", "app.py"]
