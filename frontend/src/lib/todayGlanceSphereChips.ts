/**
 * Glance Screen 0 — ≤2 domain chips from Reading highlight set.
 * Canon: docs/today/TODAY_SCREEN_SCENARIO_V3.md Экран 0 §4.
 * Same magnitude ranking as Reading chapters / Response trap pick.
 */

import {
  TODAY_CONTRACT_DOMAIN_LABEL_RU,
  type TodayContractDomainId,
  type TodayContractV1,
} from "@/lib/todayContract";
import { mapSphereToDomain, sceneMagnitudeScore } from "@/lib/todayDomainSignal";
import { readyDayScenario } from "@/lib/todayDaySpine";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";

export type GlanceSphereChip = {
  domain: TodayContractDomainId;
  label: string;
};

const CHIP_CAP = 2;

/** Up to 2 Reading domains by magnitude; empty → honest shared copy. */
export function pickGlanceSphereChips(
  contract: TodayContractV1 | null | undefined,
): GlanceSphereChip[] {
  const sc = contract ? readyDayScenario(contract) : null;
  const scenes = (sc?.scenes ?? []).filter((s) => s && typeof s === "object");
  if (!scenes.length) return [];

  const ranked = [...scenes].sort(
    (a, b) =>
      sceneMagnitudeScore({
        sphere: a.sphere,
        role_in_story: a.role_in_story,
        trap: a.trap,
        opportunity: a.opportunity,
        what_happens: a.what_happens,
      }) -
      sceneMagnitudeScore({
        sphere: b.sphere,
        role_in_story: b.role_in_story,
        trap: b.trap,
        opportunity: b.opportunity,
        what_happens: b.what_happens,
      }),
  );
  ranked.reverse();

  const chips: GlanceSphereChip[] = [];
  const seen = new Set<string>();
  for (const scene of ranked) {
    if (chips.length >= CHIP_CAP) break;
    const domain = mapSphereToDomain(scene.sphere) as TodayContractDomainId;
    if (seen.has(domain)) continue;
    seen.add(domain);
    chips.push({
      domain,
      label: TODAY_CONTRACT_DOMAIN_LABEL_RU[domain] || domain,
    });
  }
  return chips;
}

export function glanceSphereChipsHonestEmpty(
  chips: GlanceSphereChip[],
): string | null {
  return chips.length ? null : TODAY_NO_SHARP_FOCUS_COPY;
}
