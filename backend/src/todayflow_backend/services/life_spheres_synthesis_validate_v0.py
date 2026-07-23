"""Validate profile.spheres.synthesis.v1 output (schema + claim bans + distinctness)."""

from __future__ import annotations

import re
from typing import Any

SPHERE_FIELDS = ("how", "need", "risk", "turns_on", "turns_off", "helps")

# Word-boundary markers (avoid "марс" ⊂ "равновесие", "регулярно" ⊂ "регулярность").
_ASTRO_RES = (
    re.compile(r"\b(венера|юпитер|сатурн|меркурий|марс|плутон|луна|солнце)\b"),
    re.compile(r"\b(venus|jupiter|saturn|mercury|mars|pluto|ascendant)\b"),
    re.compile(r"\bасцендент\b"),
    re.compile(r"\bнаталь\w*\b"),
    re.compile(r"в знаке"),
    re.compile(r"\b\d+\s*дом\b"),
    re.compile(r"в доме"),
    re.compile(r"доме:"),
)
_SYSTEM_RES = (
    re.compile(r"система не"),
    re.compile(r"\bllm\b"),
    re.compile(r"\bалгоритм\w*\b"),
    re.compile(r"\bsnapshot\b"),
    re.compile(r"\bprojector\b"),
    re.compile(r"\beligibility\b"),
    re.compile(r"\bsynthesis\b"),
    re.compile(r"\bengine\b"),
    re.compile(r"воронк"),
    re.compile(r"недостаточно данных"),
)
_DAY_RES = (
    re.compile(r"\bсегодня\b"),
    re.compile(r"на сегодня"),
    re.compile(r"чего ждать"),
    re.compile(r"сферы сегодня"),
    re.compile(r"\btoday\b"),
)
_LONGITUDINAL_RES = (
    re.compile(r"\bрегулярно\b"),
    re.compile(r"\bкаждый раз\b"),
    re.compile(r"по чек-инам"),
    re.compile(r"as your days show"),
    re.compile(r"\bвсегда\b"),
)
_GENERIC_FILLER = (
    "энергия вселенной",
    "гармония во всём",
    "просто доверьтесь",
    "особая связь с космосом",
    "потенциал раскрытия",
)


def normalize_text(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def _norm(t: str) -> str:
    return normalize_text(t)


def _tokens(t: str) -> set[str]:
    return {x for x in re.findall(r"[a-zа-яё]{3,}", _norm(t))}


def jaccard(a: str, b: str) -> float:
    sa, sb = _tokens(a), _tokens(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _jaccard(a: str, b: str) -> float:
    return jaccard(a, b)


def validate_sphere_synthesis_v0(
    row: dict[str, Any] | None,
    *,
    identity_core: str = "",
    relevant_style: str = "",
    sphere_cues: list[str] | None = None,
    houses_available: bool = False,
) -> dict[str, Any]:
    """Return {ok, fields, defects, checks}."""
    defects: list[dict[str, str]] = []
    checks: dict[str, bool] = {}
    if not isinstance(row, dict):
        return {
            "ok": False,
            "fields": {},
            "checks": {"schema": False},
            "defects": [{"class": "RESPONSE_SCHEMA", "note": "not a JSON object"}],
        }

    cleaned: dict[str, str] = {}
    for field in SPHERE_FIELDS:
        raw = row.get(field)
        text = str(raw or "").strip()
        cleaned[field] = text
        min_len = 40 if field == "how" else 20
        max_len = 420 if field == "how" else 280
        if len(text) < min_len:
            defects.append({"class": "RESPONSE_SCHEMA", "note": f"{field}: too short (<{min_len})"})
        elif len(text) > max_len:
            defects.append({"class": "RESPONSE_SCHEMA", "note": f"{field}: too long (>{max_len})"})
    checks["schema"] = not any(d["class"] == "RESPONSE_SCHEMA" for d in defects)

    blob_all = " ".join(_norm(cleaned[f]) for f in SPHERE_FIELDS)
    astro_ok = not any(r.search(blob_all) for r in _ASTRO_RES)
    if not houses_available:
        # Ban house claims without time; allow ordinary words like «дома» in other senses carefully.
        astro_ok = astro_ok and not re.search(r"\b\d+\s*дом\b|в доме|доме:", blob_all)
    checks["no_astro_kitchen"] = astro_ok
    if not astro_ok:
        defects.append({"class": "VALIDATION", "note": "planet/sign/house/system kitchen leaked into copy"})

    system_ok = not any(r.search(blob_all) for r in _SYSTEM_RES)
    checks["voice"] = system_ok
    if not system_ok:
        defects.append({"class": "VALIDATION", "note": "system/kitchen language in output"})

    day_ok = not any(r.search(blob_all) for r in _DAY_RES)
    checks["no_day_language"] = day_ok
    if not day_ok:
        defects.append({"class": "VALIDATION", "note": "day agenda language in static sphere copy"})

    long_ok = not any(r.search(blob_all) for r in _LONGITUDINAL_RES)
    checks["no_longitudinal"] = long_ok
    if not long_ok:
        defects.append({"class": "BLOCK_PURPOSE", "note": "longitudinal claim without living evidence"})

    generic_ok = not any(m in blob_all for m in _GENERIC_FILLER)
    checks["no_generic_filler"] = generic_ok
    if not generic_ok:
        defects.append({"class": "VALIDATION", "note": "generic filler phrase"})

    # Distinct from identity / style
    how = cleaned["how"]
    id_ok = not identity_core or _jaccard(how, identity_core) < 0.45
    style_ok = not relevant_style or _jaccard(how, relevant_style) < 0.55
    # style paste into any field
    for field in SPHERE_FIELDS:
        if relevant_style and len(relevant_style) >= 24:
            chunk = _norm(relevant_style[:40])
            if chunk and chunk in _norm(cleaned[field]):
                style_ok = False
                defects.append({"class": "VALIDATION", "note": f"{field}: copies relevant_style chunk"})
                break
    checks["distinct_identity"] = id_ok
    checks["distinct_style"] = style_ok
    if not id_ok:
        defects.append({"class": "VALIDATION", "note": "how too close to identity_core"})
    if not style_ok and not any(d.get("note", "").startswith("copies relevant") for d in defects):
        defects.append({"class": "VALIDATION", "note": "how too close to relevant_style"})

    # Pairwise field distinctness
    distinct = True
    pairs = (
        ("need", "risk"),
        ("turns_on", "turns_off"),
        ("how", "helps"),
        ("need", "helps"),
        ("risk", "helps"),
    )
    for a, b in pairs:
        ta, tb = cleaned[a], cleaned[b]
        if ta and tb and (_norm(ta) == _norm(tb) or _jaccard(ta, tb) >= 0.85):
            distinct = False
            defects.append({"class": "VALIDATION", "note": f"{a}≈{b}"})
    checks["fields_distinct"] = distinct

    # helps action cue
    helps_blob = _norm(cleaned["helps"])
    helps_ok = bool(
        re.search(
            r"(назови|запиш|постав|реши|собери|ограничь|скажи|выбери|отдел|зафиксир|"
            r"один шаг|одной |написать|сказать|write |name |set |choose )",
            helps_blob,
        )
    ) or len(_tokens(cleaned["helps"])) >= 6
    checks["helps_action"] = helps_ok
    if not helps_ok:
        defects.append({"class": "VALIDATION", "note": "helps lacks actionable step"})

    # Cue grounding — share some lexical mass with cues (soft)
    cues = [c for c in (sphere_cues or []) if c]
    if cues:
        cue_tok = set()
        for c in cues:
            cue_tok |= _tokens(c)
        out_tok = _tokens(blob_all)
        overlap = len(cue_tok & out_tok) / max(1, len(cue_tok))
        grounded = overlap >= 0.08 or any(_jaccard(cleaned[f], c) >= 0.12 for f in SPHERE_FIELDS for c in cues)
        checks["cue_grounding"] = grounded
        if not grounded:
            defects.append({"class": "INPUT", "note": "output weakly grounded in sphere_cues"})
    else:
        checks["cue_grounding"] = False
        defects.append({"class": "INPUT", "note": "no sphere_cues provided"})

    ok = all(checks.values())
    return {"ok": ok, "fields": cleaned, "checks": checks, "defects": defects}
