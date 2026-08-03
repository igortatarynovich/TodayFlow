import { getJson, postJson } from "@/lib/api";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import {
  clearGuestProfileDraft,
  guestDraftToCoreSetupPayload,
  readGuestProfileDraft,
  type GuestProfileDraft,
} from "@/lib/guestProfileDraft";
import type { CoreSetupResponse } from "@/lib/coreSetup";
import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";
import {
  claimGuestSessionAfterAuth,
  clearGuestClaimCredentials,
  issueGuestClaimToken,
  syncGuestProgressToServer,
} from "@/lib/guestProgressSync";
import { refreshTodayStory } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";

export type ClaimGuestProfileResult =
  | { status: "ready"; profilePath: string; storyRefreshRequired?: boolean }
  | { status: "needs_refine"; refinePath: "/onboarding/refine?after=save" }
  | { status: "no_draft" }
  | { status: "claiming" };

export function canClaimGuestProfile(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.first_name?.trim() && draft.birth_date?.trim());
}

/** Call before navigating to auth — syncs progress + issues claim token. */
export async function prepareGuestClaimBeforeAuth(): Promise<void> {
  try {
    await syncGuestProgressToServer();
    await issueGuestClaimToken();
  } catch {
    // Best-effort; claim after auth will retry sync/token.
  }
}

async function userAlreadyHasReadyProfile(): Promise<boolean> {
  try {
    const core = await getJson<CoreProfile>("/account/core-profile");
    if (core?.is_ready) return true;
    if (core?.astro?.profile_id) return true;
    const birth = core?.astro?.birth_date;
    if (typeof birth === "string" && birth.trim()) return true;
  } catch {
    /* network — fall through and allow draft claim for brand-new accounts */
  }
  return false;
}

async function claimDayProgressOnly(options?: {
  /** Clear draft only when account already owns profile facts (avoid stale overwrite). */
  clearDraftOnSuccess?: boolean;
}): Promise<ClaimGuestProfileResult> {
  const clearDraftOnSuccess = options?.clearDraftOnSuccess ?? false;
  try {
    const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: FIRST_TODAY_PATH });
    clearGuestClaimCredentials();
    if (dayClaim.claim_status === "completed") {
      if (clearDraftOnSuccess || dayClaim.transferred_blocks.length > 0) {
        clearGuestProfileDraft();
      }
      if (dayClaim.transferred_blocks.length > 0) {
        if (dayClaim.story_refresh_required) {
          // Assemble-once: never block login/navigation on LLM rebuild.
          void refreshTodayStory({ localDate: dayClaim.local_date }).catch(() => {});
        }
        return {
          status: "ready",
          profilePath: dayClaim.redirect_target || FIRST_TODAY_PATH,
          storyRefreshRequired: dayClaim.story_refresh_required,
        };
      }
    }
  } catch {
    try {
      const { claimGuestDaySymbols } = await import("@/lib/daySymbolReveal");
      await claimGuestDaySymbols();
    } catch {
      /* best-effort */
    }
    // Keep guest draft on failure — otherwise Tarot/Today ask to recreate birth data.
    clearGuestClaimCredentials();
  }
  return { status: "no_draft" };
}

export async function claimGuestProfileAfterAuth(): Promise<ClaimGuestProfileResult> {
  const draft = readGuestProfileDraft();
  if (!canClaimGuestProfile(draft) || !draft) {
    const result = await claimDayProgressOnly();
    return result.status === "ready" ? result : { status: "no_draft" };
  }

  if (!draft.location_name?.trim()) {
    await prepareGuestClaimBeforeAuth();
    return { status: "needs_refine", refinePath: "/onboarding/refine?after=save" };
  }

  // Existing account must not be silently overwritten by a stale guest draft.
  if (await userAlreadyHasReadyProfile()) {
    return claimDayProgressOnly({ clearDraftOnSuccess: true });
  }

  // Ensure server has latest guest progress + claim token before atomic claim.
  try {
    await prepareGuestClaimBeforeAuth();
  } catch {
    /* continue */
  }

  const payload = guestDraftToCoreSetupPayload(draft);
  const response = await postJson<CoreSetupResponse>("/account/core-setup", payload);
  publishCoreProfileUpdate(response.core_profile);

  let redirect = FIRST_TODAY_PATH;
  let storyRefreshRequired = false;
  try {
    const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: FIRST_TODAY_PATH });
    redirect = dayClaim.redirect_target || FIRST_TODAY_PATH;
    storyRefreshRequired = Boolean(dayClaim.story_refresh_required);
    if (storyRefreshRequired) {
      // Fire-and-forget — Today assembling / catch-up owns the package.
      void refreshTodayStory({ localDate: dayClaim.local_date }).catch(() => {});
    }
  } catch {
    // Fallback: legacy symbols-only claim
    try {
      const { claimGuestDaySymbols } = await import("@/lib/daySymbolReveal");
      await claimGuestDaySymbols();
    } catch {
      /* best-effort */
    }
  }

  clearGuestProfileDraft();
  clearGuestClaimCredentials();
  return { status: "ready", profilePath: redirect, storyRefreshRequired };
}
