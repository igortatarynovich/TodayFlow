# Tarot Golden Eval — live report #2 · 2026-07-26

**Mode:** live · **Dataset:** `tarot_golden_dataset_v1` (12)  
**Machine report:** [TAROT_GOLDEN_EVAL_LIVE_2026-07-26.json](./TAROT_GOLDEN_EVAL_LIVE_2026-07-26.json)  
**Canon:** [TAROT_GOLDEN_EVAL_V1.md](../tarot/TAROT_GOLDEN_EVAL_V1.md)  
**Prior:** [live #1 2026-07-25](./TAROT_GOLDEN_EVAL_LIVE_2026-07-25.md) (LLM 7/12)

## Verdict

**Freeze lift gate: YES** (`freeze_lift_ready=true`) — harness threshold met (≥85% LLM).  
**Owner still decides** whether to lift architecture freeze.

| Gate | Result |
|------|--------|
| pack_pass | 12/12 |
| llm_pass | **11/12** (~91.7%, need ≥ 85%) |
| critical shape | pass |
| anti-sameness | pass (~0.027) |
| rubric_mean | ~3.94 |

## Delta vs #1

- LLM: 7/12 → **11/12**
- Only fail: `choice_work_leave_or_stay` (`llm_fail_or_quality_reject` → thin fallback; shape still OK; rubric_mean 3.625 with `answered_question=1`)
- Nebius timeouts occurred mid-run; eval completed anyway

## Next

1. Owner call on freeze lift given gate green.
2. Q3: choice compact story + length budget (`tarot-interpretation-v1.6`) — then re-check `choice_work_leave_or_stay`.
3. **Ops (2026-07-26):** Tarot LLM uses `background` timeout (45s prod / 180s live eval); JSON→plain fallback skipped on ReadTimeout — root cause of many empty_response was sync 12s cutting ~22s DeepSeek generations.
