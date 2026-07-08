# TodayFlow Astrology Service

Dedicated microservice for astronomical calculations (Sun/Moon/Rising symbols, houses, etc.). Reference: [docs/ASTROLOGY_MACHINE_CONTRACT.md](../docs/ASTROLOGY_MACHINE_CONTRACT.md).

## Why isolate it?
- Keeps Swiss Ephemeris and astro libraries out of the core API image.
- Lets us swap implementations without touching the Narrative Engine.
- Aligns with the runtime architecture doc (backend orchestrates, astro focuses on math).

## Stack
- Python 3.11
- FastAPI + Uvicorn
- `pyswisseph` (install locally for precise chart calculations)

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
