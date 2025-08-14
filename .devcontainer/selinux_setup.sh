#!/bin/bash

# Get the actual project directory (this script should be in .devcontainer/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting SELinux contexts for project: $PROJECT_DIR"

# Set the container_file_t context for the entire project
sudo chcon -R -t container_file_t "$PROJECT_DIR"

# Specifically handle common directories and files
sudo chcon -R -t container_file_t "$PROJECT_DIR/.devcontainer" 2>/dev/null || true
sudo chcon -R -t container_file_t "$PROJECT_DIR/.git" 2>/dev/null || true
sudo chcon -t container_file_t "$PROJECT_DIR"/*.py 2>/dev/null || true
sudo chcon -t container_file_t "$PROJECT_DIR"/*.txt 2>/dev/null || true
sudo chcon -t container_file_t "$PROJECT_DIR"/*.json 2>/dev/null || true

# Set contexts for any config directories
if [ -d "$PROJECT_DIR/config" ]; then
    sudo chcon -R -t container_file_t "$PROJECT_DIR/config"
fi

# Enable container to execute content
sudo setsebool -P container_execute_content on

# Also set the container_file_t context with :Z option for the bind mount
# This will be handled by Docker, but we ensure it here
sudo chcon -R -t container_file_t "$PROJECT_DIR"

echo "SELinux contexts set successfully for VSCode Docker container"
echo "Project directory: $PROJECT_DIR"