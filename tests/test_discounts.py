import unittest
from datetime import date, timedelta
from decimal import Decimal

from models.product import Product
from models.cart_item import CartItem
from models.customer import Customer
from models.order import Order
from discounts.percent import PercentDiscount
from discounts.fixed import FixedDiscount
from discounts.three_for_two import ThreeForTwoDiscount
from discounts.loyalty import LoyaltyDiscount
from discounts.free_delivery import FreeDeliveryDiscount
from discounts.first_order import FirstOrderDiscount
from discounts.promo_code import PromoConfig, PromoCodeDiscount
from models.pricing import DiscountContext
from engine.pricing_engine import PricingEngine

class DiscountEngineTests(unittest.TestCase):
    def setUp(self):
        self.product = Product("1", "Книга", Decimal("1000"), "Книги")

    def order(self, items=None, customer=None, promo=None, delivery=Decimal("300"), created=date(2026, 9, 23)):
        return Order("O1", customer or Customer("C1", None, False),
                     items or [CartItem(self.product, 2)], promo, created, delivery)

    def test_percent_positive_and_negative(self):
        order = self.order()
        result = PricingEngine([PercentDiscount(Decimal("10"), "10%")]).calculate(order)
        self.assertEqual(result.final_total, Decimal("2100.00"))
        self.assertEqual(result.applied_discounts[0].amount, Decimal("200.00"))

        no = PricingEngine([PercentDiscount(Decimal("0"), "0%")]).calculate(order)
        self.assertEqual(no.applied_discounts, [])

    def test_fixed_threshold(self):
        order = self.order()
        result = PricingEngine([FixedDiscount(Decimal("500"), Decimal("2000"), "500 от 2000")]).calculate(order)
        self.assertEqual(result.final_total, Decimal("1800.00"))
        self.assertEqual(result.applied_discounts[0].amount, Decimal("200.00") if False else Decimal("500.00"))

        no = PricingEngine([FixedDiscount(Decimal("500"), Decimal("2001"), "500 от 2001")]).calculate(order)
        self.assertEqual(no.applied_discounts, [])

    def test_three_for_two_cheapest_free(self):
        cheap = Product("1", "Cheap", Decimal("500"), "Книги")
        expensive = Product("2", "Expensive", Decimal("1000"), "Книги")
        order = self.order([CartItem(cheap, 2), CartItem(expensive, 1)])
        result = PricingEngine([ThreeForTwoDiscount("Книги", "3 по цене 2")]).calculate(order)
        self.assertEqual(result.applied_discounts[0].amount, Decimal("500.00"))
        self.assertEqual(result.final_total, Decimal("1800.00"))

    def test_loyalty_boundary(self):
        customer = Customer("C1", date(2026, 8, 24), False)
        result = PricingEngine([LoyaltyDiscount()]).calculate(self.order(customer=customer))
        self.assertEqual(result.applied_discounts[0].amount, Decimal("100.00"))

        future = Customer("C1", date(2026, 9, 24), False)
        result = PricingEngine([LoyaltyDiscount()]).calculate(self.order(customer=future))
        self.assertEqual(result.applied_discounts, [])

    def test_first_order(self):
        customer = Customer("C1", None, True)
        result = PricingEngine([FirstOrderDiscount()]).calculate(self.order(customer=customer))
        self.assertEqual(result.applied_discounts[0].amount, Decimal("200.00"))

    def test_free_delivery_strict_threshold(self):
        order = self.order(delivery=Decimal("300"))
        result = PricingEngine([FreeDeliveryDiscount(Decimal("1999"), "Бесплатная доставка")]).calculate(order)
        self.assertEqual(result.final_total, Decimal("2000.00"))
        self.assertEqual(result.applied_discounts[0].amount, Decimal("300.00"))

        equal = self.order()
        result = PricingEngine([FreeDeliveryDiscount(Decimal("2000"), "Бесплатная доставка")]).calculate(equal)
        self.assertEqual(result.applied_discounts, [])

    def test_promo_vs_percent_promo_wins_tie(self):
        order = self.order(promo="SALE")
        strategies = [
            PercentDiscount(Decimal("10"), "Обычная 10%"),
            PromoCodeDiscount(PromoConfig("SALE", "percent", Decimal("10")), "SALE")
        ]
        result = PricingEngine(strategies).calculate(order)
        self.assertEqual(len(result.applied_discounts), 1)
        self.assertEqual(result.applied_discounts[0].name, "SALE")

    def test_large_fixed_never_negative(self):
        order = self.order()
        result = PricingEngine([FixedDiscount(Decimal("9999"), Decimal("0"), "Большая скидка")]).calculate(order)
        self.assertEqual(result.final_total, Decimal("300.00"))

if __name__ == "__main__":
    unittest.main()
