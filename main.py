from datetime import date
from decimal import Decimal

from models.product import Product
from models.cart_item import CartItem
from models.customer import Customer
from models.order import Order
from config.config_provider import ConfigProvider
from factory.discount_factory import DiscountFactory, register_default_discounts
from engine.pricing_engine import PricingEngine

def main():
    register_default_discounts()
    provider = ConfigProvider()
    provider.set_discount_configs([
        {"type": "threeForTwo", "category": "Книги", "name": "3 по цене 2"},
        {"type": "percent", "value": 10, "name": "Осенняя распродажа"},
        {"type": "fixed", "value": 500, "threshold": 3000, "name": "500 рублей от 3000"},
        {"type": "loyalty", "percent": 5, "days": 30, "name": "Лояльность"},
        {"type": "freeDelivery", "threshold": 5000, "name": "Бесплатная доставка"},
    ])

    strategies = [
        DiscountFactory.create(c["type"], c)
        for c in provider.get_discount_configs()
    ]

    books = Product("1", "Книга", Decimal("1000"), "Книги")
    phone = Product("2", "Телефон", Decimal("4000"), "Электроника")
    customer = Customer("C1", date(2026, 9, 1), False)
    order = Order(
        id="ORD-001",
        customer=customer,
        items=[CartItem(books, 3), CartItem(phone, 1)],
        promo_code=None,
        created_at=date(2026, 9, 23),
        delivery_cost=Decimal("300")
    )

    result = PricingEngine(strategies).calculate(order)

    print(f"Base total: {result.base_total:.2f}")
    print("Applied discounts:")
    for discount in result.applied_discounts:
        print(f"- {discount.name}: -{discount.amount:.2f} ({discount.reason})")
    print(f"Final total: {result.final_total:.2f}")

if __name__ == "__main__":
    main()
