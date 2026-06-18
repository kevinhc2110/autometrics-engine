from datetime import date, datetime

import pytest
from pydantic import ValidationError

from autometrics_engine.api.schemas.kpi import KpiDefinitionResponse, KpiResultResponse
from autometrics_engine.api.schemas.insight import InsightResponse
from autometrics_engine.api.schemas.report import ReportResponse


class TestKpiDefinitionResponse:
    def test_valid(self):
        d = KpiDefinitionResponse(id=1, name="revenue", description="Total revenue",
                                   unit="COP", frequency="daily", higher_is_better=True)
        assert d.name == "revenue"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            KpiDefinitionResponse()

    def test_unit_any_string(self):
        d = KpiDefinitionResponse(id=1, name="x", description="x", unit="%",
                                   frequency="weekly", higher_is_better=False)
        assert d.unit == "%"


class TestKpiResultResponse:
    def test_valid(self):
        r = KpiResultResponse(id=1, kpi_name="revenue", date_id=date(2026, 6, 1),
                              value=100.0, previous_value=90.0, change_pct=11.11)
        assert r.value == 100.0
        assert r.change_pct == 11.11

    def test_nullable_fields(self):
        r = KpiResultResponse(id=1, kpi_name="revenue", date_id=date(2026, 6, 1),
                              value=100.0, previous_value=None, change_pct=None)
        assert r.previous_value is None
        assert r.change_pct is None

    def test_negative_value(self):
        r = KpiResultResponse(id=1, kpi_name="margin", date_id=date(2026, 6, 1),
                              value=-5.0, previous_value=0.0, change_pct=-100.0)
        assert r.value == -5.0


class TestInsightResponse:
    def test_valid(self):
        now = datetime(2026, 6, 1, 12, 0, 0)
        i = InsightResponse(id="abc", title="Test", summary="Sum",
                            category="trend", severity="high", generated_at=now)
        assert i.title == "Test"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            InsightResponse()

    def test_auto_now_types(self):
        i = InsightResponse(id="x", title="T", summary="S",
                            category="warn", severity="low",
                            generated_at=datetime(2026, 6, 1, 0, 0, 0))
        assert i.generated_at.year == 2026


class TestReportResponse:
    def test_valid(self):
        r = ReportResponse(id="uuid", title="Report", period_start=date(2026, 6, 1),
                           period_end=date(2026, 6, 7), summary="Good",
                           status="completed", created_at=datetime(2026, 6, 8, 0, 0, 0))
        assert r.status == "completed"

    def test_nullable_summary(self):
        r = ReportResponse(id="uuid", title="Report", period_start=date(2026, 6, 1),
                           period_end=date(2026, 6, 7), summary=None,
                           status="draft", created_at=datetime(2026, 6, 8, 0, 0, 0))
        assert r.summary is None

    def test_period_validation(self):
        r = ReportResponse(id="uuid", title="R", period_start=date(2026, 6, 1),
                           period_end=date(2026, 5, 1), summary="",
                           status="draft", created_at=datetime(2026, 6, 1, 0, 0, 0))
        assert r.period_start > r.period_end
