from datetime import date

from autometrics_engine.domain.repositories.insight_repository import InsightRepository
from autometrics_engine.domain.entities.insight import Insight


class PostgresInsightRepository(InsightRepository):

    def __init__(self, db):
        self.db = db

    async def save(self, insight: Insight, date_id: date):
        await self.db.execute("""
            INSERT INTO insights (title, summary, category, severity, date_id)
            VALUES ($1, $2, $3, $4, $5)
        """, insight.title, insight.summary, insight.category, insight.severity, date_id)

    async def get_recent(self, since: date, until: date, limit: int = 10) -> list[dict]:
        return await self.db.fetch("""
            SELECT title, summary, category, severity
            FROM insights
            WHERE date_id >= $1 AND date_id <= $2
            ORDER BY generated_at DESC
            LIMIT $3
        """, since, until, limit)
