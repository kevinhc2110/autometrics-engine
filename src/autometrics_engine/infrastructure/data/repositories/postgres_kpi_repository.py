from datetime import date

from autometrics_engine.domain.repositories.kpi_repository import KpiRepository
from autometrics_engine.domain.entities.kpi import KpiResult


class PostgresKpiRepository(KpiRepository):

    def __init__(self, db):
        self.db = db

    async def get_definition_id(self, name: str) -> int | None:
        rows = await self.db.fetch(
            "SELECT id FROM kpi_definitions WHERE name = $1", name
        )
        return rows[0]["id"] if rows else None

    async def save_result(self, result: KpiResult):
        await self.db.execute("""
            INSERT INTO kpi_results (kpi_id, date_id, product_id, store_id, value, previous_value, change_pct)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, result.kpi_id, result.date_id, result.product_id, result.store_id,
            result.value, result.previous_value, result.change_pct)

    async def get_previous_value(self, kpi_id: int, before_date: date) -> float | None:
        rows = await self.db.fetch("""
            SELECT value FROM kpi_results
            WHERE kpi_id = $1 AND date_id < $2
            ORDER BY date_id DESC LIMIT 1
        """, kpi_id, before_date)
        return float(rows[0]["value"]) if rows else None

    async def get_recent_results(self, since: date, until: date) -> list[dict]:
        return await self.db.fetch("""
            SELECT k.name, kr.value, kr.change_pct, kr.date_id
            FROM kpi_results kr
            JOIN kpi_definitions k ON k.id = kr.kpi_id
            WHERE kr.date_id >= $1 AND kr.date_id < $2
            ORDER BY kr.date_id DESC, k.name
        """, since, until)

    async def get_latest_results(self, date_id: date) -> list[dict]:
        return await self.db.fetch("""
            SELECT k.name, kr.value, kr.change_pct
            FROM kpi_results kr
            JOIN kpi_definitions k ON k.id = kr.kpi_id
            WHERE kr.date_id = $1
        """, date_id)
