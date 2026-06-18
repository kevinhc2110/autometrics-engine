from datetime import date
from pydantic import BaseModel


class KpiDefinitionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    unit: str
    frequency: str
    higher_is_better: bool


class KpiResultResponse(BaseModel):
    id: int
    kpi_name: str
    date_id: date
    value: float
    previous_value: float | None
    change_pct: float | None
