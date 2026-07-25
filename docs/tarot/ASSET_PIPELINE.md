# Tarot web asset pipeline

**UX / object language (канон сцены):** [TAROT_DESIGN_LANGUAGE_V1.md](./TAROT_DESIGN_LANGUAGE_V1.md) — принять до новых ритуальных UI.

## Layout

| Path | Role |
|------|------|
| `assets-source/tarot/masters/` | Licensed high-res masters (**gitignored**, never under `public/`) |
| `scripts/build-tarot-assets.py` | Generates AVIF + WebP at 384 / 576 / 768 |
| `frontend/public/images/cards/tarot/web/` | Production derivatives only |
| `frontend/src/data/tarotWebManifest.json` | Typed manifest for FE |

## Rebuild

```bash
# Masters at:
# assets-source/tarot/masters/white-witchcore/{Back Design.png,Major Arcana,Suit of …}
python3 scripts/build-tarot-assets.py
```

Commit `frontend/public/images/cards/tarot/web/**` and `frontend/src/data/tarotWebManifest.json`.

## Do not

- Put masters under `frontend/public/`
- Serve legacy 192×320 PNG on production paths
- Use emoji as card image fallback (use deck back + log)
