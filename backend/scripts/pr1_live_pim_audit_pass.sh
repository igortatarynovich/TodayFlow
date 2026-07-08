#!/usr/bin/env bash
# One real S0→S5 pass: meaning_events + guide generation + pim_read_audit linkage.
set -euo pipefail

API="${API_BASE:-http://localhost:8080}"
EMAIL="pr1-live-audit-$(date +%s)@example.com"
PASS="testpassword123"
TODAY=$(date +%Y-%m-%d)

echo "=== PR1 live PIM audit pass ==="
echo "API=$API user=$EMAIL date=$TODAY"

signup=$(curl -sf -X POST "$API/auth/signup" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}")
token=$(python3 -c "import json,sys; print(json.load(sys.stdin)['token'])" <<<"$signup")
auth="Authorization: Bearer $token"
user_id=$(python3 -c "import json,sys; print(json.load(sys.stdin)['user_id'])" <<<"$signup")
echo "auth ok"

post_event() {
  local type="$1" key="$2" payload="${3:-null}"
  curl -sf -X POST "$API/meaning/events" \
    -H 'Content-Type: application/json' \
    -H "$auth" \
    -d "{\"events\":[{\"event_type\":\"$type\",\"event_source\":\"today\",\"local_date\":\"$TODAY\",\"idempotency_key\":\"$key\",\"payload\":$payload}]}" || {
      echo "FAILED event $type" >&2
      return 1
    }
  echo "  event: $type"
}

post_event day_opened "pr1-day-opened-$TODAY"
post_event day_sky_fact_viewed "pr1-sky-$TODAY" '{"fact_kind":"moon_phase"}'
post_event tarot_selected "pr1-tarot-sel-$TODAY" '{"tarot_main_id":16}'
post_event tarot_revealed "pr1-tarot-rev-$TODAY" '{"tarot_main_id":16,"tarot_name_ru":"Башня"}'
post_event number_selected "pr1-num-$TODAY" '{"numerology_value":"21"}'

narrative=$(curl -sf -X POST "$API/today/narrative" \
  -H 'Content-Type: application/json' \
  -H "$auth" \
  -d "{\"target_date\":\"$TODAY\",\"surface\":\"guide\",\"ritual_context\":{\"tarot_main_id\":16,\"tarot_name_ru\":\"Башня\",\"numerology_value\":\"21\",\"head_topic\":\"work\"}}")
gen_id=$(python3 -c "import json,sys; print(json.load(sys.stdin)['generation_log_id'])" <<<"$narrative")
echo "guide generation_log_id=$gen_id"

post_event first_synthesis_viewed "pr1-syn-$TODAY" "{\"generation_id\":$gen_id,\"surface\":\"guide\"}"
echo "  event: first_synthesis_viewed (generation_id=$gen_id)"

echo ""
echo "--- SQL verification (docker postgres) ---"
docker exec todayflow-postgres-1 psql -U postgres -d todayflow -v ON_ERROR_STOP=1 -c "
SELECT event_type, COUNT(*) AS n
FROM meaning_events
WHERE user_id = $user_id
  AND event_type IN (
    'day_opened','day_sky_fact_viewed','tarot_selected','tarot_revealed',
    'number_selected','first_synthesis_viewed'
  )
GROUP BY event_type
ORDER BY event_type;

SELECT id, surface, created_at,
  (input_payload::text LIKE '%pim_read_audit%') AS has_pim_audit,
  input_payload->'orchestration'->'pim_read_audit'->'dre_fields_used' AS dre_fields_used
FROM generation_logs
WHERE id = $gen_id;
"

echo ""
echo "generation_id for chain: $gen_id"
