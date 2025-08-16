#!/bin/bash

# Exit on any error for debugging
set -e

# Enable debugging output
set -x

# Get the actual project directory (this script should be in .devcontainer/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Setting SELinux contexts for project: $PROJECT_DIR"

# Check if SELinux is enabled
if command -v getenforce >/dev/null 2>&1; then
    SELINUX_STATUS=$(getenforce 2>/dev/null || echo "Disabled")
    echo "SELinux status: $SELINUX_STATUS"
    
    if [ "$SELINUX_STATUS" = "Disabled" ]; then
        echo "SELinux is disabled, skipping context setting"
        exit 0
    fi
else
    echo "SELinux tools not found, assuming SELinux is disabled"
    exit 0
fi

# Check if we have sudo access
if ! sudo -n true 2>/dev/null; then
    echo "Warning: No sudo access available"
    # Try without sudo (might work in some containers)
    echo "Attempting to run without sudo..."
fi

# Function to safely set SELinux context
set_context() {
    local path="$1"
    local context="$2"
    
    if [ -e "$path" ]; then
        echo "Setting context $context on $path"
        if sudo -n true 2>/dev/null; then
            sudo chcon -R -t "$context" "$path" 2>/dev/null || {
                echo "Warning: Failed to set context on $path"
                return 1
            }
        else
            chcon -R -t "$context" "$path" 2>/dev/null || {
                echo "Warning: Failed to set context on $path (no sudo)"
                return 1
            }
        fi
    else
        echo "Path $path does not exist, skipping"
    fi
}

# Set the container_file_t context for the entire project
set_context "$PROJECT_DIR" "container_file_t"

# Specifically handle common directories and files
set_context "$PROJECT_DIR/.devcontainer" "container_file_t"
set_context "$PROJECT_DIR/.git" "container_file_t"

# Set contexts for file patterns (only if files exist)
for pattern in "*.py" "*.txt" "*.json"; do
    if ls "$PROJECT_DIR"/$pattern 1> /dev/null 2>&1; then
        set_context "$PROJECT_DIR"/$pattern "container_file_t"
    fi
done

# Set contexts for any config directories
if [ -d "$PROJECT_DIR/config" ]; then
    set_context "$PROJECT_DIR/config" "container_file_t"
fi

# Enable container to execute content (this might fail in some environments)
echo "Setting SELinux boolean for container execution"
if sudo -n true 2>/dev/null; then
    sudo setsebool -P container_execute_content on 2>/dev/null || {
        echo "Warning: Could not set container_execute_content boolean"
    }
else
    setsebool -P container_execute_content on 2>/dev/null || {
        echo "Warning: Could not set container_execute_content boolean (no sudo)"
    }
fi

echo "SELinux contexts set successfully for VSCode Docker container"
echo "Project directory: $PROJECT_DIR"