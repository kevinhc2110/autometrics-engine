from abc import ABC, abstractmethod
from datetime import date

from autometrics_engine.domain.entities.insight import Insight


class InsightRepository(ABC):

    @abstractmethod
    async def save(self, insight: Insight, date_id: date):
        ...

    @abstractmethod
    async def get_recent(self, since: date, until: date, limit: int = 10) -> list[dict]:
        ...
