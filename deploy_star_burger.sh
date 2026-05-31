#!/bin/bash

set -e

cd ~/djangoprojects/dockerize-django-lesson

source .env

echo "=== Starting Docker deploy ==="

echo "Pull latest code..."
git pull

last_commit=$(git rev-parse HEAD)

echo "Build and start containers..."
docker compose up --build -d

echo "Apply migrations..."
docker compose exec -T backend python manage.py migrate --noinput

echo "Collect static files..."
docker compose exec -T backend python manage.py collectstatic --noinput

echo "Restart nginx..."
docker compose restart nginx

if [ -n "$ROLLBAR_TOKEN" ]; then
  echo "Notify Rollbar..."

  curl https://api.rollbar.com/api/1/deploy/ \
    -X POST \
    -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"environment\": \"${ROLLBAR_ENVIRONMENT:-production}\", \"revision\": \"$last_commit\", \"local_username\": \"deploy\"}"
else
  echo "ROLLBAR_TOKEN is empty. Skip Rollbar notification."
fi

echo "=== Deploy finished successfully ==="
