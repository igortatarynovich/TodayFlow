/** Client helpers for server SoT day symbol reveal (`/today/symbols/*`). */

import { getStoredAccessToken, postJson } from "@/lib/api";
import { getLocale } from "@/lib/i18n";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";
const GUEST_SESSION_KEY = "todayflow_guest_session_v1";

async function symbolsRequest<T>(path: string, init?: RequestInit & { guest?: boolean }): Promise<T> {
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", "application/json");
  headers.set("Accept-Language", getLocale());
  const token = getStoredAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init?.guest || !token) {
    Object.entries(guestSessionHeaders()).forEach(([k, v]) => headers.set(k, v));
  }
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: "include" });
  if (!res.ok) {
    throw new Error(`symbolsRequest ${path} → ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type HookRevealPayload = {
  kind?: string;
  identity?: Record<string, unknown>;
  base?: { meaning?: string | null; keywords?: string[]; name?: string | null } | null;
  bridge_to_day?: string | null;
  bridge_status?: "ok" | "unavailable" | string;
  bridge_fail_copy?: string | null;
  instruction?: string | Record<string, unknown> | null;
  instruction_status?: string;
  personal_angle?: string | null;
  result_loop?: string;
};

export type DaySymbolPublicView = {
  contract_version?: string;
  local_date: string;
  timezone_name?: string;
  card: {
    status: string;
    revealed: boolean;
    id?: number | string | null;
    name?: string | null;
    orientation?: string | null;
    meaning?: string | null;
    keywords?: string[] | null;
    hook_reveal?: HookRevealPayload | null;
  };
  number: {
    status: string;
    revealed: boolean;
    value?: number | null;
    reduced_value?: number | null;
    title?: string | null;
    summary?: string | null;
    hook_reveal?: HookRevealPayload | null;
  };
  color_hook_reveal?: HookRevealPayload | null;
  story_refresh_required?: boolean;
  story_status?: string;
  story_fingerprint?: string | null;
};

export function getOrCreateGuestSessionId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem(GUEST_SESSION_KEY);
  if (!id) {
    id =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `g_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(GUEST_SESSION_KEY, id);
  }
  return id;
}

/** Drop guest session id after successful claim / account switch. */
export function clearGuestSessionId(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(GUEST_SESSION_KEY);
  } catch {
    /* ignore */
  }
}

export function guestSessionHeaders(): Record<string, string> {
  const id = getOrCreateGuestSessionId();
  return id ? { "X-Guest-Session-Id": id } : {};
}

function localDateISO(timeZone?: string): string {
  try {
    const tz = timeZone || Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
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

function clientTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

export async function fetchDaySymbolState(isAuthenticated: boolean): Promise<DaySymbolPublicView> {
  const tz = clientTimezone();
  const day = localDateISO(tz);
  const q = `?local_date=${encodeURIComponent(day)}&timezone=${encodeURIComponent(tz)}`;
  // Authenticated: Bearer only (user owner_key). Guest: X-Guest-Session-Id.
  return symbolsRequest<DaySymbolPublicView>(`/today/symbols/state${q}`, {
    method: "GET",
    guest: !isAuthenticated,
  });
}

export async function revealDayCard(input: {
  cardId: number;
  orientation?: string;
  isAuthenticated: boolean;
  source?: string;
  idempotencyKey: string;
}): Promise<DaySymbolPublicView> {
  const tz = clientTimezone();
  const body = {
    card_id: input.cardId,
    orientation: input.orientation || "upright",
    local_date: localDateISO(tz),
    timezone: tz,
    reveal_source: input.source || "ritual",
    idempotency_key: input.idempotencyKey,
  };
  return symbolsRequest<DaySymbolPublicView>("/today/symbols/card/reveal", {
    method: "POST",
    body: JSON.stringify(body),
    guest: !input.isAuthenticated,
  });
}

export async function revealDayNumber(input: {
  isAuthenticated: boolean;
  source?: string;
  idempotencyKey: string;
}): Promise<DaySymbolPublicView> {
  const tz = clientTimezone();
  const body = {
    local_date: localDateISO(tz),
    timezone: tz,
    reveal_source: input.source || "ritual",
    idempotency_key: input.idempotencyKey,
  };
  return symbolsRequest<DaySymbolPublicView>("/today/symbols/number/reveal", {
    method: "POST",
    body: JSON.stringify(body),
    guest: !input.isAuthenticated,
  });
}

/**
 * Card/number are an interpretive overlay on the assembled day (DAY_LIFECYCLE_V1).
 * Reveal must never trigger day_story reassemble — even if a legacy server sets the flag.
 */
export function shouldRefreshStoryAfterReveal(_view?: DaySymbolPublicView | null): boolean {
  return false;
}

/** Apply revealed card/number into morning payloads without rebuilding the day. */
export function applySymbolRevealToMorning(
  morning: Record<string, unknown> | null | undefined,
  view: DaySymbolPublicView,
): Record<string, unknown> | null {
  if (!morning) return null;
  const next = { ...morning };
  if (view.card?.revealed) {
    next.tarot_card = {
      ...((morning.tarot_card as Record<string, unknown> | undefined) || {}),
      selection_status: "selected",
      status: "revealed",
      id: view.card.id ?? null,
      name: view.card.name ?? null,
      orientation: view.card.orientation ?? "upright",
    };
  }
  if (view.number?.revealed) {
    const value = view.number.value ?? view.number.reduced_value ?? null;
    next.numerology_number = {
      ...((morning.numerology_number as Record<string, unknown> | undefined) || {}),
      selection_status: "selected",
      status: "revealed",
      value,
      reduced_value: view.number.reduced_value ?? value,
      title: view.number.title ?? null,
    };
  }
  return next;
}

export async function claimGuestDaySymbols(): Promise<void> {
  const guest_session_id = getOrCreateGuestSessionId();
  if (!guest_session_id) return;
  await postJson("/today/symbols/claim", {
    guest_session_id,
    local_date: localDateISO(),
  });
}
