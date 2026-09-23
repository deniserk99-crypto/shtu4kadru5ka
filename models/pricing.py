from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from .order import Order

@dataclass
class AppliedDiscount:
    name: str
    amount: Decimal
    reason: str

@dataclass
class PricingResult:
    base_total: Decimal
    applied_discounts: list[AppliedDiscount]
    final_total: Decimal

@dataclass
class DiscountContext:
    order: Order
    current_items_total: Decimal
    current_delivery_cost: Decimal
    applied_discounts: list[AppliedDiscount] = field(default_factory=list)
    applied_promo_code: Optional[str] = None
