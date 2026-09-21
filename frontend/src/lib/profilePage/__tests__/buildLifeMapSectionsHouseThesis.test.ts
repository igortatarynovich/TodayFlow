import { buildLifeMapSections } from "@/lib/profilePage/buildProfilePlanetaryData";
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

  it("omits unoccupied angular houses instead of encyclopedia fallback", () => {
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
    expect(sections.find((s) => s.house === 4)).toBeUndefined();
    expect(sections.every((s) => !/natal interpretation/i.test(s.summary))).toBe(true);
  });
});
