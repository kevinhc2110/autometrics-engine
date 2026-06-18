import pytest


@pytest.fixture
def mock_kpi_repo(mocker):
    repo = mocker.AsyncMock()
    repo.get_definition_id.return_value = 1
    repo.get_previous_value.return_value = None
    repo.get_latest_results.return_value = [
        {"name": "total_revenue", "value": 10000.0},
        {"name": "total_profit", "value": 3000.0},
        {"name": "profit_margin", "value": 30.0},
        {"name": "units_sold", "value": 500.0},
    ]
    repo.get_recent_results.return_value = [
        {"name": "total_revenue", "value": 10000.0, "change_pct": 5.0, "date_id": "2026-06-01"},
        {"name": "total_profit", "value": 3000.0, "change_pct": -2.0, "date_id": "2026-06-01"},
    ]
    return repo


@pytest.fixture
def mock_product_repo(mocker):
    repo = mocker.AsyncMock()
    repo.get_cost_price.return_value = 15.0
    repo.get_top_by_units.return_value = [
        {"name": "Product A", "total": 100},
        {"name": "Product B", "total": 80},
    ]
    return repo


@pytest.fixture
def mock_store_repo(mocker):
    repo = mocker.AsyncMock()
    repo.get_top_by_revenue.return_value = [
        {"name": "Store X", "total": 50000.0},
        {"name": "Store Y", "total": 40000.0},
    ]
    return repo


@pytest.fixture
def mock_sale_repo(mocker):
    repo = mocker.AsyncMock()
    repo.get_daily_aggregates.return_value = {
        "revenue": 10000.0,
        "profit": 3000.0,
        "units": 200,
        "discounts": 500.0,
        "customers": 50,
    }
    repo.get_period_aggregates.return_value = {
        "revenue": 300000.0,
        "profit": 90000.0,
        "units": 6000,
        "discounts": 15000.0,
        "customers": 1500,
    }
    repo.get_dates_without_kpis.return_value = [__import__("datetime").date(2026, 6, 1)]
    return repo


@pytest.fixture
def mock_insight_repo(mocker):
    repo = mocker.AsyncMock()
    repo.get_recent.return_value = [
        {
            "title": "Test Insight",
            "summary": "Summary text",
            "category": "trend",
            "severity": "medium",
            "generated_at": "2026-06-01T00:00:00",
        }
    ]
    return repo


@pytest.fixture
def mock_report_repo(mocker):
    return mocker.AsyncMock()


@pytest.fixture
def mock_source_extractor(mocker):
    ext = mocker.MagicMock()
    ext.get_products.return_value = []
    ext.get_stores.return_value = []
    ext.get_sales_since.return_value = []
    return ext


@pytest.fixture
def mock_llm(mocker):
    llm = mocker.AsyncMock()
    return llm
