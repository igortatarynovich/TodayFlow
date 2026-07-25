"""Day product logic capture session (sidecar packs).

Off by default. When enabled, records facts → interpretation → prompt → raw LLM →
postprocess → contract surfaces (color/spheres/goals/affirmations) without changing
user-facing generation results.

Never writes capture payloads into generation_logs. Sidecar files are for eval/dev.

Defect classes are architectural only (see DEFECT_CLASSES). There is no MODEL blame.
"""

from __future__ import annotations

import copy
import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

CAPTURE_CONTRACT = "day_product_logic_capture_v0"

# Architectural defect classes only — no MODEL.
DEFECT_CLASSES = (
    "INPUT",
    "THESIS",
    "PROMPT_SCHEMA",
    "RESPONSE_COHERENCE",
    "POSTPROCESS",
    "COLOR_PIPELINE",
    "SURFACE_ORPHAN",
    "SCENE_MISSING",
    "SPHERE_COVERAGE",
    "PARALLEL_FORECAST",
    "CHORUS_MUTED",
    "UI_DEDUP",
    "LIFECYCLE",
    "PROJECTION",
    "VALIDATION",
)

PRODUCT_SPHERE_IDS = (
    "work_decisions",
    "money",
    "relationships",
    "communication",
    "energy_body",
    "creativity",
    "rest_travel",
)

WIRE_DOMAIN_TO_PRODUCT = {
    "money_work": ("work_decisions", "money"),
    "relationships": ("relationships", "communication"),
    "family": ("relationships",),
}

_HUMOR_HINT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("irony", re.compile(r"ирони|сарказм|с улыбк", re.I)),
    ("domestic_joke", re.compile(r"шутк|забавн|смешн|подмигн", re.I)),
    ("vacation", re.compile(r"отпуск|уез|чемодан|смен.*обстанов", re.I)),
    ("romantic", re.compile(r"романт|свидан|флирт|нежн", re.I)),
    ("social", re.compile(r"приглашен|встреч|компани|друз", re.I)),
    ("invitation", re.compile(r"зов|приглас|неожиданн", re.I)),
    ("drop_everything", re.compile(r"вс[её]\s*брос|сбежать|уехать", re.I)),
)

_session_var: ContextVar["DayStoryCaptureSession | None"] = ContextVar(
    "day_story_capture_session_v0",
    default=None,
)


def get_day_story_capture_session() -> "DayStoryCaptureSession | None":
    return _session_var.get()


def day_story_capture_enabled() -> bool:
    sess = _session_var.get()
    return bool(sess and sess.enabled)


class DayStoryCaptureSession:
    """Mutable pack collector for one day product capture."""

    def __init__(
        self,
        *,
        case_id: str,
        label: str = "",
        redact: bool = False,
        out_dir: Path | None = None,
        target_date: str | None = None,
        user_id: int | str | None = None,
    ) -> None:
        self.enabled = True
        self.case_id = case_id
        self.label = label
        self.redact = redact
        self.out_dir = out_dir
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._last_interpretation: dict[str, Any] | None = None
        self._last_ritual: dict[str, Any] | None = None
        self.pack: dict[str, Any] = {
            "manifest": {
                "contract_version": CAPTURE_CONTRACT,
                "case_id": case_id,
                "label": label,
                "started_at": self.started_at,
                "target_date": target_date,
                "user_id": user_id,
                "production_path": True,
                "redacted": redact,
                "scenario_rubric": "DAY_SCENARIO_V1 Acts 0–VII",
            },
            "day_spine": {
                "ranked_drivers": [],
                "astro_event": None,
                "primary_conflict": None,
                "day_thesis": None,
                "strengthen_spheres": [],
                "support_spheres": [],
                "risk_spheres": [],
                "emotional_behavioral_dynamic": None,
                "natal_links": [],
                "claim_confidence": [],
                "day_history_shift": None,
            },
            "interpretive_chorus": {
                "astrology": [],
                "day_card": None,
                "day_number": None,
                "natal": [],
                "chorus_coherent": None,
                "notes": (
                    "Level 2: factors explain one conflict. "
                    "Named sky language (e.g. Moon in Pisces) is desired when tied to story."
                ),
            },
            "scenario_acts": {
                "prolog": {"present": False, "notes": "capture records inputs; engine not SoT yet"},
                "act_i_world": {"present": False, "payload": None},
                "act_ii_personal": {"present": False, "payload": None},
                "act_iii_conflict": {"present": False, "payload": None},
                "act_iv_consequences": {"present": False, "payload": None},
                "act_v_scenes": {"present": False, "scenes": []},
                "act_vi_props": {"present": False, "props": []},
                "act_vii_payoff": {"present": False, "payload": None},
            },
            "color": None,
            "spheres": {
                "wire_domains": [],
                "product_sphere_checklist": [],
            },
            "recommendations": None,
            "goals": None,
            "affirmations": None,
            "humor_and_hints": {
                "opportunities_in_raw_or_story": [],
                "emitted_in_final": [],
                "forced_empty_fields": False,
            },
            "prompt": None,
            "attempts": [],
            "final": None,
            "ui_projection": None,
            "lifecycle": {
                "get_calls_llm": False,
                "refresh_calls_llm": True,
                "force_rebuild_used": None,
                "interpretation_status": None,
                "used_fallback": None,
            },
            "defects": [],
            "editorial_review": {
                "q1_one_story_from_facts": None,
                "q2_personal_visible": None,
                "q3_single_conflict": None,
                "q4_scenes_from_conflict": None,
                "q5_raw_coherent_or_postprocess_broke": None,
                "q6_color_from_scene_or_pasted": None,
                "q7_avoid_color_amplifies_trap": None,
                "q8_do_goal_affirm_same_problem_no_dupe": None,
                "q9_living_author_not_json_form": None,
                "q10_raw_to_ui_loss": None,
                "q11_chorus_explains_not_parallel": None,
                "q12_card_archetype_number_tempo": None,
                "defect_classes": [],
                "notes": "",
            },
            "generation_metadata": {},
        }

    def record_lifecycle(self, **fields: Any) -> None:
        life = self.pack.setdefault("lifecycle", {})
        if isinstance(life, dict):
            life.update(fields)

    def record_day_spine(self, spine: dict[str, Any]) -> None:
        self.pack["day_spine"] = self._maybe_redact({**(self.pack.get("day_spine") or {}), **spine})

    def record_interpretation_snapshot(self, interpretation: dict[str, Any] | None) -> None:
        """Map interpretation into spine + provisional scenario act flags."""
        if not isinstance(interpretation, dict):
            return
        self._last_interpretation = interpretation
        pack = interpretation.get("day_events_pack") if isinstance(interpretation.get("day_events_pack"), dict) else {}
        drivers_raw = pack.get("ranked_drivers") if isinstance(pack.get("ranked_drivers"), list) else []
        drivers: list[dict[str, Any]] = []
        for item in drivers_raw[:3]:
            if isinstance(item, dict):
                drivers.append(
                    {
                        "id": item.get("id"),
                        "fact_ru": item.get("fact_ru") or item.get("title_ru") or item.get("title"),
                        "kind": item.get("kind") or item.get("family"),
                        "strength": item.get("strength"),
                    }
                )
            elif isinstance(item, str):
                drivers.append({"id": item, "fact_ru": None, "kind": None, "strength": None})

        thesis = interpretation.get("day_thesis") if isinstance(interpretation.get("day_thesis"), dict) else None
        conflict = interpretation.get("primary_conflict")
        claims = interpretation.get("derived_claims") if isinstance(interpretation.get("derived_claims"), list) else []
        claim_rows = []
        natal_links = []
        for c in claims:
            if not isinstance(c, dict):
                continue
            cid = str(c.get("id") or "")
            claim_rows.append(
                {
                    "id": cid,
                    "text": str(c.get("text") or c.get("claim_ru") or "")[:240],
                    "confidence": c.get("confidence") or c.get("evidence_status"),
                    "source": c.get("source"),
                }
            )
            if "natal" in cid or "transit" in cid or "personal" in cid:
                natal_links.append(claim_rows[-1])

        domains_present = list(interpretation.get("domains_present") or [])
        domains_absent = list(interpretation.get("domains_absent") or [])
        day_sky = interpretation.get("day_sky") if isinstance(interpretation.get("day_sky"), dict) else {}
        day_personal = interpretation.get("day_personal") if isinstance(interpretation.get("day_personal"), dict) else {}
        day_foundation = (
            interpretation.get("day_foundation") if isinstance(interpretation.get("day_foundation"), dict) else {}
        )

        astro_event = None
        if drivers:
            d0 = drivers[0]
            astro_event = {
                "what": d0.get("fact_ru") or d0.get("id"),
                "why_for_user": "see claim_confidence / natal_links",
                "evidence_ids": [d0.get("id")],
                "kind": d0.get("kind"),
            }

        self.record_day_spine(
            {
                "ranked_drivers": drivers,
                "astro_event": astro_event,
                "primary_conflict": conflict,
                "day_thesis": thesis,
                "strengthen_spheres": list(domains_present),
                "support_spheres": [],
                "risk_spheres": list(domains_absent),
                "emotional_behavioral_dynamic": day_personal.get("dynamic") or day_personal.get("summary"),
                "natal_links": natal_links[:12],
                "claim_confidence": claim_rows[:40],
                "day_foundation_keys": sorted(day_foundation.keys()) if day_foundation else [],
                "day_sky_keys": sorted(day_sky.keys()) if day_sky else [],
            }
        )
        self.record_interpretive_chorus(
            interpretation=interpretation,
            day_foundation=day_foundation,
            day_sky=day_sky,
            drivers=drivers,
            natal_links=natal_links,
        )

        acts = self.pack["scenario_acts"]
        acts["act_i_world"] = {
            "present": bool(day_sky or drivers),
            "payload": {
                "day_sky_keys": sorted(day_sky.keys()) if day_sky else [],
                "driver_count": len(drivers),
            },
        }
        acts["act_ii_personal"] = {
            "present": bool(day_personal or natal_links),
            "payload": {
                "day_personal_keys": sorted(day_personal.keys()) if day_personal else [],
                "natal_link_count": len(natal_links),
            },
        }
        label = None
        if isinstance(thesis, dict):
            label = thesis.get("label_ru")
        acts["act_iii_conflict"] = {
            "present": bool(label or conflict),
            "payload": {"day_thesis": thesis, "primary_conflict": conflict},
        }

    def record_interpretive_chorus(
        self,
        *,
        interpretation: dict[str, Any],
        day_foundation: dict[str, Any] | None = None,
        day_sky: dict[str, Any] | None = None,
        drivers: list[dict[str, Any]] | None = None,
        natal_links: list[dict[str, Any]] | None = None,
        ritual_context: dict[str, Any] | None = None,
        final_story: dict[str, Any] | None = None,
    ) -> None:
        """Level-2 chorus: astrology / day card / day number / natal explaining one conflict."""
        foundation = day_foundation if isinstance(day_foundation, dict) else {}
        sky = day_sky if isinstance(day_sky, dict) else {}
        ritual = ritual_context if isinstance(ritual_context, dict) else {}
        evidence = interpretation.get("evidence") if isinstance(interpretation.get("evidence"), list) else []

        astrology: list[dict[str, Any]] = []
        for d in drivers or []:
            if isinstance(d, dict) and (d.get("fact_ru") or d.get("id")):
                astrology.append(
                    {
                        "factor": d.get("fact_ru") or d.get("id"),
                        "kind": d.get("kind"),
                        "explains_conflict": None,
                        "named_sky_language": True,
                        "role": "astrology_what_happens",
                    }
                )
        # Lunar / ingress snippets from sky if present
        lunar = sky.get("lunar_phase") if isinstance(sky.get("lunar_phase"), dict) else {}
        if lunar.get("name"):
            astrology.append(
                {
                    "factor": lunar.get("name"),
                    "kind": "lunar_phase",
                    "guidance": lunar.get("guidance"),
                    "explains_conflict": None,
                    "role": "astrology_what_happens",
                }
            )

        card_name = None
        number_val = None
        for ev in evidence:
            if not isinstance(ev, dict):
                continue
            src = str(ev.get("source") or "")
            text = str(ev.get("text") or ev.get("fact_ru") or "")
            if "tarot" in src or str(ev.get("id") or "") == "ev.ritual.card":
                card_name = text or card_name
            if "numerology" in src or str(ev.get("id") or "") == "ev.ritual.number":
                number_val = text or number_val
        if ritual.get("tarot_name_ru") or ritual.get("tarot_main_id"):
            card_name = str(ritual.get("tarot_name_ru") or ritual.get("tarot_main_id") or card_name)
        if ritual.get("numerology_value") is not None:
            number_val = str(ritual.get("numerology_value"))

        num_block = foundation.get("numerology") if isinstance(foundation.get("numerology"), dict) else {}
        if number_val is None and num_block:
            number_val = str(
                num_block.get("personal_day")
                or num_block.get("universal_day")
                or num_block.get("day_number")
                or ""
            ) or None

        # Detect whether final prose names sky factors / card / number
        prose_blob = ""
        if isinstance(final_story, dict):
            try:
                prose_blob = json.dumps(final_story, ensure_ascii=False)
            except Exception:
                prose_blob = str(final_story)
        named_in_prose = bool(
            re.search(
                r"луна|рыб|меркури|венер|марс|сатурн|юпитер|нептун|"
                r"отшельник|маг|жрец|императ|число|персональн",
                prose_blob,
                re.I,
            )
        )

        day_card = {
            "name": card_name,
            "role": "archetype_for_conflict" if card_name else "missing",
            "present_in_inputs": bool(card_name),
            "named_in_final_prose": bool(card_name and card_name[:12].lower() in prose_blob.lower())
            if card_name and prose_blob
            else False,
            "notes": "Must describe today's conflict archetype — not a second forecast.",
        }
        day_number = {
            "value": number_val,
            "role": "how_to_live_conflict" if number_val else "missing",
            "present_in_inputs": bool(number_val),
            "foundation_numerology": {
                "personal_day": num_block.get("personal_day"),
                "universal_day": num_block.get("universal_day"),
            }
            if num_block
            else None,
            "notes": "Colors tempo/style of the same conflict — not a new story.",
        }

        has_factors = bool(astrology or card_name or number_val or natal_links)
        chorus_coherent = None
        if has_factors and isinstance(final_story, dict):
            # Heuristic: muted if factors exist but prose never names sky/card/number language
            if not named_in_prose:
                chorus_coherent = False
                self.add_defect(
                    "interpretive_chorus_muted_in_prose",
                    "Sky/card/number/natal factors present in inputs but final prose lacks named explanatory language.",
                    cls="CHORUS_MUTED",
                )
            else:
                chorus_coherent = True

        if card_name and isinstance(final_story, dict):
            # If card exists only as parallel UI module later — capture notes role; parallel check is editorial
            pass

        self.pack["interpretive_chorus"] = self._maybe_redact(
            {
                "astrology": astrology,
                "day_card": day_card,
                "day_number": day_number,
                "natal": list(natal_links or [])[:12],
                "chorus_coherent": chorus_coherent,
                "named_explanatory_language_in_final": named_in_prose if final_story else None,
                "notes": (
                    "Level 2 chorus. Prefer 'Moon entered Pisces…' tied to conflict over "
                    "generic caution without factors."
                ),
            }
        )

    def record_color(
        self,
        *,
        color_symbol: dict[str, Any] | None,
        color_name: str = "",
        trap: str = "",
        do_items: list[str] | None = None,
        domains_present: list[str] | None = None,
        preset_inputs: dict[str, Any] | None = None,
    ) -> None:
        sym = color_symbol if isinstance(color_symbol, dict) else {}
        name = str(sym.get("name") or color_name or "").strip()
        why_catalog = str(sym.get("benefit_ru") or sym.get("story_ru") or "").strip()
        avoid_name = str(sym.get("avoid_color_ru") or "").strip()
        avoid_why = str(sym.get("avoid_why_ru") or "").strip()
        trap_l = (trap or "").lower()
        why_l = why_catalog.lower()
        avoid_l = avoid_why.lower()
        linked_trap = bool(trap_l and why_l and any(tok in why_l for tok in trap_l.split() if len(tok) > 4))
        avoid_amplifies = bool(trap_l and avoid_l and any(tok in avoid_l for tok in trap_l.split() if len(tok) > 4))

        self.pack["color"] = self._maybe_redact(
            {
                "recommended": {
                    "name": name,
                    "why_catalog": why_catalog,
                    "why_linked_to_story": linked_trap,
                    "supports_or_compensates": None,
                },
                "apply": {
                    "clothing": sym.get("clothing_ru"),
                    "accessory": sym.get("accessory_ru"),
                    "workspace": None,
                    "makeup": None,
                    "ui_or_bg": None,
                    "amount": sym.get("amount_ru"),
                },
                "avoid": {
                    "name": avoid_name,
                    "why_catalog": avoid_why,
                    "amplifies_day_trap": avoid_amplifies,
                },
                "provenance": {
                    "pipeline": "date_preset+catalog",
                    "preset_inputs": preset_inputs or {},
                    "origin_scene_id": None,
                },
                "coherence": {
                    "with_trap": linked_trap,
                    "with_do": False,
                    "with_domains": bool(domains_present),
                    "notes": (
                        "Color chosen before interpretation/LLM; catalog copy is not scene-derived."
                    ),
                },
            }
        )
        if name and not linked_trap:
            self.add_defect(
                "color_not_derived_from_trap_or_scene",
                "Recommended color catalog copy does not reference day trap/scene; pipeline=date_preset+catalog.",
                cls="COLOR_PIPELINE",
            )
        if avoid_name and trap and not avoid_amplifies:
            self.add_defect(
                "avoid_color_not_tied_to_trap",
                "Avoid-color why-text does not clearly amplify the day's trap.",
                cls="COLOR_PIPELINE",
            )

    def record_prompt(
        self,
        *,
        system: str,
        user_full: str,
        user_sent: str,
        prompt_version: str,
        model: str | None = None,
    ) -> None:
        self.pack["prompt"] = {
            "system": system,
            "user_full": self._maybe_redact_str(user_full),
            "user_sent": self._maybe_redact_str(user_sent),
            "user_full_chars": len(user_full),
            "user_sent_chars": len(user_sent),
            "truncated": len(user_full) > len(user_sent),
            "prompt_version": prompt_version,
            "model": model,
            "editorial_editor_checklist": [
                "Is user JSON one readable day story?",
                "Are fields independent form answers or one drama?",
                "Are personal facts human-readable?",
            ],
        }
        meta = self.pack.setdefault("generation_metadata", {})
        if isinstance(meta, dict):
            meta["prompt_version"] = prompt_version
            meta["model"] = model

    def record_attempt(
        self,
        *,
        attempt_index: int,
        raw_response: str | None,
        parsed: dict[str, Any] | None,
        after_normalize: dict[str, Any] | None,
        after_gate: dict[str, Any] | None,
        phrase_ok: bool | None = None,
        phrase_hits: list[str] | None = None,
        status: str = "unknown",
        reject_reason: str | None = None,
    ) -> None:
        self.pack["attempts"].append(
            {
                "attempt_index": attempt_index,
                "raw_response": raw_response,
                "parsed": self._maybe_redact(parsed),
                "after_normalize": self._maybe_redact(after_normalize),
                "after_gate": self._maybe_redact(after_gate),
                "phrase_ok": phrase_ok,
                "phrase_hits": list(phrase_hits or []),
                "status": status,
                "reject_reason": reject_reason,
            }
        )
        self._scan_humor_opportunities(raw_response, parsed, after_gate)

    def record_final(
        self,
        *,
        story: dict[str, Any] | None,
        contract: dict[str, Any] | None = None,
        used_fallback: bool = False,
    ) -> None:
        story = story if isinstance(story, dict) else {}
        ds = story
        unavailable = str(story.get("interpretation_status") or "") == "unavailable"
        expect = str(story.get("expect") or "")
        trap = str(story.get("trap") or "")
        do_list = list(story.get("do") or []) if isinstance(story.get("do"), list) else []
        avoid_list = list(story.get("avoid") or []) if isinstance(story.get("avoid"), list) else []
        domains = story.get("domains") if isinstance(story.get("domains"), dict) else {}
        talisman = story.get("talisman") if isinstance(story.get("talisman"), dict) else {}
        practice = (
            story.get("practice_recommendation")
            if isinstance(story.get("practice_recommendation"), dict)
            else {}
        )
        evening = str(story.get("evening_closure") or "")
        vibe_strokes = list(story.get("vibe_strokes") or []) if isinstance(story.get("vibe_strokes"), list) else []

        self.pack["recommendations"] = self._maybe_redact(
            {
                "expect": expect,
                "trap": trap,
                "do": do_list,
                "avoid": avoid_list,
                "primary_action": (contract or {}).get("primary_action") if isinstance(contract, dict) else None,
                "today_move": story.get("today_move"),
                "events_lead": story.get("events_lead"),
            }
        )

        # Refresh Level-2 chorus against final prose
        interp = self._last_interpretation if isinstance(self._last_interpretation, dict) else {}
        foundation = interp.get("day_foundation") if isinstance(interp.get("day_foundation"), dict) else {}
        sky = interp.get("day_sky") if isinstance(interp.get("day_sky"), dict) else {}
        spine = self.pack.get("day_spine") if isinstance(self.pack.get("day_spine"), dict) else {}
        self.record_interpretive_chorus(
            interpretation=interp,
            day_foundation=foundation,
            day_sky=sky,
            drivers=list(spine.get("ranked_drivers") or []),
            natal_links=list(spine.get("natal_links") or []),
            ritual_context=self._last_ritual,
            final_story=story,
        )

        wire_domains = []
        product_checklist = []
        present_ids: list[str] = []
        for did, lens in domains.items():
            if not isinstance(lens, dict):
                continue
            present = bool(
                str(lens.get("status") or "").strip()
                or str(lens.get("opportunity") or "").strip()
                or str(lens.get("risk") or "").strip()
            )
            if present:
                present_ids.append(str(did))
            wire_domains.append(
                {
                    "id": did,
                    "present": present,
                    "status": lens.get("status"),
                    "opportunity": lens.get("opportunity"),
                    "risk": lens.get("risk"),
                    "action": lens.get("action"),
                    "evidence_status": lens.get("evidence_status"),
                }
            )

        mapped_product: set[str] = set()
        for wid in present_ids:
            for pid in WIRE_DOMAIN_TO_PRODUCT.get(wid, ()):
                mapped_product.add(pid)

        for pid in PRODUCT_SPHERE_IDS:
            in_story = pid in mapped_product
            product_checklist.append(
                {
                    "id": pid,
                    "status": "strong_or_active" if in_story else "not_in_story",
                    "evidence": f"mapped_from_wire={sorted(present_ids)}" if in_story else None,
                    "can_do": None,
                    "risk": None,
                    "domestic_example": None,
                    "in_ui": in_story,
                    "origin_scene_id": None,
                }
            )
            if not in_story:
                # not every sphere every day — only flag coverage gap if zero scenes at all
                pass

        self.pack["spheres"] = {
            "wire_domains": self._maybe_redact(wire_domains),
            "product_sphere_checklist": product_checklist,
        }
        if not present_ids:
            self.add_defect(
                "no_relevant_scenes_or_domains",
                "No present domain lenses / Act V scenes on final story.",
                cls="SCENE_MISSING",
            )
        else:
            # SPHERE_COVERAGE: product spheres beyond wire Model B never appear as first-class scenes
            missing_product = [p for p in PRODUCT_SPHERE_IDS if p not in mapped_product]
            if missing_product:
                self.add_defect(
                    "product_spheres_not_on_wire",
                    f"Product sphere ids without wire scene: {missing_product}. Wire Model B only.",
                    cls="SPHERE_COVERAGE",
                )

        kind = str(practice.get("kind") or "").strip()
        text = str(practice.get("text") or "").strip()
        affirm = {
            "practice_recommendation_if_affirmation": practice if kind == "affirmation" else None,
            "kind": kind or None,
            "text": text if kind == "affirmation" else None,
            "reason": practice.get("reason") if kind == "affirmation" else None,
            "compensates_trap": None,
            "orphan_universal": None,
            "origin_scene_id": None,
        }
        if kind == "affirmation" and text:
            trap_l = trap.lower()
            text_l = text.lower()
            linked = bool(trap_l and any(tok in text_l for tok in trap_l.split() if len(tok) > 4))
            affirm["compensates_trap"] = linked
            affirm["orphan_universal"] = (not linked) or bool(
                re.search(r"изобил|вселенн|притягива", text_l)
            )
            if affirm["orphan_universal"]:
                self.add_defect(
                    "affirmation_orphan_or_universal",
                    "Affirmation does not clearly compensate trap / looks universal.",
                    cls="SURFACE_ORPHAN",
                )
        elif kind and kind != "none" and kind != "affirmation":
            affirm["note"] = f"practice_recommendation.kind={kind} (not affirmation)"
        else:
            self.add_defect(
                "no_scene_derived_affirmation",
                "No affirmation prop derived from a scene (practice_recommendation empty/none).",
                cls="SURFACE_ORPHAN",
            )
        self.pack["affirmations"] = self._maybe_redact(affirm)

        self.pack["goals"] = self._maybe_redact(
            {
                "suggested_from_contract": do_list[:3],
                "user_goal_if_any": None,
                "coherence": {
                    "maps_to_driver": None,
                    "solves_day_problem": None,
                    "one_day_feasible": None,
                    "duplicates_do": True if do_list else None,
                    "notes": "Product day goals are not a separate LLM surface; chips derive from do/primary_action.",
                },
                "origin_scene_id": None,
            }
        )
        self.add_defect(
            "goals_not_scene_props",
            "Day goals are user/chips derived from do — not Act VI props with scene provenance.",
            cls="SURFACE_ORPHAN",
        )

        # Refresh color coherence once trap known
        color = self.pack.get("color")
        if isinstance(color, dict) and trap:
            self.record_color(
                color_symbol={
                    "name": (color.get("recommended") or {}).get("name"),
                    "benefit_ru": (color.get("recommended") or {}).get("why_catalog"),
                    "clothing_ru": (color.get("apply") or {}).get("clothing"),
                    "accessory_ru": (color.get("apply") or {}).get("accessory"),
                    "amount_ru": (color.get("apply") or {}).get("amount"),
                    "avoid_color_ru": (color.get("avoid") or {}).get("name"),
                    "avoid_why_ru": (color.get("avoid") or {}).get("why_catalog"),
                },
                trap=trap,
                do_items=[str(x) for x in do_list],
                domains_present=present_ids,
                preset_inputs=(color.get("provenance") or {}).get("preset_inputs"),
            )

        acts = self.pack["scenario_acts"]
        acts["act_iv_consequences"] = {
            "present": bool(expect or do_list or avoid_list),
            "payload": {"expect": expect, "do": do_list, "avoid": avoid_list},
            "notes": "Current slots mix consequences and advice (do).",
        }
        scenes = []
        for wd in wire_domains:
            if not wd.get("present"):
                continue
            scenes.append(
                {
                    "sphere_id": wd["id"],
                    "why_important": wd.get("status"),
                    "conflict_manifestation": None,
                    "opportunity": wd.get("opportunity"),
                    "trap": wd.get("risk"),
                    "origin": "wire_domain_lens",
                }
            )
        acts["act_v_scenes"] = {"present": bool(scenes), "scenes": self._maybe_redact(scenes)}
        props = [
            {
                "kind": "color",
                "origin_scene_id": None,
                "pipeline": "date_preset+catalog",
                "value": (self.pack.get("color") or {}).get("recommended") if isinstance(self.pack.get("color"), dict) else None,
            },
            {
                "kind": "affirmation",
                "origin_scene_id": None,
                "value": affirm.get("text"),
            },
            {
                "kind": "goal",
                "origin_scene_id": None,
                "value": do_list[:1],
            },
        ]
        acts["act_vi_props"] = {"present": True, "props": self._maybe_redact(props)}
        acts["act_vii_payoff"] = {
            "present": bool(evening),
            "payload": {"evening_closure": evening, "vibe_closing": story.get("vibe_closing")},
        }
        acts["prolog"] = {
            "present": bool((self.pack.get("day_spine") or {}).get("day_history_shift")),
            "notes": "day_history may be in prompt; explicit day_shift chapter not SoT yet",
        }

        humor = self.pack.get("humor_and_hints") if isinstance(self.pack.get("humor_and_hints"), dict) else {}
        emitted = []
        for stroke in vibe_strokes:
            emitted.append({"kind": "vibe_stroke", "text": str(stroke)[:200]})
        humor["emitted_in_final"] = emitted
        humor["forced_empty_fields"] = False
        self.pack["humor_and_hints"] = humor

        self.pack["final"] = self._maybe_redact(
            {
                "story": {
                    "interpretation_status": story.get("interpretation_status"),
                    "theme": story.get("theme"),
                    "day_thesis": story.get("day_thesis"),
                    "primary_conflict": story.get("primary_conflict"),
                    "events_lead": story.get("events_lead"),
                    "expect": expect,
                    "trap": trap,
                    "do": do_list,
                    "avoid": avoid_list,
                    "story": story.get("story"),
                    "talisman": talisman,
                    "practice_recommendation": practice,
                    "evening_closure": evening,
                    "vibe_strokes": vibe_strokes,
                    "domains": domains,
                },
                "today_contract_slice": {
                    "primary_action": (contract or {}).get("primary_action") if isinstance(contract, dict) else None,
                    "domains": (contract or {}).get("domains") if isinstance(contract, dict) else None,
                    "day_story_keys": (
                        sorted(((contract or {}).get("day_story") or {}).keys())
                        if isinstance(contract, dict) and isinstance(contract.get("day_story"), dict)
                        else None
                    ),
                },
                "used_fallback": used_fallback,
                "unavailable": unavailable,
            }
        )
        self.record_lifecycle(
            interpretation_status=story.get("interpretation_status"),
            used_fallback=used_fallback,
        )

    def record_ui_projection(self, projection: dict[str, Any] | None) -> None:
        self.pack["ui_projection"] = self._maybe_redact(projection)

    def record_day_history(self, history: dict[str, Any] | None) -> None:
        if not isinstance(history, dict):
            return
        spine = self.pack.get("day_spine") if isinstance(self.pack.get("day_spine"), dict) else {}
        spine["day_history_shift"] = self._maybe_redact(
            {
                "yesterday_date": (history.get("yesterday") or {}).get("date")
                if isinstance(history.get("yesterday"), dict)
                else None,
                "fusion_score_delta_vs_yesterday": history.get("fusion_score_delta_vs_yesterday"),
                "keys": sorted(history.keys()),
            }
        )
        self.pack["day_spine"] = spine

    def add_defect(self, code: str, detail: str, *, cls: str = "VALIDATION") -> None:
        if cls == "MODEL":
            cls = "VALIDATION"
            detail = f"[reclassified from MODEL] {detail}"
        if cls not in DEFECT_CLASSES:
            detail = f"[unknown class={cls} normalized] {detail}"
            cls = "VALIDATION"
        # de-dupe by code
        existing = {d.get("code") for d in self.pack.get("defects") or []}
        if code in existing:
            return
        self.pack["defects"].append({"code": code, "class": cls, "detail": detail})

    def _scan_humor_opportunities(self, *blobs: Any) -> None:
        text_parts: list[str] = []
        for b in blobs:
            if isinstance(b, str):
                text_parts.append(b)
            elif isinstance(b, dict):
                try:
                    text_parts.append(json.dumps(b, ensure_ascii=False))
                except Exception:
                    text_parts.append(str(b))
        blob = "\n".join(text_parts)
        humor = self.pack.setdefault("humor_and_hints", {})
        if not isinstance(humor, dict):
            return
        found = list(humor.get("opportunities_in_raw_or_story") or [])
        seen = {f.get("kind") for f in found if isinstance(f, dict)}
        for kind, pat in _HUMOR_HINT_PATTERNS:
            if kind in seen:
                continue
            if pat.search(blob):
                found.append({"kind": kind, "source": "raw_or_parsed_scan"})
        humor["opportunities_in_raw_or_story"] = found

    def finalize(self) -> dict[str, Any]:
        self.pack["manifest"]["finished_at"] = datetime.now(timezone.utc).isoformat()
        life = self.pack.get("lifecycle") if isinstance(self.pack.get("lifecycle"), dict) else {}
        if (
            life.get("used_fallback")
            and life.get("force_rebuild_used") is False
            and not life.get("llm_intentionally_skipped")
        ):
            self.add_defect(
                "get_path_skipped_llm",
                "force_rebuild=False skipped LLM; facts-only/unavailable path used.",
                cls="LIFECYCLE",
            )
        if (
            not self.pack.get("attempts")
            and life.get("force_rebuild_used")
            and not life.get("llm_intentionally_skipped")
            and life.get("used_fallback")
        ):
            self.add_defect(
                "llm_configured_but_no_attempts_recorded",
                "force_rebuild path expected LLM attempts; none recorded (config/parse fail).",
                cls="LIFECYCLE",
            )
        return self.pack

    def write_pack(self, *, stem: str | None = None) -> Path | None:
        pack = self.finalize()
        if self.out_dir is None:
            return None
        self.out_dir.mkdir(parents=True, exist_ok=True)
        name = stem or f"{self.case_id}.json"
        if not name.endswith(".json"):
            name = f"{name}.json"
        path = self.out_dir / name
        path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path = path.with_suffix(".md")
        md_path.write_text(self.to_markdown_summary(), encoding="utf-8")
        return path

    def to_markdown_summary(self) -> str:
        pack = self.pack
        defects = pack.get("defects") or []
        spine = pack.get("day_spine") or {}
        color = pack.get("color") or {}
        life = pack.get("lifecycle") or {}
        lines = [
            f"# Day product capture `{pack.get('manifest', {}).get('case_id')}`",
            "",
            f"- date: `{pack.get('manifest', {}).get('target_date')}`",
            f"- attempts: {len(pack.get('attempts') or [])}",
            f"- interpretation_status: `{life.get('interpretation_status')}`",
            f"- force_rebuild: `{life.get('force_rebuild_used')}`",
            f"- drivers: {len(spine.get('ranked_drivers') or [])}",
            f"- color: `{(color.get('recommended') or {}).get('name')}` pipeline=`{(color.get('provenance') or {}).get('pipeline')}`",
            "",
            "## Defects (architectural)",
        ]
        if not defects:
            lines.append("- (none auto-recorded)")
        for d in defects:
            lines.append(f"- `{d.get('class')}` `{d.get('code')}`: {d.get('detail')}")
        lines.append("")
        lines.append("## Editorial review")
        lines.append("Fill `editorial_review` in the JSON pack (q1–q10).")
        lines.append("")
        return "\n".join(lines)

    def _maybe_redact(self, value: Any) -> Any:
        if not self.redact:
            return copy.deepcopy(value)
        return _redact_value(value)

    def _maybe_redact_str(self, value: str) -> str:
        if not self.redact:
            return value
        out = _redact_value(value)
        return out if isinstance(out, str) else value


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            lk = str(k).lower()
            if lk in {"first_name", "last_name", "display_name", "full_name", "birth_name"}:
                out[k] = "[redacted]"
            elif lk in {"birth_date", "location_name", "latitude", "longitude"}:
                out[k] = "[redacted]"
            else:
                out[k] = _redact_value(v)
        return out
    if isinstance(value, list):
        return [_redact_value(v) for v in value]
    if isinstance(value, str):
        return re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[date]", value)
    return value


@contextmanager
def day_story_capture_session(
    *,
    case_id: str,
    label: str = "",
    redact: bool = False,
    out_dir: Path | str | None = None,
    target_date: str | None = None,
    user_id: int | str | None = None,
) -> Iterator[DayStoryCaptureSession]:
    session = DayStoryCaptureSession(
        case_id=case_id,
        label=label,
        redact=redact,
        out_dir=Path(out_dir) if out_dir else None,
        target_date=target_date,
        user_id=user_id,
    )
    token = _session_var.set(session)
    try:
        yield session
    finally:
        _session_var.reset(token)
