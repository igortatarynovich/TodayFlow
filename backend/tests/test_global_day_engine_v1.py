"""Global Day Engine v1 — energy, drivers, windows. No natal/card/number."""

from todayflow_backend.services.global_day_engine_v1 import (
    ENERGY_SET,
    build_daily_actions_v1,
    build_global_day_profile_v1,
    build_personal_day_nest_v1,
    is_global_event,
    pick_primary_energy,
    score_energy,
)


def test_drops_natal_and_card_from_global_drivers():
    pack = {
        "events": [
            {
                "id": "moon-ingress-1",
                "kind": "moon_ingress",
                "fact_ru": "Луна вошла в Рыбы",
                "sign": "pisces",
                "strength": 0.8,
            },
            {
                "id": "pt-mars-natal",
                "kind": "personal_transit",
                "fact_ru": "Марс по наталу",
                "strength": 0.99,
            },
        ],
        "ranked_drivers": ["pt-mars-natal", "moon-ingress-1"],
    }
    profile = build_global_day_profile_v1(day_events_pack=pack)
    ids = [d["id"] for d in profile["drivers"]]
    assert "moon-ingress-1" in ids
    assert "pt-mars-natal" not in ids
    assert not is_global_event(pack["events"][1])


def test_primary_energy_closed_set_and_weak_day():
    assert pick_primary_energy({k: 0.0 for k in ENERGY_SET}) == "grounded"
    scores = {k: 0.1 for k in ENERGY_SET}
    scores["tension"] = 0.9
    scores["flow"] = 0.2
    assert pick_primary_energy(scores) == "tension"
    tied = {k: 0.4 for k in ENERGY_SET}
    assert pick_primary_energy(tied) == "clarity"


def test_hard_aspect_scores_tension():
    drivers = [
        {
            "id": "mars-sq",
            "kind": "sky_aspect",
            "aspect": "square",
            "body": "Mars",
            "strength": 0.8,
            "fact_ru": "Марс в квадрате",
        }
    ]
    scores = score_energy(drivers)
    assert scores["tension"] > scores["flow"]
    profile = build_global_day_profile_v1(
        day_events_pack={"events": drivers, "ranked_drivers": ["mars-sq"]}
    )
    assert profile["primary_energy"] in ENERGY_SET
    assert "hard_negotiation" in profile["risk"] or "sensitive_conversation" in profile["risk"]


def test_windows_from_shared_sky_exact_times_not_natal():
    ce = {
        "headline_sky": {
            "id": "headline-1",
            "kind": "sky_aspect",
            "exact_time": "2026-08-15T14:30:00",
            "body": "Sun",
            "aspect": "trine",
        },
        "timed_lunar_aspects": [
            {
                "id": "moon-mars",
                "kind": "lunar_aspect",
                "exact_time": "09:15",
                "body": "Moon",
                "aspect": "square",
            }
        ],
        "void_of_course": {"status": "ok", "starts_at": "18:40", "last_aspect_id": "voc-1"},
    }
    profile = build_global_day_profile_v1(celestial_events=ce)
    times = [w["time"] for w in profile["windows"]]
    assert "14:30" in times
    assert "09:15" in times
    assert "18:40" in times
    voc = next(w for w in profile["windows"] if w["time"] == "18:40")
    assert "rest" in voc["supports"]
    assert "hard_negotiation" in voc["cautions"]
    for w in profile["windows"]:
        assert "supports" in w and "cautions" in w


def test_personal_nest_strips_energy_and_omits_when_empty():
    assert build_personal_day_nest_v1({}) is None
    nest = build_personal_day_nest_v1(
        {
            "day_personal": {
                "activations": [{"id": "a1"}],
                "primary_energy": "tension",
                "windows": [{"time": "12:00"}],
            }
        }
    )
    assert nest is not None
    assert nest["mutates_global"] is False
    assert "primary_energy" not in nest["natal_overlay"]
    assert "windows" not in nest["natal_overlay"]
    assert nest["natal_overlay"]["activations"]


def test_daily_actions_typed_from_rec_and_primary_goals():
    actions = build_daily_actions_v1(
        {
            "practice_recommendation": {
                "kind": "affirmation",
                "text": "Дыши перед ответом",
                "origin_scene_id": "s1",
            },
            "day_scenario": {
                "primary_scene_id": "s1",
                "props": {
                    "goals": [
                        {"origin_scene_id": "s1", "text": "Написать одно письмо"},
                        {"origin_scene_id": "s2", "text": "Чужая сцена"},
                    ]
                },
            },
        }
    )
    kinds = {a["kind"] for a in actions}
    texts = {a["text"] for a in actions}
    assert "affirmation" in kinds
    assert "Написать одно письмо" in texts
    assert "Чужая сцена" not in texts
