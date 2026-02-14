#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/shota/src/salesforce"
BUILD_DIR="/tmp/word-web-build-$(date +%s)"
IMAGE_NAME="word-web"
CONTAINER_NAME="word-web"
PORT="8501"

mkdir -p "$BUILD_DIR"
rsync -a "$ROOT_DIR/word-web/" "$BUILD_DIR/word-web/"
rsync -a "$ROOT_DIR/word/" "$BUILD_DIR/word/"
cp -f "$ROOT_DIR/.env" "$BUILD_DIR/.env" || true

docker build -f "$BUILD_DIR/word-web/Dockerfile" -t "$IMAGE_NAME" "$BUILD_DIR"

docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true

docker run --rm -d -p "$PORT:8501" --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "OK: http://localhost:$PORT"
