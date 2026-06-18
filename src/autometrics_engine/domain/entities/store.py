from dataclasses import dataclass


@dataclass
class Store:
    id: int
    name: str
    region: str | None = None
    city: str | None = None
    type: str | None = None
