from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class Customer:
    id: str
    last_purchase_date: Optional[date]
    is_first_order: bool
