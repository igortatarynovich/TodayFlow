import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayDayMap } from "@/lib/todayDayMap";

describe("buildTodayDayMap", () => {
  it("maps day_story structured fields into Day Map slots", () => {
    const contract = {
      contract_version: "today_contract_v1",
      global_context: { period: "" },
      personal_growth: { development_point: "" },
      domains: {
        relationships: { evidence_status: "absent" },
        money_work: {
          status: "",
          opportunity: "",
          risk: "Легко пережать сроки на работе.",
          action: "",
          evidence_status: "present",
        },
        family: { evidence_status: "absent" },
      },
      primary_action: "",
      progress: {},
      day_story: {
        contract_version: "day_story_v1",
        direction: "День про короткие договорённости и ясный тон.",
        advantage: "Одно точное сообщение работает лучше объяснений.",
        abstain: "Не раздувать домашние обязательства.",
        today_move: "Напиши одно короткое сообщение до обеда.",
        avoid: ["Длинные разборы на бегу"],
        day_foundation: {
          astro: { summary_ru: "Меркурий меняет тон разговоров." },
          lunar: { summary_ru: "Убывающая луна просит отпускать лишнее." },
        },
      },
    } as unknown as TodayContractV1;

    const map = buildTodayDayMap({ contract });
    expect(map?.source).toBe("day_story");
    expect(map?.whatHappens).toMatch(/короткие договорённости/i);
    expect(map?.whatWorks).toMatch(/точное сообщение/i);
    expect(map?.whereConflict).toMatch(/домашние/i);
    expect(map?.whereYouBreak).toMatch(/пережать|сроки/i);
    expect(map?.oneConcreteMove).toMatch(/Напиши одно/i);
    expect(map?.whyLayers.length).toBeGreaterThanOrEqual(1);
    expect(map?.avoidHints[0]).toMatch(/Длинные разборы/i);
  });

  it("prefers funnel_interpretation when present on guide payload", () => {
    const map = buildTodayDayMap({
      contract: null,
      guideNarrativePayload: {
        contract_version: "guide_funnel_interpretation_v0",
        what_happens: "День складывается из коротких контактов и мягкого темпа.",
        where_conflict: "Натяжение между скоростью и точностью.",
        where_you_break: "Легко сорваться на длинный разбор.",
        what_works: "Одна ясная фраза до обеда.",
        one_concrete_move: "Отправь одно сообщение без оправданий.",
        why_layers: ["Луна просит паузу.", "Меркурий в чувствительном знаке.", "Число дня держит ритм."],
        avoid_hints: ["Не устраивать длинный разбор", "Не обещать больше, чем успеешь", "Не давить на ответ"],
      },
    });
    expect(map?.source).toBe("funnel_interpretation");
    expect(map?.whatHappens).toMatch(/коротких контактов/i);
    expect(map?.oneConcreteMove).toMatch(/Отправь одно/i);
    expect(map?.whyLayers).toHaveLength(3);
    expect(map?.avoidHints).toHaveLength(3);
  });
});
