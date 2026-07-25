import { resolveDayPhaseHeroWash } from "@/lib/dayPhaseHeroWash";

describe("dayPhaseHeroWash", () => {
  it("never uses the moon plate for morning or day", () => {
    expect(resolveDayPhaseHeroWash("morning").src).not.toContain("moon");
    expect(resolveDayPhaseHeroWash("day").src).not.toContain("moon");
    expect(resolveDayPhaseHeroWash("morning").tone).toBe("light");
    expect(resolveDayPhaseHeroWash("day").tone).toBe("light");
  });

  it("uses moon wash only for evening", () => {
    expect(resolveDayPhaseHeroWash("evening").src).toContain("moon_wash");
    expect(resolveDayPhaseHeroWash("evening").tone).toBe("dark");
  });
});
