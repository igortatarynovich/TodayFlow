/**
 * T3.focus_title — overlay closed-set axis → map_label only.
 * Canon: TODAY_DISPLAY_INVENTORY_V1 T3.focus_title. Omit if no axis. No LLM title.
 */

import type { TodayContractDomainId, TodayContractV1 } from "@/lib/todayContract";
import { TODAY_CONTRACT_DOMAIN_LABEL_RU } from "@/lib/todayContract";

const DOMAIN_ALIAS: Record<string, TodayContractDomainId> = {
  work: "work",
  career: "work",
  money: "money",
  relationships: "relationships",
  family: "relationships",
  energy: "energy",
  body: "energy",
};

function asClosedDomain(raw: unknown): TodayContractDomainId | null {
  const key = String(raw ?? "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
  return DOMAIN_ALIAS[key] ?? null;
}

function overlayRecord(contract: TodayContractV1): Record<string, unknown> | null {
  const overlay = contract.personal_day?.natal_overlay;
  if (overlay && typeof overlay === "object" && !Array.isArray(overlay)) {
    return overlay as Record<string, unknown>;
  }
  return null;
}

function clipAxisLabel(label: string): string | null {
  const words = label.replace(/\s+/g, " ").trim().split(" ").filter(Boolean);
  if (!words.length) return null;
  const clipped = words.slice(0, 4).join(" ");
  return clipped.length > 72 ? clipped.slice(0, 72).trim() : clipped;
}

/**
 * Project Natal Overlay's already-chosen closed domain to a 1–4 word label.
 * Does not score spheres or invent a title.
 */
export function pickPersonalFocusAxisLabel(
  contract: TodayContractV1 | null | undefined,
): string | null {
  if (!contract) return null;
  const overlay = overlayRecord(contract);
  if (overlay) {
    for (const key of ["focus_axis", "axis", "domain", "sphere", "primary_sphere"] as const) {
      const id = asClosedDomain(overlay[key]);
      if (id) return clipAxisLabel(TODAY_CONTRACT_DOMAIN_LABEL_RU[id]);
    }
  }
  const scenario = contract.day_story?.day_scenario;
  const pid = String(scenario?.primary_scene_id ?? "").trim();
  const primary = pid
    ? scenario?.scenes?.find((s) => String(s.scene_id ?? "").trim() === pid)
    : undefined;
  const sphereId = asClosedDomain(primary?.sphere);
  if (sphereId) return clipAxisLabel(TODAY_CONTRACT_DOMAIN_LABEL_RU[sphereId]);
  return null;
}
