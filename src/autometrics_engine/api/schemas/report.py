from datetime import date, datetime
from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    title: str
    period_start: date
    period_end: date
    summary: str | None
    status: str
    created_at: datetime
