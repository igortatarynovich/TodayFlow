/** Safety filters for profile portrait / CUM copy shown in RU UI. */

import { getLocale } from "@/lib/i18n";

const MACHINE_TOKEN_RE =
  /^(?:ritual_mood|ritual_proximity|honest_step|theme|rec-pattern|rec-theme)[:.][a-z0-9_.-]+$/i;
const MACHINE_EMBEDDED_RE =
  /\b(?:ritual_mood|ritual_proximity|honest_step):[a-z0-9_.-]+\b/i;
const KNOWN_MACHINE_SLUGS = new Set([
  "short_focus_sessions",
  "evening_reflection",
  "asks_guidance_questions",
  "completes_today_practices",
  "tarot_deepen_from_today",
  "day_promise_habit",
]);

/** Raw CUM / analytics tokens that must never appear as user-facing copy. */
export function isMachineProfileToken(text: string | null | undefined): boolean {
  const t = (text || "").trim();
  if (!t) return false;
  if (MACHINE_TOKEN_RE.test(t)) return true;
  if (MACHINE_EMBEDDED_RE.test(t)) return true;
  if (KNOWN_MACHINE_SLUGS.has(t.toLowerCase())) return true;
  // snake_case only, no spaces — usually an internal id
  if (/^[a-z][a-z0-9]*(?:_[a-z0-9]+)+$/.test(t) && t.length <= 48) return true;
  return false;
}

/** Heuristic: Latin-heavy prose without Cyrillic → English (or other Latin language). */
export function isMostlyLatinProse(text: string | null | undefined): boolean {
  const t = (text || "").trim();
  if (t.length < 24) return false;
  let latin = 0;
  let cyrillic = 0;
  for (const ch of t) {
    if (/[A-Za-z]/.test(ch)) latin += 1;
    else if (/[А-Яа-яЁё]/.test(ch)) cyrillic += 1;
  }
  const letters = latin + cyrillic;
  if (letters < 16) return false;
  return cyrillic / letters < 0.12 && latin / letters > 0.55;
}

export function isUsableProfileCopy(
  text: string | null | undefined,
  locale: string = getLocale(),
): boolean {
  const t = (text || "").trim();
  if (!t) return false;
  if (isMachineProfileToken(t)) return false;
  if (!locale.toLowerCase().startsWith("en") && isMostlyLatinProse(t)) return false;
  return true;
}

export function filterProfileCopyList(
  items: Array<string | null | undefined>,
  max: number,
  locale: string = getLocale(),
): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const item of items) {
    if (!isUsableProfileCopy(item, locale)) continue;
    const trimmed = item!.trim();
    const key = trimmed.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(trimmed);
    if (out.length >= max) break;
  }
  return out;
}

/** Whether profile_contract_v1 text is safe to show for the active UI locale. */
export function profileContractMatchesLocale(
  contract: { identity_core?: string | null; status?: string | null } | null | undefined,
  locale: string = getLocale(),
): boolean {
  if (!contract) return false;
  const core = (contract.identity_core || "").trim();
  if (!core) return false;
  return isUsableProfileCopy(core, locale);
}
