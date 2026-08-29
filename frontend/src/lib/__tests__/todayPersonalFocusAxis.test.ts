import { pickPersonalFocusAxisLabel } from "@/lib/todayPersonalFocusAxis";
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

  it("projects primary scene sphere when it is a closed domain id", () => {
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
    ).toBe("Работа");
  });
});
