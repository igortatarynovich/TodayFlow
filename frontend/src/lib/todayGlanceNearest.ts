/**
 * Pick the single nearest glance mark for Glance-first ScreenFlow step 0.
 */

import {
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";

function parseGlanceTimeMs(timeLocal: string, now: Date): number | null {
  const raw = (timeLocal || "").trim();
  if (!raw) return null;
  try {
    const parsed = new Date(raw);
    if (!Number.isNaN(parsed.getTime())) return parsed.getTime();
  } catch {
    /* fall through */
  }
  const m = raw.match(/T(\d{2}):(\d{2})/) || raw.match(/^(\d{1,2}):(\d{2})$/);
  if (m) {
    const d = new Date(now);
    d.setHours(Number(m[1]), Number(m[2]), 0, 0);
    return d.getTime();
  }
  return null;
}

export function pickNearestGlanceItem(
  items: GlanceTimelineItem[],
  now: Date = new Date(),
): GlanceTimelineItem | null {
  if (!items.length) return null;
  const live = items.find((row) => isGlanceLiveNow(row.time_local, now));
  if (live) return live;

  let best: GlanceTimelineItem | null = null;
  let bestAbs = Number.POSITIVE_INFINITY;
  for (const row of items) {
    const t = parseGlanceTimeMs(row.time_local, now);
    if (t == null) continue;
    const abs = Math.abs(t - now.getTime());
    if (abs < bestAbs) {
      bestAbs = abs;
      best = row;
    }
  }
  return best ?? items[0] ?? null;
}

export { formatGlanceClock, isGlanceLiveNow };
