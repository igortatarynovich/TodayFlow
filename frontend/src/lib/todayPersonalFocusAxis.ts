/**
 * T3.focus_title — overlay closed-set axis → map_label only.
 * Canon: TODAY_DISPLAY_INVENTORY_V1 T3.focus_title. Omit if no F10 axis.
 * Not kitchen / scene sphere / K01 human_line / K06 headline.
 */

import type { TodayContractDomainId, TodayContractV1 } from "@/lib/todayContract";
import { TODAY_CONTRACT_DOMAIN_LABEL_RU } from "@/lib/todayContract";

function asClosedDomain(raw: unknown): TodayContractDomainId | null {
  const key = String(raw ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
  if (key === "work" || key === "money" || key === "relationships" || key === "energy") {
    return key;
  }
  return null;
}

function overlayFocusAxis(contract: TodayContractV1): unknown {
  const overlay = contract.personal_day?.natal_overlay;
  if (!overlay || typeof overlay !== "object" || Array.isArray(overlay)) return null;
  return (overlay as Record<string, unknown>).focus_axis;
}

function clipAxisLabel(label: string): string | null {
  const words = label.replace(/\s+/g, " ").trim().split(" ").filter(Boolean);
  if (!words.length) return null;
  const clipped = words.slice(0, 4).join(" ");
  return clipped.length > 72 ? clipped.slice(0, 72).trim() : clipped;
}

/**
 * Project Natal Overlay's already-chosen closed domain to a 1–4 word label.
 * Does not score spheres, invent a title, or copy K01/K06 prose.
 */
export function pickPersonalFocusAxisLabel(
  contract: TodayContractV1 | null | undefined,
): string | null {
  if (!contract) return null;
  const id = asClosedDomain(overlayFocusAxis(contract));
  if (!id) return null;
  return clipAxisLabel(TODAY_CONTRACT_DOMAIN_LABEL_RU[id]);
}
