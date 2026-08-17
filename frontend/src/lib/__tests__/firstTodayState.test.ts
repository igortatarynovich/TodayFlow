import {
  hasCompletedFirstToday,
  markFirstTodayCompleted,
  markProfileDepthUnlocked,
  resolveIsFirstDay,
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

describe("resolveIsFirstDay", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("is false on /today without ?first=1 even if First Today is unmarked", () => {
    expect(resolveIsFirstDay("/today", new URLSearchParams())).toBe(false);
  });

  it("is true only for explicit first=1 before completion", () => {
    expect(resolveIsFirstDay("/today", new URLSearchParams("first=1"))).toBe(true);
    markFirstTodayCompleted("2026-08-17");
    expect(resolveIsFirstDay("/today", new URLSearchParams("first=1"))).toBe(false);
  });
});
