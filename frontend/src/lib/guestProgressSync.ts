/** Sync guest Today progress to server SoT before auth claim. */

import { getLocale } from "@/lib/i18n";
import {
  clearGuestSessionId,
  getOrCreateGuestSessionId,
  guestSessionHeaders,
} from "@/lib/daySymbolReveal";
import { readGuestProfileDraft } from "@/lib/guestProfileDraft";
import { readOnboardingContext } from "@/lib/onboardingContext";
import { readFirstTodayState } from "@/lib/firstTodayState";
import { loadRitualPersisted } from "@/lib/todayRitualPersisted";
import { loadDayEngagement } from "@/lib/todayDayEngagement";
import { buildGuestFirstTodayPayload } from "@/lib/buildGuestFirstTodayPayload";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";
const SECRET_KEY = "todayflow_guest_session_secret_v1";
const CLAIM_TOKEN_KEY = "todayflow_guest_claim_token_v1";

function clientTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

function localDateISO(timeZone?: string): string {
  try {
    const tz = timeZone || clientTimezone();
    return new Intl.DateTimeFormat("en-CA", {
      timeZone: tz,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).format(new Date());
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

export function getGuestSessionSecret(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(SECRET_KEY) || "";
}

function setGuestSessionSecret(secret: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(SECRET_KEY, secret);
}

export function getStoredClaimToken(): string {
  if (typeof window === "undefined") return "";
  return sessionStorage.getItem(CLAIM_TOKEN_KEY) || "";
}

export function clearStoredClaimToken() {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(CLAIM_TOKEN_KEY);
}

export function clearGuestSessionSecret() {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(SECRET_KEY);
  } catch {
    /* ignore */
  }
}

/** Clear all guest claim credentials after a successful transfer. */
export function clearGuestClaimCredentials() {
  clearStoredClaimToken();
  clearGuestSessionSecret();
  clearGuestSessionId();
}

async function guestFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", "application/json");
  headers.set("Accept-Language", getLocale());
  Object.entries(guestSessionHeaders()).forEach(([k, v]) => headers.set(k, v));
  const secret = getGuestSessionSecret();
  if (secret) headers.set("X-Guest-Session-Secret", secret);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: "include" });
  if (!res.ok) {
    throw new Error(`guestFetch ${path} → ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Register guest session with backend; persist session secret once. */
export async function ensureServerGuestSession(): Promise<string> {
  const guest_session_id = getOrCreateGuestSessionId();
  const body = {
    guest_session_id,
    locale: getLocale(),
    timezone: clientTimezone(),
  };
  const out = await guestFetch<{
    guest_session_id: string;
    session_secret: string | null;
    created: boolean;
  }>("/today/guest/session", { method: "POST", body: JSON.stringify(body) });
  if (out.session_secret) {
    setGuestSessionSecret(out.session_secret);
  }
  return getOrCreateGuestSessionId();
}

/** Push local guest Today progress into server SoT (no trust on claim). */
export async function syncGuestProgressToServer(): Promise<void> {
  await ensureServerGuestSession();
  const tz = clientTimezone();
  const day = localDateISO(tz);
  const draft = readGuestProfileDraft();
  const onboarding = readOnboardingContext();
  const firstToday = readFirstTodayState();
  const ritual = loadRitualPersisted(day);
  const engagement = loadDayEngagement(day);

  let first_result: Record<string, unknown> | null = null;
  if (draft && (draft.first_today_started_at || firstToday.completed_at)) {
    try {
      const payload = buildGuestFirstTodayPayload(draft);
      first_result = {
        contract: payload.contract,
        dateISO: payload.dateISO,
        cardName: payload.cardName,
        numerologyValue: payload.numerologyValue,
        first_today_state: firstToday,
      };
    } catch {
      first_result = { first_today_state: firstToday };
    }
  }

  const mood =
    ritual?.mood || engagement.morningMoodId
      ? {
          mood: ritual?.mood || null,
          morning_mood_id: engagement.morningMoodId,
          check_in_submitted: Boolean(ritual?.checkInSubmitted),
        }
      : null;

  const goals = engagement.dayGoal
    ? { day_goal: engagement.dayGoal }
    : null;

  await guestFetch("/today/guest/progress", {
    method: "PUT",
    body: JSON.stringify({
      local_date: day,
      timezone: tz,
      locale: getLocale(),
      mood,
      goals,
      onboarding: Object.keys(onboarding).length ? onboarding : null,
      first_result,
      ritual,
      today_state: engagement,
      profile_draft: draft,
    }),
  });
}

/** Issue short-lived claim token after syncing progress (call before/during auth). */
export async function issueGuestClaimToken(): Promise<string> {
  await syncGuestProgressToServer();
  const out = await guestFetch<{ claim_token: string }>("/today/guest/claim-token", {
    method: "POST",
    body: JSON.stringify({}),
  });
  if (typeof window !== "undefined") {
    sessionStorage.setItem(CLAIM_TOKEN_KEY, out.claim_token);
  }
  return out.claim_token;
}

export type FullGuestClaimResult = {
  claim_status: string;
  transferred_blocks: string[];
  conflicts: { block: string; reason: string }[];
  story_status: string;
  story_refresh_required: boolean;
  redirect_target: string;
  local_date?: string;
};

/** Atomic server claim using stored claim token only. */
export async function claimGuestSessionAfterAuth(input?: {
  redirectTarget?: string;
}): Promise<FullGuestClaimResult> {
  let token = getStoredClaimToken();
  if (!token) {
    token = await issueGuestClaimToken();
  }
  const { postJson } = await import("@/lib/api");
  const result = await postJson<FullGuestClaimResult>("/today/guest/claim", {
    claim_token: token,
    redirect_target: input?.redirectTarget || "/today?first=1",
    local_date: localDateISO(),
  });
  clearStoredClaimToken();
  return result;
}
