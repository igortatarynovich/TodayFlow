#!/usr/bin/env bash
# Живой smoke против поднятого TodayFlow API (без pytest).
# Использование: API_BASE_URL=http://localhost:8080 bash scripts/smoke-live.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASE="${API_BASE_URL:-http://localhost:8080}"
BASE="${BASE%/}"

echo "Smoke API base: $BASE"

check() {
  local path="$1"
  local expect="${2:-200}"
  local code
  code="$(curl -sS -o /tmp/todayflow_smoke_body.json -w "%{http_code}" "$BASE$path")"
  if [[ "$code" != "$expect" ]]; then
    echo "FAIL $path → HTTP $code (expected $expect)" >&2
    head -c 500 /tmp/todayflow_smoke_body.json >&2 || true
    exit 1
  fi
  echo "OK   $path ($code)"
}

check "/tarot/daily/public"
check "/tarot/cards/0"
check "/tarot/cards/999" "404"
check "/compatibility/signs?from=aries&to=libra"
check "/reference/zodiac"
check "/reference/planets"

echo "All smoke checks passed."
