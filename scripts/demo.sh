#!/usr/bin/env bash
# Narrated demo of the warehouse three-way match, for walking a reviewer
# through what the API does and the evidence that it works.
#
# One scenario: Acme Supply ships four products against one PO, the dock
# counts them, Acme invoices. Each act states a claim, makes the real API
# call, and checks the response. Exits non-zero if any claim fails.
#
# Usage: ./scripts/demo.sh [--pause]    (or: make demo)
#   --pause  wait for Enter between acts, for presenting live
#
# Resets the database at the start, same as endpoint_test.sh.

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

PAUSE=0
[[ "$1" == "--pause" ]] && PAUSE=1

if [ -t 1 ]; then
  BOLD=$'\e[1m' DIM=$'\e[2m' GREEN=$'\e[32m' RED=$'\e[31m' CYAN=$'\e[36m' RESET=$'\e[0m'
else
  BOLD='' DIM='' GREEN='' RED='' CYAN='' RESET=''
fi

act() {
  if [[ $PAUSE -eq 1 && "$1" != "0" ]]; then
    read -rp "${DIM}[Enter for act $1]${RESET}" _ < /dev/tty
  fi
  echo
  echo "${BOLD}${CYAN}== Act $1: $2 ==${RESET}"
}

say() { echo "$*"; }

# Prints the request line, then runs it. $1 is a short human summary of the
# payload so the output stays readable.
req() {
  local summary="$1" method="$2" path="$3" data="$4"
  echo "  ${DIM}→ $method $path  $summary${RESET}"
  http "$method" "$path" "$data"
}

# Prints selected fields from LAST_BODY next to the status code.
show() {
  local out="← $LAST_STATUS " f
  for f in "$@"; do
    out+=" $f=$(echo "$LAST_BODY" | json_get "$f")"
  done
  echo "  ${DIM}$out${RESET}"
}

# Asserts the claim against LAST_STATUS / LAST_BODY.
# Usage: claim "what this proves" http=200 field=value ...
claim() {
  local text="$1" pair key want got bad=""
  shift
  for pair in "$@"; do
    key="${pair%%=*}" want="${pair#*=}"
    if [[ "$key" == "http" ]]; then
      got="$LAST_STATUS"
    else
      got=$(echo "$LAST_BODY" | json_get "$key")
    fi
    [[ "$got" == "$want" ]] || bad+=" $key: expected '$want', got '$got';"
  done
  if [[ -z "$bad" ]]; then
    echo "  ${GREEN}✔ $text${RESET}"
    PASS=$((PASS+1))
  else
    echo "  ${RED}✘ $text --$bad${RESET}"
    FAIL=$((FAIL+1))
  fi
}

# Same as claim, for a value computed in the script rather than the response.
claim_eq() {
  local text="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    echo "  ${GREEN}✔ $text${RESET}"
    PASS=$((PASS+1))
  else
    echo "  ${RED}✘ $text -- expected '$want', got '$got'${RESET}"
    FAIL=$((FAIL+1))
  fi
}

echo "${BOLD}Warehouse three-way match: PO vs. received vs. invoiced${RESET}"
echo "Target: $BASE_URL"

# ---------------------------------------------------------------------------
act 0 "The platform is up and the schema is current"
say "Three Compose services: Postgres, a one-shot Alembic migrator, and the API."
say "The API only starts after the migrator exits 0."

curl -sf "$BASE_URL/health" > /dev/null \
  || { echo "${RED}API not reachable at $BASE_URL -- run 'make up' first${RESET}"; exit 1; }
docker compose ps -a --format '  {{.Service}}\t{{.Status}}' 2>/dev/null

claim_eq "API container reports healthy (Docker HEALTHCHECK on /health)" \
  "$(docker compose ps app --format '{{.Health}}' 2>/dev/null)" "healthy"
claim_eq "migrator ran to completion and exited 0" \
  "$(docker compose ps -a migrator --format '{{.State}} {{.ExitCode}}' 2>/dev/null)" "exited 0"

DB_REV=$(sql_val "SELECT version_num FROM alembic_version;")
HEAD_REV=$(docker compose exec -T app alembic heads 2>/dev/null | awk '{print $1}')
echo "  ${DIM}database at revision $DB_REV, latest migration in repo is $HEAD_REV${RESET}"
claim_eq "database schema is at the latest Alembic revision" "$DB_REV" "$HEAD_REV"

reset_db
say "Database reset to empty for a repeatable run."

# ---------------------------------------------------------------------------
act 1 "Setup: a vendor, four products, and what Acme charges for each"

req '{"name": "Acme Supply Co."}' POST "/vendors/" '{"name": "Acme Supply Co."}'
VENDOR_ID=$(echo "$LAST_BODY" | json_get id)
show id name
claim "vendor created" http=200

# name|sku|cost
PRODUCTS=(
  "Steel widget|WID-100|12.50"
  "Corner bracket|BRK-200|8.00"
  "Door hinge|HNG-300|4.25"
  "Bolt pack (M6)|BLT-400|0.80"
)
PRODUCT_IDS=()
for p in "${PRODUCTS[@]}"; do
  IFS='|' read -r name sku cost <<< "$p"
  http POST "/products/" "{
    \"internal_sku\": \"$sku\", \"name\": \"$name\",
    \"manufacturer_id\": 1, \"category_id\": 1, \"product_type_id\": 1,
    \"brand_id\": 1, \"family_id\": 1, \"options\": {}, \"is_active\": true
  }"
  pid=$(echo "$LAST_BODY" | json_get id)
  PRODUCT_IDS+=("$pid")
  http POST "/product-vendors/" "{
    \"product_id\": $pid, \"vendor_id\": $VENDOR_ID, \"vendor_product_id\": \"ACME-$sku\",
    \"cost\": $cost, \"msrp\": $cost, \"map_pricing\": $cost, \"lead_time_days\": 7,
    \"minimum_order_qty\": 1, \"pack_qty\": 1, \"is_preferred\": true
  }"
  printf '  %s→ %-16s %-8s $%s%s\n' "$DIM" "$name" "$sku" "$cost" "$RESET"
done
claim_eq "4 products and vendor cost records created" "${#PRODUCT_IDS[@]}" "4"
P_WID=${PRODUCT_IDS[0]} P_BRK=${PRODUCT_IDS[1]} P_HNG=${PRODUCT_IDS[2]} P_BLT=${PRODUCT_IDS[3]}

# ---------------------------------------------------------------------------
act 2 "Order: one purchase order, four lines"
say "The cost on each PO line is a snapshot of the agreed price at order time."
say "Invoices are checked against this, not against today's price list."

req "4 lines: widget x10, bracket x10, hinge x10, bolts x50" POST "/purchase-orders/" "{
  \"vendor_id\": $VENDOR_ID, \"created_by\": 1,
  \"description\": \"Q4 restock\", \"order_date\": \"2026-10-01\",
  \"line_items\": [
    {\"product_id\": $P_WID, \"vendor_sku\": \"ACME-WID-100\", \"cost\": 12.50, \"qty_ordered\": 10, \"expected_delivery_date\": \"2026-10-10\"},
    {\"product_id\": $P_BRK, \"vendor_sku\": \"ACME-BRK-200\", \"cost\": 8.00,  \"qty_ordered\": 10, \"expected_delivery_date\": \"2026-10-10\"},
    {\"product_id\": $P_HNG, \"vendor_sku\": \"ACME-HNG-300\", \"cost\": 4.25,  \"qty_ordered\": 10, \"expected_delivery_date\": \"2026-10-10\"},
    {\"product_id\": $P_BLT, \"vendor_sku\": \"ACME-BLT-400\", \"cost\": 0.80,  \"qty_ordered\": 50, \"expected_delivery_date\": \"2026-10-10\"}
  ]
}"
PO_ID=$(echo "$LAST_BODY" | json_get id)
show id status reconciliation_status
claim "PO created, waiting to be reconciled" http=200 status=created reconciliation_status=pending

# The PO response doesn't return its line ids (no GET endpoints yet).
mapfile -t PO_LINES < <(sql_val "SELECT id FROM po_line_item WHERE po_id = $PO_ID ORDER BY id;")
L_WID=${PO_LINES[0]} L_BRK=${PO_LINES[1]} L_HNG=${PO_LINES[2]} L_BLT=${PO_LINES[3]}
SNAP=$(sql_val "SELECT string_agg(cost::text, ',' ORDER BY id) FROM po_line_item WHERE po_id = $PO_ID;")
echo "  ${DIM}po_line_item.cost in the database: $SNAP${RESET}"
claim_eq "nested lines stored with their agreed cost" "$SNAP" "12.50,8.00,4.25,0.80"

# ---------------------------------------------------------------------------
act 3 "Shipment: Acme's packing slip says what they sent"
say "The packing slip is the vendor's claim. Dock counts get compared to it."

req "shipped: widget 10, bracket 10, hinge 10, bolts 50" POST "/packing-slips/" "{
  \"po_id\": $PO_ID, \"vendor_packing_slip_number\": \"ACME-PS-7781\",
  \"tracking_number\": \"1Z999AA10123456784\", \"received_date\": \"2026-10-09\",
  \"lines\": [
    {\"product_id\": $P_WID, \"qty_shipped\": 10},
    {\"product_id\": $P_BRK, \"qty_shipped\": 10},
    {\"product_id\": $P_HNG, \"qty_shipped\": 10},
    {\"product_id\": $P_BLT, \"qty_shipped\": 50}
  ]
}"
SLIP_ID=$(echo "$LAST_BODY" | json_get id)
show id vendor_packing_slip_number
claim "packing slip recorded" http=200

mapfile -t SLIP_LINES < <(sql_val "SELECT id FROM packing_slip_line WHERE packing_slip_id = $SLIP_ID ORDER BY id;")
S_WID=${SLIP_LINES[0]} S_BRK=${SLIP_LINES[1]} S_HNG=${SLIP_LINES[2]} S_BLT=${SLIP_LINES[3]}
claim_eq "4 slip lines stored" "${#SLIP_LINES[@]}" "4"

# ---------------------------------------------------------------------------
act 4 "Receiving: the dock counts each line"
say "Rule: within 2% of what was shipped is auto-accepted. Anything else,"
say "or a second count of the same line, goes to a person."

say
say "Widgets: shipped 10, counted 10."
req '{"qty_counted": 10}' POST "/receipts/" "{\"po_line_item_id\": $L_WID, \"packing_slip_line_id\": $S_WID, \"qty_counted\": 10}"
R_WID=$(echo "$LAST_BODY" | json_get id)
show approval_status qty_accepted is_overage is_shortage
claim "exact match is auto-accepted" approval_status=auto qty_accepted=10

say
say "Bolts: shipped 50, counted 51 (2% over)."
req '{"qty_counted": 51}' POST "/receipts/" "{\"po_line_item_id\": $L_BLT, \"packing_slip_line_id\": $S_BLT, \"qty_counted\": 51}"
show approval_status qty_accepted is_overage
claim "variance inside the 2% band is auto-accepted, but still marked as an overage" \
  approval_status=auto qty_accepted=51 is_overage=true

say
say "Brackets: shipped 10, counted 13."
req '{"qty_counted": 13}' POST "/receipts/" "{\"po_line_item_id\": $L_BRK, \"packing_slip_line_id\": $S_BRK, \"qty_counted\": 13, \"notes\": \"3 extra on the pallet\"}"
R_BRK=$(echo "$LAST_BODY" | json_get id)
show approval_status qty_accepted is_overage
claim "30% overage is held for review, nothing accepted yet" \
  approval_status=pending qty_accepted=null is_overage=true

say
say "Hinges: shipped 10, counted 6."
req '{"qty_counted": 6}' POST "/receipts/" "{\"po_line_item_id\": $L_HNG, \"packing_slip_line_id\": $S_HNG, \"qty_counted\": 6}"
show approval_status qty_accepted is_shortage
claim "40% shortage is held for review" approval_status=pending is_shortage=true

say
say "Someone scans the widget line a second time."
req '{"qty_counted": 10}  (same slip line)' POST "/receipts/" "{\"po_line_item_id\": $L_WID, \"packing_slip_line_id\": $S_WID, \"qty_counted\": 10}"
show approval_status is_duplicate
claim "duplicate count is flagged and held, even though the quantity matches" \
  approval_status=pending is_duplicate=true

say
say "A count against a slip line that doesn't exist."
req '{"packing_slip_line_id": 999999}' POST "/receipts/" "{\"po_line_item_id\": $L_WID, \"packing_slip_line_id\": 999999, \"qty_counted\": 1}"
show detail
claim "unknown slip line is rejected" http=404

# ---------------------------------------------------------------------------
act 5 "Review: a person decides the held receipts"

say "The receiving lead keeps the 3 extra brackets."
req '{"approval_status": "approved", "qty_accepted": 13}' PATCH "/receipts/$R_BRK" '{
  "qty_accepted": 13, "approval_status": "approved", "approved_by": 1,
  "notes": "keeping the extras, Acme credited them"
}'
show approval_status qty_accepted qty_quarantined is_overage
claim "decision recorded; nothing quarantined; the overage flag stays as history" \
  approval_status=approved qty_accepted=13 qty_quarantined=0 is_overage=true

say
say "Someone tries to re-decide the widget receipt the system already auto-accepted."
req '{"approval_status": "rejected"}' PATCH "/receipts/$R_WID" '{
  "qty_accepted": 0, "approval_status": "rejected", "approved_by": 1
}'
show detail
claim "only pending receipts can be decided" http=400

# ---------------------------------------------------------------------------
act 6 "Invoice: Acme bills us, each line is checked against the PO price"
say "Rule: more than 2% away from the PO line's snapshotted cost is a problem."

req '{"vendor_invoice_number": "ACME-INV-5521"}' POST "/invoices/" "{
  \"vendor_id\": $VENDOR_ID, \"vendor_invoice_number\": \"ACME-INV-5521\",
  \"invoice_date\": \"2026-10-12\", \"ship_start_date\": \"2026-10-08\",
  \"payment_due_date\": \"2026-11-11\", \"sub_total\": 312.97,
  \"tax_total\": 0.00, \"shipping_total\": 15.00
}"
INVOICE_ID=$(echo "$LAST_BODY" | json_get id)
show id vendor_invoice_number
claim "invoice header recorded" http=200

inv_line() {
  local po_line="$1" product="$2" qty="$3" price="$4"
  req "{\"qty_invoiced\": $qty, \"price\": $price}" POST "/invoice-lines/" "{
    \"invoice_id\": $INVOICE_ID, \"po_line_item_id\": $po_line,
    \"product_id\": $product, \"qty_invoiced\": $qty, \"price\": $price
  }"
}

say
say "Widgets billed at \$12.50 (PO: \$12.50)."
inv_line "$L_WID" "$P_WID" 10 12.50
show price is_problem
claim "matching price passes" is_problem=false

say
say "Brackets billed at \$8.12 (PO: \$8.00, 1.5% over)."
inv_line "$L_BRK" "$P_BRK" 13 8.12
show price is_problem
claim "small variance inside the 2% band passes" is_problem=false

say
say "Hinges billed at \$4.75 (PO: \$4.25, 11.8% over)."
inv_line "$L_HNG" "$P_HNG" 6 4.75
show price is_problem
claim "overcharge is flagged" is_problem=true

say
say "A line that points at a PO line that doesn't exist."
inv_line 999999 "$P_BLT" 51 0.80
show detail
claim "unknown PO line is rejected" http=404

# ---------------------------------------------------------------------------
act 7 "Exception report: what a person actually has to look at"
say "Of 5 dock counts and 3 billed lines, only these need attention:"
echo
docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -P footer=off -c "
SELECT 'receipt' AS kind, r.id, p.name AS product,
       CASE WHEN r.is_duplicate THEN 'duplicate count'
            WHEN r.is_overage   THEN 'over: counted ' || r.qty_counted || ' of ' || sl.qty_shipped
            ELSE                     'short: counted ' || r.qty_counted || ' of ' || sl.qty_shipped END AS issue
FROM receipt r
JOIN packing_slip_line sl ON sl.id = r.packing_slip_line_id
JOIN product p ON p.id = sl.product_id
WHERE r.approval_status = 'pending'
UNION ALL
SELECT 'invoice line', il.id, p.name,
       'billed ' || il.price || ', PO says ' || li.cost
FROM invoice_line il
JOIN po_line_item li ON li.id = il.po_line_item_id
JOIN product p ON p.id = il.product_id
WHERE il.is_problem
ORDER BY kind, id;"

EXCEPTIONS=$(sql_val "SELECT (SELECT count(*) FROM receipt WHERE approval_status = 'pending')
                           + (SELECT count(*) FROM invoice_line WHERE is_problem);")
claim_eq "exactly 3 exceptions: short hinges, duplicate widget scan, hinge overcharge" "$EXCEPTIONS" "3"

echo
TOTAL=$((PASS+FAIL))
if [[ $FAIL -eq 0 ]]; then
  echo "${BOLD}${GREEN}All $TOTAL claims checked against the live API and database. All passed.${RESET}"
else
  echo "${BOLD}${RED}$FAIL of $TOTAL claims failed.${RESET}"
fi
[[ $FAIL -eq 0 ]]
