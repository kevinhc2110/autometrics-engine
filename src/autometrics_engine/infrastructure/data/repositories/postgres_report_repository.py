import json

from autometrics_engine.domain.repositories.report_repository import ReportRepository


class PostgresReportRepository(ReportRepository):

    def __init__(self, db):
        self.db = db

    async def save(self, title: str, period_start, period_end, summary: str, content: dict):
        await self.db.execute("""
            INSERT INTO reports (title, period_start, period_end, summary, content, status, completed_at)
            VALUES ($1, $2, $3, $4, $5, 'completed', NOW())
        """, title, period_start, period_end, summary, json.dumps(content, ensure_ascii=False))
