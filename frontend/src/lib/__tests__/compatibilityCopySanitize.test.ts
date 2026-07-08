import { filterCompatibilityParagraphs, stripCompatibilityDisplayGarbage } from "@/lib/compatibilityCopySanitize";

describe("compatibilityCopySanitize", () => {
  it("removes standalone hashtag lines", () => {
    const raw = "Нормальный текст\n#Numerology\n#SelfWorth\nЕщё абзац";
    expect(stripCompatibilityDisplayGarbage(raw)).toBe("Нормальный текст Ещё абзац");
  });

  it("filters hashtag-only paragraphs from arrays", () => {
    expect(
      filterCompatibilityParagraphs([
        "Любовная динамика — не один процент.",
        "#HealthyRelationships",
        "#PersonalGrowth",
      ]),
    ).toEqual(["Любовная динамика — не один процент."]);
  });
});
