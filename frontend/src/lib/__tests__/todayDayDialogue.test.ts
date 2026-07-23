import { buildTodayPromiseSuggestions } from "@/lib/todayDayDialogue";

describe("buildTodayPromiseSuggestions", () => {
  it("offers intentions from contract fields — never canned affirmations", () => {
    const suggestions = buildTodayPromiseSuggestions({
      primaryAction: "Если успеешь, закрой одну задачу до обеда",
      focusTopicId: "work",
      developmentPoint: "Замедлиться и услышать себя",
    });

    expect(suggestions.length).toBeGreaterThanOrEqual(1);
    expect(suggestions.length).toBeLessThanOrEqual(4);
    expect(suggestions[0]?.id).toBe("contract_primary");
    expect(suggestions[0]?.text).toMatch(/закрой одну задачу|успеешь/i);
    expect(suggestions.some((s) => s.id === "development")).toBe(true);
    expect(suggestions.some((s) => /завершу один разговор|перестану торопиться/i.test(s.text))).toBe(
      false,
    );
  });

  it("returns empty when there is no computed action", () => {
    const suggestions = buildTodayPromiseSuggestions({});
    expect(suggestions).toEqual([]);
  });

  it("prefers today_move then primary then growth then do items", () => {
    const suggestions = buildTodayPromiseSuggestions({
      todayMove: "Одна ясная линия до обеда",
      primaryAction: "Закрой задачу",
      developmentPoint: "Замедлиться",
      doItems: ["Напиши список", "Сделай паузу", "Позвони другу"],
    });

    expect(suggestions.map((s) => s.id)).toEqual([
      "today_move",
      "contract_primary",
      "development",
      "do_0",
    ]);
  });
});
