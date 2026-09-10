# tests/test_reconciliation.py
from app.services.reconciliation import evaluate_receipt, evaluate_price
from decimal import Decimal

def test_exact_match_is_auto():
    result = evaluate_receipt(qty_counted=10, qty_shipped=10, is_duplicate=False)
    assert result["approval_status"] == "auto"
    assert result["qty_accepted"] == 10
    assert result["is_overage"] is False
    assert result["is_shortage"] is False

def test_overage_beyond_tolerance_is_pending():
    result = evaluate_receipt(qty_counted=13, qty_shipped=10, is_duplicate=False)
    assert result["approval_status"] == "pending"
    assert result["qty_accepted"] is None
    assert result["is_overage"] is True
    assert result["is_shortage"] is False

def test_shortage_beyond_tolerance():
    result = evaluate_receipt(qty_counted=10, qty_shipped=13, is_duplicate=False)
    assert result["approval_status"] == "pending"
    assert result["qty_accepted"] is None
    assert result["is_overage"] is False
    assert result["is_shortage"] is True

def test_duplicate_forces_pending_even_on_exact_match():
    result = evaluate_receipt(qty_counted=10, qty_shipped=10, is_duplicate=True)
    assert result["approval_status"] == "pending"
    assert result["qty_accepted"] is None
    assert result["is_overage"] is False
    assert result["is_shortage"] is False

def test_shortage_at_tolerance_boundary():
    result = evaluate_receipt(qty_counted=98, qty_shipped=100, is_duplicate=False)
    assert result["approval_status"] == "auto"
    assert result["qty_accepted"] == 98
    assert result["is_overage"] is False
    assert result["is_shortage"] is True

def test_shortage_just_past_tolerance_is_pending():
    # 3% variance -- now it should actually flip to pending
    result = evaluate_receipt(qty_counted=97, qty_shipped=100, is_duplicate=False)
    assert result["approval_status"] == "pending"
    assert result["qty_accepted"] is None
    assert result["is_shortage"] is True

def test_zero_shipped():
    result = evaluate_receipt(qty_counted=0, qty_shipped=10, is_duplicate=False)
    assert result["approval_status"] == "pending"
    assert result["qty_accepted"] is None
    assert result["is_overage"] is False
    assert result["is_shortage"] is True

def test_overage_and_shortage_are_mutually_exclusive():
    result = evaluate_receipt(qty_counted=13, qty_shipped=10, is_duplicate=False)
    assert not (result["is_overage"] and result["is_shortage"])

def test_overage_and_shortage_are_mutually_exclusive2():
    result = evaluate_receipt(qty_counted=10, qty_shipped=13, is_duplicate=False)
    assert not (result["is_overage"] and result["is_shortage"])

def test_exact_price_match_is_not_a_problem():
    result = evaluate_price(Decimal("12.50"), Decimal("12.50"))
    assert result["is_problem"] is False

def test_overcharge_beyond_tolerance():
    result = evaluate_price(Decimal("12.50"), Decimal("15.00"))
    assert result["is_problem"] is True
    assert result["direction"] == "over_charged"

def test_undercharge_beyond_tolerance():
    result = evaluate_price(Decimal("15.00"), Decimal("12.50"))
    assert result["is_problem"] is True
    assert result["direction"] == "under_charged"

def test_undercharge_at_tolerance():
    result = evaluate_price(Decimal("100.00"), Decimal("98.00"))
    assert result["is_problem"] is False

def test_overcharge_at_tolerance():
    result = evaluate_price(Decimal("100.00"), Decimal("102.00"))
    assert result["is_problem"] is False

def test_overcharge_just_over_tolerance():
    result = evaluate_price(Decimal("100.00"), Decimal("102.01"))
    assert result["is_problem"] is True
    assert result["direction"] == "over_charged"

def test_zero_charged():
    result = evaluate_price(Decimal("100.00"), Decimal("0.00"))
    assert result["is_problem"] is True
    assert result["direction"] == "under_charged"

def test_free_item():
    result = evaluate_price(Decimal("0.00"), Decimal("0.00"))
    assert result["is_problem"] is False