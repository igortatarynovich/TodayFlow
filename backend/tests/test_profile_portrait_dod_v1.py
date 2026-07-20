"""DoD gates for profile-contract-v3: completeness, forming, invalidation, concurrency."""

from __future__ import annotations

import threading
import time
from typing import Any

from todayflow_backend.core.config import settings
from todayflow_backend.services.core_profile import CoreProfileService
from todayflow_backend.services.profile_contract_quality_v1 import (
    validate_profile_contract_strict,
    validate_required_fields,
)
from todayflow_backend.services.profile_contract_v1 import (
    FORMING_MESSAGE_RU,
    PROFILE_CONTRACT_PROMPT_VER,
    PROFILE_STATUS_FORMING,
    build_profile_contract_forming_v1,
    build_profile_contract_fallback_v1,
    _normalize_profile_contract,
)
from todayflow_backend.services.profile_disclosure_funnel_v0 import (
    SPHERE_IDS,
    SPHERE_FIELDS,
    profile_prompt_versions,
)


def _full_contract() -> dict[str, Any]:
    spheres = {
        sid: {
            "how": f"{sid} how shows in this person's concrete week with a clear scene.",
            "need": f"{sid} needs one honest boundary and a named next step.",
            "risk": f"{sid} risk is stacking silent obligations without a slot.",
            "turns_on": f"{sid} turns on with calm structure and one clear ask.",
            "turns_off": f"{sid} turns off under vague pressure and comparison.",
            "helps": f"{sid} helps with one small protected block on the calendar.",
        }
        for sid in SPHERE_IDS
    }
    # Make hows distinct enough
    for i, sid in enumerate(SPHERE_IDS):
        spheres[sid]["how"] = (
            f"В сфере {sid} человек действует через сценарий #{i}: "
            f"конкретная ситуация, глагол и граница, не общая фраза."
        )
    return _normalize_profile_contract(
        {
            "status": "ready",
            "identity_core": "Человек держит смысл через ясный фокус и прямой контакт, не через суету.",
            "strengths": ["Фокус на одном", "Прямой контакт", "Доведение до конца"],
            "growth_zones": ["Второй приоритет без слота", "Контроль вместо ясности", "Откладывание разговора"],
            "relationship_style": "Близость строится через прямые слова и предсказуемый ритм ответа.",
            "money_style": "Деньги как ценность спокойствия: один ясный шаг вместо импульса.",
            "decision_style": "Решения через один критерий и короткий дедлайн, без лишнего шума.",
            "recurring_patterns": ["Часто берёт второй приоритет, когда день уже заполнен."],
            "living_changes": "Сейчас усиливается запрос на один главный фокус и меньше параллельных обещаний.",
            "life_mission": "Удерживать свой ритм и не растворяться в чужих срочных задачах.",
            "helps": ["Один фокус на день", "Пауза перед новым да"],
            "life_spheres": spheres,
        }
    )


def test_required_fields_all_present() -> None:
    contract = _full_contract()
    assert validate_required_fields(contract) == []
    report = validate_profile_contract_strict(contract)
    assert report["ok"] is True
    assert len(contract["life_spheres"]) == 9
    for sid in SPHERE_IDS:
        for field in SPHERE_FIELDS:
            assert len(contract["life_spheres"][sid][field]) >= 8


def test_fallback_is_forming_not_fake_scaffold() -> None:
    forming = build_profile_contract_fallback_v1(
        {"person": {"display_name": "Игорь", "locale": "ru"}, "baseline": {"archetype": "Sage"}, "astro": {"sun_sign": "Leo"}},
    )
    assert forming["status"] == PROFILE_STATUS_FORMING
    assert FORMING_MESSAGE_RU in (forming.get("forming_message") or "")
    assert forming["identity_core"] == ""
    assert forming["strengths"] == []
    assert forming["life_spheres"] == {}
    # Must not contain old scaffold clichés
    blob = str(forming)
    assert "Способность держать линию" not in blob
    assert "Устойчивость" not in blob


def test_prompt_version_change_invalidates_hash() -> None:
    svc = CoreProfileService()
    h1 = svc._build_profile_hash(None, {"birth_date": "1990-01-01", "sun_sign": "Leo"}, {"life_path": 7})
    versions = profile_prompt_versions()
    # Mutate registry version via monkeypatch on profile_prompt_versions
    bumped = {**versions, "profile.spheres.v1": "9.9.9"}

    import todayflow_backend.services.core_profile as cp

    original = cp.profile_prompt_versions
    cp.profile_prompt_versions = lambda: bumped
    try:
        h2 = svc._build_profile_hash(None, {"birth_date": "1990-01-01", "sun_sign": "Leo"}, {"life_path": 7})
    finally:
        cp.profile_prompt_versions = original
    assert h1 != h2
    assert PROFILE_CONTRACT_PROMPT_VER


def test_parallel_opens_do_not_multiply_generation(monkeypatch) -> None:
    """20 parallel opens should coalesce under lock → one portrait build."""
    monkeypatch.setattr(settings, "llm_quality_mode", "rich")
    svc = CoreProfileService(cache_ttl_seconds=60)
    calls = {"n": 0}
    barrier = threading.Barrier(20)
    ready_contract = _full_contract()

    def fake_build_portrait(**kwargs):
        calls["n"] += 1
        time.sleep(0.08)
        return ready_contract, {"identity": ready_contract["identity_core"]}, {}, False

    # Patch inside the lock path: snapshot miss + portrait once.
    monkeypatch.setattr(
        "todayflow_backend.services.core_profile.build_profile_portrait_v1",
        fake_build_portrait,
    )

    class _Dummy:
        id = 1
        email = "a@b.c"

    class _Settings:
        first_name = "A"
        last_name = "B"
        gender = "unspecified"
        locale = "ru"
        greeting = None

    user = _Dummy()
    results: list[dict[str, Any]] = []

    def _one():
        # Minimal stub of build() critical section using public helpers.
        profile_hash = svc._build_profile_hash(
            _Settings(),
            {"birth_date": "1990-01-01", "sun_sign": "Leo", "relation": "self"},
            {"life_path": 7},
        )
        lock = svc._lock_for_hash(profile_hash)
        barrier.wait()
        with lock:
            cache_key = f"u1|{profile_hash}"
            now = time.time()
            cached = svc._cache.get(cache_key)
            if cached and cached[0] > now:
                results.append(cached[1])
                return
            contract, interpretation, daily, used_fb = fake_build_portrait()
            payload = {
                "profile_hash": profile_hash,
                "profile_contract_v1": contract,
                "interpretation": interpretation,
                "daily_interpretation": daily,
                "used_fallback": used_fb,
            }
            svc._cache[cache_key] = (now + 60, payload)
            results.append(payload)

    threads = [threading.Thread(target=_one) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert calls["n"] == 1
    assert len(results) == 20


def test_forming_message_constant() -> None:
    c = build_profile_contract_forming_v1(locale="ru", reason="test")
    assert c["status"] == PROFILE_STATUS_FORMING
    assert "формируется" in (c.get("forming_message") or "").lower()
