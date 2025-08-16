# Use official Python base image
FROM python:3.11-slim

# Set working directory to match devcontainer.json
WORKDIR /workspaces/microblog

# Install system build tools (adjust if you need others)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately to cache layers
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Do not copy the source code here — VS Code mounts it live
# COPY . .  <-- intentionally omitted

# Expose Flask's default port
EXPOSE 5000

# Optional default command (VS Code can override)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
