"""P0.1.1 + P0.1.2 + P0.1.3 — Today contract text quality gate (navigation copy, not Profile dump)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.ritual_cue_sanitize import (
    is_discardable_morning_focus,
    is_garbage_ritual_action_cue,
    is_ru_abstract_topic_headline,
)

MAX_STATUS_CHARS = 220
MAX_STATUS_SENTENCES = 2
MAX_OPPORTUNITY_RISK_CHARS = 160
MAX_OPPORTUNITY_RISK_SENTENCES = 1
MAX_ACTION_CHARS = 140
MAX_ACTION_SENTENCES = 1
MAX_PERIOD_CHARS = 200
MAX_GROWTH_CHARS = 180

DOMAIN_ORDER = ("relationships", "money_work", "family")

_DOMAIN_STATUS_PREFIX: dict[str, str] = {
    "relationships": "Сегодня в отношениях",
    "money_work": "Сегодня в работе и деньгах",
    "family": "Сегодня в семье",
}

_TODAY_MARKERS = (
    "сегодня",
    "день ",
    "день,",
    "день.",
    "сейчас",
    "до обеда",
    "до вечера",
    "на сегодня",
    "в этот день",
    "этот день",
    "дома ",
)

_PROFILE_TRAIT_MARKERS = (
    "отлично проявляет",
    "проявляет себя",
    "в целом",
    "как человек",
    "по характеру",
    "склонен",
    "склонна",
    "в профессии",
    "профессиях",
    "рожден",
    "натура",
    "тип личности",
    "всегда",
    "часто бывает",
    "характерная",
    "паспорт",
    "натальн",
    "знак ",
    "архетип",
    "стремится",
    "стремление",
    "заботится",
    "заботиться",
    "заботится о",
    "гармонии и пониманию",
    "такой человек",
    "ценит в",
    "любит когда",
    "отличается",
    "характеризуется",
)

_FAMILY_PROFILE_RE = re.compile(
    r"(?:^в семье\s+[А-ЯЁ][а-яё]+|"
    r"^[А-ЯЁ][а-яё]+\s+(?:стремится|заботится|склонен|склонна|любит|ценит))",
    re.I,
)

_THIRD_PERSON_TRAIT_RE = re.compile(
    r"\b(он|она)\s+(стремится|заботится|любит|ценит|склонен|склонна|отличается)",
    re.I,
)

_CROSS_DOMAIN_DUPLICATE_PHRASES = (
    "не распыля",
    "не угадыва",
    "выбери од",
    "скажи прям",
    "один вектор",
    "одну задач",
    "один понятный",
    "держи одну",
    "честный контакт",
    "без угадывания",
)

_HEADLINE_TOPIC_PATTERNS = (
    re.compile(r"^тон\s+", re.I),
    re.compile(r"^тема\s+", re.I),
    re.compile(r"^линия\s+", re.I),
    re.compile(r"^узкая\s+тема", re.I),
    re.compile(r"^близость\s+и\s+контакт$", re.I),
    re.compile(r"^работа\s+и\s+(дела|решения)$", re.I),
    re.compile(r"^дом\s+и\s+восстановление$", re.I),
    re.compile(r"^деньги\s+и\s+границы$", re.I),
)

_ACTION_IMPERATIVE_RE = re.compile(
    r"^(?:"
    r"скажи|выбери|сделай|закрой|проверь|напиши|позвони|удержи|держи|"
    r"отложи|заверши|доведи|спроси|попроси|выдели|отметь|снизи|раздели|"
    r"обсуди|помоги|возьми|начни|закончи|сохрани|позволь|дай|оставь|"
    r"тренируй|практикуй|учись|развивай|"
    r"не\s+(?:бер|дав|трать|обещай|форсируй|спеш|стро)"
    r")",
    re.I,
)

# Journey literary voice: practical move without command-lead (matches today_contract_fallbacks_v1).
_ACTION_LITERARY_MARKERS = (
    "если успеешь",
    "если что-то",
    "если удастся",
    "имеет смысл",
    "одна задача",
    "одна прямая",
    "одна честная",
    "один спокойный",
    "один ясный",
    "один короткий",
    "сегодня уместн",
    "до обеда",
    "до видимого результата",
    "к вечеру",
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def truncate_sentences(text: str, max_sentences: int, max_chars: int) -> str:
    raw = _norm_space(text)
    if not raw:
        return ""
    parts = [p.strip() for p in _SENTENCE_SPLIT.split(raw) if p.strip()]
    if not parts:
        parts = [raw]
    kept = parts[:max_sentences]
    out = " ".join(kept)
    if len(out) > max_chars:
        out = out[: max_chars - 1].rstrip(" ,;—-") + "…"
    return out


def has_today_marker(text: str) -> bool:
    low = (text or "").strip().lower()
    if not low:
        return False
    if any(m in low for m in _TODAY_MARKERS):
        return True
    if low.startswith("сегодня"):
        return True
    return False


def is_profile_trait_text(text: str | None) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    low = t.lower()
    # Today-framed navigation copy is never a Profile passport trait.
    if has_today_marker(t):
        return False
    if _FAMILY_PROFILE_RE.search(t):
        return True
    if _THIRD_PERSON_TRAIT_RE.search(low):
        return True
    if any(m in low for m in _PROFILE_TRAIT_MARKERS):
        return True
    # «Игорь …» / «Мария …» + trait without today framing
    if re.match(r"^[А-ЯЁ][а-яё]+\s+", t) and not has_today_marker(t):
        if any(w in low for w in ("проявляет", "склонен", "склонна", "характер", "личность", "професс", "стремится", "заботится")):
            return True
    if len(t) > MAX_STATUS_CHARS and not has_today_marker(t):
        return True
    # Multi-sentence biography tone
    if len(_SENTENCE_SPLIT.split(t)) >= 2 and not has_today_marker(t) and (" он " in low or " она " in low):
        return True
    return False


def is_headline_label(text: str | None) -> bool:
    t = _norm_space(text or "")
    if not t:
        return True
    if is_garbage_ritual_action_cue(t):
        return True
    if is_ru_abstract_topic_headline(t):
        return True
    if is_discardable_morning_focus(t):
        return True
    low = t.lower()
    if low in {
        "близость и контакт",
        "работа и решения",
        "работа и дела",
        "дом и восстановление",
        "семья и дом",
        "деньги и границы",
        "честный контакт",
        "тёплая поддержка",
        "завершение линии",
        "пауза перед тратой",
    }:
        return True
    for pat in _HEADLINE_TOPIC_PATTERNS:
        if pat.search(low):
            return True
    if len(t) < 48 and not re.search(r"[.!?]", t):
        if not _ACTION_IMPERATIVE_RE.search(low):
            words = t.split()
            if len(words) <= 5 and not any(w.endswith(("й", "и", "ь")) for w in words[:1]):
                if " и " in low or low.count(" ") <= 3:
                    return True
    return False


def is_valid_action_text(text: str | None) -> bool:
    """Accept imperative OR literary practical-move copy (not headlines / traits)."""
    t = truncate_sentences(_norm_space(text or ""), MAX_ACTION_SENTENCES, MAX_ACTION_CHARS)
    if len(t) < 10:
        return False
    if is_headline_label(t):
        return False
    if is_profile_trait_text(t):
        return False
    stripped = t.strip()
    if _ACTION_IMPERATIVE_RE.search(stripped):
        return True
    low = stripped.lower()
    if any(m in low for m in _ACTION_LITERARY_MARKERS) and len(stripped) >= 24:
        return True
    # Concrete observational move with outcome cue (domain fallbacks).
    if len(stripped) >= 40 and re.search(
        r"\b(?:обычно|часто|стоит|делает|помогает|уместн[аоы]?)\b",
        low,
    ):
        return True
    return False


def accept_status_source(text: str | None) -> str:
    t = _norm_space(text or "")
    if not t:
        return ""
    if is_profile_trait_text(t):
        return ""
    if is_headline_label(t) and not has_today_marker(t):
        return ""
    return t


def accept_narrative_source(text: str | None) -> str:
    """Reject profile summaries for any Today slot."""
    t = _norm_space(text or "")
    if not t or is_profile_trait_text(t):
        return ""
    if is_headline_label(t) and not has_today_marker(t):
        return ""
    return t


def normalize_domain_status(domain_id: str, text: str, fallback: str) -> str:
    if domain_id == "family" and is_profile_trait_text(text):
        return fallback
    src = accept_status_source(text)
    if not src:
        return fallback
    body = truncate_sentences(src, MAX_STATUS_SENTENCES, MAX_STATUS_CHARS)
    prefix = _DOMAIN_STATUS_PREFIX.get(domain_id, "Сегодня")
    if has_today_marker(body) and not body.lower().startswith("сегодня"):
        for part in _SENTENCE_SPLIT.split(body):
            p = part.strip()
            if has_today_marker(p):
                body = truncate_sentences(p, MAX_STATUS_SENTENCES, MAX_STATUS_CHARS)
                break
    if has_today_marker(body) or body.lower().startswith(prefix.lower()):
        return body
    clean = body.rstrip(".!? ")
    framed = f"{prefix} — {clean}."
    return truncate_sentences(framed, MAX_STATUS_SENTENCES, MAX_STATUS_CHARS)


def normalize_opportunity_risk(text: str, fallback: str) -> str:
    t = accept_narrative_source(text)
    if not t:
        return fallback
    out = truncate_sentences(t, MAX_OPPORTUNITY_RISK_SENTENCES, MAX_OPPORTUNITY_RISK_CHARS)
    if is_headline_label(out) or is_profile_trait_text(out):
        return fallback
    return out or fallback


def normalize_action(text: str, fallback: str) -> str:
    t = truncate_sentences(_norm_space(text), MAX_ACTION_SENTENCES, MAX_ACTION_CHARS)
    if is_valid_action_text(t):
        return t
    return fallback


def _slots_too_similar(a: str, b: str) -> bool:
    x = _norm_space(a).lower()
    y = _norm_space(b).lower()
    if not x or not y:
        return False
    if x == y:
        return True
    if x in y or y in x:
        return True
    for phrase in _CROSS_DOMAIN_DUPLICATE_PHRASES:
        if phrase in x and phrase in y:
            return True
    return False


def dedupe_domain_lens_slots(
    lens: dict[str, str],
    *,
    fallbacks: dict[str, str],
) -> dict[str, str]:
    out = dict(lens)
    order = ("status", "opportunity", "risk", "action")
    for i, slot in enumerate(order):
        val = out.get(slot, "")
        for prev in order[:i]:
            if _slots_too_similar(val, out.get(prev, "")):
                out[slot] = fallbacks[slot]
                break
    if _slots_too_similar(out.get("opportunity", ""), out.get("risk", "")):
        out["risk"] = fallbacks["risk"]
    if _slots_too_similar(out.get("status", ""), out.get("opportunity", "")):
        out["opportunity"] = fallbacks["opportunity"]
    return out


def dedupe_cross_domain_lenses(
    domains: dict[str, dict[str, str]],
    fallbacks_by_domain: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Each domain keeps distinct theme — no copy-paste across cards."""
    out: dict[str, dict[str, str]] = {k: dict(v) for k, v in domains.items()}
    for slot in ("status", "opportunity", "risk", "action"):
        seen: dict[str, str] = {}
        for domain_id in DOMAIN_ORDER:
            lens = out.get(domain_id)
            if not isinstance(lens, dict):
                continue
            if str(lens.get("evidence_status") or "") == "absent":
                continue
            text = str(lens.get(slot) or "")
            fb = fallbacks_by_domain.get(domain_id, {})
            for prev_domain, prev_text in seen.items():
                if _slots_too_similar(text, prev_text):
                    lens[slot] = fb.get(slot, text)
                    text = lens[slot]
                    break
            seen[domain_id] = text
    return out


def separate_growth_from_period(period: str, growth: str, growth_fallback: str) -> str:
    g = truncate_sentences(_norm_space(growth), 1, MAX_GROWTH_CHARS)
    p = truncate_sentences(_norm_space(period), 2, MAX_PERIOD_CHARS)
    if not g or _slots_too_similar(p, g):
        return growth_fallback
    if is_profile_trait_text(g):
        return growth_fallback
    return g


def apply_text_quality_gate_to_contract(
    contract: dict[str, Any],
    fallbacks_by_domain: dict[str, dict[str, str]],
    *,
    skip_absent_domains: bool = False,
) -> dict[str, Any]:
    """Normalize all user-facing strings to short Today navigation copy."""
    meta_fb = fallbacks_by_domain.get("_meta", {})
    out = dict(contract)

    period_raw = truncate_sentences(str((out.get("global_context") or {}).get("period") or ""), 2, MAX_PERIOD_CHARS)
    if is_profile_trait_text(period_raw):
        period_raw = meta_fb.get("period", period_raw)
    period = period_raw or meta_fb.get("period", "")

    growth_raw = str((out.get("personal_growth") or {}).get("development_point") or "")
    period_for_growth = period_raw or meta_fb.get("period", "")
    from todayflow_backend.services.today_contract_growth_v1 import (
        is_growth_skill_text,
        is_observation_not_growth,
        resolve_development_point,
    )

    if is_observation_not_growth(growth_raw) or not is_growth_skill_text(growth_raw):
        growth = resolve_development_point(period_for_growth, "")
    else:
        growth = resolve_development_point(period_for_growth, growth_raw)

    out["global_context"] = {"period": period}
    out["personal_growth"] = {"development_point": growth}

    domains = out.get("domains")
    if isinstance(domains, dict):
        new_domains: dict[str, Any] = {}
        for domain_id, lens in domains.items():
            if not isinstance(lens, dict):
                continue
            if skip_absent_domains and str(lens.get("evidence_status") or "") == "absent":
                new_domains[domain_id] = {
                    "status": "",
                    "opportunity": "",
                    "risk": "",
                    "action": "",
                    "evidence_status": "absent",
                }
                continue
            fb = fallbacks_by_domain.get(domain_id, {})
            normalized = {
                "status": normalize_domain_status(domain_id, str(lens.get("status") or ""), fb.get("status", "")),
                "opportunity": normalize_opportunity_risk(str(lens.get("opportunity") or ""), fb.get("opportunity", "")),
                "risk": normalize_opportunity_risk(str(lens.get("risk") or ""), fb.get("risk", "")),
                "action": normalize_action(str(lens.get("action") or ""), fb.get("action", "")),
                "evidence_status": str(lens.get("evidence_status") or "present"),
            }
            new_domains[domain_id] = dedupe_domain_lens_slots(normalized, fallbacks=fb)
        out["domains"] = dedupe_cross_domain_lenses(new_domains, fallbacks_by_domain)

    pa = normalize_action(str(out.get("primary_action") or ""), meta_fb.get("primary_action", ""))
    out["primary_action"] = pa
    return out


def validate_today_contract_text_quality_v1(contract: dict[str, Any]) -> list[str]:
    """P0.1.2 validation — navigation copy quality."""
    errors: list[str] = []
    domains = contract.get("domains")
    if not isinstance(domains, dict):
        return errors

    period = str((contract.get("global_context") or {}).get("period") or "")
    growth = str((contract.get("personal_growth") or {}).get("development_point") or "")
    from todayflow_backend.services.today_contract_growth_v1 import (
        is_growth_skill_text,
        is_observation_not_growth,
    )

    if _slots_too_similar(period, growth):
        errors.append("personal_growth duplicates global_context.period")
    if is_observation_not_growth(growth):
        errors.append("personal_growth reads as observation not skill")
    if not is_growth_skill_text(growth):
        errors.append("personal_growth not a growth skill")

    for domain_id, lens in domains.items():
        if not isinstance(lens, dict):
            continue
        if str(lens.get("evidence_status") or "") == "absent":
            continue
        status = str(lens.get("status") or "")
        if is_profile_trait_text(status):
            errors.append(f"domains.{domain_id}.status reads as profile trait")
        if not has_today_marker(status):
            errors.append(f"domains.{domain_id}.status missing today framing")

        action = str(lens.get("action") or "")
        if not is_valid_action_text(action):
            errors.append(f"domains.{domain_id}.action not imperative action")

        slots = [str(lens.get(s) or "") for s in ("status", "opportunity", "risk", "action")]
        for i, a in enumerate(slots):
            for j, b in enumerate(slots):
                if i < j and _slots_too_similar(a, b):
                    errors.append(f"domains.{domain_id} slots {i} and {j} duplicate")

        for slot in ("status", "opportunity", "risk"):
            if len(str(lens.get(slot) or "")) > MAX_STATUS_CHARS:
                errors.append(f"domains.{domain_id}.{slot} too long")

    # Cross-domain: same slot should not read as copy-paste (skip absent)
    for slot in ("status", "opportunity", "risk", "action"):
        texts: list[tuple[str, str]] = []
        for domain_id in DOMAIN_ORDER:
            lens = domains.get(domain_id)
            if isinstance(lens, dict) and str(lens.get("evidence_status") or "") != "absent":
                texts.append((domain_id, str(lens.get(slot) or "")))
        for i, (d1, t1) in enumerate(texts):
            for j, (d2, t2) in enumerate(texts):
                if i < j and _slots_too_similar(t1, t2):
                    errors.append(f"domains.{d1} and domains.{d2} duplicate in slot {slot}")

    pa = str(contract.get("primary_action") or "")
    if not is_valid_action_text(pa):
        errors.append("primary_action not imperative action")

    return errors
