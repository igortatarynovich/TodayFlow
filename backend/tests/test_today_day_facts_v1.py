"""Wave 2 Phase D.1 / D.1b — day_facts assembler + narrative projection tests."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

from todayflow_backend.services import today_day_facts_project_v1 as project
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
    assert out["conflict"] is None
    assert out["scenes"] == []
    assert out["id"] == "7:2026-07-30"
    assert out["partial"] is True


def test_assemble_cache_miss_keeps_partial_no_invented_conflict():
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
                return_value=([], activations),
            ),
            patch(
                "todayflow_backend.services.day_lifecycle_clock_c5.resolve_user_timezone",
                return_value="Europe/Moscow",
            ),
            patch(
                "todayflow_backend.services.today_day_facts_project_v1.load_ready_day_scenario",
                return_value=None,
            ),
        ):
            return await day_facts.assemble_day_facts_v1(
                user=user,
                local_date=date(2026, 7, 30),
                db=MagicMock(),
                locale="ru",
            )

    out = asyncio.run(_run())
    assert out["partial"] is True
    assert out["conflict"] is None
    assert out["scenes"] == []
    assert out["generation_provenance"]["conflict_driver_ids"] == []
    assert len(out["domain_verdicts"]) == 4


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
            patch(
                "todayflow_backend.services.today_day_facts_project_v1.load_ready_day_scenario",
                return_value=None,
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
    soft_why = aspect_class_why_short("trine")
    assert any(r["why_short"] == soft_why for r in out["domain_verdicts"] if r.get("driver_ids"))


def _ready_scenario(*, driver_ids: list[str], thesis_label: str | None = "Тема дня"):
    thesis: dict | str | None
    if thesis_label is None:
        thesis = {"family": "momentum", "variant": "x", "mode": "y"}
    else:
        thesis = {"label_ru": thesis_label, "family": "momentum"}
    return {
        "ready": True,
        "runtime_sot": True,
        "conflict": {
            "short_name": "Спешка или пауза",
            "thesis": thesis,
            "opposing_forces": {"a": "спешка", "b": "пауза"},
            "why_arose": "Факты дня собирают одну линию.",
            "why_personal": "omit",
            "driver_ids": driver_ids,
        },
        "scenes": [
            {
                "scene_id": "scene.work",
                "sphere": "work_decisions",
                "role_in_story": "primary",
                "what_happens": "Решение просится раньше срока.",
                "opportunity": "Один спокойный шаг.",
                "trap": "Нажать send без паузы.",
                "recommended_action": "Подожди 10 минут.",
                "do_not": "Не обещай сразу.",
                "domestic_example": None,
                "evidence_references": driver_ids,
            },
            {
                "scene_id": "scene.rel",
                "sphere": "relationships",
                "role_in_story": "support_or_risk",
                "what_happens": "Тон сообщения важен.",
                "opportunity": "Мягче формулировка.",
                "trap": "Додумать за другого.",
                "recommended_action": "Уточни факт.",
                "do_not": "Не читай между строк.",
                "evidence_references": driver_ids[:1],
            },
        ],
        "props": {
            "color": {
                "name": "Лазурь",
                "link_to_conflict": "держит дистанцию",
                "where_to_use": "в переписке",
            },
            "avoid_color": {"name": "Алый", "amplifies_trap": "ускоряет ответ"},
            "goals": [
                {
                    "text": "Одна пауза перед send",
                    "window": "до 14:00",
                    "serves_conflict": "Спешка или пауза",
                }
            ],
            "affirmations": [{"text": "Я могу подождать", "compensates_trap": "send без паузы"}],
            "humor": {"text": "Не герой скорости", "serves_conflict": "Спешка или пауза"},
        },
        "foundation": {
            "day_number": {"personal_day": 7},
            "sky_drivers": [
                {
                    "planet": "Moon",
                    "sign": "Cancer",
                    "degree_in_sign": 12.5,
                    "retrograde": False,
                }
            ],
            "astronomy_facts": [
                {
                    "kind": "lunar_phase",
                    "label_ru": "Растущая луна",
                    "cycle_percent": 42.0,
                }
            ],
        },
    }


def test_project_thesis_null_without_label_ru():
    conflict = project.project_conflict(
        {
            "short_name": "A или B",
            "thesis": {"family": "momentum", "variant": "x"},
            "opposing_forces": {"a": "a", "b": "b"},
            "why_arose": "why",
            "driver_ids": ["a1"],
        }
    )
    assert conflict is not None
    assert conflict["thesis"] is None


def test_project_scene_id_and_role_aliases():
    rows = project.project_scenes(
        [
            {
                "scene_id": "scene.work",
                "sphere": "work",
                "role_in_story": "support_or_risk",
                "what_happens": "x",
                "opportunity": "y",
                "trap": "z",
                "recommended_action": "do",
                "do_not": "dont",
                "evidence_references": ["a1"],
            }
        ]
    )
    assert rows[0]["id"] == "scene.work"
    assert rows[0]["role_in_story"] == "caution"
    assert rows[0]["driver_ids"] == ["a1"]


def test_assemble_projects_narrative_when_drivers_in_pool():
    user = MagicMock()
    user.id = 2
    activations = [
        {"id": "a1", "rank": 1, "transiting_planet": "Venus", "aspect": "trine", "natal_point": "Moon", "orb_deg": 1.0},
        {"id": "a2", "rank": 2, "transiting_planet": "Mars", "aspect": "square", "natal_point": "Sun", "orb_deg": 0.5},
    ]
    scenario = _ready_scenario(driver_ids=["a1", "a2"])

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
                return_value=([], activations),
            ),
            patch(
                "todayflow_backend.services.day_lifecycle_clock_c5.resolve_user_timezone",
                return_value="Europe/Moscow",
            ),
            patch(
                "todayflow_backend.services.today_day_facts_project_v1.load_ready_day_scenario",
                return_value=scenario,
            ),
        ):
            return await day_facts.assemble_day_facts_v1(
                user=user,
                local_date=date(2026, 7, 30),
                db=MagicMock(),
                locale="ru",
            )

    out = asyncio.run(_run())
    assert out["partial"] is False
    assert out["conflict"]["short_name"] == "Спешка или пауза"
    assert out["conflict"]["thesis"] == "Тема дня"
    assert out["scenes"][0]["id"] == "scene.work"
    assert out["scenes"][1]["role_in_story"] == "caution"
    assert out["props"]["evening_payoff"] is None
    assert out["props"]["practice_or_promise"]["text"] == "Одна пауза перед send"
    assert out["numerology"] == {"personal_day": 7, "source": "classic_reduce_v0"}
    assert out["sky_drivers"][0]["planet"] == "Moon"
    assert out["moon_phase"] is not None
    assert out["moon_phase"]["phase"] == "waxing"
    assert out["moon_phase"]["illumination_pct"] == 42.0
    act_ids = {a["id"] for a in out["natal_activations"]}
    assert set(out["generation_provenance"]["conflict_driver_ids"]) <= act_ids
    assert set(out["conflict"]["driver_ids"]) <= act_ids
    assert len(out["domain_verdicts"]) == 4


def test_event_pack_conflict_drivers_gate_when_pool_live():
    """Runtime day_scenario uses sky-/phase- ids; gate requires non-empty natal pool."""
    assert project.narrative_drivers_in_pool(
        ["sky-semisquare-0", "phase-full-2026-07-30"],
        [{"id": "pt-venus-trine-moon"}],
    )
    assert not project.narrative_drivers_in_pool(
        ["sky-semisquare-0"],
        [],
    )


def test_assemble_omits_stale_narrative_keeps_fresh_strip():
    """Temporal honesty: stale conflict drivers → no narrative; strip still from fresh pool."""
    user = MagicMock()
    user.id = 2
    activations = [
        {"id": "a1", "rank": 1, "transiting_planet": "Venus", "aspect": "trine", "natal_point": "Moon", "orb_deg": 1.0},
        {"id": "a2", "rank": 2, "transiting_planet": "Mars", "aspect": "square", "natal_point": "Sun", "orb_deg": 0.5},
    ]
    # Scenario still talks about drivers that left the pool (not event-pack prefixes)
    scenario = _ready_scenario(driver_ids=["gone-a", "gone-b"])

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
                return_value=([], activations),
            ),
            patch(
                "todayflow_backend.services.day_lifecycle_clock_c5.resolve_user_timezone",
                return_value="Europe/Moscow",
            ),
            patch(
                "todayflow_backend.services.today_day_facts_project_v1.load_ready_day_scenario",
                return_value=scenario,
            ),
        ):
            return await day_facts.assemble_day_facts_v1(
                user=user,
                local_date=date(2026, 7, 30),
                db=MagicMock(),
                locale="ru",
            )

    out = asyncio.run(_run())
    assert out["partial"] is True
    assert out["conflict"] is None
    assert out["scenes"] == []
    assert out["props"] is None
    assert out["generation_provenance"]["conflict_driver_ids"] == []
    assert len(out["domain_verdicts"]) == 4
    assert {a["id"] for a in out["natal_activations"]} == {"a1", "a2"}
