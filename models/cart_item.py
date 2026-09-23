from dataclasses import dataclass
from .product import Product

@dataclass(frozen=True)
class CartItem:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than 0")

    @property
    def total(self):
        return self.product.base_price * self.quantity
