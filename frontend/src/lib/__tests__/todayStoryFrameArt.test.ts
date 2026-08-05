import {
  allTodayStoryArtModesDistinct,
  assertTodayStoryArtPoolsDistinct,
  PRAKTIKI_STORY_BANNERS,
  resolvePracticeBanner,
  resolveTodayStoryFrameArt,
  resolveTodayThemeArt,
} from "@/lib/todayStoryFrameArt";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";

describe("todayStoryFrameArt", () => {
  it("uses cosmic wash art for energy, meditation/journal for greeting, praktiki for practice", () => {
    expect(resolveTodayStoryFrameArt("energy", "radiance")).toMatch(
      /\/images\/cosmic\/(moon_wash|celestial_wash|eclipse_wash|nebula)/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal")).toMatch(
      /hero-meditation|journal|Diary/,
    );
    expect(resolveTodayStoryFrameArt("practice", "momentum")).toMatch(/praktiki_banner/);
  });

  it("rotates praktiki banners across days", () => {
    const a = resolvePracticeBanner("clarity", 1);
    const b = resolvePracticeBanner("clarity", 2);
    const c = resolvePracticeBanner("clarity", 3);
    expect(PRAKTIKI_STORY_BANNERS).toContain(a);
    expect(PRAKTIKI_STORY_BANNERS).toContain(b);
    expect(PRAKTIKI_STORY_BANNERS).toContain(c);
    expect(new Set([a, b, c]).size).toBe(3);
  });

  it("never reuses the same path across roles for any mode", () => {
    for (const mode of DAY_VISUAL_MODES) {
      expect(assertTodayStoryArtPoolsDistinct(mode)).toBe(true);
    }
    expect(allTodayStoryArtModesDistinct()).toBe(true);
  });

  it("theme art follows day-atmosphere background seeds", () => {
    expect(resolveTodayThemeArt("clarity")).toBe("/images/backgrounds/5.png");
    expect(resolveTodayThemeArt("flow")).toBe("/images/backgrounds/2.png");
  });
});
