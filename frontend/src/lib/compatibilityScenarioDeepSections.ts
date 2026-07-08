/** Theme-scoped deep journal: 4 blocks aligned with scenario skin, not generic 5-pack. */

import type { ExplorationDeepSection } from "@/lib/buildCompatibilityExplorationModel";
import type { ScenarioSkin, SubscoreKey } from "@/lib/compatibilityScenarioSkins";

type AnalysisBlock = {
  key: string;
  title: string;
  subtitle?: string;
  takeaway: string;
  detail?: string;
  risk?: string;
  action?: string;
};

type PairDimension = {
  key: string;
  label: string;
  score: number;
  summary?: string;
  indicators?: string[];
};

/** Which deep_dive dimension keys feed each scenario subscore slot (pair compare). */
const PAIR_DEEP_SOURCE: Record<SubscoreKey, string[]> = {
  attraction: ["attraction", "long_term"],
  stability: ["stability", "emotional"],
  conflicts: ["communication", "emotional"],
  sexuality: ["attraction", "long_term"],
};

export function buildScenarioDeepSectionsFromBlocks(
  skin: ScenarioSkin,
  blocks: AnalysisBlock[],
): ExplorationDeepSection[] {
  const byKey = new Map(blocks.map((b) => [b.key.toLowerCase(), b]));

  return skin.dimensionLabels.flatMap((slot) => {
    const block = byKey.get(slot.key);
    if (!block?.takeaway?.trim()) return [];
    return [
      {
        id: slot.key,
        title: slot.label,
        subtitle: block.subtitle,
        takeaway: block.takeaway,
        detail: block.detail,
        risk: block.risk,
        action: block.action,
      },
    ];
  });
}

const ATTACHMENT_BLOCK_TO_SLOT: Partial<Record<string, SubscoreKey>> = {
  emotions: "stability",
  communication: "conflicts",
  conflicts: "conflicts",
  sexuality: "sexuality",
  long_term: "attraction",
};

function dimensionSlotOrderFromDeepBlocks(
  skin: ScenarioSkin,
  deepBlockOrder?: string[],
): SubscoreKey[] | undefined {
  if (!deepBlockOrder?.length) return undefined;
  const slots: SubscoreKey[] = [];
  for (const block of deepBlockOrder) {
    const slot = ATTACHMENT_BLOCK_TO_SLOT[block.toLowerCase()];
    if (slot && !slots.includes(slot)) slots.push(slot);
  }
  for (const label of skin.dimensionLabels) {
    if (!slots.includes(label.key)) slots.push(label.key);
  }
  return slots;
}

export function buildScenarioDeepSectionsFromPairDeep(
  skin: ScenarioSkin,
  deep?: { dimensions?: PairDimension[] } | null,
  aspects?: Array<{ type: string; description: string; score: number }>,
  deepBlockOrder?: string[],
): ExplorationDeepSection[] {
  const dims = deep?.dimensions ?? [];
  const dimByKey = new Map(dims.map((d) => [d.key.toLowerCase(), d]));
  const slotOrder = dimensionSlotOrderFromDeepBlocks(skin, deepBlockOrder);
  const labels = slotOrder
    ? slotOrder.map((key) => skin.dimensionLabels.find((d) => d.key === key)).filter(Boolean)
    : skin.dimensionLabels;

  return labels.flatMap((slot) => {
    if (!slot) return [];
    const sources = PAIR_DEEP_SOURCE[slot.key];
    const matched = sources.map((k) => dimByKey.get(k)).find(Boolean);
    const fallback = dims[skin.dimensionLabels.indexOf(slot)] ?? dims[0];
    const aspect = aspects?.find((a) => a.type.toLowerCase().includes(slot.key));
    const takeaway = (matched ?? fallback)?.summary?.trim() || aspect?.description?.trim() || "";
    if (!takeaway) return [];
    const detail = (matched ?? fallback)?.indicators?.filter(Boolean).join(" · ");
    return [
      {
        id: slot.key,
        title: slot.label,
        takeaway,
        detail: detail || undefined,
      },
    ];
  });
}
