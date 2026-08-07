import pytest
from fastapi.testclient import TestClient
from main import app, lifespan

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_sse_unauthorized():
    response = client.get("/sse")
    assert response.status_code in (401, 403, 500)

def test_messages_unauthorized():
    response = client.post("/messages")
    assert response.status_code in (401, 403, 500)

@pytest.mark.asyncio
async def test_lifespan():
    async with lifespan(app):
        pass
