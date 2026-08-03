/**
 * Domain signal strength for Reading cap + Response trap pick (v3.1).
 * Uses DOMAIN_MAGNITUDE_V1 irreversibility scale as absolute domain weight
 * (docs/foundation/DOMAIN_MAGNITUDE_V1.md §3.2) — not a second magnitude SoT.
 */

const SPHERE_TO_DOMAIN: Record<string, string> = {
  work: "work",
  work_decisions: "work",
  career: "work",
  money: "money",
  finances: "money",
  money_work: "money",
  relationships: "relationships",
  love: "relationships",
  family: "relationships",
  communication: "relationships",
  home: "relationships",
  energy: "energy",
  health: "energy",
  body: "energy",
  energy_body: "energy",
  creativity: "energy",
  rest_travel: "energy",
};

export function mapSphereToDomain(sphere: string | null | undefined): string {
  const key = (sphere || "").trim().toLowerCase();
  if (key === "work" || key === "money" || key === "relationships" || key === "energy") return key;
  return SPHERE_TO_DOMAIN[key] ?? "work";
}

/** |challenging_fallback| from DOMAIN_MAGNITUDE_V1 — higher = stronger day claim. */
export const DOMAIN_IRREVERSIBILITY_WEIGHT: Record<string, number> = {
  money: 0.75,
  relationships: 0.7,
  work: 0.65,
  energy: 0.6,
};

export function domainSignalWeight(sphere: string | null | undefined): number {
  const domain = mapSphereToDomain(sphere);
  return DOMAIN_IRREVERSIBILITY_WEIGHT[domain] ?? DOMAIN_IRREVERSIBILITY_WEIGHT.energy!;
}

export function sceneRoleBoost(role: string | null | undefined): number {
  const r = (role || "").trim().toLowerCase();
  if (r === "primary") return 0.2;
  if (r === "caution" || r === "peak") return 0.1;
  return 0;
}

/** Combined score for ranking Reading/Response scenes. */
export function sceneMagnitudeScore(scene: {
  sphere?: string | null;
  role_in_story?: string | null;
  trap?: string | null;
  opportunity?: string | null;
  what_happens?: string | null;
}): number {
  let score = domainSignalWeight(typeof scene.sphere === "string" ? scene.sphere : null);
  score += sceneRoleBoost(typeof scene.role_in_story === "string" ? scene.role_in_story : null);
  if (typeof scene.trap === "string" && scene.trap.trim()) score += 0.15;
  if (typeof scene.opportunity === "string" && scene.opportunity.trim()) score += 0.08;
  if (typeof scene.what_happens === "string" && scene.what_happens.trim()) score += 0.04;
  return score;
}
