import { saveDayEngagement } from "@/lib/todayDayEngagement";
import {
  buildProfileMapDayStory,
  buildProfileMapsHeatmapPreview,
  PROFILE_MAPS_HEATMAP_WINDOW_DAYS,
} from "@/lib/profileMapsHeatmapPreview";

describe("profileMapsHeatmapPreview", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("builds three heatmap rows with 35-day windows", () => {
    const model = buildProfileMapsHeatmapPreview("2026-07-03");
    expect(model.rows).toHaveLength(3);
    expect(model.rows[0]?.cells).toHaveLength(PROFILE_MAPS_HEATMAP_WINDOW_DAYS);
    expect(model.hasAnyMarks).toBe(false);
  });

  it("marks mood cells and builds day story on drill-down", () => {
    saveDayEngagement("2026-07-02", {
      morningMoodId: "calm",
      morningMoodCapturedAtMs: Date.parse("2026-07-02T08:00:00.000Z"),
    });

    const model = buildProfileMapsHeatmapPreview("2026-07-03");
    expect(model.hasAnyMarks).toBe(true);
    expect(model.rows[0]?.filledCount).toBeGreaterThan(0);

    const story = buildProfileMapDayStory("mood", "2026-07-02");
    expect(story).toMatch(/2026-07-02|2 июля|July/);
    expect(story).toMatch(/Спокой|Calm|calm/i);
  });
});
