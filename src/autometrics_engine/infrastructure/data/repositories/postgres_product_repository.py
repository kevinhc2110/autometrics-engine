from autometrics_engine.domain.repositories.product_repository import ProductRepository
from autometrics_engine.domain.entities.product import Product


class PostgresProductRepository(ProductRepository):

    def __init__(self, db):
        self.db = db

    async def upsert_many(self, products: list[Product]):
        for p in products:
            await self.db.execute("""
                INSERT INTO dim_product (id, name, category, subcategory, brand, cost_price, sale_price)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    brand = EXCLUDED.brand,
                    cost_price = EXCLUDED.cost_price,
                    sale_price = EXCLUDED.sale_price
            """, p.id, p.name, p.category, p.subcategory, p.brand, p.cost_price, p.sale_price)

    async def get_cost_price(self, product_id: int) -> float | None:
        rows = await self.db.fetch(
            "SELECT cost_price FROM dim_product WHERE id = $1", product_id
        )
        return float(rows[0]["cost_price"]) if rows else None

    async def get_top_by_units(self, start_date, end_date, limit: int = 5) -> list[dict]:
        return await self.db.fetch("""
            SELECT p.name, SUM(f.units_sold) as total
            FROM fact_sales f
            JOIN dim_product p ON p.id = f.product_id
            WHERE f.date_id BETWEEN $1 AND $2
            GROUP BY p.name
            ORDER BY total DESC
            LIMIT $3
        """, start_date, end_date, limit)
