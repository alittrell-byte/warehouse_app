# Shared helpers for endpoint_test.sh and demo.sh. Source it, don't run it.
#
# Loads .env from the repo root, sets BASE_URL / DB_USER / DB_NAME, and
# provides the request, JSON and psql helpers both scripts use.

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

set -a
[ -f .env ] && source .env
set +a

BASE_URL="http://localhost:${APP_PORT:-8090}"
DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
PASS=0
FAIL=0

# Wipes every table so each run starts from the same empty state.
reset_db() {
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -q -c \
    "TRUNCATE TABLE vendor, product, product_vendor, purchase_order, po_line_item, packing_slip, packing_slip_line, receipt, invoice, invoice_line RESTART IDENTITY CASCADE;" \
    || { echo "TRUNCATE failed -- missing table? run the migrator first"; exit 1; }
}

# Runs one HTTP request and sets LAST_STATUS and LAST_BODY. Same rule as
# check(): call as a plain statement, never inside $(...).
http() {
  local method="$1" path="$2" data="$3" resp
  resp=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" \
    -H "Content-Type: application/json" -d "$data")
  LAST_STATUS=$(echo "$resp" | tail -n1)
  LAST_BODY=$(echo "$resp" | sed '$d')
}

# Runs one HTTP request, prints PASS/FAIL, updates counters, sets LAST_BODY.
# Call as a plain statement, never inside $(...): a subshell would swallow
# the PASS/FAIL updates.
check() {
  local name="$1" method="$2" path="$3" data="$4" expected="${5:-200 201}"
  http "$method" "$path" "$data"
  if [[ " $expected " == *" $LAST_STATUS "* ]]; then
    echo "PASS  $name  ($LAST_STATUS)"
    PASS=$((PASS+1))
  else
    echo "FAIL  $name  ($LAST_STATUS, expected one of: $expected)"
    FAIL=$((FAIL+1))
  fi
  echo "$LAST_BODY"
}

# Pulls one key out of a JSON body. Booleans print lowercase, missing -> "".
json_get() {
  python3 -c '
import sys, json
try:
    v = json.load(sys.stdin).get(sys.argv[1], "")
    print(str(v).lower() if isinstance(v, bool) else ("null" if v is None else v))
except Exception:
    print("")
' "$1"
}

# Asserts a field in LAST_BODY. A 200 alone doesn't prove the logic worked.
assert_field() {
  local name="$1" field="$2" expected="$3" actual
  actual=$(echo "$LAST_BODY" | json_get "$field")
  if [[ "$actual" == "$expected" ]]; then
    echo "PASS  $name  ($field=$actual)"
    PASS=$((PASS+1))
  else
    echo "FAIL  $name  ($field: expected '$expected', got '$actual')"
    FAIL=$((FAIL+1))
  fi
}

sql_val() {
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -tA -c "$1"
}
