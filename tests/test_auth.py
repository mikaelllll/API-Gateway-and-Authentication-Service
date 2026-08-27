import uuid
import pytest

@pytest.mark.asyncio
async def test_complete_authentication_lifecycle(client):
    email=f"user-{uuid.uuid4()}@example.com"
    register=await client.post("/api/auth/register",json={"email":email,"password":"StrongPass123"})
    assert register.status_code==201
    assert "password" not in register.text
    login=await client.post("/api/auth/login",json={"email":email,"password":"StrongPass123"})
    assert login.status_code==200
    tokens=login.json()
    me=await client.get("/api/me",headers={"Authorization":f"Bearer {tokens['access_token']}"})
    assert me.status_code==200 and me.json()["email"]==email
    rotated=await client.post("/api/auth/refresh",json={"refresh_token":tokens["refresh_token"]})
    assert rotated.status_code==200
    reused=await client.post("/api/auth/refresh",json={"refresh_token":tokens["refresh_token"]})
    assert reused.status_code==401

@pytest.mark.asyncio
async def test_validation_and_protected_route(client):
    weak=await client.post("/api/auth/register",json={"email":"bad","password":"weak"})
    assert weak.status_code==422
    protected=await client.get("/api/me")
    assert protected.status_code==401

@pytest.mark.asyncio
async def test_health_and_security_headers(client):
    response=await client.get("/api/health")
    assert response.status_code==200
    assert response.headers["x-content-type-options"]=="nosniff"


@pytest.mark.asyncio
async def test_oauth2_rbac_api_key_and_revocation(client):
    email = f"user-{uuid.uuid4()}@example.com"
    password = "StrongPass123"
    await client.post("/api/auth/register", json={"email": email, "password": password})

    oauth = await client.post(
        "/api/oauth/token",
        data={"username": email, "password": password},
    )
    assert oauth.status_code == 200
    tokens = oauth.json()
    bearer = {"Authorization": f"Bearer {tokens['access_token']}"}

    forbidden = await client.get("/api/admin/overview", headers=bearer)
    assert forbidden.status_code == 403

    created_key = await client.post(
        "/api/api-keys",
        headers=bearer,
        json={"name": "Test client"},
    )
    assert created_key.status_code == 201
    service = await client.get(
        "/api/service/data",
        headers={"X-API-Key": created_key.json()["key"]},
    )
    assert service.status_code == 200
    assert service.json()["authenticated"] is True

    revoked = await client.post(
        "/api/auth/revoke",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert revoked.status_code == 204
    rejected = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert rejected.status_code == 401


@pytest.mark.asyncio
async def test_security_lab_and_cache_headers(client):
    password_demo = await client.post(
        "/api/lab/password-hash",
        json={"password": "StrongPass123"},
    )
    assert password_demo.status_code == 200
    assert password_demo.json()["algorithm"] == "Argon2"
    assert password_demo.json()["verification_passed"] is True
    assert password_demo.json()["plaintext_stored"] is False

    health = await client.get("/api/health")
    assert health.headers["cache-control"] == "no-store"
