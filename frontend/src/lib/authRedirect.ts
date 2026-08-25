"use client";

import { claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import {
  FIRST_TODAY_PATH,
  hasCompletedFirstToday,
  markFirstTodayCompleted,
} from "@/lib/firstTodayState";
import { ONBOARDING_CORE_PATH } from "@/lib/coreSetup";
import { guestSignupHref } from "@/lib/guestAccessStore";

export type AuthMode = "login" | "signup";

/** Product home after login. First Today (`?first=1`) is onboarding-only, never a login fallback. */
export const POST_AUTH_HOME_PATH = "/today";

function isFirstTodayRedirect(path: string): boolean {
  if (path === FIRST_TODAY_PATH) return true;
  try {
    const url = new URL(path, "https://todayflow.local");
    return url.pathname === "/today" && url.searchParams.get("first") === "1";
  } catch {
    return path.startsWith("/today") && path.includes("first=1");
  }
}

export function getSafeRedirectTarget(value: string | null | undefined): string {
  if (!value) return POST_AUTH_HOME_PATH;
  try {
    const decoded = decodeURIComponent(value);
    if (!decoded.startsWith("/") || decoded.startsWith("//")) return POST_AUTH_HOME_PATH;
    if (decoded.includes("setup=core")) return ONBOARDING_CORE_PATH;
    return decoded;
  } catch {
    return POST_AUTH_HOME_PATH;
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
    if (safeRedirect && safeRedirect !== "/profile" && safeRedirect !== POST_AUTH_HOME_PATH) {
      const base = guestSignupHref();
      const join = base.includes("?") ? "&" : "?";
      return `${base}${join}redirect=${encodeURIComponent(safeRedirect)}`;
    }
    return guestSignupHref();
  }
  const safeRedirect = getSafeRedirectTarget(redirect);
  if (safeRedirect === "/profile" || safeRedirect === POST_AUTH_HOME_PATH) {
    return `/auth?mode=login`;
  }
  return `/auth?mode=login&redirect=${encodeURIComponent(safeRedirect)}`;
}

/**
 * Client-only: next route after core profile is ready.
 * Login opens Today. First Today chips stay an explicit onboarding URL
 * (`CoreOnboardingFlow` / intent / reality), not a localStorage fallback.
 */
export function resolvePostCoreAuthTarget(): string {
  return POST_AUTH_HOME_PATH;
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

function rememberReturningToday(): void {
  if (!hasCompletedFirstToday()) {
    markFirstTodayCompleted();
  }
}

export async function resolvePostAuthTarget(explicitRedirect?: string | null): Promise<string> {
  const safeRedirect = getSafeRedirectTarget(explicitRedirect);
  const needsAccountGate =
    safeRedirect === POST_AUTH_HOME_PATH ||
    safeRedirect === "/profile" ||
    safeRedirect === ONBOARDING_CORE_PATH ||
    isFirstTodayRedirect(safeRedirect);

  if (!needsAccountGate) {
    return safeRedirect;
  }

  try {
    // Never hold the login spinner on a hung core-profile — open Today, not First Today chips.
    const coreProfile = await Promise.race([
      fetchCoreProfileCached(),
      new Promise<typeof CORE_PROFILE_TIMEOUT>((resolve) => {
        setTimeout(() => resolve(CORE_PROFILE_TIMEOUT), POST_AUTH_CORE_TIMEOUT_MS);
      }),
    ]);
    if (coreProfile === CORE_PROFILE_TIMEOUT) return POST_AUTH_HOME_PATH;
    if (!hasUsableCoreProfileBase(coreProfile)) return ONBOARDING_CORE_PATH;
    rememberReturningToday();
    if (safeRedirect === "/profile") return "/profile";
    return POST_AUTH_HOME_PATH;
  } catch {
    // Transient API failure must not look like "profile missing" — keep the session path.
    return POST_AUTH_HOME_PATH;
  }
}

/**
 * Leave the auth screen with a full document load.
 * Next.js `router.replace` can hang on iOS Safari / PWA after login (RSC payload
 * never commits) and leave the full-page spinner up forever.
 */
export function assignAfterAuthSession(target: string): void {
  if (typeof window === "undefined") return;
  window.location.assign(getSafeRedirectTarget(target));
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
