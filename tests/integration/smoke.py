"""End-to-end smoke test for a running Sentinel Docker Compose stack."""

from __future__ import annotations

import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8000"


def request(
    method: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    expected: int = 200,
) -> tuple[dict[str, object] | None, dict[str, str]]:
    body = json.dumps(payload).encode() if payload is not None else None
    request_headers = {"Content-Type": "application/json", **(headers or {})}
    req = Request(BASE_URL + path, data=body, headers=request_headers, method=method)
    try:
        with urlopen(req, timeout=15) as response:
            status = response.status
            raw = response.read()
            response_headers = dict(response.headers.items())
    except HTTPError as exc:
        status = exc.code
        raw = exc.read()
        response_headers = dict(exc.headers.items())

    assert status == expected, f"{method} {path}: expected {expected}, got {status}: {raw!r}"
    return (json.loads(raw) if raw else None), response_headers


def main() -> None:
    health, headers = request("GET", "/api/health")
    assert health and health["status"] == "healthy"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Cache-Control"] == "no-store"

    email = f"integration-{uuid.uuid4()}@example.com"
    password = "IntegrationPass123"
    registered, _ = request(
        "POST",
        "/api/auth/register",
        payload={"email": email, "password": password},
        expected=201,
    )
    assert registered and registered["email"] == email
    assert "password" not in registered

    tokens, _ = request(
        "POST",
        "/api/auth/login",
        payload={"email": email, "password": password},
    )
    assert tokens
    bearer = {"Authorization": f"Bearer {tokens['access_token']}"}

    identity, _ = request("GET", "/api/me", headers=bearer)
    assert identity and identity["email"] == email

    _, _ = request("GET", "/api/admin/overview", headers=bearer, expected=403)

    api_key, _ = request(
        "POST",
        "/api/api-keys",
        headers=bearer,
        payload={"name": "Integration client"},
        expected=201,
    )
    assert api_key and api_key["key"].startswith(api_key["prefix"])
    service, _ = request(
        "GET",
        "/api/service/data",
        headers={"X-API-Key": str(api_key["key"])},
    )
    assert service and service["authenticated"] is True and service["owner"] == email

    rotated, _ = request(
        "POST",
        "/api/auth/refresh",
        payload={"refresh_token": tokens["refresh_token"]},
    )
    assert rotated and rotated["refresh_token"] != tokens["refresh_token"]
    request(
        "POST",
        "/api/auth/refresh",
        payload={"refresh_token": tokens["refresh_token"]},
        expected=401,
    )

    print("Sentinel live-stack integration test passed")


if __name__ == "__main__":
    main()
