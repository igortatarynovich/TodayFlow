"""Freemium shaping for compatibility product surface."""

from todayflow_backend.services.compatibility_access_v0 import (
    apply_paragraph_gate,
    shape_product_surface_for_tier,
)
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatAnalysisBlock,
    SignCompatRoles,
    SignCompatScenarioGroup,
    SignCompatSubscores,
    SignCompatibilityProductSurface,
)


def _sample_surface() -> SignCompatibilityProductSurface:
    return SignCompatibilityProductSurface(
        score_tagline="Тянет и спорит",
        overview_paragraphs=["Абзац один про притяжение.", "Абзац два про различие.", "Абзац три про конфликт."],
        blocks=[
            SignCompatAnalysisBlock(
                key="emotions",
                title="Эмоции",
                subtitle="темп",
                takeaway="Тянет быстро",
                detail="Длинный разбор эмоций",
                risk="Не дави",
                action="Сбавь темп",
                tips=[],
            ),
            SignCompatAnalysisBlock(
                key="communication",
                title="Общение",
                subtitle="",
                takeaway="Прямота",
                detail="Как говорите",
                risk="Молчание",
                action="Назови факт",
                tips=[],
            ),
            SignCompatAnalysisBlock(
                key="conflicts",
                title="Конфликты",
                subtitle="",
                takeaway="Цикл",
                detail="Кто уходит",
                risk="Ультиматумы",
                action="Пауза 20 минут",
                tips=[],
            ),
            SignCompatAnalysisBlock(
                key="sexuality",
                title="Секс",
                subtitle="",
                takeaway="Инициатива",
                detail="Желание и темп",
                risk="Давление",
                action="Договоритесь о знаке стоп",
                tips=["Начни с тела", "Спроси темп", "Закрой цикл словами"],
            ),
            SignCompatAnalysisBlock(
                key="long_term",
                title="Долгосрок",
                subtitle="",
                takeaway="Опора",
                detail="Годы",
                risk="Застой",
                action="Ритуал сверки",
                tips=["Раз в месяц"],
            ),
        ],
        roles=SignCompatRoles(
            you_bullets=["Инициируешь", "Ждёшь ясности", "Боишься потери"],
            partner_bullets=["Держит дистанцию", "Проверяет тепло"],
        ),
        scenarios=[
            SignCompatScenarioGroup(id="closer", title="Ближе", bullets=["Назови желание", "Сбавь темп"]),
            SignCompatScenarioGroup(id="exit", title="Стоп", bullets=["Не угрожай уходом"]),
        ],
        subscores=SignCompatSubscores(
            attraction=70,
            conflicts=55,
            sexuality=68,
            stability=62,
        ),
    )


def test_guest_tier_is_teaser_only():
    shaped, meta = shape_product_surface_for_tier(_sample_surface(), tier="guest", overall_score=66, locale="ru")
    assert meta["tier"] == "guest"
    assert len(shaped.overview_paragraphs) == 1
    assert len(shaped.blocks) == 1
    assert shaped.blocks[0].action == ""
    assert shaped.scenarios == []
    assert "yes_no" in meta["locked_layers"]
    assert meta["upsell"] is not None
    assert meta.get("guidance") is None


def test_registered_locks_paid_guidance():
    shaped, meta = shape_product_surface_for_tier(
        _sample_surface(), tier="registered", overall_score=66, locale="ru"
    )
    assert meta["tier"] == "registered"
    assert len(shaped.overview_paragraphs) == 2
    assert any(b.key == "conflicts" for b in shaped.blocks)
    sex = next(b for b in shaped.blocks if b.key == "sexuality")
    assert sex.tips == []
    assert shaped.scenarios == []
    assert "do_dont_how" in meta["locked_layers"]
    assert meta["upsell"]["cta_subscribe"]


def test_paid_includes_guidance_pack():
    shaped, meta = shape_product_surface_for_tier(_sample_surface(), tier="paid", overall_score=80, locale="ru")
    assert meta["locked_layers"] == []
    assert meta["guidance"]["yes_no"]["answer"] == "да"
    assert meta["guidance"]["do"]
    assert meta["guidance"]["dont"]
    assert meta["guidance"]["how"]
    assert len(shaped.scenarios) == 2


def test_paragraph_gate_by_tier():
    paras = ["a", "b", "c", "d"]
    assert apply_paragraph_gate(paras, tier="guest") == (["a"], ["a"])
    assert apply_paragraph_gate(paras, tier="registered") == (["a", "b"], ["a", "b"])
    assert apply_paragraph_gate(paras, tier="paid") == (["a", "b", "c"], paras)
