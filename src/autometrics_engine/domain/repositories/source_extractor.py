from abc import ABC, abstractmethod
from datetime import date

from autometrics_engine.domain.entities.product import Product
from autometrics_engine.domain.entities.store import Store


class SourceExtractor(ABC):

    @abstractmethod
    def get_products(self) -> list[Product]:
        ...

    @abstractmethod
    def get_stores(self) -> list[Store]:
        ...

    @abstractmethod
    def get_sales_since(self, last_date: date) -> list[tuple]:
        ...
