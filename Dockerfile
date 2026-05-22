# syntax=docker/dockerfile:1.7

FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DOCARCHIV_STATIC_DIR=static

WORKDIR /app/backend

RUN useradd --create-home --shell /usr/sbin/nologin docarchiv

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static

RUN chmod +x ./entrypoint.sh \
    && chown -R docarchiv:docarchiv /app/backend

USER docarchiv

EXPOSE 8000

CMD ["./entrypoint.sh"]
