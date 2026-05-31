FROM node:17.6.0-bullseye-slim AS frontend-builder

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY bundles-src ./bundles-src

RUN ./node_modules/.bin/parcel build bundles-src/index.jsx \
    --dist-dir bundles \
    --public-url="/static/" \
    --no-cache


FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=frontend-builder /app/bundles ./bundles
