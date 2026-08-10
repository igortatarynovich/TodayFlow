"""Wave B1 — welcome_glass / today_progress / color_guide unit tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import json

from todayflow_backend.services.today_contract_assembler_v1 import (
    assemble_today_contract_v1,
    validate_today_contract_v1,
)
from todayflow_backend.services.today_contract_nests_b1_v1 import (
    attach_b1_nests_to_contract,
    build_color_guide_v1,
    build_welcome_glass_v1,
)

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "today_contract_v1"


def test_welcome_glass_mood_tags_from_visual_mode():
    glass = build_welcome_glass_v1(visual_mode="flow")
    assert glass["mood_tags"] == ["Мягкая чувствительность", "Идти по течению"]
    assert glass["reason"] is None
    assert glass["good_for"] == []


def test_welcome_glass_reason_lunar_no_invent():
    glass = build_welcome_glass_v1(
        visual_mode="clarity",
        lunar_name="Растущая луна",
        lunar_themes="Время уточнять один шаг. Остальное позже.",
    )
    assert glass["reason"] == "Растущая луна — Время уточнять один шаг."
    assert glass["mood_tags"] == ["Ясный ум", "Порядок в делах"]


def test_welcome_glass_good_for_from_do_short_only():
    glass = build_welcome_glass_v1(
        do_items=[
            "Один звонок",
            "Это слишком длинная строка для чипа",
            "Фокус",
            "один звонок",  # dupe
            "Шаг",
            "Ещё",
        ]
    )
    assert glass["good_for"] == ["Один звонок", "Фокус", "Шаг"]


def test_welcome_glass_unknown_mode_empty_mood():
    glass = build_welcome_glass_v1(visual_mode="not-a-mode", lunar_name="")
    assert glass["mood_tags"] == []
    assert glass["reason"] is None


def test_color_guide_from_props_fill_empty_catalog():
    guide = build_color_guide_v1(
        day_story={
            "day_scenario": {
                "props": {
                    "color": {
                        "name": "Лазурь",
                        "intensity": "лёгкий акцент",
                        "where_to_use": {"clothing": "Шарф лазурного."},
                    },
                    "avoid_color": {"name": "кислотный жёлтый", "why": "Размывает точность."},
                }
            }
        },
        target_month=6,
    )
    assert guide is not None
    assert guide["name"] == "Лазурь"
    assert guide["intensity"] == "лёгкий акцент"
    assert guide["clothing"] == "Шарф лазурного."
    assert guide["avoid"] == "кислотный жёлтый"
    assert guide["avoid_why"] == "Размывает точность."
    # Catalog fill-empty for accessory when missing
    assert guide.get("accessory")


def test_color_guide_talisman_fallback_and_null_without_name():
    guide = build_color_guide_v1(
        day_story={
            "talisman": {
                "color": "Янтарный",
                "avoid_color": "Холодный стальной",
                "avoid_why": "Усиливает контроль.",
            }
        }
    )
    assert guide is not None
    assert guide["name"] == "Янтарный"
    assert guide["avoid"] == "Холодный стальной"
    assert build_color_guide_v1(day_story={"talisman": {}}) is None


def test_attach_nests_on_contract_dict():
    contract = {
        "day_atmosphere": {"visual_mode": "radiance"},
        "day_story": {
            "do": ["Шаг", "Пауза"],
            "day_foundation": {
                "lunar": {"phase": {"name": "Полнолуние", "guidance": "Держи один фокус."}}
            },
            "day_scenario": {"props": {"color": {"name": "Изумрудный"}}},
        },
    }
    out = attach_b1_nests_to_contract(contract, target_date=date(2026, 8, 9))
    assert out["welcome_glass"]["mood_tags"] == ["Проявить себя", "Открытый контакт"]
    assert out["welcome_glass"]["reason"]
    assert out["welcome_glass"]["good_for"] == ["Шаг", "Пауза"]
    assert out["color_guide"]["name"] == "Изумрудный"
    assert out["today_progress"] == {"rows": []}


def test_welcome_glass_reason_does_not_fail_legacy_key_validation():
    """Regression: B1 welcome_glass.reason must not trip legacy-key scan (prod 500)."""
    from todayflow_backend.services.today_contract_assembler_v1 import _collect_forbidden_keys

    raw = json.loads((_FIXTURES / "full_legacy_payload.json").read_text(encoding="utf-8"))
    contract = assemble_today_contract_v1(
        spheres=raw.get("spheres"),
        narrative=raw.get("narrative"),
        morning_ritual=raw.get("morning_ritual"),
        fusion=raw.get("fusion"),
        fallback_context=raw.get("fallback_context"),
    )
    contract["day_atmosphere"] = {"visual_mode": "radiance"}
    contract["day_story"] = {
        "do": ["Шаг"],
        "day_foundation": {
            "lunar": {"phase": {"name": "Полнолуние", "guidance": "Держи один фокус."}}
        },
    }
    attach_b1_nests_to_contract(contract, target_date=date(2026, 8, 10))
    assert contract["welcome_glass"]["reason"]
    forbidden = _collect_forbidden_keys(contract)
    assert "welcome_glass.reason" not in forbidden
    assert not any(path.startswith("welcome_glass.") for path in forbidden)
    errors = validate_today_contract_v1(contract)
    assert not any("legacy keys" in e for e in errors)
