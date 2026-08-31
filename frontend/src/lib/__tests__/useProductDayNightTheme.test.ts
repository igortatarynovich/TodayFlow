import { resolveProductDayNightTheme } from "@/lib/useProductDayNightTheme";

const APPEARANCE_KEY = "todayflow_appearance_v1";

describe("resolveProductDayNightTheme", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("defaults to light regardless of the clock (appearance is preference, not time)", () => {
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 9, 0, 0))).toBe("light");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 18, 0, 0))).toBe("light");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 3, 0, 0))).toBe("light");
  });

  it("follows the stored appearance mode, not the clock", () => {
    localStorage.setItem(APPEARANCE_KEY, JSON.stringify({ mode: "dark" }));
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 9, 0, 0))).toBe("dark");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 22, 0, 0))).toBe("dark");

    localStorage.setItem(APPEARANCE_KEY, JSON.stringify({ mode: "light" }));
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 22, 0, 0))).toBe("light");
    expect(resolveProductDayNightTheme(new Date(2026, 6, 23, 3, 0, 0))).toBe("light");
  });
});
