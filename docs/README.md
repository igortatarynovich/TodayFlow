# TodayFlow documentation

**Единственная точка входа.** Остальные файлы в `docs/` доступны только через разделы ниже.

Agent rules: [AGENTS.md](../AGENTS.md) · Documentation process: [`.cursor/rules/docs-single-canon.mdc`](../.cursor/rules/docs-single-canon.mdc)  
Full file list (before any archive): [DOCUMENTATION_INVENTORY.md](./DOCUMENTATION_INVENTORY.md)

> Consolidated `PRODUCT_MAP.md` / `TECHNICAL_ARCHITECTURE.md` / `GENERATION_REGISTRY.md` / `IMPLEMENTATION_STATUS.md` / `screens/*` are **planned in PR-2**. Until then each section names the **interim** authority — update those files in place; do not add a competing SoT.

---

## 1. Product Map

What the product is, user path, and how we decide what to build.

| Role | Interim doc |
|------|-------------|
| Product model | [TODAYFLOW_PRODUCT_MODEL.md](./TODAYFLOW_PRODUCT_MODEL.md) |
| Build sequence (question → entity → sources → UI) | [TODAYFLOW_PRODUCT_BUILD_MAP.md](./TODAYFLOW_PRODUCT_BUILD_MAP.md) |
| Display honesty | [PRODUCT_TRUTH_FIRST.md](./PRODUCT_TRUTH_FIRST.md) |
| Progress / depth / missing | [UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md](./UNDERSTANDING_PROGRESS_AND_DEPTH_CANON.md) |
| First-day path | [FIRST_DAY_EXPERIENCE.md](./FIRST_DAY_EXPERIENCE.md) |

Related detail under this section: inventory → **Product Map**.

---

## 2. Technical Architecture

Services, Personal Model, data ownership, authoritative calculation paths.

| Role | Interim doc |
|------|-------------|
| Data ownership / consumption | [DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md](./DATA_OWNERSHIP_AND_CONSUMPTION_MAP.md) |
| Personal Intelligence Layer | [PERSONAL_INTELLIGENCE_LAYER.md](./PERSONAL_INTELLIGENCE_LAYER.md) |
| Explainable computation | [EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md](./EXPLAINABLE_COMPUTATION_AND_INTERPRETATION.md) |
| Reference / build order | [REFERENCE_LAYER_AND_BUILD_ORDER.md](./REFERENCE_LAYER_AND_BUILD_ORDER.md) |
| Astro machine contract | [ASTROLOGY_MACHINE_CONTRACT.md](./ASTROLOGY_MACHINE_CONTRACT.md) |

Stack snapshot (repo root): [README.md](../README.md).

Related detail under this section: inventory → **Technical Architecture**.

---

## 3. Generation Registry

Prompts, gates, schemas, voice — what may be generated and when.

| Role | Interim doc |
|------|-------------|
| Profile E2E reconstruction (eligibility before prompt) | [PROFILE_E2E_RECONSTRUCTION.md](./PROFILE_E2E_RECONSTRUCTION.md) |
| Profile prompt registry | [audits/PROFILE_E2E_PROMPT_REGISTRY.md](./audits/PROFILE_E2E_PROMPT_REGISTRY.md) |
| Voice | [content/TODAYFLOW_VOICE_CANON.md](./content/TODAYFLOW_VOICE_CANON.md) |
| LLM quality / prompt evolution | [LLM_QUALITY_AND_PROMPT_EVOLUTION.md](./LLM_QUALITY_AND_PROMPT_EVOLUTION.md) |

Related detail (passports, capture packs): inventory → **Generation Registry**. Prefer extending the prompt registry over new passport files.

---

## 4. Implementation Status

What works, what is partial/broken, what the next minimal PR is.

| Role | Interim doc |
|------|-------------|
| Execution tracker | [PRODUCT_EXECUTION_TRACKER.md](./PRODUCT_EXECUTION_TRACKER.md) |
| Web launch gaps / DoD | [status/WEB_LAUNCH_EXECUTION_PLAN.md](./status/WEB_LAUNCH_EXECUTION_PLAN.md) |
| Personal Model ↔ code (deltas) | [audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md](./audits/PERSONAL_MODEL_CODE_COMPLIANCE_2026-07-21.md) |
| Experience wiring | [audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md](./audits/PERSONAL_MODEL_EXPERIENCE_WIRING_P1_2026-07-21.md) |
| Documentation inventory | [DOCUMENTATION_INVENTORY.md](./DOCUMENTATION_INVENTORY.md) |

Audits stay as **delta lists**, not second architecture canons.

---

## 5. Screen Maps

What the user sees, block purpose, data source, CTA.

| Screen | Interim doc |
|--------|-------------|
| Today | [TODAY_SCREEN_V1_CANON.md](./TODAY_SCREEN_V1_CANON.md) · [TODAY_PERSONALIZATION_CORE.md](./TODAY_PERSONALIZATION_CORE.md) |
| Profile | [PR4_PROFILE_CANON.md](./PR4_PROFILE_CANON.md) · [PROFILE_CONTENT_CANON_V1.md](./PROFILE_CONTENT_CANON_V1.md) · [PROFILE_SCREEN_MASTER.md](./PROFILE_SCREEN_MASTER.md) |
| Compatibility | [COMPATIBILITY_CONTENT_CANON_V1.md](./COMPATIBILITY_CONTENT_CANON_V1.md) |
| Shared screen contracts | [SCREEN_CONTRACTS_V1.md](./SCREEN_CONTRACTS_V1.md) |
| Foundation UI | [TODAYFLOW_FOUNDATION_UI.md](./TODAYFLOW_FOUNDATION_UI.md) |

Related language/calibration packs: inventory → **Screen Maps**.

---

## Priority when documents disagree

1. Working **code + API contract** for the surface you are shipping  
2. The **interim doc** named in the section above for that topic  
3. [DOCUMENTATION_INVENTORY.md](./DOCUMENTATION_INVENTORY.md) to find subordinates — not to invent a new SoT  

There is **no** separate parallel “main product SoT” outside this README.
