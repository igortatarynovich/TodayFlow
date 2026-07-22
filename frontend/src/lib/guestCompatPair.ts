/** Guest durable drafts for 1A personal compatibility (two people). Not URL SoT. */

export const GUEST_COMPAT_PAIR_KEY = "todayflow_guest_compat_pair_v1";

export type GuestCompatPersonDraft = {
  label: string;
  birth_date: string;
  birth_time: string | null;
  time_unknown: boolean;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
};

export type GuestCompatPairDraft = {
  version: 1;
  person_a: GuestCompatPersonDraft;
  person_b: GuestCompatPersonDraft;
  relationship_context: string | null;
  preview_seen_at: string | null;
  save_ready_at: string | null;
  /** After claim — real AstroProfile ids */
  profile_a_id?: number | null;
  profile_b_id?: number | null;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function createEmptyCompatPerson(label: string): GuestCompatPersonDraft {
  return {
    label,
    birth_date: "",
    birth_time: null,
    time_unknown: true,
    location_name: null,
    latitude: null,
    longitude: null,
  };
}

export function readGuestCompatPair(): GuestCompatPairDraft | null {
  if (!isBrowser()) return null;
  try {
    const raw = sessionStorage.getItem(GUEST_COMPAT_PAIR_KEY) || localStorage.getItem(GUEST_COMPAT_PAIR_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as GuestCompatPairDraft;
    if (parsed?.version !== 1 || !parsed.person_a?.birth_date || !parsed.person_b?.birth_date) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeGuestCompatPair(pair: GuestCompatPairDraft): void {
  if (!isBrowser()) return;
  const payload = JSON.stringify(pair);
  sessionStorage.setItem(GUEST_COMPAT_PAIR_KEY, payload);
  // Persist across magic-link navigation (new tab may drop sessionStorage).
  localStorage.setItem(GUEST_COMPAT_PAIR_KEY, payload);
}

export function patchGuestCompatPair(patch: Partial<GuestCompatPairDraft>): GuestCompatPairDraft | null {
  const current = readGuestCompatPair();
  if (!current) return null;
  const next = { ...current, ...patch };
  writeGuestCompatPair(next);
  return next;
}

export function clearGuestCompatPair(): void {
  if (!isBrowser()) return;
  sessionStorage.removeItem(GUEST_COMPAT_PAIR_KEY);
  localStorage.removeItem(GUEST_COMPAT_PAIR_KEY);
}

export function hasGuestCompatPair(): boolean {
  return Boolean(readGuestCompatPair());
}

export function compatPersonLimitations(person: GuestCompatPersonDraft): string[] {
  const missing: string[] = [];
  if (person.time_unknown || !person.birth_time) {
    missing.push("Асцендент", "дома");
  }
  if (!person.location_name?.trim()) {
    if (!missing.includes("дома")) missing.push("дома");
  }
  return missing;
}
