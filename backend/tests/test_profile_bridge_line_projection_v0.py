"""Delta #5: bridge answers «why open Today?» — never «what to do?»."""

from __future__ import annotations

from todayflow_backend.services.profile_bridge_line_projection_v0 import (
    PROJECTION_VERSION,
    _BRIDGE_REPEAT_RU,
    _BRIDGE_TENSION_RU,
    attach_bridge_line_v0,
    project_bridge_line_v0,
)


def test_tension_bridge_explains_why_today() -> None:
    out = project_bridge_line_v0(
        insight_nodes={
            "nodes": [{"id": "node_tension_0", "kind": "tension", "insight": "x" * 20}]
        },
        effort_vector={"effort_vector": "Доводить один контур до видимого результата."},
    )
    assert out["projection_version"] == PROJECTION_VERSION
    assert out["bridge_line"] == _BRIDGE_TENSION_RU
    assert out["rules"]["answers_why_open_today_only"] is True
    assert out["rules"]["forbid_imperative_action"] is True
    assert not (out["bridge_line"] or "").lower().startswith("отметь")
    assert "завтра" not in (out["bridge_line"] or "").lower()
    # Must not restate effort_vector
    assert "контур" not in (out["bridge_line"] or "").lower()


def test_repeat_bridge_is_path_not_action() -> None:
    out = project_bridge_line_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_repeat_0",
                    "kind": "repeat",
                    "insight": "x" * 20,
                    "living_evidence": ["«заметка»"],
                }
            ]
        },
        effort_vector={
            "effort_vector": "Назвать тему разговора одним предложением до вечерней усталости."
        },
    )
    assert out["bridge_line"] == _BRIDGE_REPEAT_RU
    assert "Отметь" not in (out["bridge_line"] or "")
    assert "Назвать тему" not in (out["bridge_line"] or "")
    assert out["leads_to"] == "today"
    assert out["cta"] == "today"


def test_null_without_node() -> None:
    out = project_bridge_line_v0(insight_nodes={"nodes": []})
    assert out["bridge_line"] is None
    assert out["cta"] is None


def test_attach() -> None:
    payload = {
        "insight_nodes_v0": {
            "nodes": [{"id": "node_tension_0", "kind": "tension", "insight": "длинный инсайт узла"}]
        },
        "effort_vector_v0": {"effort_vector": "Сделать один шаг без перефраза моста."},
    }
    out = attach_bridge_line_v0(payload)
    assert out["bridge_line_v0"]["leads_to"] == "today"
    assert out["bridge_line_v0"]["rules"]["forbid_effort_vector_duplicate"] is True
