import {
  isRuAbstractTopicHeadline,
  replaceQuotedEnSlugsForRuDisplay,
  stripLlmMetaCommentary,
} from "@/components/today/ritualCueSanitizer";

describe("stripLlmMetaCommentary (O10)", () => {
  it("removes meta sentences and keeps guidance", () => {
    const raw =
      "Коротко: держи один фокус. Карта и число остаются в сводке — я не дублирую их большими блоками. " +
      "Дальше — один шаг без распыления.";
    const out = stripLlmMetaCommentary(raw);
    expect(out.toLowerCase()).not.toContain("не дублиру");
    expect(out.toLowerCase()).not.toContain("карта и число остаются");
    expect(out.toLowerCase()).toContain("один шаг");
  });

  it("strips English meta about duplication", () => {
    const raw = "Breathe evenly. To avoid duplication, I skip the chart. Take one small step.";
    const out = stripLlmMetaCommentary(raw);
    expect(out.toLowerCase()).not.toContain("avoid duplication");
    expect(out.toLowerCase()).toContain("step");
  });
});

describe("replaceQuotedEnSlugsForRuDisplay (O5)", () => {
  it("replaces quoted mood slug", () => {
    const out = replaceQuotedEnSlugsForRuDisplay("Настроение «tired» — мягче.");
    expect(out.toLowerCase()).not.toContain("tired");
    expect(out).toContain("устало");
  });

  it("replaces quoted topic slug", () => {
    const out = replaceQuotedEnSlugsForRuDisplay("Тема 'general' на сегодня.");
    expect(out.toLowerCase()).not.toContain("general");
    expect(out).toContain("общий фон дня");
  });
});

describe("isRuAbstractTopicHeadline (O3)", () => {
  it("flags rubric-only titles", () => {
    expect(isRuAbstractTopicHeadline("Картина дня")).toBe(true);
    expect(isRuAbstractTopicHeadline("Один завершённый шаг до обеда")).toBe(false);
  });
});
