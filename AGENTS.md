# AGENTS.md — TodayFlow agent operating rules

## Sources of truth (priority)

Product authority is **not** Git. Use this stack, top wins on conflict:

1. **Canon** — living docs under `docs/` (start: `docs/README.md` reading order). Meaning, contracts, UX jobs, generation rules.
2. **Backlog / tracker** — `docs/PRODUCT_EXECUTION_TRACKER.md` (and explicit product backlog the owner points to). What to build next, done/in-progress, change log.
3. **Server** — what is actually running in production (`todayflow.today` / compose stack). Runtime behavior and live contracts beat any branch story.

**Git** is a **ledger** of commits and PRs: history of what was proposed or deployed, review trail, rollback aid. It must not invent product meaning. Commit messages and PR titles must not hide Source of Truth (canon/contract) changes behind cleanup language.

When code, canon, and server disagree: **fix the mismatch**, then fix toward **canon + backlog intent**, verify on **server**.

## Before changing generation / contracts / UI narrative

1. Name the **canonical documents and current contracts** you actually opened (paths + sections).
2. Prefer the smallest blast radius that matches the declared intent.
3. Do not introduce a new “canonical / SoT / hard gate / v2” label without deleting or officially deprecating the previous source.

## Architecture impact (mandatory for qualifying PRs)

Any PR that changes **at least one** of:

- Source of Truth (canon meaning)
- generation contract
- public JSON contract
- fallback semantics
- generation order / pipeline stages
- value gate (meaning rules for hide/show or accept/reject)
- composition pipeline (what the UI treats as the day/profile story)

**must** include a dedicated PR section:

```markdown
## Architecture impact

- **SoT before:** …
- **SoT after:** …
- **Public contract changed?** yes/no — what field/semantics
- **Migration required?** yes/no — note / version bump
- **Canon updated?** yes/no — path to doc + section
- **Backward compatible?** yes/no — what breaks if old clients/cache remain
```

If the PR title sounds like cleanup (“scrub text”, “value gate”, “improve narrative”) but any Architecture impact answer is non-trivial, **split the PR** or rename it to an explicit migration.

### Examples that require Architecture impact

| Change | Why |
|--------|-----|
| Post-LLM hard overwrite of `expect`/`trap`/`do`/`avoid` by formula bank | Formula becomes SoT for user text, not a quality limiter |
| Making `day_story.story` optional when slots exist | Public contract / validation semantics |
| Duplicating value-gate rule lists on FE and BE | Two decision authorities for the same meaning |
| Changing chapter order or which slot prints where | Composition pipeline |

### Safe pattern for editorial formulas (default unless canon says otherwise)

Fill empty slots · reject invalid output · fix only clear violations.  
Do **not** unconditionally replace LLM (or event-derived) prose after generation unless that overwrite is the declared SoT in canon + Architecture impact.

### Value gate placement (default)

Meaning rules (leakage, system language, claim-without-evidence) live in **one backend place**. 
Frontend may keep only a defensive minimum: null, empty string, trivial exact duplicates.

**Transport failure (system-wide):** never invent product content (calm rows, sphere dictionary, “нет сигнала”, offline story) when a request fails or `is_fallback`/`degraded` is set. Say the failure plainly — **«Нет соединения.»** on network/API throw; **«Не удалось загрузить.»** when the server flagged unavailable. Empty UI is allowed; fake calm is not.

## After the change (honest close-out)

Report facts, not literary summary:

1. Contract delta (fields / requiredness / semantics)
2. What is now SoT for user-facing text (cite canon path)
3. What was hardcoded
4. What was removed or deprecated
5. **Server check** (endpoint/UI observed) · tests run (command + result); do not claim CI green unless GitHub checks on the SHA show it
6. Tracker/backlog updated if the work item status changed
7. Remaining risks

## Related canons (start here; do not invent a fifth)

- `docs/foundation_v1.md` — **Foundation v1** (geometry · atomic constants · single-source routing); gate before hooks/semantics
- `docs/SCREEN_CONTRACTS_V1.md` — screen / today_contract / day_story nests
- `docs/content/TODAYFLOW_VOICE_CANON.md` — person-not-system
- `docs/DAY_ENGINE_AND_COHERENCE.md` / `docs/DAY_SOURCES_CANON.md` — day calculation SoT
- `docs/today-language/TODAY_LANGUAGE_V1.md` — language quality (TL-1 gated separately)
- `docs/profile/PROFILE_SCREEN_MASTER.md` · `docs/profile/PROFILE_EXPERIENCE_SCENARIO_V1.md` · `docs/TODAYFLOW_FOUNDATION_UI.md` — Character Engine / Profile UI / visual SoT
- `docs/PRODUCT_EXECUTION_TRACKER.md` — backlog / progress
