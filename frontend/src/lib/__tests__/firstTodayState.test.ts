import {
  hasCompletedFirstToday,
  markFirstTodayCompleted,
  markProfileDepthUnlocked,
  shouldShowProfileTeaser,
} from "@/lib/firstTodayState";

describe("firstTodayState", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("tracks first today completion", () => {
    expect(hasCompletedFirstToday()).toBe(false);
    markFirstTodayCompleted("2026-06-23");
    expect(hasCompletedFirstToday()).toBe(true);
  });

  it("shows profile teaser after first today until depth unlock", () => {
    markFirstTodayCompleted();
    expect(shouldShowProfileTeaser()).toBe(true);
    markProfileDepthUnlocked();
    expect(shouldShowProfileTeaser()).toBe(false);
  });
});
