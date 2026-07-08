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
    expect(focus.neutralNote).toMatch(/нейтральн/i);
  });

  it("does not duplicate domain between peak cards", () => {
    const focus = buildTodaySphereFocus(baseContract);
    const peaks = focus.cards.filter((c) => c.role === "peak");
    const ids = peaks.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
