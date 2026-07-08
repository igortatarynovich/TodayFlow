/** Guest profile draft — value-first onboarding (pre-auth). Mirrors iOS BirthProfileDraft shape. */

export const GUEST_PROFILE_DRAFT_KEY = "todayflow_guest_profile_draft_v1";
export const GUEST_PROFILE_SESSION_KEY = "todayflow_guest_profile_session_v1";

export type GuestProfileDraft = {
  version: 1;
  first_name: string;
  birth_date: string;
  sun_sign: string | null;
  life_path: number | null;
  preview_seen_at: string | null;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
  birth_time: string | null;
  time_unknown: boolean;
  first_today_started_at: string | null;
  save_ready_at: string | null;
  preview_recognition_audit?: import("@/lib/interpretation/onboardingRecognitionTypes").RecognitionSelectionAudit | null;
};

export const VALUE_FIRST_PATHS = {
  welcome: "/onboarding/welcome",
  birth: "/onboarding/birth",
  preview: "/onboarding/preview",
  refine: "/onboarding/refine",
  save: "/onboarding/save",
  firstToday: "/today?first=1",
} as const;

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

function isCommittedGuestProgress(draft: GuestProfileDraft): boolean {
  return Boolean(draft.first_today_started_at?.trim() || draft.save_ready_at?.trim());
}

function migrateLegacyUncommittedDraft(): void {
  if (!isBrowser()) return;
  if (sessionStorage.getItem(GUEST_PROFILE_SESSION_KEY)) return;

  const rawLocal = localStorage.getItem(GUEST_PROFILE_DRAFT_KEY);
  if (!rawLocal) return;

  try {
    const parsed = JSON.parse(rawLocal) as GuestProfileDraft;
    if (parsed?.version === 1 && !isCommittedGuestProgress(parsed)) {
      sessionStorage.setItem(GUEST_PROFILE_SESSION_KEY, rawLocal);
      localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
    }
  } catch {
    localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
  }
}

export function createEmptyGuestProfileDraft(): GuestProfileDraft {
  return {
    version: 1,
    first_name: "",
    birth_date: "",
    sun_sign: null,
    life_path: null,
    preview_seen_at: null,
    location_name: null,
    latitude: null,
    longitude: null,
    birth_time: null,
    time_unknown: true,
    first_today_started_at: null,
    save_ready_at: null,
  };
}

/** Start a fresh guest onboarding path — clears in-progress draft; keeps committed progress. */
export function beginGuestOnboardingSession(): void {
  if (!isBrowser()) return;
  sessionStorage.removeItem(GUEST_PROFILE_SESSION_KEY);

  const rawLocal = localStorage.getItem(GUEST_PROFILE_DRAFT_KEY);
  if (!rawLocal) return;

  try {
    const parsed = JSON.parse(rawLocal) as GuestProfileDraft;
    if (!isCommittedGuestProgress(parsed)) {
      localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
    }
  } catch {
    localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
  }
}

export function readGuestProfileDraft(): GuestProfileDraft | null {
  if (!isBrowser()) return null;

  migrateLegacyUncommittedDraft();

  try {
    const rawLocal = localStorage.getItem(GUEST_PROFILE_DRAFT_KEY);
    if (rawLocal) {
      const parsed = JSON.parse(rawLocal) as GuestProfileDraft;
      if (parsed?.version === 1 && isCommittedGuestProgress(parsed)) {
        return parsed;
      }
    }
  } catch {
    localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
  }

  try {
    const rawSession = sessionStorage.getItem(GUEST_PROFILE_SESSION_KEY);
    if (!rawSession) return null;
    const parsed = JSON.parse(rawSession) as GuestProfileDraft;
    if (!parsed || parsed.version !== 1) return null;
    return parsed;
  } catch {
    sessionStorage.removeItem(GUEST_PROFILE_SESSION_KEY);
    return null;
  }
}

export function writeGuestProfileDraft(next: GuestProfileDraft): GuestProfileDraft {
  const payload: GuestProfileDraft = { ...next, version: 1 };
  if (!isBrowser()) return payload;

  if (isCommittedGuestProgress(payload)) {
    localStorage.setItem(GUEST_PROFILE_DRAFT_KEY, JSON.stringify(payload));
    sessionStorage.setItem(GUEST_PROFILE_SESSION_KEY, JSON.stringify(payload));
    return payload;
  }

  sessionStorage.setItem(GUEST_PROFILE_SESSION_KEY, JSON.stringify(payload));

  const rawLocal = localStorage.getItem(GUEST_PROFILE_DRAFT_KEY);
  if (rawLocal) {
    try {
      const parsed = JSON.parse(rawLocal) as GuestProfileDraft;
      if (!isCommittedGuestProgress(parsed)) {
        localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
      }
    } catch {
      localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
    }
  }

  return payload;
}

export function patchGuestProfileDraft(patch: Partial<GuestProfileDraft>): GuestProfileDraft {
  const base = readGuestProfileDraft() ?? createEmptyGuestProfileDraft();
  return writeGuestProfileDraft({ ...base, ...patch, version: 1 });
}

export function clearGuestProfileDraft(): void {
  if (isBrowser()) {
    localStorage.removeItem(GUEST_PROFILE_DRAFT_KEY);
    sessionStorage.removeItem(GUEST_PROFILE_SESSION_KEY);
  }
}

export function hasGuestName(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.first_name?.trim());
}

export function hasGuestBirthDate(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.birth_date?.trim());
}

export function hasGuestPreview(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.preview_seen_at?.trim());
}

export function isGuestSaveReady(draft: GuestProfileDraft | null = readGuestProfileDraft()): boolean {
  return Boolean(draft?.save_ready_at?.trim());
}

export function guestDraftToCoreSetupPayload(draft: GuestProfileDraft) {
  return {
    first_name: draft.first_name.trim(),
    last_name: null as string | null,
    label: "Я",
    birth_date: draft.birth_date,
    birth_time: draft.time_unknown ? null : draft.birth_time || null,
    time_unknown: draft.time_unknown,
    location_name: draft.location_name?.trim() || "",
    latitude: draft.latitude,
    longitude: draft.longitude,
    gender: "unspecified",
  };
}
