from autometrics_engine.infrastructure.constants import SYSTEM_PROMPT, INSIGHT_PROMPT, REPORT_PROMPT


class TestSystemPrompt:
    def test_contains_key_elements(self):
        assert "español" in SYSTEM_PROMPT.lower()
        assert "retail" in SYSTEM_PROMPT.lower()
        assert "insights" in SYSTEM_PROMPT.lower()

    def test_is_not_empty(self):
        assert len(SYSTEM_PROMPT.strip()) > 50


class TestInsightPrompt:
    def test_has_required_placeholders(self):
        assert "{period_start}" in INSIGHT_PROMPT
        assert "{period_end}" in INSIGHT_PROMPT
        assert "{metrics}" in INSIGHT_PROMPT

    def test_has_json_structure(self):
        assert "title" in INSIGHT_PROMPT
        assert "summary" in INSIGHT_PROMPT
        assert "category" in INSIGHT_PROMPT
        assert "severity" in INSIGHT_PROMPT

    def test_mentions_valid_categories(self):
        assert "trend" in INSIGHT_PROMPT
        assert "anomaly" in INSIGHT_PROMPT
        assert "opportunity" in INSIGHT_PROMPT
        assert "warning" in INSIGHT_PROMPT


class TestReportPrompt:
    def test_has_required_placeholders(self):
        assert "{period_start}" in REPORT_PROMPT
        assert "{period_end}" in REPORT_PROMPT
        assert "{kpis}" in REPORT_PROMPT
        assert "{insights}" in REPORT_PROMPT
        assert "{top_products}" in REPORT_PROMPT
        assert "{top_stores}" in REPORT_PROMPT

    def test_has_html_content_field(self):
        assert "html_content" in REPORT_PROMPT

    def test_has_all_json_fields(self):
        for field in ("title", "executive_summary", "highlights", "concerns", "recommendations", "sections"):
            assert field in REPORT_PROMPT

    def test_format_with_dummy_data(self):
        filled = REPORT_PROMPT.format(
            period_start="2026-06-01",
            period_end="2026-06-07",
            kpis="- revenue: 10000",
            insights="- Alerta",
            top_products="- Producto A",
            top_stores="- Tienda X",
        )
        assert "2026-06-01" in filled
        assert "10000" in filled
        assert "Tienda X" in filled
