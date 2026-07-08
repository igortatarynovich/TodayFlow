"""Narrative selection logic for Lite and Full reports aligned with Convention v1."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, Dict, List, Sequence, Set

from todayflow_backend.content import templates
from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.i18n import translate


LITE_PLAN: Sequence[dict] = [
    {"section": "Emotional Patterns", "sub_block": "Emotional Baseline"},
    {"section": "Emotional Patterns", "sub_block": "Stress Response"},
    {"section": "Relationships", "sub_block": "Connection Style"},
]

FULL_REPORT_PLAN: Sequence[dict] = [
    {"type": "executive_summary", "section": "Executive Summary"},
    {
        "section": "Core Personality",
        "source_section": "Emotional Patterns",
        "sub_blocks": [
            {"name": "Emotional Baseline", "limit": 2},
        ],
    },
    {
        "section": "Emotional Patterns",
        "source_section": "Emotional Patterns",
        "sub_blocks": [
            {"name": "Emotional Baseline", "limit": 1},
            {"name": "Stress Response", "limit": 2},
            {"name": "Recovery & Regulation", "limit": 1},
        ],
    },
    {
        "section": "Relationships",
        "source_section": "Relationships",
        "sub_blocks": [
            {"name": "Connection Style", "limit": 1},
            {"name": "Attachment & Boundaries", "limit": 1},
            {"name": "Conflict Patterns", "limit": 1},
            {"name": "Growth in Relationships", "limit": 1},
        ],
    },
    {
        "section": "Career & Responsibility",
        "source_section": "Career & Responsibility",
        "sub_blocks": [
            {"name": "Career Baseline", "limit": 1},
            {"name": "Pressure & Burnout", "limit": 1},
            {"name": "Recovery & Sustainability", "limit": 1},
            {"name": "Growth Levers", "limit": 1},
        ],
    },
    {
        "section": "Money & Security",
        "source_section": "Money & Security",
        "sub_blocks": [
            {"name": "Security Orientation", "limit": 1},
            {"name": "Risk & Control", "limit": 1},
            {"name": "Stress Around Resources", "limit": 1},
            {"name": "Sustainable Financial Behavior", "limit": 1},
        ],
    },
    {
        "section": "Life Themes",
        "source_section": "Life Themes",
        "sub_blocks": [
            {"name": "Recurring Patterns", "limit": 1},
            {"name": "Long-Term Orientation", "limit": 1},
            {"name": "Integrative Perspective", "limit": 1},
        ],
    },
    {
        "section": "Sexuality & Intimacy",
        "source_section": "Sexuality & Intimacy",
        "sub_blocks": [
            {"name": "Desire Style", "limit": 1},
            {"name": "Intimacy Patterns", "limit": 1},
            {"name": "Boundaries & Taboos", "limit": 1},
        ],
    },
    {
        "section": "Health & Body",
        "source_section": "Health & Body",
        "sub_blocks": [
            {"name": "Movement & Activity", "limit": 1},
            {"name": "Vulnerable Areas", "limit": 1},
            {"name": "Health Approach", "limit": 1},
        ],
    },
    {
        "section": "Creativity & Expression",
        "source_section": "Creativity & Expression",
        "sub_blocks": [
            {"name": "Expression Style", "limit": 1},
            {"name": "Play & Joy", "limit": 1},
            {"name": "Creative Projects", "limit": 1},
        ],
    },
    {"type": "integration", "section": "Practical Integration"},
]

ARC_STAGES = {
    "base": 18,
    "baseline": 18,
    "stress": 14,
    "tension": 14,
    "recovery": 12,
    "integration": 10,
    "growth": 8,
}

LAYER_OBSERVATION = "observation"
LAYER_INTERPRETATION = "interpretation"
LAYER_CONTEXT = "context"

LITE_LAYER_SEQUENCE = [LAYER_OBSERVATION, LAYER_INTERPRETATION]
FULL_LAYER_SEQUENCE = [LAYER_OBSERVATION, LAYER_INTERPRETATION, LAYER_CONTEXT]

SYNTHETIC_LAYER_TEXT = {
    LAYER_INTERPRETATION: [
        "What this really signals is {meaning}. That perspective explains why the baseline feels the way it does.",
        "Underneath, it is about {meaning}. Seeing that link keeps the pattern from feeling random.",
    ],
    LAYER_CONTEXT: [
        "You usually notice this around {meaning} moments—work, relationships, or self-talk echo the same dynamic.",
        "In everyday life it tends to surface when choices touch {meaning}. That is where the pattern becomes tangible.",
    ],
}

LITE_HOOK_MESSAGES = [
    "This is only the first pass through {section}. The full report continues into integration and growth.",
    "Lite highlights the pattern; the full report finishes the arc for {section} with context and guidance.",
    "Curious how {section} resolves? The paid layer unpacks integration and practical moves.",
]


@dataclass
class NarrativeContext:
    axis_priority: Dict[str, int]
    axis_values: Dict[str, float]
    dominant_axes: Set[str]
    active_modulators: Set[str]
    used_meanings: DefaultDict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    global_meanings: Set[str] = field(default_factory=set)
    axis_memory: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    seed: int = 0
    report_type: str = "lite"
    locale: str = "en"


class NarrativeEngine:
    """Handles selection of paragraphs for Lite and Full reports."""

    def __init__(self, templates_path=None):
        self.templates = templates.load_templates(templates_path)
        self.templates_by_section: DefaultDict[str, DefaultDict[str, List[templates.ParagraphTemplate]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.meaning_templates: DefaultDict[
            str, DefaultDict[str, DefaultDict[str, DefaultDict[str, List[templates.ParagraphTemplate]]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
        for tpl in self.templates:
            self.templates_by_section[tpl.section][tpl.sub_block].append(tpl)
            self.meaning_templates[tpl.section][tpl.sub_block][tpl.meaning_type][tpl.layer].append(tpl)
        self.facets = self._load_facets()
        self.bridges = self._load_bridges()

    def build_lite_preview(
        self,
        internal_model: models.InternalModelSnapshot,
        overrides: dict[str, bool] | None = None,
        text_overrides: dict[tuple[str, str], str] | None = None,
        user_id: int | None = None,
        locale: str | None = None,
    ) -> List[models.Interpretation]:
        context = self._build_context(internal_model, user_id, report_type="lite", locale=locale)
        paragraphs: List[models.Interpretation] = []
        section_order: List[str] = []
        seen_sections: Set[str] = set()
        for block in LITE_PLAN:
            rule_id = f"lite::{block['section']}::{block['sub_block']}"
            block_paragraphs = self._select_meaning_bundle(
                source_section=block["section"],
                display_section=block["section"],
                sub_block=block["sub_block"],
                layer_sequence=LITE_LAYER_SEQUENCE,
                context=context,
                overrides=overrides,
                text_overrides=text_overrides,
                rule_id=rule_id,
                locale=locale,
            )
            if block_paragraphs:
                paragraphs.extend(block_paragraphs)
                if block["section"] == "Emotional Patterns":
                    facet = self._pick_facet(context, block_paragraphs[0].paragraph_id)
                    if facet:
                        paragraphs.append(facet)
                    bridge = self._build_bridge(context, block_paragraphs[0].paragraph_id)
                    if bridge:
                        paragraphs.append(bridge)
                if block["section"] not in seen_sections:
                    seen_sections.add(block["section"])
                    section_order.append(block["section"])
        for section in section_order:
            hook = self._build_lite_hook(section, context)
            if hook:
                paragraphs.append(hook)
        return paragraphs

    def build_full_sections(
        self,
        snapshot: models.ChartSnapshot,
        internal_model: models.InternalModelSnapshot,
        overrides: dict[str, bool] | None = None,
        text_overrides: dict[tuple[str, str], str] | None = None,
        user_id: int | None = None,
        locale: str | None = None,
    ) -> List[models.FullReportSection]:
        context = self._build_context(internal_model, user_id, report_type="full", locale=locale)
        sections: List[models.FullReportSection] = []
        for block in FULL_REPORT_PLAN:
            if block.get("type") == "executive_summary":
                paragraphs = self._build_executive_summary(snapshot, internal_model)
            elif block.get("type") == "integration":
                paragraphs = self._build_integration_paragraphs()
            else:
                paragraphs = []
                source_section = block["source_section"]
                for sub_spec in block.get("sub_blocks", []):
                    block_paragraphs = self._build_block(
                        source_section=source_section,
                        display_section=block["section"],
                        sub_block=sub_spec["name"],
                        limit=sub_spec.get("limit", 1),
                        context=context,
                        overrides=overrides,
                        text_overrides=text_overrides,
                        rule_prefix=f"full::{source_section}::{sub_spec['name']}",
                        locale=locale,
                    )
                    if block_paragraphs:
                        paragraphs.extend(block_paragraphs)
            if paragraphs:
                sections.append(models.FullReportSection(section=block["section"], paragraphs=paragraphs))
        return sections

    def build_thematic_sections(
        self,
        snapshot: models.ChartSnapshot,
        internal_model: models.InternalModelSnapshot,
        plan: Sequence[dict],
        theme: str,
        overrides: dict[str, bool] | None = None,
        text_overrides: dict[tuple[str, str], str] | None = None,
        user_id: int | None = None,
        locale: str | None = None,
    ) -> List[models.FullReportSection]:
        """Build sections for a thematic report using a custom plan."""
        context = self._build_context(internal_model, user_id, report_type="thematic", locale=locale)
        sections: List[models.FullReportSection] = []
        for block in plan:
            paragraphs: List[models.Interpretation] = []
            source_section = block["source_section"]
            for sub_spec in block.get("sub_blocks", []):
                block_paragraphs = self._build_block(
                    source_section=source_section,
                    display_section=block["section"],
                    sub_block=sub_spec["name"],
                    limit=sub_spec.get("limit", 1),
                    context=context,
                    overrides=overrides,
                    text_overrides=text_overrides,
                    rule_prefix=f"thematic::{theme}::{source_section}::{sub_spec['name']}",
                    locale=locale,
                )
                if block_paragraphs:
                    paragraphs.extend(block_paragraphs)
            if paragraphs:
                sections.append(models.FullReportSection(section=block["section"], paragraphs=paragraphs))
        return sections

    def _build_block(
        self,
        source_section: str,
        display_section: str,
        sub_block: str,
        limit: int,
        context: NarrativeContext,
        overrides: dict[str, bool] | None,
        text_overrides: dict[tuple[str, str], str] | None,
        rule_prefix: str,
        locale: str | None = None,
    ) -> List[models.Interpretation]:
        selected: List[models.Interpretation] = []
        for idx in range(limit):
            block = self._select_meaning_bundle(
                source_section=source_section,
                display_section=display_section,
                sub_block=sub_block,
                layer_sequence=FULL_LAYER_SEQUENCE,
                context=context,
                overrides=overrides,
                text_overrides=text_overrides,
                rule_id=f"{rule_prefix}::{idx}",
                locale=locale,
            )
            if not block:
                break
            selected.extend(block)
        return selected

    def _build_context(
        self,
        internal_model: models.InternalModelSnapshot,
        user_id: int | None,
        report_type: str,
        locale: str | None = None,
    ) -> NarrativeContext:
        ordered_axes = sorted(internal_model.axes, key=lambda ax: abs(ax.value), reverse=True)
        axis_order = [axis.axis_id for axis in ordered_axes]
        axis_priority = {axis.axis_id: len(ordered_axes) - idx for idx, axis in enumerate(ordered_axes)}
        axis_values = {axis.axis_id: axis.value for axis in internal_model.axes}
        dominant_axes = set(axis_order[:3])
        active_modulators = {mod.modulator_id for mod in internal_model.modulators if mod.value >= 55}
        seed = self._compute_seed(user_id, report_type)
        return NarrativeContext(
            axis_priority=axis_priority,
            axis_values=axis_values,
            dominant_axes=dominant_axes,
            active_modulators=active_modulators,
            seed=seed,
            report_type=report_type,
            locale=locale or "en",
        )

    def _compute_seed(self, user_id: int | None, report_type: str) -> int:
        identity = user_id if user_id is not None else "anon"
        digest = hashlib.sha256(f"{identity}:{report_type}".encode("utf-8")).hexdigest()
        return int(digest[:12], 16)

    def _select_meaning_bundle(
        self,
        source_section: str,
        display_section: str,
        sub_block: str,
        layer_sequence: Sequence[str],
        context: NarrativeContext,
        overrides: dict[str, bool] | None,
        text_overrides: dict[tuple[str, str], str] | None,
        rule_id: str,
        locale: str | None = None,
    ) -> List[models.Interpretation] | None:
        meaning_map = self.meaning_templates.get(source_section, {}).get(sub_block, {})
        if not meaning_map:
            return None

        allow_lite_only = context.report_type == "lite"

        best_meaning: str | None = None
        best_score = float("-inf")
        best_hash = float("-inf")
        best_templates: Dict[str, templates.ParagraphTemplate | None] = {}

        for meaning_type, layer_map in meaning_map.items():
            if meaning_type in context.used_meanings[display_section]:
                continue
            observation_candidates = self._filter_templates(
                layer_map.get(LAYER_OBSERVATION, []), overrides, allow_lite_only
            )
            if not observation_candidates:
                continue
            observation_template = self._best_template(observation_candidates, sub_block, context)
            if not observation_template:
                continue
            layer_templates: Dict[str, templates.ParagraphTemplate | None] = {
                LAYER_OBSERVATION: observation_template
            }
            for layer in layer_sequence:
                if layer == LAYER_OBSERVATION:
                    continue
                candidates = self._filter_templates(layer_map.get(layer, []), overrides, allow_lite_only)
                layer_templates[layer] = self._best_template(candidates, sub_block, context) if candidates else None

            score = self._score_template(observation_template, sub_block, context)
            if meaning_type in context.global_meanings:
                score -= 5
            tie_breaker = self._stable_hash(context.seed, f"{sub_block}:{meaning_type}")
            if score > best_score or (score == best_score and tie_breaker > best_hash):
                best_meaning = meaning_type
                best_score = score
                best_hash = tie_breaker
                best_templates = layer_templates

        if best_meaning is None:
            return None

        observation_template = best_templates.get(LAYER_OBSERVATION)
        if observation_template:
            for axis in observation_template.primary_axes:
                context.axis_memory[axis] = context.axis_memory.get(axis, 0) + 1

        context.used_meanings[display_section].add(best_meaning)
        context.global_meanings.add(best_meaning)

        interpretations: List[models.Interpretation] = []
        for layer in layer_sequence:
            template = best_templates.get(layer)
            layer_rule_id = f"{rule_id}::{layer}"
            if template:
                interpretation = self._render_interpretation(
                    template=template,
                    display_section=display_section,
                    context=context,
                    text_overrides=text_overrides,
                    rule_id=layer_rule_id,
                    locale=locale or context.locale,
                )
            else:
                interpretation = self._synthesize_layer_interpretation(
                    meaning_type=best_meaning,
                    display_section=display_section,
                    layer=layer,
                    context=context,
                    rule_id=layer_rule_id,
                )
            if interpretation:
                interpretations.append(interpretation)

        return interpretations

    def _filter_templates(
        self,
        candidates: List[templates.ParagraphTemplate],
        overrides: dict[str, bool] | None,
        allow_lite_only: bool,
    ) -> List[templates.ParagraphTemplate]:
        filtered: List[templates.ParagraphTemplate] = []
        for tpl in candidates:
            if allow_lite_only and not tpl.lite_allowed:
                continue
            if overrides is not None and not overrides.get(tpl.paragraph_id, True):
                continue
            if not tpl.variants:
                continue
            filtered.append(tpl)
        return filtered

    def _best_template(
        self,
        candidates: List[templates.ParagraphTemplate],
        sub_block: str,
        context: NarrativeContext,
    ) -> templates.ParagraphTemplate | None:
        best = None
        best_score = float("-inf")
        for tpl in candidates:
            score = self._score_template(tpl, sub_block, context)
            if score > best_score:
                best = tpl
                best_score = score
        return best

    def _synthesize_layer_interpretation(
        self,
        meaning_type: str,
        display_section: str,
        layer: str,
        context: NarrativeContext,
        rule_id: str,
    ) -> models.Interpretation | None:
        templates_list = SYNTHETIC_LAYER_TEXT.get(layer)
        if not templates_list:
            return None
        digest = hashlib.sha256(f"{context.seed}:{display_section}:{meaning_type}:{layer}".encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % len(templates_list)
        text_template = templates_list[idx]
        text = text_template.format(meaning=meaning_type.lower())
        paragraph_id = f"SYNTH-{layer.upper()}-{abs(int(digest[:10], 16)) % 100000}"
        trace = models.SelectionTrace(
            paragraph_id=paragraph_id,
            meaning_type=meaning_type,
            axes_hit=[],
            modulators_hit=[],
            confidence_level="medium",
            rule_ids=[rule_id],
        )
        return models.Interpretation(
            paragraph_id=paragraph_id,
            variant_id="v1",
            text=text,
            section=display_section,
            meaning_type=meaning_type,
            selection_trace=trace,
        )

    def _build_lite_hook(self, section: str, context: NarrativeContext) -> models.Interpretation | None:
        if not LITE_HOOK_MESSAGES:
            return None
        digest = hashlib.sha256(f"{context.seed}:{section}:hook".encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % len(LITE_HOOK_MESSAGES)
        text = LITE_HOOK_MESSAGES[idx].format(section=section)
        paragraph_id = f"LITE-HOOK-{section.replace(' ', '-').upper()}"
        trace = models.SelectionTrace(
            paragraph_id=paragraph_id,
            meaning_type=f"{section} Hook",
            axes_hit=[],
            modulators_hit=[],
            confidence_level="medium",
            rule_ids=[f"lite::{section}::hook"],
        )
        return models.Interpretation(
            paragraph_id=paragraph_id,
            variant_id="v1",
            text=text,
            section=section,
            meaning_type=f"{section} Hook",
            selection_trace=trace,
        )

    def _score_template(
        self,
        template: templates.ParagraphTemplate,
        sub_block: str,
        context: NarrativeContext,
    ) -> float:
        score = 0.0
        for axis in template.primary_axes:
            score += context.axis_priority.get(axis, 0) * 10
            score += context.axis_memory.get(axis, 0) * 2
        for axis in template.secondary_axes:
            score += context.axis_priority.get(axis, 0) * 3
        score += len(set(template.modulators) & context.active_modulators) * 6
        score += self._arc_weight(sub_block)
        if set(template.primary_axes) & context.dominant_axes:
            score += 5
        return score

    def _stable_hash(self, seed: int, paragraph_id: str) -> float:
        digest = hashlib.sha256(f"{seed}:{paragraph_id}".encode("utf-8")).hexdigest()
        return float(int(digest[:12], 16))

    def _arc_weight(self, sub_block: str) -> float:
        lowered = sub_block.lower()
        for keyword, weight in ARC_STAGES.items():
            if keyword in lowered:
                return float(weight)
        return 5.0

    def _build_executive_summary(
        self,
        snapshot: models.ChartSnapshot,
        internal_model: models.InternalModelSnapshot,
    ) -> List[models.Interpretation]:
        axes_summary = ", ".join(f"{axis.axis_id}:{axis.value:+.0f}" for axis in internal_model.axes[:3])
        paragraph_texts = [
            f"Your chart blends {snapshot.sun} Sun expression with {snapshot.moon} Moon sensitivity and {snapshot.rising} Rising presence. The combination sets the tone for how you move through life before any layers are added.",
            f"Across the internal model we see emphasis on {axes_summary}. These axes color how you make sense of relationships, work, and long-term choices.",
        ]
        traces = [
            models.SelectionTrace(
                paragraph_id="EXEC-1",
                meaning_type="Executive Summary Intro",
                axes_hit=[internal_model.axes[0].axis_id] if internal_model.axes else [],
                modulators_hit=[],
                confidence_level="medium",
                rule_ids=["full::executive_summary"],
            ),
            models.SelectionTrace(
                paragraph_id="EXEC-2",
                meaning_type="Executive Summary Axes",
                axes_hit=[ax.axis_id for ax in internal_model.axes[:3]],
                modulators_hit=[],
                confidence_level="medium",
                rule_ids=["full::executive_summary"],
            ),
        ]
        return [
            models.Interpretation(
                paragraph_id=f"EXEC-{idx}",
                variant_id="v1",
                text=text,
                section="Executive Summary",
                meaning_type=trace.meaning_type,
                selection_trace=trace,
            )
            for idx, (text, trace) in enumerate(zip(paragraph_texts, traces), start=1)
        ]

    def _build_integration_paragraphs(self) -> List[models.Interpretation]:
        text = (
            "The threads across emotional patterns, relationships, and work point to integration through deliberate pacing. "
            "Notice where recurring dynamics appear in multiple sections—those parallels highlight the next phase of growth."
        )
        trace = models.SelectionTrace(
            paragraph_id="INTEGRATION-001",
            meaning_type="Integration Summary",
            axes_hit=[],
            modulators_hit=[],
            confidence_level="medium",
            rule_ids=["full::integration"],
        )
        return [
            models.Interpretation(
                paragraph_id="INTEGRATION-001",
                variant_id="v1",
                text=text,
                section="Practical Integration",
                meaning_type=trace.meaning_type,
                selection_trace=trace,
            )
        ]

    def _render_interpretation(
        self,
        template: templates.ParagraphTemplate,
        display_section: str,
        context: NarrativeContext,
        text_overrides: dict[tuple[str, str], str] | None,
        rule_id: str,
        locale: str = "en",
    ) -> models.Interpretation | None:
        variant = self._choose_variant(template, context.seed)
        if not variant:
            return None
        
        # Check for override first
        override_text = None
        if text_overrides:
            override_text = text_overrides.get((template.paragraph_id, variant.variant_id))
        
        # Get text from i18n layer using key: paragraph_id.variant_id
        if not override_text:
            i18n_key = f"{template.paragraph_id}.{variant.variant_id}"
            override_text = translate(i18n_key, locale=locale)
        
        axes_hit = list(template.primary_axes)
        modulators_hit = list(set(template.modulators) & context.active_modulators)
        trace = models.SelectionTrace(
            paragraph_id=template.paragraph_id,
            meaning_type=template.meaning_type,
            axes_hit=axes_hit,
            modulators_hit=modulators_hit,
            confidence_level=template.confidence_level,
            rule_ids=[rule_id],
        )
        return models.Interpretation(
            paragraph_id=template.paragraph_id,
            variant_id=variant.variant_id,
            text=override_text,
            section=display_section,
            meaning_type=template.meaning_type,
            selection_trace=trace,
        )

    def _choose_variant(
        self,
        template: templates.ParagraphTemplate,
        base_seed: int,
    ) -> templates.TextVariant | None:
        if not template.variants:
            return None
        digest = hashlib.sha256(f"{base_seed}:{template.paragraph_id}".encode("utf-8")).hexdigest()
        idx = int(digest[:8], 16) % len(template.variants)
        return template.variants[idx]

    def _load_facets(self) -> Dict[str, List[dict]]:
        facets = astrology_ref.ep_facets()
        mapping: Dict[str, List[dict]] = {}
        for record in facets:
            mapping[record["pattern_id"]] = record.get("facets", [])
        return mapping

    def _load_bridges(self) -> List[dict]:
        return astrology_ref.cross_domain_bridges()

    def _build_bridge(self, context: NarrativeContext, paragraph_id: str) -> models.Interpretation | None:
        digest = hashlib.sha256(f"{context.seed}:{paragraph_id}:bridge".encode("utf-8")).hexdigest()
        dominant_axis = max(context.axis_priority.items(), key=lambda item: item[1])[0] if context.axis_priority else None
        for bridge in self.bridges:
            if dominant_axis and dominant_axis in bridge.get("trigger_axes", []):
                return self._render_bridge(bridge)
        if self.bridges:
            return self._render_bridge(self.bridges[int(digest[:8], 16) % len(self.bridges)])
        return None

    def _render_bridge(self, bridge_meta: dict) -> models.Interpretation:
        trace = models.SelectionTrace(
            paragraph_id=f"BRIDGE-{bridge_meta['id']}",
            meaning_type="Cross-domain Bridge",
            axes_hit=bridge_meta.get("trigger_axes", []),
            modulators_hit=[],
            confidence_level="medium",
            rule_ids=[f"bridge::{bridge_meta['id']}"],
        )
        text = translate(f"cross_domain.{bridge_meta['id']}.tease", default=bridge_meta.get("tease", ""))
        return models.Interpretation(
            paragraph_id=trace.paragraph_id,
            variant_id="v1",
            text=text,
            section="Cross-Domain",
            meaning_type="Bridge",
            selection_trace=trace,
        )

    def _pick_facet(self, context: NarrativeContext, paragraph_id: str) -> models.Interpretation | None:
        pattern_id = paragraph_id.split(":", 1)[0]
        facets = self.facets.get(pattern_id)
        if not facets:
            return None
        digest = hashlib.sha256(f"{context.seed}:{paragraph_id}:facet".encode("utf-8")).hexdigest()
        facet_meta = facets[int(digest[:8], 16) % len(facets)]
        text = facet_meta["tease"]
        trace = models.SelectionTrace(
            paragraph_id=f"{pattern_id}-FACET-{facet_meta['id']}",
            meaning_type="Facet Tease",
            axes_hit=[],
            modulators_hit=[],
            confidence_level="medium",
            rule_ids=[f"facet::{pattern_id}::{facet_meta['id']}"],
        )
        meaning = models.Interpretation(
            paragraph_id=trace.paragraph_id,
            variant_id="facet",
            text=text,
            section="Emotional Patterns",
            meaning_type="Facet",
            selection_trace=trace,
        )
        return meaning
