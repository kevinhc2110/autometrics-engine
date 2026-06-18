from abc import ABC, abstractmethod

from autometrics_engine.domain.entities.product import Product


class ProductRepository(ABC):

    @abstractmethod
    async def upsert_many(self, products: list[Product]):
        ...

    @abstractmethod
    async def get_cost_price(self, product_id: int) -> float | None:
        ...

    @abstractmethod
    async def get_top_by_units(self, start_date, end_date, limit: int = 5) -> list[dict]:
        ...
