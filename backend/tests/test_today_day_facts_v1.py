"""Wave 2 Phase D.1 — day_facts assembler unit tests."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from todayflow_backend.services import today_day_facts_v1 as day_facts
from todayflow_backend.services.today_activation_copy_v1 import aspect_class_why_short


def test_assemble_degraded_when_activations_degraded():
    user = MagicMock()
    user.id = 7

    async def _run():
        with (
            patch(
                "todayflow_backend.services.personal_transits.get_personal_transit_service",
                new_callable=AsyncMock,
            ),
            patch("todayflow_backend.api.reports._get_user_astro_profile", new_callable=AsyncMock),
            patch("todayflow_backend.api.reports._prepare_birth_data", new_callable=AsyncMock),
            patch("todayflow_backend.api.reports._compute_natal_chart", new_callable=AsyncMock),
            patch(
                "todayflow_backend.services.today_natal_activations_v1.resolve_natal_activations",
                new_callable=AsyncMock,
                return_value=([], True),
            ),
            patch(
                "todayflow_backend.services.day_lifecycle_clock_c5.resolve_user_timezone",
                return_value="Europe/Moscow",
            ),
        ):
            return await day_facts.assemble_day_facts_v1(
                user=user,
                local_date=date(2026, 7, 30),
                db=MagicMock(),
                locale="ru",
            )

    out = asyncio.run(_run())
    assert out["is_fallback"] is True
    assert out["degraded"] is True
    assert out["domain_verdicts"] == []
    assert out["glance_timeline"] == []
    assert out["id"] == "7:2026-07-30"
    assert out["partial"] is True


def test_assemble_happy_path_provenance_subset():
    user = MagicMock()
    user.id = 2
    activations = [
        {
            "id": "a1",
            "rank": 1,
            "transiting_planet": "Venus",
            "aspect": "trine",
            "natal_point": "Moon",
            "orb_deg": 1.0,
            "exact_time_local": None,
        },
        {
            "id": "a2",
            "rank": 2,
            "transiting_planet": "Mars",
            "aspect": "square",
            "natal_point": "Sun",
            "orb_deg": 0.5,
            "exact_time_local": None,
        },
    ]
    glance_rows = [
        {
            "time_local": "2026-07-30T14:00+03:00",
            "label_short": "Есть опора",
            "valence": "favorable",
            "driver_id": "a1",
        }
    ]

    async def _run():
        with (
            patch(
                "todayflow_backend.services.personal_transits.get_personal_transit_service",
                new_callable=AsyncMock,
                return_value=MagicMock(),
            ),
            patch(
                "todayflow_backend.api.reports._get_user_astro_profile",
                new_callable=AsyncMock,
                return_value=MagicMock(),
            ),
            patch(
                "todayflow_backend.api.reports._prepare_birth_data",
                new_callable=AsyncMock,
                return_value=MagicMock(coordinates=None),
            ),
            patch(
                "todayflow_backend.api.reports._compute_natal_chart",
                new_callable=AsyncMock,
                return_value=MagicMock(positions=[{"body": "Sun"}]),
            ),
            patch(
                "todayflow_backend.services.today_natal_activations_v1.resolve_natal_activations",
                new_callable=AsyncMock,
                return_value=(activations, False),
            ),
            patch(
                "todayflow_backend.services.today_glance_timeline_v1.compute_glance_timeline",
                new_callable=AsyncMock,
                return_value=(glance_rows, activations),
            ),
            patch(
                "todayflow_backend.services.day_lifecycle_clock_c5.resolve_user_timezone",
                return_value="Europe/Moscow",
            ),
        ):
            return await day_facts.assemble_day_facts_v1(
                user=user,
                local_date=date(2026, 7, 30),
                db=MagicMock(),
                locale="ru",
            )

    out = asyncio.run(_run())
    assert out["is_fallback"] is False
    assert len(out["domain_verdicts"]) == 4
    act_ids = {a["id"] for a in out["natal_activations"]}
    for row in out["domain_verdicts"]:
        for did in row["driver_ids"]:
            assert did in act_ids
        assert "трин" not in row["why_short"].lower()
        assert "Венера" not in row["why_short"]
    timeline_ids = out["generation_provenance"]["timeline_driver_ids"]
    assert timeline_ids == ["a1"]
    assert set(timeline_ids) <= act_ids
    assert out["glance_timeline"][0]["label_short"] == "Есть опора"
    soft_why = aspect_class_why_short("trine")
    assert any(r["why_short"] == soft_why for r in out["domain_verdicts"] if r.get("driver_ids"))
