"""Модульный профиль Guidance и мост Flow (без вызова OpenAI)."""

from todayflow_backend.services.guidance_flow_bridge import build_guidance_flow_bridge
from todayflow_backend.services.guidance_profile_modules import select_guidance_profile_modules


def test_select_modules_empty_profile():
    assert select_guidance_profile_modules(None, topic=None, lane="daily") == {"profile_ready": False}


def test_select_modules_keeps_lane_and_topic():
    core = {
        "is_ready": True,
        "baseline": {"archetype_seed": "строитель"},
        "interpretation": {"identity": "Коротко о личности."},
        "living": {"learning_context": {"summary": "Предпочитает ясность"}},
    }
    m = select_guidance_profile_modules(core, topic="work", lane="money_career", user_intent="choose_action")
    assert m["profile_ready"] is True
    assert m["lane"] == "money_career"
    assert m["topic"] == "work"
    assert "baseline_archetype" in m


def test_flow_bridge_decision_lane():
    b = build_guidance_flow_bridge(lane="decision", topic=None, locale="ru")
    assert "/questions/decision" in b["href"]
    assert "from_guidance=1" in b["href"]
    assert b["kind"] == "decision_os"


def test_flow_bridge_today_default():
    b = build_guidance_flow_bridge(lane="self", topic=None, locale="ru")
    assert b["href"].startswith("/today")
    assert "from_guidance=1" in b["href"]
