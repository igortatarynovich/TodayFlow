"use client";

import { claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { fetchCoreProfileCached } from "@/lib/coreProfileCache";
import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";
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

/** Client-only: after core is ready — Profile is default (First Today optional, not a gate). */
export function resolvePostCoreAuthTarget(): string {
  return "/profile";
}

export async function resolvePostAuthTarget(explicitRedirect?: string | null): Promise<string> {
  const safeRedirect = getSafeRedirectTarget(explicitRedirect);
  if (safeRedirect !== "/profile" && safeRedirect !== ONBOARDING_CORE_PATH) {
    return safeRedirect;
  }

  try {
    const coreProfile = await fetchCoreProfileCached();
    if (!coreProfile?.is_ready) return ONBOARDING_CORE_PATH;
    return resolvePostCoreAuthTarget();
  } catch {
    return ONBOARDING_CORE_PATH;
  }
}

/** After token is set: claim value-first guest draft, then fall back to normal routing. */
export async function resolveTargetAfterAuthSession(explicitRedirect?: string | null): Promise<string> {
  try {
    const claim = await claimGuestProfileAfterAuth();
    if (claim.status === "ready") return claim.profilePath;
    if (claim.status === "needs_refine") return claim.refinePath;
  } catch {
    // Guest claim is best-effort; auth session remains valid.
  }
  return resolvePostAuthTarget(explicitRedirect);
}

export { ONBOARDING_CORE_PATH, FIRST_TODAY_PATH };
