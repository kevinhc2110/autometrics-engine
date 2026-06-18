from dataclasses import dataclass
from datetime import date


@dataclass
class KpiDefinition:
    id: int | None = None
    name: str | None = None
    description: str | None = None
    formula: str | None = None
    unit: str | None = None
    frequency: str | None = None
    higher_is_better: bool = True


@dataclass
class KpiResult:
    id: int | None = None
    kpi_id: int | None = None
    date_id: date | None = None
    product_id: int | None = None
    store_id: int | None = None
    value: float | None = None
    previous_value: float | None = None
    change_pct: float | None = None
