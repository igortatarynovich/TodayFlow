import { postJson } from "@/lib/api";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import {
  clearGuestProfileDraft,
  guestDraftToCoreSetupPayload,
  readGuestProfileDraft,
  type GuestProfileDraft,
} from "@/lib/guestProfileDraft";
import type { CoreSetupResponse } from "@/lib/coreSetup";
import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";
import { hasOnboardingIntent, hasOnboardingReality, saveIntentTheme, saveRealityState } from "@/lib/onboardingContext";
import {
  claimGuestSessionAfterAuth,
  issueGuestClaimToken,
  syncGuestProgressToServer,
} from "@/lib/guestProgressSync";
import { refreshTodayStory } from "@/lib/todayContract";

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

export async function claimGuestProfileAfterAuth(): Promise<ClaimGuestProfileResult> {
  const draft = readGuestProfileDraft();
  if (!canClaimGuestProfile(draft) || !draft) {
    // Still attempt full day claim if guest had ritual progress without draft.
    try {
      const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: FIRST_TODAY_PATH });
      if (dayClaim.claim_status === "completed" && dayClaim.transferred_blocks.length > 0) {
        if (dayClaim.story_refresh_required) {
          try {
            await refreshTodayStory({ localDate: dayClaim.local_date });
          } catch {
            /* refresh is separate from claim */
          }
        }
        return {
          status: "ready",
          profilePath: dayClaim.redirect_target || FIRST_TODAY_PATH,
          storyRefreshRequired: dayClaim.story_refresh_required,
        };
      }
    } catch {
      /* no guest progress */
    }
    return { status: "no_draft" };
  }

  if (!draft.location_name?.trim()) {
    await prepareGuestClaimBeforeAuth();
    return { status: "needs_refine", refinePath: "/onboarding/refine?after=save" };
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
      try {
        await refreshTodayStory({ localDate: dayClaim.local_date });
      } catch {
        /* FE may refresh on Today mount */
      }
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

  if (!hasOnboardingIntent()) saveIntentTheme("focus");
  if (!hasOnboardingReality()) saveRealityState("stable");
  clearGuestProfileDraft();
  return { status: "ready", profilePath: redirect, storyRefreshRequired };
}
