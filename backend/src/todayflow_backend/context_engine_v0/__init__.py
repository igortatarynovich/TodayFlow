"""Thin question→ContextPack helpers used by spheres synthesis.

P5 product-wide Context Engine is STOPPED (see RFC). Do not expand this package
into FactAtoms / Today / new registries without a proven quality or DRY case.
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
