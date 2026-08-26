#!/usr/bin/env bash
set -euo pipefail

docker compose up -d

printf '\nWaiting for Sentinel Gateway'
for attempt in $(seq 1 60); do
  if curl --fail --silent http://localhost:8000/api/health >/dev/null 2>&1; then
    printf ' ready!\n\n'
    break
  fi

  if [ "$attempt" -eq 60 ]; then
    printf ' failed.\n\n'
    docker compose ps
    docker compose logs --tail=100 app
    exit 1
  fi

  printf '.'
  sleep 2
done

if [ -n "${CODESPACE_NAME:-}" ] && [ -n "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
  APP_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
  APP_URL="http://localhost:8000"
fi

printf '\n============================================================\n'
printf '  Sentinel Gateway is running\n'
printf '  Open the frontend: %s\n' "$APP_URL"
printf '  API documentation: %s/api/docs\n' "$APP_URL"
printf '============================================================\n\n'

if [ -n "${BROWSER:-}" ] && [ -x "${BROWSER}" ]; then
  "${BROWSER}" "$APP_URL" >/dev/null 2>&1 || true
elif command -v code >/dev/null 2>&1; then
  code --open-url "$APP_URL" >/dev/null 2>&1 || true
fi
