import {
  allTodayStoryArtModesDistinct,
  assertTodayStoryArtPoolsDistinct,
  PRAKTIKI_STORY_BANNERS,
  resolveGreetingArt,
  resolvePracticeBanner,
  resolveTodayStoryFrameArt,
  resolveTodayThemeArt,
} from "@/lib/todayStoryFrameArt";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";

describe("todayStoryFrameArt", () => {
  it("uses phase assets for greeting and cosmic wash for energy", () => {
    expect(resolveTodayStoryFrameArt("energy", "radiance")).toMatch(
      /\/images\/cosmic\/(moon_wash|celestial_wash|eclipse_wash|nebula)/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "morning")).toMatch(
      /today-ritual-entry\/default-morning|hero-meditation/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "day")).toMatch(
      /today-ritual-entry\/default-day|day_girl_banner|journal/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "evening")).toMatch(
      /today-ritual-entry\/default-evening|night_banner|Diary/,
    );
    expect(resolveTodayStoryFrameArt("practice", "momentum")).toMatch(/praktiki_banner/);
  });

  it("rotates greeting art within a phase across days", () => {
    const a = resolveGreetingArt("morning", 1);
    const b = resolveGreetingArt("morning", 2);
    const c = resolveGreetingArt("morning", 3);
    expect([a, b, c].every((p) => p.includes("/images/"))).toBe(true);
    expect(new Set([a, b, c]).size).toBeGreaterThanOrEqual(2);
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

  it("never reuses the same path across roles for any mode × phase", () => {
    for (const mode of DAY_VISUAL_MODES) {
      for (const phase of ["morning", "day", "evening", "night"] as const) {
        expect(assertTodayStoryArtPoolsDistinct(mode, phase)).toBe(true);
      }
    }
    expect(allTodayStoryArtModesDistinct()).toBe(true);
  });

  it("theme art follows day-atmosphere background seeds", () => {
    expect(resolveTodayThemeArt("clarity")).toBe("/images/backgrounds/5.png");
    expect(resolveTodayThemeArt("flow")).toBe("/images/backgrounds/2.png");
  });
});
