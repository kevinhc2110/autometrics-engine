from abc import ABC, abstractmethod
from datetime import date

from autometrics_engine.domain.entities.kpi import KpiResult


class KpiRepository(ABC):

    @abstractmethod
    async def get_definition_id(self, name: str) -> int | None:
        ...

    @abstractmethod
    async def save_result(self, result: KpiResult):
        ...

    @abstractmethod
    async def get_previous_value(self, kpi_id: int, before_date: date) -> float | None:
        ...

    @abstractmethod
    async def get_recent_results(self, since: date, until: date) -> list[dict]:
        ...

    @abstractmethod
    async def get_latest_results(self, date_id: date) -> list[dict]:
        ...
