# Interpretation Quality Audit — TodayFlow

**Date:** 2026-07-20  
**Scope:** Personal interpretations and all Today generation paths  
**Status:** Inventory + dual-influence fixes + eval harness shipped; full 100-scenario blind scoring in progress  
**Eval set:** [`backend/evals/interpretation_quality/scenarios_v1.json`](../../backend/evals/interpretation_quality/scenarios_v1.json) (100 scenarios)  
**Harness:** [`backend/evals/interpretation_quality/run_blind_compare_v1.py`](../../backend/evals/interpretation_quality/run_blind_compare_v1.py)

---

## 1. Карта всех генераций

| Surface | LLM? | Caller | Prompt ID / ver | Model | Temp | max_tokens | Contract | Cache / rebuild |
|---|---|---|---|---|---|---|---|---|
| **Day Story** (canon Today) | Yes | `day_story_v1.call_day_story_llm_v1` via `day_story_wire_v1` | `day-story-v1.1` | `resolve_default_chat_model()` → Nebius `deepseek-ai/DeepSeek-V4-Pro` | 0.52 | 1800 (+provider bump) | `day_story_v1` | Fingerprint SoT; refresh via `POST /today/story/refresh` |
| **Today Contract / Guide / Spheres / Day layer / Evening** | Derived from day_story (preferred) | `day_story_to_today_contract_v1` + narrative derive | inherits day-story | — | — | — | `today_contract_v1` | same fingerprint |
| **Legacy narrative funnel** (miss / deepen) | Yes | `today_narrative` / `guide_narrative_funnel_v0` | `today-narrative-v18` + `day.*.funnel.*.v1` @ 1.0.0 | default | 0.45–0.54 | funnel budgets | funnel contracts | GenerationLog same-day |
| **Morning foundation** | Yes | `morning_ritual` | `daily-foundation-v3` | default | 0.7 | 1200 | horoscope JSON | GenerationLog |
| **Morning recommendations** | Yes | `morning_ritual` | `daily-recommendation-v2` | default | 0.65 | 300 | do/avoid/focus | GenerationLog |
| **Card explainer** | Yes | `tarot_explainer.explain_tarot_card` | `tarot-explainer-v3` | default | 0.7 | 1000 | explainer JSON | GenerationLog; gated by symbol reveal |
| **Number explainer** | Yes | `numerology_explainer.explain_numerology_number` | `numerology-explainer-v3` | default | 0.7 | 1000 | explainer JSON | GenerationLog; GET explain 409 if not revealed |
| **Profile contract** | Yes | `profile_disclosure_funnel_v0` | `profile.*.v1` / `profile-contract-v3` | default | 0.48 | funnel_step | `profile_contract_v1` | snapshot hash |
| **First Result** | **No** | FE `buildFirstResultModel` | — | — | — | — | FirstResultModel | client templates |
| **Tomorrow** | **No** | FE `buildTomorrowContinuityHook` | — | — | — | — | string | **static RU string** |
| **Mood insights / Goals prose** | **No** | fingerprint drivers only | — | — | — | — | — | rebuild day_story on change |
| **Deepen** | Yes | narrative deepen funnel | `day.deepen.funnel.*.v1` | default | 0.5 | deepen table | deepen | by topic |

**Architecture (current):**

```
foundation + recommendations (LLM)
        ↓
ritual reveal → fingerprint change
        ↓
day_story_v1 (1× LLM) → today_contract + derive guide/spheres/evening
        ↓
legacy funnel only on miss / deepen
```

**Risk:** same “day spine / do-avoid” meaning can still be produced in foundation + recommendations + day_story + explainers when legacy path runs.

---

## 2. Prompt IDs и версии

| ID | Module |
|---|---|
| `day-story-v1.1` | day_story (bumped 2026-07-20: anti double-symbol + anti-cliché) |
| `today-narrative-v18` | legacy monolith |
| `today-narrative-funnel-v0-step1-interp` / `step2-satellites-v2` / `step3-core` | guide funnel |
| `day.guide|day_layer|spheres|evening|deepen.funnel.*.v1` @ 1.0.0 | registry |
| `daily-foundation-v3` | morning |
| `daily-recommendation-v2` | morning |
| `tarot-explainer-v3` | card |
| `numerology-explainer-v3` | number |
| `profile-contract-v3` + `profile.*.v1` | profile |
| `profile-interpreter-v8` | legacy profile |

---

## 3. Источники данных

| Prompt | Profile fields | Mood / goals | Local date | TZ | History | First Result | Card/number only after reveal | Interpretations vs raw | Extra / leak risk |
|---|---|---|---|---|---|---|---|---|---|
| day_story | compressed `user_core` | yes (ritual + fingerprint) | yes (fp) | yes (fp) | `day_history` optional | no | yes (SoT) | **raw ids in ritual_context**; brief prose slimmed | dual influence **mitigated** via `slim_day_engine_brief_for_story_llm` |
| daily-recommendation | natal slice | no mood/goals | date | no | no | no | depends on caller context | was raw **+** day_meaning → **fixed: raw only** | still parallel meaning vs day_story |
| tarot-explainer | natal slice | no | date | no | no | no | reveal gate | raw card + natal | OK for role |
| numerology-explainer | natal | no | — | no | no | no | GET 409 if not revealed | raw number + catalog day_meaning/title | intentional for explainer; do not feed into day_story |
| foundation | core_profile | no | date | — | no | no | n/a | forecast summary | spine for brief |
| First Result | birth draft FE | no | no | no | no | self | n/a | templates | looks personal, not LLM |
| Tomorrow | none | none | none | none | local evening close | no | n/a | static | **hardcode** |

### Double influence (карта / число)

| Path | Status |
|---|---|
| day_story: brief prose + ritual_context | **Fixed** — slim strips card/number lines when ritual has them |
| morning recommendations: number + day_meaning | **Fixed** — day_meaning removed from prompt |
| numerology explainer: number + day_meaning | **Accepted for explainer role**; must not be piped into day_story |
| legacy narrative on day_story miss | **Open P1** — brief still embeds symbol sentences + ritual |
| FE ritual bridge / personal insight | **Open P1** — client “interpretation” beside server story |

---

## 4. Роли блоков

| Block | Must | Must not |
|---|---|---|
| **First Result** | First personal effect + product value | Retell questionnaire; full horoscope; close all value pre-auth |
| **Day story** | Main day synthesis: user + mood + goals + day context; card/number as supplements | Dominate with symbols; invent facts; copy explainer prose |
| **Card** | Symbolic angle | Prediction / destiny |
| **Number** | Rhythm / focus | Duplicate card message |
| **Evening** | Reflect what the day was | Replay morning verbatim |
| **Tomorrow** | Continuity hook | Copy of Today with time swapped |

**Current role gaps:** First Result and Tomorrow are template/static — product-looking but not LLM-personal. Evening is good when derived from day_story `evening_closure`; weak on legacy fallback.

---

## 5. Найденный хардкод

### High risk (looks personal)

| Location | Issue |
|---|---|
| `frontend/src/lib/buildFirstResultModel.ts` | Template hero / traits / closing |
| `frontend/src/lib/firstTodayPackage.ts` | Named headlines / supports |
| `frontend/src/lib/todayDayContinuity.ts` | Tomorrow static RU string |
| `frontend/src/components/today/todayRitualCopy.ts` | Card+number bridge “interpretation” |
| `frontend/src/components/today/todayPageUtils.ts` | `buildPersonalInsight` assembly |
| `services/day_narrative_brief_v0.py` | Deterministic card/number/mood sentences |
| `services/day_story_v1.py` fallback | Fixed evening_closure / story from brief |
| `services/today_contract_fallbacks_v1.py` | Domain RU defaults |
| `core/tarot_explainer.py` / `numerology_explainer.py` fallbacks | Natal-anchored personal copy |
| `today_narrative.py` `_fallback_*` | Layer/spheres/evening/deepen |

### Acceptable / gated

| Location | Note |
|---|---|
| Profile forming messages | Explicitly non-rich |
| Weekly insight content DB | Deterministic catalog |

---

## 6. Evaluation set

- **File:** `backend/evals/interpretation_quality/scenarios_v1.json`
- **Count:** 100
- **Groups covered:** new_user, almost_empty, full, positive/anxious/tired mood, conflicting/no goals, card_only / number_only / both / nothing, repeating days, locales ru/en/pl, timezones, long/short input, contradictory onboarding, same card/number across users
- **Rubric criteria (1–5):** personal, natural, specific, no_cliche, no_repeat, no_hallucination, logical_coherence, mood_link, goals_link, card_influence_ok, number_influence_ok, shippable, length_ok, tone_ok, language_ok, continuity_ok
- **Primary KPI:** `% shippable without regen`
- **Secondary:** latency, input/output tokens, cost/Today, schema fail %, fallback %, regen %

---

## 7. Результаты DeepSeek

Pilot protocol: same day_story prompt (`day-story-v1.1`) + slim brief; Nebius Token Factory.  
Run: `evals/interpretation_quality/runs/results_raw_20260720T194602Z.jsonl` (n=4 scenarios, both models).

| Metric | DeepSeek-V4-Pro (pilot n=4) |
|---|---|
| Schema JSON ok | **4/4** |
| Latency mean / p50 | **41.5s / 53.0s** |
| Mean output chars | ~3288 |
| Cliche keyword hits | 0/4 (scan: возможно / позволь себе / вселенная…) |
| Human shippable % | **Pending blind score** — engineering sample looks shippable; not a verdict |

Notes: DeepSeek is slower than Kimi on this sample but returns complete rich contracts at temp 0.52 / 1800 tokens.

---

## 8. Сравнение с Kimi

| Metric | Kimi-K2.6 (pilot n=4) |
|---|---|
| Availability | Nebius `moonshotai/Kimi-K2.6` |
| Schema JSON ok | **4/4** (after token boost ≥4000; earlier run truncated at ~1800–2600) |
| Latency mean / p50 | **22.5s / 24.3s** |
| Mean output chars | ~2985 |
| Cliche keyword hits | 1/4 |
| Blind prefer rate | **Pending human A/B** — file `results_blind_20260720T194602Z.json` |

Engineering note (not a winner call): Kimi is faster and readable; DeepSeek slightly denser. Blind scoring required before model lock. Token budget for Kimi is now `max(requested*2+800, 4000)` in `resolve_max_tokens`.

**Rule:** no production model lock until blind eval on ≥20 then ≥100 scenarios across ru/en/pl.

---

## 9. Cross-block contradictions

| Check | Finding |
|---|---|
| First Result vs profile | Templates may not match later LLM profile — **P1** |
| Profile vs day_story | Separate prompts; no shared consistency evaluator — **P1** |
| Card vs number | Separate explainers; day_story may still over-merge — mitigated by roles in prompt |
| Day story vs explainer verbatim | Explainers not fed into day_story (good); FE bridge may still echo — **P1** |
| Evening vs morning | OK when evening_closure from same day_story; legacy fallback weak |
| Tomorrow vs Today | Tomorrow is static — not a true continuity generator — **P1** |
| Mood / goals weight | Fingerprint rebuild works; prompt asks mood not to capture whole text — needs eval |
| Symbol dominance | Dual-influence P0 fixed for day_story + recommendations |

---

## 10. Cost / latency

| Item | Baseline (pilot 2026-07-20) |
|---|---|
| Today happy path LLM calls | ~1 day_story (+ morning foundation/rec if cold) |
| day_story temp / tokens | 0.52 / 1800 (Kimi effective ≥4000) |
| DeepSeek day_story latency | ~13–55s (mean ~41s on n=4) |
| Kimi day_story latency | ~18–25s (mean ~22s on n=4) |
| Cost / Today | not metered in pilot — add token accounting next |
| Schema fail % (pilot) | 0% both after Kimi token fix |
| Fallback / regen % | not measured in harness yet |

Optimize cost only after shippable KPI.

---

## 11. Список дефектов

| ID | Module | Prompt | Repro | Actual | Expected | Sev | Cause | Fix | Test |
|---|---|---|---|---|---|---|---|---|---|
| IQ-001 | day_story | day-story-v1 | reveal card+number → story | brief prose + ritual doubled symbols | symbols once | **P0** | dual influence | `slim_day_engine_brief_for_story_llm` + prompt v1.1 | `test_day_engine_brief_slim_v1.py` |
| IQ-002 | morning rec | daily-recommendation-v2 | with day_number | raw + day_meaning | raw only | **P0** | dual influence | strip day_meaning from prompt | unit/prompt inspection |
| IQ-003 | FE Tomorrow | — | open Tomorrow hook | static string | personal continuity | **P1** | hardcode | generate from evening_closure + goals or drop claim of personalization | FE + eval |
| IQ-004 | FE First Result | — | guest first result | templates | short personal preview OR labeled non-LLM | **P1** | templates look LLM | tighten copy / length / no fake depth | FE audit |
| IQ-005 | FE ritual bridge | — | after reveal | client interprets card+number | point to server story / explainer | **P1** | hardcode | remove or gate bridge | FE |
| IQ-006 | legacy narrative | today-narrative-v18 | day_story miss | brief+ritual double | same slim policy | **P1** | parallel path | apply slim in funnel input | narrative tests |
| IQ-007 | explainers vs story | tarot/numerology-v3 | both on screen | overlapping do/avoid | distinct roles | **P1** | no role contract across surfaces | prompt role lines + cross-block evaluator | eval set |
| IQ-008 | model choice | — | product claim DeepSeek best | unproven | blind win on KPI | **P1** | no blind eval yet | run harness 100 | runs/ |
| IQ-009 | EN/PL day_story | day-story-v1.1 | locale=en/pl | RU system prompt still used | locale-matched system | **P1** | `_DAY_STORY_SYS_RU` for all | add EN/PL systems | locale scenarios |
| IQ-010 | consistency | — | full day | no automated cross-block judge | rule + LLM judge | **P2** | missing evaluator | consistency evaluator v0 | eval |

---

## 12. План исправлений

1. ~~Inventory~~  
2. ~~Dual-influence day_story + recommendations~~  
3. ~~Hardcode map~~  
4. ~~Eval set 100 + harness~~  
5. Run blind DeepSeek vs Kimi (pilot 8 → 20 → 100)  
6. Fix remaining P1 prompts (locale systems, legacy slim, explainer role lines)  
7. Soften / label First Result + Tomorrow hardcode  
8. Re-run eval; lock model only if KPI clear  
9. Cost trim last  

---

## 13. Приоритизированный backlog

| Priority | Item | Owner |
|---|---|---|
| P0 done | Slim brief for day_story; bump prompt v1.1 | eng |
| P0 done | Recommendations: no day_meaning double | eng |
| P0 done | Number explain gated on reveal | eng |
| P1 | Blind pilot + score shippable % | product+eng |
| P1 | EN/PL day_story system prompts | eng |
| P1 | Legacy funnel slim on miss | eng |
| P1 | Remove/gate FE ritual bridge + Tomorrow static | eng |
| P1 | Cross-block consistency evaluator v0 | eng |
| P2 | First Result length/value gate | product |
| P2 | Cost/token optimization | eng |

---

## Prompt quality checklist (day_story v1.1)

| Required | Forbidden | Good | Bad | Validation |
|---|---|---|---|---|
| One coherent day; fields distinct; facts only from JSON; symbols supplemental | Universe/flow clichés; invented events; double symbol essay; therapy filler | Specific mood+goals link; shippable story 3–5 sentences | Generic horoscope; copy of card meaning; empty schema | schema parse + eval rubric + fingerprint rebuild tests |

---

## Change log (this audit)

- 2026-07-20: inventory complete; IQ-001/002 fixes; eval set + blind harness; doc + canvas.
