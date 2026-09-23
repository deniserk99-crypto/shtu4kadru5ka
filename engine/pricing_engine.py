from decimal import Decimal, ROUND_HALF_EVEN
from discounts.base import DiscountStage, DiscountStrategy
from models.pricing import DiscountContext, PricingResult

def money(value):
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

class PricingEngine:
    def __init__(self, strategies: list[DiscountStrategy]):
        self.strategies = list(strategies)

    def calculate(self, order):
        items_total = money(sum(
            (item.product.base_price * item.quantity for item in order.items),
            Decimal("0")
        ))
        base_total = money(items_total + order.delivery_cost)
        context = DiscountContext(order, items_total, money(order.delivery_cost))

        for stage in DiscountStage:
            stage_strategies = [s for s in self.strategies if s.stage == stage]
            self._apply_stage(context, stage_strategies)

        final_total = money(context.current_items_total + context.current_delivery_cost)
        return PricingResult(base_total, context.applied_discounts, final_total)

    def _apply_stage(self, context, strategies):
        conflict = {}
        normal = []
        for strategy in strategies:
            group = strategy.conflict_group
            if group:
                conflict.setdefault(group, []).append(strategy)
            else:
                normal.append(strategy)

        for group_strategies in conflict.values():
            if group_strategies:
                self._apply_best_conflict(context, group_strategies)

        for strategy in normal:
            result = strategy.apply(context)
            if result and result.amount > 0:
                context.applied_discounts.append(result)

    def _apply_best_conflict(self, context, strategies):
        best = None
        best_amount = Decimal("-1")
        for strategy in strategies:
            # Preview without changing the real context.
            temp = type(context)(
                order=context.order,
                current_items_total=context.current_items_total,
                current_delivery_cost=context.current_delivery_cost,
                applied_discounts=list(context.applied_discounts),
                applied_promo_code=context.applied_promo_code
            )
            result = strategy.apply(temp)
            if result and (result.amount > best_amount or (result.amount == best_amount and strategy.conflict_priority > (best.conflict_priority if best else -1))):
                best, best_amount = strategy, result.amount
        if best is not None and best_amount > 0:
            result = best.apply(context)
            if result:
                context.applied_discounts.append(result)
