import {
  PRACTICE_FORMAT_IDS,
  PRACTICE_NEED_IDS,
  inferPracticeFormat,
  practiceCardTitle,
  practiceFormatLabel,
  practiceMatchesFormat,
  practiceMatchesNeed,
  practiceNeedLabel,
  rankPracticesForNeed,
} from "@/lib/practicesPage/practicesCanon";

describe("practicesCanon", () => {
  it("locks six needs with sleep last", () => {
    expect(PRACTICE_NEED_IDS).toEqual([
      "calm",
      "focus",
      "recover",
      "body",
      "understand",
      "sleep",
    ]);
    expect(practiceNeedLabel("ru", "body")).toBe("Почувствовать тело");
    expect(practiceNeedLabel("ru", "understand")).toBe("Понять себя");
    expect(practiceNeedLabel("ru", "sleep")).toBe("Уснуть");
  });

  it("locks nine formats including yoga stretch music reflection sleep", () => {
    expect(PRACTICE_FORMAT_IDS).toEqual([
      "meditation",
      "breath",
      "yoga",
      "stretch",
      "visualization",
      "affirmation",
      "reflection",
      "music",
      "sleep",
    ]);
    expect(practiceFormatLabel("ru", "yoga")).toBe("Йога");
    expect(practiceFormatLabel("ru", "music")).toBe("Музыка");
  });

  it("matches needs and formats by keywords / backend category", () => {
    expect(
      practiceMatchesNeed(
        { title: "Мягкая растяжка", description: "Вернуть тело", category: "ritual", tags: [] },
        "body",
      ),
    ).toBe(true);
    expect(
      practiceMatchesFormat(
        { title: "Box breathing", description: "", category: "breathing", tags: [] },
        "breath",
      ),
    ).toBe(true);
    expect(inferPracticeFormat({ title: "Дневник ясности", category: "reflection", tags: [] })).toBe(
      "reflection",
    );
  });

  it("prefers need_ids and format_id tags over keywords", () => {
    const tagged = {
      title: "Капалабхати",
      description: "энергия",
      category: "breathing",
      tags: ["энергия"],
      need_ids: ["recover", "focus"],
      format_id: "breath",
      outcome_label: "Пробудить ясность",
    };
    expect(practiceMatchesNeed(tagged, "recover")).toBe(true);
    expect(practiceMatchesNeed(tagged, "calm")).toBe(false);
    expect(practiceMatchesFormat(tagged, "breath")).toBe(true);
    expect(practiceMatchesFormat(tagged, "meditation")).toBe(false);
    expect(inferPracticeFormat(tagged)).toBe("breath");
    expect(practiceCardTitle(tagged)).toBe("Пробудить ясность");
  });

  it("ranks practices with primary need first", () => {
    const pool = [
      { title: "A", need_ids: ["focus", "calm"] },
      { title: "B", need_ids: ["calm"] },
      { title: "C", need_ids: ["sleep", "calm"] },
      { title: "D", description: "спокойствие" },
    ] as Array<{ title: string; need_ids?: string[]; description?: string }>;
    const ranked = rankPracticesForNeed(pool, "calm");
    expect(ranked[0].title).toBe("B");
    expect(ranked.map((p) => p.title).slice(0, 3)).toEqual(["B", "A", "C"]);
  });

  it("practiceCardTitle falls back to title", () => {
    expect(practiceCardTitle({ title: "Дыхание 4-7-8" })).toBe("Дыхание 4-7-8");
    expect(practiceCardTitle({ title: "X", outcome_label: "  Снизить тревожность  " })).toBe(
      "Снизить тревожность",
    );
  });
});
