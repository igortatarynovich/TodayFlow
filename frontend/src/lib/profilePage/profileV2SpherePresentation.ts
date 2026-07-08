import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";

/** Short template line for direction grid cards (from sphere.need). */
export function profileV2SphereCardLine(sphere: ProfileLifeSphere): string {
  const need = sphere.need.trim();
  if (!need) return sphere.helps.trim() || sphere.title;
  const firstClause = need.split(/[.;]/)[0]?.trim();
  if (!firstClause) return need;
  return firstClause.length > 88 ? `${firstClause.slice(0, 85)}…` : firstClause;
}

/** Deterministic 35–92% bar width for sphere cards — not evolution_score. */
export function profileV2SphereProgressPercent(sphereId: string, awarenessPercent: number): number {
  let hash = 0;
  for (let i = 0; i < sphereId.length; i += 1) {
    hash = (hash * 31 + sphereId.charCodeAt(i)) % 997;
  }
  const spread = 35 + (hash % 40);
  const blend = Math.round(spread * 0.55 + awarenessPercent * 0.45);
  return Math.max(28, Math.min(92, blend));
}
