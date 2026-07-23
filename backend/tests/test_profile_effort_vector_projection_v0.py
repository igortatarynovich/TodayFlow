"""Delta #4: effort_vector from selected insight node only."""

from __future__ import annotations

from todayflow_backend.services.profile_effort_vector_projection_v0 import (
    PROJECTION_VERSION,
    attach_effort_vector_v0,
    project_effort_vector_v0,
)


def test_repeat_uses_help_as_effort_vector() -> None:
    out = project_effort_vector_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_repeat_0",
                    "kind": "repeat",
                    "insight": "Ты откладываешь сложный разговор, пока усталость не делает его ещё тяжелее.",
                    "help": "Назвать тему разговора одним предложением до того, как накопится вечерняя усталость.",
                }
            ]
        }
    )
    assert out["projection_version"] == PROJECTION_VERSION
    assert out["rules"]["no_llm"] is True
    assert out["source_node_id"] == "node_repeat_0"
    assert out["role"] == "exit_recurring_trap"
    assert out["effort_vector"].startswith("Назвать тему")
    assert "откладываешь" not in (out["effort_vector"] or "")
    assert "insight_nodes_v0.nodes[0].help" in out["source_fields"]


def test_tension_uses_help_not_insight_copy() -> None:
    out = project_effort_vector_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_tension_0",
                    "kind": "tension",
                    "insight": "Ты легко открываешь новый контур, но устойчивость появляется только после закрепления.",
                    "help": "Один завершённый контур важнее трёх новых начал.",
                }
            ]
        }
    )
    assert out["role"] == "steer_main_tension"
    assert out["effort_vector"] == "Один завершённый контур важнее трёх новых начал."
    assert len(out["effort_vector"]) <= 140


def test_null_when_help_missing() -> None:
    out = project_effort_vector_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_tension_0",
                    "kind": "tension",
                    "insight": "Ты легко открываешь новый контур без устойчивого закрепления.",
                    "help": None,
                }
            ]
        }
    )
    assert out["effort_vector"] is None
    assert out["source_node_id"] == "node_tension_0"
    assert out["rules"]["null_when_no_safe_help"] is True


def test_null_when_help_restates_insight() -> None:
    same = "Откладывание сложных разговоров до вечерней усталости."
    out = project_effort_vector_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_repeat_0",
                    "kind": "repeat",
                    "insight": same,
                    "help": same,
                }
            ]
        }
    )
    assert out["effort_vector"] is None


def test_null_without_nodes() -> None:
    out = project_effort_vector_v0(insight_nodes={"nodes": []})
    assert out["effort_vector"] is None
    assert out["source_node_id"] is None


def test_does_not_use_life_mission_or_external_lists() -> None:
    """Guard: even if payload had mission elsewhere, projector only sees nodes."""
    out = project_effort_vector_v0(
        insight_nodes={
            "nodes": [
                {
                    "id": "node_repeat_0",
                    "kind": "repeat",
                    "insight": "Повтор достаточно длинный для контекста узла.",
                    "help": "Сделать один короткий разговор до накопления усталости.",
                    # Noise fields must be ignored if ever present on node.
                    "life_mission": "Не должна стать effort_vector",
                }
            ]
        }
    )
    assert out["effort_vector"] == "Сделать один короткий разговор до накопления усталости."
    assert "Не должна" not in (out["effort_vector"] or "")


def test_attach_reads_insight_nodes_only() -> None:
    payload = {
        "insight_nodes_v0": {
            "nodes": [
                {
                    "id": "node_tension_0",
                    "kind": "tension",
                    "insight": "Напряжение достаточно длинное как контекст узла.",
                    "help": "Доводить один контур до видимого результата.",
                }
            ]
        },
        "profile_contract_v1": {"life_mission": "Миссия не источник effort_vector"},
    }
    out = attach_effort_vector_v0(payload)
    assert out["effort_vector_v0"]["effort_vector"] == "Доводить один контур до видимого результата."
    assert out["effort_vector_v0"]["rules"]["forbid_life_mission"] is True
