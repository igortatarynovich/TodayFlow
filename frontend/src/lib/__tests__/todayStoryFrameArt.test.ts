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
  it("uses dedicated phase greeting backgrounds and cosmic wash for energy", () => {
    expect(resolveTodayStoryFrameArt("energy", "radiance")).toMatch(
      /\/images\/cosmic\/(moon_wash|celestial_wash|eclipse_wash|nebula)/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "morning")).toBe(
      "/images/backgrounds/greetings/greetings_morning.png",
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "day")).toBe(
      "/images/backgrounds/greetings/greetings_day.png",
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "evening")).toBe(
      "/images/backgrounds/greetings/greetings_evening.png",
    );
    expect(resolveTodayStoryFrameArt("greeting", "renewal", "night")).toBe(
      "/images/backgrounds/greetings/greetings_evening.png",
    );
    expect(resolveTodayStoryFrameArt("practice", "momentum")).toMatch(/praktiki_banner/);
  });

  it("maps each phase to its greeting pack asset", () => {
    expect(resolveGreetingArt("morning")).toContain("greetings_morning");
    expect(resolveGreetingArt("day")).toContain("greetings_day");
    expect(resolveGreetingArt("evening")).toContain("greetings_evening");
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
