# Use the latest Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  postgresql-client \
  build-essential \
  libpq-dev \
  gettext \
  curl \
  pkg-config \
  libcairo2-dev \
  libffi-dev \
  libpango1.0-dev \
  libgdk-pixbuf-xlib-2.0-dev \
  libjpeg-dev \
  libpng-dev \
  && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8090

# Default command
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "config.wsgi"]
