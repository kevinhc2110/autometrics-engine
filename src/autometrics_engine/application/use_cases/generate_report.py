import json
from datetime import date, timedelta

from autometrics_engine.domain.repositories.kpi_repository import KpiRepository
from autometrics_engine.domain.repositories.insight_repository import InsightRepository
from autometrics_engine.domain.repositories.report_repository import ReportRepository
from autometrics_engine.domain.repositories.product_repository import ProductRepository
from autometrics_engine.domain.repositories.store_repository import StoreRepository
from autometrics_engine.domain.repositories.sale_repository import SaleRepository
from autometrics_engine.domain.services.llm_provider import LLMProvider
from autometrics_engine.infrastructure.constants import REPORT_PROMPT


class GenerateReportUseCase:

    def __init__(
        self,
        kpi_repo: KpiRepository,
        insight_repo: InsightRepository,
        report_repo: ReportRepository,
        product_repo: ProductRepository,
        store_repo: StoreRepository,
        sale_repo: SaleRepository,
        llm: LLMProvider,
    ):
        self._kpi_repo = kpi_repo
        self._insight_repo = insight_repo
        self._report_repo = report_repo
        self._product_repo = product_repo
        self._store_repo = store_repo
        self._sale_repo = sale_repo
        self._llm = llm

    async def execute(self):
        today = date.today()
        period_start = today - timedelta(days=30)
        period_end = today - timedelta(days=1)

        kpis = await self._kpi_repo.get_latest_results(period_end)
        insights = await self._insight_repo.get_recent(period_start, period_end)
        top_products = await self._product_repo.get_top_by_units(period_start, period_end)
        top_stores = await self._store_repo.get_top_by_revenue(period_start, period_end)

        kpis_text = "\n".join(f"- {r['name']}: {r['value']}" for r in kpis)
        insights_text = "\n".join(
            f"- [{r['severity']}] {r['title']}: {r['summary']}" for r in insights
        )
        products_text = "\n".join(
            f"- {r['name']}: {r['total']} unidades" for r in top_products
        )
        stores_text = "\n".join(
            f"- {r['name']}: ${r['total']:,.0f}" for r in top_stores
        )

        prompt = REPORT_PROMPT.format(
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            kpis=kpis_text or "Sin datos",
            insights=insights_text or "Sin insights",
            top_products=products_text or "Sin datos",
            top_stores=stores_text or "Sin datos",
        )

        response = await self._llm.generate(prompt, temperature=0.3)
        data = json.loads(response.strip().removeprefix("```json").removesuffix("```").strip())

        await self._report_repo.save(
            title=data["title"],
            period_start=period_start,
            period_end=period_end,
            summary=data.get("executive_summary", ""),
            content=data,
        )
