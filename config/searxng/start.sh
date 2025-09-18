#!/bin/bash
# SearXNG Startup Script

set -e

export BIND_ADDRESS="0.0.0.0:8080"
export INSTANCE_NAME="CrewAI Search Engine"

# Check if settings.yml exists, if not copy from template
if [ ! -f /etc/searxng/settings.yml ]; then
    echo "No settings.yml found, using default configuration..."
    cp /usr/local/searxng/searx/settings.yml /etc/searxng/settings.yml
fi

# Start SearXNG
exec python searx/webapp.py
