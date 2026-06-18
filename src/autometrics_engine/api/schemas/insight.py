from datetime import datetime
from pydantic import BaseModel


class InsightResponse(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    severity: str
    generated_at: datetime
