import type { DsCalloutLabel } from "@/design-system";
import { mapSphereToDomain } from "@/lib/todayDomainSignal";

/**
 * Reading chapter id → life-theme capsule for DsCallout (FOUNDATION_UI §5.1).
 * Tone stays independent — this only maps the label axis.
 */
export function calloutLabelForChapterId(chapterId: string): DsCalloutLabel {
  if (!chapterId.startsWith("sphere-")) return "help";
  const domain = mapSphereToDomain(chapterId.slice("sphere-".length));
  if (domain === "relationships") return "relations";
  if (domain === "money") return "money";
  if (domain === "energy") return "emotions";
  // work — closest catalog label
  return "thought";
}
