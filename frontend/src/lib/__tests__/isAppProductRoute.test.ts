import { isAppProductRoute, SECTION_THEME_COLORS } from "@/lib/sectionAtmosphere";
import { usesProductWebAppShell } from "@/lib/productWebShell";

describe("isAppProductRoute", () => {
  it("matches ProductWebAppShell surface", () => {
    for (const path of ["/today", "/profile", "/weekly", "/account/settings", "/challenges", "/tarot"]) {
      expect(isAppProductRoute(path)).toBe(true);
      expect(isAppProductRoute(path)).toBe(usesProductWebAppShell(path));
    }
  });

  it("excludes marketing and auth", () => {
    expect(isAppProductRoute("/")).toBe(false);
    expect(isAppProductRoute("/auth")).toBe(false);
    expect(isAppProductRoute("/pricing")).toBe(false);
    expect(isAppProductRoute("/onboarding/welcome")).toBe(false);
  });

  it("keeps one light chrome color for every product section including tarot", () => {
    expect(SECTION_THEME_COLORS.tarot).toBe(SECTION_THEME_COLORS.default);
    expect(SECTION_THEME_COLORS.tarot).not.toMatch(/^#0/);
    for (const key of ["today", "profile", "compatibility", "practices", "tarot"] as const) {
      expect(SECTION_THEME_COLORS[key].toLowerCase()).not.toBe("#07080c");
    }
  });
});
