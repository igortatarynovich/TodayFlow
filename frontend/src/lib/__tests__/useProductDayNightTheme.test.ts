import { resolveProductDayNightTheme } from "@/lib/useProductDayNightTheme";

describe("resolveProductDayNightTheme", () => {
  it("is light during morning and day hours", () => {
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 9, 0, 0))).toBe("light");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 14, 0, 0))).toBe("light");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 17, 59, 0))).toBe("light");
  });

  it("is dark during evening and late night", () => {
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 18, 0, 0))).toBe("dark");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 22, 0, 0))).toBe("dark");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 3, 0, 0))).toBe("dark");
  });
});
