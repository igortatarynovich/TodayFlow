/**
 * Profile journey Steps 1–5 for UI — maps CoreProfile read-path projections.
 * SoT: docs/PRODUCT_BLOCK_SIX_QUESTIONS.md · PROFILE_PRODUCT_JOURNEY_FORMS_V1.md
 *
 * Primary presentation contract. Matrix slots feed progressiveDetails (Explore),
 * not the Journey scroll order.
 */
import type { CoreProfile } from "@/lib/types";
import {
  buildProfileProgressiveDetailsProjection,
  type ProgressiveDetailItem,
  PROFILE_SLOT_HELPS,
  PROFILE_SLOT_STRENGTHS,
  PROFILE_SLOT_TENSIONS,
} from "@/lib/profilePage/buildProfileProgressiveDetailsProjection";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";
import { elementRuName, zodiacRuName } from "@/lib/zodiacKnowledge";

export type ProfileJourneyWhyRow = {
  id: string;
  class: "selected_by" | "portrait_influenced_by" | string;
  label: string;
};

export type ProfileJourneyNode = {
  id: string;
  kind: string;
  title: string;
  insight: string;
  groundedOn: Array<{ id?: string; label: string }>;
  help: string | null;
  /** Adjacent living context — not proof of this pattern (v0). */
  livingEvidence: string[];
  sourceFields: string[];
};

export type ProfileJourneyRecognition = {
  name: string | null;
  line: string | null;
  archetypeSeed: string | null;
  /** Full identity_core — longer than recognition_line when present. */
  identityCore: string | null;
};

export type ProfileJourneyWhy = {
  title: string | null;
  selectedBy: ProfileJourneyWhyRow[];
  influencedBy: ProfileJourneyWhyRow[];
  honesty: string | null;
};

export type ProfileJourneyBridge = {
  line: string | null;
  leadsTo: string | null;
};

export type ProfileJourneyProjection = {
  hasJourneySurface: boolean;
  recognition: ProfileJourneyRecognition;
  /** Max 3 real markers: sign · element · life path. Never a joined dump string. */
  identityMarkers: string[];
  why: ProfileJourneyWhy | null;
  insightNode: ProfileJourneyNode | null;
  effortVector: string | null;
  bridge: ProfileJourneyBridge | null;
  progressiveDetails: ProgressiveDetailItem[];
};

type WhyRowIn = {
  id?: string;
  class?: string;
  label?: string;
};

function titleCaseRu(value: string): string {
  const t = value.trim();
  if (!t) return "";
  return t.charAt(0).toUpperCase() + t.slice(1);
}

function mapWhyRows(rows: WhyRowIn[] | undefined | null): ProfileJourneyWhyRow[] {
  if (!Array.isArray(rows)) return [];
  return rows
    .map((row) => {
      const label = String(row?.label || "").trim();
      if (!label) return null;
      return {
        id: String(row?.id || label),
        class: String(row?.class || ""),
        label,
      };
    })
    .filter((row): row is ProfileJourneyWhyRow => Boolean(row));
}

function buildIdentityMarkers(
  core: CoreProfile | null | undefined,
  recognitionName: string | null,
  recognitionLine: string | null,
): string[] {
  const markers: string[] = [];
  const sun = core?.astro?.sun_sign?.trim();
  if (sun) {
    const name = titleCaseRu(zodiacRuName(sun) || sun);
    if (name) markers.push(name);
  }
  const elementRaw = core?.astro?.sun_element?.trim();
  if (elementRaw) {
    const el = titleCaseRu(elementRuName(elementRaw) || elementRaw);
    if (el) markers.push(el);
  }
  const lifePath = core?.numerology?.life_path;
  if (lifePath != null) {
    markers.push(`Путь ${lifePath}`);
  }

  const banned = new Set(
    [recognitionName, recognitionLine]
      .filter(Boolean)
      .map((s) => String(s).trim().toLowerCase()),
  );

  const out: string[] = [];
  for (const m of markers) {
    const key = m.trim().toLowerCase();
    if (!key) continue;
    if (banned.has(key)) continue;
    if (out.some((x) => x.toLowerCase() === key)) continue;
    out.push(m);
    if (out.length >= 3) break;
  }
  return out;
}

function omitSlotsForInsight(node: ProfileJourneyNode | null): string[] {
  if (!node) return [];
  const omit: string[] = [];
  const fields = new Set(node.sourceFields.map((f) => f.toLowerCase()));
  // When the node already narrates these materials, keep them out of Explore lists.
  if (
    node.kind === "tension" ||
    node.kind === "repeat" ||
    fields.has("growth_zones") ||
    fields.has("recurring_patterns") ||
    fields.has("internal_tensions")
  ) {
    omit.push(PROFILE_SLOT_TENSIONS);
  }
  if (node.kind === "strength" || fields.has("strengths")) {
    omit.push(PROFILE_SLOT_STRENGTHS);
  }
  if (node.help || fields.has("helps")) {
    omit.push(PROFILE_SLOT_HELPS);
  }
  return omit;
}

export function buildProfileJourneyProjection(
  core: CoreProfile | null | undefined,
): ProfileJourneyProjection {
  const contract = core?.profile_contract_v1;
  const seed = core?.baseline?.archetype_seed?.trim() || null;
  const recognitionName = seed ? archetypeDisplayLabel(seed, "ru") : null;
  const recognitionLine = contract?.recognition_line?.trim() || null;
  const identityCore = contract?.identity_core?.trim() || null;

  const whyRaw = core?.portrait_why_v0 ?? null;
  const whySelectedBy = mapWhyRows(whyRaw?.selected_by);
  const whyInfluencedBy = mapWhyRows(whyRaw?.portrait_influenced_by);
  const whyTitle = whyRaw?.title?.trim() || null;
  const whyHonesty = whyRaw?.honesty_line?.trim() || null;
  const why: ProfileJourneyWhy | null =
    whySelectedBy.length || whyInfluencedBy.length || whyTitle || whyHonesty
      ? {
          title: whyTitle,
          selectedBy: whySelectedBy,
          influencedBy: whyInfluencedBy,
          honesty: whyHonesty,
        }
      : null;

  const rawNode = core?.insight_nodes_v0?.nodes?.[0];
  let insightNode: ProfileJourneyNode | null = null;
  if (rawNode?.insight?.trim() && rawNode.title?.trim()) {
    insightNode = {
      id: String(rawNode.id || "node_0"),
      kind: String(rawNode.kind || "tension"),
      title: rawNode.title.trim(),
      insight: rawNode.insight.trim(),
      groundedOn: (rawNode.grounded_on ?? [])
        .map((g) => ({
          id: g?.id,
          label: String(g?.label || "").trim(),
        }))
        .filter((g) => g.label),
      help: rawNode.help?.trim() || null,
      livingEvidence: (rawNode.living_evidence ?? [])
        .map((q) => String(q || "").trim())
        .filter(Boolean),
      sourceFields: (rawNode.source_fields ?? [])
        .map((f) => String(f || "").trim())
        .filter(Boolean),
    };
  }

  const effortVector = core?.effort_vector_v0?.effort_vector?.trim() || null;
  const bridgeLine = core?.bridge_line_v0?.bridge_line?.trim() || null;
  const bridgeLeadsTo = core?.bridge_line_v0?.leads_to?.trim() || null;
  const bridge: ProfileJourneyBridge | null =
    bridgeLine || bridgeLeadsTo
      ? { line: bridgeLine, leadsTo: bridgeLeadsTo }
      : null;

  const identityMarkers = buildIdentityMarkers(core, recognitionName, recognitionLine);

  const progressive = buildProfileProgressiveDetailsProjection(core, {
    omitSlotIds: omitSlotsForInsight(insightNode),
  });

  const hasJourneySurface = Boolean(
    (recognitionName && recognitionLine) ||
      why ||
      insightNode ||
      effortVector ||
      bridgeLine,
  );

  return {
    hasJourneySurface,
    recognition: {
      name: recognitionName,
      line: recognitionLine,
      archetypeSeed: seed,
      identityCore,
    },
    identityMarkers,
    why,
    insightNode,
    effortVector,
    bridge,
    progressiveDetails: progressive.items,
  };
}
