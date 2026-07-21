"""Canonical Context Engine v0 (P5).

RFC: docs/rfc/RFC_CANONICAL_CONTEXT_ENGINE_V0.md
First slice: docs/audits/CONTEXT_ENGINE_P5_FIRST_SLICE.md
"""

from todayflow_backend.context_engine_v0.build_context_pack_v0 import (
    build_context_pack_for_sphere,
    build_context_pack_v0,
    context_pack_to_synthesis_input,
)
from todayflow_backend.context_engine_v0.question_registry_v0 import (
    QUESTION_SPECS,
    SPHERE_TO_QUESTION,
    get_question_spec,
    list_question_ids,
    question_id_for_sphere,
)
from todayflow_backend.context_engine_v0.types_v0 import CONTEXT_ENGINE_VERSION

__all__ = [
    "CONTEXT_ENGINE_VERSION",
    "QUESTION_SPECS",
    "SPHERE_TO_QUESTION",
    "build_context_pack_for_sphere",
    "build_context_pack_v0",
    "context_pack_to_synthesis_input",
    "get_question_spec",
    "list_question_ids",
    "question_id_for_sphere",
]
