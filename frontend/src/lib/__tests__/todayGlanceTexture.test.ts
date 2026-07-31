import type { TodayContractV1 } from "@/lib/todayContract";
import {
  buildGlanceDayTexture,
  buildGlanceThemeEyebrow,
  looksLikeAspectBankWhy,
} from "@/lib/todayGlanceTexture";

const bankWhy =
  "Связь Солнца и Марса описывает, как ты идёшь к цели сразу после искры; это мотор напора и риска. · Связка Луна–Сатурн показывает, как осторожность охраняет уязвимость.";

const base = {
  day_story: {
    interpretation_status: "ready",
    theme: "Сорваться или удержать меру",
    day_scenario: {
      ready: true,
      runtime_sot: true,
      conflict: {
        short_name: "Сорваться или удержать меру",
        why_arose: bankWhy,
        opposing_forces: { a: "сорваться", b: "удержать меру" },
      },
      scenes: [{ sphere: "work", what_happens: "x", role_in_story: "primary" }],
    },
  },
} as unknown as TodayContractV1;

describe("buildGlanceDayTexture", () => {
  it("detects sticky aspect-bank why", () => {
    expect(looksLikeAspectBankWhy(bankWhy)).toBe(true);
  });

  it("prefers opposing_forces over aspect-bank why on Glance", () => {
    const texture = buildGlanceDayTexture(base);
    expect(texture).toContain("сорваться");
    expect(texture).toContain("удержать меру");
    expect(texture).not.toMatch(/Солнца и Марса/i);
  });

  it("uses first sentence of lived why when not aspect-bank", () => {
    const c = {
      ...base,
      day_story: {
        ...base.day_story!,
        day_scenario: {
          ...base.day_story!.day_scenario!,
          conflict: {
            ...base.day_story!.day_scenario!.conflict!,
            why_arose: "День тянет на привычные рельсы. К вечеру давление вырастет.",
          },
        },
      },
    } as TodayContractV1;
    const texture = buildGlanceDayTexture(c);
    expect(texture).toBe("День тянет на привычные рельсы.");
  });

  it("eyebrow stays the short label", () => {
    expect(buildGlanceThemeEyebrow(base)).toBe("Сорваться или удержать меру");
  });
});
