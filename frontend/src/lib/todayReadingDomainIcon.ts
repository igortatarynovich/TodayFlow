import { TODAY_DOMAIN_ICON_MAP } from "@/design-system/icons/DsIcons";
import { mapSphereToDomain } from "@/lib/todayDomainSignal";
import type { DomainKey } from "@/lib/todayDomainVerdicts";

/**
 * Reading sphere chapter id (`sphere-{raw}`) → domain icon component.
 * FOUNDATION_UI §16.6 A1 — primary consumer is Reading, not VerdictStrip.
 */
export function domainIconForChapterId(chapterId: string) {
  if (!chapterId.startsWith("sphere-")) return null;
  const sphereKey = chapterId.slice("sphere-".length);
  const domain = mapSphereToDomain(sphereKey);
  if (domain === "work" || domain === "money" || domain === "relationships" || domain === "energy") {
    return TODAY_DOMAIN_ICON_MAP[domain as DomainKey];
  }
  return null;
}
