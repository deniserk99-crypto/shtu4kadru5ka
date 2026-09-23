from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Optional
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

@dataclass(frozen=True)
class PromoConfig:
    code: str
    kind: str
    value: Decimal
    expires_at: Optional[date] = None
    active: bool = True

class PromoCodeDiscount(DiscountStrategy):
    def __init__(self, config: PromoConfig, name: str | None = None):
        self.config = config
        self._name = name or f"Промокод {config.code}"

    @property
    def name(self): return self._name

    @property
    def stage(self):
        return DiscountStage.PERCENT if self.config.kind == "percent" else DiscountStage.FIXED

    @property
    def conflict_group(self):
        return "ordinary_percent" if self.config.kind == "percent" else None

    @property
    def conflict_priority(self):
        return 1 if self.config.kind == "percent" else 0

    def is_valid(self, context):
        code = context.order.promo_code
        if not self.config.active or code is None or code.upper() != self.config.code.upper():
            return False
        if self.config.expires_at is not None and context.order.created_at > self.config.expires_at:
            return False
        return True

    def apply(self, context):
        if not self.is_valid(context):
            return None
        if self.config.kind == "percent":
            amount = money(context.current_items_total * self.config.value / Decimal("100"))
        else:
            amount = money(self.config.value)
        amount = min(amount, context.current_items_total)
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        context.applied_promo_code = self.config.code
        return AppliedDiscount(self.name, amount, f"Применён промокод {self.config.code}")
