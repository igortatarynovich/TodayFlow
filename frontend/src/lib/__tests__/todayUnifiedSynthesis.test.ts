import { buildTodayUnifiedSynthesis } from "@/lib/todayUnifiedSynthesis";
import { isRuUserFacingText, isGenericRhythmCliche, polishDayHeadline, resolveTodayThemeHeadline } from "@/lib/todaySynthesisTextPolicy";
import type { TodayContractV1 } from "@/lib/todayContract";

const baseContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: {
    period: "Проживать день через устойчивость через понятный ритм и действовать ровно и без суеты.",
  },
  personal_growth: {
    development_point: "Сегодня полезно замечать момент, когда ты начинаешь ускоряться из тревоги.",
  },
  domains: {
    relationships: {
      status: "Сегодня в отношениях — прямой контакт.",
      opportunity: "Прямой разговор снижает напряжение.",
      risk: "Молчание строит дистанцию.",
      action: "Скажи прямо одну вещь, которую обычно обходишь.",
    },
    money_work: {
      status: "Сегодня в работе — один вектор.",
      opportunity: "Один результат до вечера.",
      risk: "Не бери новые обязательства.",
      action: "Выбери одну задачу и доведи её до результата.",
    },
    family: {
      status: "Сегодня дома полезнее спокойный ритм.",
      opportunity: "Тёплое присутствие важнее скорости.",
      risk: "Не тащи контроль на близких.",
      action: "Сделай один бытовой шаг для спокойствия дома.",
    },
  },
  primary_action: "Выбери одну вещь и доведи её до конца.",
  progress: {},
  generation_id: "test",
};

describe("todaySynthesisTextPolicy", () => {
  it("rejects English tarot leak", () => {
    expect(
      isRuUserFacingText("Avoiding the inevitable, prolonged instability, suppressed emotion erupting later."),
    ).toBe(false);
  });

  it("polishes broken headline", () => {
    const h = polishDayHeadline(
      "Проживать день через устойчивость через понятный ритм и действовать ровно",
      "Сегодня полезно замечать момент, когда ты начинаешь ускоряться из тревоги.",
    );
    expect(h).toContain("ритм");
    expect(h).not.toContain("действовать");
    expect(h).not.toContain("устойчивость через понятный ритм");
  });

  it("rejects generic rhythm cliché headline", () => {
    expect(isGenericRhythmCliche("Сегодня день устойчивость через понятный ритм.")).toBe(true);
    expect(
      resolveTodayThemeHeadline({
        ...baseContract,
        global_context: {
          period: "Проживать день через устойчивость через понятный ритм и действовать ровно и без суеты.",
        },
      }),
    ).not.toMatch(/устойчивость через понятный ритм/i);
  });
});

describe("buildTodayUnifiedSynthesis", () => {
  it("weaves Tower with stability theme without English", () => {
    const model = buildTodayUnifiedSynthesis({
      contract: baseContract,
      guidePayload: null,
      tarotMainId: 16,
      numerologyValue: "7",
      numerologyMeaning: "Сегодня ответы приходят через наблюдение, чем через давление.",
      personalObservation: "Башня зовёт в движение, а ты устал — сужай поле",
      mood: "tired",
      dateISO: "2026-06-22",
      eyebrow: "Твой день сегодня",
    });

    expect(model.headline).not.toMatch(/действовать/i);
    expect(model.paragraphs.join(" ")).toMatch(/Башня|перемен/i);
    expect(model.paragraphs.join(" ")).toMatch(/ритм|устойчив|поле внимания/i);
    expect(model.paragraphs.join(" ")).not.toMatch(/Avoiding/i);
    expect(model.eveningPrompt).not.toMatch(/Одна фраза — без отчёта/);
  });

  it("does not expose separate raw ingredient fields", () => {
    const model = buildTodayUnifiedSynthesis({
      contract: baseContract,
      guidePayload: null,
      tarotMainId: 16,
      numerologyValue: "7",
      numerologyMeaning: "Avoiding the inevitable",
      dateISO: "2026-06-22",
      eyebrow: "Твой день",
    });
    expect(model.paragraphs.every((p) => isRuUserFacingText(p))).toBe(true);
  });
});
