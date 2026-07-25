import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayDayMap } from "@/lib/todayDayMap";

describe("buildTodayDayMap", () => {
  it("maps day_story expect to glance expect and trap to trap — not advantage", () => {
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
        day_thesis: {
          family: "communication",
          variant: "truth_without_filter",
          label_ru: "Прямота без фильтра",
        },
        events_lead: "Меркурий задаёт острый тон разговорам.",
        expect: "Слова вылетают острее обычного: правда ближе к поверхности.",
        trap: "Сказать «как есть» так, что разговор станет судом.",
        direction: "День про короткие договорённости и ясный тон.",
        advantage: "Одно точное сообщение работает лучше объяснений.",
        abstain: "Не раздувать домашние обязательства.",
        today_move: "Напиши одно короткое сообщение до обеда.",
        do: ["Говорить коротко и по существу."],
        avoid: ["Не устраивать разбор полётов при свидетелях."],
        day_foundation: {
          astro: { summary_ru: "Меркурий меняет тон разговоров." },
          lunar: { summary_ru: "Убывающая луна просит отпускать лишнее." },
        },
      },
    } as unknown as TodayContractV1;

    const map = buildTodayDayMap({ contract });
    expect(map?.source).toBe("day_story");
    expect(map?.primaryConflict).toMatch(/Прямота/i);
    expect(map?.whatWorks).toMatch(/острее обычного|правда ближе/i);
    expect(map?.whatWorks).not.toMatch(/точное сообщение/i);
    expect(map?.whereConflict).toMatch(/судом/i);
    expect(map?.whatHappens).toMatch(/Меркурий|острый/i);
    expect(map?.whatHappens).not.toBe(map?.whatWorks);
    expect(map?.oneConcreteMove).toMatch(/Напиши одно/i);
    expect(map?.doHints[0]).toMatch(/коротко/i);
    expect(map?.avoidHints[0]).toMatch(/свидетелях|разбор/i);
  });

  it("prefers day_story over funnel when expect/trap are present", () => {
    const contract = {
      contract_version: "today_contract_v1",
      global_context: { period: "" },
      personal_growth: { development_point: "" },
      domains: {
        relationships: { evidence_status: "absent" },
        money_work: { evidence_status: "absent" },
        family: { evidence_status: "absent" },
      },
      primary_action: "",
      progress: {},
      day_story: {
        contract_version: "day_story_v1",
        day_thesis: { label_ru: "Прямота без фильтра" },
        expect: "Слова вылетают острее обычного.",
        trap: "Сказать правду как суд.",
        events_lead: "Меркурий режет воздух.",
      },
    } as unknown as TodayContractV1;

    const map = buildTodayDayMap({
      contract,
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
    expect(map?.source).toBe("day_story");
    expect(map?.whatWorks).toMatch(/острее/i);
    expect(map?.whereConflict).toMatch(/суд/i);
  });

  it("uses funnel when day_story has no expect/trap", () => {
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
  });
});
