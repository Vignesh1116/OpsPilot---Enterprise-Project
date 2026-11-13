import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "OpsPilot"
    assert data["status"] == "online"


@pytest.mark.asyncio
async def test_top_level_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_system_health_check(client: AsyncClient):
    response = await client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "OpsPilot"
    assert data["components"]["database"]["status"] == "healthy"
    assert data["enterprise_context"]["headquarters"] == "Coimbatore, Tamil Nadu"
    assert "timestamp" in data
    assert "total_latency_ms" in data


@pytest.mark.asyncio
async def test_404_error_rfc7807_format(client: AsyncClient):
    response = await client.get("/api/v1/non-existent-route")
    assert response.status_code == 404
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert data["status"] == 404
    assert data["instance"] == "/api/v1/non-existent-route"
