import {
  DAY_PHASE_THEME_COLORS,
  dayPhaseFromHour,
  dayPhaseFromTimeOfDay,
  pulseDayPhaseRevealFlash,
  resolveDayPhase,
} from "@/lib/dayPhaseAtmosphere";

describe("dayPhaseAtmosphere", () => {
  it("maps hours to morning/day/evening/night", () => {
    expect(dayPhaseFromHour(7)).toBe("morning");
    expect(dayPhaseFromHour(14)).toBe("day");
    expect(dayPhaseFromHour(19)).toBe("evening");
    expect(dayPhaseFromHour(23)).toBe("night");
    expect(dayPhaseFromHour(2)).toBe("night");
  });

  it("maps legacy clock phases 1:1", () => {
    expect(dayPhaseFromTimeOfDay("morning")).toBe("morning");
    expect(dayPhaseFromTimeOfDay("day")).toBe("day");
    expect(dayPhaseFromTimeOfDay("evening")).toBe("evening");
  });

  it("applies only on /today", () => {
    expect(resolveDayPhase({ pathname: "/profile", hour: 8 })).toBeNull();
    expect(resolveDayPhase({ pathname: "/", hour: 20 })).toBeNull();
    expect(resolveDayPhase({ pathname: "/today", hour: 8 })).toBe("morning");
    expect(resolveDayPhase({ pathname: "/today/flow", hour: 14 })).toBe("day");
  });

  it("first day wins over clock", () => {
    expect(resolveDayPhase({ pathname: "/today", isFirstDay: true, hour: 20 })).toBe("first");
  });

  it("ignores mood — day-phase follows clock only", () => {
    expect(
      resolveDayPhase({
        pathname: "/today",
        hour: 14,
        mood: "night",
      }),
    ).toBe("day");
    expect(
      resolveDayPhase({
        pathname: "/today",
        isFirstDay: true,
        hour: 14,
        mood: "night",
      }),
    ).toBe("first");
  });

  it("exposes theme colors for all phases", () => {
    expect(DAY_PHASE_THEME_COLORS.morning).toMatch(/^#/);
    expect(DAY_PHASE_THEME_COLORS.evening).toBe("#1a1714");
    expect(DAY_PHASE_THEME_COLORS.night).toMatch(/^#/);
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
