from app.services.reconciliation import check_quantity_discrepancy, check_price_discrepancy

####################################
# 
# testing check_quantity_discrepancy
#
####################################
def test_qty_short_shipped():
    result = check_quantity_discrepancy(ordered_qty=100, received_qty=80)
    assert result["status"] == "short_shipped"
    assert result["difference"] == 20

def test_qty_over_shipped():
    result = check_quantity_discrepancy(ordered_qty=100, received_qty=120)
    assert result["status"] == "over_shipped"
    assert result["difference"] == 20

def test_qty_exact_match():
    result = check_quantity_discrepancy(ordered_qty=100, received_qty=100)
    assert result["status"] == "ok"

####################################
# 
# testing check_price_discrepancy
#
####################################

def test_under_charged_over_threshold():
    result = check_price_discrepancy(expected_price=49.99, received_price=40.00, tolerance_pct=.02)
    assert result["status"] == "under_charged"
    assert result["difference"] == 9.99
    # 19.98
    assert result["pct_diff"] == pytest.approx(19.98, 0.01) 

def test_over_charged_over_threshold():
    result = check_price_discrepancy(expected_price=49.99, received_price=60.00, tolerance_pct=.02)
    assert result["status"] == "over_charged"
    assert result["difference"] == 10.01
    assert result["pct_diff"] == 20.02

def test_under_charged_under_threshold():
    result = check_price_discrepancy(expected_price=49.99, received_price=49.90, tolerance_pct=.02)
    assert result["status"] == "ok"
    assert result["difference"] == .09
    # 19.98
    assert result["pct_diff"] == 0.18

def test_over_charged_under_threshold():
    result = check_price_discrepancy(expected_price=49.99, received_price=50.15, tolerance_pct=.02)
    assert result["status"] == "ok"
    assert result["difference"] == 0.16
    assert result["pct_diff"] == 0.32

def test_exact_price_match():
    result = check_price_discrepancy(expected_price=49.99, received_price=49.99, tolerance_pct=.02)
    assert result["status"] == "ok"
