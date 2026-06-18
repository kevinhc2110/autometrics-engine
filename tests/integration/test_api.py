from unittest.mock import AsyncMock

import httpx
import pytest

from autometrics_engine.main import app
from autometrics_engine.api.dependencies import (
    get_database,
    get_redis_pool,
    get_kpi_repository,
    get_insight_repository,
    get_report_repository,
    get_product_repository,
    get_store_repository,
    get_sale_repository,
    get_source_extractor,
    get_llm_provider,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()

    _call_count = 0

    async def fetch(query, *args):
        nonlocal _call_count
        _call_count += 1
        q = query.lower()

        if "kpi_definitions" in q and "kpi_results" not in q and "join" not in q:
            return [
                {"name": "total_revenue", "unit": "COP", "description": "Ingresos"},
                {"name": "units_sold", "unit": "units", "description": "Unidades"},
            ]

        if "distinct on" in q:
            return [
                {"name": "total_revenue", "value": 10000.0, "change_pct": 5.0},
            ]

        if "kpi_results" in q and "order by kr.date_id, k.name" in q:
            return [
                {"name": "total_revenue", "date_id": "2026-06-01", "value": 10000.0},
                {"name": "total_revenue", "date_id": "2026-06-02", "value": 12000.0},
            ]

        if "sum(f.units_sold)" in q:
            return [
                {"name": "Product A", "total": 100.0},
            ]

        if "sum(f.revenue)" in q:
            return [
                {"name": "Store X", "total": 50000.0},
            ]

        if "from insights" in q:
            return [
                {"title": "Test", "summary": "Sum", "category": "trend", "severity": "low", "generated_at": "2026-06-01T00:00:00"},
            ]

        if "from reports" in q:
            return [
                {"id": "abc123", "title": "Report", "created_at": "2026-06-01T00:00:00"},
            ]

        return []

    db.fetch = AsyncMock(side_effect=fetch)
    return db


@pytest.fixture
def mock_redis(mocker):
    redis = mocker.AsyncMock()
    redis.enqueue_job = AsyncMock(return_value=None)
    return redis


@pytest.fixture
def test_app(mock_db, mock_redis):
    app.dependency_overrides = {
        get_database: lambda: mock_db,
        get_redis_pool: lambda: mock_redis,
        get_kpi_repository: lambda: AsyncMock(),
        get_insight_repository: lambda: AsyncMock(),
        get_report_repository: lambda: AsyncMock(),
        get_product_repository: lambda: AsyncMock(),
        get_store_repository: lambda: AsyncMock(),
        get_sale_repository: lambda: AsyncMock(),
        get_source_extractor: lambda: AsyncMock(),
        get_llm_provider: lambda: AsyncMock(),
    }
    yield app
    app.dependency_overrides = {}


@pytest.fixture
async def client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestDashboardAPI:
    async def test_dashboard_data(self, client):
        resp = await client.get("/api/dashboard/data")
        assert resp.status_code == 200
        data = resp.json()
        assert "kpi_definitions" in data
        assert "latest" in data
        assert "trends" in data
        assert "top_products" in data
        assert "top_stores" in data
        assert "insights" in data
        assert "last_report" in data

    async def test_dashboard_data_defines_kpis(self, client):
        resp = await client.get("/api/dashboard/data")
        data = resp.json()
        names = [k["name"] for k in data["kpi_definitions"]]
        assert "total_revenue" in names
        assert "units_sold" in names


class TestKPIsAPI:
    async def test_list_kpi_definitions(self, client):
        resp = await client.get("/api/kpis/definitions")
        assert resp.status_code == 200


class TestReportsAPI:
    async def test_list_reports(self, client):
        resp = await client.get("/api/reports")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_generate_report_returns_202(self, client, mock_redis):
        resp = await client.post("/api/reports/generate")
        assert resp.status_code == 202
        assert resp.json()["message"] == "Report generation job enqueued"
        mock_redis.enqueue_job.assert_called_once_with("generate_report")


class TestETLAPI:
    async def test_run_etl_returns_202(self, client, mock_redis):
        resp = await client.post("/api/etl/run")
        assert resp.status_code == 202
        assert resp.json()["message"] == "ETL job enqueued"
        mock_redis.enqueue_job.assert_called_once_with("run_etl_pipeline")


class TestInsightsAPI:
    async def test_generate_insights_returns_202(self, client, mock_redis):
        resp = await client.post("/api/insights/generate")
        assert resp.status_code == 202
        assert resp.json()["message"] == "Insight generation job enqueued"
        mock_redis.enqueue_job.assert_called_once_with("generate_insights")
