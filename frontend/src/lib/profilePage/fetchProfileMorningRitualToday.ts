import { getJson } from "@/lib/api";
import type { MorningRitualData } from "@/components/today/todayPageUtils";

export function profileTodayIso(): string {
  return new Date().toISOString().split("T")[0];
}

/** Today's celestial anchors — same source as Today (`GET /morning-ritual/today`). */
export async function fetchProfileMorningRitualToday(
  targetDate: string = profileTodayIso(),
): Promise<MorningRitualData | null> {
  try {
    return await getJson<MorningRitualData>(
      `/morning-ritual/today?target_date=${encodeURIComponent(targetDate)}`,
    );
  } catch {
    return null;
  }
}
