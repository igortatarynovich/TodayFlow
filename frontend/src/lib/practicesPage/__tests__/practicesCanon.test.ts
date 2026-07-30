import {
  PRACTICE_FORMAT_IDS,
  PRACTICE_NEED_IDS,
  inferPracticeFormat,
  practiceFormatLabel,
  practiceMatchesFormat,
  practiceMatchesNeed,
  practiceNeedLabel,
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
});
