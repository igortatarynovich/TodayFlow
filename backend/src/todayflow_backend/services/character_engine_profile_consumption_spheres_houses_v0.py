"""CE consumption — life_spheres + house person-lines by Identity thesis.

Natal cusp/sign/degree stay Swiss. These strings are person-voice essays only.
"""

from __future__ import annotations

import re
from typing import Any

# Sphere IDs that Profile V2 contract builder accepts (full 6 fields required).
_SPHERE_IDS = ("love", "money", "decisions", "work", "family", "friends", "body")

# Compact mechanism tag for templates.
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

_HOUSE_FOCUS: dict[int, str] = {
    1: "как ты заходишь в мир",
    2: "что для тебя ценно и чем ты себя держишь",
    3: "как думаешь и общаешься",
    4: "где ты настоящий и откуда берёшь опору",
    5: "где живёшь ради себя и творчества",
    6: "как устроены будни, тело и ритм дел",
    7: "как строишь значимую связь",
    8: "где меняешься и делишь глубину",
    9: "как ищешь смысл и горизонт",
    10: "как хочешь выглядеть в мире и реализовываться",
    11: "с кем идёшь в будущее",
    12: "где теряешь или находишь себя наедине",
}


def _mech(identity_thesis: str) -> str:
    return _MECH.get(identity_thesis, "своё ядро характера")


def build_life_spheres_for_identity_v0(identity_thesis: str) -> dict[str, dict[str, str]]:
    m = _mech(identity_thesis)
    # Shared skeleton; wording stays «ты», mechanism-specific.
    packs: dict[str, dict[str, str]] = {
        "love": {
            "how": f"В любви ты идёшь через {m}: сначала внутренний контур, потом открытость.",
            "need": "Нужно пространство, где тебя не просят сдать свой основной способ быть.",
            "risk": "Риск — держать дистанцию или анализ там, где уже пора выбрать близость.",
            "turns_on": "Включает честный темп, уважение к твоей ясности и взаимная зрелость.",
            "turns_off": "Выключает давление подогнать тебя под чужой ритм и растворить границы.",
            "helps": "Назови одно правило связи вслух — что оставляешь своим, что открываешь.",
        },
        "money": {
            "how": f"К деньгам ты относишься через {m}: ресурс должен обслуживать твой контур выбора.",
            "need": "Нужна понятная рамка, где поток средств не ломает независимость.",
            "risk": "Риск — копить контроль или схемы вместо ясного денежного шага.",
            "turns_on": "Включает свобода манёвра и честный обмен без скрытых ожиданий.",
            "turns_off": "Выключает зависимость от чужих условий и размытые договорённости.",
            "helps": "Зафиксируй один денежный приоритет на этот месяц — без идеальной схемы.",
        },
        "decisions": {
            "how": f"Решения ты собираешь через {m}: внутренний «да» важнее внешнего хора.",
            "need": "Нужно время дойти до ясности самому — без спешки чужого темпа.",
            "risk": "Риск — бесконечно уточнять картину вместо выбора.",
            "turns_on": "Включает тишина, структура и право на неполный, но честный шаг.",
            "turns_off": "Выключает давление решить «для всех» до собственной ясности.",
            "helps": "Поставь срок сбору данных — потом сделай один видимый шаг.",
        },
        "work": {
            "how": f"В работе ты проявляешься через {m}: смысл и контур важнее чужой повестки.",
            "need": "Нужна роль, где можно держать свою систему и видеть влияние.",
            "risk": "Риск — уйти в автономный перфекционизм или отложить выход в поле.",
            "turns_on": "Включает задача с ясной рамкой и свободой метода.",
            "turns_off": "Выключает микроконтроль и бессмысленная демонстрация занятости.",
            "helps": "Выбери один рабочий фронт на сегодня и закрой его до новых идей.",
        },
        "family": {
            "how": f"Дом и корни ты строишь через {m}: опора должна давать воздух, а не клетку.",
            "need": "Нужен быт, где можно восстановиться без потери себя.",
            "risk": "Риск — держать порядок или дистанцию вместо живого контакта с близкими.",
            "turns_on": "Включает уважение к границам и спокойный совместный ритм.",
            "turns_off": "Выключает вторжение в твой контур под видом «заботы».",
            "helps": "Скажи дома одно явное «мне нужно» — коротко и без оправданий.",
        },
        "friends": {
            "how": f"В круге ты выбираешь через {m}: близость идей и взаимное уважение темпа.",
            "need": "Нужны люди, с которыми можно быть цельным, не играя роль.",
            "risk": "Риск — держаться сети знакомств без настоящей выбранной связи.",
            "turns_on": "Включает честный разговор и свобода быть разным.",
            "turns_off": "Выключает обязательная социальность и скрытые долги внимания.",
            "helps": "Напиши одному человеку по делу — без поддержания «галочки» связи.",
        },
        "body": {
            "how": f"Тело ты слышишь через {m}: сигнал «хватит / можно» приходит раньше чужих норм.",
            "need": "Нужен ритм, где нагрузка и пауза согласованы с твоим контуром.",
            "risk": "Риск — игнорировать тело, пока ум или долг ведут дальше.",
            "turns_on": "Включает ясный режим и движение без насилия над собой.",
            "turns_off": "Выключает чужие стандарты формы и вечная гонка без восстановления.",
            "helps": "Сделай один телесный жест сегодня — сон, еда или прогулка — осознанно.",
        },
    }
    # Optional sex/kids — lighter, still complete for chrome if we add later.
    return {sid: packs[sid] for sid in _SPHERE_IDS if sid in packs}


def build_house_person_lines_for_identity_v0(identity_thesis: str) -> dict[str, dict[str, str]]:
    m = _mech(identity_thesis)
    out: dict[str, dict[str, str]] = {}
    for num, focus in _HOUSE_FOCUS.items():
        out[str(num)] = {
            "line": (
                f"Через {m} здесь видно {focus}: "
                f"это не энциклопедия знака, а то, как твоё ядро проявляется в этой зоне жизни."
            ),
        }
    # Stronger specific lines for angular houses (life map cards).
    specifics = {
        1: f"Ты входишь в мир через {m} — первое впечатление читается как твой контур, не маска каталога.",
        4: f"Домашняя опора собирается через {m}: здесь ты либо восстанавливаешься, либо прячешься.",
        7: f"Связь строится через {m}: партнёрство работает, когда другой не стирает твой способ быть.",
        10: f"В мире ты реализуешься через {m}: роль должна давать видимость без потери внутреннего контура.",
    }
    for num, line in specifics.items():
        out[str(num)] = {"line": line}
    return out


def matrix_style_fields_for_identity_v0(identity_thesis: str) -> dict[str, str]:
    """Contract fields that feed profile_matrix emotional / work / home slots."""
    m = _mech(identity_thesis)
    return {
        "emotional_style": (
            f"Эмоции ты пропускаешь через {m}: сначала внутренний контур и ясность, "
            f"потом проявление наружу. Чувства не обязаны быть красивыми для других — "
            f"им нужно место в твоей системе."
        ),
        "work_and_realization": (
            f"В работе ты реализуешься через {m}: роль должна давать влияние без потери "
            f"собственного контура. Видимость важна, если она не требует сдать твой способ делать."
        ),
        "home_and_security": (
            f"Дом и безопасность ты собираешь через {m}: опора должна давать воздух для "
            f"восстановления, а не клетку из чужих правил и суеты."
        ),
    }


def _norm_aspect_key(bodies: str, aspect: str) -> str:
    body_bits = re.findall(r"[A-Za-z]+", str(bodies or ""))
    asp = re.sub(r"[^a-z0-9]+", "_", str(aspect or "").strip().lower()).strip("_")
    parts = [b.lower() for b in body_bits if b]
    if asp:
        parts.append(asp)
    return "_".join(parts)


def apply_aspect_lines_to_payload(payload: dict[str, Any], *, identity_thesis: str) -> None:
    """Rewrite natal_summary aspect gists + emit FE map keyed for callout matching."""
    m = _mech(identity_thesis)
    ns = payload.get("natal_summary")
    if not isinstance(ns, dict):
        return
    notable = ns.get("notable_aspects")
    if not isinstance(notable, list) or not notable:
        return
    houses_map: dict[str, dict[str, str]] = {}
    new_notable: list[dict[str, Any]] = []
    for row in notable:
        if not isinstance(row, dict):
            continue
        bodies = str(row.get("bodies") or "").strip()
        aspect = str(row.get("aspect") or "").strip()
        if not bodies:
            new_notable.append(row)
            continue
        line = (
            f"Через {m} связка {bodies}"
            + (f" ({aspect})" if aspect else "")
            + " показывает, где ядро проявляется в карте — "
            "не энциклопедия аспекта, а напряжение/поток именно твоего механизма."
        )
        key = _norm_aspect_key(bodies, aspect)
        if key:
            houses_map[key] = {"line": line}
        # Also index by raw aspect_id if already looks like sun_moon_…
        raw_asp = aspect.lower().replace(" ", "_")
        if raw_asp and "_" in raw_asp:
            houses_map[raw_asp] = {"line": line}
        updated = dict(row)
        updated["gist"] = line
        new_notable.append(updated)
    ns = dict(ns)
    ns["notable_aspects"] = new_notable
    payload["natal_summary"] = ns
    payload["character_engine_aspect_lines_v0"] = {
        "projection_version": "character_engine_aspect_lines_v0",
        "identity_thesis": identity_thesis,
        "aspects": houses_map,
        "note": "Person-voice only; aspect geometry stays Swiss/natal engine.",
    }


def apply_spheres_and_houses_to_payload(
    payload: dict[str, Any],
    *,
    identity_thesis: str,
) -> None:
    """Mutate payload: contract.life_spheres + house lines + matrix style fields + aspects."""
    spheres = build_life_spheres_for_identity_v0(identity_thesis)
    houses = build_house_person_lines_for_identity_v0(identity_thesis)
    styles = matrix_style_fields_for_identity_v0(identity_thesis)
    contract = payload.get("profile_contract_v1")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["life_spheres"] = spheres
        contract.update(styles)
        payload["profile_contract_v1"] = contract
    payload["character_engine_house_lines_v0"] = {
        "projection_version": "character_engine_house_lines_v0",
        "identity_thesis": identity_thesis,
        "houses": houses,
        "note": "Person-voice only; cusp/sign/degree remain Swiss natal facts.",
    }
    apply_aspect_lines_to_payload(payload, identity_thesis=identity_thesis)
