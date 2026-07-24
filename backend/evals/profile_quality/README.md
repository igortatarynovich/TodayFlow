# Profile quality eval (C3)

Canon: `docs/profile/PROFILE_CONTENT_CANON_V1.md`  
Code: `services/profile_content_v1/`

## First batch

10 scenarios in `scenarios_v1.json` (birth / onboarding / partial / check-ins / contradictory / premium).

```bash
# inside backend env with Nebius/LLM configured
python evals/profile_quality/run_review_packs_v1.py --batch first10
```

Outputs: `runs/review_packs_<UTC>/case_*.md` — full input · prompts · raw · final.

**Runtime note:** production funnel is 4 sync LLM steps. Audit runner uses **1 attempt** and stops after `patterns` (skips `spheres`) so a batch finishes in minutes, not ~50.

Latest salvage run: `runs/review_packs_20260721T085424Z/` (01–08 funnel partial; 09–10 timeout stubs).

## Method

Same as Compatibility: scorecard for technical defects; humans score value & natural RU.

---

## Life Path co-voice (identity)

Detect whether `numerology.life_path` is a real co-voice vs astro-only copy.

```bash
# LLM required (backend container or configured venv)
python evals/profile_quality/run_life_path_co_voice_eval_v0.py
```

Matrix A/B/C/D × 2 runs. Detector: `services/life_path_visibility_v0.py`.  
Release: `summary.release_ok == true` (no F1/F3/F4).

Do **not** use `run_review_packs_v1.py` for degradation forensics. Use:

```bash
python evals/profile_quality/run_production_capture_v0.py --cases A,B
```

- Same production funnel (4 steps, retry, quality validator, portrait builder)
- Sidecar pack: prompts/raw/parse/validation/snapshot/GET/QuickMap/visible_blocks
- Off by default; optional `--redact`
- **Eval-only** default HTTP timeout 120s via process env (does not change production Settings defaults)
- Spec: `docs/audits/PROFILE_PRODUCTION_CAPTURE_PACK.md`
- Case A/B report: `docs/audits/PROFILE_CAPTURE_CASE_AB_REPORT.md`

---

## Life spheres quality pack (deterministic projector)

Contrastive foundations for **love / money / decisions** — claim trace + product criteria (no LLM).

```bash
python evals/profile_quality/run_life_spheres_quality_pack_v0.py
```

- Cases: `life_spheres_quality_cases_v0.json` (8 contrast profiles)
- Outputs: `runs/life_spheres_quality_<UTC>/pack.{json,md}`
- SoT review: `docs/audits/PROFILE_LIFE_SPHERES_QUALITY_REVIEW_V0.md`

**Gate:** do not expand to other spheres until review D1/D2 (how traits + style buckets) are fixed.
