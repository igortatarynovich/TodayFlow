"""Phase C3.1–C3.2 — Editorial quality **analysis** for native day_scenario LLM output.

C3.1: everyday scene concreteness.
C3.2: interpretive chorus causal chain (one story, four roles).

Runs after schema validation. Analyzers emit defects + scores for capture/eval.
**Runtime policy is owned by C3.6 gate maturity** (`day_scenario_gate_maturity_c36`):
quality codes are experimental/advisory (observe only). Do not treat
`CRITICAL_DEFECTS` / `editorial_has_critical` as user-runtime blockers.

Canon: docs/audits/DAY_SCENARIO_EVERYDAY_QUALITY_C31.md
       docs/audits/DAY_SCENARIO_CHORUS_QUALITY_C32.md
       docs/audits/DAY_SCENARIO_GATE_MATURITY_C36.md
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
DEFECT_ASTRO_JARGON_BARE = "ASTRO_JARGON_BARE"  # legacy alias; chorus uses CHORUS_UNTRANSLATED_JARGON
DEFECT_PSEUDO_DIAGNOSIS = "PSEUDO_DIAGNOSIS"
DEFECT_CATEGORICAL_PROMISE = "CATEGORICAL_PROMISE"
DEFECT_CHORUS_PARALLEL_ECHO = "CHORUS_PARALLEL_ECHO"  # soft legacy; prefer C3.2 codes
DEFECT_AFFIRMATION_UNNATURAL = "AFFIRMATION_UNNATURAL"
DEFECT_BUREAUCRATIC = "BUREAUCRATIC"
DEFECT_NATAL_WITHOUT_EVIDENCE = "NATAL_WITHOUT_EVIDENCE"  # legacy; chorus uses CHORUS_NATAL_WITHOUT_EVIDENCE

# C3.2 chorus quality
DEFECT_CHORUS_PARALLEL_FORECAST = "CHORUS_PARALLEL_FORECAST"
DEFECT_CHORUS_SEMANTIC_DUPLICATION = "CHORUS_SEMANTIC_DUPLICATION"
DEFECT_CHORUS_ROLE_DRIFT = "CHORUS_ROLE_DRIFT"
DEFECT_CHORUS_UNTRANSLATED_JARGON = "CHORUS_UNTRANSLATED_JARGON"
DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE = "CHORUS_NATAL_WITHOUT_EVIDENCE"

# ScreenFlow v3.1 seed-kill (hard via C3.6 maturity — not score_only quality)
DEFECT_SEED_BANK_BINARY_SHORT_NAME = "SEED_BANK_BINARY_SHORT_NAME"
DEFECT_SEED_CHORUS_PASTE = "SEED_CHORUS_PASTE"

# Prod gen 1117: jargon retry pasted why_today into astrology[1]; seed-kill retry reverted to jargon.
# Prod gen 1119: seed-kill missed why_arose→scene.why; attempt 2 reverted astrology[2] to jargon.
SEED_JARGON_CROSS_HINT_RU = (
    "Не чини ASTRO_JARGON_BARE копипастом why_today и не чини seed-leak откатом в жаргон: "
    "human_meaning КАЖДОГО interpretive_chorus.astrology[i] (включая [1]/[2]) — "
    "среда дня своими словами; не копия named_factor и не копия conflict.why_today/title "
    "(≥6 слов = verbatim_seed_leak). "
    "Не копируй why_today/why_arose (≥6 слов) в scenes[].why / why_sphere / setup "
    "(prod gen 1119: conflict.why_arose+scenes[0].why). "
    "Не чини этот leak откатом astrology[i] в жаргон."
)

CRITICAL_DEFECTS = frozenset(
    {
        # Severity labels for eval/scoring — NOT runtime blockers (see C3.6 maturity).
        DEFECT_SCENE_ABSTRACT,
        DEFECT_SCENE_UNIVERSAL_ADVICE,
        DEFECT_SCENE_CLONE,
        DEFECT_SCENE_MISSING_EVERYDAY,
        DEFECT_THESIS_ECHO,
        DEFECT_ASTRO_JARGON_BARE,
        DEFECT_PSEUDO_DIAGNOSIS,
        DEFECT_CATEGORICAL_PROMISE,
        DEFECT_NATAL_WITHOUT_EVIDENCE,
        DEFECT_CHORUS_PARALLEL_FORECAST,
        DEFECT_CHORUS_SEMANTIC_DUPLICATION,
        DEFECT_CHORUS_ROLE_DRIFT,
        DEFECT_CHORUS_UNTRANSLATED_JARGON,
        DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
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
        DEFECT_CHORUS_PARALLEL_FORECAST,
        DEFECT_CHORUS_SEMANTIC_DUPLICATION,
        DEFECT_CHORUS_ROLE_DRIFT,
        DEFECT_CHORUS_UNTRANSLATED_JARGON,
        DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
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
    DEFECT_CHORUS_PARALLEL_FORECAST: "CHORUS_QUALITY",
    DEFECT_CHORUS_SEMANTIC_DUPLICATION: "CHORUS_QUALITY",
    DEFECT_CHORUS_ROLE_DRIFT: "CHORUS_QUALITY",
    DEFECT_CHORUS_UNTRANSLATED_JARGON: "CHORUS_QUALITY",
    DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE: "VALIDATION",
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
    r"счёт|оплат|перевод|дедлайн|задач|созвон|кабинет|подъезд|проект|"
    r"скажет|напишет|позвон|откроет|закроет|подожд|"
    # Quoted dialogue needs content — bare «» must not count as lived moment.
    r"«[^»]{6,}»|\"[^\"]{6,}\"|"
    r"момент,\s+когда|именно\s+когда|в\s+тот\s+момент"
    r")",
    re.I,
)


def everyday_has_lived_specificity(text: str, *, locale: str = "ru") -> bool:
    """True when everyday_example carries a lived moment, not a thin tip/template.

    Specificity signals (any one): clock time, substantive quote, person+speech act,
    named channel, or long prose with concrete markers. Bare keywords like «сообщение:»
    without a moment are not enough (C3.6.2 human calib gap fix).
    """
    t = (text or "").strip()
    if not t:
        return False
    loc = (locale or "ru").strip().lower()
    if re.search(r"\d{1,2}[:.]\d{2}", t):
        return True
    if re.search(r"«[^»]{12,}»|\"[^\"]{12,}\"|'[^']{12,}'", t):
        return True
    if loc.startswith("en"):
        if re.search(
            r"(message|chat|email|slack|call|partner|colleague|manager|door|draft|"
            r"jira|doc|phone|meeting|comment).{0,50}(at\s+\d|asks|writes|texts|:|\d)",
            t,
            re.I,
        ):
            return True
        if len(t) >= 48 and re.search(
            r"(message|chat|email|call|colleague|partner|deadline|draft|kitchen|"
            r"door|phone|meeting|invoice|reply|slack|jira|doc|comment)",
            t,
            re.I,
        ):
            return True
        return False
    if re.search(
        r"(партн|коллег|друг|подруг|мама|папа|менеджер|клиент).{0,80}"
        r"(спрашива|пишет|говор|сообщ|звон|предлага|скажет|ответ|напис)",
        t,
        re.I,
    ):
        return True
    if re.search(r"(напис|говор|скаж|ответ).{0,40}(коллег|партн|друг|подруг)", t, re.I):
        return True
    if re.search(r"(в\s+чате|в\s+почте|черновик|slack|telegram|whatsapp)", t, re.I):
        return True
    if len(t) >= 100 and _CONCRETE_MARKER_RE.search(t):
        return True
    return False


_ASTRO_TERM_RE = re.compile(
    r"("
    r"луна\s+в\s+\w+|"
    r"солнце\s+в\s+\w+|"
    r"меркурий|венера|марс|юпитер|сатурн|уран|нептун|плутон|"
    r"квадрат|трин|соединен|оппозиц|ретроград|аспект|транзит|директ|"
    r"в\s+рыбах|в\s+овне|в\s+тельце|в\s+близнецах|в\s+раке|"
    r"во\s+льве|в\s+деве|в\s+весах|в\s+скорпионе|в\s+стрельце|"
    r"в\s+козероге|в\s+водолее|в\s+знаке"
    r")",
    re.I,
)

_HUMAN_TRANSLATION_RE = re.compile(
    r"("
    r"поэтому|из[- ]за\s+этого|делает|становится|заметн|"
    r"хочется|легче|сложнее|сильнее|тише|резче|"
    r"эмоц|слов|ответ|решени|темп|ритм|пауз|"
    # Lived env / conflict translation (C3.6.2 ASTRO_JARGON FP fix)
    r"сред[аеуы]|атмосфер|давлен|желани|разговор|"
    r"ясн|импульс|соблазн|сталкива|похож|"
    r"внешн|мотор|напор|искр|конфликт|выбор|"
    r"сглад|высказать|прямот"
    r")",
    re.I,
)

# LLM filler that repeats sky jargon + conflict title ≠ human translation
_JARGON_ECHO_TEMPLATE_RE = re.compile(
    r"("
    r"это\s+подталкивает\s+день\s+к\s+сюжету|"
    r"объясняет,\s+почему\s+сегодня\s+в\s+центре"
    r")",
    re.I,
)


def astrology_voice_lacks_human_translation(named: str, meaning: str, link: str) -> bool:
    """True when chorus astrology has sky jargon without a lived translation.

    Named factors may keep astro labels. Fail when meaning/link lack human framing,
    or when meaning is the echo-template wrapping repeated jargon (calib FP/TP split).
    """
    jargon_blob = f"{named} {meaning} {link}"
    if not _ASTRO_TERM_RE.search(jargon_blob):
        return False
    body = f"{meaning} {link}".strip()
    if not body:
        return True
    named_s = (named or "").strip()
    meaning_s = (meaning or "").strip()
    named_echoed = bool(named_s) and named_s.lower()[: min(50, len(named_s))] in meaning_s.lower()[
        : max(80, len(named_s) + 20)
    ]
    if _JARGON_ECHO_TEMPLATE_RE.search(meaning_s) and (
        _ASTRO_TERM_RE.search(meaning_s) or named_echoed
    ):
        return True
    return not bool(_HUMAN_TRANSLATION_RE.search(body))


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

# C3.2 — chorus role markers
_CHORUS_ENV_RE = re.compile(
    r"("
    r"сред[аеуы]|атмосфер|фон\s+дня|внешн|небо|подтекст|заметн|"
    r"делает|становится|воздух|обстановк|контекст\s+дня"
    r")",
    re.I,
)
_CHORUS_ARCHETYPE_RE = re.compile(
    r"("
    r"архетип|карт[аыуе]|роль|образ|паттерн|реакц|"
    r"как\s+реагир|приглашает|подсказыв"
    r")",
    re.I,
)
_CHORUS_TEMPO_RE = re.compile(
    r"("
    r"темп|ритм|способ|сначала|потом|без\s+спешк|через\s+\d|"
    r"в\s+два\s+шаг|последовательн|прохождени|стиль"
    r")",
    re.I,
)
_CHORUS_NATAL_PERSONAL_RE = re.compile(
    r"("
    r"\bвам\b|\bвас\b|\bваш|"
    r"личн|уязвим|ресурс|чувствительн|привычк|именно\s+вы"
    r")",
    re.I,
)
_CHORUS_PARALLEL_FORECAST_RE = re.compile(
    r"("
    r"сегодня\s+вас\s+жд|"
    r"день\s+принес|"
    r"карта\s+говорит,\s+что\s+сегодня|"
    r"число\s+говорит,\s+что\s+сегодня|"
    r"астрология\s+обещает|"
    r"отдельн\w+\s+прогноз|"
    r"параллельн\w+\s+прогноз|"
    r"в\s+работе\s+сегодня.{0,40}в\s+отношениях|"
    r"ждите\s+новост|"
    r"день\s+благоприят"
    r")",
    re.I | re.S,
)


def conflict_anchor_id(conflict: dict[str, Any] | None) -> str:
    """Stable conflict_id from conflict title — voices must bind to this."""
    c = conflict if isinstance(conflict, dict) else {}
    title = str(c.get("title") or c.get("short_name") or "day").strip()
    slug = re.sub(r"[^0-9A-Za-zА-Яа-яЁё]+", "-", title, flags=re.U).strip("-").lower()
    slug = slug[:48] or "day"
    return f"conflict.{slug}"


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
        elif not everyday_has_lived_specificity(everyday, locale="ru") or not _CONCRETE_MARKER_RE.search(
            everyday
        ):
            # Thin/generic tip with length ≠ lived moment (canon: SCENE_MISSING_EVERYDAY).
            defects.append(
                _defect(
                    DEFECT_SCENE_MISSING_EVERYDAY,
                    field=field,
                    message="everyday_example too thin — need a lived moment (time/quote/person+act)",
                )
            )
            # Human calib co-labels thin everyday as ABSTRACT as well — keep both codes.
            defects.append(
                _defect(
                    DEFECT_SCENE_ABSTRACT,
                    field=field,
                    message="everyday_example lacks a lived moment (thin tip/template)",
                )
            )

        combined_for_concrete = f"{everyday} {setup} {opp} {trap}"
        if everyday and everyday_has_lived_specificity(everyday, locale="ru") and not _CONCRETE_MARKER_RE.search(
            combined_for_concrete
        ):
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

    # --- chorus (C3.2 causal chain) ---
    conflict_id_expected = conflict_anchor_id(conflict)

    def _voice_text(row: dict[str, Any]) -> str:
        return " ".join(
            str(row.get(k) or "")
            for k in (
                "named_factor",
                "human_meaning",
                "archetype_role",
                "tempo",
                "style",
                "link_to_conflict",
            )
        )

    def _check_conflict_binding(row: dict[str, Any], field: str) -> None:
        cid = str(row.get("conflict_id") or "").strip()
        link = str(row.get("link_to_conflict") or "").strip()
        if not cid:
            defects.append(
                _defect(
                    DEFECT_CHORUS_PARALLEL_FORECAST,
                    field=field,
                    message="missing conflict_id — every chorus voice must bind to the day's conflict",
                )
            )
        elif cid not in {conflict_id_expected, "conflict", title}:
            slug = conflict_id_expected.split(".", 1)[-1]
            if slug not in cid.lower() and cid.lower() not in conflict_id_expected.lower():
                defects.append(
                    _defect(
                        DEFECT_CHORUS_PARALLEL_FORECAST,
                        field=field,
                        message=f"conflict_id mismatch (expected {conflict_id_expected})",
                    )
                )
        if not link:
            defects.append(
                _defect(
                    DEFECT_CHORUS_PARALLEL_FORECAST,
                    field=field,
                    message="missing link_to_conflict — voice must explain its role in the conflict",
                )
            )
        # v3.1 seed-kill: do NOT require link_to_conflict to share tokens with
        # conflict title / force_a / force_b — that recreates the nine-repeat seed.
        # Binding is conflict_id (+ non-empty link). Tone phrasing is enough.

    voice_entries: list[tuple[str, str, dict[str, Any]]] = []
    # (role, field, row)

    astro_rows = _as_list(chorus.get("astrology"))
    for i, row in enumerate(astro_rows):
        if isinstance(row, dict):
            voice_entries.append(("astrology", f"chorus.astrology[{i}]", row))

    card = _as_dict(chorus.get("day_card"))
    if card.get("named_factor") or card.get("link_to_conflict") or card.get("archetype_role"):
        voice_entries.append(("day_card", "chorus.day_card", card))

    number = _as_dict(chorus.get("day_number"))
    if number.get("named_factor") or number.get("link_to_conflict") or number.get("tempo"):
        voice_entries.append(("day_number", "chorus.day_number", number))

    natal_rows = _as_list(chorus.get("natal"))
    for i, row in enumerate(natal_rows):
        if isinstance(row, dict):
            voice_entries.append(("natal", f"chorus.natal[{i}]", row))

    labeled_blobs: list[tuple[str, str, set[str]]] = []
    for role, field, row in voice_entries:
        _check_conflict_binding(row, field)
        blob = _voice_text(row)
        labeled_blobs.append((role, field, _tokens(blob)))

        if _CHORUS_PARALLEL_FORECAST_RE.search(blob):
            defects.append(
                _defect(
                    DEFECT_CHORUS_PARALLEL_FORECAST,
                    field=field,
                    message="voice reads as a parallel mini-forecast, not a causal step of one story",
                )
            )

        # role drift
        if role == "astrology":
            if not _CHORUS_ENV_RE.search(blob) and not _ASTRO_TERM_RE.search(blob):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="astrology must explain external environment / sky factor for the conflict",
                    )
                )
            # astrology should not be only personal natal framing
            if _CHORUS_NATAL_PERSONAL_RE.search(blob) and not _CHORUS_ENV_RE.search(blob):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="astrology drifted into personal natal voice without environment",
                    )
                )
            named = str(row.get("named_factor") or "")
            meaning = str(row.get("human_meaning") or "")
            link = str(row.get("link_to_conflict") or "")
            if astrology_voice_lacks_human_translation(named, meaning, link):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_UNTRANSLATED_JARGON,
                        field=field,
                        message="astro term without human translation into today's conflict",
                    )
                )
                # keep legacy code for older capture rubrics
                defects.append(
                    _defect(
                        DEFECT_ASTRO_JARGON_BARE,
                        field=field,
                        message="astro term without human translation into today's conflict",
                    )
                )
        elif role == "day_card":
            archetype_role = str(row.get("archetype_role") or "").strip()
            meaning_parts = f"{archetype_role} {row.get('link_to_conflict') or ''} {row.get('human_meaning') or ''}"
            has_archetype_signal = bool(archetype_role) or bool(
                re.search(r"архетип|роль|образ|паттерн|реакц|как\s+реагир", meaning_parts, re.I)
            )
            if not has_archetype_signal:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="day_card must name an archetype / reaction pattern for the conflict",
                    )
                )
            elif _CHORUS_ENV_RE.search(meaning_parts) and not has_archetype_signal:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="day_card drifted into environment forecast (astrology's job)",
                    )
                )
            # Pure environment prose with empty archetype_role
            if (
                not archetype_role
                and _CHORUS_ENV_RE.search(meaning_parts)
                and not re.search(r"архетип|роль|образ|паттерн|реакц", meaning_parts, re.I)
            ):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="day_card drifted into environment forecast (astrology's job)",
                    )
                )
        elif role == "day_number":
            tempo_blob = f"{row.get('tempo') or ''} {row.get('style') or ''} {blob}"
            if not _CHORUS_TEMPO_RE.search(tempo_blob) and not (
                str(row.get("tempo") or "").strip() or str(row.get("style") or "").strip()
            ):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="day_number must set tempo / way of moving through the conflict",
                    )
                )
        elif role == "natal":
            if not _CHORUS_NATAL_PERSONAL_RE.search(blob):
                defects.append(
                    _defect(
                        DEFECT_CHORUS_ROLE_DRIFT,
                        field=field,
                        message="natal must name personal vulnerability or resource for this conflict",
                    )
                )
            if has_natal_evidence is False:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
                        field=field,
                        message="natal voice present without natal evidence — do not invent deep personalization",
                    )
                )
                defects.append(
                    _defect(
                        DEFECT_NATAL_WITHOUT_EVIDENCE,
                        field=field,
                        message="natal voice present without natal evidence — do not invent deep personalization",
                    )
                )

    # semantic duplication / term-swapped paragraphs
    for i in range(len(labeled_blobs)):
        for j in range(i + 1, len(labeled_blobs)):
            role_i, field_i, toks_i = labeled_blobs[i]
            role_j, field_j, toks_j = labeled_blobs[j]
            jac = _jaccard(toks_i, toks_j)
            if jac >= 0.58:
                defects.append(
                    _defect(
                        DEFECT_CHORUS_SEMANTIC_DUPLICATION,
                        field=f"{field_i}|{field_j}",
                        message="chorus voices nearly duplicate each other (same paragraph, swapped labels)",
                    )
                )
            elif jac >= 0.45 and role_i != role_j:
                # strip role-specific stopwords and re-check
                stop = {
                    "луна",
                    "солнце",
                    "карта",
                    "число",
                    "натал",
                    "астрология",
                    "день",
                    "сегодня",
                }
                ti2 = {t for t in toks_i if t not in stop}
                tj2 = {t for t in toks_j if t not in stop}
                if _jaccard(ti2, tj2) >= 0.62:
                    defects.append(
                        _defect(
                            DEFECT_CHORUS_SEMANTIC_DUPLICATION,
                            field=f"{field_i}|{field_j}",
                            message="semantic near-duplicate after removing voice labels",
                        )
                    )

    # natal without evidence when rows exist (if not already flagged per-row)
    if natal_rows and has_natal_evidence is False:
        if not any(d.get("code") == DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE for d in defects):
            defects.append(
                _defect(
                    DEFECT_CHORUS_NATAL_WITHOUT_EVIDENCE,
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

    # v3.1 seed-kill hard detectors (runtime via C3.6 GATE_RULES, not CRITICAL_DEFECTS score).
    from todayflow_backend.services.day_scenario_v1 import (
        chorus_seed_paste_needs_heal_v1,
        invented_bank_short_name_needs_heal_v1,
    )

    plot_title = str(conflict.get("title") or conflict.get("short_name") or "").strip()
    if invented_bank_short_name_needs_heal_v1(plot_title):
        defects.append(
            _defect(
                DEFECT_SEED_BANK_BINARY_SHORT_NAME,
                field="conflict.title",
                message=(
                    "Plot title is a legacy opposing-forces bank binary "
                    "(e.g. «тащить старое или…») — inventing A|B drama is forbidden; "
                    "use tone/registry short_name without pasting forces"
                ),
            )
        )
    if chorus_seed_paste_needs_heal_v1(chorus, short_name=plot_title):
        defects.append(
            _defect(
                DEFECT_SEED_CHORUS_PASTE,
                field="interpretive_chorus",
                message=(
                    "Chorus pastes conflict short_name or old bridge templates "
                    "(«подталкивает день к сюжету», «окрашивает прохождение», "
                    "«какой ролью пройти») — each voice must speak from its own factor"
                ),
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
        "Хор = одна причинная линия (C3.2), не четыре мини-прогноза:",
        "1) астрология → внешняя среда; 2) карта → архетип реакции; 3) число → темп/способ; 4) натал → личная уязвимость/ресурс.",
        "Каждый голос: conflict_id + link_to_conflict к тому же conflict; без смысловых повторов и без жаргона без перевода.",
        "Дефекты:",
    ]
    seed_codes = {DEFECT_SEED_BANK_BINARY_SHORT_NAME, DEFECT_SEED_CHORUS_PASTE}
    if any(str(d.get("code") or "") in seed_codes for d in defects):
        lines.insert(
            1,
            "SEED-KILL: не цитируй short_name/A|B в chorus; не используй шаблоны "
            "«подталкивает день к сюжету» / «окрашивает прохождение» / «какой ролью пройти»; "
            "не ставь bank-binary («тащить старое или…») в title.",
        )
    codes = {str(d.get("code") or "") for d in defects}
    if DEFECT_SCENE_MISSING_EVERYDAY in codes or DEFECT_SCENE_ABSTRACT in codes:
        lines.insert(
            len(lines) - 1,
            "everyday_example на КАЖДОЙ сцене (не только listed field): часы ЧЧ:ММ, "
            "или цитата ≥12 знаков в «ёлочках», или человек+пишет/спрашивает, или «в чате». "
            "Сцены без дефекта не укорачивай — retry не должен ломать уже валидный момент. "
            "Пример: «Рабочий чат, 11:15: коллега пишет «нам это нужно сегодня до совещания?»». "
            "setup — тот же момент, не абстрактная «напряжённость в отношениях».",
        )
    if DEFECT_CHORUS_PARALLEL_FORECAST in codes or DEFECT_CHORUS_ROLE_DRIFT in codes:
        lines.insert(
            len(lines) - 1,
            "CHORUS_PARALLEL: каждый голос — одна роль в ОДНОМ конфликте (conflict_id + link_to_conflict), "
            "не четыре отдельные «сегодня в работе… в отношениях…». "
            "astrology=среда; card=архетип реакции; number=темп; natal=личная уязвимость — без копипаста сфер.",
        )
    if DEFECT_ASTRO_JARGON_BARE in codes or DEFECT_CHORUS_UNTRANSLATED_JARGON in codes:
        lines.insert(
            len(lines) - 1,
            "astrology voice: named_factor может держать факт неба; human_meaning + link_to_conflict "
            "КАЖДОГО astrology[i] (не только [0]) ОБЯЗАНЫ перевести в среду дня "
            "(давление, темп, разговор, импульс) — "
            "не «это подталкивает день к сюжету» и не копия named_factor. "
            + SEED_JARGON_CROSS_HINT_RU,
        )
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
