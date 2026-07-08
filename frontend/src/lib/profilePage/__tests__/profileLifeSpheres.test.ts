import { buildProfileLifeSpheresFromChart, buildProfileLifeSpheresFromProfileData, chartHouseNarrativeLine } from "@/lib/profilePage/profileLifeSpheres";
import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";

describe("chartHouseNarrativeLine", () => {
  it("joins theme and description", () => {
    const preview = {
      interpretations: {
        houses: {
          "7": { theme: "Партнёрство", description: "Коротко про близость." },
        },
      },
    } as unknown as NatalChartPreview;
    expect(chartHouseNarrativeLine(preview, 7)).toContain("Партнёрство");
    expect(chartHouseNarrativeLine(preview, 7)).toContain("близость");
  });

  it("returns null when house missing", () => {
    expect(chartHouseNarrativeLine(null, 7)).toBeNull();
  });
});

describe("buildProfileLifeSpheresFromChart", () => {
  it("prefers joined chart slices over API love line when 7th house present", () => {
    const preview = {
      interpretations: {
        houses: {
          "7": { theme: "7 дом", description: "Про отношения из карты." },
        },
      },
    } as unknown as NatalChartPreview;
    const spheres = buildProfileLifeSpheresFromChart({
      preview,
      love: "Текст из API про любовь.",
      career: "",
      money: "",
      family: "",
      sunLine: "",
      moonLine: "Луна: эмоции.",
      venusLine: "Венера: стиль.",
      marsLine: "",
      mercuryLine: "",
      saturnLine: "",
      jupiterLine: "",
      plutoLine: "",
    });
    const love = spheres.find((s) => s.id === "love");
    expect(love?.how).toMatch(/^В отношениях/i);
    expect(love?.how?.toLowerCase()).toContain("про отношения");
    expect(love?.how).not.toContain("Текст из API");
    expect(love?.how).toContain("Венера");
    expect(love?.how).toContain("Луна");
  });

  it("falls back to API when no chart fragments", () => {
    const spheres = buildProfileLifeSpheresFromChart({
      preview: null,
      love: "Только API.",
      career: "",
      money: "",
      family: "",
      sunLine: "",
      moonLine: "",
      venusLine: "",
      marsLine: "",
      mercuryLine: "",
      saturnLine: "",
      jupiterLine: "",
      plutoLine: "",
    });
    expect(spheres.find((s) => s.id === "love")?.how).toMatch(/^В отношениях/i);
  });

  it("uses life_areas.sex when there is no chart slice", () => {
    const apiSex =
      "Отдельный абзац из ядра профиля про секс, желание и темп без штампов — с уважением к границам.";
    const spheres = buildProfileLifeSpheresFromChart({
      preview: null,
      love: "",
      career: "",
      money: "",
      family: "",
      sex: apiSex,
      sunLine: "",
      moonLine: "",
      venusLine: "",
      marsLine: "",
      mercuryLine: "",
      saturnLine: "",
      jupiterLine: "",
      plutoLine: "",
    });
    expect(spheres.find((s) => s.id === "sex")?.how).toMatch(/^В сексе/i);
  });

  it("uses life_areas.body when chart slice and moon fallback are empty", () => {
    const apiBody =
      "Текст про тело и энергию из API: сон, нагрузка и честные сигналы усталости без морали и без крайностей.";
    const spheres = buildProfileLifeSpheresFromChart({
      preview: null,
      love: "",
      career: "",
      money: "",
      family: "",
      body: apiBody,
      sunLine: "",
      moonLine: "",
      venusLine: "",
      marsLine: "",
      mercuryLine: "",
      saturnLine: "",
      jupiterLine: "",
      plutoLine: "",
    });
    expect(spheres.find((s) => s.id === "body")?.how).toMatch(/^Для тела/i);
  });
});

describe("buildProfileLifeSpheresFromProfileData", () => {
  it("maps core life_areas into sphere how lines when chart is empty", () => {
    const spheres = buildProfileLifeSpheresFromProfileData(null, {
      interpretation: {
        life_areas: {
          love: "Тепло и доверие важнее скорости.",
        },
      },
    } as never);
    const love = spheres.find((s) => s.id === "love");
    expect(love?.how).toMatch(/^В отношениях/i);
    expect(love?.how?.toLowerCase()).toContain("тепло и доверие");
  });
});
