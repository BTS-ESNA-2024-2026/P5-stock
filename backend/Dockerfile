# Use Python 3.11 Alpine image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    mariadb-connector-c-dev \
    pkgconfig

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend code
COPY . .

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=src
ENV PYTHONUNBUFFERED=1

# Run gunicorn in production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src:create_app()"]
