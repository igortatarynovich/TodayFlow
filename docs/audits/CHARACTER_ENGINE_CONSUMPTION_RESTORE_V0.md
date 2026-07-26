# Character Engine — live Profile consumption restore + thesis leak scrub

**Date:** 2026-07-26  
**Status:** LIVE

## Problem

1. Backend container lost CE env vars (`.env` had `PROFILE_CONSUMPTION=1` / `PUBLISH_READY=1`, but running process had none → settings all `False`). Profile looked empty of Why / Effort / 7 spheres despite CE `ready`.
2. Stage 4 generic potential embedded machine thesis ids (`builds_through_water_care`) into person-facing Effort copy.

## Fix

| Change | Detail |
|--------|--------|
| Recreate backend with CE flags from `.env` | all Stage shadow + `PROFILE_CONSUMPTION=1` + `PUBLISH_READY=1` |
| Compose default | `CHARACTER_ENGINE_PROFILE_CONSUMPTION:-1` (was `:-0`) |
| `.env.production.example` | consumption default on with cutover |
| Stage 4 `_generic_life` | human thesis labels in `surface_text` |
| Consumption scrub | replace `builds_through_*` before writing contract / helps |

## Smoke (user 26 / snapshot 28)

- `applied=True`, label=`Забота`
- spheres: love/money/decisions/work/family/friends/body
- why + effort + bridge present
- seed remains `Observer` for illustration

## Ops note

Shell can sticky-set CE flags and override compose interpolation. Always `set -a; . ./.env; set +a` (or explicit export) before `docker compose … up` backend. Verify with `docker exec … printenv | grep CHARACTER_ENGINE` and settings flags.

## Architecture impact

- **SoT before:** CE ready but consumption off → funnel/partial contract still on screen without CE Why/Effort.
- **SoT after:** consumption on → CE overwrites journey slots on GET (ephemeral).
- **Public contract changed?** no required fields; richer ephemeral nests when flag on.
- **Migration required?** no
- **Canon updated?** this audit + tracker
- **Backward compatible?** yes
