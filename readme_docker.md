# Microblog Development with Docker

This project includes a complete Docker development environment that works consistently across all platforms.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd microblog
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Open http://localhost:5000 in your browser
   - The app will auto-reload when you make changes

## Development Commands

| Command | Description |
|---------|-------------|
| `docker-compose up --build` | Build and start the development server |
| `docker-compose up -d` | Start in background (detached mode) |
| `docker-compose down` | Stop and remove containers |
| `docker-compose exec microblog-dev bash` | Get a shell in the running container |
| `docker-compose logs -f microblog-dev` | View live logs |

## Optional Scripts

Create a `scripts/` directory and add these helper scripts:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Quick development
./scripts/dev.sh

# Get a shell
./scripts/shell.sh

# View logs
./scripts/logs.sh

# Clean up
./scripts/clean.sh
```

## Project Structure

```
microblog/
├── .devcontainer/
│   ├── devcontainer.json     # VS Code dev container config
│   └── Dockerfile           # Development container
├── microblog/              # Python package
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker Compose configuration
├── .env                   # Environment variables (optional)
└── README.md
```

## Features

- **🔄 Hot Reload**: Code changes automatically restart the Flask server
- **📦 Dependency Management**: Automatically installs requirements.txt
- **🔒 SELinux Compatible**: Works on RHEL/CentOS/Fedora systems
- **👥 Team Ready**: Consistent environment for all developers
- **🐳 Portable**: Works on Windows, Mac, and Linux

## Troubleshooting

### Permission Issues
If you encounter permission issues, create a `.env` file:
```bash
USER_UID=1000
USER_GID=1000
```

### Port Already in Use
If port 5000 is busy, change it in `docker-compose.yml`:
```yaml
ports:
  - "3000:5000"  # Use port 3000 instead
```

### SELinux Issues
The setup includes SELinux support with the `:Z` flag. If you still have issues:
```bash
sudo chcon -Rt container_file_t .
```

## VS Code Integration

This project includes VS Code dev container support. Install the "Dev Containers" extension and:

1. Open the project in VS Code
2. Press `F1` → "Dev Containers: Reopen in Container"
3. VS Code will build and open the project in the container

## Contributing

1. Make your changes
2. Test with `docker-compose up --build`
3. Submit a pull request

The Docker environment ensures all contributors work with identical setups.