import { buildGlanceEnergyFromChorus } from "@/lib/todayGlanceEnergy";
import type { TodayContractV1 } from "@/lib/todayContract";

describe("buildGlanceEnergyFromChorus", () => {
  it("builds effect + cause from interpretive_chorus", () => {
    const contract = {
      day_story: {
        interpretive_chorus: {
          astrology_lead: "Убывающая луна снижает запас сил.",
          astrology_meaning: "Тело просит паузы и короткий шаг.",
        },
      },
    } as unknown as TodayContractV1;
    const line = buildGlanceEnergyFromChorus(contract);
    expect(line?.effect).toMatch(/тело просит паузы/i);
    expect(line?.cause).toMatch(/убывающая луна/i);
    expect(line?.line).toContain("·");
  });

  it("returns null without usable chorus effect", () => {
    expect(buildGlanceEnergyFromChorus({} as TodayContractV1)).toBeNull();
  });
});
