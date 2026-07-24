"""Adapter: numerology Source Family (universal day always; personal when birth_date)."""

from __future__ import annotations

from datetime import date

from todayflow_backend.services.day_sources.types import DaySourceInputs, SourceResult

_CALC = "numerology-adapter-v0"
_MASTER = {11, 22, 33}


def _reduce(value: int) -> int:
    while value > 9 and value not in _MASTER:
        value = sum(int(d) for d in str(value))
    return value


def _sum_digits(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def universal_day_number(target: date) -> int:
    """Canon §3 / §5.5.1 — digit sum of civil YYYYMMDD, keep 11/22/33."""
    total = sum(int(d) for d in target.strftime("%Y%m%d"))
    return _reduce(total)


def personal_year_number(birth: date, year: int) -> int:
    """Canon: birth_day + birth_month + year digits → reduce."""
    total = birth.day + birth.month + _sum_digits(year)
    return _reduce(total)


def personal_month_number(personal_year: int, month: int) -> int:
    return _reduce(personal_year + month)


def personal_day_number(personal_month: int, day: int) -> int:
    return _reduce(personal_month + day)


def run_numerology(inputs: DaySourceInputs) -> SourceResult:
    target = inputs.target_date
    universal = universal_day_number(target)
    caps = ["universal_day"]
    payload: dict = {
        "universal_day": universal,
        "target_date": target.isoformat(),
    }
    evidence = ["target_date"]

    if inputs.birth_date is not None:
        py = personal_year_number(inputs.birth_date, target.year)
        pm = personal_month_number(py, target.month)
        pd = personal_day_number(pm, target.day)
        payload["personal_year"] = py
        payload["personal_month"] = pm
        payload["personal_day"] = pd
        payload["birth_date"] = inputs.birth_date.isoformat()
        caps.extend(["personal_year", "personal_month", "personal_day"])
        evidence.append("birth_date")

    return SourceResult(
        family_id="numerology",
        capability_ids=caps,
        layer="foundation",
        status="ok",
        payload=payload,
        evidence_refs=evidence,
        calculation_version=_CALC,
    )
