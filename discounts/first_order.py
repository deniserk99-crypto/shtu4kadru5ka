from decimal import Decimal, ROUND_HALF_EVEN
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class FirstOrderDiscount(DiscountStrategy):
    def __init__(self, percent: Decimal = Decimal("10"), name: str = "Первый заказ"):
        self.percent, self._name = percent, name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.PERCENT

    @property
    def conflict_group(self): return None

    def apply(self, context):
        if not context.order.customer.is_first_order:
            return None
        amount = money(context.current_items_total * self.percent / Decimal("100"))
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        return AppliedDiscount(self.name, amount, f"Первый заказ: скидка {self.percent}%")
