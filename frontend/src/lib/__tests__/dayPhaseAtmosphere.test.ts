import {
  DAY_PHASE_THEME_COLORS,
  dayPhaseFromTimeOfDay,
  pulseDayPhaseRevealFlash,
  resolveDayPhase,
} from "@/lib/dayPhaseAtmosphere";

describe("dayPhaseAtmosphere", () => {
  it("maps clock phases 1:1 except first-day override", () => {
    expect(dayPhaseFromTimeOfDay("morning")).toBe("morning");
    expect(dayPhaseFromTimeOfDay("day")).toBe("day");
    expect(dayPhaseFromTimeOfDay("evening")).toBe("evening");
  });

  it("applies only on /today", () => {
    expect(resolveDayPhase({ pathname: "/profile", timeOfDay: "morning" })).toBeNull();
    expect(resolveDayPhase({ pathname: "/", timeOfDay: "evening" })).toBeNull();
    expect(resolveDayPhase({ pathname: "/today", timeOfDay: "morning" })).toBe("morning");
    expect(resolveDayPhase({ pathname: "/today/flow", timeOfDay: "day" })).toBe("day");
  });

  it("first day wins over clock", () => {
    expect(
      resolveDayPhase({ pathname: "/today", isFirstDay: true, timeOfDay: "evening" }),
    ).toBe("first");
  });

  it("exposes theme colors for all phases", () => {
    expect(DAY_PHASE_THEME_COLORS.morning).toMatch(/^#/);
    expect(DAY_PHASE_THEME_COLORS.evening).toBe("#1a1714");
    expect(DAY_PHASE_THEME_COLORS.first).toMatch(/^#/);
  });

  it("pulseDayPhaseRevealFlash sets and clears data attribute", () => {
    jest.useFakeTimers();
    document.documentElement.removeAttribute("data-day-phase-flash");
    pulseDayPhaseRevealFlash(100);
    expect(document.documentElement.getAttribute("data-day-phase-flash")).toBe("1");
    jest.advanceTimersByTime(100);
    expect(document.documentElement.getAttribute("data-day-phase-flash")).toBeNull();
    jest.useRealTimers();
  });
});
