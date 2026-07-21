"""C2 — Compatibility content contracts, guest baseline, quality checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from todayflow_backend.services.compatibility_content_v1.banned_phrases import find_banned_hits
from todayflow_backend.services.compatibility_content_v1.contracts import (
    GuestContentV1,
    PremiumContentV1,
    RegisteredContentV1,
)
from todayflow_backend.services.compatibility_content_v1.generate_v1 import generate_content_v1
from todayflow_backend.services.compatibility_content_v1.guest_baseline_v1 import build_guest_content_v1
from todayflow_backend.services.compatibility_content_v1.quality_checks import (
    check_guest_vs_registered_distinct,
    check_premium_vs_registered_distinct,
    check_template_diversity,
    run_quality_suite,
    sense_fingerprint,
)
from todayflow_backend.services.compatibility_content_v1.source_depth import resolve_source_depth
from todayflow_backend.services.compatibility_content_v1.surface_adapter import (
    guest_to_product_surface,
)
from todayflow_backend.services.compatibility_content_v1.validators import (
    validate_guest_dict,
    validate_premium_dict,
    validate_registered_dict,
)


def test_source_depth_levels():
    assert resolve_source_depth(has_signs=True) == "zodiac_only"
    assert resolve_source_depth(has_birth_dates=True) == "birth_dates"
    assert resolve_source_depth(profile_a_ready=True) == "profile_enriched"
    assert resolve_source_depth(profile_a_ready=True, profile_b_ready=True) == "two_profiles"


def test_guest_baseline_finished_and_valid():
    g = build_guest_content_v1(from_sign="aries", to_sign="cancer", relationship_context="just_met")
    assert g.tier == "guest"
    assert g.source_depth == "zodiac_only"
    assert len(g.locked_preview) >= 2
    model, errs = validate_guest_dict(g.model_dump())
    assert model is not None
    assert errs == []
    q = run_quality_suite(tier="guest", content=g.model_dump())
    assert q["ok"], q["errors"]


def test_guest_same_sign_distinct_from_hard_pair():
    same = build_guest_content_v1(from_sign="scorpio", to_sign="scorpio")
    hard = build_guest_content_v1(from_sign="aries", to_sign="cancer")
    assert sense_fingerprint(same.model_dump()) != sense_fingerprint(hard.model_dump())
    assert "зеркало" in same.headline.lower() or "одинаков" in same.summary.lower()


def test_guest_stability():
    a = build_guest_content_v1(from_sign="leo", to_sign="aquarius", relationship_context="in_relationship")
    b = build_guest_content_v1(from_sign="leo", to_sign="aquarius", relationship_context="in_relationship")
    assert a.model_dump() == b.model_dump()


def test_banned_phrases_caught():
    hits = find_banned_hits("Вам важно найти баланс и ключ к гармонии")
    assert hits


def test_registered_schema_and_no_block_clone():
    data = {
        "tier": "registered",
        "source_depth": "birth_dates",
        "locale": "ru",
        "headline": "Темп решает больше знака",
        "score": 70,
        "summary": "Короткий обзор пары без пересказа блоков ниже — про темп и восстановление.",
        "attraction": "Тянет через общий юмор и вечера без плана, когда оба отпускают контроль.",
        "emotions": "Близость у вас включается после дела, не до: сначала решили быт, потом тепло.",
        "communication": "Один говорит фактами, второй — настроением; без перевода ссора звучит громче смысла.",
        "conflict": "Срыв начинается с молчания в переписке; чините через короткий звонок, не через длинный разбор.",
        "strengths": "Вы быстро собираетесь в кризис — поездка, ремонт, дедлайн — и это склеивает пару.",
        "vulnerable_spot": "Уязвимо место — обида «меня не выбрали», если планы меняются в последний момент.",
        "what_helps": "Помогает заранее назвать окно на разговор и не решать важное в голоде и спешке.",
        "main_risk": "Риск — копить претензии до взрыва из‑за «потом обсудим».",
        "practical_advice": "На этой неделе зафиксируйте один вечер без телефонов на 40 минут.",
        "confidence": "medium",
    }
    model, errs = validate_registered_dict(data)
    assert model is not None, errs
    assert errs == []


def test_premium_do_avoid_contradiction():
    bad = {
        "tier": "premium",
        "source_depth": "profile_enriched",
        "locale": "ru",
        "verdict": "скорее да",
        "verdict_reason": "Есть опора в быту и готовность чинить ссоры, если не давить темпом.",
        "do": "Говорите сразу о ревности.",
        "avoid": "Говорите сразу о ревности.",
        "how": "Выберите спокойный вечер и начните с факта, не с обвинения.",
        "what_to_say": "Мне важно понять, что для тебя значит эта пауза — можем поговорить спокойно?",
        "focus_now": "Темп сближения после ссоры.",
        "next_step": "Назначьте разговор на завтра вечером.",
        "direct_answer": None,
        "confidence": "medium",
        "score": 68,
    }
    model, errs = validate_premium_dict(bad)
    assert "contradiction:do_vs_avoid" in errs


def test_guest_vs_registered_distinct():
    guest = build_guest_content_v1(from_sign="virgo", to_sign="pisces").model_dump()
    registered = {
        **guest,
        "tier": "registered",
        "emotions": "Эмоции здесь включаются медленно: сначала проверка безопасности, потом тепло.",
        "communication": "Общение лучше короткое и конкретное — длинные монологи уводят в защиту.",
        "conflict": "В конфликте один чинит делом, второй ждёт слов — без моста оба остаются одни.",
        "strengths": "Сильны в заботе о деталях и в умении держать дом как базу.",
        "vulnerable_spot": "Уязвимы, когда критика звучит как оценка личности, а не просьба.",
        "what_helps": "Помогает договориться о «паузе 20 минут» без исчезновения из чата.",
        "summary": "Совсем другой summary для registered слоя, не копия guest.",
    }
    # Drop guest-only
    registered.pop("locked_preview", None)
    errs = check_guest_vs_registered_distinct(guest, registered)
    assert errs == []


def test_premium_not_copy_of_registered():
    registered = {
        "practical_advice": "Сделайте короткий честный разговор о темпе.",
        "emotions": "Эмоции нарастают после совместного дела, не до него.",
    }
    premium = {
        "verdict": "зависит",
        "do": "Зафиксируйте один бытовой ритуал на неделю.",
        "verdict_reason": "Есть притяжение, но без ясности статуса всё срывается.",
        "how": "Начните с одного конкретного вопроса про ожидания.",
        "focus_now": "Статус и темп.",
    }
    assert check_premium_vs_registered_distinct(premium, registered) == []


def test_generate_with_injectable_chat():
    def fake_chat(system: str, user: str) -> str:
        assert "GUEST" in system or "guest" in system.lower() or "СЛОЙ: GUEST" in system
        return json.dumps(
            {
                "contract_version": "compatibility_content_v1",
                "tier": "guest",
                "source_depth": "zodiac_only",
                "locale": "ru",
                "headline": "Овен и Рак: ток есть, темп разный",
                "score": 64,
                "summary": (
                    "По знакам между вами сильное притяжение, но этого недостаточно, чтобы судить "
                    "о реальном поведении в конфликте. На практике один ускоряет разговор, второй "
                    "уходит в себя — и оба думают, что их не слышат. Если поймать эти роли рано, "
                    "вечер спасается; если нет — одна и та же сцена повторяется уже через неделю. "
                    "Смотрите не на «совместимы ли знаки», а на то, кто обычно делает первый шаг "
                    "после паузы и кто ждёт извинений в чате."
                ),
                "attraction": "Тянет контраст огня и воды: вспышка рядом с глубиной ощущается живо.",
                "main_risk": "Риск — ссора из‑за темпа: один уже решил, второй ещё внутри чувства.",
                "practical_advice": "Перед серьёзным разговором договоритесь о паузе в десять минут без исчезновения.",
                "locked_preview": ["Эмоции и общение", "Конфликты", "Что помогает паре"],
                "confidence": "low",
            },
            ensure_ascii=False,
        )

    out = generate_content_v1(
        tier="guest",
        input_payload={"from_sign": "aries", "to_sign": "cancer", "locale": "ru"},
        chat_fn=fake_chat,
    )
    assert out["ok"], out.get("errors")


def test_guest_surface_adapter():
    g = build_guest_content_v1(from_sign="gemini", to_sign="capricorn")
    surface = guest_to_product_surface(g)
    assert surface.score_tagline == g.headline
    assert len(surface.overview_paragraphs) >= 3
    assert surface.scenarios == []


def test_eval_set_coverage():
    path = Path(__file__).resolve().parents[1] / "evals" / "compatibility_quality" / "scenarios_v1.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["scenario_count"] == 80
    assert len(doc["scenarios"]) == 80
    from collections import Counter

    c = Counter(s["group"] for s in doc["scenarios"])
    assert c["zodiac_only"] == 20
    assert c["birth_dates"] == 20
    assert c["profile_enriched"] == 20
    assert c["two_profiles"] == 20
    tags = {t for s in doc["scenarios"] for t in s.get("tags") or []}
    for required in ("same_sign", "hard_pair", "opposite_styles", "similar_profiles", "user_question", "missing_data"):
        assert required in tags

    # Diversity across guest baselines for zodiac group
    outs = [
        build_guest_content_v1(from_sign=s["from_sign"], to_sign=s["to_sign"]).model_dump()
        for s in doc["scenarios"]
        if s["group"] == "zodiac_only"
    ]
    assert check_template_diversity(outs, field="summary", min_unique_ratio=0.5) == []


def test_content_v1_flag_default_off(monkeypatch):
    from todayflow_backend.services.compatibility_content_v1.flag import content_v1_enabled
    from todayflow_backend.core import config as cfg

    monkeypatch.setattr(cfg.settings, "compatibility_content_v1", False)
    assert content_v1_enabled() is False
    monkeypatch.setattr(cfg.settings, "compatibility_content_v1", True)
    assert content_v1_enabled() is True


def test_score_zero_invalid_for_registered():
    data = {
        "tier": "registered",
        "source_depth": "zodiac_only",
        "locale": "ru",
        "headline": "Темп важнее ярлыка совместимости",
        "score": 0,
        "summary": "Короткий обзор пары без пересказа блоков ниже — про темп и восстановление после паузы.",
        "attraction": "Тянет через общий юмор и вечера без плана, когда оба отпускают контроль.",
        "emotions": "Близость у вас включается после дела, не до: сначала решили быт, потом тепло.",
        "communication": "Один говорит фактами, второй — настроением; без перевода ссора звучит громче смысла.",
        "conflict": "Срыв начинается с молчания в переписке; чините через короткий звонок, не через длинный разбор.",
        "strengths": "Вы быстро собираетесь в кризис — поездка, ремонт, дедлайн — и это склеивает пару.",
        "vulnerable_spot": "Уязвимо место — обида «меня не выбрали», если планы меняются в последний момент.",
        "what_helps": "Помогает заранее назвать окно на разговор и не решать важное в голоде и спешке.",
        "main_risk": "Риск — копить претензии до взрыва из‑за «потом обсудим».",
        "practical_advice": "На этой неделе зафиксируйте один вечер без телефонов на 40 минут.",
        "confidence": "medium",
    }
    model, errs = validate_registered_dict(data)
    assert model is None
    assert any("score" in e for e in errs)


def test_registered_premium_leak_caught():
    from todayflow_backend.services.compatibility_content_v1.banned_phrases import (
        find_registered_premium_leaks,
    )

    hits = find_registered_premium_leaks(
        "Спроси про встречи. Если разрыв большой, продолжать смысла нет."
    )
    assert hits


def test_gender_hack_banned():
    hits = find_banned_hits("Когда он(а) молчит, спросите спокойно.")
    assert any("gender_hack" in h for h in hits)


def test_bez_isterik_not_banned():
    hits = find_banned_hits("Оба говорят по делу, без истерик, ценят конструктив.")
    assert "истерик" not in hits
    assert "истеричка" not in hits


def test_birth_dates_honesty_no_false_numbers():
    from todayflow_backend.services.compatibility_content_v1.source_depth import depth_honesty_line

    line = depth_honesty_line("birth_dates", locale="ru")
    assert "базов" not in line.lower()
    assert "дат" in line.lower()


def test_publish_gate_blocks_invalid():
    from todayflow_backend.services.compatibility_content_v1.publish_gate import evaluate_publish

    gate = evaluate_publish(
        tier="registered",
        content={"tier": "registered", "score": 0, "summary": "x"},
        attempt=2,
        max_attempts=2,
    )
    assert gate["publish_allowed"] is False
    assert gate["user_facing"] is None
    assert gate["decision"] == "reject_keep_baseline"


def test_prompt_version_v11():
    from todayflow_backend.services.compatibility_content_v1.prompts_v1 import PROMPT_VERSION

    assert PROMPT_VERSION == "compatibility_content_prompt_v1.1"
    from todayflow_backend.services.compatibility_content_v1.prompts_v1 import (
        system_prompt_registered_v1,
        system_prompt_premium_v1,
    )

    reg = system_prompt_registered_v1(source_depth="zodiac_only")
    assert "продолжать смысла нет" in reg or "ГРАНИЦА С PREMIUM" in reg
    assert "20 до 95" in reg or "20 до 95" in reg.replace("—", "-")
    prem = system_prompt_premium_v1(source_depth="profile_enriched")
    assert "score НЕ возвращай" in prem or "Поле score НЕ" in prem


def test_maybe_replace_guest_surface(monkeypatch):
    from todayflow_backend.core import config as cfg
    from todayflow_backend.services.compatibility_content_v1.apply_guest_v1 import (
        maybe_replace_guest_surface,
    )
    from todayflow_backend.services.sign_compatibility_product import (
        SignCompatRoles,
        SignCompatSubscores,
        SignCompatibilityProductSurface,
    )

    legacy = SignCompatibilityProductSurface(
        score_tagline="legacy",
        subscores=SignCompatSubscores(attraction=60, stability=60, conflicts=60, sexuality=60),
        overview_paragraphs=["cut"],
        blocks=[],
        roles=SignCompatRoles(you_bullets=[], partner_bullets=[]),
        scenarios=[],
    )
    monkeypatch.setattr(cfg.settings, "compatibility_content_v1", False)
    s1, c1, _ = maybe_replace_guest_surface(
        legacy,
        tier="guest",
        from_sign="aries",
        to_sign="leo",
        relationship_context="just_met",
        locale="ru",
        score=70,
    )
    assert c1 is None
    assert s1.score_tagline == "legacy"

    monkeypatch.setattr(cfg.settings, "compatibility_content_v1", True)
    s2, c2, meta = maybe_replace_guest_surface(
        legacy,
        tier="guest",
        from_sign="aries",
        to_sign="leo",
        relationship_context="just_met",
        locale="ru",
        score=70,
    )
    assert c2 is not None
    assert c2["tier"] == "guest"
    assert s2.score_tagline != "legacy"
    assert meta.get("content_contract") == "compatibility_content_v1"
