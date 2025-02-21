# Use Redis as base image
FROM redis:6.2

# Install system dependencies
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git supervisor

# Set working directory
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Create a virtual environment
RUN python3 -m venv /app/venv

# Activate the virtual environment and install dependencies
RUN /app/venv/bin/pip install --upgrade pip && /app/venv/bin/pip install -r /app/requirements.txt

# Copy supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose API port
EXPOSE 7860

# Start Redis, Celery, and FastAPI using supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
