"""CE consumption — life_spheres + house person-lines by Identity thesis.

Natal cusp/sign/degree stay Swiss. These strings are person-voice essays only.
Rules:
- Do not stamp the same «через {mechanism}» lead on every house/aspect/sphere.
- Angular houses (1/4/7/10) get distinct lines; other houses stay Swiss-only (no CE fill).
- Aspects keep Swiss/natal gists — CE does not overwrite with one template.
"""

from __future__ import annotations

from typing import Any

# Sphere IDs that Profile V2 contract builder accepts (full 6 fields required).
_SPHERE_IDS = ("love", "money", "decisions", "work", "family", "friends", "body")

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


def _mech(identity_thesis: str) -> str:
    return _MECH.get(identity_thesis, "своё ядро характера")


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
            "turns_off": "Выключает давление подогнать тебя под чужой ритм.",
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


def build_house_person_lines_for_identity_v0(identity_thesis: str) -> dict[str, dict[str, str]]:
    """Only angular houses get CE person-voice — avoids 12× identical stamp."""
    m = _mech(identity_thesis)
    return {
        "1": {
            "line": (
                f"Первое впечатление читается как твой контур: ты заходишь в мир, "
                f"держа {m}, а не маску под чужой темп."
            ),
        },
        "4": {
            "line": (
                "Домашняя опора — место либо восстановления, либо прятанья. "
                "Важно заметить, чем дом становится для тебя сейчас."
            ),
        },
        "7": {
            "line": (
                "Связь работает, когда другой не стирает твой способ быть. "
                "Партнёрство просит ясности границ, не растворения."
            ),
        },
        "10": {
            "line": (
                "В мире роль должна давать видимость без потери внутреннего контура. "
                "Реализация — про влияние, которое ты выбираешь."
            ),
        },
    }


def matrix_style_fields_for_identity_v0(identity_thesis: str) -> dict[str, str]:
    """Contract fields that feed profile_matrix emotional / work / home slots."""
    m = _mech(identity_thesis)
    return {
        "emotional_style": (
            f"Эмоции сначала проходят через внутренний контур — {m} — "
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
    """Do not overwrite every aspect gist with the same CE template.

    Swiss/natal descriptions stay authoritative. Empty CE map = FE uses callout text.
    """
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
        "projection_version": "character_engine_house_lines_v0.2",
        "identity_thesis": identity_thesis,
        "houses": houses,
        "note": "Person-voice only on angular houses; cusp/sign/degree remain Swiss.",
    }
    apply_aspect_lines_to_payload(payload, identity_thesis=identity_thesis)
