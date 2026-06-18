from dataclasses import dataclass
from datetime import date


@dataclass
class Sale:
    id: int
    product_id: int
    store_id: int
    quantity: int
    unit_price: float
    total: float
    sale_date: date
    discount: float = 0.0
    customer_id: int | None = None
