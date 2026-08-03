import type { TodayContractV1 } from "@/lib/todayContract";
import {
  TODAY_NO_SHARP_FOCUS_COPY,
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
        thesis: { mode: "stability", family: "pressure" },
      },
      scenes: [{ sphere: "work", what_happens: "x", role_in_story: "primary" }],
    },
  },
} as unknown as TodayContractV1;

describe("buildGlanceDayTexture", () => {
  it("detects sticky aspect-bank why", () => {
    expect(looksLikeAspectBankWhy(bankWhy)).toBe(true);
  });

  it("uses thesis.mode tone — not opposing_forces A|B seed", () => {
    const texture = buildGlanceDayTexture(base);
    expect(texture).toMatch(/ровный темп/i);
    expect(texture).not.toContain("сорваться");
    expect(texture).not.toMatch(/Солнца и Марса/i);
  });

  it("uses lived short why when mode missing and why is feel-language", () => {
    const c = {
      ...base,
      day_story: {
        ...base.day_story!,
        day_scenario: {
          ...base.day_story!.day_scenario!,
          conflict: {
            short_name: "День",
            why_arose: "День тянет на привычные рельсы. К вечеру давление вырастет.",
            opposing_forces: { a: "", b: "" },
            thesis: { mode: "", family: "momentum" },
          },
        },
      },
    } as TodayContractV1;
    const texture = buildGlanceDayTexture(c);
    expect(texture).toBe("День тянет на привычные рельсы.");
  });

  it("hides binary dramaturgy from eyebrow on stability", () => {
    expect(buildGlanceThemeEyebrow(base)).toBeNull();
  });

  it("exports shared no-focus copy", () => {
    expect(TODAY_NO_SHARP_FOCUS_COPY).toMatch(/без острого фокуса/i);
  });
});
