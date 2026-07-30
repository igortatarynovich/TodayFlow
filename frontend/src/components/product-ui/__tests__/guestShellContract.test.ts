import {
  APP_NAV_GUEST_PRODUCT_ORDER,
  buildAppNavItems,
} from "@/lib/appNavConfig";

/**
 * Documents the ProductWebAppShell guest chrome contract:
 * guest = not authenticated (including auth still loading / SSR).
 * Do not gate on authLoading — that baked «Путник» + full nav into HTML.
 */
describe("guest product shell contract", () => {
  it("guestProduct nav excludes Today and Profile", () => {
    const items = buildAppNavItems("ru", "guestProduct");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_GUEST_PRODUCT_ORDER);
    expect(items.map((i) => i.id)).not.toContain("today");
    expect(items.map((i) => i.id)).not.toContain("profile");
  });

  it("authenticated nav keeps the five primary items", () => {
    const items = buildAppNavItems("ru", "authenticated");
    expect(items.map((i) => i.id)).toEqual([
      "today",
      "profile",
      "compatibility",
      "tarot",
      "practices",
    ]);
  });
});
