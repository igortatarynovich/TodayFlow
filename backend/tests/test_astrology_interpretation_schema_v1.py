"""Astrology Interpretation Library v1 — schema lock (no active meaning catalog)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "docs" / "schemas" / "astrology_interpretation_v1.schema.json"
CLAIMS_SCHEMA = ROOT / "docs" / "schemas" / "astrology_claims_v1.schema.json"
EXAMPLE = ROOT / "docs" / "schemas" / "fixtures" / "astrology_interpretation_v1.example.json"
CORPUS_SCHEMA = ROOT / "docs" / "schemas" / "astrology_source_corpus_v1.schema.json"
RUNTIME = ROOT / "DATA" / "reference" / "astrology" / "interpretation_v1"
CORPUS = RUNTIME / "source_corpus_v1.json"
OBJECTS = RUNTIME / "objects_v1.json"
CLAIMS_DIR = RUNTIME / "claims"


FORBIDDEN_SURFACE_KEYS = (
    "today_message",
    "today_copy",
    "profile_blurb",
    "profile_message",
    "compatibility_line",
    "compat_copy",
    "screen_copy",
)


def _collect_property_names(node, acc: set[str]) -> None:
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        acc.update(props)
        for child in props.values():
            _collect_property_names(child, acc)
    for key in ("$defs", "allOf", "anyOf", "oneOf", "then", "else", "if", "items", "additionalProperties"):
        child = node.get(key)
        if isinstance(child, dict):
            _collect_property_names(child, acc)
        elif isinstance(child, list):
            for item in child:
                _collect_property_names(item, acc)


def test_example_fixture_matches_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert payload["contract_version"] == "astrology_interpretation_v1"
    by_id = {obj["object_id"]: obj for obj in payload["objects"]}
    saturn = by_id["astro.object.saturn"]
    combo = by_id["astro.combo.transit.saturn.square.natal.venus"]
    assert saturn["layer"] == 1
    assert saturn["type"] == "celestial_object"
    assert combo["type"] == "transit_to_natal"
    assert combo["curation_reason"] == "non_compositional"
    assert "astro.object.venus" in combo["composed_from"]
    assert all(obj["status"] == "schema_example" for obj in payload["objects"])
    assert all(obj["confidence"] is None for obj in payload["objects"])
    for obj in payload["objects"]:
        for row in obj["provenance"]:
            assert row["review_status"] == "schema_example"
            assert row["evidence_tier"] == "editorial"


def test_schema_and_example_are_surface_neutral():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    names: set[str] = set()
    _collect_property_names(schema, names)
    leaked = names.intersection(FORBIDDEN_SURFACE_KEYS)
    assert not leaked, f"surface-specific keys in schema: {leaked}"
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    for obj in payload["objects"]:
        leaked_obj = set(obj).intersection(FORBIDDEN_SURFACE_KEYS)
        assert not leaked_obj, f"{obj.get('object_id')} has {leaked_obj}"
        assert "surface" not in obj
    pack_props = schema["$defs"]["expression_pack"]["properties"]
    assert "surface" in pack_props
    assert "today_message" not in schema["$defs"]["knowledge_object"]["properties"]


def test_source_corpus_candidate_only():
    schema = json.loads(CORPUS_SCHEMA.read_text(encoding="utf-8"))
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)
    assert len(payload["sources"]) >= 30
    assert all(src["status"] == "candidate" for src in payload["sources"])
    classes = {src["source_class"] for src in payload["sources"]}
    assert classes == {"astronomy", "classical", "traditional", "psychological", "professional"}
    swiss = next(s for s in payload["sources"] if s["source_id"] == "src.astronomy.swiss_ephemeris")
    assert swiss["legal_status"] == "dual_license_astronomy"
    assert swiss["ingest_rule"] == "facts_only"


def test_no_active_meaning_catalog_yet():
    """IL-1 may hold draft objects; nothing is product-active yet."""
    json_files = sorted(p.name for p in RUNTIME.glob("*.json"))
    assert json_files == ["objects_v1.json", "source_corpus_v1.json"], (
        f"unexpected runtime IL files: {json_files}"
    )
    payload = json.loads(OBJECTS.read_text(encoding="utf-8"))
    assert payload["objects"], "IL-1 started: expect at least one draft object"
    assert all(obj["status"] in {"draft", "review"} for obj in payload["objects"])
    assert all(obj["status"] != "active" for obj in payload["objects"])
    for obj in payload["objects"]:
        leaked = set(obj).intersection(FORBIDDEN_SURFACE_KEYS)
        assert not leaked, f"{obj.get('object_id')} has {leaked}"
        assert "surface" not in obj
        assert "today_message" not in obj
        for row in obj["provenance"]:
            assert row["evidence_tier"] != "core"
            assert row["review_status"] != "schema_example"


def test_classical_seven_draft_ledgers():
    object_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, object_schema)
    corpus_ids = {src["source_id"] for src in corpus["sources"]}
    expected = {
        "astro.object.sun",
        "astro.object.moon",
        "astro.object.mercury",
        "astro.object.venus",
        "astro.object.mars",
        "astro.object.jupiter",
        "astro.object.saturn",
    }
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert expected <= set(by_id)
    for object_id in expected:
        claims = json.loads((CLAIMS_DIR / f"{object_id}.json").read_text(encoding="utf-8"))
        jsonschema.validate(claims, claims_schema)
        obj = by_id[object_id]
        assert obj["status"] == "draft"
        assert obj["layer"] == 1
        assert claims["object_id"] == object_id
        assert claims["calc_entity"] == obj["machine_entity_code"]
        used_ids = {row["source_id"] for row in claims["claims"]}
        pending_ids = set(claims["pending_source_ids"])
        assert used_ids <= corpus_ids
        assert pending_ids <= corpus_ids
        assert used_ids.isdisjoint(pending_ids)
        assert "src.classical.ptolemy_tetrabiblos" in used_ids
        assert "src.classical.lilly_christian_astrology" in used_ids
        assert all(row["evidence_tier"] != "core" for row in claims["claims"])
        assert any("CORE cannot be scored" in note for note in claims["gap_notes"])


def test_saturn_claims_not_schema_example():
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    saturn = next(obj for obj in objects["objects"] if obj["object_id"] == "astro.object.saturn")
    assert saturn["function"] != "structure, limits, time, responsibility"
    compared = {row["concept_id"] for row in claims["claims"] if row["review_status"] == "compared"}
    assert {"claim.saturn.cold", "claim.saturn.dry", "claim.saturn.malefic"} <= compared
    moon = json.loads((CLAIMS_DIR / "astro.object.moon.json").read_text(encoding="utf-8"))
    assert any("Temperature conflict" in note for note in moon["gap_notes"])
    mercury = json.loads((CLAIMS_DIR / "astro.object.mercury.json").read_text(encoding="utf-8"))
    assert any("Native-quality conflict" in note for note in mercury["gap_notes"])


def test_houses_and_aspects_from_opened_loci_only():
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    houses = [obj for obj in objects["objects"] if obj["layer"] == 3]
    aspects = [obj for obj in objects["objects"] if obj["layer"] == 4]
    assert {obj["object_id"] for obj in houses} == {f"astro.house.{i:02d}" for i in range(1, 13)}
    assert {obj["object_id"] for obj in aspects} == {
        "astro.aspect.conjunction",
        "astro.aspect.sextile",
        "astro.aspect.square",
        "astro.aspect.trine",
        "astro.aspect.opposition",
    }
    assert not any(obj["type"] == "sign" for obj in objects["objects"])
    assert "astro.object.asc" not in by_id
    assert "astro.object.mc" not in by_id
    for obj in houses:
        used = {row["source_id"] for row in obj["provenance"]}
        assert used == {"src.classical.lilly_christian_astrology"}
        notes = json.loads((CLAIMS_DIR / f"{obj['object_id']}.json").read_text(encoding="utf-8"))["gap_notes"]
        assert any("not Ptolemy+Lilly consensus" in n for n in notes)
    for obj in aspects:
        used = {row["source_id"] for row in obj["provenance"]}
        assert used == {"src.classical.ptolemy_tetrabiblos"}
        assert obj["requires_action"] is False
        notes = json.loads((CLAIMS_DIR / f"{obj['object_id']}.json").read_text(encoding="utf-8"))["gap_notes"]
        assert any("does not establish the property" in n for n in notes)
    square = by_id["astro.aspect.square"]
    assert square["interaction"] == "friction"
    assert square["angle"] == 90


def test_sign_classifications_do_not_invent_layer2_psychology():
    claims = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(claims, schema)
    notes = " ".join(claims["gap_notes"])
    assert "No Layer 2 sign objects yet" in notes
    assert "later interpretive layer" in notes
    assert "Element conflict" in notes
    assert "Mode conflict" in notes
    compared = {row["concept_id"] for row in claims["claims"] if row["review_status"] == "compared"}
    assert "claim.sign.masculine_alternate" in compared
    assert "claim.sign.fire_triangle_elements" not in compared
