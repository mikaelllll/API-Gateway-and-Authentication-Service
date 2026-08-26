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

