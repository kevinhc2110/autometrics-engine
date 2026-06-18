from unittest.mock import AsyncMock

import httpx
import pytest

from autometrics_engine.main import app
from autometrics_engine.api.dependencies import (
    get_database,
    get_redis_pool,
)


@pytest.fixture
def empty_db():
    db = AsyncMock()
    db.fetch = AsyncMock(return_value=[])
    db.fetchrow = AsyncMock(return_value=None)
    return db


@pytest.fixture
def client(empty_db):
    app.dependency_overrides = {
        get_database: lambda: empty_db,
        get_redis_pool: lambda: AsyncMock(),
    }
    transport = httpx.ASGITransport(app=app)
    client = httpx.AsyncClient(transport=transport, base_url="http://test")
    yield client
    app.dependency_overrides = {}


class TestReportNotFound:
    async def test_get_nonexistent_report(self, client):
        resp = await client.get("/api/reports/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    async def test_get_nonexistent_report_html(self, client):
        resp = await client.get("/api/reports/00000000-0000-0000-0000-000000000000/html")
        assert resp.status_code == 404
        assert "Reporte no encontrado" in resp.text


class TestEmptyDashboard:
    async def test_kpis_list_empty(self, client):
        resp = await client.get("/api/kpis")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_insights_list_empty(self, client):
        resp = await client.get("/api/insights")
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_reports_list_empty(self, client):
        resp = await client.get("/api/reports")
        assert resp.status_code == 200
        assert resp.json() == []


class TestDashboardWithEmptyData:
    async def test_dashboard_data_without_kpis(self, client):
        resp = await client.get("/api/dashboard/data")
        assert resp.status_code == 200
        data = resp.json()
        assert data["latest"] == {}
        assert data["trends"] == {}
        assert data["top_products"] == []
        assert data["last_report"] is None
