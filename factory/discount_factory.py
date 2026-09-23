from decimal import Decimal
from discounts.percent import PercentDiscount
from discounts.fixed import FixedDiscount
from discounts.three_for_two import ThreeForTwoDiscount
from discounts.loyalty import LoyaltyDiscount
from discounts.free_delivery import FreeDeliveryDiscount
from discounts.first_order import FirstOrderDiscount
from discounts.promo_code import PromoConfig, PromoCodeDiscount

class DiscountFactory:
    _creators = {}

    @classmethod
    def register(cls, discount_type, creator):
        cls._creators[discount_type] = creator

    @classmethod
    def create(cls, discount_type, config):
        if discount_type not in cls._creators:
            raise ValueError(f"Unknown discount type: {discount_type}")
        return cls._creators[discount_type](config)

def register_default_discounts():
    DiscountFactory.register("percent", lambda c: PercentDiscount(Decimal(str(c["value"])), c["name"]))
    DiscountFactory.register("fixed", lambda c: FixedDiscount(Decimal(str(c["value"])), Decimal(str(c["threshold"])), c["name"]))
    DiscountFactory.register("threeForTwo", lambda c: ThreeForTwoDiscount(c["category"], c["name"]))
    DiscountFactory.register("loyalty", lambda c: LoyaltyDiscount(Decimal(str(c.get("percent", 5))), int(c.get("days", 30)), c["name"]))
    DiscountFactory.register("freeDelivery", lambda c: FreeDeliveryDiscount(Decimal(str(c["threshold"])), c["name"]))
    DiscountFactory.register("firstOrder", lambda c: FirstOrderDiscount(Decimal(str(c.get("percent", 10))), c["name"]))
    DiscountFactory.register("promoCode", lambda c: PromoCodeDiscount(
        PromoConfig(
            code=c["code"],
            kind=c["kind"],
            value=Decimal(str(c["value"])),
            expires_at=c.get("expires_at"),
            active=bool(c.get("active", True))
        ), c.get("name")
    ))
