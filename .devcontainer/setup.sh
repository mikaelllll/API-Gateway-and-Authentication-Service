#!/usr/bin/env bash
set -euo pipefail

echo "Building Sentinel Gateway containers..."
docker compose build

echo "Build completed. Starting the application..."
bash .devcontainer/start.sh
