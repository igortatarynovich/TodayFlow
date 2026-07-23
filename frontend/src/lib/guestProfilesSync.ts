/** Sync guest profile drafts to durable server SoT (`/guest/profiles`). */

import { getLocale } from "@/lib/i18n";
import { guestSessionHeaders, getOrCreateGuestSessionId } from "@/lib/daySymbolReveal";
import { readGuestCompatPair } from "@/lib/guestCompatPair";
import { readGuestProfileDraft, type GuestProfileDraft } from "@/lib/guestProfileDraft";
import {
  ensureServerGuestSession,
  getGuestSessionSecret,
} from "@/lib/guestProgressSync";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

async function guestFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", "application/json");
  headers.set("Accept-Language", getLocale());
  Object.entries(guestSessionHeaders()).forEach(([k, v]) => headers.set(k, v));
  const secret = getGuestSessionSecret();
  if (secret) headers.set("X-Guest-Session-Secret", secret);
  // Ensure session id header even if guestSessionHeaders missed it.
  if (!headers.get("X-Guest-Session-Id")) {
    headers.set("X-Guest-Session-Id", getOrCreateGuestSessionId());
  }
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, credentials: "include" });
  if (!res.ok) {
    throw new Error(`guestProfilesFetch ${path} → ${res.status}`);
  }
  return res.json() as Promise<T>;
}

function draftToUpsertBody(draft: GuestProfileDraft) {
  return {
    local_key: "self",
    display_name: draft.first_name || null,
    birth_date: draft.birth_date,
    birth_time: draft.time_unknown ? null : draft.birth_time,
    birth_time_known: !draft.time_unknown && Boolean(draft.birth_time),
    location_name: draft.location_name,
    latitude: draft.latitude,
    longitude: draft.longitude,
    relation: "self",
    is_owner_candidate: true,
    natal_facts: draft.natal_facts ?? null,
  };
}

/** Upsert 1B self draft and/or 1A compat pair onto server. */
export async function syncGuestProfilesToServer(): Promise<void> {
  await ensureServerGuestSession();

  const draft = readGuestProfileDraft();
  if (draft?.birth_date?.trim()) {
    await guestFetch("/guest/profiles", {
      method: "POST",
      body: JSON.stringify(draftToUpsertBody(draft)),
    });
  }

  const pair = readGuestCompatPair();
  if (pair?.person_a?.birth_date && pair?.person_b?.birth_date) {
    await guestFetch("/guest/profiles/compat-pair", {
      method: "POST",
      body: JSON.stringify({
        person_a: {
          label: pair.person_a.label,
          birth_date: pair.person_a.birth_date,
          birth_time: pair.person_a.time_unknown ? null : pair.person_a.birth_time,
          time_unknown: pair.person_a.time_unknown,
          location_name: pair.person_a.location_name,
          latitude: pair.person_a.latitude,
          longitude: pair.person_a.longitude,
        },
        person_b: {
          label: pair.person_b.label,
          birth_date: pair.person_b.birth_date,
          birth_time: pair.person_b.time_unknown ? null : pair.person_b.birth_time,
          time_unknown: pair.person_b.time_unknown,
          location_name: pair.person_b.location_name,
          latitude: pair.person_b.latitude,
          longitude: pair.person_b.longitude,
        },
      }),
    });
  }
}

export async function fetchServerGuestProfiles(): Promise<{
  guest_session_id: string;
  profiles: Array<{ local_key: string; birth_date: string | null; id: number }>;
} | null> {
  try {
    await ensureServerGuestSession();
    return await guestFetch("/guest/profiles", { method: "GET" });
  } catch {
    return null;
  }
}
