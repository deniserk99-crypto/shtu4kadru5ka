from decimal import Decimal, ROUND_HALF_EVEN
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class FixedDiscount(DiscountStrategy):
    def __init__(self, value: Decimal, threshold: Decimal, name: str):
        if value < 0 or threshold < 0:
            raise ValueError("value and threshold must be non-negative")
        self.value, self.threshold, self._name = value, threshold, name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.FIXED

    def apply(self, context):
        if context.current_items_total < self.threshold:
            return None
        amount = min(money(self.value), context.current_items_total)
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        return AppliedDiscount(self.name, amount, f"Сумма товаров не меньше {self.threshold}")
