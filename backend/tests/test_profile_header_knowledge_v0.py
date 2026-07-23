"""Deterministic Profile header knowledge pack — no LLM for sign/traditions/stone."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.profile_header_knowledge_v0 import (
    PACK_VERSION,
    build_profile_header_knowledge,
    header_pack_to_matrix_catalog,
)
from todayflow_backend.services.profile_matrix_adapter_v0 import project_profile_slots_v0


def test_header_pack_for_known_date_has_traditions_and_correspondences():
    pack = build_profile_header_knowledge(date(1990, 5, 15), life_path=7)
    assert pack is not None
    assert pack["pack_version"] == PACK_VERSION
    assert pack["source"] == "deterministic_catalog"
    assert pack["tropical_sign"]["id"] == "taurus"
    assert pack["tropical_sign"]["element"] == "earth"
    assert pack["correspondences"]["color"]
    assert isinstance(pack["correspondences"]["stones"], list)
    assert len(pack["correspondences"]["stones"]) >= 1
    ids = {t["id"] for t in pack["traditions"]}
    assert ids == {"tropical_western", "chinese", "tibetan"}
    assert pack["numerology_core"]["life_path"] == 7


def test_header_pack_none_without_birth_date():
    assert build_profile_header_knowledge(None) is None
    assert build_profile_header_knowledge("not-a-date") is None


def test_catalog_feeds_cultural_catalog_slot():
    pack = build_profile_header_knowledge("1990-05-15", life_path=7)
    catalog = header_pack_to_matrix_catalog(pack)
    assert catalog is not None
    assert catalog["traditions"]
    assert catalog["color"]

    proj = project_profile_slots_v0(
        contract={"recognition_line": "тест", "element": "earth", "life_path": 7},
        natal_facts=None,
        birth_date="1990-05-15",
        access="free",
        catalog=catalog,
    )
    assert "cultural_catalog" in proj["slots"]
    assert "cultural_catalog" in proj["revealed_slots"]
    assert proj["slots"]["cultural_catalog"]["traditions"]
    sun = proj["slots"]["sun_element_numerology"]
    assert sun["sun_sign"] in ("taurus", "Телец")
    assert sun["element"] == "earth"
    assert sun["life_path"] == 7
