from decimal import Decimal
from datetime import date

def check_quantity_discrepancy(ordered_qty: int, received_qty: int) -> dict:
    if received_qty < ordered_qty:
        return {"status": "short_shipped", "difference": ordered_qty - received_qty}
    elif received_qty > ordered_qty:
        return {"status": "over_shipped", "difference": received_qty - ordered_qty}
    return {"status": "ok", "difference": 0}

def check_price_discrepancy(expected_price: Decimal, received_price: Decimal, tolerance_pct: float) -> dict:

    pct_diff: float = round((abs(expected_price - received_price) / expected_price) * 100, 2)
    price_diff: Decimal = abs(expected_price - received_price)

    if received_price < expected_price and pct_diff >= tolerance_pct:
        return {"status": "under_charged", "difference": expected_price - received_price, "pct_diff": pct_diff}
    elif received_price > expected_price:
        return {"status": "over_charged", "difference": received_price - expected_price, "pct_diff": pct_diff}
    return {"status": "ok", "difference": price_diff, "pct_diff": pct_diff}

def check_delivery_timing(expected_date: date, received_date: date) -> dict:
    return {}

def is_duplicate_receipt(receipt_id: int, existing_receipt_ids: list[int]) -> bool:
    return False

def reconcile_line_item(line_item: dict, receipt: dict, tolerance_pct: float = 0.02) -> dict:
    return {}
