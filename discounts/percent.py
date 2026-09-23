from decimal import Decimal, ROUND_HALF_EVEN
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class PercentDiscount(DiscountStrategy):
    def __init__(self, percent: Decimal, name: str):
        if percent < 0:
            raise ValueError("percent must be non-negative")
        self.percent = percent
        self._name = name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.PERCENT

    @property
    def conflict_group(self): return "ordinary_percent"

    def apply(self, context):
        amount = money(context.current_items_total * self.percent / Decimal("100"))
        amount = min(amount, context.current_items_total)
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        return AppliedDiscount(self.name, amount, f"Скидка {self.percent}% от текущей суммы товаров")
