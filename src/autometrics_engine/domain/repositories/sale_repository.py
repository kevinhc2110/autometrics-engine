from abc import ABC, abstractmethod
from datetime import date


class SaleRepository(ABC):

    @abstractmethod
    async def bulk_insert(self, rows: list[tuple]):
        ...

    @abstractmethod
    async def get_daily_aggregates(self, sale_date: date) -> dict:
        ...

    @abstractmethod
    async def get_period_aggregates(self, start_date: date, end_date: date) -> dict:
        ...

    @abstractmethod
    async def get_dates_without_kpis(self) -> list[date]:
        ...
