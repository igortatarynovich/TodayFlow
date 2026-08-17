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

  it("keeps Moon climate, one headline, and optional personal overlay", () => {
    const model = buildTodaySkyStripModel(
      {
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
            title_ru: "Меркурий во Льве — соединение — Юпитер во Льве",
            story_ru: "Меркурий — соединение — Юпитер: разговоры и договорённости легче сдвинуть с места.",
          },
        },
      },
      "тебе обычно проще держать слово, если оно взвешено заранее",
    );
    expect(model?.moonLabel).toBe("Луна в Деве");
    expect(model?.headlineLabel).toContain("соединение");
    expect(model?.sharedStory).toContain("договорённости");
    expect(model?.personalLine).toContain("держать слово");
  });

    it("omits personal overlay when empty", () => {
    const model = buildTodaySkyStripModel({
      ...base,
      sky_today: {
        moon: { body: "moon", body_ru: "Луна", sign: "Virgo", sign_ru: "Дева" },
      },
    });
    expect(model?.personalLine).toBeNull();
    expect(model?.headlineLabel).toBeNull();
    expect(model?.moonWhen).toBeNull();
    expect(model?.headlineWhen).toBeNull();
  });

  it("exposes degree and clock when exact_time_local is present", () => {
    const model = buildTodaySkyStripModel({
      ...base,
      sky_today: {
        moon: {
          body: "moon",
          body_ru: "Луна",
          sign: "Virgo",
          sign_ru: "Дева",
          degree: 28.7,
          exact_time_local: "2026-08-15T03:14:00+03:00",
        },
        headline: {
          id: "sky-mercury-conjunction-jupiter",
          planet_a: "mercury",
          planet_b: "jupiter",
          planet_a_ru: "Меркурий",
          planet_b_ru: "Юпитер",
          aspect: "conjunction",
          aspect_ru: "соединение",
          title_ru: "Меркурий во Льве — соединение — Юпитер во Льве",
          orb_delta: 0.043,
          exact_time_local: "2026-08-15T11:40:00+03:00",
        },
        window: {
          kind: "void_of_course",
          starts_at: "2026-08-15T18:10:00+03:00",
          ends_at: "2026-08-16T03:14:00+03:00",
        },
      },
    });
    expect(model?.moonDegree).toBe("29°");
    expect(model?.moonWhen).toBe("03:14");
    expect(model?.headlineWhen).toBe("11:40");
    expect(model?.headlineOrb).toBe("0°");
    expect(model?.windowLabel).toBe("18:10–03:14");
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
