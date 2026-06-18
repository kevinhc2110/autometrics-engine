import json
from datetime import date, timedelta

from autometrics_engine.domain.repositories.kpi_repository import KpiRepository
from autometrics_engine.domain.repositories.insight_repository import InsightRepository
from autometrics_engine.domain.services.llm_provider import LLMProvider
from autometrics_engine.domain.entities.insight import Insight
from autometrics_engine.infrastructure.constants import INSIGHT_PROMPT


class GenerateInsightsUseCase:

    def __init__(
        self,
        kpi_repo: KpiRepository,
        insight_repo: InsightRepository,
        llm: LLMProvider,
    ):
        self._kpi_repo = kpi_repo
        self._insight_repo = insight_repo
        self._llm = llm

    async def execute(self):
        today = date.today()
        week_ago = today - timedelta(days=7)

        results = await self._kpi_repo.get_recent_results(week_ago, today)

        metrics_text = "\n".join(
            f"- {r['name']}: {r['value']} (cambio: {r['change_pct']:.1f}% el {r['date_id']})"
            for r in results if r["change_pct"] is not None
        ) or "Sin datos disponibles para el período."

        prompt = INSIGHT_PROMPT.format(
            period_start=week_ago.isoformat(),
            period_end=(today - timedelta(days=1)).isoformat(),
            metrics=metrics_text,
        )

        response = await self._llm.generate(prompt, temperature=0.3)
        data = json.loads(response.strip().removeprefix("```json").removesuffix("```").strip())

        for ins in data["insights"]:
            await self._insight_repo.save(
                Insight(
                    title=ins["title"],
                    summary=ins["summary"],
                    category=ins["category"],
                    severity=ins["severity"],
                ),
                today,
            )
