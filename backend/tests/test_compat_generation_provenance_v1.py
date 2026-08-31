"""Provenance: compatibility dynamics LLM generation logs include core_profile_snapshot_id."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from todayflow_backend.services.compatibility_llm import generate_llm_product_surface
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatibilityProductSurface,
    SignCompatSubscores,
    SignCompatAnalysisBlock,
    SignCompatRoles,
    SignCompatScenarioGroup,
)


def _minimal_template() -> SignCompatibilityProductSurface:
    return SignCompatibilityProductSurface(
        score_tagline="tagline",
        subscores=SignCompatSubscores(attraction=50, stability=50, conflicts=50, sexuality=50),
        overview_paragraphs=["overview"],
        blocks=[
            SignCompatAnalysisBlock(
                key="communication",
                title="Communication",
                subtitle="sub",
                takeaway="take",
                detail="detail",
                risk="risk",
                action="action",
                tips=["tip"],
            )
        ],
        roles=SignCompatRoles(you_bullets=["you"], partner_bullets=["partner"]),
        scenarios=[SignCompatScenarioGroup(id="closer", title="Closer", bullets=["b"])],
    )


@pytest.mark.smoke
def test_generate_llm_product_surface_logs_core_profile_snapshot_id(
    db_session: Session,
) -> None:
    """When a core_profile_snapshot_id is provided, the generation log must carry it."""
    template = _minimal_template()
    mock_learning = MagicMock()
    mock_learning.log_generation.return_value = MagicMock(id=7)
    mock_client = MagicMock()

    with (
        patch(
            "todayflow_backend.services.compatibility_llm.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.get_openai_compatible_client",
            return_value=mock_client,
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.chat_completion_text",
            side_effect=RuntimeError("forced failure"),
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.get_learning_service",
            return_value=mock_learning,
        ),
    ):
        surface, source, _ = generate_llm_product_surface(
            db=db_session,
            template_surface=template,
            pair_display="Aries × Taurus",
            user1_label="You",
            user2_label="Partner",
            relationship_context="just_met",
            pair_dynamics={},
            signals={},
            element_relation="fire-earth",
            rhythm_relation="cardinal-fixed",
            block_feedback=None,
            user_id=1,
            locale="ru",
            core_profile_snapshot_id=42,
        )

    assert source == "template"
    assert surface == template
    mock_learning.log_generation.assert_called_once()
    call_kwargs = mock_learning.log_generation.call_args.kwargs
    assert call_kwargs.get("core_profile_snapshot_id") == 42


def test_generate_llm_product_surface_snapshot_defaults_to_none(
    db_session: Session,
) -> None:
    """No snapshot id is passed as None, not omitted."""
    template = _minimal_template()
    mock_learning = MagicMock()
    mock_learning.log_generation.return_value = MagicMock(id=8)
    mock_client = MagicMock()

    with (
        patch(
            "todayflow_backend.services.compatibility_llm.is_llm_chat_configured",
            return_value=True,
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.get_openai_compatible_client",
            return_value=mock_client,
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.chat_completion_text",
            side_effect=RuntimeError("forced failure"),
        ),
        patch(
            "todayflow_backend.services.compatibility_llm.get_learning_service",
            return_value=mock_learning,
        ),
    ):
        generate_llm_product_surface(
            db=db_session,
            template_surface=template,
            pair_display="Aries × Taurus",
            user1_label="You",
            user2_label="Partner",
            relationship_context="just_met",
            pair_dynamics={},
            signals={},
            element_relation="fire-earth",
            rhythm_relation="cardinal-fixed",
            block_feedback=None,
            user_id=1,
            locale="ru",
        )

    call_kwargs = mock_learning.log_generation.call_args.kwargs
    assert "core_profile_snapshot_id" in call_kwargs
    assert call_kwargs["core_profile_snapshot_id"] is None
