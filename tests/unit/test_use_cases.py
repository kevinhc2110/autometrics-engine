from datetime import date

import pytest

from autometrics_engine.application.use_cases.run_etl import RunEtlUseCase
from autometrics_engine.application.use_cases.generate_insights import GenerateInsightsUseCase
from autometrics_engine.application.use_cases.generate_report import GenerateReportUseCase


class TestRunEtlUseCase:
    async def test_execute_loads_products_and_stores(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()

        mock_source_extractor.get_products.assert_called_once()
        mock_source_extractor.get_stores.assert_called_once()
        mock_product_repo.upsert_many.assert_called_once()
        mock_store_repo.upsert_many.assert_called_once()

    async def test_execute_calculates_kpis_for_pending_dates(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        mock_sale_repo.get_dates_without_kpis.return_value = [
            date(2026, 6, 1),
            date(2026, 6, 2),
        ]

        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()

        assert mock_sale_repo.get_daily_aggregates.call_count == 2
        assert mock_kpi_repo.save_result.call_count == 12  # 6 KPIs × 2 days

    async def test_execute_handles_empty_sales(
        self, mock_product_repo, mock_store_repo, mock_sale_repo, mock_kpi_repo, mock_source_extractor
    ):
        mock_sale_repo.get_dates_without_kpis.return_value = []
        mock_source_extractor.get_sales_since.return_value = []

        use_case = RunEtlUseCase(
            product_repo=mock_product_repo,
            store_repo=mock_store_repo,
            sale_repo=mock_sale_repo,
            kpi_repo=mock_kpi_repo,
            source=mock_source_extractor,
        )
        await use_case.execute()

        mock_sale_repo.bulk_insert.assert_called_once_with([])
        mock_kpi_repo.save_result.assert_not_called()


class TestGenerateInsightsUseCase:
    async def test_execute_calls_llm_and_saves(
        self, mock_kpi_repo, mock_insight_repo, mock_llm
    ):
        mock_llm.generate.return_value = """{
            "insights": [
                {"title": "Ventas al alza", "summary": "Las ventas crecieron 15%", "category": "trend", "severity": "high"}
            ]
        }"""

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        await use_case.execute()

        mock_kpi_repo.get_recent_results.assert_called_once()
        mock_llm.generate.assert_called_once()
        mock_insight_repo.save.assert_called_once()

    async def test_execute_handles_invalid_llm_response(
        self, mock_kpi_repo, mock_insight_repo, mock_llm
    ):
        mock_llm.generate.return_value = "not valid json"

        use_case = GenerateInsightsUseCase(
            kpi_repo=mock_kpi_repo,
            insight_repo=mock_insight_repo,
            llm=mock_llm,
        )
        with pytest.raises(Exception):
            await use_case.execute()

        mock_insight_repo.save.assert_not_called()


class TestGenerateReportUseCase:
    async def test_execute_generates_and_saves_report(
        self, mock_kpi_repo, mock_insight_repo, mock_report_repo,
        mock_product_repo, mock_store_repo, mock_sale_repo, mock_llm
    ):
        mock_llm.generate.return_value = """{
            "title": "Reporte Semanal",
            "html_content": "<div>report content</div>",
            "executive_summary": "Buena semana",
            "highlights": ["Ventas estables"],
            "concerns": [],
            "recommendations": ["Mantener inventario"],
            "sections": [{"title": "Ventas", "content": "Detalle", "metrics": {"revenue": 1000}}]
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

        mock_kpi_repo.get_latest_results.assert_called_once()
        mock_insight_repo.get_recent.assert_called_once()
        mock_product_repo.get_top_by_units.assert_called_once()
        mock_store_repo.get_top_by_revenue.assert_called_once()
        mock_report_repo.save.assert_called_once()

        _, kwargs = mock_report_repo.save.call_args
        assert kwargs["html_content"] == "<div>report content</div>"
        assert kwargs["title"] == "Reporte Semanal"
