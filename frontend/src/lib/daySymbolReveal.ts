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
  };
  number: {
    status: string;
    revealed: boolean;
    value?: number | null;
    reduced_value?: number | null;
    title?: string | null;
  };
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

export async function fetchDaySymbolState(_isAuthenticated: boolean): Promise<DaySymbolPublicView> {
  const tz = clientTimezone();
  const day = localDateISO(tz);
  const q = `?local_date=${encodeURIComponent(day)}&timezone=${encodeURIComponent(tz)}`;
  return symbolsRequest<DaySymbolPublicView>(`/today/symbols/state${q}`, { method: "GET", guest: true });
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

/** After reveal: show symbols immediately; refresh story only when server asks. */
export function shouldRefreshStoryAfterReveal(view: DaySymbolPublicView | null | undefined): boolean {
  return Boolean(view?.story_refresh_required);
}

export async function claimGuestDaySymbols(): Promise<void> {
  const guest_session_id = getOrCreateGuestSessionId();
  if (!guest_session_id) return;
  await postJson("/today/symbols/claim", {
    guest_session_id,
    local_date: localDateISO(),
  });
}
