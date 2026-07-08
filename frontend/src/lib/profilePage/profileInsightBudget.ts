/**
 * Profile v0 · insight budget (cardinality).
 *
 * Cardinality alone is NOT sufficient — see profileInsightTaxonomy.ts (category gate).
 * Five strings about «глубина» = budget 5, taxonomy pass 1.
 */

export const PROFILE_INSIGHT_BUDGET = {
  hero: 4,
  why: 3,
  corePattern: 5,
  socialMirror: 4,
  love: 5,
  money: 5,
  compass: 5,
} as const;

export const PROFILE_INSIGHT_BUDGET_TOTAL = Object.values(PROFILE_INSIGHT_BUDGET).reduce(
  (sum, n) => sum + n,
  0,
);

export type ProfileInsightLayer = keyof typeof PROFILE_INSIGHT_BUDGET;
