import {
  dynamicsClassFromThesisMode,
  resolveDayPhaseHeroWash,
  resolveHeroChromeTone,
  resolvePlotHeroWash,
} from "@/lib/dayPhaseHeroWash";

describe("dayPhaseHeroWash", () => {
  it("never uses the moon plate for morning or day", () => {
    expect(resolveDayPhaseHeroWash("morning").src).not.toContain("moon");
    expect(resolveDayPhaseHeroWash("day").src).not.toContain("moon");
    expect(resolveDayPhaseHeroWash("morning").plate).toBe("daylight");
    expect(resolveDayPhaseHeroWash("day").plate).toBe("daylight");
  });

  it("uses moon wash for evening and night", () => {
    expect(resolveDayPhaseHeroWash("evening").src).toContain("moon_wash");
    expect(resolveDayPhaseHeroWash("night").src).toContain("moon_wash");
    expect(resolveDayPhaseHeroWash("evening").plate).toBe("night");
  });

  it("dark appearance darkens daylight chrome without swapping the plate", () => {
    const day = resolveDayPhaseHeroWash("day");
    expect(resolveHeroChromeTone(day, "dark")).toBe("dark");
    expect(day.src).toContain("observe");
  });

  it("maps thesis.mode to internal dynamics class", () => {
    expect(dynamicsClassFromThesisMode("stability")).toBe("even");
    expect(dynamicsClassFromThesisMode("recovery")).toBe("dominant");
    expect(dynamicsClassFromThesisMode("opportunity")).toBe("build");
    expect(dynamicsClassFromThesisMode("conflict")).toBe("tension");
  });

  it("even day never picks morning nebula drama", () => {
    const wash = resolvePlotHeroWash("stability", "morning");
    expect(wash.src).not.toContain("nebula");
    expect(wash.src).toContain("observe");
    expect(wash.plate).toBe("daylight");
  });

  it("conflict morning uses dense daylight not moon", () => {
    const wash = resolvePlotHeroWash("conflict", "morning");
    expect(wash.src).not.toContain("moon");
    expect(wash.plate).toBe("daylight");
  });
});
