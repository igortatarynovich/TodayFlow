"""Tests for playful compatibility surface contract."""

from todayflow_backend.services.compatibility_playful_surface import apply_playful_surface_contract
from todayflow_backend.services.compatibility_scenario_tone import SCENARIO_TONE_REGISTRY
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatAnalysisBlock,
    SignCompatRoles,
    SignCompatScenarioGroup,
    SignCompatSubscores,
    SignCompatibilityProductSurface,
)


def _sample_surface() -> SignCompatibilityProductSurface:
    return SignCompatibilityProductSurface(
        score_tagline="С лёгкой иронией: Вы хорошо держитесь вместе в кризисах, если роли распределены заранее и вы оба готовы долго обсуждать чувства.",
        subscores=SignCompatSubscores(attraction=79, stability=83, conflicts=68, sexuality=81),
        overview_paragraphs=[
            "Длинный первый абзац про притяжение и различия.",
            "Второй абзац про конфликты и напряжение в отношениях.",
            "Третий абзац с советами на годы вперёд.",
        ],
        blocks=[
            SignCompatAnalysisBlock(
                key="emotions",
                title="Эмоции",
                subtitle="sub",
                takeaway="Длинный takeaway про эмоции",
                detail="Очень длинный detail про эмоции и циклы",
                risk="Риск эмоционального выгорания",
                action="Договоритесь о паузах",
            ),
            SignCompatAnalysisBlock(
                key="communication",
                title="Общение",
                subtitle="sub",
                takeaway="t",
                detail="d",
                risk="r",
                action="a",
            ),
            SignCompatAnalysisBlock(
                key="conflicts",
                title="Конфликты",
                subtitle="sub",
                takeaway="t",
                detail="d",
                risk="r",
                action="a",
            ),
            SignCompatAnalysisBlock(
                key="sexuality",
                title="Сексуальность",
                subtitle="sub",
                takeaway="t",
                detail="d",
                risk="r",
                action="a",
            ),
            SignCompatAnalysisBlock(
                key="long_term",
                title="Долгосрок",
                subtitle="sub",
                takeaway="t",
                detail="d",
                risk="r",
                action="a",
            ),
        ],
        roles=SignCompatRoles(you_bullets=["a", "b", "c"], partner_bullets=["d", "e", "f"]),
        scenarios=[SignCompatScenarioGroup(id="closer", title="t", bullets=["x", "y"])],
    )


def test_playful_contract_trims_surface() -> None:
    spec = SCENARIO_TONE_REGISTRY["partner_in_crime"]
    surface = _sample_surface()
    apply_playful_surface_contract(surface, spec, locale="ru")

    assert len(surface.overview_paragraphs) == 1
    assert len(surface.overview_paragraphs[0]) <= 200
    assert not surface.scenarios
    for block in surface.blocks:
        assert block.detail == ""
        assert block.risk == ""
        assert block.action == ""
        assert len(block.takeaway) <= 96


def test_playful_contract_strips_irony_prefix() -> None:
    spec = SCENARIO_TONE_REGISTRY["after_wine"]
    surface = _sample_surface()
    apply_playful_surface_contract(surface, spec, locale="ru")
    assert not surface.score_tagline.lower().startswith("с лёгкой иронией")
