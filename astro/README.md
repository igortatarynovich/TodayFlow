# TodayFlow Astrology Service

Dedicated microservice for astronomical calculations (Sun/Moon/Rising symbols, houses, etc.). Reference: [docs/ASTROLOGY_MACHINE_CONTRACT.md](../docs/ASTROLOGY_MACHINE_CONTRACT.md).

## Why isolate it?
- Keeps Swiss Ephemeris and astro libraries out of the core API image.
- Lets us swap implementations without touching the Narrative Engine.
- Aligns with the runtime architecture doc (backend orchestrates, astro focuses on math).

## Stack
- Python 3.11
- FastAPI + Uvicorn
- `pyswisseph` (Swiss Ephemeris; **dual license AGPL / Professional** — see `docs/foundation_v1.md` §1.4). Compressed ephe files reproduce NASA JPL **DE431**. Public copy claims: `docs/content/TODAYFLOW_TRUST_LAYER.md` · Foundation §1.4.1.

## License
Swiss Ephemeris is not “just a pip package.” Production must have either AGPL-compliant distribution or a Professional License from Astrodienst. This repo does not currently store that license.

## Running locally
```bash
cd astro
uv venv && source .venv/bin/activate
pip install -e .
uvicorn todayflow_astro.main:app --reload --port 8081
```

### API contract
- `POST /chart` accepts `{ "birth": { "date": "1992-03-14", "time": "07:12", "location": "Paris" }, "coordinates": { "latitude": 48.8566, "longitude": 2.3522 } }`
- Response includes `mode`, `positions` (sun/moon/rising), optional `houses`, and metadata.

Replace the placeholder math inside `services.engine.AstroEngine` with Swiss Ephemeris computations and plug in a real gazetteer lookup before launch.
