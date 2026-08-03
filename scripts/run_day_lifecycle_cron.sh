#!/usr/bin/env bash
# Day lifecycle + push due dispatcher (C5.1–C5.3 + rhythm).
# Install: every 10 minutes — see docs/audits/DAY_LIFECYCLE_V1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a
  # shellcheck disable=SC1090
  source .env
  set +a
fi
SECRET="${PUSH_DISPATCH_SECRET:-}"
if [[ -z "$SECRET" ]]; then
  echo "PUSH_DISPATCH_SECRET missing" >&2
  exit 1
fi
URL="${TODAYFLOW_INTERNAL_PUSH_URL:-http://127.0.0.1:8080/internal/push/run-due}"
# Prewarm can LLM for several users; 120s was timing out mid-assemble.
curl -sS -X POST "$URL" \
  -H "X-Push-Dispatch-Secret: ${SECRET}" \
  -H "Content-Type: application/json" \
  -d '{"max_prewarm":8}' \
  --max-time 600
echo
