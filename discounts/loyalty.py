from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class LoyaltyDiscount(DiscountStrategy):
    def __init__(self, percent: Decimal = Decimal("5"), days: int = 30, name: str = "Лояльность"):
        self.percent, self.days, self._name = percent, days, name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.PERCENT

    @property
    def conflict_group(self): return None

    def apply(self, context):
        last = context.order.customer.last_purchase_date
        if last is None:
            return None
        delta = (context.order.created_at - last).days
        if delta < 0 or delta > self.days:
            return None
        amount = money(context.current_items_total * self.percent / Decimal("100"))
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        return AppliedDiscount(self.name, amount, f"Последняя покупка была {delta} дней назад")
