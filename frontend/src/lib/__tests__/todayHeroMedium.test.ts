import { buildTodayHeroPillars, buildTodayHeroSymbol } from "@/lib/todayHeroMedium";

describe("todayHeroMedium", () => {
  it("builds sun pillar from core profile", () => {
    const pillars = buildTodayHeroPillars({
      astro: { sun_sign: "Aquarius" },
    } as never);
    expect(pillars).toHaveLength(1);
    expect(pillars[0]?.label).toContain("Солнце");
  });

  it("prefers archetype symbol when seed present", () => {
    const symbol = buildTodayHeroSymbol({
      baseline: { archetype_seed: "Sage" },
    } as never);
    expect(symbol).toBeTruthy();
  });
});
