"""Fixed-4 DomainLens wire helpers (v3.1)."""

from todayflow_backend.services.today_domain_wire_v1 import (
    DOMAIN_WIRE_IDS,
    expand_legacy_domain_lenses,
    normalize_domains_present,
    sphere_to_wire,
)


def test_domain_wire_ids_are_fixed_four():
    assert DOMAIN_WIRE_IDS == ("work", "money", "relationships", "energy")


def test_sphere_to_wire_splits_money_work_and_energy():
    assert sphere_to_wire("work_decisions") == "work"
    assert sphere_to_wire("money") == "money"
    assert sphere_to_wire("money_work") == "money"
    assert sphere_to_wire("relationships") == "relationships"
    assert sphere_to_wire("home") == "relationships"
    assert sphere_to_wire("energy_body") == "energy"
    assert sphere_to_wire("rest_travel") == "energy"


def test_normalize_domains_present_expands_legacy_triad():
    assert normalize_domains_present(["money_work", "family"]) == ["work", "money", "relationships"]
    assert normalize_domains_present(["work", "energy"]) == ["work", "energy"]


def test_expand_legacy_domain_lenses():
    legacy = {
        "money_work": {"status": "mw", "opportunity": "o", "risk": "r", "action": "a"},
        "family": {"status": "f", "opportunity": "fo", "risk": "fr", "action": "fa"},
        "relationships": {"status": "rel", "opportunity": "ro", "risk": "rr", "action": "ra"},
    }
    out = expand_legacy_domain_lenses(legacy)
    assert out["relationships"]["status"] == "rel"  # prefer existing
    assert out["work"]["status"] == "mw"
    assert out["money"]["status"] == "mw"
    assert "family" not in out
    assert "money_work" not in out
