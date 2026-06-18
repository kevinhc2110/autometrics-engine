from datetime import date

from autometrics_engine.domain.repositories.sale_repository import SaleRepository


class PostgresSaleRepository(SaleRepository):

    def __init__(self, db):
        self.db = db

    async def bulk_insert(self, rows: list[tuple]):
        for r in rows:
            await self.db.execute("""
                INSERT INTO fact_sales (product_id, store_id, date_id, units_sold, revenue, cost, profit, discount_amount, customer_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, *r)

    async def get_daily_aggregates(self, sale_date: date) -> dict:
        rows = await self.db.fetch("""
            SELECT
                COALESCE(SUM(revenue),0) as total_revenue,
                COALESCE(SUM(profit),0) as total_profit,
                COALESCE(SUM(units_sold),0) as units_sold,
                COALESCE(SUM(customer_count),0) as customer_count,
                COALESCE(SUM(discount_amount),0) as discount_amount
            FROM fact_sales WHERE date_id = $1
        """, sale_date)
        r = rows[0]
        return {
            "revenue": float(r["total_revenue"]),
            "profit": float(r["total_profit"]),
            "units": float(r["units_sold"]),
            "customers": float(r["customer_count"]),
            "discounts": float(r["discount_amount"]),
        }

    async def get_dates_without_kpis(self) -> list[date]:
        rows = await self.db.fetch("""
            SELECT DISTINCT f.date_id
            FROM fact_sales f
            LEFT JOIN kpi_results k ON k.date_id = f.date_id
            WHERE k.id IS NULL
            ORDER BY f.date_id
        """)
        return [r["date_id"] for r in rows]

    async def get_period_aggregates(self, start_date: date, end_date: date) -> dict:
        rows = await self.db.fetch("""
            SELECT
                COALESCE(SUM(revenue),0) as total_revenue,
                COALESCE(SUM(profit),0) as total_profit,
                COALESCE(SUM(units_sold),0) as units_sold
            FROM fact_sales WHERE date_id BETWEEN $1 AND $2
        """, start_date, end_date)
        r = rows[0]
        return {
            "revenue": float(r["total_revenue"]),
            "profit": float(r["total_profit"]),
            "units": float(r["units_sold"]),
        }
