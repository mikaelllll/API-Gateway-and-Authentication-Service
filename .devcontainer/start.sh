#!/usr/bin/env bash
set -euo pipefail
docker compose up -d
echo "Sentinel Gateway is starting on port 8000. Codespaces will open it automatically."

