/** Pre-registration free tier (web). Enforcement on routes — incremental. */

export const GUEST_ACCESS_LIMITS = {
  tarotSpreads: 1,
  compatibilityChecks: 4,
  practicesTier: "basic" as const,
} as const;

export type GuestAccessLimits = typeof GUEST_ACCESS_LIMITS;
