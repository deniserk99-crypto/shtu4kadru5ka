from collections import defaultdict
from decimal import Decimal, ROUND_HALF_EVEN
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class ThreeForTwoDiscount(DiscountStrategy):
    def __init__(self, category: str, name: str):
        self.category, self._name = category, name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.QUANTITY

    def apply(self, context):
        items = [i for i in context.order.items if i.product.category == self.category]
        units = []
        for item in items:
            units.extend([item.product.base_price] * item.quantity)
        free_count = len(units) // 3
        if free_count == 0:
            return None
        amount = money(sum(sorted(units)[:free_count], Decimal("0")))
        amount = min(amount, context.current_items_total)
        if amount <= 0:
            return None
        context.current_items_total = money(context.current_items_total - amount)
        return AppliedDiscount(
            self.name, amount,
            f"Категория {self.category}: {len(units)} единиц, {free_count} бесплатно"
        )
