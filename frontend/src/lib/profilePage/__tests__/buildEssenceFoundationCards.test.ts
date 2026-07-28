import { buildEssenceFoundationCards } from "@/lib/profilePage/buildEssenceFoundationCards";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";

describe("buildEssenceFoundationCards", () => {
  const natal = {
    positions: {
      sun: { sign: "Aquarius", house: 8 },
      moon: { sign: "Libra", house: 4 },
      mc: { sign: "Pisces" },
    },
    houses: [
      { house: 1, sign: "Cancer" },
      { house: 10, sign: "Pisces" },
    ],
    ascendant: { sign: "Cancer", longitude: 114 },
  } as NatalChartPreview;

  it("uses RU facts and life-path meaning instead of empty English dumps", () => {
    const cards = buildEssenceFoundationCards({
      natalPreview: natal,
      numerology: { life_path: 7, birth_date: "1990-02-13" },
      frameworkCards: [
        {
          id: "sun",
          title: "Солнце",
          anchor: "в Водолее",
          body: "Ты проявляешь себя через независимость и системный взгляд.",
        },
      ],
      refYear: 2026,
    });

    const sun = cards.find((c) => c.id === "sun");
    expect(sun?.fact).toMatch(/Водолей/);
    expect(sun?.fact).toMatch(/8 дом/);
    expect(sun?.fact).not.toMatch(/Aquarius/);
    expect(sun?.meaning).toMatch(/независимость|системн/i);

    const lp = cards.find((c) => c.id === "life_path");
    expect(lp?.fact).toBe("7");
    expect(lp?.meaning).toMatch(/глубин|смысл|понят/i);
    expect(lp?.meaning).not.toMatch(/главный сценарий/i);

    const py = cards.find((c) => c.id === "personal_year");
    expect(py?.fact).toMatch(/2026/);
    expect(py?.meaning.length).toBeGreaterThan(20);
  });

  it("omits ASC/MC when birth time unknown", () => {
    const cards = buildEssenceFoundationCards({
      natalPreview: { ...natal, time_unknown: true },
      numerology: { life_path: 7 },
    });
    expect(cards.find((c) => c.id === "asc")).toBeUndefined();
    expect(cards.find((c) => c.id === "mc")).toBeUndefined();
    expect(cards.find((c) => c.id === "sun")).toBeTruthy();
  });
});
