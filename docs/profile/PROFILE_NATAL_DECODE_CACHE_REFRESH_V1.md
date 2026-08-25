# Natal Decode Cache Refresh V1

**Date:** 2026-08-25  
**Status:** **LOCKED** — ops one-shot moves persisted Natal Decode to the live `natal_decode_depth_v0.3` fingerprint. **Not** a semantic pass. **Not** IL-2/3/4. **Not** prompt/gate change. **Not** `active`. **Not** Profile polish reopen. **Not** GET auto-rebuild. **Not** client «собрать ещё раз».  
**Canon:** [PROFILE_NATAL_DECODE_DEPTH_V1.md](./PROFILE_NATAL_DECODE_DEPTH_V1.md) (one-shot + ops path) · [PROFILE_MEANING_POLISH_V1.md](./PROFILE_MEANING_POLISH_V1.md) (1.3.123 stands). Inventory: step 46 · KC-C-DECODE-CACHE-REFRESH. AGENTS.md Architecture impact.

This pass answers: **how existing cached decode reaches the 1.3.123 polish fingerprint** without reopening meaning.

Catalog **38 draft / 0 `active`**. Unchanged.

---

## Architecture impact

- **SoT before:** 1.3.123 put `decode_version` in the fingerprint (`natal_decode_depth_v0.3`) and bound sky theses to IL-4. GET `/account/profile/natal-decode` matches that fingerprint only. Production still had grounded v0.2 logs (prompt 1.0.1). GET therefore returned `access: offer` / `can_generate: true` — polish never ran for those profiles. Client `force_refresh` was already ignored; `ops_force` was named and unimplemented.
- **SoT after:** **Natal Decode Cache Refresh V1** is the ops one-shot named in Natal Decode Depth. `generate_natal_decode_depth_v0(ops_force=True)` skips fingerprint cache. Script `backend/scripts/natal_decode_cache_refresh_v1.py` inventories latest success logs and rebuilds named users. GET still never LLM. Client still cannot force. Identity Core stays CE. Prompt **1.1.0** / polish 1.3.123 unchanged. Public JSON fields unchanged; GET `version` on a ready artifact is the **persisted** version, not a live stamp over stale prose. Installed-package `load_objects()` reads `TODAYFLOW_DATA_DIR` (compose `/DATA`) — not a lemma/IL-2 rewrite; without it attach FileNotFound and refresh cannot run.
- **Public contract changed?** no — no new fields. GET ready `version` is honest to the stored artifact.
- **Migration required?** yes — ops `--apply` for stale users (not GET, not FE CTA spam). Sample lock: users **1** and **2**.
- **Canon updated?** yes — this file · IL §6.72 · inventory KC-C-DECODE-CACHE-REFRESH + step 46 · natal decode · handoff · tracker
- **Backward compatible?** yes — fingerprint miss still offers generate; v0.2 logs remain unread until refresh

---

## 0. Contract

| Rule | Do | Do not |
|------|----|--------|
| Rebuild | Explicit ops `ops_force` / script `--apply` | GET `/natal-decode` · core-profile GET · publish · FE button |
| Client | Ignore `force_refresh` | Treat POST as spam regenerate |
| Fingerprint | Live `DECODE_VERSION` (`v0.3`) | Rewrite IL lemmas · bump prompt |
| Identity | Keep CE `thesis_key` | Overwrite portrait / `character_engine_v1` |
| Scope | Natal Decode Depth only | Today native · CE cascade · catalog `active` |
| Proof | `v0.2` → `v0.3`, prompt 1.1.0, thesis unchanged, `writes_character_engine=false` | Invent quality pass from ops output |

`GET never rebuilds.` Inventory is not a rebuild signal.

---

## 1. Hook

| Step | Location |
|------|----------|
| Inventory | `list_latest_natal_decode_by_user` · `decode_cache_state` |
| Ops generate | `generate_natal_decode_depth_v0(..., ops_force=True)` |
| Script | `backend/scripts/natal_decode_cache_refresh_v1.py` (`--list` default · `--apply --user-ids`) |
| Catalog path | `load_objects()` reads `TODAYFLOW_DATA_DIR` (`/DATA` in compose), not site-packages `parents[4]/DATA` |

Prompt version unchanged: `profile.natal_decode_depth.v1` **1.1.0**. Artifact version: `natal_decode_depth_v0.3`.

---

## 2. This pass does not do

- IL lemma / pack / schema / `active`
- Prompt or editorial-gate change (1.3.123 stands)
- CE / personality_v1 inject
- Today native refresh
- Frontend chrome / scroller named pass
- Quality pass on Profile prose

---

## Changelog

- **1.0 (2026-08-25)** — 1.3.124. Ops cache refresh onto v0.3 fingerprint. Public contracts unchanged. Production sample (users 1, 2) `--apply` blocked on Nebius K3 402; v0.2 success logs remain latest.
