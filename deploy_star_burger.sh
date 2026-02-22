#!/bin/bash

set -e

source .env

last_commit=$(git rev-parse HEAD)

echo "---Starting deploy---"

git pull

./venv/bin/pip install -r requirements.txt

npm install --include=dev

rm -rf .parcel-cache bundles

./node_modules/.bin/parcel build bundles-src/index.jsx --dist-dir bundles --public-url="/static/" --no-cache

./venv/bin/python manage.py collectstatic --noinput

./venv/bin/python manage.py migrate --noinput

sudo systemctl restart star-burger

curl https://api.rollbar.com/api/1/deploy \
  -X POST \
  -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environment": "production", "revision": "'"$last_commit"'", "local_username": "deploy"}'

echo "---Deploy finisched successfully---"
