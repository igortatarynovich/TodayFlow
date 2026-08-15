import { buildTodaySkyStripModel, positionLabel } from "@/lib/todaySkyToday";
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
  primary_action: "a",
  progress: {},
  generation_id: "g",
};

describe("buildTodaySkyStripModel", () => {
  it("returns null without moon in sign", () => {
    expect(buildTodaySkyStripModel(base)).toBeNull();
    expect(buildTodaySkyStripModel({ ...base, sky_today: { positions: [], aspects: [] } })).toBeNull();
  });

  it("keeps Moon every day and one headline pair", () => {
    const model = buildTodaySkyStripModel({
      ...base,
      sky_today: {
        moon: { body: "moon", body_ru: "Луна", sign: "Virgo", sign_ru: "Дева", degree: 28.7 },
        headline: {
          id: "sky-mercury-conjunction-jupiter",
          planet_a: "mercury",
          planet_b: "jupiter",
          planet_a_ru: "Меркурий",
          planet_b_ru: "Юпитер",
          sign_a_ru: "Лев",
          sign_b_ru: "Лев",
          aspect: "conjunction",
          aspect_ru: "соединение",
          title_ru: "Меркурий в Льве — соединение — Юпитер в Льве",
        },
        positions: [
          { body: "sun", body_ru: "Солнце", sign: "Leo", sign_ru: "Лев", degree: 22.7 },
          { body: "moon", body_ru: "Луна", sign: "Virgo", sign_ru: "Дева", degree: 28.7 },
        ],
        aspects: [],
      },
    });
    expect(model?.moonLabel).toBe("Луна в Деве");
    expect(model?.headlineLabel).toContain("соединение");
    expect(model?.positions).toHaveLength(2);
  });
});

describe("positionLabel", () => {
  it("writes body in sign with degree and Rx", () => {
    expect(
      positionLabel({
        body: "saturn",
        body_ru: "Сатурн",
        sign: "Aries",
        sign_ru: "Овен",
        degree: 14.4,
        retrograde: true,
      }),
    ).toBe("Сатурн в Овне 14° Rx");
  });
});
