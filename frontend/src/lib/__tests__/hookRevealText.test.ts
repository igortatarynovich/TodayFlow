import { asTrimmedText, formatColorWhereToUse } from "@/lib/hookRevealText";

describe("hookRevealText", () => {
  it("asTrimmedText only trims strings", () => {
    expect(asTrimmedText("  hello  ")).toBe("hello");
    expect(asTrimmedText("")).toBeNull();
    expect(asTrimmedText(null)).toBeNull();
    expect(asTrimmedText({ clothing: "x" })).toBeNull();
    expect(asTrimmedText(7)).toBeNull();
  });

  it("formatColorWhereToUse joins clothing/accessory object (Igor crash fixture)", () => {
    expect(
      formatColorWhereToUse({
        clothing: "Янтарный шарф или тёплый свитер.",
        accessory: "Украшение медового оттенка.",
        workspace: null,
        makeup: null,
        ui_or_bg: null,
      }),
    ).toBe("Янтарный шарф или тёплый свитер. · Украшение медового оттенка.");
  });

  it("formatColorWhereToUse keeps plain strings", () => {
    expect(formatColorWhereToUse("  один акцент  ")).toBe("один акцент");
  });
});
