import {
  allTodayStoryArtModesDistinct,
  assertTodayStoryArtPoolsDistinct,
  resolveTodayStoryFrameArt,
  resolveTodayThemeArt,
} from "@/lib/todayStoryFrameArt";
import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";

describe("todayStoryFrameArt", () => {
  it("keeps greeting / energy / practice in distinct pools", () => {
    expect(resolveTodayStoryFrameArt("energy", "radiance")).toMatch(/\/images\/cosmic\//);
    expect(resolveTodayStoryFrameArt("practice", "momentum")).toMatch(
      /praktiki_banner|hero-meditation|journal|Diary/,
    );
    expect(resolveTodayStoryFrameArt("greeting", "flow")).toMatch(
      /day_banner|day_girl|self-discovery|inner_reflection|ritual-entry|night_banner/,
    );
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
