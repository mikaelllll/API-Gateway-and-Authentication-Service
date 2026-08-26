import os
os.environ["DATABASE_URL"]="sqlite+aiosqlite:///./test_gateway.db"
os.environ["JWT_SECRET"]="test-secret-that-is-long-enough-for-testing"
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as client:
            yield client

