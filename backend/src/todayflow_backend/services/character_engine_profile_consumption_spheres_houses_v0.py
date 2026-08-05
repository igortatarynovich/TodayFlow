"""CE consumption — life_spheres + applied ASC/house cards by Identity thesis.

Natal cusp/sign/degree stay Swiss. CE owns person-voice how+do only.
Rules:
- Do not stamp the same «через {mechanism}» lead on every house/aspect/sphere.
- Emit ASC + MC + **all 12 houses** with factor how+do (domain + cusp modality + planet function when occupied).
- Aspects keep Swiss/natal gists — CE does not overwrite with one template.
"""

from __future__ import annotations

from typing import Any

# Sphere IDs that Profile V2 contract builder accepts (full 6 fields required).
_SPHERE_IDS = ("love", "money", "decisions", "work", "family", "friends", "body")

_ANGULAR = frozenset({1, 4, 7, 10})
_PERSONAL_PLANETS = frozenset({"Sun", "Moon", "Mercury", "Venus", "Mars"})

# Compact mechanism tag — used sparingly (not every line).
_MECH: dict[str, str] = {
    "builds_through_autonomy": "автономию и собственную систему",
    "builds_through_analysis": "анализ до шага",
    "builds_through_air_mind": "идеи и связи",
    "builds_through_earth_stability": "осязаемую опору",
    "builds_through_water_care": "заботу и проницаемость",
    "builds_through_emotional_depth": "эмоциональную глубину",
    "builds_through_earth_anchor": "привычный якорь и порядок",
    "builds_through_freedom_vs_stability": "ось свободы и опоры",
    "builds_through_fire_drive": "импульс действия",
    "builds_through_air_presence": "лёгкий контакт и разговор",
    "builds_through_fire_presence": "прямой вход",
    "builds_through_earth_presence": "плотную надёжную форму",
    "builds_through_water_presence": "чуткий вход",
}

_SIGN_RU: dict[str, str] = {
    "aries": "Овне",
    "taurus": "Тельце",
    "gemini": "Близнецах",
    "cancer": "Раке",
    "leo": "Льве",
    "virgo": "Деве",
    "libra": "Весах",
    "scorpio": "Скорпионе",
    "sagittarius": "Стрельце",
    "capricorn": "Козероге",
    "aquarius": "Водолее",
    "pisces": "Рыбах",
}

_SIGN_ELEMENT: dict[str, str] = {
    "aries": "fire",
    "taurus": "earth",
    "gemini": "air",
    "cancer": "water",
    "leo": "fire",
    "virgo": "earth",
    "libra": "air",
    "scorpio": "water",
    "sagittarius": "fire",
    "capricorn": "earth",
    "aquarius": "air",
    "pisces": "water",
}

# Cusp sign → short modality thesis (compressed; not encyclopedia).
_SIGN_MODALITY: dict[str, str] = {
    "aries": "прямой старт",
    "taurus": "устойчивость без спешки",
    "gemini": "разговор и варианты",
    "cancer": "безопасность «своих»",
    "leo": "быть увиденным",
    "virgo": "точность деталей",
    "libra": "взаимность и баланс",
    "scorpio": "дозированный доступ",
    "sagittarius": "смысл и горизонт",
    "capricorn": "обязательства и статус",
    "aquarius": "дистанция идей",
    "pisces": "эмпатия и мягкие границы",
}

_PLANET_RU: dict[str, str] = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
}

# Personal planet in house — short function tag.
_PLANET_FUNCTION: dict[str, str] = {
    "Sun": "воля заметнее",
    "Moon": "нужна безопасность",
    "Mercury": "речь и договорённости",
    "Venus": "притяжение и оценка",
    "Mars": "инициатива и темп",
}

# Person-facing theses (not house encyclopedia). do = one check.
_HOUSE_ZONE: dict[int, dict[str, str]] = {
    1: {
        "how": "В первом контакте тебя считывают по темпу и дистанции — ещё до знакомства с ядром.",
        "do": "В одном новом контакте отметь первый жест: ближе, дальше или сразу правила?",
    },
    2: {
        "how": "Самооценка для тебя читается через «это моё» — деньги, навыки, право не оправдываться.",
        "do": "Назови одну вещь или навык, который сегодня не отдаёшь «ради мира».",
    },
    3: {
        "how": "Ты думаешь вслух рядом — учёба, спор, факты для ближайшего круга.",
        "do": "Скажи одно конкретное предложение по делу — без смягчения «никого не задеть».",
    },
    4: {
        "how": "Дом и приватный ритм показывают, чем ты реально заряжаешься и от чего прячешься.",
        "do": "Сделай дома один завершённый жест восстановления — и отметь начало/конец.",
    },
    5: {
        "how": "Игра, творчество и риск «ради себя» — здесь видно, умеешь ли ты жить не только ролью.",
        "do": "Выдели 20 минут на занятие без пользы для резюме — и не оправдывай его.",
    },
    6: {
        "how": "Режим тела и мелочей либо держит тебя, либо копится как долг.",
        "do": "Закрой один мелкий бытовой или телесный долг — с явным «готово».",
    },
    7: {
        "how": "В равных отношениях важно, умеешь ли ты держать явные правила двоих.",
        "do": "Зафиксируй с близким одно правило двоих (время, деньги, доступ) — без намёков.",
    },
    8: {
        "how": "Совместные ресурсы и необратимые перемены — здесь контроль спорит с уязвимостью.",
        "do": "Назови себе одной фразой момент, где держишь контроль вместо прямого разговора.",
    },
    9: {
        "how": "Тебе нужна рамка смысла шире «как сделать» — убеждения, учёба, горизонт.",
        "do": "Запиши одним предложением «зачем этот месяц» — без плана на год.",
    },
    10: {
        "how": "Публичная роль показывает, по какому следу тебя судят о результате.",
        "do": "Выбери один видимый рабочий результат и доведи до проверяемого «сделано».",
    },
    11: {
        "how": "В сети и общем будущем важно, где взаимный вектор, а где только поддержка контакта.",
        "do": "Напиши одному человеку по конкретному делу — без «просто поддержать связь».",
    },
    12: {
        "how": "Вне зрителей ты либо восстанавливаешься, либо теряешь себя без свидетелей.",
        "do": "10 минут без экрана: отметь первый телесный сигнал (напряжение, голод, сон).",
    },
}

# Angular + autonomy: still theses, not paragraphs.
_ANGULAR_AUTONOMY_HOW: dict[int, str] = {
    1: "В первом контакте сначала проверка, что тебя не переформатируют — потом открытость.",
    4: "Приватное пространство работает, только если даёт воздух для себя.",
    7: "Устойчивая связь = отдельные решения без разрыва и без «мы вместо я».",
    10: "Ты держишься в поле достижений, когда видимость не требует сдать свой метод.",
}


def _mech(identity_thesis: str) -> str:
    return _MECH.get(identity_thesis, "своё ядро характера")


def _norm_sign(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    aliases = {
        "овен": "aries",
        "телец": "taurus",
        "близнецы": "gemini",
        "рак": "cancer",
        "лев": "leo",
        "дева": "virgo",
        "весы": "libra",
        "скорпион": "scorpio",
        "стрелец": "sagittarius",
        "козерог": "capricorn",
        "водолей": "aquarius",
        "рыбы": "pisces",
    }
    if s in aliases:
        return aliases[s]
    if s in _SIGN_RU:
        return s
    return s if s in _SIGN_ELEMENT else None


def _sign_ru_prep(sign: str | None) -> str | None:
    if not sign:
        return None
    return _SIGN_RU.get(sign)


def _sign_tint_clause(sign: str | None) -> str:
    """Fold cusp modality into one short clause — no «куспид в …» encyclopedia tag."""
    if not sign:
        return ""
    modality = _SIGN_MODALITY.get(sign, "")
    if not modality:
        return ""
    return f" Темп зоны — {modality}."


def _planet_function_clause(planets: list[str]) -> str:
    """One short accent from personal planets — not a label dump."""
    if not planets:
        return ""
    bits: list[str] = []
    for p in planets[:2]:
        fn = _PLANET_FUNCTION.get(p)
        if fn:
            bits.append(fn)
    if not bits:
        return ""
    return " Здесь заметнее " + ", ".join(bits) + "."

def _card(how: str, do: str, *, anchors: dict[str, Any] | None = None) -> dict[str, Any]:
    how_c = " ".join(how.split()).strip()
    do_c = " ".join(do.split()).strip()
    row: dict[str, Any] = {
        "how": how_c,
        "do": do_c,
        "line": how_c,  # backward-compat alias for FE readers of `.line`
    }
    if anchors:
        row["anchors"] = anchors
    return row


def build_life_spheres_for_identity_v0(identity_thesis: str) -> dict[str, dict[str, str]]:
    """Domain-first sphere copy. Mechanism appears in at most one lead per pack."""
    m = _mech(identity_thesis)
    packs: dict[str, dict[str, str]] = {
        "love": {
            "how": (
                f"В любви сначала нужен внутренний контур, потом открытость — "
                f"иначе связь давит на твой способ держаться через {m}."
            ),
            "need": "Нужно пространство, где тебя не просят сдать свой основной способ быть.",
            "risk": "Риск — держать дистанцию там, где уже пора выбрать близость.",
            "turns_on": "Включает честный темп, уважение к ясности и взаимная зрелость.",
            "turns_off": "Выключает давление подогнать тебя под чужой темп.",
            "helps": "Назови одно правило связи вслух — что оставляешь своим, что открываешь.",
        },
        "money": {
            "how": "К деньгам ты относишься как к ресурсу независимости: поток должен обслуживать выбор, а не чужие ожидания.",
            "need": "Нужна понятная рамка, где поток средств не ломает независимость.",
            "risk": "Риск — копить схемы вместо одного ясного денежного шага.",
            "turns_on": "Включает свобода манёвра и честный обмен без скрытых ожиданий.",
            "turns_off": "Выключает зависимость от чужих условий и размытые договорённости.",
            "helps": "Зафиксируй один денежный приоритет на этот месяц — без идеальной схемы.",
        },
        "decisions": {
            "how": "Решения зреют, когда внутренний «да» собран — внешний хор редко ускоряет ясность.",
            "need": "Нужно время дойти до ясности самому — без спешки чужого темпа.",
            "risk": "Риск — бесконечно уточнять картину вместо выбора.",
            "turns_on": "Включает тишина, структура и право на неполный, но честный шаг.",
            "turns_off": "Выключает давление решить «для всех» до собственной ясности.",
            "helps": "Поставь срок сбору данных — потом сделай один видимый шаг.",
        },
        "work": {
            "how": "В работе смысл и метод важнее чужой повестки: роль должна давать влияние без потери контура.",
            "need": "Нужна роль, где можно держать свою систему и видеть влияние.",
            "risk": "Риск — уйти в автономный перфекционизм или отложить выход в поле.",
            "turns_on": "Включает задача с ясной рамкой и свободой метода.",
            "turns_off": "Выключает микроконтроль и бессмысленная демонстрация занятости.",
            "helps": "Выбери один рабочий фронт на сегодня и закрой его до новых идей.",
        },
        "family": {
            "how": "Дом должен давать воздух для восстановления, а не клетку из чужих правил.",
            "need": "Нужен быт, где можно восстановиться без потери себя.",
            "risk": "Риск — держать порядок или дистанцию вместо живого контакта с близкими.",
            "turns_on": "Включает уважение к границам и спокойный совместный ритм.",
            "turns_off": "Выключает вторжение в твой контур под видом «заботы».",
            "helps": "Скажи дома одно явное «мне нужно» — коротко и без оправданий.",
        },
        "friends": {
            "how": "В круге важны близость идей и взаимное уважение темпа — не обязательная социальность.",
            "need": "Нужны люди, с которыми можно быть цельным, не играя роль.",
            "risk": "Риск — держаться сети знакомств без настоящей взаимной связи.",
            "turns_on": "Включает честный разговор и свобода быть разным.",
            "turns_off": "Выключает обязательная социальность и скрытые долги внимания.",
            "helps": "Напиши одному человеку по делу — без поддержания «галочки» связи.",
        },
        "body": {
            "how": "Тело сигналит «хватит / можно» раньше чужих норм — если дать этому голос.",
            "need": "Нужен ритм, где нагрузка и пауза согласованы с твоим контуром.",
            "risk": "Риск — игнорировать тело, пока ум или долг ведут дальше.",
            "turns_on": "Включает ясный режим и движение без насилия над собой.",
            "turns_off": "Выключает чужие стандарты формы и гонка без восстановления.",
            "helps": "Сделай один телесный жест сегодня — сон, еда или прогулка — осознанно.",
        },
    }
    return {sid: packs[sid] for sid in _SPHERE_IDS if sid in packs}


def extract_swiss_house_asc_anchors_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Pull cusp signs, ASC/MC, and personal planets-in-house from payload."""
    cusp_signs: dict[int, str] = {}
    asc_sign: str | None = None
    mc_sign: str | None = None
    planets_by_house: dict[int, list[str]] = {}

    diagnostics = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else {}
    stage2_art = diagnostics.get("character_engine_stage2") if isinstance(diagnostics, dict) else None
    stage0 = {}
    if isinstance(stage2_art, dict):
        stage0 = stage2_art.get("stage0") if isinstance(stage2_art.get("stage0"), dict) else {}
    facts = stage0.get("raw_facts") if isinstance(stage0.get("raw_facts"), list) else []

    for row in facts:
        if not isinstance(row, dict):
            continue
        ft = str(row.get("fact_type") or "").strip().lower()
        value = row.get("value")
        sign = None
        if isinstance(value, dict):
            sign = _norm_sign(value.get("sign"))
        else:
            sign = _norm_sign(value)
        if ft.startswith("house_cusp_sign:") and sign:
            try:
                house = int(ft.split(":", 1)[1])
            except (TypeError, ValueError):
                continue
            if 1 <= house <= 12:
                cusp_signs[house] = sign
        elif ft == "angle_sign:ascendant" and sign:
            asc_sign = sign
        elif ft == "angle_sign:mc" and sign:
            mc_sign = sign

    natal = payload.get("natal_summary") if isinstance(payload.get("natal_summary"), dict) else {}
    angles = natal.get("angles") if isinstance(natal.get("angles"), dict) else {}
    if not asc_sign:
        asc_sign = _norm_sign(angles.get("ascendant_sign"))
    if not mc_sign:
        mc_sign = _norm_sign(angles.get("midheaven_sign"))
    # House 1 cusp often equals ASC; house 10 often MC.
    if asc_sign and 1 not in cusp_signs:
        cusp_signs[1] = asc_sign
    if mc_sign and 10 not in cusp_signs:
        cusp_signs[10] = mc_sign

    # Fill remaining cusps from natal_summary.houses when stage0 facts are sparse.
    houses_raw = natal.get("houses")
    if isinstance(houses_raw, list):
        for item in houses_raw:
            if not isinstance(item, dict):
                continue
            try:
                house = int(item.get("house")) if item.get("house") is not None else None
            except (TypeError, ValueError):
                house = None
            sign = _norm_sign(item.get("sign"))
            if house and 1 <= house <= 12 and sign and house not in cusp_signs:
                cusp_signs[house] = sign
    elif isinstance(houses_raw, dict):
        for key, item in houses_raw.items():
            try:
                house = int(key)
            except (TypeError, ValueError):
                continue
            sign = None
            if isinstance(item, dict):
                sign = _norm_sign(item.get("sign"))
            else:
                sign = _norm_sign(item)
            if 1 <= house <= 12 and sign and house not in cusp_signs:
                cusp_signs[house] = sign

    for bucket in ("luminaries", "personal_planets"):
        rows = natal.get(bucket) if isinstance(natal.get(bucket), list) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").strip()
            if name not in _PERSONAL_PLANETS:
                continue
            try:
                house = int(row.get("house")) if row.get("house") is not None else None
            except (TypeError, ValueError):
                house = None
            if house is None or not (1 <= house <= 12):
                continue
            planets_by_house.setdefault(house, [])
            if name not in planets_by_house[house]:
                planets_by_house[house].append(name)

    return {
        "cusp_signs": cusp_signs,
        "asc_sign": asc_sign,
        "mc_sign": mc_sign,
        "planets_by_house": planets_by_house,
    }


def build_asc_applied_v0(
    identity_thesis: str,
    *,
    asc_sign: str | None,
) -> dict[str, Any] | None:
    """Applied ASC card: first-contact thesis + one check. None when ASC unknown."""
    if not asc_sign:
        return None
    ru = _sign_ru_prep(asc_sign)
    modality = _SIGN_MODALITY.get(asc_sign, "свой темп")
    if identity_thesis == "builds_through_autonomy":
        how = (
            f"ASC в {ru or 'знаке'}: вход через {modality}; "
            "сначала проверка, что тебя не переформатируют."
        )
        do = "В новом знакомстве отметь первый жест: дистанция, шаг ближе или сразу правила?"
    else:
        how = f"ASC в {ru or 'знаке'}: первый контакт через {modality} — манера начинать, не весь характер."
        do = "В одном новом контакте отметь первый жест — дистанция, тепло или анализ."
    return {
        "sign": asc_sign,
        **_card(how, do, anchors={"sign": asc_sign}),
    }


def build_mc_applied_v0(
    identity_thesis: str,
    *,
    mc_sign: str | None,
) -> dict[str, Any] | None:
    if not mc_sign:
        return None
    ru = _sign_ru_prep(mc_sign)
    modality = _SIGN_MODALITY.get(mc_sign, "свой критерий результата")
    if identity_thesis == "builds_through_autonomy":
        how = (
            f"MC в {ru or 'знаке'}: публичная роль через {modality}; "
            "видимость без сдачи своего метода."
        )
    else:
        how = f"MC в {ru or 'знаке'}: публичная роль и результат через {modality}."
    do = "Выбери один видимый результат на сегодня — маленький, но названный."
    return {
        "sign": mc_sign,
        **_card(how, do, anchors={"sign": mc_sign}),
    }


def _house_how_do(
    house: int,
    *,
    identity_thesis: str,
    cusp_sign: str | None,
    planets: list[str],
) -> tuple[str, str]:
    zone = _HOUSE_ZONE.get(house) or {
        "how": "Эта зона жизни читается по куспиду и занятым личным планетам — без общей энциклопедии дома.",
        "do": "Заметь один момент сегодня, где эта зона уже видна в поведении.",
    }
    if house in _ANGULAR and identity_thesis == "builds_through_autonomy":
        how = _ANGULAR_AUTONOMY_HOW.get(house, zone["how"])
    else:
        how = zone["how"]
    how = how + _sign_tint_clause(cusp_sign)
    how = how + _planet_function_clause(planets)
    return how, zone["do"]


def build_house_person_lines_for_identity_v0(
    identity_thesis: str,
    *,
    cusp_signs: dict[int, str] | None = None,
    planets_by_house: dict[int, list[str]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Applied house cards for all 12 houses: domain + cusp modality + planet function when occupied."""
    cusp_signs = cusp_signs or {}
    planets_by_house = planets_by_house or {}
    out: dict[str, dict[str, Any]] = {}
    for house in range(1, 13):
        planets = [p for p in planets_by_house.get(house, []) if p in _PERSONAL_PLANETS]
        # Stable planet order
        planets = [p for p in ("Sun", "Moon", "Mercury", "Venus", "Mars") if p in planets]
        cusp = cusp_signs.get(house)
        how, do = _house_how_do(
            house,
            identity_thesis=identity_thesis,
            cusp_sign=cusp,
            planets=planets,
        )
        anchors: dict[str, Any] = {}
        if cusp:
            anchors["cusp_sign"] = cusp
        if planets:
            anchors["planets"] = planets
        out[str(house)] = _card(how, do, anchors=anchors or None)
    return out


# Back-compat name used by older tests / callers expecting angular-only map.
def build_house_person_lines_angular_only_v0(identity_thesis: str) -> dict[str, dict[str, Any]]:
    return build_house_person_lines_for_identity_v0(identity_thesis)


def matrix_style_fields_for_identity_v0(identity_thesis: str) -> dict[str, str]:
    """Contract fields that feed profile_matrix emotional / work / home slots."""
    m = _mech(identity_thesis)
    return {
        "emotional_style": (
            f"Эмоции ты сначала проводишь через внутренний контур — {m} — "
            f"и только потом наружу. Им нужно место в твоей системе, не красивость для других."
        ),
        "work_and_realization": (
            "В работе роль должна давать влияние без потери собственного контура. "
            "Видимость важна, если она не требует сдать твой способ делать."
        ),
        "home_and_security": (
            "Дом и безопасность — воздух для восстановления, а не клетка из чужих правил и суеты."
        ),
    }


def apply_aspect_lines_to_payload(payload: dict[str, Any], *, identity_thesis: str) -> None:
    """Do not overwrite every aspect gist with the same CE template."""
    del identity_thesis  # reserved for future differentiated aspect essays
    payload["character_engine_aspect_lines_v0"] = {
        "projection_version": "character_engine_aspect_lines_v0.2",
        "aspects": {},
        "note": (
            "No blanket CE stamp on aspects — natal/Swiss gist remains. "
            "Differentiated aspect essays may land later."
        ),
    }


def apply_spheres_and_houses_to_payload(
    payload: dict[str, Any],
    *,
    identity_thesis: str,
) -> None:
    """Mutate payload: contract.life_spheres + applied ASC/houses + matrix + aspects."""
    spheres = build_life_spheres_for_identity_v0(identity_thesis)
    anchors = extract_swiss_house_asc_anchors_v0(payload)
    houses = build_house_person_lines_for_identity_v0(
        identity_thesis,
        cusp_signs=anchors["cusp_signs"],
        planets_by_house=anchors["planets_by_house"],
    )
    styles = matrix_style_fields_for_identity_v0(identity_thesis)
    contract = payload.get("profile_contract_v1")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["life_spheres"] = spheres
        contract.update(styles)
        payload["profile_contract_v1"] = contract
    payload["character_engine_house_lines_v0"] = {
        "projection_version": "character_engine_house_lines_v0.6",
        "identity_thesis": identity_thesis,
        "houses": houses,
        "note": (
            "One concise person thesis per house (how+do); cusp/planet fold into the sentence. "
            "Cusp/sign/degree remain Swiss. Long natal prose = Natal Decode one-shot only."
        ),
    }
    asc = build_asc_applied_v0(identity_thesis, asc_sign=anchors.get("asc_sign"))
    mc = build_mc_applied_v0(identity_thesis, mc_sign=anchors.get("mc_sign"))
    payload["character_engine_asc_v0"] = {
        "projection_version": "character_engine_asc_v0.1",
        "identity_thesis": identity_thesis,
        "asc": asc,
        "mc": mc,
        "note": "Applied first-contact / role cards; omit when angle unknown.",
    }
    apply_aspect_lines_to_payload(payload, identity_thesis=identity_thesis)
