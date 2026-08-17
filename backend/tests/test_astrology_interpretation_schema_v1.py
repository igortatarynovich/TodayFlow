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
    assert not any(obj["type"] == "sign" for obj in objects["objects"])
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
    assert "No Layer 2 sign objects yet" in notes
    assert "later interpretive layer" in notes
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
        assert any("No Layer 2 object" in n for n in sign_claims["gap_notes"])
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
    assert not any(obj["type"] == "sign" for obj in objects["objects"])


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
    solar = next(row for row in sun_claims["claims"] if row["concept_id"] == "claim.sun.solar_consciousness_eternal")
    assert solar["source_class"] == "psychological"
    assert solar["evidence_tier"] == "school_specific"
    assert solar["source_id"] == "src.psychological.greene_luminaries"
    moon_ids = {row["concept_id"] for row in moon_claims["claims"]}
    assert "claim.moon.earth_mother_embodiment" in moon_ids
    assert "claim.moon.embodied_life_as_numinous" in moon_ids
    assert "claim.moon.night_world_function" in moon_ids
    assert "claim.moon.emotion_habit_function" in moon_ids
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
    venus_claims = json.loads((CLAIMS_DIR / "astro.object.venus.json").read_text(encoding="utf-8"))
    assert "src.psychological.greene_inner_planets" in set(venus_claims["pending_source_ids"])
    assert "src.psychological.greene_inner_planets" not in {row["source_id"] for row in venus_claims["claims"]}
    assert "src.professional.hand_horoscope_symbols" not in set(venus_claims["pending_source_ids"])
    hand_venus = [row for row in venus_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_venus) == 12
    assert all(row["source_class"] == "professional" for row in hand_venus)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_venus)
    assert all(row["school"] == "modern_professional" for row in hand_venus)
    assert all("runtime_semantic_candidate" not in row for row in hand_venus)
    assert "moist temperate quality disposed to pleasure and company" == by_id["astro.object.venus"]["function"]
    assert "claim.venus.hand_noncoercive_bonding" in {row["concept_id"] for row in by_id["astro.object.venus"]["provenance"]}
    assert "voluntary" not in by_id["astro.object.venus"]["function"]
    assert any("p.69" in note and "not opened" in note.lower() for note in venus_claims["gap_notes"])
    assert any("carolina de pedro" in note.lower() for note in venus_claims["gap_notes"])
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
    assert "unconscious" not in moon["function"]
    assert "embodiment" not in moon["function"]
    assert "spontaneity" not in mercury["function"]
    sun_prov = {row["concept_id"] for row in sun["provenance"]}
    moon_prov = {row["concept_id"] for row in moon["provenance"]}
    mercury_prov = {row["concept_id"] for row in mercury["provenance"]}
    assert "claim.sun.essential_self" in sun_prov
    assert "claim.sun.solar_consciousness_eternal" in sun_prov
    assert "claim.moon.night_world_function" in moon_prov
    assert "claim.moon.earth_mother_embodiment" in moon_prov
    assert "claim.mercury.mind_curiosity" in mercury_prov
    assert "claim.mercury.hermes_spontaneity" in mercury_prov
    inner = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_inner_planets")
    assert inner["source_class"] == "psychological"
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
    assert "src.psychological.greene_inner_planets" in set(mars_claims["pending_source_ids"])
    assert "src.psychological.greene_inner_planets" not in {row["source_id"] for row in mars_claims["claims"]}
    assert "src.professional.hand_horoscope_symbols" not in set(mars_claims["pending_source_ids"])
    hand_mars = [row for row in mars_claims["claims"] if row["source_id"] == "src.professional.hand_horoscope_symbols"]
    assert len(hand_mars) == 13
    assert all(row["source_class"] == "professional" for row in hand_mars)
    assert all(row["evidence_tier"] == "school_specific" for row in hand_mars)
    assert all(row["school"] == "modern_professional" for row in hand_mars)
    assert all("runtime_semantic_candidate" not in row for row in hand_mars)
    assert "heating and drying quality that contends" == by_id["astro.object.mars"]["function"]
    assert "survival" not in by_id["astro.object.mars"]["function"]
    assert "claim.mars.hand_survival_energy" in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    assert "claim.mars.hand_body_muscular_vigor" not in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    assert "claim.mars.hand_blocked_health_manifestation" not in {row["concept_id"] for row in by_id["astro.object.mars"]["provenance"]}
    mars_domains = json.dumps(by_id["astro.object.mars"]["domains"]).lower()
    assert "inflammation" not in mars_domains
    assert "iron" not in mars_domains
    assert any("p.138" in note and "not opened" in note.lower() for note in mars_claims["gap_notes"])
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
    assert "claim.jupiter.hand_healing_reintegration" not in jupiter_prov
    jupiter_domains = json.dumps(by_id["astro.object.jupiter"]["domains"]).lower()
    assert "healing" not in jupiter_domains
    assert "medicine" not in jupiter_domains
    mercury_notes = " ".join(json.loads((CLAIMS_DIR / "astro.object.mercury.json").read_text(encoding="utf-8"))["gap_notes"]).lower()
    assert "breadth-over-depth" in mercury_notes or "breadth over depth" in mercury_notes
    assert "expansion" not in by_id["astro.object.jupiter"]["function"]
    assert "integration" not in by_id["astro.object.jupiter"]["function"]
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
    assert by_id["astro.object.saturn"]["themes"] == ["cold", "dryness", "slowness", "solitude", "austerity"]
    assert "claim.saturn.hand_resistance" in {row["concept_id"] for row in by_id["astro.object.saturn"]["provenance"]}
    assert not any("structure" in theme for theme in by_id["astro.object.saturn"]["themes"])
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
    assert "Neptune and Pluto Ch.4 extracted" in hand["notes"]
    assert "Sun/Moon/Mercury" in hand["notes"]
    cpa = next(src for src in corpus["sources"] if src["source_id"] == "src.psychological.greene_jupiter_cpa")
    assert cpa["source_class"] == "psychological"
    assert cpa["legal_status"] == "copyrighted_site"


def test_hand_uranus_claims_not_core():
    """Hand Ch.4 Uranus is professional school_specific ledger-only; object withheld; not CORE."""
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
    got_ids = {row["concept_id"] for row in claims["claims"]}
    assert got_ids == expected_ids
    assert len(claims["claims"]) == 12
    assert all(row["source_id"] == "src.professional.hand_horoscope_symbols" for row in claims["claims"])
    assert all(row["source_class"] == "professional" for row in claims["claims"])
    assert all(row["evidence_tier"] == "school_specific" for row in claims["claims"])
    assert all(row["school"] == "modern_professional" for row in claims["claims"])
    assert all(row["review_status"] == "extracted" for row in claims["claims"])
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes
    assert "jupiter" in notes and "alien" in notes
    assert "1981" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    assert len(objects["objects"]) == 24


def test_hand_neptune_claims_not_core():
    """Hand Ch.4 Neptune is professional school_specific ledger-only; object withheld; not CORE."""
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
    got_ids = {row["concept_id"] for row in claims["claims"]}
    assert got_ids == expected_ids
    assert len(claims["claims"]) == 17
    assert all(row["source_id"] == "src.professional.hand_horoscope_symbols" for row in claims["claims"])
    assert all(row["source_class"] == "professional" for row in claims["claims"])
    assert all(row["evidence_tier"] == "school_specific" for row in claims["claims"])
    assert all(row["school"] == "modern_professional" for row in claims["claims"])
    assert all(row["review_status"] == "extracted" for row in claims["claims"])
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    combo_ids = {"claim.neptune.maya_with_saturn", "claim.neptune.artistic_creativity_with_venus"}
    assert combo_ids <= got_ids
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes
    assert "dreams" in notes and "intuition" in notes
    assert "maya" in notes and "neptune+saturn" in notes.replace(" ", "")
    assert "venus" in notes
    assert "1981" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    assert len(objects["objects"]) == 24


def test_hand_pluto_claims_not_core():
    """Hand Ch.4 Pluto is professional school_specific ledger-only; object withheld; not CORE."""
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
    got_ids = {row["concept_id"] for row in claims["claims"]}
    assert got_ids == expected_ids
    assert len(claims["claims"]) == 15
    assert all(row["source_id"] == "src.professional.hand_horoscope_symbols" for row in claims["claims"])
    assert all(row["source_class"] == "professional" for row in claims["claims"])
    assert all(row["evidence_tier"] == "school_specific" for row in claims["claims"])
    assert all(row["school"] == "modern_professional" for row in claims["claims"])
    assert all(row["review_status"] == "extracted" for row in claims["claims"])
    assert all("runtime_semantic_candidate" not in row for row in claims["claims"])
    assert all("do_not_compare_with" not in row for row in claims["claims"])
    assert all("classification_gap" not in row for row in claims["claims"])
    assert "modern_structural" not in {row["source_class"] for row in claims["claims"]}
    pending = set(claims["pending_source_ids"])
    used = {row["source_id"] for row in claims["claims"]}
    assert "src.psychological.greene_outer_planets" in pending
    assert "src.professional.hand_planets_in_transit" in pending
    assert "src.professional.hand_horoscope_symbols" not in pending
    assert "src.psychological.greene_outer_planets" not in used
    notes = " ".join(claims["gap_notes"]).lower()
    assert "object withheld" in notes
    assert "psychotic" in notes and "excluded" in notes
    assert "generic transformation" in notes or "big-transformation" in notes or "big transformation" in notes
    assert "uranus" in notes and "neptune" in notes
    assert "1981" in notes
    assert "not core" in notes or "cannot be scored" in notes
    assert all(row["evidence_tier"] != "core" for row in claims["claims"])
    concept_fields = {row["concept_id"]: row["field"] for row in claims["claims"]}
    assert concept_fields["claim.pluto.gradual_not_uranian_sudden"] == "tempo"
    assert len(objects["objects"]) == 24

