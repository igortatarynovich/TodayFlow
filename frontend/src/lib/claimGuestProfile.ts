import { getJson, postJson } from "@/lib/api";
import { publishCoreProfileUpdate } from "@/lib/coreProfileCacheStorage";
import {
  clearGuestProfileDraft,
  guestDraftToCoreSetupPayload,
  readGuestProfileDraft,
  type GuestProfileDraft,
} from "@/lib/guestProfileDraft";
import {
  clearGuestCompatPair,
  readGuestCompatPair,
  type GuestCompatPersonDraft,
} from "@/lib/guestCompatPair";
import type { CoreSetupResponse } from "@/lib/coreSetup";
import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";
import { hasOnboardingIntent, hasOnboardingReality, saveIntentTheme, saveRealityState } from "@/lib/onboardingContext";
import {
  claimGuestSessionAfterAuth,
  clearGuestClaimCredentials,
  issueGuestClaimToken,
  syncGuestProgressToServer,
} from "@/lib/guestProgressSync";
import { refreshTodayStory } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";
import type { AstroProfileSaveResponse } from "@/lib/types";

export type ClaimGuestProfileResult =
  | { status: "ready"; profilePath: string; storyRefreshRequired?: boolean }
  | { status: "needs_refine"; refinePath: "/onboarding/refine?after=save" }
  | { status: "no_draft" }
  | { status: "claiming" };

export function canClaimGuestProfile(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  // Name is optional (name numerology only). Birth date is the hard minimum.
  return Boolean(draft?.birth_date?.trim());
}

async function createAstroFromCompatPerson(
  person: GuestCompatPersonDraft,
  opts: { relation: string; is_primary: boolean },
): Promise<number | null> {
  try {
    const saved = await postJson<AstroProfileSaveResponse>("/account/astro-data", {
      label: person.label.trim() || "Профиль",
      relation: opts.relation,
      birth_date: person.birth_date,
      birth_time: person.time_unknown ? null : person.birth_time || null,
      time_unknown: person.time_unknown,
      location_name: person.location_name,
      latitude: person.latitude,
      longitude: person.longitude,
      is_primary: opts.is_primary,
    });
    return saved.id;
  } catch {
    return null;
  }
}

/** Bind two durable drafts from 1A personal compatibility after auth. */
export async function claimGuestCompatPairAfterAuth(opts?: {
  /** When primary was already created via core-setup / existing account. */
  skipPrimary?: boolean;
}): Promise<{
  profile_a_id: number | null;
  profile_b_id: number | null;
} | null> {
  const pair = readGuestCompatPair();
  if (!pair) return null;

  const skipPrimary = Boolean(opts?.skipPrimary) || (await userAlreadyHasReadyProfile());
  let profileA: number | null = null;
  let profileB: number | null = null;

  if (!skipPrimary) {
    profileA = await createAstroFromCompatPerson(pair.person_a, {
      relation: "self",
      is_primary: true,
    });
  } else {
    // Do not recreate person_a as a duplicate of the bound primary (1B).
    profileA = null;
  }

  profileB = await createAstroFromCompatPerson(pair.person_b, {
    relation: "partner",
    is_primary: false,
  });

  // Pure 1A path with existing account: also store person_a as close_person.
  if (skipPrimary && opts?.skipPrimary !== true) {
    // Existing account before this claim — keep both people as circle profiles.
    profileA = await createAstroFromCompatPerson(pair.person_a, {
      relation: "close_person",
      is_primary: false,
    });
  }

  clearGuestCompatPair();
  return { profile_a_id: profileA, profile_b_id: profileB };
}

/** Call before navigating to auth — syncs progress + durable profiles + claim token. */
export async function prepareGuestClaimBeforeAuth(): Promise<void> {
  try {
    await syncGuestProgressToServer();
  } catch {
    // Best-effort; claim after auth will retry sync/token.
  }
  try {
    const { syncGuestProfilesToServer } = await import("@/lib/guestProfilesSync");
    await syncGuestProfilesToServer();
  } catch {
    /* profiles sync is best-effort; local draft remains fallback */
  }
  try {
    await issueGuestClaimToken();
  } catch {
    /* claim after auth will retry */
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

async function claimDayProgressOnly(): Promise<ClaimGuestProfileResult> {
  try {
    const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: FIRST_TODAY_PATH });
    clearGuestClaimCredentials();
    clearGuestProfileDraft();
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
    try {
      const { claimGuestDaySymbols } = await import("@/lib/daySymbolReveal");
      await claimGuestDaySymbols();
    } catch {
      /* best-effort */
    }
    // Keep local drafts on failure so user can retry claim (server drafts also retained).
  }
  return { status: "no_draft" };
}

export async function claimGuestProfileAfterAuth(): Promise<ClaimGuestProfileResult> {
  const draft = readGuestProfileDraft();
  const compatPair = readGuestCompatPair();

  // Ensure server has latest drafts before any bind path.
  try {
    await prepareGuestClaimBeforeAuth();
  } catch {
    /* continue */
  }

  // Prefer server claim (binds guest_profiles + day progress). Falls back to core-setup.
  let serverBoundProfiles = false;
  try {
    const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: "/profile" });
    if (dayClaim.claim_status === "completed") {
      const blocks = dayClaim.transferred_blocks || [];
      serverBoundProfiles = blocks.includes("profiles");
      if (serverBoundProfiles || (await userAlreadyHasReadyProfile())) {
        clearGuestProfileDraft();
        clearGuestCompatPair();
        clearGuestClaimCredentials();
        if (dayClaim.story_refresh_required) {
          try {
            await refreshTodayStory({ localDate: dayClaim.local_date });
          } catch {
            /* FE may refresh on Today mount */
          }
        }
        const path =
          compatPair && !draft?.birth_date
            ? "/account/profiles"
            : dayClaim.redirect_target || "/profile";
        return {
          status: "ready",
          profilePath: path,
          storyRefreshRequired: Boolean(dayClaim.story_refresh_required),
        };
      }
    }
  } catch {
    /* fall through to local draft / core-setup */
  }

  if (!canClaimGuestProfile(draft) || !draft) {
    if (compatPair) {
      try {
        await claimGuestCompatPairAfterAuth();
        clearGuestClaimCredentials();
        return { status: "ready", profilePath: "/account/profiles" };
      } catch {
        return { status: "no_draft" };
      }
    }
    const result = await claimDayProgressOnly();
    return result.status === "ready" ? result : { status: "no_draft" };
  }

  // Location is optional when time is unknown — soft missing, not a bind blocker.
  // Existing account must not be silently overwritten by a stale guest draft.
  if (await userAlreadyHasReadyProfile()) {
    if (compatPair) {
      try {
        await claimGuestCompatPairAfterAuth();
      } catch {
        /* best-effort */
      }
    }
    return claimDayProgressOnly();
  }

  const payload = guestDraftToCoreSetupPayload(draft);
  const response = await postJson<CoreSetupResponse>("/account/core-setup", payload);
  publishCoreProfileUpdate(response.core_profile);

  // 1A dual drafts: bind partner (person_b); primary already from core-setup.
  if (compatPair) {
    try {
      await claimGuestCompatPairAfterAuth({ skipPrimary: true });
    } catch {
      /* primary claim already succeeded */
    }
  }

  const PROFILE_PATH = "/profile";
  let redirect = PROFILE_PATH;
  let storyRefreshRequired = false;
  try {
    const dayClaim = await claimGuestSessionAfterAuth({ redirectTarget: PROFILE_PATH });
    const coreReady = Boolean(response.core_profile?.is_ready);
    redirect = coreReady ? PROFILE_PATH : dayClaim.redirect_target || PROFILE_PATH;
    storyRefreshRequired = Boolean(dayClaim.story_refresh_required);
    if (storyRefreshRequired) {
      try {
        await refreshTodayStory({ localDate: dayClaim.local_date });
      } catch {
        /* FE may refresh on Today mount */
      }
    }
  } catch {
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
  clearGuestClaimCredentials();
  return { status: "ready", profilePath: redirect, storyRefreshRequired };
}
