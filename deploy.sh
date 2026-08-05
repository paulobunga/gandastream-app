#!/bin/bash
set -e

echo "Deploying gandastream to VPS..."

# Pull latest code
git pull origin main

# Build and start services
docker compose down
docker compose build
docker compose up -d

echo "Deployment complete."
echo "Frontend: http://$(hostname -I | awk '{print $1}')"
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
