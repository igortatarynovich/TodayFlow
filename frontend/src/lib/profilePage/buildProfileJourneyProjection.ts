/**
 * Profile journey Steps 1–5 for UI — maps CoreProfile read-path projections.
 * SoT: docs/PRODUCT_BLOCK_SIX_QUESTIONS.md · PROFILE_PRODUCT_JOURNEY_FORMS_V1.md
 */
import type { CoreProfile } from "@/lib/types";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";

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
};

export type ProfileJourneyProjection = {
  recognitionName: string | null;
  recognitionLine: string | null;
  archetypeSeed: string | null;
  whyTitle: string | null;
  whySelectedBy: ProfileJourneyWhyRow[];
  whyInfluencedBy: ProfileJourneyWhyRow[];
  whyHonesty: string | null;
  node: ProfileJourneyNode | null;
  effortVector: string | null;
  bridgeLine: string | null;
  bridgeLeadsTo: string | null;
  /** True when enough journey surface exists to prefer journey UI over card wall. */
  hasJourneySurface: boolean;
};

type WhyRowIn = {
  id?: string;
  class?: string;
  label?: string;
};

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

export function buildProfileJourneyProjection(
  core: CoreProfile | null | undefined,
): ProfileJourneyProjection {
  const contract = core?.profile_contract_v1;
  const seed = core?.baseline?.archetype_seed?.trim() || null;
  const recognitionName = seed ? archetypeDisplayLabel(seed, "ru") : null;
  const recognitionLine = contract?.recognition_line?.trim() || null;

  const why = core?.portrait_why_v0 ?? null;
  const whySelectedBy = mapWhyRows(why?.selected_by);
  const whyInfluencedBy = mapWhyRows(why?.portrait_influenced_by);
  const whyTitle = why?.title?.trim() || null;
  const whyHonesty = why?.honesty_line?.trim() || null;

  const rawNode = core?.insight_nodes_v0?.nodes?.[0];
  let node: ProfileJourneyNode | null = null;
  if (rawNode?.insight?.trim() && rawNode.title?.trim()) {
    node = {
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
    };
  }

  const effortVector = core?.effort_vector_v0?.effort_vector?.trim() || null;
  const bridgeLine = core?.bridge_line_v0?.bridge_line?.trim() || null;
  const bridgeLeadsTo = core?.bridge_line_v0?.leads_to?.trim() || null;

  const hasJourneySurface = Boolean(
    (recognitionName && recognitionLine) ||
      whySelectedBy.length ||
      node ||
      effortVector ||
      bridgeLine,
  );

  return {
    recognitionName,
    recognitionLine,
    archetypeSeed: seed,
    whyTitle,
    whySelectedBy,
    whyInfluencedBy,
    whyHonesty,
    node,
    effortVector,
    bridgeLine,
    bridgeLeadsTo,
    hasJourneySurface,
  };
}
