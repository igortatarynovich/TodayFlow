"""C3.5.1 — English editorial eval gate (parity with RU C3.1/C3.2).

Eval-only. Not wired into runtime refresh / Nebius path.
Semantic heuristics are score/warning weight — calibrate via golden set later.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
    CRITICAL_DEFECTS,
    DEFECT_AFFIRMATION_UNNATURAL,
    DEFECT_ASTRO_JARGON_BARE,
    DEFECT_BUREAUCRATIC,
    DEFECT_CATEGORICAL_PROMISE,
    DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
    DEFECT_CHORUS_PARALLEL_FORECAST,
    DEFECT_CHORUS_ROLE_DRIFT,
    DEFECT_CHORUS_SEMANTIC_DUPLICATION,
    DEFECT_CHORUS_UNTRANSLATED_JARGON,
    DEFECT_PSEUDO_DIAGNOSIS,
    DEFECT_SCENE_ABSTRACT,
    DEFECT_SCENE_CLONE,
    DEFECT_SCENE_MISSING_CHOICE,
    DEFECT_SCENE_MISSING_EVERYDAY,
    DEFECT_SCENE_UNIVERSAL_ADVICE,
    DEFECT_THESIS_ECHO,
    score_editorial_quality_c31,
)
from todayflow_backend.services.day_scenario_personalization_c33 import _as_dict, _as_list, _clip

# Locale / language mismatch (eval)
DEFECT_LOCALE_LANGUAGE_MISMATCH = "LOCALE_LANGUAGE_MISMATCH"

_EN_UNIVERSAL_RE = re.compile(
    r"("
    r"don'?t\s+rush|"
    r"take\s+a\s+pause|"
    r"listen\s+to\s+yourself|"
    r"trust\s+the\s+process|"
    r"find\s+balance|"
    r"stay\s+in\s+the\s+moment|"
    r"avoid\s+conflict|"
    r"set\s+healthy\s+boundaries|"
    r"be\s+mindful|"
    r"practice\s+self[- ]care"
    r")",
    re.I,
)

_EN_ABSTRACT_RE = re.compile(
    r"("
    r"in\s+relationships?\s+(there\s+may\s+be|tension\s+is\s+possible)|"
    r"the\s+\w+\s+sphere\s+is\s+highlighted|"
    r"energy\s+manifests|"
    r"pay\s+more\s+attention\s+to\s+the\s+area"
    r")",
    re.I,
)

_EN_CONCRETE_RE = re.compile(
    r"("
    r"message|chat|email|call|colleague|partner|deadline|draft|"
    r"kitchen|door|phone|meeting|invoice|reply|"
    r"moment\s+when|exactly\s+when|"
    r"\"[^\"]{4,}\"|"
    r"asks\s+you|texts?\s+you|writes?"
    r")",
    re.I,
)

_EN_ASTRO_RE = re.compile(
    r"("
    r"moon\s+in\s+\w+|sun\s+in\s+\w+|"
    r"mercury|venus|mars|jupiter|saturn|uranus|neptune|pluto|"
    r"square|trine|conjunction|opposition|retrograde|transit|"
    r"in\s+pisces|in\s+aries|in\s+taurus|in\s+gemini|in\s+cancer|"
    r"in\s+leo|in\s+virgo|in\s+libra|in\s+scorpio|in\s+sagittarius|"
    r"in\s+capricorn|in\s+aquarius"
    r")",
    re.I,
)

_EN_HUMAN_RE = re.compile(
    r"("
    r"so\s+|therefore|makes|becomes|noticeable|"
    r"you\s+want|easier|harder|louder|quieter|"
    r"emotion|word|reply|decision|tempo|pace|pause"
    r")",
    re.I,
)

_EN_PSEUDO_RE = re.compile(
    r"("
    r"you\s+are\s+codependent|"
    r"your\s+trauma|"
    r"narcissis|"
    r"you\s+are\s+in\s+denial|"
    r"clinical\s+|"
    r"personality\s+disorder|"
    r"you\s+don'?t\s+know\s+how\s+to\s+love"
    r")",
    re.I,
)

_EN_CATEGORICAL_RE = re.compile(
    r"("
    r"will\s+definitely\s+happen|"
    r"guaranteed\s+to|"
    r"you\s+must\s+|"
    r"inevitably\s+|"
    r"100\s*%|"
    r"without\s+exception\s+will"
    r")",
    re.I,
)

_EN_BUREAU_RE = re.compile(
    r"("
    r"optimize\s+the\s+process|"
    r"facilitate\s+communication|"
    r"within\s+the\s+framework\s+of\s+interaction|"
    r"actualize\s+the\s+request|"
    r"realize\s+the\s+intention|"
    r"ensure\s+balance\s+of\s+interests"
    r")",
    re.I,
)

_EN_AFFIRM_FAKE_RE = re.compile(
    r"("
    r"i\s+deserve\s+all\s+the\s+best|"
    r"the\s+universe\s+takes\s+care|"
    r"i\s+attract\s+abundance|"
    r"every\s+day\s+i\s+become\s+better|"
    r"i\s+radiate\s+love"
    r")",
    re.I,
)

_CYRILLIC_RE = re.compile(r"[а-яёА-ЯЁ]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")


def _defect(code: str, *, field: str, message: str, severity: str = "critical") -> dict[str, str]:
    return {"code": code, "field": field, "message": message, "severity": severity}


def _scene_blob(s: dict[str, Any]) -> str:
    return " ".join(
        str(s.get(k) or "")
        for k in ("setup", "opportunity", "trap", "recommended_action", "everyday_example", "avoid_action")
    )


def _jaccard(a: str, b: str) -> float:
    ta = {t.lower() for t in re.findall(r"[a-z0-9']+", a.lower()) if len(t) > 2}
    tb = {t.lower() for t in re.findall(r"[a-z0-9']+", b.lower()) if len(t) > 2}
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def detect_locale_language_mismatch(native: dict[str, Any], *, locale: str) -> list[dict[str, str]]:
    """RU locale should not be mostly Latin-only; EN should not be mostly Cyrillic."""
    loc = (locale or "ru").strip().lower()
    blobs: list[str] = []
    c = _as_dict(native.get("conflict"))
    blobs.extend(str(c.get(k) or "") for k in ("title", "thesis", "force_a", "force_b"))
    for s in _as_list(native.get("scenes")):
        if isinstance(s, dict):
            blobs.append(_scene_blob(s))
    text = " ".join(blobs)
    if not text.strip():
        return []
    cyr = len(_CYRILLIC_RE.findall(text))
    lat = len(_LATIN_WORD_RE.findall(text))
    total = cyr + lat
    if total < 8:
        return []
    if loc == "en" and cyr / total > 0.35:
        return [
            _defect(
                DEFECT_LOCALE_LANGUAGE_MISMATCH,
                field="locale",
                message="EN cell contains substantial Cyrillic prose",
            )
        ]
    if loc == "ru" and lat / total > 0.55 and cyr / total < 0.2:
        return [
            _defect(
                DEFECT_LOCALE_LANGUAGE_MISMATCH,
                field="locale",
                message="RU cell contains mostly Latin prose",
            )
        ]
    return []


def run_editorial_quality_gate_en_c351(native: dict[str, Any] | None) -> list[dict[str, str]]:
    """Parallel EN editorial checks (eval-only)."""
    if not isinstance(native, dict) or not native:
        return [_defect(DEFECT_SCENE_ABSTRACT, field="payload", message="native payload missing")]

    defects: list[dict[str, str]] = []
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    if not scenes:
        defects.append(_defect(DEFECT_SCENE_ABSTRACT, field="scenes", message="no scenes"))

    thesis = _clip(_as_dict(native.get("conflict")).get("thesis"), 240)
    scene_texts: list[str] = []
    for i, s in enumerate(scenes):
        field = f"scenes[{i}]"
        blob = _scene_blob(s)
        scene_texts.append(blob)
        everyday = _clip(s.get("everyday_example"), 240)
        if not everyday or len(everyday) < 20:
            defects.append(
                _defect(DEFECT_SCENE_MISSING_EVERYDAY, field=field, message="missing everyday_example")
            )
        elif not _EN_CONCRETE_RE.search(everyday) and not _EN_CONCRETE_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_SCENE_ABSTRACT,
                    field=field,
                    message="no concrete lived moment markers",
                )
            )
        if _EN_ABSTRACT_RE.search(blob):
            defects.append(_defect(DEFECT_SCENE_ABSTRACT, field=field, message="abstract sphere forecast"))
        if _EN_UNIVERSAL_RE.search(blob) and not _EN_CONCRETE_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_SCENE_UNIVERSAL_ADVICE,
                    field=field,
                    message="universal advice without concrete scene",
                )
            )
        if not str(s.get("opportunity") or "").strip() or not str(s.get("trap") or "").strip():
            defects.append(
                _defect(
                    DEFECT_SCENE_MISSING_CHOICE,
                    field=field,
                    message="missing opportunity/trap tension",
                    severity="soft",
                )
            )
        if thesis and token_overlap_high(thesis, blob):
            defects.append(_defect(DEFECT_THESIS_ECHO, field=field, message="thesis echoed in scene"))
        if _EN_PSEUDO_RE.search(blob):
            defects.append(_defect(DEFECT_PSEUDO_DIAGNOSIS, field=field, message="pseudo-diagnosis"))
        if _EN_CATEGORICAL_RE.search(blob):
            defects.append(_defect(DEFECT_CATEGORICAL_PROMISE, field=field, message="categorical promise"))
        if _EN_BUREAU_RE.search(blob):
            defects.append(
                _defect(DEFECT_BUREAUCRATIC, field=field, message="bureaucratic voice", severity="soft")
            )

    for i in range(len(scene_texts)):
        for j in range(i + 1, len(scene_texts)):
            if _jaccard(scene_texts[i], scene_texts[j]) >= 0.72:
                defects.append(
                    _defect(
                        DEFECT_SCENE_CLONE,
                        field=f"scenes[{i}|{j}]",
                        message="near-duplicate scenes",
                    )
                )

    # Chorus
    chorus = _as_dict(native.get("interpretive_chorus"))
    conflict_title = _clip(_as_dict(native.get("conflict")).get("title"), 120)
    voice_blobs: list[tuple[str, str]] = []
    for voice, key in (
        ("astrology", "astrology"),
        ("day_card", "day_card"),
        ("day_number", "day_number"),
        ("natal", "natal"),
    ):
        rows = chorus.get(key)
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            rows = []
        for ri, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            text = " ".join(str(row.get(k) or "") for k in row.keys())
            voice_blobs.append((voice, text))
            link = str(row.get("link_to_conflict") or "").strip()
            cid = str(row.get("conflict_id") or "").strip()
            if not link and not cid:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_PARALLEL_FORECAST,
                        field=f"chorus.{voice}[{ri}]",
                        message="unbound chorus voice (no link_to_conflict)",
                    )
                )
            if voice == "astrology" and _EN_ASTRO_RE.search(text) and not _EN_HUMAN_RE.search(text):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_UNTRANSLATED_JARGON,
                        field=f"chorus.{voice}[{ri}]",
                        message="astro jargon without human translation",
                    )
                )
                defects.append(
                    _defect(
                        DEFECT_ASTRO_JARGON_BARE,
                        field=f"chorus.{voice}[{ri}]",
                        message="bare astro jargon",
                    )
                )
            if voice == "natal":
                refs = _as_list(row.get("evidence_refs"))
                if not refs:
                    defects.append(
                        _defect(
                            DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
                            field=f"chorus.natal[{ri}]",
                            message="natal voice without evidence_refs",
                        )
                    )
            # Soft role drift: astrology talking only about "you usually"
            if voice == "astrology" and re.search(r"\byou\s+usually\b|\byour\s+chart\s+always\b", text, re.I):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=f"chorus.{voice}[{ri}]",
                        message="astrology voice drifts into natal personal habit",
                    )
                )

    for i in range(len(voice_blobs)):
        for j in range(i + 1, len(voice_blobs)):
            if voice_blobs[i][0] == voice_blobs[j][0]:
                continue
            if _jaccard(voice_blobs[i][1], voice_blobs[j][1]) >= 0.7:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_SEMANTIC_DUPLICATION,
                        field=f"chorus.{voice_blobs[i][0]}|{voice_blobs[j][0]}",
                        message="near-duplicate chorus voices",
                    )
                )

    props = _as_dict(native.get("prop_material") or native.get("props"))
    aff = _as_dict(props.get("affirmation_tension") or props.get("affirmation"))
    aff_text = str(aff.get("text") or "")
    if aff_text and _EN_AFFIRM_FAKE_RE.search(aff_text):
        defects.append(
            _defect(DEFECT_AFFIRMATION_UNNATURAL, field="prop_material.affirmation", message="fake wellness affirmation")
        )

    _ = conflict_title  # reserved for future binding checks
    return defects


def token_overlap_high(a: str, b: str, *, threshold: float = 0.55) -> bool:
    return _jaccard(a, b) >= threshold


def score_editorial_en_c351(native: dict[str, Any], *, locale: str = "en") -> dict[str, Any]:
    defects = run_editorial_quality_gate_en_c351(native)
    defects.extend(detect_locale_language_mismatch(native, locale=locale))
    scored = score_editorial_quality_c31(defects)
    return {
        **scored,
        "mode": "editorial_gate_en_c351",
        "defect_codes": scored.get("codes") or [],
        "checks": {
            "editorial_clean": not any(
                str(d.get("code")) in CRITICAL_DEFECTS or d.get("code") == DEFECT_LOCALE_LANGUAGE_MISMATCH
                for d in defects
                if d.get("severity") != "soft"
            )
        },
        "defects": defects,
    }
