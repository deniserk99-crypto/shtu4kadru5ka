from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from .customer import Customer
from .cart_item import CartItem

@dataclass(frozen=True)
class Order:
    id: str
    customer: Customer
    items: list[CartItem]
    promo_code: Optional[str]
    created_at: date
    delivery_cost: Decimal

    def __post_init__(self):
        if self.delivery_cost < 0:
            raise ValueError("delivery_cost must be non-negative")
