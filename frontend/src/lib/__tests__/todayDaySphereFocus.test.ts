import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodaySphereFocus } from "@/lib/todayDaySphereFocus";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности." },
  personal_growth: { development_point: "Замедлиться." },
  domains: {
    relationships: {
      status: "сегодня в отношениях — слушать",
      opportunity: "глубокие разговоры",
      risk: "конфликты и спешка",
      action: "Напиши близкому.",
    },
    money_work: {
      status: "сегодня в работе — ясность",
      opportunity: "планирование и закрытие задач",
      risk: "импulsive решения",
      action: "Одна задача.",
    },
    family: {
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
        relationships: {
          ...baseContract.domains.relationships,
          evidence_status: "absent",
          status: "",
          opportunity: "",
          risk: "",
          action: "",
        },
        money_work: {
          ...baseContract.domains.money_work,
          evidence_status: "present",
        },
        family: {
          ...baseContract.domains.family,
          evidence_status: "absent",
          status: "",
          opportunity: "",
          risk: "",
          action: "",
        },
      },
    };
    const focus = buildTodaySphereFocus(contract);
    expect(focus.cards.every((c) => c.id.includes("money_work"))).toBe(true);
    expect(focus.cards.some((c) => /relationships|family/.test(c.id))).toBe(false);
  });
});
