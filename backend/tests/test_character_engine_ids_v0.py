"""ID stability for Character Engine — must not depend on LLM surface text."""

from __future__ import annotations

from todayflow_backend.services.character_engine_ids_v0 import (
    fingerprint_ids,
    make_claim_id,
    make_compass_item_id,
    make_edge_id,
    make_fact_id,
    make_scene_id,
)


def test_fact_id_stable_and_independent_of_display_value() -> None:
    a = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="swiss_ephe_v1",
    )
    b = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="swiss_ephe_v1",
    )
    assert a == b
    assert a.startswith("fact:")


def test_fact_id_changes_with_calc_version() -> None:
    a = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="swiss_ephe_v1",
    )
    b = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="swiss_ephe_v2",
    )
    assert a != b


def test_claim_id_ignores_fact_order_and_surface_text() -> None:
    f1 = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="v1",
    )
    f2 = make_fact_id(
        fact_type="life_path_number",
        normalized_key="7",
        authority="deterministic_numerology",
        calc_version="v1",
    )
    a = make_claim_id(
        claim_kind="identity_core",
        thesis_key="builds_own_world_system",
        primary_fact_ids=[f1, f2],
    )
    b = make_claim_id(
        claim_kind="identity_core",
        thesis_key="builds_own_world_system",
        primary_fact_ids=[f2, f1],
    )
    assert a == b
    # surface text is not an input — regenerating prose cannot change claim_id
    assert a == make_claim_id(
        claim_kind="identity_core",
        thesis_key="builds_own_world_system",
        primary_fact_ids=[f1, f2],
    )


def test_claim_id_changes_with_thesis_key() -> None:
    f1 = make_fact_id(
        fact_type="sun_sign",
        normalized_key="aquarius",
        authority="swiss",
        calc_version="v1",
    )
    a = make_claim_id(
        claim_kind="identity_core",
        thesis_key="builds_own_world_system",
        primary_fact_ids=[f1],
    )
    b = make_claim_id(
        claim_kind="identity_core",
        thesis_key="follows_external_map",
        primary_fact_ids=[f1],
    )
    assert a != b


def test_edge_and_scene_and_compass_ids_stable() -> None:
    fact = make_fact_id(
        fact_type="moon_sign",
        normalized_key="pisces",
        authority="swiss",
        calc_version="v1",
    )
    claim = make_claim_id(
        claim_kind="tension",
        thesis_key="freedom_vs_stability",
        primary_fact_ids=[fact],
    )
    e1 = make_edge_id(fact_id=fact, claim_id=claim, edge_type="supports")
    e2 = make_edge_id(fact_id=fact, claim_id=claim, edge_type="supports")
    assert e1 == e2

    s1 = make_scene_id(scene_kind="intimacy", tension_or_mechanism_ref="freedom_vs_stability")
    s2 = make_scene_id(scene_kind="intimacy", tension_or_mechanism_ref="freedom_vs_stability")
    assert s1 == s2

    c1 = make_compass_item_id(
        item_kind="strengths",
        source_refs={"claim_ids": [claim, fact], "scene_ids": [s1]},
    )
    c2 = make_compass_item_id(
        item_kind="strengths",
        source_refs={"claim_ids": [fact, claim], "scene_ids": [s1]},
    )
    assert c1 == c2


def test_fingerprint_ids_order_independent() -> None:
    assert fingerprint_ids(["b", "a"]) == fingerprint_ids(["a", "b"])
