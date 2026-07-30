import { pickNearestGlanceItem } from "@/lib/todayGlanceNearest";
import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";

describe("pickNearestGlanceItem", () => {
  const items: GlanceTimelineItem[] = [
    { time_local: "2026-07-30T09:00:00", label_short: "утро", valence: "favorable", driver_id: "a" },
    { time_local: "2026-07-30T14:00:00", label_short: "день", valence: "caution", driver_id: "b" },
    { time_local: "2026-07-30T20:00:00", label_short: "вечер", valence: "favorable", driver_id: "c" },
  ];

  it("picks closest absolute time", () => {
    expect(pickNearestGlanceItem(items, new Date("2026-07-30T13:50:00"))?.driver_id).toBe("b");
  });

  it("returns null for empty", () => {
    expect(pickNearestGlanceItem([], new Date())).toBeNull();
  });
});
