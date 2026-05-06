#!/bin/bash
set -e

echo "🛑 Stopping existing containers..."
docker compose down

echo "🔨 Building images..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "✅ Deployment complete!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
