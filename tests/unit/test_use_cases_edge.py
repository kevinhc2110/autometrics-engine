from datetime import date

import pytest

from autometrics_engine.application.use_cases.run_etl import RunEtlUseCase
from autometrics_engine.application.use_cases.generate_insights import GenerateInsightsUseCase
from autometrics_engine.application.use_cases.generate_report import GenerateReportUseCase


class TestRunEtlUseCaseEdge:
    async def test_skips_kpi_if_unknown_definition(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        mock_kpi_repo.get_definition_id.return_value = None

        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()

        mock_kpi_repo.save_result.assert_not_called()

    async def test_handles_zero_revenue_for_margin(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        mock_sale_repo.get_daily_aggregates.return_value = {
            "revenue": 0.0, "profit": 0.0, "units": 0, "discounts": 0.0, "customers": 0,
        }

        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()
        # Should not raise ZeroDivisionError for profit_margin (0/0)
        mock_kpi_repo.save_result.assert_called()

    async def test_handles_zero_customers_for_avg_ticket(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        mock_sale_repo.get_daily_aggregates.return_value = {
            "revenue": 1000.0, "profit": 300.0, "units": 50, "discounts": 50.0, "customers": 0,
        }

        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()
        mock_kpi_repo.save_result.assert_called()


class TestGenerateInsightsUseCaseEdge:
    async def test_empty_results_produces_fallback_text(self, mock_kpi_repo, mock_insight_repo, mock_llm):
        mock_kpi_repo.get_recent_results.return_value = []
        mock_llm.generate.return_value = '{"insights": []}'

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        prompt_arg = mock_llm.generate.call_args[0][0]
        assert "Sin datos disponibles" in prompt_arg

    async def test_results_without_change_pct_are_filtered(self, mock_kpi_repo, mock_insight_repo, mock_llm):
        mock_kpi_repo.get_recent_results.return_value = [
            {"name": "revenue", "value": 100.0, "change_pct": None, "date_id": "2026-06-01"},
        ]
        mock_llm.generate.return_value = '{"insights": []}'

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        prompt_arg = mock_llm.generate.call_args[0][0]
        assert "Sin datos disponibles" in prompt_arg

    async def test_llm_returns_empty_insights_list(self, mock_kpi_repo, mock_insight_repo, mock_llm):
        mock_llm.generate.return_value = '{"insights": []}'

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        mock_insight_repo.save.assert_not_called()

    async def test_llm_returns_json_with_code_fence(self, mock_kpi_repo, mock_insight_repo, mock_llm):
        mock_llm.generate.return_value = """```json
        {"insights": [{"title": "T", "summary": "S", "category": "trend", "severity": "low"}]}
        ```"""

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        mock_insight_repo.save.assert_called_once()


class TestGenerateReportUseCaseEdge:
    async def test_empty_insights_still_generates_report(
        self, mock_kpi_repo, mock_insight_repo, mock_report_repo,
        mock_product_repo, mock_store_repo, mock_sale_repo, mock_llm
    ):
        mock_insight_repo.get_recent.return_value = []
        mock_llm.generate.return_value = """{
            "title": "Report", "html_content": "<div>ok</div>", "executive_summary": "Sum",
            "highlights": [], "concerns": [], "recommendations": [], "sections": []
        }"""

        use_case = GenerateReportUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            report_repo=mock_report_repo,
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        mock_report_repo.save.assert_called_once()
        assert mock_report_repo.save.call_args[1]["html_content"] == "<div>ok</div>"

    async def test_llm_returns_minimal_json(
        self, mock_kpi_repo, mock_insight_repo, mock_report_repo,
        mock_product_repo, mock_store_repo, mock_sale_repo, mock_llm
    ):
        mock_llm.generate.return_value = """{
            "title": "Minimal", "html_content": "<p>hi</p>"
        }"""

        use_case = GenerateReportUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            report_repo=mock_report_repo,
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        mock_report_repo.save.assert_called_once()
        assert mock_report_repo.save.call_args[1]["title"] == "Minimal"
