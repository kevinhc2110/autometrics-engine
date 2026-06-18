from dataclasses import dataclass


@dataclass
class Insight:
    title: str
    summary: str
    category: str
    severity: str = "medium"
    related_kpi_ids: list[int] | None = None


@dataclass
class Report:
    title: str
    period_start: str
    period_end: str
    summary: str | None = None
    content: dict | None = None
    status: str = "draft"
