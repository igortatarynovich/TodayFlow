from __future__ import annotations

from datetime import date

import pytest

from todayflow_backend.db import models as db_models
from todayflow_backend.services import today_narrative as today_narrative_service
from todayflow_backend.services.generation_orchestrator import (
    MERGE_PASS_CONTRACT,
    ORCHESTRATOR_VERSION,
    PIPELINE_TODAY_NARRATIVE,
)
from todayflow_backend.services.today_narrative import (
    MODULE,
    NARRATIVE_HIERARCHY_CONTRACT_V0,
    _DAY_LAYER_NUDGE_MAX,
    _clamp_narrative_depth_for_insight_tier,
    _dedupe_guide_payload_cross_fields,
    _fallback_day_layer,
    _finalize_day_layer_payload_o8,
    _fusion_slim_for_prompt,
    _guide_payload_concrete,
    _load_narrative_cache,
    _ru_narrative_quality_reject,
    _system_prompt_for_surface,
    _texts_semantically_redundant,
    _validate_payload_shape,
    build_today_narrative,
)


def test_system_prompt_includes_low_energy_ritual_addon_ru():
    """O6: усталые ritual moods добавляют в system prompt ветку «короче и мягче»."""
    p = _system_prompt_for_surface("guide", "ru", ritual_norm={"mood": "tired"})
    assert "РЕЖИМ_НИЗКИЙ_РЕСУРС" in p


def test_system_prompt_includes_low_energy_ritual_addon_en():
    p = _system_prompt_for_surface("guide", "en", ritual_norm={"mood": "heavy"})
    assert "LOW_RESOURCE_MOOD" in p


def test_system_prompt_skips_low_energy_addon_for_high_energy_mood():
    p = _system_prompt_for_surface("guide", "ru", ritual_norm={"mood": "motivated"})
    assert "РЕЖИМ_НИЗКИЙ_РЕСУРС" not in p


def test_o8_finalize_day_layer_truncates_long_strings():
    """O8: day_layer строки не разрастаются в «простыню»."""
    p = _fallback_day_layer("enc", [], "ru")
    p["nudge_message"] = "слово " * 120
    p["personal_insight_body"] = "абзац. " * 200
    out = _finalize_day_layer_payload_o8(dict(p), day_engine_brief=None)
    assert len(out["nudge_message"]) <= _DAY_LAYER_NUDGE_MAX + 2
    assert len(out["personal_insight_body"]) <= 522


def test_o8_finalize_day_layer_strips_verbatim_anchor_lead():
    anchor = "Сегодня держи одну линию и не распыляйся по срочному."
    p = _fallback_day_layer("x", [], "ru")
    p["personal_insight_body"] = anchor + " Добавь паузу перед ответом коллеге."
    out = _finalize_day_layer_payload_o8(dict(p), day_engine_brief={"anchor_summary": anchor})
    assert "паузу" in out["personal_insight_body"].lower()
    assert not out["personal_insight_body"].strip().lower().startswith(anchor.lower())


def test_o10_finalize_day_layer_strips_llm_meta_sentences():
    """O10: мета-про формат ответа не попадает в короткую сводку day_layer."""
    p = _fallback_day_layer("x", [], "ru")
    p["nudge_message"] = (
        "День про ясность. Уже было в предыдущем блоке про карту — не повторяю блок. "
        "Один короткий шаг до обеда."
    )
    out = _finalize_day_layer_payload_o8(dict(p), day_engine_brief=None)
    assert "предыдущем блоке" not in out["nudge_message"].lower()
    assert "не повторяю блок" not in out["nudge_message"].lower()
    assert "шаг" in out["nudge_message"].lower()


def test_fusion_slim_for_prompt_trims_heavy_fusion_keys():
    slim = _fusion_slim_for_prompt(
        {
            "scores": {"energy": 44, "emotional_balance": 55, "focus": 66},
            "encouragement": "steady",
            "recommendations": ["one", "two"],
            "rhythm_context": {
                "goals": [],
                "habits": [{"name": "walk", "category": None, "frequency": "daily", "completed_today": False}],
                "ascetics": [],
                "diary": {"has_entry_today": False, "entries_last_7_days": 1},
            },
            "cycle_context": {"tracked": True},
            "activity_context": {"diary_done": True},
        }
    )
    assert slim["scores"]["energy"] == 44
    assert slim["encouragement"] == "steady"
    assert slim["recommendations"] == ["one", "two"]
    assert slim["rhythm_context"]["habits"][0]["name"] == "walk"
    assert "cycle_context" not in slim
    assert "activity_context" not in slim


def test_fusion_slim_for_prompt_keeps_flow_closure_flags():
    slim = _fusion_slim_for_prompt(
        {
            "scores": {"energy": 50},
            "encouragement": "x",
            "recommendations": [],
            "rhythm_context": {},
            "activity_context": {
                "practice_count": 9,
                "morning_completed": True,
                "day_completed": False,
                "evening_completed": True,
                "guide_action_options_selected_today": 2,
            },
        }
    )
    assert slim["activity_context"] == {
        "morning_completed": True,
        "day_completed": False,
        "evening_completed": True,
        "guide_action_options_selected_today": 2,
    }


def test_fusion_slim_clamps_guide_meaning_completions_today():
    slim = _fusion_slim_for_prompt(
        {
            "scores": {"energy": 50},
            "encouragement": "x",
            "recommendations": [],
            "rhythm_context": {},
            "activity_context": {
                "guide_meaning_completions_today": {
                    "habit_completed": 3,
                    "practice_completed": 99,
                    "focus_completed": "x",
                    "affirmation_done": -1,
                    "ascetic_step_done": 0,
                },
            },
        }
    )
    gmc = slim["activity_context"]["guide_meaning_completions_today"]
    assert gmc["habit_completed"] == 3
    assert gmc["practice_completed"] == 50
    assert gmc["focus_completed"] == 0
    assert gmc["affirmation_done"] == 0
    assert gmc["ascetic_step_done"] == 0


def test_today_narrative_logs_policy_and_voice_profile(db_session, monkeypatch):
    # Avoid external API calls in tests.
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_args, **_kwargs: None)
    # Ensure required tables exist for environments where metadata may be partial.
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-contract@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    payload, generation_id, used_fallback, profile_sel = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 4, 25),
        locale="ru",
        surface="guide",
        core_profile={},
        fusion_dump={"scores": {"energy": 50, "focus": 50, "emotional_balance": 50}, "encouragement": "ok"},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )

    assert isinstance(payload, dict)
    assert generation_id > 0
    assert isinstance(used_fallback, bool)
    deb = payload.get("day_engine_brief")
    assert isinstance(deb, dict)
    assert deb.get("contract_version") == "day_narrative_brief_v0"
    assert isinstance(deb.get("anchor_summary"), str) and deb["anchor_summary"].strip()
    nh = payload.get("narrative_hierarchy")
    assert isinstance(nh, dict)
    assert nh.get("contract_version") == NARRATIVE_HIERARCHY_CONTRACT_V0
    assert nh.get("primary_anchor") == "day_engine_brief"
    assert payload.get("contract_version") == "guide_contract_v2"
    gp = payload.get("guide_pipeline")
    assert isinstance(gp, dict) and gp.get("contract_version") == "guide_pipeline_v0"
    dm = payload.get("day_model")
    assert isinstance(dm, dict) and dm.get("contract_version") == "day_model_v0"

    log = db_session.query(db_models.GenerationLog).filter(db_models.GenerationLog.id == generation_id).first()
    assert log is not None
    assert isinstance(log.input_payload, dict)
    assert log.input_payload.get("day_engine_brief_contract") == "day_narrative_brief_v0"
    assert log.input_payload.get("day_model_contract") == "day_model_v0"
    assert log.input_payload.get("policy_version") == "clean-info-v1"
    assert log.input_payload.get("voice_profile") == "live-clean-supportive-v1"
    assert log.input_payload.get("locale") == "ru"
    assert log.input_payload.get("depth_level") == "normal"
    assert log.input_payload.get("day_context_contract_version") == "day_context_v0"
    h = log.input_payload.get("day_context_sha256")
    assert isinstance(h, str) and len(h) == 64
    assert log.input_payload.get("prompt_label") == today_narrative_service.PROMPT_VER
    ip_ps = log.input_payload.get("profile_selector")
    assert profile_sel == (ip_ps if isinstance(ip_ps, dict) else None)
    orch = log.input_payload.get("orchestration")
    assert isinstance(orch, dict)
    assert orch.get("orchestrator_version") == ORCHESTRATOR_VERSION
    assert orch.get("pipeline") == PIPELINE_TODAY_NARRATIVE
    assert "day_context_v0" in orch.get("stages", [])
    assert "merge_pass_documented" in orch.get("stages", [])
    assert orch.get("merge_pass_contract") == MERGE_PASS_CONTRACT
    assert isinstance(orch.get("merge_pass_steps"), list)
    assert "ensure_guide_actionable_fields" in orch.get("merge_pass_steps", [])
    assert orch.get("primary_narrative_anchor") == "day_engine_brief"
    assert orch.get("canon_ref") == "docs/SOURCE_OF_TRUTH_PIPELINE.md"
    rt = orch.get("reasoning_trace")
    assert isinstance(rt, dict)
    assert "selector_resolution" in rt
    assert rt["selector_resolution"].get("task") in (
        "today_summary",
        "guidance_question",
        "today_spheres",
        "evening_reflection",
    )
    sdbg = rt.get("selector_debug")
    assert isinstance(sdbg, dict)
    assert sdbg.get("resolved_task") == rt["selector_resolution"].get("task")


def test_today_narrative_en_locale_uses_en_fallback(db_session, monkeypatch):
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_args, **_kwargs: None)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-en@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    payload, generation_id, _, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 4, 25),
        locale="en-US",
        surface="guide",
        core_profile={},
        fusion_dump={"scores": {"energy": 50, "focus": 50, "emotional_balance": 50}, "encouragement": "ok"},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )

    assert generation_id > 0
    assert isinstance(payload, dict)
    assert "headline" in payload
    hl = str(payload.get("headline", "")).strip()
    assert len(hl) >= 12
    assert any(c.isascii() and c.isalpha() for c in hl)
    deb = payload.get("day_engine_brief")
    assert isinstance(deb, dict) and deb.get("contract_version") == "day_narrative_brief_v0"

    log = db_session.query(db_models.GenerationLog).filter(db_models.GenerationLog.id == generation_id).first()
    assert log is not None
    assert isinstance(log.input_payload, dict)
    assert log.input_payload.get("locale") == "en"


@pytest.mark.parametrize(
    "surface",
    ["day_layer", "spheres", "evening", "deepen"],
)
def test_today_narrative_non_guide_user_json_includes_day_logic_layers(db_session, monkeypatch, surface: str):
    captured: dict[str, str] = {}

    def capture_openai(system: str, user: str, **_kwargs) -> dict | None:
        captured["user"] = user
        return None

    monkeypatch.setattr(today_narrative_service, "_openai_json", capture_openai)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email=f"narrative-{surface}-dm@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    fusion = {
        "scores": {"energy": 50, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }
    build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 4, 27),
        locale="ru",
        surface=surface,  # type: ignore[arg-type]
        core_profile={},
        fusion_dump=fusion,
        parent_generation_id=None,
        deepen_topic="full_day" if surface == "deepen" else None,
    )

    u = captured.get("user", "")
    assert "day_model" in u
    assert "day_model_v0" in u
    assert "day_engine_brief" in u


_RU_GUIDE_LLM_FIXTURE: dict = {
    "headline": "Ось дня из гороскопа — один завершённый шаг без лишнего героизма.",
    "subline": "Карта и число задают акцент; ритм из профиля не спорит с этим.",
    "energy_line": "Ресурса хватает на один качественный блок внимания.",
    "focus_line": "Выбери один шаг и доведи его до конца.",
    "risk_line": "Распыление",
    "risk_detail": "Если потянуться за всем сразу, к вечеру будет ощущение «ничего не закрыто».",
    "do_items": ["Один шаг по приоритету", "Короткая фиксация", "Пауза перед ответом"],
    "avoid_items": ["Новые обещания без времени", "Реакция на срочное", "Дожим ясности силой"],
    "header_disclaimer": "Экран только про твой день по данным профиля.",
    "context_for_next_surfaces": "Тезис дня: один приоритет и спокойный темп без лишних импульсов.",
    "pattern_insight": "",
    "life_context_insight": "",
    "core_message": {
        "headline": "Смысл дня",
        "body": "Сегодня легко уйти в срочное и потерять нить главного. Лучше выбрать одну задачу и довести её.",
        "risk": "Перегруз ответами «да» всем подряд.",
        "best_move": "Один завершённый шаг даст больше спокойствия, чем десять начатых.",
    },
    "action_options": [
        {"title": "Закрыть одну рабочую задачу", "reason": "даст ощущение контроля", "estimated_minutes": 20},
        {"title": "Поговорить с близким человеком", "reason": "снимет недосказанность"},
        "Навести порядок на столе за десять минут",
    ],
    "sphere_triad": [
        {"area": "work", "stance": "up", "line": "Работа — лучшее место для движения: завершение одной линии."},
        {"area": "love", "stance": "down", "line": "Отношения — не дави ответом сразу, лучше сказать прямо."},
        {"area": "money", "stance": "neutral", "line": "Деньги — нейтрально: цифры и границы без импульса."},
    ],
    "support_hooks": ["Поставь одну цель на сегодня в Flow.", "Или короткая практика три минуты."],
}


def test_guide_narrative_cache_hit_when_day_context_unchanged(db_session, monkeypatch):
    """При неизменном DayContext (в т.ч. fusion) guide берётся из кэша — один вызов LLM."""
    calls = {"n": 0}

    def capture_openai(_system: str, _user: str, **_kwargs) -> dict:
        calls["n"] += 1
        return dict(_RU_GUIDE_LLM_FIXTURE)

    # Воронка guide вызывает отдельный LLM-путь; эти тесты мокают только монолитный _openai_json.
    monkeypatch.setattr(today_narrative_service, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(today_narrative_service, "_openai_json", capture_openai)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-guide-cache-same@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 5, 12)
    base_kw = dict(
        user_id=user.id,
        insight_depth_tier="free",
        target_date=target,
        locale="ru",
        surface="guide",
        core_profile={},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )
    fusion = {
        "scores": {"energy": 58, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }

    p1, gid1, fb1, ps1 = build_today_narrative(db_session, **base_kw, fusion_dump=fusion)
    assert calls["n"] == 1
    assert fb1 is False
    p2, gid2, fb2, ps2 = build_today_narrative(db_session, **base_kw, fusion_dump=fusion)
    assert calls["n"] == 1
    assert gid2 == gid1
    assert fb2 is False
    assert p2.get("headline") == p1.get("headline")
    assert ps2.get("amll_gate", {}).get("gate_decision") == "cache_hit"
    assert {k: v for k, v in ps1.items() if k != "amll_gate"} == {
        k: v for k, v in ps2.items() if k != "amll_gate"
    }


def test_guide_narrative_reuses_same_day_when_only_fusion_changes(db_session, monkeypatch):
    """Same-day reuse: fusion scores drift intra-day from the user's own tracked
    activity, so a fusion-only change (same date/ritual/intent/tier/depth/profile)
    must REUSE the already-generated guide instead of re-calling the LLM. Otherwise
    the narrative regenerates on every visit. Deterministic layers (day_model /
    guide_decision) are still refreshed from current fusion on the cache-hit path."""
    calls = {"n": 0}

    def capture_openai(_system: str, _user: str, **_kwargs) -> dict:
        calls["n"] += 1
        return dict(_RU_GUIDE_LLM_FIXTURE)

    monkeypatch.setattr(today_narrative_service, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(today_narrative_service, "_openai_json", capture_openai)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-guide-cache-fusion@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 5, 13)
    base_kw = dict(
        user_id=user.id,
        insight_depth_tier="free",
        target_date=target,
        locale="ru",
        surface="guide",
        core_profile={},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )
    fusion_hi = {
        "scores": {"energy": 58, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }
    fusion_lo = {
        "scores": {"energy": 22, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }

    _, gid1, _, _ = build_today_narrative(db_session, **base_kw, fusion_dump=fusion_hi)
    _, gid2, _, ps2 = build_today_narrative(db_session, **base_kw, fusion_dump=fusion_lo)
    assert calls["n"] == 1
    assert gid2 == gid1
    gate = ps2.get("amll_gate", {})
    assert gate.get("gate_decision") == "cache_hit"
    assert gate.get("reason") == "GATE:cache_hit:same_day_reuse"


def _narrative_cache_input(*, sha: str, target: date, surface: str = "guide") -> dict:
    return {
        "target_date": target.isoformat(),
        "surface": surface,
        "parent_generation_id": -1,
        "deepen_topic": "",
        "insight_depth_tier": "free",
        "locale": "ru",
        "ritual_context_fp": "ritual-fp-1",
        "intent_context_fp": "intent-fp-1",
        "depth_level": "normal",
        "day_context_sha256": sha,
        "prompt_label": today_narrative_service.PROMPT_VER,
    }


def _add_narrative_log(db_session, *, user_id: int, sha: str, target: date):
    log = db_models.GenerationLog(
        user_id=user_id,
        module=MODULE,
        surface="guide",
        status="success",
        model="test",
        normalized_response={"headline": "reused"},
        input_payload=_narrative_cache_input(sha=sha, target=target),
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log


def test_load_narrative_cache_reuses_on_sha_drift(db_session):
    """Same-day reuse: intra-day fusion/history drift changes day_context_sha256,
    but the guide narrative must be reused (stable key unchanged) instead of
    regenerating — this is the core fix for 'Сегодня собирается бесконечно'."""
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    user = db_models.User(email="narr-cache-reuse@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 6, 1)
    log = _add_narrative_log(db_session, user_id=user.id, sha="sha-first-visit", target=target)

    hit = _load_narrative_cache(
        db_session,
        user.id,
        target,
        "guide",
        None,
        None,
        None,
        "free",
        "ru",
        ritual_context_fp="ritual-fp-1",
        intent_context_fp="intent-fp-1",
        day_context_sha256="sha-second-visit-drifted",
        depth_level="normal",
        prompt_label=today_narrative_service.PROMPT_VER,
    )
    assert hit is not None
    assert hit.id == log.id


def test_load_narrative_cache_prefers_exact_sha_match(db_session):
    """When an exact context hash exists it is preferred (freshest) over a drifted row."""
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    user = db_models.User(email="narr-cache-exact@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 6, 2)
    _add_narrative_log(db_session, user_id=user.id, sha="sha-drifted-newer", target=target)
    exact = _add_narrative_log(db_session, user_id=user.id, sha="sha-exact", target=target)

    hit = _load_narrative_cache(
        db_session,
        user.id,
        target,
        "guide",
        None,
        None,
        None,
        "free",
        "ru",
        ritual_context_fp="ritual-fp-1",
        intent_context_fp="intent-fp-1",
        day_context_sha256="sha-exact",
        depth_level="normal",
        prompt_label=today_narrative_service.PROMPT_VER,
    )
    assert hit is not None
    assert hit.id == exact.id


def test_load_narrative_cache_miss_on_ritual_change(db_session):
    """A change in the stable key (ritual_fp) still misses — meaningful inputs
    correctly trigger regeneration, unlike volatile fusion/history drift."""
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    user = db_models.User(email="narr-cache-ritual@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 6, 3)
    _add_narrative_log(db_session, user_id=user.id, sha="sha-x", target=target)

    miss = _load_narrative_cache(
        db_session,
        user.id,
        target,
        "guide",
        None,
        None,
        None,
        "free",
        "ru",
        ritual_context_fp="ritual-fp-CHANGED",
        intent_context_fp="intent-fp-1",
        day_context_sha256="sha-x",
        depth_level="normal",
        prompt_label=today_narrative_service.PROMPT_VER,
    )
    assert miss is None


def test_clamp_narrative_depth_free_tier_deep_to_normal():
    assert _clamp_narrative_depth_for_insight_tier("deep", "free") == "normal"
    assert _clamp_narrative_depth_for_insight_tier("deep", "pro") == "deep"
    assert _clamp_narrative_depth_for_insight_tier("quick", "free") == "quick"


def test_free_tier_narrative_log_stores_clamped_depth_not_deep(db_session, monkeypatch):
    """DE-8: при insight_depth_tier=free запрошенный deep в логе — normal (кэш и DayContext согласованы)."""
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_args, **_kwargs: None)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-depth-clamp@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    fusion = {
        "scores": {"energy": 50, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }
    _, generation_id, _, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 5, 20),
        locale="ru",
        surface="day_layer",
        core_profile={},
        fusion_dump=fusion,
        parent_generation_id=None,
        deepen_topic=None,
        depth_level="deep",
    )
    log = db_session.query(db_models.GenerationLog).filter(db_models.GenerationLog.id == generation_id).first()
    assert log is not None
    assert log.input_payload.get("depth_level") == "normal"


def test_guide_narrative_cache_miss_when_depth_level_changes(db_session, monkeypatch):
    """Смена depth_level не должна попадать в кэш ответа с другим режимом."""
    calls = {"n": 0}

    def capture_openai(_system: str, _user: str, **_kwargs) -> dict:
        calls["n"] += 1
        return dict(_RU_GUIDE_LLM_FIXTURE)

    monkeypatch.setattr(today_narrative_service, "is_llm_chat_configured", lambda: True)
    monkeypatch.setattr(today_narrative_service, "_openai_json", capture_openai)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-guide-cache-depth@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    target = date(2026, 5, 14)
    base_kw = dict(
        user_id=user.id,
        # premium: иначе free-кламп DE-8 сводит deep → normal и кэш совпадает с normal.
        insight_depth_tier="premium",
        target_date=target,
        locale="ru",
        surface="guide",
        core_profile={},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )
    fusion = {
        "scores": {"energy": 50, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }

    _, gid1, _, _ = build_today_narrative(db_session, **base_kw, fusion_dump=fusion, depth_level="normal")
    _, gid2, _, _ = build_today_narrative(db_session, **base_kw, fusion_dump=fusion, depth_level="deep")
    assert calls["n"] == 2
    assert gid2 != gid1


def test_today_narrative_day_layer_logs_day_context_hash(db_session, monkeypatch):
    monkeypatch.setattr(today_narrative_service, "_openai_json", lambda *_args, **_kwargs: None)
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-daylayer@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    fusion = {
        "scores": {"energy": 50, "focus": 50, "emotional_balance": 50},
        "encouragement": "ok",
    }
    dl_payload, generation_id, _, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 4, 26),
        locale="ru",
        surface="day_layer",
        core_profile={},
        fusion_dump=fusion,
        parent_generation_id=None,
        deepen_topic=None,
    )
    assert "narrative_hierarchy" not in dl_payload

    log = db_session.query(db_models.GenerationLog).filter(db_models.GenerationLog.id == generation_id).first()
    assert log is not None
    assert log.input_payload.get("surface") == "day_layer"
    assert log.input_payload.get("day_context_contract_version") == "day_context_v0"
    assert log.input_payload.get("day_model_contract") == "day_model_v0"
    assert isinstance(log.input_payload.get("day_context_sha256"), str) and len(log.input_payload["day_context_sha256"]) == 64


def test_today_narrative_rejects_wrong_language_and_falls_back(db_session, monkeypatch):
    # Force model-like response with wrong language for requested locale.
    monkeypatch.setattr(today_narrative_service, "is_llm_chat_configured", lambda: False)
    monkeypatch.setattr(
        today_narrative_service,
        "_openai_json",
        lambda *_args, **_kwargs: {
            "headline": "English only headline",
            "subline": "English only subline",
            "energy_line": "Energy line",
            "focus_line": "Focus line",
            "risk_line": "Risk",
            "risk_detail": "Risk detail",
            "do_items": ["Do one thing", "Keep calm", "Write note"],
            "avoid_items": ["Don't rush", "Don't overload", "Don't react"],
            "header_disclaimer": "Personal only",
            "context_for_next_surfaces": "Context",
            "pattern_insight": "",
            "life_context_insight": "",
            "core_message": "First paragraph in English only.\n\nSecond paragraph stays English.",
            "action_options": ["Close one clear task today.", "Take a ten minute walk outside.", "Write one line in the journal."],
            "sphere_triad": [
                {"area": "work", "stance": "up", "line": "Work is the best place to finish one line today."},
                {"area": "love", "stance": "down", "line": "Love needs calm tone and one honest sentence today."},
                {"area": "money", "stance": "neutral", "line": "Money stays neutral: check numbers before any move."},
            ],
            "support_hooks": ["Set one goal for today in Flow.", "Or a five minute practice to reset."],
        },
    )
    db_models.PromptVersion.__table__.create(bind=db_session.get_bind(), checkfirst=True)
    db_models.GenerationLog.__table__.create(bind=db_session.get_bind(), checkfirst=True)

    user = db_models.User(email="narrative-ru-fallback@example.com", password_hash="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    payload, generation_id, used_fallback, _ = build_today_narrative(
        db_session,
        user_id=user.id,
        insight_depth_tier="free",
        target_date=date(2026, 4, 25),
        locale="ru-RU",
        surface="guide",
        core_profile={},
        fusion_dump={"scores": {"energy": 50, "focus": 50, "emotional_balance": 50}, "encouragement": "ok"},
        parent_generation_id=None,
        deepen_topic=None,
        policy_version="clean-info-v1",
        voice_profile="live-clean-supportive-v1",
    )

    assert generation_id > 0
    assert used_fallback is True
    assert isinstance(payload, dict)
    assert "Сегодня" in str(payload.get("headline", "")) or "Ресурс" in str(payload.get("energy_line", ""))


def test_guide_payload_shape_accepts_structured_core_message_and_action_objects():
    """Паритет веб/iOS: объектный core_message и action_options — см. DAY_ENGINE_AND_COHERENCE.md §9."""
    payload = dict(_RU_GUIDE_LLM_FIXTURE)
    assert _validate_payload_shape("guide", payload) is True
    assert _guide_payload_concrete("ru", payload) is True


def test_ru_narrative_quality_rejects_template_phrases():
    assert _ru_narrative_quality_reject(["Смысл и коммуникация — главное"]) is True
    assert _ru_narrative_quality_reject(["не заходить в линию general сегодня"]) is True
    assert _ru_narrative_quality_reject(["Сегодня держим одну линию", "Конкретный шаг по работе"]) is False


def test_o4_guide_payload_links_ritual_context_when_present():
    """O4: при непустом ritual_norm видимый текст содержит якорь ритуала."""
    p = dict(_RU_GUIDE_LLM_FIXTURE)
    assert _guide_payload_concrete("ru", p, ritual_norm={"head_topic": "гороскоп"}) is True
    assert _guide_payload_concrete("ru", p, ritual_norm={"head_topic": "кванты", "numerology_value": "9"}) is False


def test_guide_payload_concrete_rejects_headline_duplicated_in_do():
    payload = {
        "headline": "Один и тот же текст",
        "subline": "Подстрочник достаточной длины для теста валидации.",
        "energy_line": "Ресурс дня около 50/100: при необходимости снижай темп.",
        "focus_line": "Внимание и ясность — около 50/100: один блок.",
        "risk_line": "Риск",
        "risk_detail": "Детали риска в двух предложениях для прохождения валидации.",
        "do_items": ["Один и тот же текст", "Второй нормальный шаг по делу", "Третий нормальный шаг дня"],
        "avoid_items": ["Избегать перегруза", "Избегать суеты", "Избегать импульса"],
        "header_disclaimer": "Только про личный день.",
        "context_for_next_surfaces": "Тезис дня для следующих экранов, достаточно длинный текст.",
        "pattern_insight": "",
        "life_context_insight": "",
        "core_message": "Тело сообщения про день.",
        "action_options": ["Шаг один", "Шаг два", "Шаг три"],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один завершённый кусок."},
            {"area": "love", "stance": "down", "line": "Отношения — сказать прямо."},
            {"area": "money", "stance": "neutral", "line": "Деньги — цифры и границы."},
        ],
        "support_hooks": ["Опора один", "Опора два"],
        "why_astrological_layers": [{"kind": "daily_spine", "anchor": "ось", "detail": "деталь"}],
    }
    assert _validate_payload_shape("guide", payload) is True
    assert _guide_payload_concrete("ru", payload) is False


def test_texts_semantically_redundant_token_overlap():
    a = "сегодня важно держать одну ясную линию и не распыляться на лишние задачи"
    b = "держать одну ясную линию сегодня без распыления на лишние дела и входы"
    assert _texts_semantically_redundant(a, b) is True
    assert _texts_semantically_redundant("совсем другой текст про кофе", b) is False


def test_dedupe_guide_payload_strips_core_message_headline_redundant_with_body():
    payload = {
        "headline": "Главный акцент дня про приоритет и ясность формулировок.",
        "subline": "Подстрочник достаточной длины для теста валидации и прохождения гейта.",
        "energy_line": "Ресурс дня около 55/100: при необходимости снижай темп.",
        "focus_line": "Внимание и ясность — около 50/100: один завершённый блок.",
        "risk_line": "Перегруз",
        "risk_detail": "Следи, чтобы срочное не съело главное и не размыло линию дня.",
        "do_items": [
            "Сделай первый короткий шаг по главной линии и зафиксируй результат.",
            "Второй конкретный шаг по делу без лишних обещаний.",
            "Третий шаг дня с понятным завершением.",
        ],
        "avoid_items": ["Лишние обещания без ресурса", "Реактивность вместо важного", "Попытка закрыть всё сразу"],
        "header_disclaimer": "Только про личный день по профилю.",
        "context_for_next_surfaces": "Тезис дня для следующих экранов, достаточно длинный текст для контекста.",
        "pattern_insight": "",
        "life_context_insight": "",
        "core_message": {
            "headline": "Главный акцент дня про приоритет и ясность формулировок.",
            "body": "Главный акцент дня — приоритет и ясность формулировок без распыления.",
            "risk": "Не смешивай срочное с важным.",
            "best_move": "Один короткий шаг по линии.",
        },
        "action_options": [
            {"title": "Закрой одну задачу, которая реально блокирует день.", "reason": "Чтобы освободить внимание."},
            {"title": "Разберись с одним вопросом: что решить и до когда."},
            {"title": "Не перегружай день: максимум три пункта, остальное — перенос."},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один завершённый кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — сказать прямо, не угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — цифры и границы без импульса."},
        ],
        "support_hooks": ["Поставь одну цель на сегодня в Flow.", "Или короткая практика 3–5 минут."],
        "why_astrological_layers": [
            {"kind": "daily_spine", "anchor": "ось дня", "detail": "Главный акцент дня про приоритет и ясность формулировок полностью."}
        ],
    }
    foundation = {
        "spine": {
            "first_move": "Детерминированный первый шаг из стержня без повтора заголовка.",
            "best_mode": "Режим дня из расчёта: ровно и без суеты.",
        }
    }
    fusion = {"scores": {"energy": 44, "focus": 62}}
    out = _dedupe_guide_payload_cross_fields(payload, foundation, fusion, "ru")
    cm = out["core_message"]
    assert isinstance(cm, dict)
    assert "headline" not in cm
    assert isinstance(cm.get("body"), str) and cm["body"]
    why = out["why_astrological_layers"][0]
    assert why["detail"] != payload["why_astrological_layers"][0]["detail"]
    assert "заголовк" in why["detail"].lower()


def test_dedupe_guide_o1_brief_seed_rewrites_redundant_context_and_pattern():
    """O1: якорь day_engine_brief в пуле; context_for_next_surfaces и pattern_insight не дублируют опору."""
    anchor = (
        "Сегодня важно держать один приоритет и не распыляться на срочное вместо важного "
        "потому что ресурс дня ограничен и лучше один завершённый блок по главной линии"
    )
    brief = {
        "contract_version": "day_narrative_brief_v0",
        "anchor_summary": anchor,
        "do_hint": "Один короткий шаг по приоритету.",
        "avoid_hint": "Без лишних обещаний.",
        "tempo_hint": "Ровный темп.",
    }
    headline = "Главный акцент дня про приоритет и ясность формулировок."
    payload = {
        "headline": headline,
        "subline": "Подстрочник достаточной длины для теста валидации и прохождения гейта.",
        "energy_line": "Ресурс дня около 55/100: при необходимости снижай темп.",
        "focus_line": "Внимание и ясность — около 50/100: один завершённый блок.",
        "risk_line": "Перегруз",
        "risk_detail": "Следи, чтобы срочное не съело главное и не размыло линию дня.",
        "do_items": [
            "Сделай первый короткий шаг по главной линии и зафиксируй результат.",
            "Второй конкретный шаг по делу без лишних обещаний.",
            "Третий шаг дня с понятным завершением.",
        ],
        "avoid_items": ["Лишние обещания без ресурса", "Реактивность вместо важного", "Попытка закрыть всё сразу"],
        "header_disclaimer": "Только про личный день по профилю.",
        "context_for_next_surfaces": anchor,
        "pattern_insight": headline,
        "life_context_insight": "Отдельная мысль про контекст жизни без повтора заголовка дословно.",
        "core_message": {
            "headline": "Главный акцент дня про приоритет и ясность формулировок.",
            "body": "Главный акцент дня — приоритет и ясность формулировок без распыления.",
            "risk": "Не смешивай срочное с важным.",
            "best_move": "Один короткий шаг по линии.",
        },
        "action_options": [
            {"title": "Закрой одну задачу, которая реально блокирует день.", "reason": "Чтобы освободить внимание."},
            {"title": "Разберись с одним вопросом: что решить и до когда."},
            {"title": "Не перегружай день: максимум три пункта, остальное — перенос."},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один завершённый кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — сказать прямо, не угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — цифры и границы без импульса."},
        ],
        "support_hooks": ["Поставь одну цель на сегодня в Flow.", "Или короткая практика 3–5 минут."],
        "why_astrological_layers": [
            {"kind": "daily_spine", "anchor": "ось дня", "detail": "Сводка дня без дублирования заголовка полностью."}
        ],
    }
    foundation = {
        "spine": {
            "first_move": "Детерминированный первый шаг из стержня без повтора заголовка.",
            "best_mode": "Режим дня из расчёта: ровно и без суеты.",
        }
    }
    fusion = {"scores": {"energy": 44, "focus": 62}}
    out = _dedupe_guide_payload_cross_fields(
        payload, foundation, fusion, "ru", day_engine_brief=brief
    )
    assert out["context_for_next_surfaces"].strip() != anchor
    assert out["pattern_insight"].strip() != headline
    assert len(out["pattern_insight"].strip()) > 20


def test_o1_top_level_hero_cleared_when_redundant_with_core_body_and_brief_anchor():
    """O1: headline/subline не дублируют core_message.body и anchor_summary."""
    anchor = "Сегодня держи один приоритет и не распыляйся на срочное вместо важного."
    body = (
        "Сегодня держи один приоритет и не распыляйся на срочное вместо важного — "
        "это главная линия дня без отвлечений."
    )
    brief = {"contract_version": "day_narrative_brief_v0", "anchor_summary": anchor}
    payload = {
        "headline": anchor,
        "subline": anchor + " Дублирующий подстрочник.",
        "energy_line": "Ресурс дня около 55/100: при необходимости снижай темп.",
        "focus_line": "Внимание и ясность — около 50/100: один завершённый блок.",
        "risk_line": "Перегруз",
        "risk_detail": "Следи, чтобы срочное не съело главное и не размыло линию дня.",
        "do_items": [
            "Сделай первый короткий шаг по главной линии и зафиксируй результат.",
            "Второй конкретный шаг по делу без лишних обещаний.",
            "Третий шаг дня с понятным завершением.",
        ],
        "avoid_items": ["Лишние обещания без ресурса", "Реактивность вместо важного", "Попытка закрыть всё сразу"],
        "header_disclaimer": "Только про личный день по профилю.",
        "context_for_next_surfaces": "Тезис дня для следующих экранов, достаточно длинный текст для контекста.",
        "pattern_insight": "",
        "life_context_insight": "",
        "core_message": {"body": body},
        "action_options": [
            {"title": "Закрой одну задачу, которая реально блокирует день.", "reason": "Чтобы освободить внимание."},
            {"title": "Разберись с одним вопросом: что решить и до когда."},
            {"title": "Не перегружай день: максимум три пункта, остальное — перенос."},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один завершённый кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — сказать прямо, не угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — цифры и границы без импульса."},
        ],
        "support_hooks": ["Поставь одну цель на сегодня в Flow.", "Или короткая практика 3–5 минут."],
        "why_astrological_layers": [],
    }
    foundation = {
        "spine": {
            "first_move": "Детерминированный первый шаг из стержня без повтора заголовка.",
            "best_mode": "Режим дня из расчёта: ровно и без суеты.",
        }
    }
    fusion = {"scores": {"energy": 44, "focus": 62}}
    out = _dedupe_guide_payload_cross_fields(
        payload, foundation, fusion, "ru", day_engine_brief=brief
    )
    assert not str(out.get("headline") or "").strip()
    assert not str(out.get("subline") or "").strip()
    cm = out.get("core_message")
    assert isinstance(cm, dict) and str(cm.get("body") or "").strip() == body


def test_o1_subline_cleared_when_redundant_with_headline_only():
    """O1: подстрочник не копирует заголовок, если body отличается."""
    payload = {
        "headline": "Отдельный заголовок про дисциплину и один фокус на сегодня.",
        "subline": "Отдельный заголовок про дисциплину и один фокус на сегодня.",
        "energy_line": "Ресурс дня около 55/100: при необходимости снижай темп.",
        "focus_line": "Внимание и ясность — около 50/100: один завершённый блок.",
        "risk_line": "Перегруз",
        "risk_detail": "Следи, чтобы срочное не съело главное и не размыло линию дня.",
        "do_items": [
            "Сделай первый короткий шаг по главной линии и зафиксируй результат.",
            "Второй конкретный шаг по делу без лишних обещаний.",
            "Третий шаг дня с понятным завершением.",
        ],
        "avoid_items": ["Лишние обещания без ресурса", "Реактивность вместо важного", "Попытка закрыть всё сразу"],
        "header_disclaimer": "Только про личный день по профилю.",
        "context_for_next_surfaces": "Тезис дня для следующих экранов, достаточно длинный текст для контекста.",
        "pattern_insight": "",
        "life_context_insight": "",
        "core_message": {
            "body": "Луна в аспекте к натальному Солнцу подсказывает мягкий темп без резких смен курса.",
        },
        "action_options": [
            {"title": "Закрой одну задачу, которая реально блокирует день.", "reason": "Чтобы освободить внимание."},
            {"title": "Разберись с одним вопросом: что решить и до когда."},
            {"title": "Не перегружай день: максимум три пункта, остальное — перенос."},
        ],
        "sphere_triad": [
            {"area": "work", "stance": "up", "line": "Работа — один завершённый кусок важнее десяти начатых."},
            {"area": "love", "stance": "down", "line": "Отношения — сказать прямо, не угадывать."},
            {"area": "money", "stance": "neutral", "line": "Деньги — цифры и границы без импульса."},
        ],
        "support_hooks": ["Поставь одну цель на сегодня в Flow.", "Или короткая практика 3–5 минут."],
        "why_astrological_layers": [],
    }
    foundation = {
        "spine": {
            "first_move": "Детерминированный первый шаг из стержня без повтора заголовка.",
            "best_mode": "Режим дня из расчёта: ровно и без суеты.",
        }
    }
    fusion = {"scores": {"energy": 44, "focus": 62}}
    out = _dedupe_guide_payload_cross_fields(payload, foundation, fusion, "ru")
    assert str(out.get("headline") or "").strip()
    assert not str(out.get("subline") or "").strip()
