import { buildTodayPromiseSuggestions } from "@/lib/todayDayDialogue";

describe("buildTodayPromiseSuggestions", () => {
  it("offers at most one intention from primary action — never canned affirmations", () => {
    const suggestions = buildTodayPromiseSuggestions({
      primaryAction: "Если успеешь, закрой одну задачу до обеда",
      focusTopicId: "work",
      developmentPoint: "Замедлиться и услышать себя",
    });

    expect(suggestions).toHaveLength(1);
    expect(suggestions[0]?.id).toBe("contract_primary");
    expect(suggestions[0]?.text).toMatch(/закрой одну задачу|успеешь/i);
    expect(suggestions.some((s) => /завершу один разговор|перестану торопиться/i.test(s.text))).toBe(
      false,
    );
  });

  it("returns empty when there is no computed action", () => {
    const suggestions = buildTodayPromiseSuggestions({});
    expect(suggestions).toEqual([]);
  });
});
