# Profile Selection K3 usage audit harness (2026-08-29)

**Status:** harness implemented. Phase 2.6 audit report is still blocked on K3/billing top-up; once `POST /chat/completions` = 200, run the harness against a real K3 Profile Decode response.

**Purpose:** measure which of the ~24 IL-3 themes in a Profile Decode prompt K3 actually cites, ignores, or competes with. Do not blindly cut Profile to 5–8 themes without these facts.

**Scope:** `services/il3_profile_usage_audit_v1.py` + `tests/test_il3_profile_usage_audit_v1.py`. No IL-3 meaning changes. No public JSON changes. No LLM calls in the harness itself.

---

## What the harness does

1. `make_synthetic_profile_pack()` returns a deterministic 24-line natal IL-4 pack:
   - 10 `planet_in_house` lines
   - 10 `planet_in_sign` lines
   - 4 `aspect_pair` lines
2. `evaluate_citation(response_text, pack)` counts how many of those lines are cited by the response.
3. Per-line topic mapping is taken from `services/il4_selection_v1` (`ASTRO_OBJECT_TOPIC_MAP` + `SIGN_TOPIC_MAP`), so we can report coverage per `ProfileTopicDomain`.
4. `audit_report(response_text, pack)` produces a tracker-ready summary.

## Citation rules

For each IL-4 line the harness builds a set of markers:

- object ids from the line's `jobs` → English/Russian planet/sign/house names;
- the line's own `text` plus each word in it.

A line is **cited** if any marker appears in the response text (case-insensitive, word boundaries for short tokens). This is intentionally conservative: a single word match counts as a citation, but it is enough to surface ignored themes.

## Example output

```python
from todayflow_backend.services.il3_profile_usage_audit_v1 import audit_report, make_synthetic_profile_pack

pack = make_synthetic_profile_pack()
report = audit_report(k3_response_text, pack, response_source="k3")
```

```json
{
  "response_source": "k3",
  "pack_shape": {"surface": "profile", "tone": "structural", "line_count": 24},
  "summary": {
    "cited": 9,
    "ignored": 15,
    "coverage_ratio": 0.375,
    "topic_coverage_ratio": {
      "relationships": 0.25,
      "work": 0.5,
      ...
    }
  },
  "ignored_lines": [
    {"rank": 3, "text": "Mercury in 3th house", "topics": ["decision", "work", "relationships"]}
  ]
}
```

## How to run the real audit once billing is restored

1. Pick a user with a grounded Character Engine Identity Core and a natal chart.
2. Generate a Profile Decode response via `services/natal_decode_depth_v0.py`.
3. Capture the raw IL-4 pack that was sent to the prompt (from `il4_surface_attach_v1.attach_il4_expression_pack(surface="profile", natal=...)`).
4. Feed the K3 response text + pack into `audit_report()`.
5. Record the summary in `docs/PRODUCT_EXECUTION_TRACKER.md` and decide whether to:
   - keep the full 24-line bag,
   - add a stronger deterministic selection before the prompt, or
   - adjust the object→topic mapping.

Do not cut the bag size without repeating the audit on at least 3 diverse natal charts.

## Tests

```bash
cd /opt/TodayFlow/backend
.venv/bin/python -m pytest tests/test_il3_profile_usage_audit_v1.py -q
```

All green.

## Architecture impact

- **SoT before:** no reusable way to measure K3 citation of IL-3 themes; Phase 2.6 was blocked on manual prompt inspection.
- **SoT after:** a deterministic, test-covered harness that can evaluate any K3/mocked response against a known IL-4 pack and report per-topic coverage.
- **Public contract changed?** no.
- **Migration required?** no.
- **Canon updated?** yes — this file · `docs/PRODUCT_EXECUTION_TRACKER.md`.
- **Backward compatible?** yes (read-only analysis tool).

---

## Changelog

- **1.0 (2026-08-29)** — Harness implemented; blocked on live K3 response until billing is restored.
