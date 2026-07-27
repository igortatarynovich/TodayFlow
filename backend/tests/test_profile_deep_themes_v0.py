"""Subscriber deep themes L3 — preference caps, change window, tips immutability."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from todayflow_backend.services.profile_deep_themes_v0 import (
    apply_deep_themes_to_payload,
    build_tips_by_theme,
    can_change_selection,
    theme_cap_for_billing,
    tips_for_theme,
)


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


def test_autonomy_tips_non_empty_for_sex_money() -> None:
    assert len(tips_for_theme("builds_through_autonomy", "sex")) >= 3
    assert len(tips_for_theme("builds_through_autonomy", "money")) >= 3
    pack = build_tips_by_theme("builds_through_autonomy", ["sex", "money"])
    assert "sex" in pack and "money" in pack


def test_apply_does_not_rewrite_life_spheres() -> None:
    spheres = {
        "money": {
            "how": "BASE HOW",
            "need": "n",
            "risk": "r",
            "turns_on": "on",
            "turns_off": "off",
            "helps": "h",
        }
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
    assert out["profile_contract_v1"]["life_spheres"]["money"]["how"] == "BASE HOW"
    nest = out["character_engine_deep_themes_v0"]
    assert nest["gated"] is False
    assert nest["selected"] == ["money"]
    assert nest["tips_by_theme"]["money"]["tips"]


def test_free_omits_tips_body() -> None:
    payload = {
        "profile_contract_v1": {"life_spheres": {}},
        "character_engine_consumption_v0": {"identity_thesis": "builds_through_autonomy"},
    }
    settings = SimpleNamespace(
        profile_deep_themes={"selected": ["sex"], "updated_at": "2026-01-01T00:00:00+00:00"}
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
