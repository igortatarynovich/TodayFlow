import { isLowEnergyRitualMood } from "@/components/today/todayRitualCopy";

describe("isLowEnergyRitualMood", () => {
  it("returns true for tired, heavy, quiet_wish (case/trim)", () => {
    expect(isLowEnergyRitualMood("tired")).toBe(true);
    expect(isLowEnergyRitualMood("  HEAVY ")).toBe(true);
    expect(isLowEnergyRitualMood("quiet_wish")).toBe(true);
  });

  it("returns false for other moods and empty", () => {
    expect(isLowEnergyRitualMood("motivated")).toBe(false);
    expect(isLowEnergyRitualMood(null)).toBe(false);
    expect(isLowEnergyRitualMood(undefined)).toBe(false);
  });
});
