"""Life Path co-voice visibility rubric + detector (Profile identity/styles).

«Видимо» = at least one scored field carries a theme from the claimed LP dictionary
that is distinguishable from other LPs (exclusive / stronger match for claimed LP).
"""

from __future__ import annotations

from typing import Any, Iterable

# Thematic cores (human rubric) — short labels for reports.
LIFE_PATH_CORE: dict[int, str] = {
    1: "инициация, независимость",
    2: "партнёрство, баланс",
    3: "самовыражение, лёгкость",
    4: "структура, надёжность",
    5: "перемены, свобода",
    6: "забота, ответственность за других",
    7: "анализ, уединение для понимания",
    8: "власть, материальный результат",
    9: "завершение, служение, отпускание",
    11: "интуиция, вдохновение других",
    22: "масштаб, реализация большого",
    33: "забота через учительство/пример",
}

# Exclusive lexical stems (RU + a few EN). Prefer stems that separate neighboring LPs
# (e.g. LP9 completion ≠ LP6 caretaking).
LIFE_PATH_MARKERS: dict[int, tuple[str, ...]] = {
    1: (
        "первым",
        "первопроход",
        "не жда",
        "без разрешен",
        "собственн",
        "независим",
        "иници",
        "не ждать",
        "first to",
        "own path",
        "independen",
    ),
    2: (
        "подстра",
        "дипломат",
        "резонанс",
        "трудно настоя",
        "баланс с друг",
        "партнёр",
        "в паре",
        "attun",
        "diplom",
    ),
    3: (
        "услышан",
        "разбрасыв",
        "юмор",
        "самовыраж",
        "словом",
        "многие дел",
        "express",
        "be heard",
    ),
    4: (
        "методичн",
        "надёжн",
        "пошаг",
        "фундамент",
        "дисциплин",
        "систематиз",
        "methodical",
        "reliable structur",
        "step by step",
    ),
    5: (
        "рутин",
        "тесно",
        "перемен",
        "свобод",
        "скук",
        "новый опыт",
        "движен",
        "restless",
        "need change",
    ),
    6: (
        "чужие проблем",
        "не моя забот",
        "семья как",
        "дом как",
        "тянет на себя",
        "ответственн за друг",
        "опека",
        "caretak",
        "others' problems",
    ),
    7: (
        "время одн",
        "уединен",
        "поверхностн",
        "внутренн",
        "поиск смысл",
        "самокопа",
        "alone to understand",
        "solitud",
    ),
    8: (
        "статус",
        "контроль",
        "результат",
        "деньги как",
        "власть",
        "материалн",
        "не отпуст",
        "status",
        "control",
    ),
    9: (
        "заверш",
        "цикл",
        "проща",
        "отпуска",
        "служен",
        "сострадан",
        "сочувств",
        "закрыва",
        "освобожд",
        "после себя",
        "отдава",
        "милосерд",
        "complet",
        "letting go",
        "close a cycle",
        "farewell",
        "compassion",
    ),
    11: (
        "не сказан",
        "вдохновля",
        "нервн",
        "интуиц",
        "чужое вниман",
        "unspoken",
        "inspir",
    ),
    22: (
        "масштаб",
        "на годы",
        "систем",
        "нетерпел",
        "мелк",
        "large-scale",
        "years ahead",
    ),
    33: (
        "пример",
        "учительств",
        "передач",
        "чужих ожидан",
        "ведёт пример",
        "teach by",
        "example not order",
    ),
}

# LP pairs that share care/help language — if only shared stems fire, not distinct.
_CARE_OVERLAP_LPS = frozenset({6, 9, 33})

IDENTITY_FIELDS = (
    "recognition_line",
    "identity_core",
    "strengths",
    "growth_zones",
)
STYLES_FIELDS = (
    "relationship_style",
    "money_style",
    "decision_style",
)


def _norm(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _field_texts(payload: dict[str, Any], fields: Iterable[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for key in fields:
        val = payload.get(key)
        if isinstance(val, list):
            for i, item in enumerate(val):
                if isinstance(item, str) and item.strip():
                    out.append((f"{key}[{i}]", item))
        elif isinstance(val, str) and val.strip():
            out.append((key, val))
    return out


def score_field_against_life_paths(text: str) -> dict[int, list[str]]:
    """Return {life_path: [matched stems]} for stems found in text."""
    blob = _norm(text)
    hits: dict[int, list[str]] = {}
    for lp, stems in LIFE_PATH_MARKERS.items():
        matched = [s for s in stems if s in blob]
        if matched:
            hits[lp] = matched
    return hits


def field_visible_for_life_path(text: str, life_path: int) -> tuple[bool, dict[str, Any]]:
    """True if field distinctly evidences claimed life_path."""
    try:
        lp = int(life_path)
    except (TypeError, ValueError):
        return False, {"reason": "invalid_life_path"}

    hits = score_field_against_life_paths(text)
    claimed = hits.get(lp) or []
    if not claimed:
        return False, {"reason": "no_claimed_markers", "hits": hits}

    # Stronger or exclusive: claimed has more stems than any other LP,
    # OR claimed has stems that no other LP matched.
    others = {k: v for k, v in hits.items() if k != lp}
    max_other = max((len(v) for v in others.values()), default=0)
    exclusive = True
    for other_lp, other_stems in others.items():
        # Shared care trap: LP9 vs LP6/33 — require claimed-only stem if both fire.
        if lp in _CARE_OVERLAP_LPS and other_lp in _CARE_OVERLAP_LPS:
            claimed_set = set(claimed)
            other_set = set(other_stems)
            if claimed_set <= other_set:
                exclusive = False
                break
        if len(other_stems) > len(claimed):
            exclusive = False
            break

    if len(claimed) >= max_other and exclusive:
        return True, {
            "reason": "claimed_distinct",
            "claimed_stems": claimed,
            "hits": hits,
        }

    # Tie-break: claimed still wins if it has at least one stem unused by strongest rival.
    if others:
        rival_lp = max(others.items(), key=lambda kv: len(kv[1]))[0]
        rival_stems = set(others[rival_lp])
        if any(s not in rival_stems for s in claimed) and len(claimed) >= len(others[rival_lp]):
            return True, {
                "reason": "claimed_exclusive_stem",
                "claimed_stems": claimed,
                "hits": hits,
            }

    return False, {
        "reason": "not_distinct",
        "claimed_stems": claimed,
        "hits": hits,
    }


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def detect_life_path_visibility(
    payload: dict[str, Any],
    life_path: int,
    *,
    fields: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Scan identity/styles payload for visible claimed LP."""
    keys = tuple(fields) if fields is not None else IDENTITY_FIELDS + STYLES_FIELDS
    visible_fields: list[str] = []
    per_field: dict[str, Any] = {}
    for name, text in _field_texts(payload, keys):
        ok, detail = field_visible_for_life_path(text, life_path)
        per_field[name] = {"ok": ok, **detail}
        if ok:
            visible_fields.append(name)
    return {
        "life_path": int(life_path) if str(life_path).isdigit() or isinstance(life_path, int) else life_path,
        "core": LIFE_PATH_CORE.get(int(life_path)) if _as_int(life_path) is not None else None,
        "visible": bool(visible_fields),
        "visible_fields": visible_fields,
        "per_field": per_field,
    }


def life_path_co_voice_hint(life_path: Any) -> dict[str, Any] | None:
    """Compact hint injected into shared numerology for identity/styles prompts."""
    try:
        lp = int(life_path)
    except (TypeError, ValueError):
        return None
    core = LIFE_PATH_CORE.get(lp)
    if not core:
        return None
    # Human themes (not detector stems) — grounded in the Phase-0 rubric.
    themes: dict[int, tuple[str, ...]] = {
        1: ("первым начинать", "не ждать разрешения", "собственный путь vs чужой"),
        2: ("подстройка под другого", "дипломатия", "трудно настоять на своём"),
        3: ("нужно быть услышанным", "разбрасывается", "слово/юмор как инструмент"),
        4: ("методичность", "недоверие к быстрым путям", "держит систему"),
        5: ("тесно в рутине", "нужно движение", "скука как сигнал уйти"),
        6: ("тянет чужие проблемы", "дом/семья как центр", "трудно сказать «не моя забота»"),
        7: ("время одному, чтобы понять", "недоверие к поверхностному", "внутренний поиск смысла"),
        8: ("результат/статус", "трудно отпустить контроль", "деньги как мера уважения к себе"),
        9: ("закрывать циклы", "сострадание → действие", "умеет отпускать, даже когда трудно"),
        11: ("чувствует несказанное", "нервное напряжение от чужого внимания", "вдохновляет непреднамеренно"),
        22: ("думает масштабом", "нетерпелив к мелкому", "строит на годы вперёд"),
        33: ("ведёт примером", "тяжесть чужих ожиданий", "служение через передачу"),
    }
    return {
        "life_path": lp,
        "core_ru": core,
        "themes_ru": list(themes.get(lp, ())),
        "instruction_ru": (
            "Одно из strengths/growth_zones (identity) или styles-полей должно явно "
            "опираться на themes_ru / core_ru — так, чтобы другой life_path изменил это поле."
        ),
    }
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def themes_shift(a: dict[str, Any], b: dict[str, Any], *, fields: Iterable[str]) -> bool:
    """True if at least one field pair differs enough that LP themes diverge."""
    texts_a = {k: _norm(v) for k, v in _field_texts(a, fields)}
    texts_b = {k: _norm(v) for k, v in _field_texts(b, fields)}
    # Compare joined strengths/growth as bags; recognition/identity as strings.
    for key in fields:
        if key in ("strengths", "growth_zones"):
            ta = " | ".join(v for k, v in texts_a.items() if k.startswith(f"{key}["))
            tb = " | ".join(v for k, v in texts_b.items() if k.startswith(f"{key}["))
        else:
            ta = texts_a.get(key, "")
            tb = texts_b.get(key, "")
        if not ta or not tb:
            continue
        if ta == tb:
            continue
        # Different LP marker sets between the two texts.
        ha = set(score_field_against_life_paths(ta).keys())
        hb = set(score_field_against_life_paths(tb).keys())
        if ha != hb:
            return True
        # Substantial lexical shift even without marker change.
        if abs(len(ta) - len(tb)) > 40 or ta[:80] != tb[:80]:
            return True
    return False
