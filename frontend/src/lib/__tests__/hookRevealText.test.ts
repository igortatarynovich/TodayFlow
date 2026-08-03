import { asTrimmedText, formatColorWhereToUse } from "@/lib/hookRevealText";

describe("hookRevealText", () => {
  it("asTrimmedText only trims strings", () => {
    expect(asTrimmedText("  hello  ")).toBe("hello");
    expect(asTrimmedText("")).toBeNull();
    expect(asTrimmedText(null)).toBeNull();
    expect(asTrimmedText({ clothing: "x" })).toBeNull();
    expect(asTrimmedText(7)).toBeNull();
  });

  it("formatColorWhereToUse picks one tip — clothing first, no mash", () => {
    expect(
      formatColorWhereToUse({
        clothing: "Янтарный шарф или тёплый свитер.",
        accessory: "Украшение медового оттенка.",
        workspace: null,
        makeup: null,
        ui_or_bg: null,
      }),
    ).toBe("Янтарный шарф или тёплый свитер.");
  });

  it("formatColorWhereToUse falls back to accessory when clothing empty", () => {
    expect(
      formatColorWhereToUse({
        clothing: null,
        accessory: "Тонкий браслет.",
        workspace: "Стикер на приоритете.",
      }),
    ).toBe("Тонкий браслет.");
  });

  it("formatColorWhereToUse keeps plain strings", () => {
    expect(formatColorWhereToUse("  один акцент  ")).toBe("один акцент");
  });
});
