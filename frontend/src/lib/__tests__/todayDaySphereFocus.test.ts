import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodaySphereFocus } from "@/lib/todayDaySphereFocus";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности." },
  personal_growth: { development_point: "Замедлиться." },
  domains: {
    work: {
      status: "сегодня в работе — ясность",
      opportunity: "планирование и закрытие задач",
      risk: "импulsive решения",
      action: "Одна задача.",
    },
    money: {
      status: "сегодня в работе — ясность",
      opportunity: "планирование и закрытие задач",
      risk: "импulsive решения",
      action: "Одна задача.",
    },
    relationships: {
      status: "сегодня в отношениях — слушать",
      opportunity: "глубокие разговоры",
      risk: "конфликты и спешка",
      action: "Напиши близкому.",
    },
    energy: {
      status: "сегодня дома — тишина",
      opportunity: "короткий разговор",
      risk: "перегруз",
      action: "10 минут семье.",
    },
  },
  primary_action: "Одна задача до обеда.",
  progress: {},
  generation_id: "test",
};

describe("buildTodaySphereFocus", () => {
  it("picks 2–3 cards with peak and caution", () => {
    const focus = buildTodaySphereFocus(baseContract);
    expect(focus.cards.length).toBeGreaterThanOrEqual(2);
    expect(focus.cards.length).toBeLessThanOrEqual(3);
    expect(focus.cards.some((c) => c.role === "peak")).toBe(true);
    expect(focus.cards.some((c) => c.role === "caution")).toBe(true);
    expect(focus.neutralNote).toBe("");
    expect(focus.cards.some((c) => /опирайся|сегодня сильнее/i.test(c.body))).toBe(false);
  });

  it("does not duplicate domain between peak cards", () => {
    const focus = buildTodaySphereFocus(baseContract);
    const peaks = focus.cards.filter((c) => c.role === "peak");
    const ids = peaks.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("skips domains marked evidence_status absent", () => {
    const contract: TodayContractV1 = {
      ...baseContract,
      domains: {
        work: {
          ...baseContract.domains.money,
          evidence_status: "present",
        },
        money: {
          ...baseContract.domains.money,
          evidence_status: "present",
        },
        relationships: {
          ...baseContract.domains.relationships,
          evidence_status: "absent",
          status: "",
          opportunity: "",
          risk: "",
          action: "",
        },
        energy: {
          ...baseContract.domains.energy,
          evidence_status: "absent",
          status: "",
          opportunity: "",
          risk: "",
          action: "",
        },
      },
    };
    const focus = buildTodaySphereFocus(contract);
    expect(focus.cards.every((c) => /work|money/.test(c.id))).toBe(true);
    expect(focus.cards.some((c) => /relationships|energy/.test(c.id))).toBe(false);
  });

  it("falls back to day_scenario scenes when domains are empty", () => {
    const contract: TodayContractV1 = {
      ...baseContract,
      domains: {
        work: { status: "", opportunity: "", risk: "", action: "", evidence_status: "absent" },
        money: { status: "", opportunity: "", risk: "", action: "", evidence_status: "absent" },
        relationships: { status: "", opportunity: "", risk: "", action: "", evidence_status: "absent" },
        energy: { status: "", opportunity: "", risk: "", action: "", evidence_status: "absent" },
      },
      day_story: {
        contract_version: "day_story_v1",
        theme: "Точность",
        story: "День коротких решений.",
        day_scenario: {
          scenes: [
            {
              scene_id: "work_peak",
              sphere: "money_work",
              sphere_label_ru: "Работа и деньги",
              role_in_story: "peak",
              opportunity: "Закрыть одну задачу до обеда.",
              trap: "Распыление на мелочи.",
            },
            {
              scene_id: "home_caution",
              sphere: "family",
              sphere_label_ru: "Дом и семья",
              role_in_story: "caution",
              trap: "Лишние обязательства легко перегружают.",
              recommended_action: "Оставь минимум без вины.",
            },
          ],
        },
      },
    };
    const focus = buildTodaySphereFocus(contract);
    expect(focus.cards.some((c) => c.role === "peak" && /работ/i.test(c.sphere))).toBe(true);
    expect(focus.cards.some((c) => c.role === "caution" && /дом|сем/i.test(c.sphere))).toBe(true);
  });
});
