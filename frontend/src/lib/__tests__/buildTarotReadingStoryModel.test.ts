import type { GuidanceReadingResult } from "@/components/guidance/GuidanceStructuredResult";
import { buildTarotReadingStoryFromGuidance, buildTarotReadingStoryFromSpread } from "@/lib/buildTarotReadingStoryModel";
import { humanizeTarotPositionLabel, sanitizeTarotStoryText } from "@/lib/tarotReadingStorySanitize";

function baseGuidanceResult(overrides: Partial<GuidanceReadingResult> = {}): GuidanceReadingResult {
  return {
    generation_log_id: 42,
    question: "Может ли он мне дать то, что я хочу?",
    spread_id: "sexual_dynamic_5",
    lane: "love",
    lane_title: "Сексуальная динамика",
    profile_ready: true,
    answer: {
      clarity: "Краткий ответ.",
      explanation: "Этот расклад больше говорит о напряжении между желанием и свободой.",
      forecast: "Здесь есть притяжение, но вместе с ним — страх снова попасть в старый сценарий.",
      decision: "Для тебя здесь особенно важна ясность.",
      today: "Сегодня ориентируйся на честный разговор с собой.",
    },
    suggested_route: { href: "/journal", label: "Сохранить вывод", reason: "Зафиксировать мысль" },
    tarot_cards: [
      {
        name: "The Tower",
        orientation: "upright",
        position: "tension",
        position_id: "tension",
        position_prompt: "Что тебя тянет",
        meaning: "Справочное значение: резкий внутренний сдвиг.",
        card_id: 16,
      },
      {
        name: "The Lovers",
        orientation: "upright",
        position: "obstacle",
        position_id: "obstacle",
        position_prompt: "Что останавливает",
        meaning: "Здесь важен выбор и последствия.",
        card_id: 6,
      },
    ],
    interpretation: {
      summary: "Этот расклад больше говорит не о страсти, а о напряжении между желанием и внутренней свободой.",
      core_insight: "Здесь есть притяжение, но вместе с ним — страх снова попасть в старый сценарий.",
      profile_bridge: "Когда ситуация становится эмоционально липкой, ты можешь уходить в анализ вместо прямого признания.",
      action: "Сформулируй один честный вопрос себе.",
      avoid: "Не делай: не превращать разбор в предсказание. Это тормоз, а не повод для стыда.",
      continue_hint: "На сервере не больше одного уточнения.",
      why_outline: "Напряжение видно в позиции tension. Профиль подстраивает темп.",
      position_weights_note: "Позиции с большим весом сильнее влияют на итог.",
    },
    ...overrides,
  };
}

describe("tarotReadingStorySanitize", () => {
  it("removes banned technical phrases", () => {
    const cleaned = sanitizeTarotStoryText(
      "Справочное значение аркана. Это тормоз. Профиль подстраивает темп. Сегодня ориентируйся на контроль.",
    );
    expect(cleaned).not.toMatch(/справочное значение/i);
    expect(cleaned).not.toMatch(/тормоз/i);
    expect(cleaned).not.toMatch(/подстраивает темп/i);
    expect(cleaned).not.toMatch(/Сегодня ориентируйся/i);
  });

  it("humanizes position ids into story labels", () => {
    expect(humanizeTarotPositionLabel("tension", "tension", null, "ru")).toBe("Где напряжение");
    expect(humanizeTarotPositionLabel("position", "obstacle", "Что останавливает", "ru")).toBe("Что останавливает");
  });
});

describe("buildTarotReadingStoryFromSpread", () => {
  it("maps question-first synthesis blocks and routes", () => {
    const model = buildTarotReadingStoryFromSpread({
      question: "Стоит ли менять работу?",
      spreadTitle: "Три карты",
      concernDomain: "work",
      locale: "ru",
      cards: [
        {
          cardId: 16,
          englishName: "The Tower",
          orientation: "upright",
          position: "past",
          meaning: "Старый порядок больше не держится.",
        },
      ],
      reading: {
        meaning: "Похоже, сейчас важнее честный взгляд, чем новое решение.",
        synthesis_why: "Несколько карт складываются в одну линию — остановиться и посмотреть иначе.",
        insight_holding: "Сейчас удерживает страх потерять стабильность.",
        insight_shifting: "Постепенно появляется ясность критериев.",
        insight_attention: "Стоит заметить, как прошлые решения влияют на сегодня.",
        today_suggestion: "Сегодня зафиксируй один честный критерий для работы.",
        follow_up_prompt: "Что тебе сейчас хочется больше?",
        follow_up_chips: [
          { id: "clarity", label: "Стало понятнее" },
          { id: "same", label: "Пока без изменений" },
        ],
        card_insights: [
          {
            position_label: "Прошлое",
            card_name_ru: "Башня",
            card_id: 16,
            orientation: "upright",
            line: "Старый порядок больше не держится — и это не про деньги, а про то, как ты держишь контроль.",
          },
        ],
      },
    });

    expect(model.mainAnswer).toContain("честный взгляд");
    expect(model.storyNarrative).toContain("одну линию");
    expect(model.cardInsights).toHaveLength(1);
    expect(model.cardInsights[0].cardNameRu).toBe("Башня");
    expect(model.cardInsights[0].line).toContain("контроль");
    expect(model.insights.holding).toContain("удерживает");
    expect(model.todaySuggestion).toContain("критерий");
    expect(model.followUpChips).toHaveLength(2);
    expect(model.actions.some((a) => a.id === "today")).toBe(true);
    expect(model.actions.some((a) => a.id === "goal")).toBe(true);
  });
});

describe("buildTarotReadingStoryFromGuidance", () => {
  it("builds question-first story model without card encyclopedia fields", () => {
    const model = buildTarotReadingStoryFromGuidance(baseGuidanceResult(), "ru", {
      clarifyAvailable: true,
      showCompatibility: true,
    });

    expect(model.question).toContain("Может ли он");
    expect(model.mainAnswer).toMatch(/напряжении между желанием/);
    expect(model.mainAnswer).not.toMatch(/Сегодня ориентируйся/i);
    expect(model.cardInsights).toHaveLength(2);
    expect(model.cardInsights[0].cardNameRu).toMatch(/Башня/);
    expect(model.insights.holding).toMatch(/притяжение/);
    expect(model.todaySuggestion).toMatch(/честный разговор/);
    expect(model.followUpChips.length).toBeGreaterThan(2);
    expect(model.actions.map((a) => a.id)).toEqual(["clarify", "save", "compatibility"]);
  });
});
