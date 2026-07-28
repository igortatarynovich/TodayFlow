import { buildLifeMapSections } from "@/lib/profilePage/buildProfilePlanetaryData";
import { HOUSE_FALLBACK } from "@/components/profile/profileHouseConstants";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";

describe("buildLifeMapSections house theses", () => {
  it("prefers CE how/do over natal interpretation encyclopedia", () => {
    const natalPreview = {
      positions: {},
      houses: [],
      interpretations: {
        houses: {
          7: {
            name: "Партнерство",
            theme: "Тема",
            description:
              "Длинный энциклопедический абзац про седьмой дом, который больше не должен попадать в life map.",
          },
        },
      },
    } as NatalChartPreview;

    const sections = buildLifeMapSections(natalPreview, {
      "7": {
        how: "В союзе тебе важны явные правила двоих.",
        do: "Назови условие до обещания.",
      },
    });
    const h7 = sections.find((s) => s.house === 7);
    expect(h7?.summary).toBe("В союзе тебе важны явные правила двоих.");
    expect(h7?.do).toBe("Назови условие до обещания.");
    expect(h7?.summary).not.toMatch(/энциклопедическ/i);
  });

  it("falls back to short person thesis, not interpretation.description", () => {
    const natalPreview = {
      positions: {},
      houses: [],
      interpretations: {
        houses: {
          4: {
            name: "Дом",
            theme: "Корни",
            description: "Очень длинный natal interpretation dump про четвёртый дом и семью.",
          },
        },
      },
    } as NatalChartPreview;

    const sections = buildLifeMapSections(natalPreview, null);
    const h4 = sections.find((s) => s.house === 4);
    expect(h4?.summary).toBe(HOUSE_FALLBACK[4]);
    expect(h4?.summary).not.toMatch(/natal interpretation/i);
    expect(h4?.summary.length).toBeLessThan(120);
  });
});
