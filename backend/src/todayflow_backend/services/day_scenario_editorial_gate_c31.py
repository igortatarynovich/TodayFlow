"""Phase C3.1 — Editorial quality gate for native day_scenario LLM output.

Runs after schema validation. Finds abstract / universal / duplicate / jargon defects.
Does **not** rewrite prose with formula templates — reject → retry with defect feedback
→ facts_only_unavailable if still failing.

Canon: docs/audits/DAY_SCENARIO_EVERYDAY_QUALITY_C31.md
"""

from __future__ import annotations

import re
from typing import Any

# Defect codes (capture / eval / retry feedback)
DEFECT_SCENE_ABSTRACT = "SCENE_ABSTRACT"
DEFECT_SCENE_UNIVERSAL_ADVICE = "SCENE_UNIVERSAL_ADVICE"
DEFECT_SCENE_CLONE = "SCENE_CLONE"
DEFECT_SCENE_MISSING_EVERYDAY = "SCENE_MISSING_EVERYDAY"
DEFECT_SCENE_MISSING_CHOICE = "SCENE_MISSING_CHOICE"
DEFECT_THESIS_ECHO = "THESIS_ECHO"
DEFECT_ASTRO_JARGON_BARE = "ASTRO_JARGON_BARE"
DEFECT_PSEUDO_DIAGNOSIS = "PSEUDO_DIAGNOSIS"
DEFECT_CATEGORICAL_PROMISE = "CATEGORICAL_PROMISE"
DEFECT_CHORUS_PARALLEL_ECHO = "CHORUS_PARALLEL_ECHO"
DEFECT_AFFIRMATION_UNNATURAL = "AFFIRMATION_UNNATURAL"
DEFECT_BUREAUCRATIC = "BUREAUCRATIC"
DEFECT_NATAL_WITHOUT_EVIDENCE = "NATAL_WITHOUT_EVIDENCE"

CRITICAL_DEFECTS = frozenset(
    {
        DEFECT_SCENE_ABSTRACT,
        DEFECT_SCENE_UNIVERSAL_ADVICE,
        DEFECT_SCENE_CLONE,
        DEFECT_SCENE_MISSING_EVERYDAY,
        DEFECT_THESIS_ECHO,
        DEFECT_ASTRO_JARGON_BARE,
        DEFECT_PSEUDO_DIAGNOSIS,
        DEFECT_CATEGORICAL_PROMISE,
        DEFECT_NATAL_WITHOUT_EVIDENCE,
    }
)

EDITORIAL_DEFECT_CODES = frozenset(
    {
        DEFECT_SCENE_ABSTRACT,
        DEFECT_SCENE_UNIVERSAL_ADVICE,
        DEFECT_SCENE_CLONE,
        DEFECT_SCENE_MISSING_EVERYDAY,
        DEFECT_SCENE_MISSING_CHOICE,
        DEFECT_THESIS_ECHO,
        DEFECT_ASTRO_JARGON_BARE,
        DEFECT_PSEUDO_DIAGNOSIS,
        DEFECT_CATEGORICAL_PROMISE,
        DEFECT_CHORUS_PARALLEL_ECHO,
        DEFECT_AFFIRMATION_UNNATURAL,
        DEFECT_BUREAUCRATIC,
        DEFECT_NATAL_WITHOUT_EVIDENCE,
    }
)

# Capture architectural classes (map editorial → pack taxonomy)
CAPTURE_CLASS_BY_DEFECT: dict[str, str] = {
    DEFECT_SCENE_ABSTRACT: "SCENE_QUALITY",
    DEFECT_SCENE_UNIVERSAL_ADVICE: "SCENE_QUALITY",
    DEFECT_SCENE_CLONE: "SCENE_QUALITY",
    DEFECT_SCENE_MISSING_EVERYDAY: "SCENE_QUALITY",
    DEFECT_SCENE_MISSING_CHOICE: "SCENE_QUALITY",
    DEFECT_THESIS_ECHO: "RESPONSE_COHERENCE",
    DEFECT_ASTRO_JARGON_BARE: "CHORUS_QUALITY",
    DEFECT_PSEUDO_DIAGNOSIS: "LANGUAGE",
    DEFECT_CATEGORICAL_PROMISE: "LANGUAGE",
    DEFECT_CHORUS_PARALLEL_ECHO: "CHORUS_QUALITY",
    DEFECT_AFFIRMATION_UNNATURAL: "LANGUAGE",
    DEFECT_BUREAUCRATIC: "LANGUAGE",
    DEFECT_NATAL_WITHOUT_EVIDENCE: "VALIDATION",
}

_UNIVERSAL_ADVICE_RE = re.compile(
    r"("
    r"не\s+торопитесь|"
    r"сохраняйте\s+баланс|"
    r"слушайте\s+себя|"
    r"прислушайтесь\s+к\s+себе|"
    r"избегайте\s+конфликтов|"
    r"сделайте\s+паузу|"
    r"будьте\s+осторожн|"
    r"оставайтесь\s+в\s+моменте|"
    r"доверяйте\s+процессу|"
    r"найдите\s+гармонию|"
    r"держите\s+границы(?!\s+в\s)|"  # bare «держите границы» without concrete context often weak
    r"сохраняйте\s+спокойствие|"
    r"не\s+распыляйтесь|"
    r"выберите\s+главное|"
    r"мягко\s+проявите\s+себя"
    r")",
    re.I,
)

_ABSTRACT_SPHERE_RE = re.compile(
    r"("
    r"в\s+отношениях\s+возможн|"
    r"возможна\s+напряж[её]н|"
    r"сфера\s+\w+\s+подсвеч|"
    r"акцент\s+на\s+сфер|"
    r"сегодня\s+в\s+\w+\s+важн|"
    r"проявляется\s+энергия|"
    r"нужно\s+больше\s+внимания\s+к"
    r")",
    re.I,
)

_CONCRETE_MARKER_RE = re.compile(
    r"("
    r"сообщен|письм|звон|спросит|ответ|встреч|кофе|кухн|мессенджер|"
    r"чате|telegram|whatsapp|коллег|партн[её]р|мама|папа|реб[её]н|"
    r"счёт|оплат|перевод|дедлайн|задач|созвон|кабинет|подъезд|"
    r"скажет|напишет|позвон|откроет|закроет|подожд|"
    r"«|»|\".{3,} \"|"  # quoted dialogue-ish
    r"момент,\s+когда|именно\s+когда|в\s+тот\s+момент"
    r")",
    re.I,
)

_ASTRO_TERM_RE = re.compile(
    r"("
    r"луна\s+в\s+\w+|"
    r"солнце\s+в\s+\w+|"
    r"меркурий|венера|марс|юпитер|сатурн|уран|нептун|плутон|"
    r"квадрат|трин|соединен|оппозиц|ретроград|аспект|транзит|"
    r"в\s+рыбах|в\s+овне|в\s+тельце|в\s+близнецах|в\s+раке|"
    r"во\s+льве|в\s+деве|в\s+весах|в\s+скорпионе|в\s+стрельце|"
    r"в\s+козероге|в\s+водолее"
    r")",
    re.I,
)

_HUMAN_TRANSLATION_RE = re.compile(
    r"("
    r"поэтому|из[- ]за\s+этого|делает|становится|заметн|"
    r"хочется|легче|сложнее|сильнее|тише|резче|"
    r"эмоц|слов|ответ|решени|темп|ритм|пауз"
    r")",
    re.I,
)

_PSEUDO_DIAGNOSIS_RE = re.compile(
    r"("
    r"у\s+вас\s+травм|"
    r"вы\s+созависим|"
    r"нарцисси|"
    r"вы\s+в\s+отрицании|"
    r"ваша\s+психика|"
    r"клиническ|"
    r"расстройств\w+\s+личност|"
    r"вы\s+не\s+умеете\s+любить"
    r")",
    re.I,
)

_CATEGORICAL_RE = re.compile(
    r"("
    r"обязательно\s+случится|"
    r"точно\s+произойдёт|"
    r"гарантирован|"
    r"вы\s+обязаны|"
    r"неизбежно\s+получите|"
    r"100\s*%|"
    r"без\s+вариантов\s+будет"
    r")",
    re.I,
)

_BUREAUCRATIC_RE = re.compile(
    r"("
    r"осуществить\s+коммуникац|"
    r"в\s+рамках\s+взаимодейств|"
    r"оптимизировать\s+процесс|"
    r"произвести\s+рефлексию|"
    r"актуализировать\s+запрос|"
    r"реализовать\s+интенцию|"
    r"обеспечить\s+баланс\s+интересов"
    r")",
    re.I,
)

_AFFIRMATION_FAKE_RE = re.compile(
    r"("
    r"я\s+достоин\s+всего\s+лучшего|"
    r"вселенная\s+заботится|"
    r"я\s+притягиваю\s+изобилие|"
    r"каждый\s+день\s+я\s+становлюсь\s+лучше|"
    r"я\s+свечусь\s+любовью"
    r")",
    re.I,
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zа-яё0-9]{4,}", text.lower()) if t}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _defect(
    code: str,
    *,
    field: str,
    message: str,
    severity: str = "critical",
) -> dict[str, str]:
    return {
        "code": code,
        "field": field,
        "message": message,
        "severity": severity if severity in {"critical", "soft"} else "critical",
        "capture_class": CAPTURE_CLASS_BY_DEFECT.get(code, "VALIDATION"),
    }


def _scene_blob(sc: dict[str, Any]) -> str:
    return " ".join(
        str(sc.get(k) or "")
        for k in (
            "setup",
            "opportunity",
            "trap",
            "recommended_action",
            "avoid_action",
            "everyday_example",
        )
    )


def run_editorial_quality_gate_c31(
    native: dict[str, Any] | None,
    *,
    has_natal_evidence: bool | None = None,
) -> list[dict[str, str]]:
    """Return editorial defects. Empty list = pass."""
    if not isinstance(native, dict):
        return [_defect(DEFECT_SCENE_ABSTRACT, field="payload", message="native payload missing")]

    defects: list[dict[str, str]] = []
    conflict = _as_dict(native.get("conflict"))
    title = _norm(conflict.get("title") or conflict.get("thesis"))
    thesis = _norm(conflict.get("thesis"))
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    chorus = _as_dict(native.get("interpretive_chorus"))
    prop = _as_dict(native.get("prop_material"))

    # --- scenes ---
    scene_token_sets: list[tuple[str, set[str]]] = []
    for idx, sc in enumerate(scenes):
        sid = str(sc.get("scene_id") or sc.get("sphere") or idx)
        field = f"scenes[{idx}:{sid}]"
        blob = _scene_blob(sc)
        everyday = str(sc.get("everyday_example") or "").strip()
        setup = str(sc.get("setup") or "").strip()
        opp = str(sc.get("opportunity") or "").strip()
        trap = str(sc.get("trap") or "").strip()
        action = str(sc.get("recommended_action") or "").strip()

        if not everyday or len(everyday) < 24:
            defects.append(
                _defect(
                    DEFECT_SCENE_MISSING_EVERYDAY,
                    field=field,
                    message="everyday_example missing or too thin — need a concrete domestic moment",
                )
            )

        combined_for_concrete = f"{everyday} {setup} {opp} {trap}"
        # everyday_example itself must carry a lived moment (not only setup)
        if everyday and len(everyday) >= 24 and not _CONCRETE_MARKER_RE.search(everyday):
            defects.append(
                _defect(
                    DEFECT_SCENE_ABSTRACT,
                    field=field,
                    message="everyday_example lacks concrete markers (message/ask/moment/object/person)",
                )
            )
        elif everyday and not _CONCRETE_MARKER_RE.search(combined_for_concrete):
            defects.append(
                _defect(
                    DEFECT_SCENE_ABSTRACT,
                    field=field,
                    message="scene lacks concrete markers (message/ask/moment/object/person)",
                )
            )
        if _ABSTRACT_SPHERE_RE.search(setup) and not _CONCRETE_MARKER_RE.search(setup + " " + everyday):
            defects.append(
                _defect(
                    DEFECT_SCENE_ABSTRACT,
                    field=field,
                    message="setup reads as abstract sphere forecast, not a lived moment",
                )
            )

        advice_blob = f"{action} {opp}"
        # Ignore quotation marks alone as "concrete" — need a real object/action token
        advice_concrete = bool(
            re.search(
                r"("
                r"сообщен|письм|звон|спросит|ответ|встреч|кофе|кухн|мессенджер|"
                r"чате|коллег|партн|мама|папа|реб[её]н|"
                r"счёт|оплат|перевод|дедлайн|задач|созвон|"
                r"скажет|напишет|позвон|откроет|закроет|черновик|абзац"
                r")",
                advice_blob,
                re.I,
            )
        )
        if _UNIVERSAL_ADVICE_RE.search(advice_blob) and not advice_concrete:
            defects.append(
                _defect(
                    DEFECT_SCENE_UNIVERSAL_ADVICE,
                    field=field,
                    message="universal advice without concrete today-action",
                )
            )

        # Choice between strategies: trap + opportunity or force language
        if (not opp or not trap) and not re.search(r"между|вместо|а не |или ", blob, re.I):
            defects.append(
                _defect(
                    DEFECT_SCENE_MISSING_CHOICE,
                    field=field,
                    message="scene should show two strategies (opportunity vs trap)",
                    severity="soft",
                )
            )

        if _PSEUDO_DIAGNOSIS_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_PSEUDO_DIAGNOSIS,
                    field=field,
                    message="pseudo-psychological diagnosis language",
                )
            )
        if _CATEGORICAL_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_CATEGORICAL_PROMISE,
                    field=field,
                    message="categorical promise / inevitability",
                )
            )
        if _BUREAUCRATIC_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_BUREAUCRATIC,
                    field=field,
                    message="bureaucratic / unnatural voice",
                    severity="soft",
                )
            )

        scene_token_sets.append((field, _tokens(blob)))

    # near-duplicate scenes
    for i in range(len(scene_token_sets)):
        for j in range(i + 1, len(scene_token_sets)):
            fi, ti = scene_token_sets[i]
            fj, tj = scene_token_sets[j]
            if _jaccard(ti, tj) >= 0.62:
                defects.append(
                    _defect(
                        DEFECT_SCENE_CLONE,
                        field=f"{fi}|{fj}",
                        message="scenes are near-duplicates under different spheres",
                    )
                )

    # thesis echo across scenes — verbatim thesis dump, not a short title mention
    if thesis and len(thesis) >= 24:
        echoes = 0
        needle = thesis[:40]
        for sc in scenes:
            blob = _norm(_scene_blob(sc))
            if needle in blob:
                echoes += 1
        if echoes >= 2:
            defects.append(
                _defect(
                    DEFECT_THESIS_ECHO,
                    field="scenes",
                    message="conflict thesis repeated verbatim across multiple scenes",
                )
            )

    # --- chorus ---
    astro_rows = _as_list(chorus.get("astrology"))
    for i, row in enumerate(astro_rows):
        if not isinstance(row, dict):
            continue
        named = str(row.get("named_factor") or "")
        meaning = str(row.get("human_meaning") or "")
        link = str(row.get("link_to_conflict") or "")
        blob = f"{named} {meaning} {link}"
        if _ASTRO_TERM_RE.search(blob) and not _HUMAN_TRANSLATION_RE.search(meaning + " " + link):
            defects.append(
                _defect(
                    DEFECT_ASTRO_JARGON_BARE,
                    field=f"chorus.astrology[{i}]",
                    message="astro term without human translation into today's conflict",
                )
            )

    # chorus voices almost the same paragraph
    voice_blobs: list[str] = []
    for row in astro_rows[:2]:
        if isinstance(row, dict):
            voice_blobs.append(_norm(f"{row.get('named_factor')} {row.get('human_meaning')} {row.get('link_to_conflict')}"))
    card = _as_dict(chorus.get("day_card"))
    if card:
        voice_blobs.append(
            _norm(f"{card.get('named_factor')} {card.get('archetype_role')} {card.get('link_to_conflict')}")
        )
    number = _as_dict(chorus.get("day_number"))
    if number:
        voice_blobs.append(
            _norm(
                f"{number.get('named_factor')} {number.get('tempo')} {number.get('style')} {number.get('link_to_conflict')}"
            )
        )
    for i in range(len(voice_blobs)):
        for j in range(i + 1, len(voice_blobs)):
            if _jaccard(_tokens(voice_blobs[i]), _tokens(voice_blobs[j])) >= 0.7:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_PARALLEL_ECHO,
                        field="interpretive_chorus",
                        message="chorus voices nearly duplicate each other instead of sequenced roles",
                        severity="soft",
                    )
                )

    natal_rows = _as_list(chorus.get("natal"))
    if natal_rows and has_natal_evidence is False:
        defects.append(
            _defect(
                DEFECT_NATAL_WITHOUT_EVIDENCE,
                field="chorus.natal",
                message="natal voice present without natal evidence — do not invent deep personalization",
            )
        )

    # affirmations
    affirm = _as_dict(prop.get("affirmation_tension"))
    at = str(affirm.get("text") or "")
    if at and _AFFIRMATION_FAKE_RE.search(at):
        defects.append(
            _defect(
                DEFECT_AFFIRMATION_UNNATURAL,
                field="prop_material.affirmation_tension",
                message="unnatural / universal affirmation",
            )
        )

    # conflict-level categorical / diagnosis
    conflict_blob = " ".join(str(conflict.get(k) or "") for k in ("thesis", "why_today", "why_personal"))
    if _PSEUDO_DIAGNOSIS_RE.search(conflict_blob):
        defects.append(
            _defect(
                DEFECT_PSEUDO_DIAGNOSIS,
                field="conflict",
                message="pseudo-diagnosis in conflict prose",
            )
        )
    if _CATEGORICAL_RE.search(conflict_blob):
        defects.append(
            _defect(
                DEFECT_CATEGORICAL_PROMISE,
                field="conflict",
                message="categorical promise in conflict prose",
            )
        )

    # de-dupe identical codes+field
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for d in defects:
        key = f"{d['code']}:{d['field']}:{d['message'][:40]}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(d)
    return unique


def editorial_has_critical(defects: list[dict[str, str]]) -> bool:
    return any(
        d.get("severity") == "critical" or d.get("code") in CRITICAL_DEFECTS for d in defects
    )


def format_editorial_retry_feedback(defects: list[dict[str, str]], *, limit: int = 8) -> str:
    """Compact RU feedback for the next LLM attempt — defects only, no rewrite templates."""
    if not defects:
        return ""
    lines = [
        "Предыдущий JSON отклонён editorial quality gate. Исправь дефекты; не подставляй шаблоны Formula Bank.",
        "Нужны узнаваемые бытовые сцены: момент + импульс + внешняя ситуация + выбор двух стратегий + последствие + действие на сегодня.",
        "Запрещены универсальные советы («не торопитесь», «слушайте себя», «сохраняйте баланс») без конкретной сцены.",
        "Хор: астрология→среда, карта→архетип, число→ритм, натал→личная чувствительность — без четырёх одинаковых абзацев.",
        "Дефекты:",
    ]
    for d in defects[:limit]:
        lines.append(f"- [{d.get('code')}] {d.get('field')}: {d.get('message')}")
    return "\n".join(lines)


def score_editorial_quality_c31(defects: list[dict[str, str]]) -> dict[str, Any]:
    """Simple capture/eval score — 1.0 clean, decreases by defect weight."""
    score = 1.0
    for d in defects:
        if d.get("severity") == "soft" or d.get("code") not in CRITICAL_DEFECTS:
            score -= 0.04
        else:
            score -= 0.12
    score = max(0.0, round(score, 3))
    return {
        "editorial_score": score,
        "defect_count": len(defects),
        "critical_count": sum(1 for d in defects if editorial_has_critical([d])),
        "codes": sorted({str(d.get("code")) for d in defects}),
    }
