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

export type ClaimGuestProfileResult =
  | { status: "ready"; profilePath: typeof FIRST_TODAY_PATH }
  | { status: "needs_refine"; refinePath: "/onboarding/refine?after=save" }
  | { status: "no_draft" };

export function canClaimGuestProfile(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.first_name?.trim() && draft.birth_date?.trim());
}

export async function claimGuestProfileAfterAuth(): Promise<ClaimGuestProfileResult> {
  const draft = readGuestProfileDraft();
  if (!canClaimGuestProfile(draft) || !draft) {
    return { status: "no_draft" };
  }

  if (!draft.location_name?.trim()) {
    return { status: "needs_refine", refinePath: "/onboarding/refine?after=save" };
  }

  const payload = guestDraftToCoreSetupPayload(draft);
  const response = await postJson<CoreSetupResponse>("/account/core-setup", payload);
  publishCoreProfileUpdate(response.core_profile);
  if (!hasOnboardingIntent()) saveIntentTheme("focus");
  if (!hasOnboardingReality()) saveRealityState("stable");
  clearGuestProfileDraft();
  return { status: "ready", profilePath: FIRST_TODAY_PATH };
}
