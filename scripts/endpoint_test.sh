#!/usr/bin/env bash
# Full endpoint test for the warehouse PO reconciliation API.
#
# Covers: vendors, products, product-vendors, purchase-orders (nested lines),
# po-line-items, packing-slips (nested lines), packing-slip-lines, receipts
# (create + PATCH decision), invoices, invoice-lines (price-mismatch flag).
#
# Run from anywhere; lib.sh cd's to the repo root and loads .env, then this
# resets the DB.
# Exits non-zero if any check fails, so CI can use it as-is later.
#
# Host port comes from APP_PORT (default 8090) to match compose.yml.
#
# Known gap: PackingSlipOut doesn't return its lines and there's no GET
# endpoint yet, so step 6 does one psql lookup to get the line ids.

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

echo "Target: $BASE_URL"
curl -sf "$BASE_URL/health" > /dev/null || { echo "API not reachable at $BASE_URL -- is the stack up?"; exit 1; }

reset_db

echo "== 1. Create vendor =="
check "create vendor" POST "/vendors/" '{"name": "Test Vendor"}'
VENDOR_ID=$(echo "$LAST_BODY" | json_get id)
echo "vendor_id=$VENDOR_ID"
echo

echo "== 2. Create product =="
check "create product" POST "/products/" '{
  "internal_sku": "SKU-TEST-1",
  "name": "Test Product",
  "manufacturer_id": 1,
  "category_id": 1,
  "product_type_id": 1,
  "brand_id": 1,
  "family_id": 1,
  "options": {"color": "blue", "size": "L"},
  "is_active": true
}'
PRODUCT_ID=$(echo "$LAST_BODY" | json_get id)
echo "product_id=$PRODUCT_ID"
echo

echo "== 3. Create product_vendor =="
check "create product_vendor" POST "/product-vendors/" "{
  \"product_id\": ${PRODUCT_ID:-0},
  \"vendor_id\": ${VENDOR_ID:-0},
  \"vendor_product_id\": \"VP-001\",
  \"cost\": 12.50,
  \"msrp\": 15.00,
  \"map_pricing\": 14.00,
  \"lead_time_days\": 7,
  \"minimum_order_qty\": 1,
  \"pack_qty\": 1,
  \"is_preferred\": true
}"
echo

echo "== 4. Create purchase_order with nested line items =="
check "create purchase_order" POST "/purchase-orders/" "{
  \"vendor_id\": ${VENDOR_ID:-0},
  \"created_by\": 1,
  \"description\": \"Test PO\",
  \"notes\": \"created by test script\",
  \"order_date\": \"2026-09-02\",
  \"line_items\": [
    {
      \"product_id\": ${PRODUCT_ID:-0},
      \"vendor_sku\": \"VP-001\",
      \"cost\": 12.50,
      \"qty_ordered\": 10,
      \"expected_delivery_date\": \"2026-09-15\"
    }
  ]
}"
PO_ID=$(echo "$LAST_BODY" | json_get id)
echo "po_id=$PO_ID"
echo

echo "== 5. Create standalone po_line_item (cost 12.50) =="
check "create po_line_item" POST "/po-line-items/" "{
  \"po_id\": ${PO_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"vendor_sku\": \"VP-001\",
  \"cost\": 12.50,
  \"qty_ordered\": 5,
  \"expected_delivery_date\": \"2026-09-15\",
  \"notes\": \"created by test script\"
}"
PO_LINE_ITEM_ID=$(echo "$LAST_BODY" | json_get id)
echo "po_line_item_id=$PO_LINE_ITEM_ID"
echo

echo "== 6. Create packing_slip with 3 nested lines (qty_shipped=10 each) =="
check "create packing_slip" POST "/packing-slips/" "{
  \"po_id\": ${PO_ID:-0},
  \"vendor_packing_slip_number\": \"PS-001\",
  \"tracking_number\": \"TRACK123\",
  \"received_date\": \"2026-09-03\",
  \"notes\": \"created by test script\",
  \"lines\": [
    {\"product_id\": ${PRODUCT_ID:-0}, \"qty_shipped\": 10},
    {\"product_id\": ${PRODUCT_ID:-0}, \"qty_shipped\": 10},
    {\"product_id\": ${PRODUCT_ID:-0}, \"qty_shipped\": 10}
  ]
}"
PACKING_SLIP_ID=$(echo "$LAST_BODY" | json_get id)
LINE_IDS=$(sql_val "SELECT id FROM packing_slip_line WHERE packing_slip_id = ${PACKING_SLIP_ID:-0} ORDER BY id;")
LINE_A=$(echo "$LINE_IDS" | sed -n '1p')
LINE_B=$(echo "$LINE_IDS" | sed -n '2p')
LINE_C=$(echo "$LINE_IDS" | sed -n '3p')
echo "packing_slip_id=$PACKING_SLIP_ID  line_a=$LINE_A  line_b=$LINE_B  line_c=$LINE_C"
echo

echo "== 7. Create standalone packing_slip_line =="
check "create packing_slip_line" POST "/packing-slip-lines/" "{
  \"packing_slip_id\": ${PACKING_SLIP_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_shipped\": 4
}"
echo

echo "== 8. Receipt: exact match (10 vs 10) -> auto, accepted=10 =="
check "receipt exact match" POST "/receipts/" "{
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"packing_slip_line_id\": ${LINE_A:-0},
  \"qty_counted\": 10
}"
assert_field "exact match status" approval_status auto
assert_field "exact match accepted" qty_accepted 10
RECEIPT_AUTO_ID=$(echo "$LAST_BODY" | json_get id)
echo

echo "== 9. Receipt: overage (13 vs 10) -> pending, is_overage =="
check "receipt overage" POST "/receipts/" "{
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"packing_slip_line_id\": ${LINE_B:-0},
  \"qty_counted\": 13,
  \"notes\": \"3 extra units on pallet\"
}"
assert_field "overage status" approval_status pending
assert_field "overage flag" is_overage true
RECEIPT_OVERAGE_ID=$(echo "$LAST_BODY" | json_get id)
echo

echo "== 10. Receipt: shortage (6 vs 10) -> pending, is_shortage =="
check "receipt shortage" POST "/receipts/" "{
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"packing_slip_line_id\": ${LINE_C:-0},
  \"qty_counted\": 6
}"
assert_field "shortage status" approval_status pending
assert_field "shortage flag" is_shortage true
echo

echo "== 11. Receipt: duplicate against line A -> pending, is_duplicate =="
check "receipt duplicate" POST "/receipts/" "{
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"packing_slip_line_id\": ${LINE_A:-0},
  \"qty_counted\": 10
}"
assert_field "duplicate status" approval_status pending
assert_field "duplicate flag" is_duplicate true
echo

echo "== 12. PATCH: approve the overage, keep the excess =="
check "approve overage receipt" PATCH "/receipts/${RECEIPT_OVERAGE_ID:-0}" '{
  "qty_accepted": 13,
  "approval_status": "approved",
  "approved_by": 1,
  "notes": "approved, keeping the extra 3 units"
}'
assert_field "approved status" approval_status approved
assert_field "approved quarantined" qty_quarantined 0
echo

echo "== 13. PATCH: re-deciding the auto receipt -> 400 =="
check "patch non-pending receipt" PATCH "/receipts/${RECEIPT_AUTO_ID:-0}" '{
  "qty_accepted": 10,
  "approval_status": "approved",
  "approved_by": 1
}' "400"
echo

echo "== 14. Create invoice =="
check "create invoice" POST "/invoices/" "{
  \"vendor_id\": ${VENDOR_ID:-0},
  \"vendor_invoice_number\": \"INV-1001\",
  \"invoice_date\": \"2026-10-11\",
  \"ship_start_date\": \"2026-10-01\",
  \"payment_due_date\": \"2026-11-10\",
  \"sub_total\": 125.00,
  \"tax_total\": 0.00,
  \"shipping_total\": 10.00,
  \"notes\": \"created by test script\"
}"
INVOICE_ID=$(echo "$LAST_BODY" | json_get id)
echo "invoice_id=$INVOICE_ID"
echo

echo "== 15. Invoice line: price matches PO cost (12.50) -> is_problem false =="
check "invoice line matching price" POST "/invoice-lines/" "{
  \"invoice_id\": ${INVOICE_ID:-0},
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_invoiced\": 5,
  \"price\": 12.50
}"
assert_field "matching price flag" is_problem false
echo

echo "== 16. Invoice line: overcharged (15.00 vs 12.50) -> is_problem true =="
check "invoice line overcharge" POST "/invoice-lines/" "{
  \"invoice_id\": ${INVOICE_ID:-0},
  \"po_line_item_id\": ${PO_LINE_ITEM_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_invoiced\": 5,
  \"price\": 15.00
}"
assert_field "overcharge flag" is_problem true
echo

echo "== 17. Invoice line: nonexistent po_line_item -> 404 =="
check "invoice line bad po_line_item" POST "/invoice-lines/" "{
  \"invoice_id\": ${INVOICE_ID:-0},
  \"po_line_item_id\": 999999,
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_invoiced\": 1,
  \"price\": 12.50
}" "404"
echo

echo "== 18. Free item: PO line cost 0.00, invoiced 0.00 -> is_problem false =="
check "create free po_line_item" POST "/po-line-items/" "{
  \"po_id\": ${PO_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"vendor_sku\": \"VP-FREE\",
  \"cost\": 0.00,
  \"qty_ordered\": 1,
  \"expected_delivery_date\": \"2026-09-15\"
}"
FREE_LINE_ID=$(echo "$LAST_BODY" | json_get id)
check "invoice line free item" POST "/invoice-lines/" "{
  \"invoice_id\": ${INVOICE_ID:-0},
  \"po_line_item_id\": ${FREE_LINE_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_invoiced\": 1,
  \"price\": 0.00
}"
assert_field "free item flag" is_problem false
echo

echo "== 19. Free item billed anyway (5.00) -> is_problem true =="
check "invoice line free item billed" POST "/invoice-lines/" "{
  \"invoice_id\": ${INVOICE_ID:-0},
  \"po_line_item_id\": ${FREE_LINE_ID:-0},
  \"product_id\": ${PRODUCT_ID:-0},
  \"qty_invoiced\": 1,
  \"price\": 5.00
}"
assert_field "free item billed flag" is_problem true
echo

echo "== Receipt table =="
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c \
  "SELECT id, packing_slip_line_id, qty_counted, qty_accepted, qty_quarantined, is_overage, is_shortage, is_duplicate, approval_status FROM receipt ORDER BY id;"

echo "== Invoice lines =="
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c \
  "SELECT id, invoice_id, po_line_item_id, price, is_problem FROM invoice_line ORDER BY id;"

echo "======================"
echo "Passed: $PASS  Failed: $FAIL"
[[ $FAIL -eq 0 ]]