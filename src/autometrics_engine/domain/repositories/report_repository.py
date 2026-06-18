from abc import ABC, abstractmethod


class ReportRepository(ABC):

    @abstractmethod
    async def save(self, title: str, period_start, period_end, summary: str, content: dict, html_content: str = ""):
        ...
