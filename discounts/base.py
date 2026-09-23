from abc import ABC, abstractmethod
from decimal import Decimal
from enum import IntEnum

from models.pricing import AppliedDiscount, DiscountContext

class DiscountStage(IntEnum):
    QUANTITY = 1
    PERCENT = 2
    FIXED = 3
    DELIVERY = 4

class DiscountStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def stage(self) -> DiscountStage:
        ...

    @property
    def conflict_group(self) -> str | None:
        return None

    @property
    def conflict_priority(self) -> int:
        return 0

    @abstractmethod
    def apply(self, context: DiscountContext) -> AppliedDiscount | None:
        ...
