from decimal import Decimal
from .base import DiscountStage, DiscountStrategy
from models.pricing import AppliedDiscount, DiscountContext

class FreeDeliveryDiscount(DiscountStrategy):
    def __init__(self, threshold: Decimal, name: str):
        self.threshold, self._name = threshold, name

    @property
    def name(self): return self._name

    @property
    def stage(self): return DiscountStage.DELIVERY

    def apply(self, context):
        if context.current_items_total <= self.threshold or context.current_delivery_cost <= 0:
            return None
        amount = context.current_delivery_cost
        context.current_delivery_cost = Decimal("0.00")
        return AppliedDiscount(self.name, amount, f"Сумма товаров строго больше {self.threshold}")
