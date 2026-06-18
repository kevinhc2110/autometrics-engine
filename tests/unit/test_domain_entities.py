from datetime import date

from autometrics_engine.domain.entities.product import Product
from autometrics_engine.domain.entities.store import Store
from autometrics_engine.domain.entities.sale import Sale
from autometrics_engine.domain.entities.kpi import KpiDefinition, KpiResult
from autometrics_engine.domain.entities.insight import Insight, Report


class TestProduct:
    def test_create_minimal(self):
        p = Product(id=1, name="Test")
        assert p.id == 1
        assert p.name == "Test"
        assert p.category is None
        assert p.cost_price is None

    def test_create_full(self):
        p = Product(id=2, name="Laptop", category="Electronics", subcategory="Computers",
                     brand="Dell", cost_price=800.0, sale_price=1200.0)
        assert p.category == "Electronics"
        assert p.sale_price == 1200.0

    def test_defaults(self):
        p = Product(id=3, name="Item")
        assert p.subcategory is None
        assert p.brand is None


class TestStore:
    def test_create_minimal(self):
        s = Store(id=1, name="Main St")
        assert s.name == "Main St"
        assert s.region is None

    def test_create_full(self):
        s = Store(id=2, name="Downtown", region="Central", city="NYC", type="Retail")
        assert s.region == "Central"
        assert s.type == "Retail"


class TestSale:
    def test_create_minimal(self):
        s = Sale(id=1, product_id=1, store_id=1, quantity=2, unit_price=10.0,
                 total=20.0, sale_date=date(2026, 6, 1))
        assert s.discount == 0.0
        assert s.customer_id is None

    def test_create_full(self):
        s = Sale(id=2, product_id=1, store_id=2, quantity=1, unit_price=100.0,
                 total=95.0, sale_date=date(2026, 6, 1), discount=5.0, customer_id=42)
        assert s.discount == 5.0
        assert s.customer_id == 42


class TestKpiDefinition:
    def test_create_minimal(self):
        k = KpiDefinition()
        assert k.id is None
        assert k.name is None
        assert k.higher_is_better is True

    def test_create_full(self):
        k = KpiDefinition(id=1, name="revenue", description="Total revenue",
                          formula="SUM(revenue)", unit="COP", frequency="daily",
                          higher_is_better=True)
        assert k.name == "revenue"
        assert k.frequency == "daily"

    def test_higher_is_better_default(self):
        k = KpiDefinition()
        assert k.higher_is_better is True


class TestKpiResult:
    def test_create_minimal(self):
        kr = KpiResult()
        assert kr.id is None
        assert kr.value is None
        assert kr.change_pct is None

    def test_create_with_values(self):
        kr = KpiResult(kpi_id=1, date_id=date(2026, 6, 1), value=100.0,
                       previous_value=90.0, change_pct=11.11)
        assert kr.value == 100.0
        assert kr.change_pct == 11.11

    def test_negative_change(self):
        kr = KpiResult(kpi_id=1, date_id=date(2026, 6, 1), value=80.0,
                       previous_value=100.0, change_pct=-20.0)
        assert kr.change_pct == -20.0


class TestInsight:
    def test_create_minimal(self):
        ins = Insight(title="Test", summary="Summary", category="trend")
        assert ins.severity == "medium"
        assert ins.related_kpi_ids is None

    def test_create_full(self):
        ins = Insight(title="Alert", summary="Something", category="warning",
                      severity="high", related_kpi_ids=[1, 2, 3])
        assert ins.severity == "high"
        assert ins.related_kpi_ids == [1, 2, 3]

    def test_severity_edge_cases(self):
        for s in ("low", "medium", "high", "critical"):
            ins = Insight(title="X", summary="Y", category="trend", severity=s)
            assert ins.severity == s


class TestReport:
    def test_create_minimal(self):
        r = Report(title="Weekly", period_start="2026-06-01", period_end="2026-06-07")
        assert r.status == "draft"
        assert r.summary is None
        assert r.content is None

    def test_create_completed(self):
        r = Report(title="Monthly", period_start="2026-06-01", period_end="2026-06-30",
                   summary="Good month", content={"kpis": {"revenue": 100}}, status="completed")
        assert r.status == "completed"
        assert r.content["kpis"]["revenue"] == 100
