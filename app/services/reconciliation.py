from decimal import Decimal
from datetime import date
from typing import Optional, TypedDict


class ReceiptEvaluation(TypedDict):
    is_overage: bool
    is_shortage: bool
    approval_status: str
    qty_accepted: Optional[int]

def evaluate_receipt(
    qty_counted: int,
    qty_shipped: int,
    is_duplicate: bool,
    tolerance_pct: float = 0.02,

) -> ReceiptEvaluation:
    is_overage = qty_counted > qty_shipped
    is_shortage = qty_counted < qty_shipped

    variance_pct = abs(qty_counted - qty_shipped) / qty_shipped if qty_shipped else 1.0

    if is_duplicate or variance_pct > tolerance_pct:
        approval_status = "pending"
        qty_accepted = None
    else:
        approval_status = "auto"
        qty_accepted = qty_counted

    return {
        "is_overage": is_overage,
        "is_shortage": is_shortage,
        "approval_status": approval_status,
        "qty_accepted": qty_accepted
    }

def evaluate_price(expected_price: Decimal, invoiced_price: Decimal,
                   tolerance_pct: Decimal = Decimal("0.02")) -> dict:
    variance = invoiced_price - expected_price
    if expected_price == 0:
        # agreed price is free: only a problem if they billed anything
        variance_pct = Decimal(0) if invoiced_price == 0 else Decimal(1)
    else:
        variance_pct = abs(variance) / expected_price
    return {
        "is_problem": variance_pct > tolerance_pct,
        "direction": "over_charged" if variance > 0 else "under_charged" if variance < 0 else "match",
        "variance": variance,
        "variance_pct": variance_pct,
    }