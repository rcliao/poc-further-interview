FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files from backend directory (build context is repo root)
COPY backend/pyproject.toml ./

# Install Python dependencies system-wide (no virtual env needed in Docker)
RUN uv pip install --system -r pyproject.toml

# Copy application code from backend directory
COPY backend/ .

# Expose port
EXPOSE 8000

# Run migrations, seed knowledge, and start gunicorn
CMD sh -c "python manage.py migrate && python manage.py seed_knowledge && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"
