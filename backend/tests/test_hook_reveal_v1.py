"""hook_reveal_v1 + static base banks."""

from __future__ import annotations

from todayflow_backend.data import card_base_v1, number_base_v1
from todayflow_backend.services import hook_reveal_v1 as hooks


def test_number_base_valid_and_stable():
    assert number_base_v1.validate_number_base_v1() == []
    a = number_base_v1.get_number_base(7)
    b = number_base_v1.get_number_base(7)
    assert a and b
    assert a["base_meaning"] == b["base_meaning"]
    assert "наблюден" in a["base_meaning"].lower() or "пауз" in a["base_meaning"].lower()


def test_card_base_valid_78_both_orientations():
    assert card_base_v1.validate_card_base_v1() == []
    up = card_base_v1.get_base_meaning(0, "upright")
    rev = card_base_v1.get_base_meaning(0, "reversed")
    assert up and rev
    assert up["meaning"] != rev["meaning"]
    assert up["orientation"] == "upright"
    assert rev["orientation"] == "reversed"


def test_number_hook_bridge_from_chorus_only():
    hook = hooks.build_number_hook_reveal(
        value=7,
        chorus={"day_number": {"link_to_conflict": "замедляет давление в этом конфликте"}},
    )
    assert hook["base"]["meaning"]
    assert hook["bridge_status"] == "ok"
    assert hook["bridge_to_day"] == "замедляет давление в этом конфликте"


def test_number_hook_bridge_fail_keeps_base():
    hook = hooks.build_number_hook_reveal(value=7, chorus={})
    assert hook["base"]["meaning"]
    assert hook["bridge_status"] == "unavailable"
    assert hook["bridge_to_day"] is None
    assert "Не удалось раскрыть" in (hook.get("bridge_fail_copy") or "")


def test_card_hook_bridge_fail_keeps_base():
    hook = hooks.build_card_hook_reveal(card_id=16, orientation="reversed", chorus=None)
    assert hook["identity"]["orientation"] == "reversed"
    assert hook["base"]["meaning"]
    assert hook["bridge_status"] == "unavailable"
    assert hook["bridge_fail_copy"]


def test_card_hook_does_not_use_parallel_bridge_fields_as_base():
    hook = hooks.build_card_hook_reveal(
        card_id=0,
        orientation="upright",
        chorus={"day_card": {"link_to_conflict": "архетип описывает сегодняшний конфликт"}},
        instruction="Сделай один маленький старт.",
    )
    assert hook["bridge_status"] == "ok"
    assert hook["instruction"] == "Сделай один маленький старт."
    # base must stay from bank, not chorus
    bank = card_base_v1.get_base_meaning(0, "upright")
    assert hook["base"]["meaning"] == bank["meaning"]


def test_card_hook_rejects_conflict_id_slug_as_bridge():
    """Regression: LLM stuffed conflict_id into link_to_conflict → raw id on Symbols."""
    hook = hooks.build_card_hook_reveal(
        card_id=0,
        orientation="upright",
        chorus={
            "day_card": {
                "link_to_conflict": "conflict.intensity_without_drama",
                "conflict_id": "conflict.intensity_without_drama",
                "archetype_role": "intensity_without_drama",
            }
        },
    )
    assert hook["bridge_status"] == "unavailable"
    assert hook["bridge_to_day"] is None
    assert "Не удалось раскрыть" in (hook.get("bridge_fail_copy") or "")
    assert hook["base"]["meaning"]  # base still shown


def test_color_hook_uses_props_link():
    hook = hooks.build_color_hook_reveal(
        color_name="Лазурь",
        props_color={
            "name": "Лазурь",
            "link_to_conflict": "якорь ясности против срыва",
            "where_to_use": "один акцент в одежде",
        },
    )
    assert hook["base"]["meaning"]
    assert hook["bridge_status"] == "ok"
    assert hook["bridge_to_day"] == "якорь ясности против срыва"
    assert hook["instruction"]


def test_color_hook_formats_where_to_use_object():
    """Regression: where_to_use is a dict in day_scenario props — never str(dict)."""
    hook = hooks.build_color_hook_reveal(
        color_name="Янтарный",
        props_color={
            "name": "Янтарный",
            "link_to_conflict": "тёплая энергия без суеты",
            "where_to_use": {
                "clothing": "Янтарный шарф",
                "accessory": "Украшение медового оттенка",
                "workspace": None,
            },
        },
    )
    assert hook["bridge_status"] == "ok"
    assert hook["instruction"] == "Янтарный шарф · Украшение медового оттенка"
    assert "{" not in (hook["instruction"] or "")
