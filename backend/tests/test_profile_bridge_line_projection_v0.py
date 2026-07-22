"""Delta #5: bridge_line as path transition to Today — not empty CTA / day forecast."""

from __future__ import annotations

from todayflow_backend.services.profile_bridge_line_projection_v0 import (
    PROJECTION_VERSION,
    _BRIDGE_REPEAT_RU,
    _BRIDGE_TENSION_RU,
    attach_bridge_line_v0,
    project_bridge_line_v0,
)


def test_tension_bridge_to_observations() -> None:
    out = project_bridge_line_v0(
        insight_nodes={
            "nodes": [{"id": "node_tension_0", "kind": "tension", "insight": "x" * 20}]
        }
    )
    assert out["projection_version"] == PROJECTION_VERSION
    assert out["bridge_line"] == _BRIDGE_TENSION_RU
    assert out["cta"] == "today"
    assert out["leads_to"] == "today"
    assert out["rules"]["forbid_day_forecast"] is True
    assert "завтра" not in (out["bridge_line"] or "").lower()


def test_repeat_bridge_to_today_check() -> None:
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
        }
    )
    assert out["bridge_line"] == _BRIDGE_REPEAT_RU
    assert out["source_node_id"] == "node_repeat_0"
    assert "Today" in (out["bridge_line"] or "")


def test_null_without_node() -> None:
    out = project_bridge_line_v0(insight_nodes={"nodes": []})
    assert out["bridge_line"] is None
    assert out["cta"] is None


def test_attach() -> None:
    payload = {
        "insight_nodes_v0": {
            "nodes": [{"id": "node_tension_0", "kind": "tension", "insight": "длинный инсайт узла"}]
        },
        "effort_vector_v0": {"effort_vector": "Сделать один шаг"},
    }
    out = attach_bridge_line_v0(payload)
    assert out["bridge_line_v0"]["leads_to"] == "today"
