"""OpenAPI components for attachment reference, CUM ILR slice, learning event payloads."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_openapi_attachment_reference_schema(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    schemas = spec.get("components", {}).get("schemas", {})
    assert "CompatibilityAttachmentReferenceV0" in schemas
    props = schemas["CompatibilityAttachmentReferenceV0"]["properties"]
    assert "attachment_style_hints" in props
    assert "deep_block_order" in props

    hint = schemas["AttachmentStyleHintResponse"]["properties"]
    assert {"code", "label", "summary"}.issubset(hint.keys())

    sign_compat = schemas["SignCompatibilityResponse"]["properties"]
    att_ref = sign_compat["attachment_reference"]
    ref = att_ref.get("$ref") or ""
    if not ref and "anyOf" in att_ref:
        ref = next(
            (item.get("$ref", "") for item in att_ref["anyOf"] if item.get("$ref")),
            "",
        )
    assert ref.endswith("CompatibilityAttachmentReferenceV0")


@pytest.mark.smoke
def test_openapi_cum_interpretation_instances_schema(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    schemas = spec.get("components", {}).get("schemas", {})
    assert "CompactUserModelInterpretationInstance" in schemas
    props = schemas["CompactUserModelInterpretationInstance"]["properties"]
    assert "user_verdict" in props
    assert "interpretation_ref_id" in props

    cum = schemas["CompactUserModelResponse"]["properties"]
    items_ref = cum["interpretation_instances_top_k"]["items"].get("$ref", "")
    assert items_ref.endswith("CompactUserModelInterpretationInstance")


@pytest.mark.smoke
def test_openapi_meaning_learning_payload_schemas(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    paths = spec.get("paths", {})
    assert "/meaning/events/learning-payloads" in paths
    assert "get" in paths["/meaning/events/learning-payloads"]

    schemas = spec.get("components", {}).get("schemas", {})
    for name in (
        "CompatibilityAttachmentConfirmPayload",
        "InterpretationInstanceConfirmPayload",
        "ProfileAtomCorrectionPayload",
        "MeaningLearningPayloadSchemaRefs",
    ):
        assert name in schemas, f"missing OpenAPI schema {name}"

    r = client.get("/meaning/events/learning-payloads")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["compatibility_attachment_confirm"]["surface"] == "analyze_dynamics"
    assert body["interpretation_instance_confirm"]["instance_id"] == "ilr-inst-example"
