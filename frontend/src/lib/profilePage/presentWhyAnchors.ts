/**
 * Present Why anchors for Profile Step 2 UI.
 * Splits fact labels; never invents interpretive prose (Journey Forms §2).
 * Localizes EN sign / ASC / MC tokens to RU for product surface.
 */
import type { ProfileJourneyWhyRow } from "@/lib/profilePage/buildProfileJourneyProjection";
import { zodiacRuName } from "@/lib/zodiacKnowledge";

export type WhyAnchorPresentation = {
  id: string;
  class: string;
  title: string;
  detail: string | null;
  /** Structural role from class — not personality copy. */
  role: "selected" | "influenced";
  /** Primary pillar grid (≤4) vs secondary chips. */
  tier: "primary" | "secondary";
  /**
   * When CE packs claim—fact as «prose — fact», prose moves here so the card
   * title can be the fact (Forms: fact + meaning).
   */
  claimProse?: string | null;
};

const PRIMARY_ORDER = ["archetype_from_life_path", "sun", "moon", "asc"] as const;

const EN_SIGNS = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
] as const;

/** Product RU for kitchen/EN astro tokens in why / grounded labels. */
export function localizeAstroFactLine(text: string): string {
  let out = text.replace(/\s+/g, " ").trim();
  if (!out) return out;
  out = out.replace(/\bASC\b/gi, "Асцендент");
  out = out.replace(/\bMC\b/g, "Середина неба");
  for (const en of EN_SIGNS) {
    const ru = zodiacRuName(en);
    if (!ru || ru === en) continue;
    const prep: Record<string, string> = {
      Овен: "Овне",
      Телец: "Тельце",
      Близнецы: "Близнецах",
      Рак: "Раке",
      Лев: "Льве",
      Дева: "Деве",
      Весы: "Весах",
      Скорпион: "Скорпионе",
      Стрелец: "Стрельце",
      Козерог: "Козероге",
      Водолей: "Водолее",
      Рыбы: "Рыбах",
    };
    const afterV = prep[ru] || ru;
    out = out.replace(new RegExp(`(^|[^\\p{L}])в\\s+${en}(?![\\p{L}])`, "giu"), `$1в ${afterV}`);
    out = out.replace(new RegExp(`(?<![\\p{L}])${en}(?![\\p{L}])`, "giu"), ru);
  }
  return out;
}

function isFactLine(text: string): boolean {
  return /^(солнце|луна|асцендент|середина неба|марс|меркурий|венера|стихия|ритм|число пути)(\s|$|[.—–-])/iu.test(
    text.replace(/\s+/g, " ").trim(),
  );
}

function splitLabel(
  label: string,
  role: WhyAnchorPresentation["role"],
): { title: string; detail: string | null; claimProse: string | null } {
  const raw = localizeAstroFactLine(label);
  if (!raw) return { title: "", detail: null, claimProse: null };
  const parts = raw.split(/\s+[—–-]\s+/);
  if (parts.length >= 2) {
    const left = parts[0]!.trim();
    const right = parts.slice(1).join(" — ").trim();
    // Selected: claim title only — never show sun/ASC as if they chose the name (Forms).
    if (role === "selected" && right && isFactLine(right)) {
      return { title: left || raw, detail: null, claimProse: null };
    }
    // Influenced CE: «Первый контакт… — Асцендент в Водолее» → fact as title, prose as meaning.
    if (
      role === "influenced" &&
      right &&
      isFactLine(right) &&
      left &&
      !isFactLine(left)
    ) {
      return { title: right, detail: null, claimProse: left };
    }
    return { title: left || raw, detail: right || null, claimProse: null };
  }
  return { title: raw, detail: null, claimProse: null };
}

function tierFor(id: string, role: WhyAnchorPresentation["role"]): WhyAnchorPresentation["tier"] {
  if (role === "selected") return "primary";
  const low = id.toLowerCase();
  if ((PRIMARY_ORDER as readonly string[]).includes(id)) return "primary";
  // CE claim ids: treat sun/moon/asc presence as primary pillars.
  if (low.includes(":sun") || low.includes("planet_sign:sun") || low.includes("_sun")) return "primary";
  if (low.includes("moon")) return "primary";
  if (low.includes("_asc") || low.includes("ascendant") || low.includes("presence")) return "primary";
  return "secondary";
}

export function presentWhyAnchors(rows: ProfileJourneyWhyRow[]): {
  primary: WhyAnchorPresentation[];
  secondary: WhyAnchorPresentation[];
} {
  const mapped: WhyAnchorPresentation[] = rows.map((row) => {
    const role: WhyAnchorPresentation["role"] =
      row.class === "selected_by" ? "selected" : "influenced";
    const { title, detail, claimProse } = splitLabel(row.label, role);
    return {
      id: row.id,
      class: row.class,
      title,
      detail,
      claimProse,
      role,
      tier: tierFor(row.id, role),
    };
  });

  const primaryIds = new Set<string>();
  const primary: WhyAnchorPresentation[] = [];

  // Selected_by always leads (what chose the name).
  for (const row of mapped) {
    if (row.role !== "selected") continue;
    if (primary.length >= 4) break;
    primary.push(row);
    primaryIds.add(row.id);
  }

  for (const id of PRIMARY_ORDER) {
    if (primary.length >= 4) break;
    const hit = mapped.find((row) => row.id === id && !primaryIds.has(row.id));
    if (hit) {
      primary.push(hit);
      primaryIds.add(hit.id);
    }
  }

  // Fill remaining with other influenced primaries if still short.
  for (const row of mapped) {
    if (primary.length >= 4) break;
    if (primaryIds.has(row.id)) continue;
    if (row.tier !== "primary") continue;
    primary.push(row);
    primaryIds.add(row.id);
  }

  const secondary = mapped.filter((row) => !primaryIds.has(row.id));
  return { primary, secondary };
}
