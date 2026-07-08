import { buildTodayPromiseSuggestions } from "@/lib/todayDayDialogue";

describe("buildTodayPromiseSuggestions", () => {
  it("prefers human static chips first, then focus when room", () => {
    const suggestions = buildTodayPromiseSuggestions({
      primaryAction: "Закрыть одну задачу до обеда",
      focusTopicId: "work",
      developmentPoint: "Замедлиться и услышать себя",
    });

    expect(suggestions).toHaveLength(3);
    expect(suggestions[0]?.id).toBe("one_talk");
    expect(suggestions[0]?.text).toMatch(/завершу один разговор/i);
    expect(suggestions[1]?.id).toBe("no_rush");
    expect(suggestions[2]?.id).toBe("no_anxious_decisions");
  });

  it("falls back to static chips when contract fields are empty", () => {
    const suggestions = buildTodayPromiseSuggestions({});
    expect(suggestions.length).toBeGreaterThan(0);
    expect(suggestions.length).toBeLessThanOrEqual(3);
  });
});
