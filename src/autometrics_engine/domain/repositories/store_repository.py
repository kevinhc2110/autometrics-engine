from abc import ABC, abstractmethod

from autometrics_engine.domain.entities.store import Store


class StoreRepository(ABC):

    @abstractmethod
    async def upsert_many(self, stores: list[Store]):
        ...

    @abstractmethod
    async def get_top_by_revenue(self, start_date, end_date, limit: int = 5) -> list[dict]:
        ...
