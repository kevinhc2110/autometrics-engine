from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    category: str | None = None
    subcategory: str | None = None
    brand: str | None = None
    cost_price: float | None = None
    sale_price: float | None = None
