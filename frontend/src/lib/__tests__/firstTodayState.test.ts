import {
  hasCompletedFirstToday,
  isFirstTodayCompleteForOtherDay,
  markFirstTodayCompleted,
  markProfileDepthUnlocked,
  resolveIsFirstDay,
  shouldShowProfileTeaser,
} from "@/lib/firstTodayState";
import { todayDayKey } from "@/lib/onboardingContext";

describe("firstTodayState", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("tracks first today completion", () => {
    expect(hasCompletedFirstToday()).toBe(false);
    markFirstTodayCompleted("2026-06-23");
    expect(hasCompletedFirstToday()).toBe(true);
  });

  it("day-keys completion: same-day reload stays in first-today mode", () => {
    expect(isFirstTodayCompleteForOtherDay(todayDayKey())).toBe(false);
    markFirstTodayCompleted(todayDayKey());
    expect(isFirstTodayCompleteForOtherDay(todayDayKey())).toBe(false);
  });

  it("day-keys completion: a different day ends first-today mode", () => {
    markFirstTodayCompleted("2026-06-23");
    expect(isFirstTodayCompleteForOtherDay(todayDayKey())).toBe(true);
  });

  it("day-keys completion: legacy record without day_key counts as a previous day", () => {
    markFirstTodayCompleted();
    expect(isFirstTodayCompleteForOtherDay(todayDayKey())).toBe(true);
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

  it("stays true on same-day reload after completion", () => {
    markFirstTodayCompleted(todayDayKey());
    expect(resolveIsFirstDay("/today", new URLSearchParams("first=1"))).toBe(true);
  });
});
