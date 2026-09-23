from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Product:
    id: str
    name: str
    base_price: Decimal
    category: str

    def __post_init__(self):
        if self.base_price < 0:
            raise ValueError("base_price must be non-negative")
