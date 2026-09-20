"""Subscriber deep themes L3 — K16 derived from grounded K07 how/need/risk."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from todayflow_backend.services.profile_deep_themes_v0 import (
    PIC_F,
    PIC_K,
    apply_deep_themes_to_payload,
    build_tips_by_theme,
    can_change_selection,
    derive_practical_tips_from_k07_sphere,
    theme_cap_for_billing,
)

_K07_MONEY = {
    "how": "act / pursue — possessions, money.",
    "need": "possessions, money, personal-resources",
    "risk": "Сила в точности, а срыв — когда торопишь вывод.",
}


def test_pic_k16_cites_f06() -> None:
    assert PIC_K == ("K16",)
    assert PIC_F == ("F06",)


def test_caps_by_billing() -> None:
    assert theme_cap_for_billing("free") == 0
    assert theme_cap_for_billing("lite") == 1
    assert theme_cap_for_billing("pro") == 2


def test_change_window_blocks_material_change() -> None:
    now = datetime(2026, 7, 27, tzinfo=timezone.utc)
    prev_at = now - timedelta(days=2)
    ok, unlock = can_change_selection(
        previous=["money"],
        previous_updated_at=prev_at,
        new_selected=["sex"],
        now=now,
    )
    assert ok is False
    assert unlock is not None
    ok2, _ = can_change_selection(
        previous=["money"],
        previous_updated_at=prev_at,
        new_selected=["money"],
        now=now,
    )
    assert ok2 is True


def test_tips_derive_from_k07_how_need_max_two() -> None:
    tips = derive_practical_tips_from_k07_sphere(_K07_MONEY)
    assert 1 <= len(tips) <= 2
    blob = " ".join(tips)
    assert "act / pursue" in blob or "possessions, money" in blob
    assert "медленнее" not in blob
    assert "Один денежный шаг на эту неделю" not in blob


def test_tips_omit_without_grounded_k07_sphere() -> None:
    pack = build_tips_by_theme(["money", "sex"], {"work": {"how": "x", "need": "y"}})
    assert pack == {}
    empty = derive_practical_tips_from_k07_sphere({})
    assert empty == []
    assert derive_practical_tips_from_k07_sphere(None) == []


def test_tips_do_not_depend_on_identity_thesis() -> None:
    spheres = {"money": dict(_K07_MONEY)}
    a = build_tips_by_theme(["money"], spheres)
    b = build_tips_by_theme(["money"], spheres)
    assert a == b
    assert a["money"]["tips"] == derive_practical_tips_from_k07_sphere(_K07_MONEY)


def test_apply_does_not_rewrite_life_spheres() -> None:
    spheres = {
        "money": dict(_K07_MONEY),
    }
    payload = {
        "profile_contract_v1": {"life_spheres": spheres},
        "character_engine_consumption_v0": {"identity_thesis": "builds_through_autonomy"},
    }
    settings = SimpleNamespace(
        profile_deep_themes={
            "selected": ["money"],
            "updated_at": "2026-01-01T00:00:00+00:00",
        }
    )
    out = apply_deep_themes_to_payload(
        payload,
        settings=settings,  # type: ignore[arg-type]
        billing_level="lite",
        access_allows_reveal=True,
        identity_thesis="builds_through_autonomy",
    )
    assert out["profile_contract_v1"]["life_spheres"]["money"]["how"] == _K07_MONEY["how"]
    assert out["profile_contract_v1"]["life_spheres"]["money"]["need"] == _K07_MONEY["need"]
    nest = out["character_engine_deep_themes_v0"]
    assert nest["gated"] is False
    assert nest["selected"] == ["money"]
    tips = nest["tips_by_theme"]["money"]["tips"]
    assert 1 <= len(tips) <= 2
    assert nest["k16_source"] == "k07_how_need_risk"


def test_apply_omits_tips_when_selected_theme_has_no_k07_row() -> None:
    payload = {
        "profile_contract_v1": {
            "life_spheres": {"work": {"how": "act — career.", "need": "career"}}
        },
        "character_engine_consumption_v0": {"identity_thesis": "builds_through_autonomy"},
    }
    settings = SimpleNamespace(
        profile_deep_themes={"selected": ["sex"], "updated_at": "2026-01-01T00:00:00+00:00"}
    )
    out = apply_deep_themes_to_payload(
        payload,
        settings=settings,  # type: ignore[arg-type]
        billing_level="lite",
        access_allows_reveal=True,
        identity_thesis="builds_through_autonomy",
    )
    nest = out["character_engine_deep_themes_v0"]
    assert nest["selected"] == ["sex"]
    assert nest["tips_by_theme"] == {}
    assert nest["k16_source"] == "omitted_no_grounded_k07"


def test_free_omits_tips_body() -> None:
    payload = {
        "profile_contract_v1": {"life_spheres": {"money": dict(_K07_MONEY)}},
        "character_engine_consumption_v0": {"identity_thesis": "builds_through_autonomy"},
    }
    settings = SimpleNamespace(
        profile_deep_themes={"selected": ["money"], "updated_at": "2026-01-01T00:00:00+00:00"}
    )
    out = apply_deep_themes_to_payload(
        payload,
        settings=settings,  # type: ignore[arg-type]
        billing_level="free",
        access_allows_reveal=False,
        identity_thesis="builds_through_autonomy",
    )
    nest = out["character_engine_deep_themes_v0"]
    assert nest["gated"] is True
    assert nest["selected"] == []
    assert nest["tips_by_theme"] == {}
    assert nest["k16_source"] == "omitted_no_grounded_k07"


def test_k16_source_is_k07_derivation_not_thesis_or_stage_bank() -> None:
    from pathlib import Path

    text = Path(__file__).resolve().parents[1] / "src" / "todayflow_backend" / "services" / "profile_deep_themes_v0.py"
    src = text.read_text(encoding="utf-8")
    assert "derive_practical_tips_from_k07_sphere" in src
    assert "_GENERIC_TIPS" not in src
    assert "tips_for_theme" not in src
    assert "character_engine_stage4" not in src
    assert "character_engine_stage5" not in src
    assert "_essays_for" not in src
