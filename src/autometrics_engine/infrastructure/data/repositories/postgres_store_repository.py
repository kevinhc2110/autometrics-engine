from autometrics_engine.domain.repositories.store_repository import StoreRepository
from autometrics_engine.domain.entities.store import Store


class PostgresStoreRepository(StoreRepository):

    def __init__(self, db):
        self.db = db

    async def upsert_many(self, stores: list[Store]):
        for s in stores:
            await self.db.execute("""
                INSERT INTO dim_store (id, name, region, city, type)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    region = EXCLUDED.region,
                    city = EXCLUDED.city,
                    type = EXCLUDED.type
            """, s.id, s.name, s.region, s.city, s.type)

    async def get_top_by_revenue(self, start_date, end_date, limit: int = 5) -> list[dict]:
        return await self.db.fetch("""
            SELECT s.name, SUM(f.revenue) as total
            FROM fact_sales f
            JOIN dim_store s ON s.id = f.store_id
            WHERE f.date_id BETWEEN $1 AND $2
            GROUP BY s.name
            ORDER BY total DESC
            LIMIT $3
        """, start_date, end_date, limit)
