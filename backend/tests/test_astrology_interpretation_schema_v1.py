"""Astrology Interpretation Library v1 — schema lock (no active meaning catalog)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

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

LATER_INTERPRETIVE_KEYS = (
    "motivation",
    "expression",
    "strengths",
    "excess",
    "deficiency",
    "behavioral_tendencies",
)

OUTER_MEANING_KEYS = (
    "function",
    "themes",
    "positive_expression",
    "shadow",
    "domains",
    "tempo",
)

OUTER_OBJECT_IDS = (
    "astro.object.uranus",
    "astro.object.neptune",
    "astro.object.pluto",
)

LILLY_SIGN_GRID = {
    "aries": ("cardinal", "fire", "positive"),
    "taurus": ("fixed", "earth", "negative"),
    "gemini": ("mutable", "air", "positive"),
    "cancer": ("cardinal", "water", "negative"),
    "leo": ("fixed", "fire", "positive"),
    "virgo": ("mutable", "earth", "negative"),
    "libra": ("cardinal", "air", "positive"),
    "scorpio": ("fixed", "water", "negative"),
    "sagittarius": ("mutable", "fire", "positive"),
    "capricorn": ("cardinal", "earth", "negative"),
    "aquarius": ("fixed", "air", "positive"),
    "pisces": ("mutable", "water", "negative"),
}

QUALITY_PERSONALITY = (
    "choleric",
    "melancholy",
    "sanguine",
    "phlegmatic",
    "deceitful",
    "idle",
    "violent",
    "luxurious",
    "intemperate",
    "barren",
    "bestial",
    "lascivious",
    "sickly",
    "effeminate",
    "subtle",
)


def _assert_il1_catalog_counts(objects: dict) -> None:
    assert len(objects["objects"]) == 36
    by_type: dict[str, list] = {}
    for obj in objects["objects"]:
        by_type.setdefault(obj["type"], []).append(obj)
    assert len(by_type["celestial_object"]) == 7
    assert len(by_type["sign"]) == 12
    assert len(by_type["house"]) == 12
    assert len(by_type["aspect"]) == 5
    assert all(obj["status"] != "active" for obj in objects["objects"])
    for sign in by_type["sign"]:
        assert sign["status"] == "draft"
        assert sign["layer"] == 2
        for key in LATER_INTERPRETIVE_KEYS:
            assert key not in sign, sign["object_id"]


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
    assert classes == {
        "astronomy",
        "classical",
        "traditional",
        "psychological",
        "humanistic",
        "professional",
    }
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
        assert "src.classical.valens_anthologies" in used_ids
        assert all(row["evidence_tier"] != "core" for row in claims["claims"])
        assert any("CORE cannot be scored" in note for note in claims["gap_notes"])


def test_saturn_claims_not_schema_example():
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    saturn = next(obj for obj in objects["objects"] if obj["object_id"] == "astro.object.saturn")
    assert saturn["function"] != "structure, limits, time, responsibility"
    compared = {row["concept_id"] for row in claims["claims"] if row["review_status"] == "compared"}
    assert {"claim.saturn.cold", "claim.saturn.dry", "claim.saturn.malefic", "claim.saturn.solitariness"} <= compared
    malefic_ids = {row["source_id"] for row in claims["claims"] if row["concept_id"] == "claim.saturn.malefic"}
    assert "src.classical.valens_anthologies" not in malefic_ids
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
    _assert_il1_catalog_counts(objects)
    assert "astro.object.asc" not in by_id
    assert "astro.object.mc" not in by_id
    for obj in houses:
        used = {row["source_id"] for row in obj["provenance"]}
        notes = json.loads((CLAIMS_DIR / f"{obj['object_id']}.json").read_text(encoding="utf-8"))["gap_notes"]
        assert "src.classical.lilly_christian_astrology" in used
        assert "src.classical.valens_anthologies" in used
        assert "src.classical.ptolemy_tetrabiblos" not in used
        assert any("not Ptolemy+Lilly consensus" in n for n in notes)
        assert any("derived-place" in n for n in notes)
        if obj["object_id"] in {"astro.house.01", "astro.house.06", "astro.house.07", "astro.house.12"}:
            assert "src.traditional.houlding_houses" in used
        else:
            assert "src.traditional.houlding_houses" not in used
    for obj in aspects:
        used = {row["source_id"] for row in obj["provenance"]}
        assert used >= {
            "src.classical.ptolemy_tetrabiblos",
            "src.classical.lilly_christian_astrology",
            "src.traditional.houlding_aspects",
        }
        assert obj["requires_action"] is False
        claims = json.loads((CLAIMS_DIR / f"{obj['object_id']}.json").read_text(encoding="utf-8"))
        assert "src.classical.lilly_christian_astrology" not in claims["pending_source_ids"]
        notes = claims["gap_notes"]
        assert any("does not establish the property" in n for n in notes)
        compared_angles = [
            row for row in claims["claims"]
            if row["field"] == "angle" and row["review_status"] == "compared"
        ]
        assert {row["source_id"] for row in compared_angles} == {
            "src.classical.ptolemy_tetrabiblos",
            "src.classical.lilly_christian_astrology",
        }
        assert all(row["evidence_tier"] != "core" for row in claims["claims"] if row["field"] == "interaction")
    square = by_id["astro.aspect.square"]
    assert square["interaction"] == "friction"
    assert square["angle"] == 90


def test_activation_gates_block_active_ambiguity():
    """Unevidenced boolean and Layer 5 candidates must not ship as active."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    ra = schema["$defs"]["knowledge_object"]["properties"]["requires_action"]
    assert ra["type"] == "boolean"
    assert "unevidenced" in ra["description"]
    assert "active" in ra["description"]
    curation = schema["$defs"]["knowledge_object"]["properties"]["curation_reason"]
    assert "candidates" in curation["description"]
    for obj in objects["objects"]:
        if obj.get("type") == "aspect" and obj.get("requires_action") is False:
            assert obj["status"] != "active", obj["object_id"]
        if obj.get("curation_reason") == "non_compositional":
            assert obj["status"] != "active", obj["object_id"]
            assert obj["layer"] == 5


def test_sign_classifications_do_not_invent_layer2_psychology():
    claims = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(claims, schema)
    notes = " ".join(claims["gap_notes"])
    assert "1.3.68" in notes
    assert "optional on IL-1 draft" in notes
    assert "Element conflict" in notes
    assert "Mode conflict" in notes
    compared = {row["concept_id"] for row in claims["claims"] if row["review_status"] == "compared"}
    assert "claim.sign.masculine_alternate" in compared
    assert "claim.sign.commanding_summer_semicircle" in compared
    assert "claim.sign.fire_triangle_elements" not in compared
    assert "claim.sign.commanding_equinox_pairs" not in compared
    assert "claim.sign.beholding_tropical_distance" not in compared
    assert "claim.sign.antiscion_tropical_distance" not in compared
    assert "claim.sign.aries.valens_fiery" not in compared
    notes_joined = " ".join(claims["gap_notes"])
    assert "pair-relation" in notes_joined
    assert "Antiscion" in notes_joined
    assert "watery" in notes_joined
    for sign in (
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ):
        sign_claims = json.loads((CLAIMS_DIR / f"astro.sign.{sign}.json").read_text(encoding="utf-8"))
        jsonschema.validate(sign_claims, schema)
        used = {row["source_id"] for row in sign_claims["claims"]}
        assert "src.classical.lilly_christian_astrology" in used
        if sign == "aries":
            assert "src.classical.valens_anthologies" in used
        else:
            assert used == {"src.classical.lilly_christian_astrology"}
        assert all(row["evidence_tier"] != "core" for row in sign_claims["claims"])
        assert any("1.3.68 classification-only draft" in n for n in sign_claims["gap_notes"])
        assert not any("fiery/cardinal/equinoctial here" in n for n in sign_claims["gap_notes"])


def test_valens_and_lilly19_collisions_not_averaged():
    """Opened Valens / Lilly I.19 must log collisions, not rewrite draft meaning slots."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    saturn = by_id["astro.object.saturn"]
    assert saturn["function"] == "cooling quality operating by distance from heat"
    assert saturn["status"] == "draft"
    saturn_claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    assert any("cold and moisture" in n.lower() or "cold AND moisture" in n for n in saturn_claims["gap_notes"])
    house01 = by_id["astro.house.01"]
    assert house01["domain"] == "life, stature, and the querent's person"
    house07 = json.loads((CLAIMS_DIR / "astro.house.07.json").read_text(encoding="utf-8"))
    compared07 = {row["concept_id"] for row in house07["claims"] if row["review_status"] == "compared"}
    assert "claim.house.07.marriage" in compared07
    assert "claim.house.07.domain" not in compared07
    square = by_id["astro.aspect.square"]
    assert square["interaction"] == "friction"
    assert square["requires_action"] is False
    assert square["status"] != "active"
    square_claims = json.loads((CLAIMS_DIR / "astro.aspect.square.json").read_text(encoding="utf-8"))
    assert any(row["concept_id"] == "claim.aspect.square.imperfect_enmity" for row in square_claims["claims"])
    assert any("moiet" in n.lower() for n in square_claims["gap_notes"])
    _assert_il1_catalog_counts(objects)


def test_houlding_first_traditional_class_not_averaged():
    """Living-traditional Houlding is a new school_class; it must not rewrite drafts or score CORE."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.house.01"]["domain"] == "life, stature, and the querent's person"
    assert by_id["astro.aspect.square"]["interaction"] == "friction"
    h01 = json.loads((CLAIMS_DIR / "astro.house.01.json").read_text(encoding="utf-8"))
    life = [r for r in h01["claims"] if r["concept_id"] == "claim.house.01.life"]
    assert {r["source_class"] for r in life} == {"classical", "traditional"}
    assert all(r["evidence_tier"] != "core" for r in h01["claims"])
    assert any("personality" in n.lower() for n in h01["gap_notes"])
    h06 = json.loads((CLAIMS_DIR / "astro.house.06.json").read_text(encoding="utf-8"))
    servants = [r for r in h06["claims"] if r["concept_id"] == "claim.house.06.servants"]
    assert {r["source_id"] for r in servants} == {
        "src.classical.lilly_christian_astrology",
        "src.traditional.houlding_houses",
    }
    assert all(r["review_status"] == "compared" for r in servants)
    h07 = json.loads((CLAIMS_DIR / "astro.house.07.json").read_text(encoding="utf-8"))
    assert any(r["concept_id"] == "claim.house.07.known_enemies_rule" for r in h07["claims"])
    square = json.loads((CLAIMS_DIR / "astro.aspect.square.json").read_text(encoding="utf-8"))
    not_bad = next(r for r in square["claims"] if r["concept_id"] == "claim.aspect.square.not_simply_bad")
    assert not_bad["evidence_tier"] == "school_specific"
    orbs = [r for r in square["claims"] if r["concept_id"] == "claim.aspect.orbs_planetary"]
    assert {r["source_class"] for r in orbs} == {"classical", "traditional"}
    assert all(r["evidence_tier"] != "core" for r in square["claims"])
    classes = {r["source_class"] for obj in objects["objects"] for r in obj["provenance"]}
    assert "traditional" in classes
    assert all(obj["status"] != "active" for obj in objects["objects"])


def test_greene_first_psychological_class_not_averaged():
    """Opened Greene Introduction is a new school_class; it must not rewrite Saturn or score CORE."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    saturn = next(obj for obj in objects["objects"] if obj["object_id"] == "astro.object.saturn")
    claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    assert saturn["function"] == "cooling quality operating by distance from heat"
    assert saturn["themes"] == ["cold", "dryness", "slowness", "solitude", "austerity"]
    assert saturn["status"] == "draft"
    used = {row["source_id"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    assert "src.psychological.greene_saturn" in used
    assert "src.psychological.greene_saturn" not in pending
    psychic = next(row for row in claims["claims"] if row["concept_id"] == "claim.saturn.psychic_process")
    pain = next(row for row in claims["claims"] if row["concept_id"] == "claim.saturn.pain_self_discovery")
    assert psychic["source_class"] == "psychological"
    assert psychic["evidence_tier"] == "school_specific"
    assert psychic["review_status"] == "extracted"
    assert pain["evidence_tier"] == "school_specific"
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    notes = " ".join(claims["gap_notes"]).lower()
    assert "psychic process" in notes or "psychic-process" in notes
    assert "structure" in notes
    assert "layer 5" in notes
    provenance_classes = {row["source_class"] for row in saturn["provenance"]}
    assert "psychological" in provenance_classes
    assert not any("structure" in theme for theme in saturn["themes"])


def test_houlding_saturn_article_not_averaged():
    """Houlding Saturn article adds traditional lemmas beside cold/dry; it must not rewrite function or score CORE."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    saturn = next(obj for obj in objects["objects"] if obj["object_id"] == "astro.object.saturn")
    claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    assert saturn["function"] == "cooling quality operating by distance from heat"
    assert saturn["themes"] == ["cold", "dryness", "slowness", "solitude", "austerity"]
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.traditional.houlding_saturn" in used
    boundary = next(row for row in claims["claims"] if row["concept_id"] == "claim.saturn.personal_boundary")
    mature = next(row for row in claims["claims"] if row["concept_id"] == "claim.saturn.mature_through_constraint")
    assert boundary["source_class"] == "traditional"
    assert boundary["evidence_tier"] == "school_specific"
    assert mature["evidence_tier"] == "school_specific"
    cold_classes = {
        row["source_class"] for row in claims["claims"] if row["concept_id"] == "claim.saturn.cold"
    }
    assert cold_classes == {"classical", "traditional"}
    assert all(row["review_status"] == "compared" for row in claims["claims"] if row["concept_id"] == "claim.saturn.cold")
    notes = " ".join(claims["gap_notes"]).lower()
    assert "t1-t4" in notes or "t1–t4" in notes
    assert "structure-setting" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    assert "boundary" not in saturn["function"]
    assert "structure" not in saturn["function"]


def test_watters_greene_luminaries_not_averaged():
    """Watters 2003 is modern practical parked as professional; Greene stays psychological school_specific."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    watters = next(src for src in corpus["sources"] if src["source_id"] == "src.professional.watters_today")
    assert watters["source_class"] == "professional"
    assert watters["role"] == "bridge"
    functions = {
        "astro.object.sun": "heating quality with moderate dryness",
        "astro.object.moon": "moistening quality acting close to earth and bodies",
        "astro.object.mercury": "convertible quality taking the nature of what it joins",
        "astro.object.venus": "moist temperate quality disposed to pleasure and company",
        "astro.object.mars": "heating and drying quality that contends",
        "astro.object.jupiter": "temperate warming and moistening quality",
        "astro.object.saturn": "cooling quality operating by distance from heat",
    }
    for object_id, function in functions.items():
        assert by_id[object_id]["function"] == function
        assert by_id[object_id]["status"] == "draft"
    planets = (
        "astro.object.sun",
        "astro.object.moon",
        "astro.object.mercury",
        "astro.object.venus",
        "astro.object.mars",
        "astro.object.jupiter",
    )
    for object_id in planets:
        claims = json.loads((CLAIMS_DIR / f"{object_id}.json").read_text(encoding="utf-8"))
        obj = by_id[object_id]
        used = {row["source_id"] for row in claims["claims"]}
        pending = set(claims["pending_source_ids"])
        assert "src.professional.watters_today" in used
        assert "src.professional.watters_today" not in pending
        watters_rows = [row for row in claims["claims"] if row["source_id"] == "src.professional.watters_today"]
        assert watters_rows
        assert all(row["source_class"] == "professional" for row in watters_rows)
        assert all(row["evidence_tier"] == "school_specific" for row in watters_rows)
        assert all(row["review_status"] == "extracted" for row in watters_rows)
        assert all(row["school"] == "modern_general_practical" for row in watters_rows)
        assert not any("body_" in row["concept_id"] for row in obj["provenance"])
        assert not any("fertility" in row["concept_id"] or "health" in row["concept_id"] for row in obj["provenance"])
        domains_text = json.dumps(obj["domains"]).lower()
        assert "gynecolog" not in domains_text
        assert "diabetes" not in domains_text
        assert "sciatic" not in domains_text
        assert "blood sugar" not in domains_text
        assert all(row["evidence_tier"] != "core" for row in claims["claims"])
        if object_id in ("astro.object.venus", "astro.object.mars", "astro.object.jupiter"):
            assert "src.professional.hand_horoscope_symbols" in used
            assert "src.professional.hand_horoscope_symbols" not in pending
        else:
            assert "src.professional.hand_horoscope_symbols" in pending
        notes = " ".join(claims["gap_notes"]).lower()
        assert "modern general practical" in notes or "classification gap" in notes
        assert all("do_not_compare_with" not in row for row in claims["claims"])
        assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
        assert all("classification_gap" not in row for row in claims["claims"])
        assert "modern_general_practical" not in {row["source_class"] for row in claims["claims"]}
        assert "modern_psychological" not in {row["source_class"] for row in claims["claims"]}
    sun_claims = json.loads((CLAIMS_DIR / "astro.object.sun.json").read_text(encoding="utf-8"))
    moon_claims = json.loads((CLAIMS_DIR / "astro.object.moon.json").read_text(encoding="utf-8"))
    sun_ids = {row["concept_id"] for row in sun_claims["claims"]}
    assert "claim.sun.essential_self" in sun_ids
    assert "claim.sun.becoming" in sun_ids
    assert "claim.sun.father_signifier_female_chart" in sun_ids
    assert "claim.sun.attraction_type_female_chart" in sun_ids
    assert "claim.sun.strong_sun_traits" in sun_ids
    assert "claim.sun.strong_sun_health" in sun_ids
    assert "claim.sun.annual_orbit_fact" in sun_ids
    assert "claim.sun.solar_return_symbolism" in sun_ids
    assert "claim.sun.essential_self_and_becoming" not in sun_ids
    assert "claim.sun.solar_consciousness_eternal" in sun_ids
    solar = next(row for row in sun_claims["claims"] if row["concept_id"] == "claim.sun.solar_consciousness_eternal")
    assert solar["source_class"] == "psychological"
    assert solar["evidence_tier"] == "school_specific"
    assert solar["source_id"] == "src.psychological.greene_luminaries"
    rudhyar_sun = [row for row in sun_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_sun) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_sun)
    assert all(row["school"] == "humanistic" for row in rudhyar_sun)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_sun)
    assert all(row["review_status"] == "extracted" for row in rudhyar_sun)
    assert {row["concept_id"] for row in rudhyar_sun} == {
        "claim.sun.rudhyar_heart_vs_photosphere",
        "claim.sun.rudhyar_light_as_integration",
        "claim.sun.rudhyar_light_vs_life",
        "claim.sun.rudhyar_light_becomes_life",
        "claim.sun.rudhyar_inner_sun",
        "claim.sun.rudhyar_changeless_heart",
        "claim.sun.rudhyar_song_of_selfhood",
        "claim.sun.rudhyar_will",
        "claim.sun.rudhyar_sun_jupiter_saturn",
        "claim.sun.rudhyar_our_source",
        "claim.sun.rudhyar_immanent_god",
        "claim.sun.rudhyar_light_bearers",
    }
    integration = next(row for row in rudhyar_sun if row["concept_id"] == "claim.sun.rudhyar_light_as_integration")
    assert integration["field"] == "function"
    assert "integration" in integration["normalized_claim"].lower()
    assert "essential self" not in integration["normalized_claim"].lower()
    assert "solar consciousness" not in integration["normalized_claim"].lower()
    assert all("essential self" not in row["normalized_claim"].lower() for row in rudhyar_sun)
    assert all("solar consciousness" not in row["normalized_claim"].lower() for row in rudhyar_sun)
    assert "src.humanistic.rudhyar_new_mansions" not in set(sun_claims["pending_source_ids"])
    assert "src.psychological.greene_apollos_chariot" in set(sun_claims["pending_source_ids"])
    assert "src.psychological.greene_apollon_sun" not in set(sun_claims["pending_source_ids"])
    assert "src.professional.hand_horoscope_symbols" in set(sun_claims["pending_source_ids"])
    assert any("song of light" in note.lower() for note in sun_claims["gap_notes"])
    assert any("apollon" in note.lower() and "not this locus" in note.lower() for note in sun_claims["gap_notes"])
    assert any("apollo's chariot" in note.lower() or "apollos chariot" in note.lower() for note in sun_claims["gap_notes"])
    assert any("1.3.50" in note for note in sun_claims["gap_notes"])
    apollon_sun = [row for row in sun_claims["claims"] if row["source_id"] == "src.psychological.greene_apollon_sun"]
    assert len(apollon_sun) == 10
    assert all(row["source_class"] == "psychological" for row in apollon_sun)
    assert all(row["school"] == "psychological_jungian" for row in apollon_sun)
    assert all(row["evidence_tier"] == "school_specific" for row in apollon_sun)
    assert all(row["review_status"] == "extracted" for row in apollon_sun)
    assert {row["concept_id"] for row in apollon_sun} == {
        "claim.sun.greene_apollon_carrier",
        "claim.sun.greene_apollon_inner_light",
        "claim.sun.greene_apollon_core_identity",
        "claim.sun.greene_apollon_family_curse",
        "claim.sun.greene_apollon_chart_centre",
        "claim.sun.greene_apollon_cosmocrator",
        "claim.sun.greene_apollon_vocation",
        "claim.sun.greene_apollon_healer_will",
        "claim.sun.greene_apollon_unexpressed",
        "claim.sun.greene_apollon_aloneness_price",
    }
    carrier = next(row for row in apollon_sun if row["concept_id"] == "claim.sun.greene_apollon_carrier")
    assert carrier["field"] == "function"
    assert "carrier" in carrier["normalized_claim"].lower()
    assert all("essential self" not in row["normalized_claim"].lower() for row in apollon_sun)
    assert all("solar consciousness" not in row["normalized_claim"].lower() for row in apollon_sun)
    assert all("integration" not in row["normalized_claim"].lower() for row in apollon_sun)
    moon_ids = {row["concept_id"] for row in moon_claims["claims"]}
    assert "claim.moon.earth_mother_embodiment" in moon_ids
    assert "claim.moon.embodied_life_as_numinous" in moon_ids
    assert "claim.moon.night_world_function" in moon_ids
    assert "claim.moon.emotion_habit_function" in moon_ids
    rudhyar_moon = [row for row in moon_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_moon) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_moon)
    assert all(row["school"] == "humanistic" for row in rudhyar_moon)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_moon)
    assert all(row["review_status"] == "extracted" for row in rudhyar_moon)
    assert {row["concept_id"] for row in rudhyar_moon} == {
        "claim.moon.rudhyar_song_of_life",
        "claim.moon.rudhyar_current_of_induction",
        "claim.moon.rudhyar_resurrected_past",
        "claim.moon.rudhyar_not_dead_weight",
        "claim.moon.rudhyar_not_evil",
        "claim.moon.rudhyar_congregation",
        "claim.moon.rudhyar_raw_materials",
        "claim.moon.rudhyar_alchemical_vessel",
        "claim.moon.rudhyar_gestation_individuation",
        "claim.moon.rudhyar_four_times_seven",
        "claim.moon.rudhyar_life_tides",
        "claim.moon.rudhyar_old_vs_new_song",
    }
    song = next(row for row in rudhyar_moon if row["concept_id"] == "claim.moon.rudhyar_song_of_life")
    assert song["field"] == "function"
    assert "song of life" in song["normalized_claim"].lower()
    assert "night-world" not in song["normalized_claim"].lower()
    assert "embodiment" not in song["normalized_claim"].lower()
    assert all("night-world" not in row["normalized_claim"].lower() for row in rudhyar_moon)
    assert all("gaia" not in row["normalized_claim"].lower() for row in rudhyar_moon)
    assert "src.humanistic.rudhyar_new_mansions" not in set(moon_claims["pending_source_ids"])
    assert "src.psychological.costello_astrological_moon" in set(moon_claims["pending_source_ids"])
    assert "src.professional.hand_horoscope_symbols" in set(moon_claims["pending_source_ids"])
    assert any("song of life" in note.lower() for note in moon_claims["gap_notes"])
    assert any("costello" in note.lower() and "need_owner" in note.lower() for note in moon_claims["gap_notes"])
    assert any("1.3.51" in note for note in moon_claims["gap_notes"])
    moon_psych = [row for row in moon_claims["claims"] if row["source_class"] == "psychological"]
    assert len(moon_psych) == 2
    assert all(row["source_id"] == "src.psychological.greene_luminaries" for row in moon_psych)
    venus_ids = {
        row["concept_id"]
        for row in json.loads((CLAIMS_DIR / "astro.object.venus.json").read_text(encoding="utf-8"))["claims"]
    }
    assert "claim.venus.love_desire_function" in venus_ids
    assert "claim.venus.venus_mercury_contrast" in venus_ids
    assert "claim.venus.hand_noncoercive_bonding" in venus_ids
    assert "claim.venus.hand_complementary_union" in venus_ids
    assert "claim.venus.hand_love_as_bonding" in venus_ids
    assert "claim.venus.hand_relationship_self_expression" in venus_ids
    assert "claim.venus.hand_beauty_harmony" in venus_ids
    assert "claim.venus.hand_creation" in venus_ids
    assert "claim.venus.hand_spontaneous_attraction" in venus_ids
    assert "claim.venus.hand_mars_polarity" in venus_ids
    assert "claim.venus.hand_excess_loss_of_separateness" in venus_ids
    assert "claim.venus.hand_mother_love" in venus_ids
    assert "claim.venus.hand_flashy_aesthetic_shadow" in venus_ids
    assert "claim.venus.hand_venusian_traits" in venus_ids
    assert "claim.venus.rudhyar_inward_way" in venus_ids
    assert "claim.venus.rudhyar_quintessence" in venus_ids
    venus_claims = json.loads((CLAIMS_DIR / "astro.object.venus.json").read_text(encoding="utf-8"))
    assert "src.psychological.greene_inner_planets" in set(venus_claims["pending_source_ids"])
    assert "src.psychological.greene_inner_planets" not in {row["source_id"] for row in venus_claims["claims"]}
    assert "src.professional.hand_horoscope_symbols" not in set(venus_claims["pending_source_ids"])
    assert "src.humanistic.rudhyar_new_mansions" not in set(venus_claims["pending_source_ids"])
    hand_venus = [row for row in venus_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_venus) == 12
    assert all(row["source_class"] == "professional" for row in hand_venus)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_venus)
    assert all(row["school"] == "modern_professional" for row in hand_venus)
    assert all("runtime_semantic_candidate" not in row for row in hand_venus)
    rudhyar_venus = [row for row in venus_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_venus) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_venus)
    assert all(row["school"] == "humanistic" for row in rudhyar_venus)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_venus)
    assert all(row["review_status"] == "extracted" for row in rudhyar_venus)
    inward = next(row for row in rudhyar_venus if row["concept_id"] == "claim.venus.rudhyar_inward_way")
    assert inward["field"] == "function"
    assert "inward" in inward["normalized_claim"].lower()
    assert "love/desire" not in inward["normalized_claim"].lower()
    assert "bonding" not in inward["normalized_claim"].lower()
    assert "harlot" not in inward["normalized_claim"].lower()
    thyroid = next(row for row in rudhyar_venus if row["concept_id"] == "claim.venus.rudhyar_thyroid_alchemy")
    assert thyroid["field"] == "domains"
    assert "thyroid" not in by_id["astro.object.venus"].get("domains", {})
    assert "moist temperate quality disposed to pleasure and company" == by_id["astro.object.venus"]["function"]
    assert "claim.venus.hand_noncoercive_bonding" in {row["concept_id"] for row in by_id["astro.object.venus"]["provenance"]}
    assert "claim.venus.rudhyar_inward_way" in {row["concept_id"] for row in by_id["astro.object.venus"]["provenance"]}
    assert "voluntary" not in by_id["astro.object.venus"]["function"]
    assert "inward" not in by_id["astro.object.venus"]["function"]
    assert any("p.69" in note and "not opened" in note.lower() for note in venus_claims["gap_notes"])
    assert any("carolina de pedro" in note.lower() for note in venus_claims["gap_notes"])
    assert any("humanistic" in note.lower() and "rudhyar" in note.lower() for note in venus_claims["gap_notes"])
    assert any("1.3.41" in note for note in venus_claims["gap_notes"])
    assert any("1.3.48" in note for note in venus_claims["gap_notes"])
    assert any("sullivan" in note.lower() for note in venus_claims["gap_notes"])
    assert any("mythic astrology" in note.lower() for note in venus_claims["gap_notes"])
    assert "src.psychological.sullivan_venus_jupiter" not in set(venus_claims["pending_source_ids"])
    assert "src.psychological.greene_inner_planets" in set(venus_claims["pending_source_ids"])
    assert "src.psychological.greene_mythic_astrology" in set(venus_claims["pending_source_ids"])
    sullivan_venus = [
        row for row in venus_claims["claims"] if row["source_id"] == "src.psychological.sullivan_venus_jupiter"
    ]
    assert len(sullivan_venus) == 9
    assert all(row["source_class"] == "psychological" for row in sullivan_venus)
    assert all(row["school"] == "psychological_cpa" for row in sullivan_venus)
    assert all(row["evidence_tier"] == "school_specific" for row in sullivan_venus)
    assert all(row["review_status"] == "extracted" for row in sullivan_venus)
    assert {row["concept_id"] for row in sullivan_venus} == {
        "claim.venus.sullivan_channel_for_eros",
        "claim.venus.sullivan_dual_goddess",
        "claim.venus.sullivan_bridge_ideal_real",
        "claim.venus.sullivan_same_impulse",
        "claim.venus.sullivan_saturn_midwife",
        "claim.venus.sullivan_eros_amok",
        "claim.venus.sullivan_creativity_discovery",
        "claim.venus.sullivan_not_only_fine_arts",
        "claim.venus.sullivan_precreative_chaos",
    }
    channel = next(row for row in sullivan_venus if row["concept_id"] == "claim.venus.sullivan_channel_for_eros")
    assert channel["field"] == "function"
    assert "channel" in channel["normalized_claim"].lower()
    assert "eros" in channel["normalized_claim"].lower()
    assert all("bonding" not in row["normalized_claim"].lower() for row in sullivan_venus)
    assert all("harlot" not in row["normalized_claim"].lower() for row in sullivan_venus)
    assert all("love/desire" not in row["normalized_claim"].lower() for row in sullivan_venus)
    assert all("inward way" not in row["normalized_claim"].lower() for row in sullivan_venus)
    assert "claim.venus.sullivan_channel_for_eros" in {row["concept_id"] for row in by_id["astro.object.venus"]["provenance"]}
    assert "moist temperate quality disposed to pleasure and company" == by_id["astro.object.venus"]["function"]
    assert "channel" not in by_id["astro.object.venus"]["function"]
    assert "eros" not in by_id["astro.object.venus"]["function"].lower()
    mercury_claims = json.loads((CLAIMS_DIR / "astro.object.mercury.json").read_text(encoding="utf-8"))
    mercury_ids = {row["concept_id"] for row in mercury_claims["claims"]}
    assert "claim.mercury.mind_curiosity" in mercury_ids
    assert "claim.mercury.mind_breadth_over_depth" in mercury_ids
    assert "claim.mercury.hermes_spontaneity" in mercury_ids
    assert "src.psychological.greene_inner_planets" in {row["source_id"] for row in mercury_claims["claims"]}
    assert "src.psychological.greene_inner_planets" not in set(mercury_claims["pending_source_ids"])
    hermes = next(row for row in mercury_claims["claims"] if row["concept_id"] == "claim.mercury.hermes_spontaneity")
    assert hermes["source_class"] == "psychological"
    assert hermes["evidence_tier"] == "school_specific"
    rudhyar_mercury = [row for row in mercury_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_mercury) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_mercury)
    assert all(row["school"] == "humanistic" for row in rudhyar_mercury)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_mercury)
    assert {row["concept_id"] for row in rudhyar_mercury} == {
        "claim.mercury.rudhyar_weaver",
        "claim.mercury.rudhyar_saturn_vs_mercury",
        "claim.mercury.rudhyar_nervous_system",
        "claim.mercury.rudhyar_lines_of_communication",
        "claim.mercury.rudhyar_servant_of_jupiter",
        "claim.mercury.rudhyar_liberation_from_saturn",
        "claim.mercury.rudhyar_hand",
        "claim.mercury.rudhyar_two_planes",
        "claim.mercury.rudhyar_operative_wholeness",
        "claim.mercury.rudhyar_black_magician",
        "claim.mercury.rudhyar_caduceus",
        "claim.mercury.rudhyar_cut_in_twain",
    }
    weaver = next(row for row in rudhyar_mercury if row["concept_id"] == "claim.mercury.rudhyar_weaver")
    assert weaver["field"] == "function"
    assert "weaver" in weaver["normalized_claim"].lower()
    assert "spontaneity" not in weaver["normalized_claim"].lower()
    assert "curiosity" not in weaver["normalized_claim"].lower()
    assert all("spontaneity" not in row["normalized_claim"].lower() for row in rudhyar_mercury)
    assert all("hermes" not in row["normalized_claim"].lower() for row in rudhyar_mercury)
    assert "src.humanistic.rudhyar_new_mansions" not in set(mercury_claims["pending_source_ids"])
    assert "src.professional.hand_horoscope_symbols" in set(mercury_claims["pending_source_ids"])
    assert any("weaver" in note.lower() for note in mercury_claims["gap_notes"])
    assert any("humanistic" in note.lower() and "rudhyar" in note.lower() for note in mercury_claims["gap_notes"])
    assert any("1.3.52" in note for note in mercury_claims["gap_notes"])
    mercury_psych = [row for row in mercury_claims["claims"] if row["source_class"] == "psychological"]
    assert len(mercury_psych) == 1
    assert mercury_psych[0]["concept_id"] == "claim.mercury.hermes_spontaneity"
    for object_id in ("astro.object.venus", "astro.object.mars", "astro.object.jupiter"):
        claims = json.loads((CLAIMS_DIR / f"{object_id}.json").read_text(encoding="utf-8"))
        used = {row["source_id"] for row in claims["claims"]}
        assert "src.psychological.greene_luminaries" not in used
        assert "src.psychological.greene_inner_planets" not in used
    sun = by_id["astro.object.sun"]
    moon = by_id["astro.object.moon"]
    mercury = by_id["astro.object.mercury"]
    assert "essential self" not in sun["function"]
    assert "solar consciousness" not in sun["function"]
    assert "integration" not in sun["function"]
    assert "heart of the sun" not in sun["function"]
    assert "will" not in sun["function"]
    assert "carrier" not in sun["function"]
    assert "cosmocrator" not in sun["function"]
    assert "heating quality with moderate dryness" == sun["function"]
    domains_text = json.dumps(sun["domains"]).lower()
    assert "endocrine" not in domains_text
    assert "nerve" not in domains_text
    assert "unconscious" not in moon["function"]
    assert "embodiment" not in moon["function"]
    assert "song of life" not in moon["function"]
    assert "raw" not in moon["function"]
    moon_domains = json.dumps(moon["domains"]).lower()
    assert "womb" not in moon_domains
    assert "alchemical" not in moon_domains
    assert "spontaneity" not in mercury["function"]
    assert "weaver" not in mercury["function"]
    assert "wholeness" not in mercury["function"]
    assert "nervous" not in mercury["function"]
    mercury_domains = json.dumps(mercury["domains"]).lower()
    assert "nadi" not in mercury_domains
    assert "kundalini" not in mercury_domains
    assert "nervous" not in mercury_domains
    sun_prov = {row["concept_id"] for row in sun["provenance"]}
    moon_prov = {row["concept_id"] for row in moon["provenance"]}
    mercury_prov = {row["concept_id"] for row in mercury["provenance"]}
    assert "claim.sun.essential_self" in sun_prov
    assert "claim.sun.solar_consciousness_eternal" in sun_prov
    assert "claim.sun.rudhyar_light_as_integration" in sun_prov
    assert "claim.sun.greene_apollon_carrier" in sun_prov
    assert "claim.moon.night_world_function" in moon_prov
    assert "claim.moon.earth_mother_embodiment" in moon_prov
    assert "claim.moon.rudhyar_song_of_life" in moon_prov
    assert "claim.mercury.mind_curiosity" in mercury_prov
    assert "claim.mercury.hermes_spontaneity" in mercury_prov
    assert "claim.mercury.rudhyar_weaver" in mercury_prov
    inner = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_inner_planets")
    assert inner["source_class"] == "psychological"
    assert "1.3.52" in inner["notes"]
    assert "1.3.54" in inner["notes"]
    assert "same-author" in inner["notes"].lower()
    sullivan = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.sullivan_venus_jupiter")
    assert sullivan["source_class"] == "psychological"
    assert sullivan["status"] == "candidate"
    assert sullivan["legal_status"] == "copyrighted_site"
    assert "unread" in sullivan["notes"].lower()
    assert "1.3.41" in sullivan["notes"]
    assert "1.3.48" in sullivan["notes"]
    assert "ingested" in sullivan["notes"].lower()
    mythic = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_mythic_astrology")
    assert mythic["source_class"] == "psychological"
    assert mythic["status"] == "candidate"
    assert "not ingested" in mythic["notes"].lower()
    assert "1.3.41" in mythic["notes"]
    assert "1.3.42" in mythic["notes"]
    assert "1.3.43" in mythic["notes"]
    assert "1.3.44" in mythic["notes"]
    assert "1.3.45" in mythic["notes"]
    assert "1.3.46" in mythic["notes"]
    assert "1.3.48" in mythic["notes"]
    assert "1.3.49" in mythic["notes"]
    assert "1.3.51" in mythic["notes"]
    assert "1.3.52" in mythic["notes"]
    assert "1.3.53" in mythic["notes"]
    assert "1.3.54" in mythic["notes"]
    art_fire = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_art_of_stealing_fire")
    assert art_fire["source_class"] == "psychological"
    assert art_fire["status"] == "candidate"
    assert "not a substitute" in art_fire["notes"].lower()
    tarnas = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.tarnas_prometheus")
    assert tarnas["source_class"] == "psychological"
    assert tarnas["status"] == "candidate"
    assert "unread" in tarnas["notes"].lower()
    tarnas_intro = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.tarnas_archetypal_intro"
    )
    assert tarnas_intro["source_class"] == "psychological"
    assert tarnas_intro["status"] == "candidate"
    assert "1.3.46" in tarnas_intro["notes"]
    assert "1.3.47" in tarnas_intro["notes"]
    assert "1.3.53" in tarnas_intro["notes"]
    assert "1.3.54" in tarnas_intro["notes"]
    assert "ingested" in tarnas_intro["notes"].lower()
    assert "not prometheus the awakener" in tarnas_intro["notes"].lower() or "not this book" in tarnas["notes"].lower()
    uranus_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_uranus_cpa")
    assert uranus_cpa["status"] == "candidate"
    assert "1.3.43" in uranus_cpa["notes"]
    mars_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_mars_cpa")
    assert mars_cpa["source_class"] == "psychological"
    assert mars_cpa["status"] == "candidate"
    assert "1.3.42" in mars_cpa["notes"]
    assert "1.3.49" in mars_cpa["notes"]
    assert "1.3.54" in mars_cpa["notes"]
    assert "transcript" in mars_cpa["notes"].lower()
    bell = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.bell_mars_quartet")
    assert bell["source_class"] == "psychological"
    assert bell["status"] == "candidate"
    assert "1.3.42" in bell["notes"]
    assert "1.3.49" in bell["notes"]
    assert "1.3.54" in bell["notes"]
    assert "1.3.55" in bell["notes"]
    mars_claims = json.loads((CLAIMS_DIR / "astro.object.mars.json").read_text(encoding="utf-8"))
    mars_ids = {row["concept_id"] for row in mars_claims["claims"]}
    assert "claim.mars.hand_survival_energy" in mars_ids
    assert "claim.mars.hand_individuality" in mars_ids
    assert "claim.mars.hand_identification" in mars_ids
    assert "claim.mars.hand_effective_action" in mars_ids
    assert "claim.mars.hand_conflict" in mars_ids
    assert "claim.mars.hand_excess_aggression" in mars_ids
    assert "claim.mars.hand_venus_polarity" in mars_ids
    assert "claim.mars.hand_individuation_enables_love" in mars_ids
    assert "claim.mars.hand_fight_or_flight" in mars_ids
    assert "claim.mars.hand_force_register" in mars_ids
    assert "claim.mars.hand_iron_steel" in mars_ids
    assert "claim.mars.hand_body_muscular_vigor" in mars_ids
    assert "claim.mars.hand_blocked_health_manifestation" in mars_ids
    assert "claim.mars.rudhyar_first_gesture" in mars_ids
    assert "claim.mars.rudhyar_energy_release" in mars_ids
    assert "src.psychological.greene_inner_planets" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.greene_inner_planets" not in {row["source_id"] for row in mars_claims["claims"]}
    assert "src.professional.hand_horoscope_symbols" not in set(mars_claims["pending_source_ids"])
    assert "src.humanistic.rudhyar_new_mansions" not in set(mars_claims["pending_source_ids"])
    hand_mars = [row for row in mars_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_mars) == 13
    assert all(row["source_class"] == "professional" for row in hand_mars)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_mars)
    assert all(row["school"] == "modern_professional" for row in hand_mars)
    assert all("runtime_semantic_candidate" not in row for row in hand_mars)
    rudhyar_mars = [row for row in mars_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_mars) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_mars)
    assert all(row["school"] == "humanistic" for row in rudhyar_mars)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_mars)
    first_gesture = next(row for row in rudhyar_mars if row["concept_id"] == "claim.mars.rudhyar_first_gesture")
    assert first_gesture["field"] == "function"
    assert "first gesture" in first_gesture["normalized_claim"].lower()
    assert "survival" not in first_gesture["normalized_claim"].lower()
    assert "assertive" not in first_gesture["normalized_claim"].lower()
    assert "warrior" not in first_gesture["normalized_claim"].lower()
    assert "heating and drying quality that contends" == by_id["astro.object.mars"]["function"]
    assert "survival" not in by_id["astro.object.mars"]["function"]
    assert "first gesture" not in by_id["astro.object.mars"]["function"]
    assert "claim.mars.hand_survival_energy" in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    assert "claim.mars.rudhyar_first_gesture" in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    assert "claim.mars.hand_body_muscular_vigor" not in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    assert "claim.mars.hand_blocked_health_manifestation" not in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    mars_domains = json.dumps(by_id["astro.object.mars"]["domains"]).lower()
    assert "inflammation" not in mars_domains
    assert "iron" not in mars_domains
    assert any("p.138" in note and "not opened" in note.lower() for note in mars_claims["gap_notes"])
    assert any("humanistic" in note.lower() and "rudhyar" in note.lower() for note in mars_claims["gap_notes"])
    assert any("1.3.42" in note for note in mars_claims["gap_notes"])
    assert any("1.3.49" in note for note in mars_claims["gap_notes"])
    assert any("1.3.54" in note for note in mars_claims["gap_notes"])
    assert any("1.3.55" in note for note in mars_claims["gap_notes"])
    assert any("1.3.56" in note for note in mars_claims["gap_notes"])
    assert any("1.3.57" in note for note in mars_claims["gap_notes"])
    assert any("ACCESS_BLOCKED" in note for note in mars_claims["gap_notes"])
    assert any("3 dedicated independent loci" in note for note in mars_claims["gap_notes"])
    assert any("mythic astrology" in note.lower() for note in mars_claims["gap_notes"])
    assert "src.psychological.greene_mars_cpa" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.bell_mars_quartet" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.sasportas_dynamics_unconscious" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.huber_planets" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.sasportas_dynamics_unconscious" not in {row["source_id"] for row in mars_claims["claims"]}
    assert "src.psychological.huber_planets" not in {row["source_id"] for row in mars_claims["claims"]}
    assert all(row["source_class"] != "psychological" for row in mars_claims["claims"])
    assert "heating and drying quality that contends" == by_id["astro.object.mars"]["function"]
    jupiter_claims = json.loads((CLAIMS_DIR / "astro.object.jupiter.json").read_text(encoding="utf-8"))
    jupiter_ids = {row["concept_id"] for row in jupiter_claims["claims"]}
    assert "claim.jupiter.benefic_assumption_contingent" in jupiter_ids
    assert "claim.jupiter.return_life_development_doorways" in jupiter_ids
    assert "claim.jupiter.seven_sins_gluttony_tradition" in jupiter_ids
    cpa_rows = [row for row in jupiter_claims["claims"] if row["source_id"] == "src.psychological.greene_jupiter_cpa"]
    assert cpa_rows
    assert all(row["source_class"] == "psychological" for row in cpa_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in cpa_rows)
    assert "src.psychological.greene_jupiter_cpa" not in set(jupiter_claims["pending_source_ids"])
    assert "src.psychological.greene_relating" in set(jupiter_claims["pending_source_ids"])
    assert "src.psychological.greene_by_jove" not in set(jupiter_claims["pending_source_ids"])
    assert "src.humanistic.rudhyar_new_mansions" not in set(jupiter_claims["pending_source_ids"])
    assert "src.humanistic.ruperti_cycles" in set(jupiter_claims["pending_source_ids"])
    by_jove = [row for row in jupiter_claims["claims"] if row["source_id"] == "src.psychological.greene_by_jove"]
    assert len(by_jove) == 12
    assert all(row["source_class"] == "psychological" for row in by_jove)
    assert all(row["school"] == "psychological_jungian" for row in by_jove)
    assert all(row["evidence_tier"] == "school_specific" for row in by_jove)
    assert all(row["review_status"] == "extracted" for row in by_jove)
    assert {row["concept_id"] for row in by_jove} == {
        "claim.jupiter.greene_gluttony_not_greed",
        "claim.jupiter.greene_never_full",
        "claim.jupiter.greene_versatile_gluttony",
        "claim.jupiter.greene_moderate_vs_breach",
        "claim.jupiter.greene_envy_kit",
        "claim.jupiter.greene_unpredictable",
        "claim.jupiter.greene_leap_of_faith",
        "claim.jupiter.greene_individuation_teleology",
        "claim.jupiter.greene_sow_possibilities",
        "claim.jupiter.greene_not_controllable",
        "claim.jupiter.greene_purpose_as_defence",
        "claim.jupiter.greene_identification_hubris",
    }
    teleology = next(row for row in by_jove if row["concept_id"] == "claim.jupiter.greene_individuation_teleology")
    assert teleology["field"] == "function"
    assert "individuation" in teleology["normalized_claim"].lower()
    assert "expansion" not in teleology["normalized_claim"].lower()
    assert "enlargement" not in teleology["normalized_claim"].lower()
    assert all("benefic" not in row["normalized_claim"].lower() for row in by_jove)
    gluttony = next(row for row in by_jove if row["concept_id"] == "claim.jupiter.greene_gluttony_not_greed")
    assert "greed" in gluttony["normalized_claim"].lower()
    assert any("by jove" in note.lower() and "extract" in note.lower() for note in jupiter_claims["gap_notes"])
    assert any("nmnm_jupiter" in note.lower() for note in jupiter_claims["gap_notes"])
    assert any("seminar description" in note.lower() or "not the transcript" in note.lower() for note in jupiter_claims["gap_notes"])
    assert "claim.jupiter.hand_expansion" in jupiter_ids
    assert "claim.jupiter.hand_integration" in jupiter_ids
    assert "claim.jupiter.hand_becoming" in jupiter_ids
    assert "claim.jupiter.hand_exploration_learning" in jupiter_ids
    assert "claim.jupiter.hand_autonomy_freedom" in jupiter_ids
    assert "claim.jupiter.hand_incorporation" in jupiter_ids
    assert "claim.jupiter.hand_parental_encouragement" in jupiter_ids
    assert "claim.jupiter.hand_place_in_world" in jupiter_ids
    assert "claim.jupiter.hand_integrative_mind" in jupiter_ids
    assert "claim.jupiter.hand_social_consciousness" in jupiter_ids
    assert "claim.jupiter.hand_excess_growth" in jupiter_ids
    assert "claim.jupiter.hand_detail_neglect" in jupiter_ids
    assert "claim.jupiter.hand_possessive_expansion" in jupiter_ids
    assert "claim.jupiter.hand_integration_arrogance" in jupiter_ids
    assert "claim.jupiter.hand_saturn_polarity" in jupiter_ids
    assert "claim.jupiter.hand_healing_reintegration" in jupiter_ids
    assert "src.professional.hand_horoscope_symbols" not in set(jupiter_claims["pending_source_ids"])
    hand_jupiter = [row for row in jupiter_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_jupiter) == 16
    assert all(row["source_class"] == "professional" for row in hand_jupiter)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_jupiter)
    assert all(row["school"] == "modern_professional" for row in hand_jupiter)
    assert all("runtime_semantic_candidate" not in row for row in hand_jupiter)
    jupiter_prov = {row["concept_id"] for row in by_id["astro.object.jupiter"]["provenance"]}
    assert "claim.jupiter.hand_expansion" in jupiter_prov
    assert "claim.jupiter.hand_integration" in jupiter_prov
    assert "claim.jupiter.greene_individuation_teleology" in jupiter_prov
    assert "claim.jupiter.rudhyar_organizer" in jupiter_prov
    assert "claim.jupiter.hand_healing_reintegration" not in jupiter_prov
    jupiter_domains = json.dumps(by_id["astro.object.jupiter"]["domains"]).lower()
    assert "healing" not in jupiter_domains
    assert "medicine" not in jupiter_domains
    assert "gluttony" not in jupiter_domains
    assert "addiction" not in jupiter_domains
    assert "food" not in jupiter_domains
    assert "lymph" not in jupiter_domains
    assert "cancer" not in jupiter_domains
    rudhyar_jupiter = [row for row in jupiter_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_jupiter) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_jupiter)
    assert all(row["school"] == "humanistic" for row in rudhyar_jupiter)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_jupiter)
    assert {row["concept_id"] for row in rudhyar_jupiter} == {
        "claim.jupiter.rudhyar_organizer",
        "claim.jupiter.rudhyar_purpose_form_function",
        "claim.jupiter.rudhyar_within_only",
        "claim.jupiter.rudhyar_hierarch",
        "claim.jupiter.rudhyar_religion_binds",
        "claim.jupiter.rudhyar_twins",
        "claim.jupiter.rudhyar_expansion_if_balanced",
        "claim.jupiter.rudhyar_soul_compensator",
        "claim.jupiter.rudhyar_conditioned_by_saturn",
        "claim.jupiter.rudhyar_greater_fortune",
        "claim.jupiter.rudhyar_mirage_god",
        "claim.jupiter.rudhyar_soul_emanation",
    }
    organizer = next(row for row in rudhyar_jupiter if row["concept_id"] == "claim.jupiter.rudhyar_organizer")
    assert organizer["field"] == "function"
    assert "organic function" in organizer["normalized_claim"].lower()
    assert "expansion" not in organizer["normalized_claim"].lower()
    assert all("gluttony" not in row["normalized_claim"].lower() for row in rudhyar_jupiter)
    assert all("individuation" not in row["normalized_claim"].lower() for row in rudhyar_jupiter)
    assert any("organizer" in note.lower() or "organizer-of-functions" in note.lower() for note in jupiter_claims["gap_notes"])
    assert any("1.3.40" in note for note in jupiter_claims["gap_notes"])
    assert any("ruperti" in note.lower() for note in jupiter_claims["gap_notes"])
    mercury_notes = " ".join(json.loads((CLAIMS_DIR / "astro.object.mercury.json").read_text(encoding="utf-8"))["gap_notes"]).lower()
    assert "breadth-over-depth" in mercury_notes or "breadth over depth" in mercury_notes
    assert "expansion" not in by_id["astro.object.jupiter"]["function"]
    assert "integration" not in by_id["astro.object.jupiter"]["function"]
    assert "individuation" not in by_id["astro.object.jupiter"]["function"]
    assert "gluttony" not in by_id["astro.object.jupiter"]["function"]
    assert "teleology" not in by_id["astro.object.jupiter"]["function"]
    assert "organizer" not in by_id["astro.object.jupiter"]["function"]
    assert "soul" not in by_id["astro.object.jupiter"]["function"]
    assert "temperate warming and moistening quality" == by_id["astro.object.jupiter"]["function"]
    saturn_claims = json.loads((CLAIMS_DIR / "astro.object.saturn.json").read_text(encoding="utf-8"))
    saturn_ids = {row["concept_id"] for row in saturn_claims["claims"]}
    for concept_id in (
        "claim.saturn.hand_resistance",
        "claim.saturn.hand_structure_limits",
        "claim.saturn.hand_exclusion_definition",
        "claim.saturn.hand_consensus_reality",
        "claim.saturn.hand_social_rules_obligations",
        "claim.saturn.hand_consequences",
        "claim.saturn.hand_maturation",
        "claim.saturn.hand_responsibility_discipline",
        "claim.saturn.hand_reality_not_truth",
        "claim.saturn.hand_structure_addiction",
        "claim.saturn.hand_rigidity",
        "claim.saturn.hand_actualization",
        "claim.saturn.hand_conformity_self_betrayal",
        "claim.saturn.hand_guilt_shadow",
        "claim.saturn.hand_jupiter_polarity",
        "claim.saturn.hand_ordinary_reality_boundary",
    ):
        assert concept_id in saturn_ids
    assert "src.professional.hand_horoscope_symbols" not in set(saturn_claims["pending_source_ids"])
    hand_saturn = [row for row in saturn_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_saturn) == 16
    assert all(row["source_class"] == "professional" for row in hand_saturn)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_saturn)
    assert all(row["school"] == "modern_professional" for row in hand_saturn)
    assert all("runtime_semantic_candidate" not in row for row in hand_saturn)
    assert "cooling quality operating by distance from heat" == by_id["astro.object.saturn"]["function"]
    assert "resistance" not in by_id["astro.object.saturn"]["function"]
    assert "structure" not in by_id["astro.object.saturn"]["function"]
    assert "i am i" not in by_id["astro.object.saturn"]["function"].lower()
    assert "ring-pass-not" not in by_id["astro.object.saturn"]["function"].lower()
    assert by_id["astro.object.saturn"]["themes"] == ["cold", "dryness", "slowness", "solitude", "austerity"]
    assert "claim.saturn.hand_resistance" in {row["concept_id"] for row in by_id["astro.object.saturn"]["provenance"]}
    assert "claim.saturn.rudhyar_i_am_i" in {row["concept_id"] for row in by_id["astro.object.saturn"]["provenance"]}
    assert not any("structure" in theme for theme in by_id["astro.object.saturn"]["themes"])
    saturn_domains = json.dumps(by_id["astro.object.saturn"]["domains"]).lower()
    assert "kundalini" not in saturn_domains
    assert "spine" not in saturn_domains
    assert "sacroiliac" not in saturn_domains
    rudhyar_saturn = [row for row in saturn_claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"]
    assert len(rudhyar_saturn) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_saturn)
    assert all(row["school"] == "humanistic" for row in rudhyar_saturn)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_saturn)
    assert {row["concept_id"] for row in rudhyar_saturn} == {
        "claim.saturn.rudhyar_systole",
        "claim.saturn.rudhyar_i_am_i",
        "claim.saturn.rudhyar_ring_pass_not",
        "claim.saturn.rudhyar_let_there_be_form",
        "claim.saturn.rudhyar_spirit_into_form",
        "claim.saturn.rudhyar_golden_age_instinct",
        "claim.saturn.rudhyar_integrity",
        "claim.saturn.rudhyar_fate_tester",
        "claim.saturn.rudhyar_satan_pride",
        "claim.saturn.rudhyar_logician",
        "claim.saturn.rudhyar_seed_diamond",
        "claim.saturn.rudhyar_two_in_one",
    }
    i_am = next(row for row in rudhyar_saturn if row["concept_id"] == "claim.saturn.rudhyar_i_am_i")
    assert i_am["field"] == "function"
    assert "i am i" in i_am["normalized_claim"].lower()
    assert all("psychic process" not in row["normalized_claim"].lower() for row in rudhyar_saturn)
    assert all("resistance" not in row["normalized_claim"].lower() for row in rudhyar_saturn)
    assert "src.humanistic.rudhyar_new_mansions" not in set(saturn_claims["pending_source_ids"])
    assert any("ring-pass-not" in note.lower() or "i-am-i" in note.lower() for note in saturn_claims["gap_notes"])
    assert any("humanistic" in note.lower() and "rudhyar" in note.lower() for note in saturn_claims["gap_notes"])
    tarnas_saturn = [row for row in saturn_claims["claims"] if row["source_id"] == "src.psychological.tarnas_archetypal_intro"]
    assert len(tarnas_saturn) == 9
    assert all(row["source_class"] == "psychological" for row in tarnas_saturn)
    assert all(row["school"] == "archetypal_depth" for row in tarnas_saturn)
    assert all(row["evidence_tier"] == "school_specific" for row in tarnas_saturn)
    assert {row["concept_id"] for row in tarnas_saturn} == {
        "claim.saturn.tarnas_limit_necessity",
        "claim.saturn.tarnas_senex",
        "claim.saturn.tarnas_chronos_chart",
        "claim.saturn.tarnas_gravitas",
        "claim.saturn.tarnas_birth_labor",
        "claim.saturn.tarnas_skeleton",
        "claim.saturn.tarnas_inner_judge",
        "claim.saturn.tarnas_inner_authority",
        "claim.saturn.tarnas_threshold_guardian",
    }
    senex = next(row for row in tarnas_saturn if row["concept_id"] == "claim.saturn.tarnas_senex")
    assert senex["field"] == "themes"
    assert "senex" in senex["normalized_claim"].lower()
    assert all("psychic process" not in row["normalized_claim"].lower() for row in tarnas_saturn)
    assert all("i am i" not in row["normalized_claim"].lower() for row in tarnas_saturn)
    assert any("1.3.53" in note for note in saturn_claims["gap_notes"])
    saturn_psych = [row for row in saturn_claims["claims"] if row["source_class"] == "psychological"]
    assert {row["source_id"] for row in saturn_psych} == {
        "src.psychological.greene_saturn",
        "src.psychological.tarnas_archetypal_intro",
    }
    assert "claim.saturn.tarnas_senex" in {row["concept_id"] for row in by_id["astro.object.saturn"]["provenance"]}
    assert "claim.saturn.tarnas_chronos_chart" in {row["concept_id"] for row in by_id["astro.object.saturn"]["provenance"]}
    assert "senex" not in by_id["astro.object.saturn"]["function"].lower()
    assert "chronos" not in by_id["astro.object.saturn"]["function"].lower()
    assert "threshold" not in by_id["astro.object.saturn"]["function"].lower()
    hand_claim_files = {
        path.name
        for path in CLAIMS_DIR.glob("astro.object.*.json")
        if any(
            row["source_id"] == "src.professional.hand_horoscope_symbols"
            for row in json.loads(path.read_text(encoding="utf-8"))["claims"]
        )
    }
    assert hand_claim_files == {
        "astro.object.venus.json",
        "astro.object.mars.json",
        "astro.object.jupiter.json",
        "astro.object.saturn.json",
        "astro.object.uranus.json",
        "astro.object.neptune.json",
        "astro.object.pluto.json",
    }
    hand = next(src for src in corpus["sources"] if src["source_id"] == "src.professional.hand_horoscope_symbols")
    assert "not Planets in Transit" in hand["notes"]
    assert "Venus–Pluto Ch.4 extracted" in hand["notes"]
    assert "Sun/Moon/Mercury" in hand["notes"]
    cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_jupiter_cpa")
    assert cpa["source_class"] == "psychological"
    assert cpa["legal_status"] == "copyrighted_site"
    by_jove_src = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_by_jove")
    assert by_jove_src["source_class"] == "psychological"
    assert by_jove_src["legal_status"] == "copyrighted_site"
    assert "1.3.38" in by_jove_src["notes"]
    assert "in_lgbyjove2" in by_jove_src["notes"]
    assert "jagger" in by_jove_src["notes"].lower()
    rudhyar_nmnm = next(src for src in corpus["sources"] if src["source_id"] == "src.humanistic.rudhyar_new_mansions")
    assert rudhyar_nmnm["source_class"] == "humanistic"
    assert rudhyar_nmnm["role"] == "humanistic"
    assert rudhyar_nmnm["legal_status"] == "copyrighted_site"
    assert "Humanistic, not psychological" in rudhyar_nmnm["notes"]
    assert "Sun 1.3.35" in rudhyar_nmnm["notes"]
    assert "Moon 1.3.36" in rudhyar_nmnm["notes"]
    assert "Mercury 1.3.37" in rudhyar_nmnm["notes"]
    assert "Saturn 1.3.39" in rudhyar_nmnm["notes"]
    assert "Jupiter 1.3.40" in rudhyar_nmnm["notes"]
    ruperti = next(src for src in corpus["sources"] if src["source_id"] == "src.humanistic.ruperti_cycles")
    assert ruperti["source_class"] == "humanistic"
    assert ruperti["status"] == "candidate"
    assert "unread" in ruperti["notes"].lower()
    assert "1.3.40" in ruperti["notes"]
    chariot = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_apollos_chariot")
    assert chariot["source_class"] == "psychological"
    assert chariot["status"] == "candidate"
    assert "unread" in chariot["notes"].lower()
    assert "1.3.50" in chariot["notes"]
    assert "need_owner" in chariot["notes"].lower()
    apollon = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_apollon_sun")
    assert apollon["source_class"] == "psychological"
    assert apollon["legal_status"] == "copyrighted_site"
    assert apollon["status"] == "candidate"
    assert "1.3.50" in apollon["notes"]
    assert "ingested" in apollon["notes"].lower()
    assert "not apollo's chariot" in apollon["notes"].lower() or "not apollo’s chariot" in apollon["notes"].lower()
    costello = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.costello_astrological_moon")
    assert costello["source_class"] == "psychological"
    assert costello["status"] == "candidate"
    assert "unread" in costello["notes"].lower()
    assert "need_owner" in costello["notes"].lower()
    assert "1.3.51" in costello["notes"]
    reinhart_moon = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.reinhart_moon_talk")
    assert reinhart_moon["source_class"] == "psychological"
    assert reinhart_moon["status"] == "candidate"
    assert reinhart_moon["legal_status"] == "copyrighted_site"
    assert "1.3.51" in reinhart_moon["notes"]
    assert "not natal" in reinhart_moon["notes"].lower()
    clark_hermes = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.clark_hermes_guide")
    assert clark_hermes["source_class"] == "psychological"
    assert clark_hermes["status"] == "candidate"
    assert clark_hermes["legal_status"] == "copyrighted_site"
    assert "1.3.52" in clark_hermes["notes"]
    assert "not natal" in clark_hermes["notes"].lower()
    martin = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.martin_mapping_psyche")
    assert martin["source_class"] == "psychological"
    assert martin["status"] == "candidate"
    assert "unread" in martin["notes"].lower()
    assert "lesson 2" in martin["notes"].lower()
    assert "lesson 4" in martin["notes"].lower()
    assert "1.3.52" in martin["notes"]
    assert "1.3.53" in martin["notes"]
    assert "1.3.54" in martin["notes"]
    assert "1.3.55" in martin["notes"]
    unused_rudhyar = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.rudhyar_personality")
    assert unused_rudhyar["source_class"] == "psychological"
    mars_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_mars_cpa")
    assert mars_cpa["source_class"] == "psychological"
    assert "transcript" in mars_cpa["notes"].lower()
    saturn_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_saturn_cpa")
    assert saturn_cpa["source_class"] == "psychological"
    assert saturn_cpa["status"] == "candidate"
    assert "transcript" in saturn_cpa["notes"].lower()
    assert "1.3.39" in saturn_cpa["notes"]
    assert "1.3.53" in saturn_cpa["notes"]
    uranus_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_uranus_cpa")
    assert uranus_cpa["source_class"] == "psychological"
    assert uranus_cpa["status"] == "candidate"
    assert "transcript" in uranus_cpa["notes"].lower()
    assert "1.3.43" in uranus_cpa["notes"]
    neptune_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_neptune_cpa")
    assert neptune_cpa["source_class"] == "psychological"
    assert neptune_cpa["status"] == "candidate"
    assert "transcript" in neptune_cpa["notes"].lower()
    assert "1.3.44" in neptune_cpa["notes"]
    greene_neptune_book = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_astrological_neptune"
    )
    assert greene_neptune_book["source_class"] == "psychological"
    assert greene_neptune_book["status"] == "candidate"
    assert "unread" in greene_neptune_book["notes"].lower()
    pluto_cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_pluto_cpa")
    assert pluto_cpa["source_class"] == "psychological"
    assert pluto_cpa["status"] == "candidate"
    assert "transcript" in pluto_cpa["notes"].lower()
    assert "1.3.45" in pluto_cpa["notes"]
    living = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_living_with_pluto")
    assert living["source_class"] == "psychological"
    assert living["status"] == "candidate"
    assert "1.3.45" in living["notes"]
    assert "ingested" in living["notes"].lower()
    reinhart = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.reinhart_pluto_lord")
    assert reinhart["source_class"] == "psychological"
    assert reinhart["status"] == "candidate"
    assert "not this locus" in reinhart["notes"].lower()
    cunningham = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.cunningham_healing_pluto"
    )
    assert cunningham["source_class"] == "psychological"
    assert cunningham["status"] == "candidate"
    assert "unread" in cunningham["notes"].lower() or "cover only" in cunningham["notes"].lower()
    hamaker = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.hamaker_psychological")
    assert hamaker["source_class"] == "psychological"
    assert hamaker["status"] == "candidate"
    assert "unread" in hamaker["notes"].lower()
    assert "1.3.56" in hamaker["notes"]
    sasportas_change = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.sasportas_gods_of_change"
    )
    assert sasportas_change["source_class"] == "psychological"
    assert sasportas_change["status"] == "candidate"
    assert "unread" in sasportas_change["notes"].lower() or "not opened" in sasportas_change["notes"].lower()
    assert "1.3.45" in sasportas_change["notes"]
    bell = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.bell_mars_quartet")
    assert bell["source_class"] == "psychological"
    assert bell["status"] == "candidate"
    dynamics = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.sasportas_dynamics_unconscious"
    )
    assert dynamics["source_class"] == "psychological"
    assert dynamics["status"] == "candidate"
    assert "1.3.55" in dynamics["notes"]
    assert "1.3.57" in dynamics["notes"]
    assert "ACCESS_BLOCKED" in dynamics["notes"]
    assert "aggression" in dynamics["notes"].lower()
    assert "printdisabled" in dynamics["notes"].lower() or "archive" in dynamics["notes"].lower()
    huber = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.huber_planets")
    assert huber["source_class"] == "psychological"
    assert huber["status"] == "candidate"
    assert "1.3.56" in huber["notes"]
    assert "1.3.57" in huber["notes"]
    assert "ACCESS_BLOCKED" in huber["notes"]
    assert "masculine" in huber["notes"].lower()
    assert "unread" in huber["notes"].lower()
    inner_planets = next(
        src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_inner_planets"
    )
    assert "1.3.57" in inner_planets["notes"]
    assert "ACCESS_BLOCKED" in inner_planets["notes"]


def test_hand_uranus_claims_not_core():
    """Hand Ch.4 Uranus is professional school_specific; Rudhyar NMNM is humanistic; Tarnas intro is psychological; object withheld; not CORE."""
    object_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, object_schema)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert "astro.object.uranus" not in by_id
    assert "astro.object.neptune" not in by_id
    assert "astro.object.pluto" not in by_id
    claims = json.loads((CLAIMS_DIR / "astro.object.uranus.json").read_text(encoding="utf-8"))
    jsonschema.validate(claims, claims_schema)
    assert claims["object_id"] == "astro.object.uranus"
    assert claims["calc_entity"] == "astrology.planet.uranus"
    expected_ids = {
        "claim.uranus.disrupts_saturnine_structure",
        "claim.uranus.random_mutation",
        "claim.uranus.freedom_drive",
        "claim.uranus.insight_enlightenment",
        "claim.uranus.peripheral_awareness",
        "claim.uranus.alien_world_expansion",
        "claim.uranus.altered_consciousness",
        "claim.uranus.eccentric_unusual_expression",
        "claim.uranus.collective_disruption",
        "claim.uranus.science_technology",
        "claim.uranus.saturn_balance",
        "claim.uranus.chaos_life_function",
    }
    hand_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"
    ]
    assert {row["concept_id"] for row in hand_rows} == expected_ids
    assert len(hand_rows) == 12
    assert all(row["source_class"] == "professional" for row in hand_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_rows)
    assert all(row["school"] == "modern_professional" for row in hand_rows)
    assert all(row["review_status"] == "extracted" for row in hand_rows)
    rudhyar_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"
    ]
    assert {row["concept_id"] for row in rudhyar_rows} == {
        "claim.uranus.rudhyar_transforms",
        "claim.uranus.rudhyar_through",
        "claim.uranus.rudhyar_what_if",
        "claim.uranus.rudhyar_not_modification",
        "claim.uranus.rudhyar_not_jupiter",
        "claim.uranus.rudhyar_not_regeneration",
        "claim.uranus.rudhyar_pierce_and_project",
        "claim.uranus.rudhyar_protean",
        "claim.uranus.rudhyar_metamorphosis",
        "claim.uranus.rudhyar_no_going_back",
        "claim.uranus.rudhyar_path_not_factor",
        "claim.uranus.rudhyar_84_year_cycle",
    }
    assert len(rudhyar_rows) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_rows)
    assert all(row["school"] == "humanistic" for row in rudhyar_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_rows)
    assert all(row["review_status"] == "extracted" for row in rudhyar_rows)
    transforms = next(row for row in rudhyar_rows if row["concept_id"] == "claim.uranus.rudhyar_transforms")
    assert transforms["field"] == "function"
    assert "transform" in transforms["normalized_claim"].lower()
    assert "disruption" not in transforms["normalized_claim"].lower()
    assert "mutation" not in transforms["normalized_claim"].lower()
    regen = next(row for row in rudhyar_rows if row["concept_id"] == "claim.uranus.rudhyar_not_regeneration")
    assert "pluto" in regen["normalized_claim"].lower()
    tarnas_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.psychological.tarnas_archetypal_intro"
    ]
    assert {row["concept_id"] for row in tarnas_rows} == {
        "claim.uranus.tarnas_prometheus_figure",
        "claim.uranus.tarnas_freedom_rebellion",
        "claim.uranus.tarnas_breakthroughs",
        "claim.uranus.tarnas_breakup_structures",
        "claim.uranus.tarnas_individual_path",
        "claim.uranus.tarnas_genius_vs_eccentric",
        "claim.uranus.tarnas_unintegrated_from_without",
        "claim.uranus.tarnas_hold_the_past",
        "claim.uranus.tarnas_restless_quest",
    }
    assert len(tarnas_rows) == 9
    assert all(row["source_class"] == "psychological" for row in tarnas_rows)
    assert all(row["school"] == "archetypal_depth" for row in tarnas_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in tarnas_rows)
    assert all(row["review_status"] == "extracted" for row in tarnas_rows)
    prometheus = next(row for row in tarnas_rows if row["concept_id"] == "claim.uranus.tarnas_prometheus_figure")
    assert prometheus["field"] == "function"
    assert "prometheus" in prometheus["normalized_claim"].lower()
    assert "ouranos" in prometheus["normalized_claim"].lower()
    assert "disruption" not in prometheus["normalized_claim"].lower()
    assert "mutation" not in prometheus["normalized_claim"].lower()
    assert "transform" not in prometheus["normalized_claim"].lower()
    unintegrated = next(
        row for row in tarnas_rows if row["concept_id"] == "claim.uranus.tarnas_unintegrated_from_without"
    )
    assert unintegrated["field"] == "shadow"
    assert "forced change" in unintegrated["normalized_claim"].lower()
    assert "saturnine structure" not in unintegrated["normalized_claim"].lower()
    assert all("disruption of over-stabilized" not in row["normalized_claim"].lower() for row in tarnas_rows)
    assert all("transform" not in row["normalized_claim"].lower() for row in tarnas_rows)
    assert len(claims["claims"]) == 33
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.psychological.sasportas_gods_of_change" in pending
    assert "src.psychological.greene_uranus_cpa" in pending
    assert "src.psychological.greene_art_of_stealing_fire" in pending
    assert "src.psychological.tarnas_prometheus" in pending
    assert "src.psychological.greene_mythic_astrology" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.humanistic.rudhyar_new_mansions" not in pending
    assert "src.psychological.tarnas_archetypal_intro" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    assert "src.psychological.sasportas_gods_of_change" not in used
    assert "src.psychological.tarnas_prometheus" not in used
    assert "src.humanistic.rudhyar_new_mansions" in used
    assert "src.psychological.tarnas_archetypal_intro" in used
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes or "object still withheld" in notes
    assert "jupiter" in notes and "alien" in notes
    assert "1981" in notes
    assert "rudhyar" in notes and "humanistic" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert "1.3.43" in notes
    assert "1.3.46" in notes
    assert "prometheus" in notes
    assert "mythic astrology" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    _assert_il1_catalog_counts(objects)


def test_hand_neptune_claims_not_core():
    """Hand Ch.4 Neptune is professional; Rudhyar NMNM humanistic; Tarnas intro psychological; object withheld; not CORE."""
    object_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, object_schema)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert "astro.object.neptune" not in by_id
    assert "astro.object.pluto" not in by_id
    claims = json.loads((CLAIMS_DIR / "astro.object.neptune.json").read_text(encoding="utf-8"))
    jsonschema.validate(claims, claims_schema)
    assert claims["object_id"] == "astro.object.neptune"
    assert claims["calc_entity"] == "astrology.planet.neptune"
    expected_ids = {
        "claim.neptune.ultimate_reality",
        "claim.neptune.dissolves_distinctions",
        "claim.neptune.nirvana",
        "claim.neptune.mystical_perception",
        "claim.neptune.nonattachment",
        "claim.neptune.maya_with_saturn",
        "claim.neptune.imagination",
        "claim.neptune.abstract_arts",
        "claim.neptune.artistic_creativity_with_venus",
        "claim.neptune.ideals",
        "claim.neptune.illusion_of_perfection",
        "claim.neptune.sacrifice_higher_causes",
        "claim.neptune.martyr_expression",
        "claim.neptune.victim_expression",
        "claim.neptune.unreality_illusion",
        "claim.neptune.mystery_confusion",
        "claim.neptune.ego_denial_defeat",
    }
    hand_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"
    ]
    assert {row["concept_id"] for row in hand_rows} == expected_ids
    assert len(hand_rows) == 17
    assert all(row["source_class"] == "professional" for row in hand_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_rows)
    assert all(row["school"] == "modern_professional" for row in hand_rows)
    assert all(row["review_status"] == "extracted" for row in hand_rows)
    rudhyar_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"
    ]
    assert {row["concept_id"] for row in rudhyar_rows} == {
        "claim.neptune.rudhyar_ecstasy_realm",
        "claim.neptune.rudhyar_end_of_journey",
        "claim.neptune.rudhyar_prenatal_growth",
        "claim.neptune.rudhyar_compassion_atonement",
        "claim.neptune.rudhyar_melting_pot",
        "claim.neptune.rudhyar_organisms_of_light",
        "claim.neptune.rudhyar_glamor",
        "claim.neptune.rudhyar_regressive_merge",
        "claim.neptune.rudhyar_two_ecstasies",
        "claim.neptune.rudhyar_intoxication_relief",
        "claim.neptune.rudhyar_universal_rescues",
        "claim.neptune.rudhyar_after_uranus_collective",
    }
    assert len(rudhyar_rows) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_rows)
    assert all(row["school"] == "humanistic" for row in rudhyar_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_rows)
    assert all(row["review_status"] == "extracted" for row in rudhyar_rows)
    ecstasy = next(row for row in rudhyar_rows if row["concept_id"] == "claim.neptune.rudhyar_ecstasy_realm")
    assert ecstasy["field"] == "function"
    assert "ecstasy" in ecstasy["normalized_claim"].lower()
    assert "ultimate reality" not in ecstasy["normalized_claim"].lower()
    assert "dissolution of" not in ecstasy["normalized_claim"].lower()
    prenatal = next(row for row in rudhyar_rows if row["concept_id"] == "claim.neptune.rudhyar_prenatal_growth")
    assert "pluto" in prenatal["normalized_claim"].lower()
    tarnas_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.psychological.tarnas_archetypal_intro"
    ]
    assert {row["concept_id"] for row in tarnas_rows} == {
        "claim.neptune.tarnas_transcendent_ideal",
        "claim.neptune.tarnas_ocean_of_consciousness",
        "claim.neptune.tarnas_thirst_transcendence",
        "claim.neptune.tarnas_nirvana_and_maya",
        "claim.neptune.tarnas_narcissus",
        "claim.neptune.tarnas_longing_loss",
        "claim.neptune.tarnas_imagination_compassion",
        "claim.neptune.tarnas_deny_self",
        "claim.neptune.tarnas_madness_mysticism",
    }
    assert len(tarnas_rows) == 9
    assert all(row["source_class"] == "psychological" for row in tarnas_rows)
    assert all(row["school"] == "archetypal_depth" for row in tarnas_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in tarnas_rows)
    assert all(row["review_status"] == "extracted" for row in tarnas_rows)
    ocean = next(row for row in tarnas_rows if row["concept_id"] == "claim.neptune.tarnas_ocean_of_consciousness")
    assert ocean["field"] == "function"
    assert "ocean of consciousness" in ocean["normalized_claim"].lower()
    assert "dissolution of" not in ocean["normalized_claim"].lower()
    assert "ultimate reality" not in ocean["normalized_claim"].lower()
    thirst = next(row for row in tarnas_rows if row["concept_id"] == "claim.neptune.tarnas_thirst_transcendence")
    assert "addictive" in thirst["normalized_claim"].lower()
    assert "spiritual" in thirst["normalized_claim"].lower()
    maya = next(row for row in tarnas_rows if row["concept_id"] == "claim.neptune.tarnas_nirvana_and_maya")
    assert maya["field"] == "polarity"
    assert "maya" in maya["normalized_claim"].lower()
    assert "neptune+saturn" not in maya["normalized_claim"].lower().replace(" ", "")
    assert all("dissolution of distinction" not in row["normalized_claim"].lower() for row in tarnas_rows)
    assert all("ecstasy" not in row["normalized_claim"].lower() for row in tarnas_rows)
    assert len(claims["claims"]) == 38
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.psychological.sasportas_gods_of_change" in pending
    assert "src.psychological.greene_astrological_neptune" in pending
    assert "src.psychological.greene_neptune_cpa" in pending
    assert "src.psychological.greene_mythic_astrology" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.humanistic.rudhyar_new_mansions" not in pending
    assert "src.psychological.tarnas_archetypal_intro" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    assert "src.psychological.greene_astrological_neptune" not in used
    assert "src.humanistic.rudhyar_new_mansions" in used
    assert "src.psychological.tarnas_archetypal_intro" in used
    combo_ids = {"claim.neptune.maya_with_saturn", "claim.neptune.artistic_creativity_with_venus"}
    assert combo_ids <= expected_ids
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes or "object still withheld" in notes
    assert "dreams" in notes and "intuition" in notes
    assert "maya" in notes and "neptune+saturn" in notes.replace(" ", "")
    assert "venus" in notes
    assert "1981" in notes
    assert "rudhyar" in notes and "humanistic" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert "1.3.44" in notes
    assert "1.3.47" in notes
    assert "mythic astrology" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    _assert_il1_catalog_counts(objects)


def test_hand_pluto_claims_not_core():
    """Hand Ch.4 Pluto is professional; Rudhyar NMNM humanistic; Greene Campion interview psychological; object withheld; not CORE."""
    object_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, object_schema)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert "astro.object.pluto" not in by_id
    claims = json.loads((CLAIMS_DIR / "astro.object.pluto.json").read_text(encoding="utf-8"))
    jsonschema.validate(claims, claims_schema)
    assert claims["object_id"] == "astro.object.pluto"
    assert claims["calc_entity"] == "astrology.planet.pluto"
    expected_ids = {
        "claim.pluto.completes_outer_planet_process",
        "claim.pluto.radical_transformation",
        "claim.pluto.death_resurrection_archetype",
        "claim.pluto.decompose_reconstitute",
        "claim.pluto.total_reality_crisis",
        "claim.pluto.requires_new_reality",
        "claim.pluto.transpersonal_power",
        "claim.pluto.resistance_intensifies_crisis",
        "claim.pluto.detachment_requirement",
        "claim.pluto.evolutionary_power",
        "claim.pluto.gradual_not_uranian_sudden",
        "claim.pluto.help_transformation",
        "claim.pluto.power_over_vulnerable",
        "claim.pluto.decay_corruption_death",
        "claim.pluto.purifying_fire",
    }
    hand_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"
    ]
    assert {row["concept_id"] for row in hand_rows} == expected_ids
    assert len(hand_rows) == 15
    assert all(row["source_class"] == "professional" for row in hand_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_rows)
    assert all(row["school"] == "modern_professional" for row in hand_rows)
    assert all(row["review_status"] == "extracted" for row in hand_rows)
    rudhyar_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.humanistic.rudhyar_new_mansions"
    ]
    assert {row["concept_id"] for row in rudhyar_rows} == {
        "claim.pluto.rudhyar_sower_of_seed",
        "claim.pluto.rudhyar_in_not_of",
        "claim.pluto.rudhyar_hierophant_of_birth",
        "claim.pluto.rudhyar_two_outcomes",
        "claim.pluto.rudhyar_immortality_as_process",
        "claim.pluto.rudhyar_descent",
        "claim.pluto.rudhyar_fecundation",
        "claim.pluto.rudhyar_god_in_the_lowest",
        "claim.pluto.rudhyar_seed_must_die",
        "claim.pluto.rudhyar_divine_substantiality",
        "claim.pluto.rudhyar_godseed_in_every_man",
        "claim.pluto.rudhyar_penetration_of_depths",
    }
    assert len(rudhyar_rows) == 12
    assert all(row["source_class"] == "humanistic" for row in rudhyar_rows)
    assert all(row["school"] == "humanistic" for row in rudhyar_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in rudhyar_rows)
    seed = next(row for row in rudhyar_rows if row["concept_id"] == "claim.pluto.rudhyar_sower_of_seed")
    assert seed["field"] == "function"
    assert "seed" in seed["normalized_claim"].lower()
    assert "reconstruction" not in seed["normalized_claim"].lower()
    assert "decomposition" not in seed["normalized_claim"].lower()
    hierophant = next(row for row in rudhyar_rows if row["concept_id"] == "claim.pluto.rudhyar_hierophant_of_birth")
    assert "birth" in hierophant["normalized_claim"].lower()
    greene_rows = [
        row for row in claims["claims"] if row["source_id"] == "src.psychological.greene_living_with_pluto"
    ]
    assert {row["concept_id"] for row in greene_rows} == {
        "claim.pluto.greene_image_family",
        "claim.pluto.greene_life_force",
        "claim.pluto.greene_breakdown_new_forms",
        "claim.pluto.greene_multiple_registers",
        "claim.pluto.greene_overwhelm_defend",
        "claim.pluto.greene_grind_or_victim",
        "claim.pluto.greene_life_or_death",
        "claim.pluto.greene_obsessive_takeover",
        "claim.pluto.greene_accept_greater",
        "claim.pluto.greene_survival_instinct",
    }
    assert len(greene_rows) == 10
    assert all(row["source_class"] == "psychological" for row in greene_rows)
    assert all(row["school"] == "psychological_jungian" for row in greene_rows)
    assert all(row["evidence_tier"] == "school_specific" for row in greene_rows)
    assert all(row["review_status"] == "extracted" for row in greene_rows)
    life_force = next(row for row in greene_rows if row["concept_id"] == "claim.pluto.greene_life_force")
    assert life_force["field"] == "function"
    assert "life-force" in life_force["normalized_claim"].lower() or "life force" in life_force["normalized_claim"].lower()
    assert "reconstruction" not in life_force["normalized_claim"].lower()
    assert "seed" not in life_force["normalized_claim"].lower()
    grind = next(row for row in greene_rows if row["concept_id"] == "claim.pluto.greene_grind_or_victim")
    assert grind["field"] == "shadow"
    assert "victim" in grind["normalized_claim"].lower()
    assert all("reconstruction" not in row["normalized_claim"].lower() for row in greene_rows)
    assert all("celestial-seed" not in row["normalized_claim"].lower() for row in greene_rows)
    assert len(claims["claims"]) == 37
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.psychological.sasportas_gods_of_change" in pending
    assert "src.psychological.greene_pluto_cpa" in pending
    assert "src.psychological.reinhart_pluto_lord" in pending
    assert "src.psychological.cunningham_healing_pluto" in pending
    assert "src.psychological.hamaker_psychological" in pending
    assert "src.psychological.greene_mythic_astrology" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.humanistic.rudhyar_new_mansions" not in pending
    assert "src.psychological.greene_living_with_pluto" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    assert "src.humanistic.rudhyar_new_mansions" in used
    assert "src.psychological.greene_living_with_pluto" in used
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes or "object still withheld" in notes
    assert "psychotic" in notes and "excluded" in notes
    assert "generic transformation" in notes or "big-transformation" in notes or "big transformation" in notes
    assert "uranus" in notes and "neptune" in notes
    assert "1981" in notes
    assert "rudhyar" in notes and "humanistic" in notes
    assert "1.3.45" in notes
    assert "living with pluto" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    concept_fields = {row["concept_id"]: row["field"] for row in claims["claims"]}
    assert concept_fields["claim.pluto.gradual_not_uranian_sudden"] == "tempo"
    _assert_il1_catalog_counts(objects)


def test_sun_pluto_live_recount_after_access_blocked():
    """1.3.58: dashboard from ledgers, not the 1.3.44 snapshot. No ingest this pass."""
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    psych_n = {}
    total = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych = [row for row in payload["claims"] if row.get("source_class") == "psychological"]
        psych_n[name] = len(psych)
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert sum(psych_n.values()) == 82
    assert core_n == 0
    assert psych_n["pluto"] == 10
    assert psych_n["mars"] == 0
    assert psych_n["moon"] == 2
    assert psych_n["mercury"] == 1
    assert psych_n["sun"] == 12
    assert psych_n["venus"] == 9
    assert psych_n["jupiter"] == 19
    assert psych_n["saturn"] == 11
    assert psych_n["uranus"] == 9
    assert psych_n["neptune"] == 9
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert "astro.object.pluto" not in by_id
    assert "heating and drying quality that contends" == by_id["astro.object.mars"]["function"]
    audit = (ROOT / "docs" / "astrology" / "IL1_SUN_PLUTO_GAP_AUDIT.md").read_text(encoding="utf-8")
    assert "1.3.58" in audit
    assert "**ACCESS_BLOCKED**" in audit
    assert "**COVERED**" in audit
    assert "**THIN**" in audit
    assert "EMPTY **0**" in audit or "EMPTY 0" in audit
    assert "1.3.44 dashboard snapshots" in audit or "replace 1.3.44" in audit
    # live queue must not revive the 1.3.44 instruction
    live_queue = audit.split("## 6. Next research queue")[1].split("## 7.")[0]
    assert "Do **not** run 1.3.44" in live_queue or "Retired instructions" in live_queue
    assert "Pluto is COVERED" in audit or "Pluto | 10 | **COVERED**" in audit


def test_planet_fill_research_stable_layer2_definition():
    """1.3.59: planet fill research-stable; Layer 2 definition before literature. No ingest."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "1.3.59" in canon
    assert "### 6.12 Planet fill research-stable (1.3.59)" in canon
    assert "### 6.13 Layer 2 Signs — definition pass" in canon
    assert "must not** generate planet research tasks" in canon
    assert "не ждать Arroyo/Rudhyar как обязательных авторов" in canon
    assert "ждать локусы (Arroyo, Rudhyar" not in canon
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Layer 2 Signs" in next_block
    assert "access queue" not in next_block.lower() or "opportunistic" in next_block.lower()
    assert "Do **not** start CORE" in next_block or "Do **not** start CORE scoring" in next_block
    audit = (ROOT / "docs" / "astrology" / "IL1_SUN_PLUTO_GAP_AUDIT.md").read_text(encoding="utf-8")
    live_queue = audit.split("## 6. Next research queue")[1].split("## 7.")[0]
    assert "Layer 2 Signs" in live_queue
    assert "research-stable" in live_queue
    assert "Do not start a new semantic core" not in live_queue
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "research-stable" in parent
    assert "Layer 2 Signs" in parent
    assert "1.3.59" in parent


def test_layer2_schools_and_source_types_before_literature_map():
    """1.3.60: Layer 2 schools + source types from the model, not from Arroyo/Rudhyar. No ingest."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "1.3.60" in canon
    assert "### 6.14 Layer 2 Signs — schools and source types" in canon
    assert "not** the school list" in canon
    assert "Stopped before step 7" in canon
    assert "evolutionary" in canon.lower()
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "§6.14" in parent
    assert "Layer 2 Signs" in parent


def test_layer2_literature_map_from_matrix_no_ingest():
    """1.3.61: literature map from school × constituent matrix. No ingest, no sign objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    assert "src.psychological.rudhyar_personality" in aries["pending_source_ids"]
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "1.3.61" in canon
    assert "### 6.15 Layer 2 Signs — literature map" in canon
    lit = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_LITERATURE_MAP.md").read_text(encoding="utf-8")
    assert "school × constituent" in lit or "School × constituent" in lit
    assert "not a shortlist" in lit.lower() or "Not a shortlist" in lit
    assert "Houlding" in lit and "triplicit" in lit.lower()
    assert "Pulse of Life" in lit
    assert "cookbook-risk" in lit
    assert "Do **not** ingest from this page" in lit or "Do **not** ingest" in lit
    assert "Hand Ch.11" in lit or "Ch.11" in lit
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.61" in parent


def test_layer2_selection_criteria_locked_no_shortlist_no_ingest():
    """1.3.62: selection criteria locked separately from shortlist. No ingest, no sign objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    assert "src.psychological.rudhyar_personality" in aries["pending_source_ids"]
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "1.3.62" in canon
    assert "### 6.16 Layer 2 Signs — selection criteria" in canon
    assert "Stopped before step 9" in canon
    criteria = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_SELECTION_CRITERIA.md").read_text(encoding="utf-8")
    assert "Not a shortlist" in criteria or "not a shortlist" in criteria.lower()
    assert "L2-C1" in criteria and "L2-C15" in criteria
    assert "L2-C8" in criteria and "L2-C11" in criteria
    assert "Two scores" in criteria or "two scores" in criteria.lower()
    assert "access" in criteria.lower() and "epistemic" in criteria.lower()
    assert "cookbook-risk" in criteria.lower() or "Cookbook-risk" in criteria
    assert "No winner in 1.3.62" in criteria or "unscored" in criteria.lower()
    assert "Do **not** ingest" in criteria
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.62" in parent


def test_layer2_shortlist_scored_from_criteria_no_ingest():
    """1.3.63: shortlist from locked criteria. Cell C is a cell, not a winner. No ingest."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    assert "src.psychological.rudhyar_personality" in aries["pending_source_ids"]
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "1.3.63" in canon
    assert "### 6.17 Layer 2 Signs — shortlist" in canon
    assert "Stopped before step 10" in canon
    shortlist = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_SHORTLIST.md").read_text(encoding="utf-8")
    assert "Not ingest" in shortlist or "not ingest" in shortlist.lower()
    assert "Houlding" in shortlist and "ontology" in shortlist.lower()
    assert "Pulse of Life" in shortlist
    assert "optional / later" in shortlist.lower() or "optional/later" in shortlist.lower()
    assert "No winner" in shortlist or "no winner" in shortlist.lower()
    assert "Arroyo" in shortlist and "Martin" in shortlist and "Hamaker" in shortlist
    assert "Do **not** ingest from this page" in shortlist or "Do **not** ingest" in shortlist
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.63" in parent
    assert "шага 10" in parent


def test_layer2_houlding_ontology_extract_no_sign_objects():
    """1.3.64: Houlding triplicity ontology on classifications only. No rulers, no sign objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    corpus_schema = json.loads(CORPUS_SCHEMA.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    jsonschema.validate(corpus, corpus_schema)
    assert any(src["source_id"] == "src.traditional.houlding_triplicities" for src in corpus["sources"])
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    assert "src.psychological.rudhyar_personality" in aries["pending_source_ids"]
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    houlding = [row for row in classifications["claims"] if row.get("source_id") == "src.traditional.houlding_triplicities"]
    assert len(houlding) == 3
    assert all(row["source_class"] == "traditional" for row in houlding)
    assert all(row["evidence_tier"] == "school_specific" for row in houlding)
    assert all(row["field"] == "element" for row in houlding)
    assert {row["concept_id"] for row in houlding} == {
        "claim.sign.triplicity_trigonal_geometry",
        "claim.sign.elemental_labels_later",
        "claim.sign.no_ptolemy_air_water_sign_labels",
    }
    blob = " ".join((row.get("original_claim") or "") + " " + (row.get("normalized_claim") or "") for row in houlding).lower()
    assert "ruler" not in blob
    assert "dignity" not in blob
    assert "fortune" not in blob
    assert not any(row.get("evidence_tier") == "core" for row in classifications["claims"])
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.18 Layer 2 Signs — Houlding ontology extract" in canon
    assert "Stopped before Pulse Part One" in canon
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.64" in parent


def test_layer2_cell_c_access_blocked_no_ingest():
    """1.3.65: Cell C ACCESS_BLOCKED. No fourth book. No sign objects. Pulse is not this slot."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.arroyo_four_elements" in aries["pending_source_ids"]
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    assert not any(row.get("source_class") == "psychological" for row in classifications["claims"])
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.19 Layer 2 Signs — Cell C ACCESS_BLOCKED" in canon
    assert "### Architecture impact — 1.3.65 Layer 2 Cell C ACCESS_BLOCKED" in canon
    map_text = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_LITERATURE_MAP.md").read_text(encoding="utf-8")
    assert "Layer 2 psychological later-interpretive (Cell C) **is** `ACCESS_BLOCKED`" in map_text
    shortlist = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_SHORTLIST.md").read_text(encoding="utf-8")
    assert "ACCESS_BLOCKED" in shortlist
    assert "No winner" in shortlist or "no winner" in shortlist.lower()
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.65" in parent
    assert "ACCESS_BLOCKED" in parent


def test_layer2_pulse_part_one_extract_no_sign_objects():
    """1.3.66: Pulse Part One humanistic on classifications. No psych slots. No Part Two. No sign objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    claims_schema = json.loads(CLAIMS_SCHEMA.read_text(encoding="utf-8"))
    corpus_schema = json.loads(CORPUS_SCHEMA.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    jsonschema.validate(corpus, corpus_schema)
    assert len(corpus["sources"]) <= 80
    assert any(src["source_id"] == "src.humanistic.rudhyar_pulse_of_life" for src in corpus["sources"])
    pulse_src = next(src for src in corpus["sources"] if src["source_id"] == "src.humanistic.rudhyar_pulse_of_life")
    assert pulse_src["source_class"] == "humanistic"
    planets = [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ]
    total = 0
    psych_n = 0
    core_n = 0
    for name in planets:
        payload = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        jsonschema.validate(payload, claims_schema)
        total += len(payload["claims"])
        psych_n += sum(1 for row in payload["claims"] if row.get("source_class") == "psychological")
        core_n += sum(1 for row in payload["claims"] if row.get("evidence_tier") == "core")
    assert total == 491
    assert psych_n == 82
    assert core_n == 0
    _assert_il1_catalog_counts(objects)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    jsonschema.validate(aries, claims_schema)
    assert "src.psychological.rudhyar_personality" in aries["pending_source_ids"]
    assert not any(row.get("source_id") == "src.humanistic.rudhyar_pulse_of_life" for row in aries["claims"])
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    jsonschema.validate(classifications, claims_schema)
    pulse = [row for row in classifications["claims"] if row.get("source_id") == "src.humanistic.rudhyar_pulse_of_life"]
    assert len(pulse) == 3
    assert all(row["source_class"] == "humanistic" for row in pulse)
    assert all(row["evidence_tier"] == "school_specific" for row in pulse)
    assert {row["field"] for row in pulse} <= {"orientation", "mode"}
    forbidden = ("motivation", "strengths", "excess", "deficiency", "behavioral_tendencies")
    assert not any(row["field"] in forbidden for row in pulse)
    assert {row["concept_id"] for row in pulse} == {
        "claim.sign.zodiac_dynamic_process",
        "claim.sign.day_night_four_turning_points",
        "claim.sign.phase_more_or_less",
    }
    blob = " ".join((row.get("original_claim") or "") + " " + (row.get("normalized_claim") or "") for row in pulse).lower()
    assert "personality type" in blob or "either-or" in blob
    assert "aries =" not in blob
    assert not any(row.get("source_class") == "psychological" for row in pulse)
    assert not any(row.get("evidence_tier") == "core" for row in classifications["claims"])
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.20 Layer 2 Signs — Pulse Part One extract" in canon
    assert "1.3.66" in canon
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.66" in parent


def test_layer2_later_interpretive_optional_no_sign_objects():
    """1.3.67: later-interpretive optional on IL-1 draft type=sign. Not filled from Pulse/QUALITY."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    layer2 = next(
        branch
        for branch in schema["$defs"]["knowledge_object"]["allOf"]
        if branch.get("if", {}).get("properties", {}).get("layer", {}).get("const") == 2
    )
    required = layer2["then"]["required"]
    assert required == ["type", "mode", "element", "orientation"]
    forbidden = ("motivation", "expression", "strengths", "excess", "deficiency", "behavioral_tendencies")
    assert not any(name in required for name in forbidden)
    props = schema["$defs"]["knowledge_object"]["properties"]
    for name in forbidden:
        assert name in props
    _assert_il1_catalog_counts(objects)
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    notes = " ".join(classifications["gap_notes"])
    assert "1.3.67" in notes
    assert "optional on IL-1 draft" in notes
    pulse = [row for row in classifications["claims"] if row.get("source_id") == "src.humanistic.rudhyar_pulse_of_life"]
    assert not any(row["field"] in ("motivation", "strengths", "excess", "deficiency", "behavioral_tendencies") for row in pulse)
    aries = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    assert "optional on IL-1 draft type=sign" in " ".join(aries["gap_notes"])
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.21 Layer 2 Signs — later-interpretive optional on IL-1 draft" in canon
    assert "### Architecture impact — 1.3.67 Layer 2 later-interpretive optional on IL-1 draft" in canon
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.67" in parent
    shortlist = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_SHORTLIST.md").read_text(encoding="utf-8")
    assert "1.3.67" in shortlist


def test_layer2_lilly_classification_drafts_no_later_interpretive():
    """1.3.68: twelve type=sign drafts from Lilly grid. Later-interpretive omitted. Not CORE. Nothing active."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    for name, (mode, element, orientation) in LILLY_SIGN_GRID.items():
        obj = by_id[f"astro.sign.{name}"]
        assert obj["mode"] == mode
        assert obj["element"] == element
        assert obj["orientation"] == orientation
        assert obj["theme_clusters"] == ["timing"]
        assert obj["polarity"] == ["neutral"]
        assert obj["machine_entity_code"] == f"astrology.sign.{name}"
        fields = {row["field"]: row for row in obj["provenance"]}
        assert set(fields) == {"mode", "element", "orientation"}
        assert all(row["source_id"] == "src.classical.lilly_christian_astrology" for row in obj["provenance"])
        assert all(row["evidence_tier"] == "school_specific" for row in obj["provenance"])
        assert all(row["source_class"] == "classical" for row in obj["provenance"])
        blob = " ".join(row["normalized_claim"].lower() for row in obj["provenance"])
        assert "choleric" not in blob
        assert "deceitful" not in blob
        assert "idle" not in blob
        assert "violent" not in blob
    leo_mode = next(row for row in by_id["astro.sign.leo"]["provenance"] if row["field"] == "mode")
    assert leo_mode["concept_id"] == "claim.sign.fixed_follow_turning"
    virgo_mode = next(row for row in by_id["astro.sign.virgo"]["provenance"] if row["field"] == "mode")
    assert virgo_mode["concept_id"] == "claim.sign.bicorporeal"
    aries_elem = next(row for row in by_id["astro.sign.aries"]["provenance"] if row["field"] == "element")
    assert aries_elem["concept_id"] == "claim.sign.aries.lilly_quality"
    aries_claims = json.loads((CLAIMS_DIR / "astro.sign.aries.json").read_text(encoding="utf-8"))
    assert any(row["concept_id"] == "claim.sign.aries.valens_fiery" for row in aries_claims["claims"])
    assert by_id["astro.sign.aries"]["element"] == "fire"
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.22 Layer 2 Signs — Lilly classification drafts" in canon
    assert "### Architecture impact — 1.3.68 Layer 2 Lilly classification drafts" in canon
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.68" in parent


def test_layer2_classification_complete_interpretation_deferred():
    """1.3.69: close-out audit. No ingest. Layer 2 classification-complete / interpretation-deferred."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    signs = [obj for obj in objects["objects"] if obj["type"] == "sign"]
    keysets = {
        tuple(sorted(k for k in obj.keys() if k != "provenance"))
        for obj in signs
    }
    assert len(keysets) == 1
    classifications = json.loads((CLAIMS_DIR / "astro.sign.classifications.json").read_text(encoding="utf-8"))
    class_pairs = {(row["concept_id"], row["source_id"]) for row in classifications["claims"]}
    collision_sources = {
        "src.classical.ptolemy_tetrabiblos",
        "src.classical.valens_anthologies",
        "src.traditional.houlding_triplicities",
        "src.humanistic.rudhyar_pulse_of_life",
    }
    used_class_sources = {row["source_id"] for row in classifications["claims"]}
    assert collision_sources <= used_class_sources
    for obj in signs:
        name = obj["object_id"].split(".")[-1]
        ledger = json.loads((CLAIMS_DIR / f"{obj['object_id']}.json").read_text(encoding="utf-8"))
        claim_pairs = {(row["concept_id"], row["source_id"]) for row in ledger["claims"]}
        quality = next(row for row in ledger["claims"] if row["concept_id"].endswith("lilly_quality"))
        q = quality["original_claim"].lower()
        for row in obj["provenance"]:
            assert (row["concept_id"], row["source_id"]) in claim_pairs | class_pairs
            assert row["source_id"] == "src.classical.lilly_christian_astrology"
            assert row["source_id"] not in collision_sources
            norm = row["normalized_claim"].lower()
            for word in QUALITY_PERSONALITY:
                assert word not in norm, (obj["object_id"], row["field"], word)
        mode_row = next(row for row in obj["provenance"] if row["field"] == "mode")
        if name in {"leo", "virgo"}:
            assert "fixed" not in q and "common" not in q and "moveable" not in q and "cardinal" not in q
            assert mode_row["concept_id"] in {"claim.sign.fixed_follow_turning", "claim.sign.bicorporeal"}
        else:
            assert mode_row["concept_id"].endswith("lilly_quality")
        assert "optional on IL-1 draft type=sign" in " ".join(ledger["gap_notes"])
        assert quality["field"] == "expression"
        assert "expression" not in obj
    notes = " ".join(classifications["gap_notes"])
    assert "1.3.69" in notes
    assert "classification-complete" in notes
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.23 Layer 2 Signs — classification close-out" in canon
    assert "### Architecture impact — 1.3.69 Layer 2 classification-complete / interpretation-deferred" in canon
    closeout = (ROOT / "docs" / "astrology" / "IL1_LAYER2_SIGNS_CLOSEOUT.md").read_text(encoding="utf-8")
    assert "classification-complete / interpretation-deferred" in closeout
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "classification-complete" in next_block
    assert "Do **not** start CORE scoring" in next_block
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.69" in parent
    assert "classification-complete" in parent


def test_layer1_outers_definition_readiness_no_objects():
    """1.3.70: outer definition/readiness. No ingest. No objects. Catalog unchanged."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    ids = {obj["object_id"] for obj in objects["objects"]}
    assert "astro.object.uranus" not in ids
    assert "astro.object.neptune" not in ids
    assert "astro.object.pluto" not in ids
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert "heating" in by_id["astro.object.sun"]["function"]
    assert "structure" not in by_id["astro.object.saturn"]["themes"]
    for name in ("uranus", "neptune", "pluto"):
        claims = json.loads((CLAIMS_DIR / f"astro.object.{name}.json").read_text(encoding="utf-8"))
        assert all(row["evidence_tier"] != "core" for row in claims["claims"])
        notes = " ".join(claims["gap_notes"]).lower()
        assert "object withheld" in notes or "still withheld" in notes
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.24 Layer 1 Outers — definition / readiness" in canon
    assert "### Architecture impact — 1.3.70 Layer 1 outers definition / readiness" in canon
    definition = (ROOT / "docs" / "astrology" / "IL1_LAYER1_OUTERS_DEFINITION.md").read_text(encoding="utf-8")
    assert "Sufficiency bar" in definition
    assert "Do not start from Hand" in definition
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "1.3.70" in parent
    assert "Layer 1 Outers" in parent


def _minimal_outer_draft(object_id: str) -> dict:
    body = object_id.rsplit(".", 1)[-1].capitalize()
    return {
        "object_id": object_id,
        "layer": 1,
        "type": "celestial_object",
        "status": "draft",
        "version": "0.1.0",
        "phenomenon": body,
        "machine_entity_code": f"astrology.planet.{body.lower()}",
        "theme_clusters": ["timing"],
        "polarity": ["neutral"],
        "temporal_class": "natal",
        "confidence": None,
        "composed_from": [],
        "curation_reason": None,
        "provenance": [
            {
                "concept_id": f"claim.{body.lower()}.structural_identity",
                "source_id": "schema_example",
                "source_class": "internal_normalization",
                "author": None,
                "edition": None,
                "locus": None,
                "school": None,
                "original_claim": "Structural identity only — not a school function package",
                "normalized_claim": f"{body} is a calc-emitted lookup primitive",
                "evidence_tier": "editorial",
                "review_status": "extracted",
                "field": "phenomenon",
            }
        ],
    }


def _minimal_sign_draft(object_id: str = "astro.sign.aries") -> dict:
    body = object_id.rsplit(".", 1)[-1]
    return {
        "object_id": object_id,
        "layer": 2,
        "type": "sign",
        "status": "draft",
        "version": "0.1.0",
        "phenomenon": body.capitalize(),
        "machine_entity_code": f"astrology.sign.{body}",
        "theme_clusters": ["timing"],
        "polarity": ["neutral"],
        "temporal_class": "natal",
        "confidence": None,
        "composed_from": [],
        "curation_reason": None,
        "mode": "cardinal",
        "element": "fire",
        "orientation": "positive",
        "provenance": [
            {
                "concept_id": f"claim.sign.{body}.lilly_quality",
                "source_id": "src.classical.lilly_christian_astrology",
                "source_class": "classical",
                "author": "William Lilly",
                "edition": "Christian Astrology 1659; Wikisource p.93–98",
                "school": "traditional_horary",
                "reviewer": None,
                "reviewed_at": None,
                "locus": "Book I Chapter XVI",
                "original_claim": "Classification-only illustration — not a Canon pack",
                "normalized_claim": f"Lilly's {body.capitalize()} is cardinal",
                "evidence_tier": "school_specific",
                "review_status": "extracted",
                "field": "mode",
            }
        ],
    }


def _minimal_house_draft(object_id: str = "astro.house.04") -> dict:
    number = object_id.rsplit(".", 1)[-1]
    return {
        "object_id": object_id,
        "layer": 3,
        "type": "house",
        "status": "draft",
        "version": "0.1.0",
        "phenomenon": f"{int(number)}th house",
        "machine_entity_code": f"astrology.house.{number}",
        "theme_clusters": ["home"],
        "polarity": ["neutral"],
        "temporal_class": "natal",
        "confidence": None,
        "composed_from": [],
        "curation_reason": None,
        "domain": "father, land, hidden things, and endings",
        "internal_meaning": "fathers, inheritances, the earth, hidden treasure, and the end of a matter",
        "external_manifestations": ["lands, houses, tenements, tillage"],
        "people": ["fathers in general"],
        "activities": ["tillage"],
        "resources": ["lands, hidden treasure, ancient dwellings"],
        "risks": ["barren, stony or woody ground when so signified"],
        "provenance": [
            {
                "concept_id": f"claim.house.{number}.lilly_domain",
                "source_id": "src.classical.lilly_christian_astrology",
                "source_class": "classical",
                "author": "William Lilly",
                "edition": "Christian Astrology 1659; Wikisource",
                "school": "traditional_horary",
                "reviewer": None,
                "reviewed_at": None,
                "locus": "Book I Chapter VII",
                "original_claim": "Classification-only illustration — not a Canon pack",
                "normalized_claim": "Lilly house domain remains classical prose",
                "evidence_tier": "school_specific",
                "review_status": "extracted",
                "field": "domain",
            }
        ],
    }


def _minimal_aspect_draft(object_id: str = "astro.aspect.square") -> dict:
    name = object_id.rsplit(".", 1)[-1]
    return {
        "object_id": object_id,
        "layer": 4,
        "type": "aspect",
        "status": "draft",
        "version": "0.1.0",
        "phenomenon": name,
        "machine_entity_code": f"astrology.aspect.{name}",
        "theme_clusters": ["power"],
        "polarity": ["challenging"],
        "temporal_class": "natal",
        "confidence": None,
        "composed_from": [],
        "curation_reason": None,
        "angle": 90,
        "interaction": "friction",
        "requires_action": False,
        "provenance": [
            {
                "concept_id": f"claim.aspect.{name}.interaction",
                "source_id": "src.classical.ptolemy_tetrabiblos",
                "source_class": "classical",
                "author": "Claudius Ptolemy / J.M. Ashmand trans.",
                "edition": "Ashmand 1822; Gutenberg ebook 70850",
                "school": "hellenistic",
                "reviewer": None,
                "reviewed_at": None,
                "locus": "Tetrabiblos Book I Chapter XIII",
                "original_claim": "Classification-only illustration — not a Canon pack",
                "normalized_claim": "Stored interaction remains classical grain",
                "evidence_tier": "school_specific",
                "review_status": "extracted",
                "field": "interaction",
            }
        ],
    }


def test_outer_planet_draft_representation_optional_on_draft():
    """1.3.72: outer meaning keys optional on draft. Sun–Saturn still required. No objects yet."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    ids = {obj["object_id"] for obj in objects["objects"]}
    for object_id in OUTER_OBJECT_IDS:
        assert object_id not in ids
        draft = _minimal_outer_draft(object_id)
        for key in OUTER_MEANING_KEYS:
            assert key not in draft
        jsonschema.validate({"contract_version": "astrology_interpretation_v1", "objects": [draft]}, schema)

    sun = next(obj for obj in objects["objects"] if obj["object_id"] == "astro.object.sun")
    stripped = {k: v for k, v in sun.items() if k != "function"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"contract_version": "astrology_interpretation_v1", "objects": [stripped]}, schema)

    fake = _minimal_outer_draft("astro.object.uranus")
    fake["function"] = "change, rebellion, freedom"
    jsonschema.validate({"contract_version": "astrology_interpretation_v1", "objects": [fake]}, schema)
    # Schema may accept the string; fill-rule forbids writing it. Catalog must not contain it.
    assert all(
        "change, rebellion" not in obj.get("function", "")
        for obj in objects["objects"]
        if obj["type"] == "celestial_object"
    )

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.26 Outer Planet Draft Representation" in canon
    representation = (ROOT / "docs" / "astrology" / "IL1_OUTER_PLANET_DRAFT_REPRESENTATION.md").read_text(
        encoding="utf-8"
    )
    assert "optional on draft" in representation.lower()
    assert "Do not collapse" in representation or "synthetic collapse" in representation.lower()
    inventory = (ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md").read_text(
        encoding="utf-8"
    )
    assert "**APPROVED**" in inventory
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.72" in next_block
    assert "Do **not** start CORE scoring" in next_block


def test_todayflow_canon_semantic_selection_no_objects():
    """1.3.73: TodayFlow Canon methodology. CORE demoted. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    ids = {obj["object_id"] for obj in objects["objects"]}
    assert "astro.object.uranus" not in ids
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.27 TodayFlow Canon" in canon
    assert "research characteristic" in canon
    method = (ROOT / "docs" / "astrology" / "TODAYFLOW_CANON_V1.md").read_text(encoding="utf-8")
    assert "prevalence" in method.lower()
    assert "recognition" in method.lower()
    assert "distinctiveness" in method.lower()
    assert "composability" in method.lower()
    assert "LLM does not decide" in method
    assert "not a permission bit" in method.lower() or "not a permission bit" in canon.lower()
    parent = (ROOT / "docs" / "KNOWLEDGE_CORE_RESEARCH_ORDER_V1.md").read_text(encoding="utf-8")
    assert "TodayFlow Canon" in parent
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.73" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_todayflow_three_layers_corpus_consensus_canon():
    """1.3.74: Evidence Corpus / Semantic Consensus / TodayFlow Canon. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.28 Three layers" in canon
    method = (ROOT / "docs" / "astrology" / "TODAYFLOW_CANON_V1.md").read_text(encoding="utf-8")
    assert "## 0. Three layers" in method
    assert "Evidence Corpus" in method
    assert "Semantic Consensus" in method
    assert "TodayFlow Canon" in method
    assert "cheap inference" in method.lower()
    assert "swappable LLM" in method.lower() or "swappable LLM" in method
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.74" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "research cycle" in next_block.lower()


def test_il_architecture_frozen_pending_costar_teardown():
    """1.3.75: freeze IL architecture; Co-Star teardown is next. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.29 IL architecture frozen" in canon
    teardown = (
        ROOT / "docs" / "audits" / "COSTAR_SEMANTIC_CONTENT_ENGINE_TEARDOWN_V1.md"
    ).read_text(encoding="utf-8")
    assert "Astrology model" in teardown
    assert "Semantic model" in teardown
    assert "Content engine" in teardown
    assert "Product psychology" in teardown
    assert "Calculation" in teardown
    assert "Meaning" in teardown
    inventory = (
        ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_SEMANTIC_INVENTORY.md"
    ).read_text(encoding="utf-8")
    assert "Co–Star" in inventory or "Co-Star" in inventory
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.75" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "teardown" in next_block.lower()


def test_product_canon_vs_lenses_mainstream_not_objects():
    """1.3.76: Product Canon vs Lenses. Mainstream convention. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.30 Product Canon vs Lenses" in canon
    split = (
        ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md"
    ).read_text(encoding="utf-8")
    assert "Mainstream meaning" in split
    assert "Lenses" in split
    assert "not a product gate" in split.lower() or "not a gate" in split.lower()
    assert "Astrodienst" in split
    assert "Cafe Astrology" in split
    assert "self · identity · vitality" in split
    method = (ROOT / "docs" / "astrology" / "TODAYFLOW_CANON_V1.md").read_text(encoding="utf-8")
    assert "Mainstream V1" in method
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.76" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "Mainstream" in next_block


def test_mainstream_planet_semantic_map_v1():
    """1.3.77: Mainstream planet map. Concept families. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.31 Mainstream Planet Semantic Map" in canon
    planet_map = (
        ROOT / "docs" / "astrology" / "MAINSTREAM_PLANET_SEMANTIC_MAP_V1.md"
    ).read_text(encoding="utf-8")
    assert "Astrology.com" in planet_map
    assert "concept family" in planet_map.lower() or "concept families" in planet_map.lower()
    assert "2/3" in planet_map
    assert "self · identity · vitality" in planet_map
    assert "power · intensity · compulsion" in planet_map
    assert "Not JSON" in planet_map or "not JSON" in planet_map
    assert "core function" in planet_map.lower()
    split = (
        ROOT / "docs" / "astrology" / "KNOWLEDGE_CORE_V1_PRODUCT_CANON_AND_LENSES.md"
    ).read_text(encoding="utf-8")
    assert "Astrology.com" in split
    assert "2/3 literal-word" in split.lower() or "2/3 literal" in split.lower()
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.77" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_planet_canon_grammar_v1():
    """1.3.78: Planet Canon grammar. Six slots. tempo out. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.32 Planet Canon grammar" in canon
    grammar = (ROOT / "docs" / "astrology" / "PLANET_CANON_GRAMMAR_V1.md").read_text(
        encoding="utf-8"
    )
    assert "core_function" in grammar
    assert "drive" in grammar
    assert "needs" in grammar
    assert "constructive" in grammar
    assert "distorted" in grammar
    assert "domains" in grammar
    assert "tempo" in grammar.lower()
    assert "not a Canon slot" in grammar or "not Canon" in grammar
    assert "needs` ≠ `drive" in grammar or "needs ≠ drive" in grammar
    assert "Dry-run" in grammar or "dry-run" in grammar
    assert "1.3.79" in grammar
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.78" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_planet_canon_v1_fill_with_provenance():
    """1.3.79: Planet Canon V1 packs + direct/derived. No ingest. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.33 Planet Canon V1" in canon
    packs = (ROOT / "docs" / "astrology" / "PLANET_CANON_V1.md").read_text(encoding="utf-8")
    assert "direct" in packs
    assert "derived" in packs
    assert "direct-secondary" in packs
    assert "achievement" in packs
    assert "coercive-control" in packs
    assert "openness-to-opportunity" in packs
    assert "appeasement" in packs
    assert "dogmatism" in packs
    assert "containment" in packs
    assert "### Sun" in packs
    assert "### Pluto" in packs
    assert "Sun ↔ Mars" in packs
    assert "Saturn ↔ Pluto" in packs
    assert "schema pass" in packs.lower()
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.79" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_planet_canon_storage_v1():
    """1.3.80: optional canon nest. Grammar names unchanged. No object fill."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    jsonschema.validate(example, schema)
    _assert_il1_catalog_counts(objects)

    pack = schema["$defs"]["canon_pack"]
    for key in ("core_function", "drive", "needs", "constructive", "distorted", "domains"):
        assert key in pack["required"]
        assert key in pack["properties"]
    assert "tempo" not in pack["properties"]
    assert "canon" in schema["$defs"]["knowledge_object"]["properties"]
    assert "canon" not in schema["$defs"]["knowledge_object"]["required"]

    for obj in objects["objects"]:
        if obj["type"] not in ("celestial_object", "sign", "house", "aspect"):
            assert "canon" not in obj

    saturn_ex = next(obj for obj in example["objects"] if obj["object_id"] == "astro.object.saturn")
    assert set(saturn_ex["canon"]) == {
        "core_function",
        "drive",
        "needs",
        "constructive",
        "distorted",
        "domains",
    }
    assert saturn_ex["function"] == "structure, limits, time, responsibility"
    assert isinstance(saturn_ex["domains"], dict)
    assert isinstance(saturn_ex["canon"]["domains"], list)

    partial = dict(saturn_ex)
    partial["canon"] = {
        "core_function": ["limit"],
        "drive": ["order"],
        "needs": ["boundaries"],
        "constructive": ["form"],
        "distorted": ["rigidity"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [partial]},
            schema,
        )

    outer = _minimal_outer_draft("astro.object.uranus")
    outer["canon"] = {
        "core_function": ["change", "disrupt"],
        "drive": ["freedom"],
        "needs": ["autonomy"],
        "constructive": ["innovation"],
        "distorted": ["disruption"],
        "domains": ["change", "freedom", "innovation"],
    }
    jsonschema.validate({"contract_version": "astrology_interpretation_v1", "objects": [outer]}, schema)

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.34 Planet Canon storage" in canon
    storage = (ROOT / "docs" / "astrology" / "PLANET_CANON_STORAGE_V1.md").read_text(encoding="utf-8")
    assert "canon.core_function" in storage
    assert "four natal keys" in storage.lower() or "Four natal keys" in storage
    assert "object fill" in storage.lower()
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.80" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


SUN_SATURN_CANON_PACKS = {
    "astro.object.sun": {
        "core_function": ["identify", "vitalize", "will"],
        "drive": ["purpose", "self-coherence"],
        "needs": ["center", "continuity"],
        "constructive": ["vitality", "integrity", "self-direction"],
        "distorted": ["ego-inflation", "will-excess", "depletion"],
        "domains": ["self", "identity", "vitality", "purpose"],
    },
    "astro.object.moon": {
        "core_function": ["feel", "respond", "protect"],
        "drive": ["safety"],
        "needs": ["familiarity", "responsiveness"],
        "constructive": ["attunement", "protection", "instinct"],
        "distorted": ["fusion", "clinging", "reactivity"],
        "domains": ["emotions", "needs", "security", "the-familiar"],
    },
    "astro.object.mercury": {
        "core_function": ["think", "communicate", "learn"],
        "drive": ["sense-making", "exchange"],
        "needs": ["input", "channel"],
        "constructive": ["clarity", "curiosity", "skill"],
        "distorted": ["noise", "rumination", "pedantry"],
        "domains": ["thinking", "communication", "learning", "information"],
    },
    "astro.object.venus": {
        "core_function": ["attract", "value", "relate"],
        "drive": ["pleasure", "bond"],
        "needs": ["reciprocity", "worth"],
        "constructive": ["affection", "taste", "fairness"],
        "distorted": ["appeasement", "indulgence", "vanity"],
        "domains": ["love", "attraction", "relationships", "values", "pleasure"],
    },
    "astro.object.mars": {
        "core_function": ["act", "pursue", "assert"],
        "drive": ["agency", "desire"],
        "needs": ["autonomy", "outlet"],
        "constructive": ["courage", "initiative", "decisiveness"],
        "distorted": ["aggression", "impulsivity", "force"],
        "domains": ["action", "desire", "competition", "confrontation"],
    },
    "astro.object.jupiter": {
        "core_function": ["expand", "believe"],
        "drive": ["growth", "opportunity", "meaning"],
        "needs": ["horizon", "faith"],
        "constructive": ["generosity", "perspective", "openness-to-opportunity"],
        "distorted": ["excess", "inflation", "dogmatism"],
        "domains": ["growth", "opportunity", "belief", "meaning"],
    },
    "astro.object.saturn": {
        "core_function": ["limit", "structure", "mature"],
        "drive": ["order"],
        "needs": ["boundaries", "realism"],
        "constructive": ["responsibility", "discipline", "form"],
        "distorted": ["rigidity", "inhibition", "severity"],
        "domains": ["limits", "structure", "responsibility", "discipline"],
    },
}

CLASSICAL_FUNCTION = {
    "astro.object.sun": "heating quality with moderate dryness",
    "astro.object.moon": "moistening quality acting close to earth and bodies",
    "astro.object.mercury": "convertible quality taking the nature of what it joins",
    "astro.object.venus": "moist temperate quality disposed to pleasure and company",
    "astro.object.mars": "heating and drying quality that contends",
    "astro.object.jupiter": "temperate warming and moistening quality",
    "astro.object.saturn": "cooling quality operating by distance from heat",
}


def test_planet_canon_sun_saturn_fill():
    """1.3.81: copy locked packs onto object.canon. No function rewrite. Next = 1.3.82 smoke-test."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}

    for object_id, pack in SUN_SATURN_CANON_PACKS.items():
        obj = by_id[object_id]
        assert obj["status"] == "draft"
        assert obj["canon"] == pack
        assert obj["function"] == CLASSICAL_FUNCTION[object_id]
        assert isinstance(obj["domains"], dict)
        assert set(obj["domains"]) == {"relationships", "money", "work", "self"}

    mars_lemmas = " ".join(" ".join(v) for v in by_id["astro.object.mars"]["canon"].values())
    assert "achievement" not in mars_lemmas
    assert "will" not in by_id["astro.object.mars"]["canon"]["core_function"]
    assert "control" not in by_id["astro.object.saturn"]["canon"]["drive"]
    assert "purpose" not in by_id["astro.object.jupiter"]["canon"]["drive"]
    assert "safety" in by_id["astro.object.moon"]["canon"]["drive"]
    assert "affection" in by_id["astro.object.venus"]["canon"]["constructive"]

    for obj in objects["objects"]:
        if obj["type"] not in ("celestial_object", "sign", "house", "aspect"):
            assert "canon" not in obj
    for object_id in ("astro.object.uranus", "astro.object.neptune", "astro.object.pluto"):
        assert object_id not in by_id

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.35 Planet Canon Sun–Saturn fill" in canon
    fill = (ROOT / "docs" / "astrology" / "PLANET_CANON_SUN_SATURN_FILL_V1.md").read_text(
        encoding="utf-8"
    )
    assert "1.3.82" in fill
    assert "object.canon" in fill
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.81" in next_block
    assert "1.3.82" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "Signs Mainstream" in next_block or "start Signs" in next_block


def test_mainstream_sign_semantic_map_v1():
    """1.3.83: Mainstream sign map. Concept families. No ingest. No objects. No manner."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.37 Mainstream Sign Semantic Map" in canon
    sign_map = (
        ROOT / "docs" / "astrology" / "MAINSTREAM_SIGN_SEMANTIC_MAP_V1.md"
    ).read_text(encoding="utf-8")
    assert "Astrology.com" in sign_map
    assert "Astrodienst" in sign_map
    assert "Cafe Astrology" in sign_map
    assert "concept family" in sign_map.lower() or "concept families" in sign_map.lower()
    assert "earth" in sign_map.lower() and "practical" in sign_map.lower()
    assert "cardinal" in sign_map.lower() and "initiating" in sign_map.lower()
    assert "trait ≠ manner" in sign_map.lower() or "Trait ≠ manner" in sign_map
    assert "ambition · discipline · endurance" in sign_map
    assert "initiative · energy · courage" in sign_map
    assert "Not JSON" in sign_map or "not JSON" in sign_map
    assert "manner operator" in sign_map.lower() or "manner" in sign_map.lower()
    for sign in (
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ):
        assert f"### {sign}" in sign_map
        assert "**Include**" in sign_map
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    cap = by_id["astro.sign.capricorn"]
    assert cap["mode"] == "cardinal"
    assert cap["element"] == "earth"
    assert cap["orientation"] == "negative"
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.83" in next_block
    assert "1.3.84" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "Sign Canon Grammar" in next_block or "Sign Canon grammar" in next_block


def test_mainstream_house_semantic_map_v1():
    """1.3.89: Mainstream house map. Concept families. No ingest. No objects. No Canon slots."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.43 Mainstream House Semantic Map" in canon
    assert "**Версия:** 1.3.98" in canon
    house_map = (
        ROOT / "docs" / "astrology" / "MAINSTREAM_HOUSE_SEMANTIC_MAP_V1.md"
    ).read_text(encoding="utf-8")
    assert "Astrology.com" in house_map
    assert "Astrodienst" in house_map
    assert "Cafe Astrology" in house_map
    assert "concept family" in house_map.lower() or "concept families" in house_map.lower()
    assert "House 1 ≠ ASC" in house_map
    assert "1st = Aries" in house_map
    assert "Lilly" in house_map
    assert "Foundation §2.3" in house_map
    assert "angular" in house_map.lower()
    assert "Not JSON" in house_map or "not JSON" in house_map
    assert "home · family · roots · private-base" in house_map
    assert "career · public-role · reputation · calling" in house_map
    assert "daily-work / job" in house_map and "career / public-role" in house_map
    for heading in (
        "1st House",
        "2nd House",
        "3rd House",
        "4th House",
        "5th House",
        "6th House",
        "7th House",
        "8th House",
        "9th House",
        "10th House",
        "11th House",
        "12th House",
    ):
        assert f"### {heading}" in house_map
        assert "**Include**" in house_map
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.house.04"]["domain"] == "father, land, hidden things, and endings"
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.89" in next_block
    assert "1.3.88" in next_block
    assert "1.3.82" in next_block
    assert "House Canon Grammar" in next_block or "House Canon grammar" in next_block
    assert "Sign Canon fill" in next_block
    assert "Sign Canon storage" in next_block
    assert "Sign Canon grammar" in next_block
    assert "Planet × Sign" in next_block
    assert "Mainstream" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Signs" in next_block


def test_house_canon_grammar_v1():
    """1.3.90: House Canon grammar. One slot (arena). Not fill. Not objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.44 House Canon grammar" in canon
    assert "**Версия:** 1.3.98" in canon
    grammar = (ROOT / "docs" / "astrology" / "HOUSE_CANON_GRAMMAR_V1.md").read_text(
        encoding="utf-8"
    )
    assert "**arena**" in grammar
    assert "Deletion test" in grammar
    assert "**Surplus**" in grammar
    assert "planet.domains" in grammar or "planet.canon.domains" in grammar
    assert "House ≠ Sign" in grammar
    assert "House ≠ Angle" in grammar or "1st ≠ ASC" in grammar
    assert "Moon × 4th" in grammar
    assert "Moon × 10th" in grammar
    assert "Mars × 4th" in grammar
    assert "Venus × 4th" in grammar
    assert "Venus × 5th" in grammar
    assert "Venus × 7th" in grammar
    assert "Mercury × 3rd" in grammar
    assert "Mercury × 9th" in grammar
    assert "Saturn × 10th" in grammar
    assert "not locked" in grammar.lower() or "Dry-run" in grammar
    assert "One. Not two." in grammar or "One required slot" in grammar
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.house.04"]["domain"] == "father, land, hidden things, and endings"
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.90" in next_block
    assert "1.3.89" in next_block
    assert "House Canon fill" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Signs" in next_block


def test_house_canon_v1_fill_with_provenance():
    """1.3.91: House Canon V1 packs + origin. Five gates. No schema. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.45 House Canon V1 fill" in canon
    assert "**Версия:** 1.3.98" in canon
    packs = (ROOT / "docs" / "astrology" / "HOUSE_CANON_V1.md").read_text(encoding="utf-8")
    assert "direct" in packs
    assert "Destination noun" in packs or "destination noun" in packs.lower()
    for heading in (
        "1st House",
        "2nd House",
        "3rd House",
        "4th House",
        "5th House",
        "6th House",
        "7th House",
        "8th House",
        "9th House",
        "10th House",
        "11th House",
        "12th House",
    ):
        assert f"### {heading}" in packs
        assert "arena:" in packs
    fourth = packs.split("### 4th House")[1].split("### 5th House")[0]
    fourth_arena = fourth.split("```text")[1].split("```")[0]
    assert "home" in fourth_arena
    assert "family" in fourth_arena
    assert "roots" in fourth_arena
    assert "private-base" in fourth_arena
    assert "emotional" not in fourth_arena
    assert "seek" not in fourth_arena
    assert "Cancer" not in fourth_arena
    tenth = packs.split("### 10th House")[1].split("### 11th House")[0]
    tenth_arena = tenth.split("```text")[1].split("```")[0]
    assert "career" in tenth_arena
    assert "public-role" in tenth_arena
    assert "home" not in tenth_arena
    sixth = packs.split("### 6th House")[1].split("### 7th House")[0]
    sixth_arena = sixth.split("```text")[1].split("```")[0]
    assert "daily-work" in sixth_arena
    assert "career" not in sixth_arena
    second = packs.split("### 2nd House")[1].split("### 3rd House")[0]
    second_arena = second.split("```text")[1].split("```")[0]
    eighth = packs.split("### 8th House")[1].split("### 9th House")[0]
    eighth_arena = eighth.split("```text")[1].split("```")[0]
    assert "personal-resources" in second_arena
    assert "shared-resources" in eighth_arena
    assert "shared-resources" not in second_arena
    fifth = packs.split("### 5th House")[1].split("### 6th House")[0]
    fifth_arena = fifth.split("```text")[1].split("```")[0]
    seventh = packs.split("### 7th House")[1].split("### 8th House")[0]
    seventh_arena = seventh.split("```text")[1].split("```")[0]
    assert "romance" in fifth_arena
    assert "partnership" in seventh_arena
    assert "partnership" not in fifth_arena
    assert "Moon × 4th" in packs
    assert "Mars × 4th" in packs
    assert "Venus × 4th" in packs
    assert "seek emotional security at home" in packs
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.house.04"]["domain"] == "father, land, hidden things, and endings"
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.91" in next_block
    assert "1.3.90" in next_block
    assert "House Canon storage" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Signs" in next_block


def test_sign_canon_grammar_v1():
    """1.3.84: Sign Canon grammar. Two slots. Not fill. Not objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(encoding="utf-8")
    assert "### 6.38 Sign Canon grammar" in canon
    assert "**Версия:** 1.3.98" in canon
    grammar = (ROOT / "docs" / "astrology" / "SIGN_CANON_GRAMMAR_V1.md").read_text(
        encoding="utf-8"
    )
    assert "**manner**" in grammar
    assert "**excess**" in grammar
    assert "core_function" in grammar.lower()
    assert "drive / aim" in grammar or "**Surplus**" in grammar
    assert "Venus × Capricorn" in grammar
    assert "Mars × Aries" in grammar
    assert "Mercury × Gemini" in grammar
    assert "Moon × Cancer" in grammar
    assert "Venus × Scorpio" in grammar
    assert "Jupiter × Sagittarius" in grammar
    assert "Mercury × Pisces" in grammar
    assert "Saturn × Aquarius" in grammar
    assert "Deletion test" in grammar
    assert "earth" in grammar.lower()
    assert "not locked" in grammar.lower() or "Dry-run" in grammar
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.sign.capricorn"]["mode"] == "cardinal"
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.84" in next_block
    assert "1.3.85" in next_block
    assert "Sign Canon fill" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_sign_canon_v1_fill_with_provenance():
    """1.3.85: Sign Canon V1 packs + origin. Four gates. No schema. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.39 Sign Canon V1 fill" in canon
    assert "**Версия:** 1.3.98" in canon
    packs = (ROOT / "docs" / "astrology" / "SIGN_CANON_V1.md").read_text(encoding="utf-8")
    assert "direct" in packs
    assert "derived" in packs
    assert "direct-secondary" in packs
    for sign in (
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ):
        assert f"### {sign}" in packs
        assert "manner:" in packs
        assert "excess:" in packs
    assert "reserved · disciplined · structured" in packs
    assert "intense · probing · concentrated" in packs
    cap = packs.split("### Capricorn")[1].split("### Aquarius")[0]
    cap_manner = cap.split("```text")[1].split("```")[0]
    assert "reserved" in cap_manner
    assert "disciplined" in cap_manner
    assert "structured" in cap_manner
    assert "ambition" not in cap_manner
    assert "achievement" not in cap_manner
    assert "ambition / achievement" in cap
    gemini_manner = packs.split("### Gemini")[1].split("```text")[1].split("```")[0]
    assert "communicate" not in gemini_manner
    assert "think" not in gemini_manner
    aries_manner = packs.split("### Aries")[1].split("```text")[1].split("```")[0]
    assert "assert" not in aries_manner
    assert "act" not in aries_manner
    assert "Mercury × Capricorn" in packs
    assert "Mars × Capricorn" in packs
    assert "Moon × Capricorn" in packs
    assert "Venus × Scorpio" in packs
    assert "Origin control" in packs
    assert "Domicile collision" in packs
    assert "Discrimination" in packs
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.85" in next_block
    assert "Sign Canon storage" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


def test_sign_canon_storage_v1():
    """1.3.86: optional sign_canon_pack. Grammar names unchanged. No object fill."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    jsonschema.validate(example, schema)
    _assert_il1_catalog_counts(objects)

    pack = schema["$defs"]["sign_canon_pack"]
    assert pack["required"] == ["manner", "excess"]
    assert "core_function" not in pack["properties"]
    assert "canon" in schema["$defs"]["knowledge_object"]["properties"]
    assert "canon" not in schema["$defs"]["knowledge_object"]["required"]

    for obj in objects["objects"]:
        if obj["type"] == "sign":
            for key in LATER_INTERPRETIVE_KEYS:
                assert key not in obj

    cap_ex = next(obj for obj in example["objects"] if obj["object_id"] == "astro.sign.capricorn")
    assert cap_ex["canon"] == {
        "manner": ["reserved", "disciplined", "structured"],
        "excess": ["withholding", "hardening"],
    }
    assert "excess" not in cap_ex
    assert cap_ex["mode"] == "cardinal"
    saturn_ex = next(obj for obj in example["objects"] if obj["object_id"] == "astro.object.saturn")
    assert "manner" not in saturn_ex["canon"]

    sign = _minimal_sign_draft("astro.sign.capricorn")
    sign["mode"] = "cardinal"
    sign["element"] = "earth"
    sign["orientation"] = "negative"
    sign["canon"] = {
        "manner": ["reserved", "disciplined", "structured"],
        "excess": ["withholding", "hardening"],
    }
    jsonschema.validate(
        {"contract_version": "astrology_interpretation_v1", "objects": [sign]},
        schema,
    )

    partial = dict(sign)
    partial["canon"] = {"manner": ["reserved"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [partial]},
            schema,
        )

    planet_pack_on_sign = dict(sign)
    planet_pack_on_sign["canon"] = {
        "core_function": ["limit"],
        "drive": ["order"],
        "needs": ["boundaries"],
        "constructive": ["form"],
        "distorted": ["rigidity"],
        "domains": ["limits"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [planet_pack_on_sign]},
            schema,
        )

    sign_pack_on_planet = dict(saturn_ex)
    sign_pack_on_planet["canon"] = {
        "manner": ["reserved"],
        "excess": ["hardening"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [sign_pack_on_planet]},
            schema,
        )

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.40 Sign Canon storage" in canon
    storage = (ROOT / "docs" / "astrology" / "SIGN_CANON_STORAGE_V1.md").read_text(
        encoding="utf-8"
    )
    assert "canon.manner" in storage
    assert "later-interpretive" in storage.lower()
    assert "object fill" in storage.lower()
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.86" in next_block
    assert "1.3.87" in next_block or "1.3.88" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


SIGN_CANON_PACKS = {
    "astro.sign.aries": {
        "manner": ["initiating", "direct", "headlong"],
        "excess": ["premature-charge", "over-direct"],
    },
    "astro.sign.taurus": {
        "manner": ["slow-and-steady", "steadfast", "patient"],
        "excess": ["immovable", "over-holding"],
    },
    "astro.sign.gemini": {
        "manner": ["mobile", "versatile", "switching"],
        "excess": ["scattered", "unstaying"],
    },
    "astro.sign.cancer": {
        "manner": ["close", "indirect", "holding"],
        "excess": ["clinging", "sideways-defense"],
    },
    "astro.sign.leo": {
        "manner": ["central", "warm", "displayed"],
        "excess": ["over-display", "center-demand"],
    },
    "astro.sign.virgo": {
        "manner": ["precise", "discerning", "utilitarian"],
        "excess": ["over-critique", "over-refine"],
    },
    "astro.sign.libra": {
        "manner": ["balancing", "tactful", "proportionate"],
        "excess": ["indecision", "over-accommodation"],
    },
    "astro.sign.scorpio": {
        "manner": ["intense", "probing", "concentrated"],
        "excess": ["possessive", "corrosive"],
    },
    "astro.sign.sagittarius": {
        "manner": ["exploratory", "free", "far-ranging"],
        "excess": ["uncommitted-ranging", "overshoot"],
    },
    "astro.sign.capricorn": {
        "manner": ["reserved", "disciplined", "structured"],
        "excess": ["withholding", "hardening"],
    },
    "astro.sign.aquarius": {
        "manner": ["detached", "unconventional", "original"],
        "excess": ["cold-distance", "idea-obstinacy"],
    },
    "astro.sign.pisces": {
        "manner": ["permeable", "imaginal", "adaptive"],
        "excess": ["unfocused", "impression-as-fact"],
    },
}


def test_sign_canon_materialization_v1():
    """1.3.87: copy locked packs onto sign object.canon. No lemma rewrite. Next = 1.3.88 smoke-test."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    _assert_il1_catalog_counts(objects)
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}

    for object_id, pack in SIGN_CANON_PACKS.items():
        obj = by_id[object_id]
        assert obj["status"] == "draft"
        assert obj["canon"] == pack
        assert obj["mode"] in ("cardinal", "fixed", "mutable")
        assert obj["element"] in ("fire", "earth", "air", "water")
        assert obj["orientation"] in ("positive", "negative")
        for key in LATER_INTERPRETIVE_KEYS:
            assert key not in obj

    cap = by_id["astro.sign.capricorn"]
    assert cap["mode"] == "cardinal"
    assert cap["element"] == "earth"
    assert cap["orientation"] == "negative"
    assert "ambition" not in cap["canon"]["manner"]
    assert "communicate" not in by_id["astro.sign.gemini"]["canon"]["manner"]
    assert "assert" not in by_id["astro.sign.aries"]["canon"]["manner"]
    assert cap["canon"]["excess"] == ["withholding", "hardening"]

    for obj in objects["objects"]:
        if obj["type"] not in ("celestial_object", "sign", "house", "aspect"):
            assert "canon" not in obj
    for object_id, pack in SUN_SATURN_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == pack

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.41 Sign Canon materialization" in canon
    fill = (ROOT / "docs" / "astrology" / "SIGN_CANON_MATERIALIZATION_V1.md").read_text(
        encoding="utf-8"
    )
    assert "1.3.88" in fill
    assert "object.canon" in fill
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.87" in next_block
    assert "1.3.88" in next_block
    assert "Planet × Sign" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block


HOUSE_CANON_PACKS = {
    "astro.house.01": {"arena": ["self-presentation", "appearance", "first-impression"]},
    "astro.house.02": {"arena": ["possessions", "money", "personal-resources"]},
    "astro.house.03": {"arena": ["everyday-communication", "siblings-neighbors", "local-learning"]},
    "astro.house.04": {"arena": ["home", "family", "roots", "private-base"]},
    "astro.house.05": {"arena": ["play", "creativity", "romance"]},
    "astro.house.06": {"arena": ["daily-work", "routine", "health-maintenance"]},
    "astro.house.07": {"arena": ["partnership", "one-to-one", "contracts"]},
    "astro.house.08": {"arena": ["shared-resources", "crisis", "intimacy"]},
    "astro.house.09": {"arena": ["philosophy", "far-travel", "higher-learning"]},
    "astro.house.10": {"arena": ["career", "public-role", "reputation", "calling"]},
    "astro.house.11": {"arena": ["friends", "groups", "community"]},
    "astro.house.12": {"arena": ["hidden", "retreat", "behind-the-scenes"]},
}

ASPECT_CANON_PACKS = {
    "astro.aspect.conjunction": {"relation": ["blend", "fuse", "immediate-connection"]},
    "astro.aspect.opposition": {"relation": ["polarity", "facing", "the-other"]},
    "astro.aspect.square": {"relation": ["friction", "blockage", "cross-purposes"]},
    "astro.aspect.trine": {"relation": ["easy-flow", "support", "natural-ease"]},
    "astro.aspect.sextile": {
        "relation": ["ease-with-participation", "directed-potential", "cooperation"]
    },
}

ASPECT_INTERACTION = {
    "astro.aspect.conjunction": "merging",
    "astro.aspect.opposition": "polarization",
    "astro.aspect.square": "friction",
    "astro.aspect.trine": "flow",
    "astro.aspect.sextile": "flow",
}


def test_house_canon_storage_materialization_v1():
    """1.3.92: house_canon_pack + copy locked 1.3.91 packs. Lilly fields unchanged. Next = 1.3.93 smoke."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    jsonschema.validate(example, schema)
    _assert_il1_catalog_counts(objects)

    pack = schema["$defs"]["house_canon_pack"]
    assert pack["required"] == ["arena"]
    assert set(pack["properties"]) == {"arena"}
    assert "domains" not in pack["properties"]
    assert "manner" not in pack["properties"]
    assert "excess" not in pack["properties"]
    assert "canon" in schema["$defs"]["knowledge_object"]["properties"]
    assert "canon" not in schema["$defs"]["knowledge_object"]["required"]

    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    for object_id, locked in HOUSE_CANON_PACKS.items():
        obj = by_id[object_id]
        assert obj["status"] == "draft"
        assert obj["type"] == "house"
        assert obj["canon"] == locked
        assert "domains" not in obj["canon"]
        assert "manner" not in obj["canon"]
        assert "excess" not in obj["canon"]
        assert isinstance(obj["domain"], str)
        assert obj["people"]
        assert obj["activities"]

    fourth = by_id["astro.house.04"]
    assert fourth["canon"]["arena"] == ["home", "family", "roots", "private-base"]
    assert fourth["domain"] == "father, land, hidden things, and endings"
    assert "seek" not in " ".join(fourth["canon"]["arena"])
    assert "emotional" not in " ".join(fourth["canon"]["arena"])
    assert by_id["astro.house.01"]["domain"] == "life, stature, and the querent's person"
    assert "home" not in by_id["astro.house.10"]["canon"]["arena"]
    assert "career" not in by_id["astro.house.04"]["canon"]["arena"]
    assert "astro.object.asc" not in by_id
    assert "astro.object.mc" not in by_id

    for obj in objects["objects"]:
        if obj["type"] not in ("celestial_object", "sign", "house", "aspect"):
            assert "canon" not in obj
    for object_id, planet_pack in SUN_SATURN_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == planet_pack
    for object_id, sign_pack in SIGN_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == sign_pack

    house_ex = next(obj for obj in example["objects"] if obj["object_id"] == "astro.house.04")
    assert house_ex["canon"] == {"arena": ["home", "family", "roots", "private-base"]}
    assert house_ex["domain"] == "father, land, hidden things, and endings"
    assert "manner" not in house_ex["canon"]

    house = _minimal_house_draft("astro.house.04")
    jsonschema.validate(
        {"contract_version": "astrology_interpretation_v1", "objects": [house]},
        schema,
    )

    filled = dict(house)
    filled["canon"] = {"arena": ["home", "family", "roots", "private-base"]}
    jsonschema.validate(
        {"contract_version": "astrology_interpretation_v1", "objects": [filled]},
        schema,
    )

    partial = dict(house)
    partial["canon"] = {}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [partial]},
            schema,
        )

    second_slot = dict(house)
    second_slot["canon"] = {
        "arena": ["home"],
        "excess": ["clinging"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [second_slot]},
            schema,
        )

    domains_key = dict(house)
    domains_key["canon"] = {"domains": ["home"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [domains_key]},
            schema,
        )

    sign_pack_on_house = dict(house)
    sign_pack_on_house["canon"] = {
        "manner": ["reserved"],
        "excess": ["hardening"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [sign_pack_on_house]},
            schema,
        )

    planet_pack_on_house = dict(house)
    planet_pack_on_house["canon"] = {
        "core_function": ["limit"],
        "drive": ["order"],
        "needs": ["boundaries"],
        "constructive": ["form"],
        "distorted": ["rigidity"],
        "domains": ["limits"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [planet_pack_on_house]},
            schema,
        )

    house_pack_on_sign = _minimal_sign_draft("astro.sign.capricorn")
    house_pack_on_sign["mode"] = "cardinal"
    house_pack_on_sign["element"] = "earth"
    house_pack_on_sign["orientation"] = "negative"
    house_pack_on_sign["canon"] = {"arena": ["home"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [house_pack_on_sign]},
            schema,
        )

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.46 House Canon storage and materialization" in canon
    assert "**Версия:** 1.3.98" in canon
    storage = (
        ROOT / "docs" / "astrology" / "HOUSE_CANON_STORAGE_MATERIALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "canon.arena" in storage
    assert "Lilly" in storage
    assert "1.3.93" in storage
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.92" in next_block
    assert "1.3.91" in next_block
    assert "1.3.90" in next_block
    assert "1.3.89" in next_block
    assert "1.3.88" in next_block
    assert "1.3.87" in next_block
    assert "1.3.86" in next_block
    assert "1.3.85" in next_block
    assert "1.3.84" in next_block
    assert "1.3.83" in next_block
    assert "1.3.82" in next_block
    assert "Planet × House" in next_block
    assert "Planet × Sign" in next_block
    assert "Sign Canon fill" in next_block
    assert "Sign Canon storage" in next_block
    assert "Sign Canon grammar" in next_block
    assert "House Canon storage" in next_block
    assert "House Canon fill" in next_block
    assert "House Canon grammar" in next_block or "House Canon Grammar" in next_block
    assert "Mainstream" in next_block
    assert "House" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Signs" in next_block


def test_mainstream_aspect_semantic_map_v1():
    """1.3.94: Mainstream aspect map. Concept families. No ingest. No objects. No Canon slots."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.48 Mainstream Aspect Semantic Map" in canon
    assert "**Версия:** 1.3.98" in canon
    aspect_map = (
        ROOT / "docs" / "astrology" / "MAINSTREAM_ASPECT_SEMANTIC_MAP_V1.md"
    ).read_text(encoding="utf-8")
    assert "Astrology.com" in aspect_map
    assert "Astrodienst" in aspect_map
    assert "Cafe Astrology" in aspect_map
    assert "concept family" in aspect_map.lower() or "concept families" in aspect_map.lower()
    assert "relation, not a theme" in aspect_map.lower() or "relation, not theme" in aspect_map.lower()
    assert "challenge causes growth" in aspect_map.lower() or "challenge-causes-growth" in aspect_map
    assert "one slot vs two atoms" in aspect_map.lower() or "one `relation` slot" in aspect_map
    assert "Not JSON" in aspect_map or "not JSON" in aspect_map
    assert "blend · unite · fuse · immediate-connection" in aspect_map
    assert "friction · blockage · cross-purposes · demand-for-action" in aspect_map
    assert "easy-flow · support · natural-ease · complementary" in aspect_map
    assert "orbs" in aspect_map.lower()
    assert "applying" in aspect_map.lower()
    for heading in (
        "Conjunction",
        "Opposition",
        "Square",
        "Trine",
        "Sextile",
    ):
        assert f"### {heading}" in aspect_map
        assert "**Include**" in aspect_map
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.aspect.square"]["interaction"] == "friction"
    assert by_id["astro.aspect.trine"]["interaction"] == "flow"
    assert by_id["astro.aspect.square"]["canon"]["relation"]
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.94" in next_block
    assert "1.3.93" in next_block
    assert "Aspect Canon" in next_block or "Aspect Canon grammar" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block


def test_aspect_canon_grammar_v1():
    """1.3.95: Aspect Canon grammar. One slot (relation). Not fill. Not objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.49 Aspect Canon grammar" in canon
    assert "**Версия:** 1.3.98" in canon
    grammar = (ROOT / "docs" / "astrology" / "ASPECT_CANON_GRAMMAR_V1.md").read_text(
        encoding="utf-8"
    )
    assert "**relation**" in grammar
    assert "Deletion test" in grammar
    assert "**Surplus**" in grammar
    assert "requires_action" in grammar
    assert "object.interaction" in grammar or "stored `interaction`" in grammar
    assert "Aspect ≠ theme" in grammar
    assert "Mars □ Saturn" in grammar
    assert "Jupiter △ Sun" in grammar
    assert "Mars ☍ Saturn" in grammar
    assert "Venus △ Mars" in grammar
    assert "Venus ✶ Mars" in grammar
    assert "Sun ☌ Mercury" in grammar
    assert "Venus □ Saturn" in grammar
    assert "Moon ☍ Saturn" in grammar
    assert "not locked" in grammar.lower() or "Dry-run" in grammar
    assert "One. Not two." in grammar or "One required slot" in grammar
    assert "mixed-valence" in grammar
    assert "mini-Composition Engine" in grammar
    assert "IL-2" in grammar
    assert "minimal payload" in grammar.lower() or "minimal aspect payload" in grammar.lower()
    assert "both sides remain" in grammar.lower() or "both poles" in grammar.lower()
    assert "Today / Profile / Compatibility" in grammar or "Today/Profile/Compatibility" in grammar
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.aspect.square"]["interaction"] == "friction"
    assert by_id["astro.aspect.trine"]["interaction"] == "flow"
    assert by_id["astro.aspect.sextile"]["interaction"] == "flow"
    assert by_id["astro.aspect.square"]["canon"]["relation"]
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.95" in next_block
    assert "1.3.94" in next_block
    assert "Aspect Canon fill" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block


def test_aspect_canon_v1_fill_with_provenance():
    """1.3.96: Aspect Canon V1 packs + origin. Five gates. No schema. No objects."""
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    _assert_il1_catalog_counts(objects)
    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.50 Aspect Canon V1 fill" in canon
    assert "**Версия:** 1.3.98" in canon
    packs = (ROOT / "docs" / "astrology" / "ASPECT_CANON_V1.md").read_text(
        encoding="utf-8"
    )
    assert "direct" in packs
    assert "mixed-valence" in packs
    assert "Topology, not meaning" in packs or "topology, not meaning" in packs.lower()
    for heading in (
        "Conjunction",
        "Opposition",
        "Square",
        "Trine",
        "Sextile",
    ):
        assert f"### {heading}" in packs
        assert "relation:" in packs
    square = packs.split("### Square")[1].split("### Trine")[0]
    square_rel = square.split("```text")[1].split("```")[0]
    assert "friction" in square_rel
    assert "blockage" in square_rel
    assert "cross-purposes" in square_rel
    assert "growth" not in square_rel
    assert "challenge" not in square_rel
    trine = packs.split("### Trine")[1].split("### Sextile")[0]
    trine_rel = trine.split("```text")[1].split("```")[0]
    assert "easy-flow" in trine_rel
    assert "natural-ease" in trine_rel
    assert "luck" not in trine_rel
    sextile = packs.split("### Sextile")[1].split("## 3.")[0]
    sextile_rel = sextile.split("```text")[1].split("```")[0]
    assert "ease-with-participation" in sextile_rel
    assert "directed-potential" in sextile_rel
    assert "natural-ease" not in sextile_rel
    conjunction = packs.split("### Conjunction")[1].split("### Opposition")[0]
    conj_rel = conjunction.split("```text")[1].split("```")[0]
    assert "blend" in conj_rel
    assert "fuse" in conj_rel
    assert "immediate-connection" in conj_rel
    assert "harmonious" not in conj_rel
    assert "difficult" not in conj_rel
    opposition = packs.split("### Opposition")[1].split("### Square")[0]
    opp_rel = opposition.split("```text")[1].split("```")[0]
    assert "polarity" in opp_rel
    assert "facing" in opp_rel
    assert "friction" not in opp_rel
    assert "Mars □ Saturn" in packs
    assert "Venus □ Saturn" in packs
    assert "Jupiter △ Sun" in packs
    assert "Venus △ Mars" in packs
    assert "Venus ✶ Mars" in packs
    assert "Sun ☌ Mercury" in packs
    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    assert by_id["astro.aspect.square"]["interaction"] == "friction"
    assert by_id["astro.aspect.sextile"]["interaction"] == "flow"
    assert by_id["astro.aspect.square"]["canon"]["relation"]
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.96" in next_block
    assert "1.3.95" in next_block
    assert "storage" in next_block.lower() or "materialization" in next_block.lower()
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block


def test_aspect_canon_storage_materialization_v1():
    """1.3.97: aspect_canon_pack + copy locked 1.3.96 packs. interaction unchanged. Next = 1.3.98 smoke."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    objects = json.loads(OBJECTS.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    jsonschema.validate(objects, schema)
    jsonschema.validate(example, schema)
    _assert_il1_catalog_counts(objects)

    pack = schema["$defs"]["aspect_canon_pack"]
    assert pack["required"] == ["relation"]
    assert set(pack["properties"]) == {"relation"}
    assert pack.get("additionalProperties") is False
    assert "requires_action" not in pack["properties"]
    assert "valence" not in pack["properties"]
    assert "interaction" not in pack["properties"]
    assert "arena" not in pack["properties"]
    assert "manner" not in pack["properties"]
    assert "canon" in schema["$defs"]["knowledge_object"]["properties"]
    assert "canon" not in schema["$defs"]["knowledge_object"]["required"]

    by_id = {obj["object_id"]: obj for obj in objects["objects"]}
    for object_id, locked in ASPECT_CANON_PACKS.items():
        obj = by_id[object_id]
        assert obj["status"] == "draft"
        assert obj["type"] == "aspect"
        assert obj["canon"] == locked
        assert obj["interaction"] == ASPECT_INTERACTION[object_id]
        assert obj["requires_action"] is False
        assert "requires_action" not in obj["canon"]
        assert "valence" not in obj["canon"]
        assert "orb" not in obj["canon"]
        assert "pair" not in obj["canon"]

    square = by_id["astro.aspect.square"]
    assert square["canon"]["relation"] == ["friction", "blockage", "cross-purposes"]
    assert square["interaction"] == "friction"
    opposition = by_id["astro.aspect.opposition"]
    assert opposition["canon"]["relation"] == ["polarity", "facing", "the-other"]
    assert opposition["interaction"] == "polarization"
    assert square["canon"] != opposition["canon"]
    trine = by_id["astro.aspect.trine"]
    sextile = by_id["astro.aspect.sextile"]
    assert trine["interaction"] == "flow"
    assert sextile["interaction"] == "flow"
    assert trine["canon"] != sextile["canon"]
    conjunction = by_id["astro.aspect.conjunction"]
    assert conjunction["interaction"] == "merging"
    assert conjunction["canon"] != trine["canon"]
    lemmas = " ".join(conjunction["canon"]["relation"])
    assert "harmonious" not in lemmas
    assert "difficult" not in lemmas
    assert "growth" not in " ".join(square["canon"]["relation"])
    assert "luck" not in " ".join(trine["canon"]["relation"])
    assert "astro.object.asc" not in by_id
    assert "astro.object.mc" not in by_id

    for obj in objects["objects"]:
        if obj["type"] not in ("celestial_object", "sign", "house", "aspect"):
            assert "canon" not in obj
    for object_id, planet_pack in SUN_SATURN_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == planet_pack
    for object_id, sign_pack in SIGN_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == sign_pack
    for object_id, house_pack in HOUSE_CANON_PACKS.items():
        assert by_id[object_id]["canon"] == house_pack

    square_ex = next(obj for obj in example["objects"] if obj["object_id"] == "astro.aspect.square")
    assert square_ex["canon"] == {"relation": ["friction", "blockage", "cross-purposes"]}
    assert square_ex["interaction"] == "friction"
    assert "arena" not in square_ex["canon"]

    aspect = _minimal_aspect_draft("astro.aspect.square")
    jsonschema.validate(
        {"contract_version": "astrology_interpretation_v1", "objects": [aspect]},
        schema,
    )

    filled = dict(aspect)
    filled["canon"] = {"relation": ["friction", "blockage", "cross-purposes"]}
    jsonschema.validate(
        {"contract_version": "astrology_interpretation_v1", "objects": [filled]},
        schema,
    )

    partial = dict(aspect)
    partial["canon"] = {}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [partial]},
            schema,
        )

    second_slot = dict(aspect)
    second_slot["canon"] = {
        "relation": ["friction"],
        "arena": ["home"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [second_slot]},
            schema,
        )

    action_key = dict(aspect)
    action_key["canon"] = {
        "relation": ["friction"],
        "requires_action": False,
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [action_key]},
            schema,
        )

    house_pack_on_aspect = dict(aspect)
    house_pack_on_aspect["canon"] = {"arena": ["home"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [house_pack_on_aspect]},
            schema,
        )

    sign_pack_on_aspect = dict(aspect)
    sign_pack_on_aspect["canon"] = {
        "manner": ["reserved"],
        "excess": ["hardening"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [sign_pack_on_aspect]},
            schema,
        )

    planet_pack_on_aspect = dict(aspect)
    planet_pack_on_aspect["canon"] = {
        "core_function": ["limit"],
        "drive": ["order"],
        "needs": ["boundaries"],
        "constructive": ["form"],
        "distorted": ["rigidity"],
        "domains": ["limits"],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [planet_pack_on_aspect]},
            schema,
        )

    aspect_pack_on_house = _minimal_house_draft("astro.house.04")
    aspect_pack_on_house["canon"] = {"relation": ["friction"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [aspect_pack_on_house]},
            schema,
        )

    combo = next(obj for obj in example["objects"] if obj["type"] == "transit_to_natal")
    combo_with_canon = dict(combo)
    combo_with_canon["canon"] = {"relation": ["friction"]}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"contract_version": "astrology_interpretation_v1", "objects": [combo_with_canon]},
            schema,
        )

    canon = (ROOT / "docs" / "astrology" / "INTERPRETATION_LIBRARY_V1.md").read_text(
        encoding="utf-8"
    )
    assert "### 6.51 Aspect Canon storage and materialization" in canon
    assert "**Версия:** 1.3.98" in canon
    storage = (
        ROOT / "docs" / "astrology" / "ASPECT_CANON_STORAGE_MATERIALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "canon.relation" in storage
    assert "interaction" in storage
    assert "1.3.98" in storage
    assert "verbatim" in storage.lower() or "1.3.96 packs" in storage
    handoff = (ROOT / "docs" / "astrology" / "IL1_HANDOFF.md").read_text(encoding="utf-8")
    next_block = handoff.split("## 3. What to do next")[1].split("## 4.")[0]
    assert "1.3.97" in next_block
    assert "1.3.96" in next_block
    assert "1.3.95" in next_block
    assert "1.3.94" in next_block
    assert "1.3.93" in next_block
    assert "1.3.92" in next_block
    assert "1.3.91" in next_block
    assert "1.3.90" in next_block
    assert "Planet × Aspect" in next_block or "stored Planet × Aspect" in next_block
    assert "Aspect Canon fill" in next_block
    assert "House Canon fill" in next_block
    assert "House Canon storage" in next_block
    assert "Do **not** start CORE scoring" in next_block
    assert "classification-complete" in next_block
    assert "STOP Houses" in next_block
    assert "STOP Signs" in next_block









