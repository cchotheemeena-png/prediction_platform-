#!/bin/bash
echo "🚀 Deploying Prediction Platform..."

# Load env
set -a
source .env
set +a

# Start services
docker-compose up -d db redis

# Backend migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py createsuperuser --noinput || true

# Frontend build
docker-compose up frontend --build

# Start all
docker-compose up -d

echo "✅ Platform deployed! Visit: http://localhost:8000"
echo "Admin: http://localhost:8000/admin/"
echo "Swagger: http://localhost:8000/swagger/"
