import { isAppProductRoute } from "@/lib/sectionAtmosphere";
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
});
