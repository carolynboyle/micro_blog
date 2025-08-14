FROM python:3.11

# Ensure we have bash for conditional checks
SHELL ["/bin/bash", "-c"]

WORKDIR /workspace

# Install git, build tools, and sudo
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with matching UID/GID to host user
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID devuser \
    && useradd --uid $USER_UID --gid $USER_GID --shell /bin/bash --create-home devuser \
    && echo devuser ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/devuser \
    && chmod 0440 /etc/sudoers.d/devuser

# Install common Python packages that are likely needed
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir flask python-dotenv

# Change ownership of the workspace to devuser
RUN chown -R devuser:devuser /workspace

USER devuser

# Expose the Flask port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=microblog.app
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Command to run the Flask application
CMD ["bash", "-c", "cd /workspace && if [ -f requirements.txt ]; then pip install --user -r requirements.txt 2>/dev/null || sudo pip install -r requirements.txt; fi && flask run"]