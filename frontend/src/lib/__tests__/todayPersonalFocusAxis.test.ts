import { pickPersonalFocusAxisId, pickPersonalFocusAxisLabel } from "@/lib/todayPersonalFocusAxis";
import type { TodayContractV1 } from "@/lib/todayContract";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "p" },
  personal_growth: { development_point: "d" },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
};

describe("pickPersonalFocusAxisId", () => {
  it("returns the closed F10 id and omits Global energy or kitchen aliases", () => {
    expect(pickPersonalFocusAxisId(base)).toBeNull();
    expect(
      pickPersonalFocusAxisId({
        ...base,
        global_day: { primary_energy: "radiance" },
        personal_day: { natal_overlay: { focus_axis: "work" } },
      }),
    ).toBe("work");
    expect(
      pickPersonalFocusAxisId({
        ...base,
        global_day: { primary_energy: "clarity" },
      }),
    ).toBeNull();
    expect(
      pickPersonalFocusAxisId({
        ...base,
        personal_day: { natal_overlay: { axis: "work", domain: "money" } },
      }),
    ).toBeNull();
  });
});

describe("pickPersonalFocusAxisLabel", () => {
  it("maps overlay closed-set domain and omits when none", () => {
    expect(pickPersonalFocusAxisLabel(base)).toBeNull();
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        personal_day: { natal_overlay: { focus_axis: "relationships" } },
      }),
    ).toBe("Отношения");
  });

  it("does not invent a free-form title from Global theme or why_personal", () => {
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          theme: "День коротких договорённостей без лишнего шума.",
          day_scenario: {
            conflict: { why_personal: "тебе обычно проще держать слово" },
          },
        },
      }),
    ).toBeNull();
  });

  it("omits Global scene sphere instead of filling T3.focus_title", () => {
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        day_story: {
          contract_version: "day_story_v1",
          day_scenario: {
            primary_scene_id: "s1",
            scenes: [{ scene_id: "s1", sphere: "work" }],
          },
        },
      }),
    ).toBeNull();
  });

  it("does not take meaning from kitchen overlay aliases", () => {
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        personal_day: {
          natal_overlay: {
            axis: "work",
            domain: "money",
            sphere: "relationships",
            primary_sphere: "energy",
            short_name: "Солнечный возврат",
          },
        },
      }),
    ).toBeNull();
  });

  it("does not duplicate K01 human_line or K06 headline", () => {
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        global_day: { primary_energy: "radiance" },
        day_story: {
          contract_version: "day_story_v1",
          day_personal: {
            summary_ru: "Транзит к Луне держит разговор в теле, а не в тексте.",
          },
        },
        personal_day: {
          natal_overlay: {
            focus_axis: "Сияние",
            summary_ru: "Транзит к Луне держит разговор в теле, а не в тексте.",
          },
        },
      }),
    ).toBeNull();
  });

  it("maps energy domain as the 4-set label, not a K01 energy sentence", () => {
    expect(
      pickPersonalFocusAxisLabel({
        ...base,
        global_day: { primary_energy: "radiance" },
        personal_day: { natal_overlay: { focus_axis: "energy" } },
      }),
    ).toBe("Энергия");
  });
});
