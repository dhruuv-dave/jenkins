#!/bin/bash
# Don't use set -e here, we want to continue even if chmod fails

# Fix Docker socket permissions on startup
# This works on both Linux and Windows Docker Desktop
if [ -S /var/run/docker.sock ]; then
    echo "🔧 Fixing Docker socket permissions..."
    if chmod 666 /var/run/docker.sock 2>/dev/null; then
        echo "✅ Docker socket permissions configured"
    else
        echo "⚠️  Warning: Could not change Docker socket permissions (this is okay if already set)"
    fi
fi

# Switch to jenkins user and execute the original Jenkins entrypoint
# Jenkins entrypoint script handles user switching internally, but we run as root first
# to fix permissions, then let jenkins.sh handle the user switch
exec /usr/local/bin/jenkins.sh "$@"

