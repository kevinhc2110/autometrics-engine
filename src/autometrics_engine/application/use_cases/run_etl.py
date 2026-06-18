from datetime import date, timedelta

from autometrics_engine.domain.repositories.product_repository import ProductRepository
from autometrics_engine.domain.repositories.store_repository import StoreRepository
from autometrics_engine.domain.repositories.sale_repository import SaleRepository
from autometrics_engine.domain.repositories.kpi_repository import KpiRepository
from autometrics_engine.domain.repositories.source_extractor import SourceExtractor
from autometrics_engine.domain.entities.kpi import KpiResult


class RunEtlUseCase:

    def __init__(
        self,
        product_repo: ProductRepository,
        store_repo: StoreRepository,
        sale_repo: SaleRepository,
        kpi_repo: KpiRepository,
        source: SourceExtractor,
    ):
        self._product_repo = product_repo
        self._store_repo = store_repo
        self._sale_repo = sale_repo
        self._kpi_repo = kpi_repo
        self._source = source

    async def execute(self):
        # 1. Extract from SQL Server → load warehouse
        products = self._source.get_products()
        await self._product_repo.upsert_many(products)

        stores = self._source.get_stores()
        await self._store_repo.upsert_many(stores)

        sales = self._source.get_sales_since(date(2020, 1, 1))
        enriched = []
        for row in sales:
            sale_id, product_id, store_id, qty, unit_price, total, sale_date, discount, cust_id = row
            total = float(total)
            discount = float(discount)
            qty = int(qty)
            cost_price = await self._product_repo.get_cost_price(product_id)
            cost = float(cost_price or 0) * qty
            profit = total - cost - discount
            enriched.append((
                product_id, store_id, sale_date, qty, total, cost, profit, discount,
                1 if cust_id else 0,
            ))
        await self._sale_repo.bulk_insert(enriched)

        # 2. Calculate daily KPIs for all pending dates
        pending_dates = await self._sale_repo.get_dates_without_kpis()
        for day in pending_dates:
            agg = await self._sale_repo.get_daily_aggregates(day)

            kpis = {
                "total_revenue": agg["revenue"],
                "total_profit": agg["profit"],
                "profit_margin": (agg["profit"] / agg["revenue"] * 100) if agg["revenue"] else 0,
                "units_sold": agg["units"],
                "avg_ticket": (agg["revenue"] / agg["customers"]) if agg["customers"] else 0,
                "discount_rate": (agg["discounts"] / agg["revenue"] * 100) if agg["revenue"] else 0,
            }

            for name, value in kpis.items():
                kpi_id = await self._kpi_repo.get_definition_id(name)
                if kpi_id is None:
                    continue

                prev_value = await self._kpi_repo.get_previous_value(kpi_id, day)
                change_pct = (
                    ((value - prev_value) / prev_value * 100)
                    if prev_value is not None and prev_value != 0
                    else None
                )

                await self._kpi_repo.save_result(KpiResult(
                    kpi_id=kpi_id,
                    date_id=day,
                    value=round(value, 4),
                    previous_value=round(prev_value, 4) if prev_value is not None else None,
                    change_pct=round(change_pct, 4) if change_pct is not None else None,
                ))
