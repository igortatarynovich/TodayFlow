"use client";

import { claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import {
  FIRST_TODAY_PATH,
  hasCompletedFirstToday,
} from "@/lib/firstTodayState";
import { ONBOARDING_CORE_PATH } from "@/lib/coreSetup";
import { guestSignupHref } from "@/lib/guestAccessStore";

export type AuthMode = "login" | "signup";

export function getSafeRedirectTarget(value: string | null | undefined): string {
  if (!value) return "/profile";
  try {
    const decoded = decodeURIComponent(value);
    if (!decoded.startsWith("/") || decoded.startsWith("//")) return "/profile";
    if (decoded.includes("setup=core")) return ONBOARDING_CORE_PATH;
    return decoded;
  } catch {
    return "/profile";
  }
}

export function getSafeAuthMode(value: string | null | undefined): AuthMode {
  // Password signup is retired — only soft onboarding registers new users.
  return value === "signup" ? "signup" : "login";
}

/**
 * Login → `/auth` (returning users only).
 * Signup → canonical soft flow (`/onboarding/welcome`) — never the password form.
 */
export function buildAuthHref(mode: AuthMode = "login", redirect?: string | null): string {
  if (mode === "signup") {
    const safeRedirect = getSafeRedirectTarget(redirect);
    if (safeRedirect && safeRedirect !== "/profile") {
      const base = guestSignupHref();
      const join = base.includes("?") ? "&" : "?";
      return `${base}${join}redirect=${encodeURIComponent(safeRedirect)}`;
    }
    return guestSignupHref();
  }
  const safeRedirect = getSafeRedirectTarget(redirect);
  if (safeRedirect === "/profile") {
    return `/auth?mode=login`;
  }
  return `/auth?mode=login&redirect=${encodeURIComponent(safeRedirect)}`;
}

/** Client-only: next route after core profile is ready (onboarding → First Today → Profile). */
export function resolvePostCoreAuthTarget(): string {
  // Intent/Reality live inside First Today (placement C) — do not divert to /onboarding/intent|reality.
  if (!hasCompletedFirstToday()) return FIRST_TODAY_PATH;
  return "/profile";
}

/** Birth facts / astro id already on the account — do not force core setup again. */
export function hasUsableCoreProfileBase(coreProfile: {
  is_ready?: boolean;
  astro?: { profile_id?: number | null; birth_date?: string | null } | null;
} | null | undefined): boolean {
  if (!coreProfile) return false;
  if (coreProfile.is_ready) return true;
  if (coreProfile.astro?.profile_id) return true;
  const birth = coreProfile.astro?.birth_date;
  return typeof birth === "string" && Boolean(birth.trim());
}

const POST_AUTH_CORE_TIMEOUT_MS = 4_000;
const CORE_PROFILE_TIMEOUT = Symbol("core-profile-timeout");

export async function resolvePostAuthTarget(explicitRedirect?: string | null): Promise<string> {
  const safeRedirect = getSafeRedirectTarget(explicitRedirect);
  if (safeRedirect !== "/profile" && safeRedirect !== ONBOARDING_CORE_PATH) {
    return safeRedirect;
  }

  try {
    // Never hold the login spinner on a hung core-profile — fall through to First Today / profile.
    const coreProfile = await Promise.race([
      fetchCoreProfileCached(),
      new Promise<typeof CORE_PROFILE_TIMEOUT>((resolve) => {
        setTimeout(() => resolve(CORE_PROFILE_TIMEOUT), POST_AUTH_CORE_TIMEOUT_MS);
      }),
    ]);
    if (coreProfile === CORE_PROFILE_TIMEOUT) return resolvePostCoreAuthTarget();
    if (!hasUsableCoreProfileBase(coreProfile)) return ONBOARDING_CORE_PATH;
    return resolvePostCoreAuthTarget();
  } catch {
    // Transient API failure must not look like "profile missing" — keep the session path.
    return resolvePostCoreAuthTarget();
  }
}

/** After token is set: route immediately; guest claim is best-effort and must not block login. */
export async function resolveTargetAfterAuthSession(explicitRedirect?: string | null): Promise<string> {
  // Sync refine gate — no network. Returning users without a draft skip this.
  try {
    const { canClaimGuestProfile, prepareGuestClaimBeforeAuth } = await import("@/lib/claimGuestProfile");
    const { readGuestProfileDraft } = await import("@/lib/guestProfileDraft");
    const draft = readGuestProfileDraft();
    if (canClaimGuestProfile(draft) && draft && !draft.location_name?.trim()) {
      void prepareGuestClaimBeforeAuth().catch(() => {});
      return "/onboarding/refine?after=save";
    }
  } catch {
    /* ignore */
  }

  const target = await resolvePostAuthTarget(explicitRedirect);
  // Fire-and-forget — never hold the login spinner / navigation on claim or story refresh.
  void claimGuestProfileAfterAuth().catch(() => {});
  return target;
}

export { ONBOARDING_CORE_PATH, FIRST_TODAY_PATH };
