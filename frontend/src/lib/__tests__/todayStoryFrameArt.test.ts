import { resolveTodayStoryFrameArt, resolveTodayThemeArt } from "@/lib/todayStoryFrameArt";

describe("todayStoryFrameArt", () => {
  it("maps greeting / energy / practice to existing public assets", () => {
    expect(resolveTodayStoryFrameArt("greeting", "clarity")).toMatch(/\/images\//);
    expect(resolveTodayStoryFrameArt("energy", "radiance")).toBe("/images/cosmic/moon_orb.webp");
    expect(resolveTodayStoryFrameArt("practice", "momentum")).toBe(
      "/images/today-ritual-entry/default-evening.webp",
    );
  });

  it("theme art follows day-atmosphere background seeds", () => {
    expect(resolveTodayThemeArt("clarity")).toBe("/images/backgrounds/5.png");
    expect(resolveTodayThemeArt("flow")).toBe("/images/backgrounds/2.png");
  });
});
