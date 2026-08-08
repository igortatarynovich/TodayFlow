# Day Atmosphere art seeds

Source PNG mockups for Day Atmosphere photo wash (`FOUNDATION_UI` §13).

Runtime serves compressed WebP under `frontend/public/images/backgrounds/`:

- `{1–5}.webp` — desktop wash (~20–55 KB)
- `{1–5}-m.webp` — mobile wash (~12–25 KB)

Do not put these PNGs back in `public/` — they are art-direction seeds only (~1.5–2.2 MB each).

Regenerate WebP (from repo root):

```bash
python3 <<'PY'
from pathlib import Path
from PIL import Image, ImageFilter
seed = Path('frontend/art-seeds/day-atmosphere')
out = Path('frontend/public/images/backgrounds')
for i in range(1, 6):
    im = Image.open(seed / f'{i}.png').convert('RGB')
    w, h = im.size
    desk = im.filter(ImageFilter.GaussianBlur(0.6))
    desk.save(out / f'{i}.webp', 'WEBP', quality=78, method=6)
    mw, mh = 900, max(1, round(h * 900 / w))
    mob = im.resize((mw, mh), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(1.1))
    mob.save(out / f'{i}-m.webp', 'WEBP', quality=68, method=6)
PY
```
