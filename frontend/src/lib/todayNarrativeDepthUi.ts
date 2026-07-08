import type { InsightDepthTier } from "@/lib/types";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export type NarrativeDepthLevel = "quick" | "normal" | "deep";

export function effectiveNarrativeDepth(
  raw: string | null | undefined,
  insightTier: InsightDepthTier,
): NarrativeDepthLevel {
  const r = String(raw ?? "normal").toLowerCase().trim();
  if (r !== "quick" && r !== "normal" && r !== "deep") return "normal";
  if (r === "deep" && insightTier === "free") return "normal";
  return r as NarrativeDepthLevel;
}

export function narrativeDepthLabelRu(level: NarrativeDepthLevel): string {
  switch (level) {
    case "quick":
      return RITUAL_COPY.narrativeDepthOptionQuick;
    case "normal":
      return RITUAL_COPY.narrativeDepthOptionNormal;
    case "deep":
      return RITUAL_COPY.narrativeDepthOptionDeep;
  }
}
