# Swiss Ephemeris data (FLG_SWIEPH)

Required compressed files for production accuracy (1800–2400 CE):

- `sepl_18.se1` — planets
- `semo_18.se1` — Moon
- `seas_18.se1` — main asteroids (Chiron etc.)

Source: [aloistr/swisseph ephe](https://github.com/aloistr/swisseph/tree/master/ephe)

`AstroEngine` refuses to start / compute if these are missing and Swiss would
silently fall back to Moshier (`FLG_MOSEPH`).
