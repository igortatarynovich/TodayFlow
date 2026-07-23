/**
 * Present Why anchors for Profile Step 2 UI.
 * Splits fact labels; never invents interpretive prose (Journey Forms §2).
 */
import type { ProfileJourneyWhyRow } from "@/lib/profilePage/buildProfileJourneyProjection";

export type WhyAnchorPresentation = {
  id: string;
  class: string;
  title: string;
  detail: string | null;
  /** Structural role from class — not personality copy. */
  role: "selected" | "influenced";
  /** Primary pillar grid (≤4) vs secondary chips. */
  tier: "primary" | "secondary";
};

const PRIMARY_ORDER = ["archetype_from_life_path", "sun", "moon", "asc"] as const;

function splitLabel(label: string): { title: string; detail: string | null } {
  const raw = label.trim();
  if (!raw) return { title: "", detail: null };
  const parts = raw.split(/\s+[—–-]\s+/);
  if (parts.length >= 2) {
    const title = parts[0]!.trim();
    const detail = parts.slice(1).join(" — ").trim();
    return { title: title || raw, detail: detail || null };
  }
  return { title: raw, detail: null };
}

function tierFor(id: string, role: WhyAnchorPresentation["role"]): WhyAnchorPresentation["tier"] {
  if (role === "selected") return "primary";
  if ((PRIMARY_ORDER as readonly string[]).includes(id)) return "primary";
  return "secondary";
}

export function presentWhyAnchors(rows: ProfileJourneyWhyRow[]): {
  primary: WhyAnchorPresentation[];
  secondary: WhyAnchorPresentation[];
} {
  const mapped: WhyAnchorPresentation[] = rows.map((row) => {
    const role: WhyAnchorPresentation["role"] =
      row.class === "selected_by" ? "selected" : "influenced";
    const { title, detail } = splitLabel(row.label);
    return {
      id: row.id,
      class: row.class,
      title,
      detail,
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
