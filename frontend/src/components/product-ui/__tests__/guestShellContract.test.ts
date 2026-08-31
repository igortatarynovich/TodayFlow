import {
  APP_NAV_GUEST_PRODUCT_ORDER,
  APP_NAV_GUEST_PRODUCT_PRIMARY,
  buildAppNavItems,
} from "@/lib/appNavConfig";

/**
 * Documents the ProductWebAppShell guest chrome contract:
 * guest = not authenticated (including auth still loading / SSR).
 * Do not gate on authLoading — that baked «Путник» + full nav into HTML.
 */
describe("guest product shell contract", () => {
  it("guestProduct nav includes Today, Profile, and Compatibility as primary", () => {
    const items = buildAppNavItems("ru", "guestProduct");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_GUEST_PRODUCT_ORDER);
    expect(APP_NAV_GUEST_PRODUCT_PRIMARY).toEqual(["today", "profile", "compatibility"]);
    expect(items.map((i) => i.id).slice(0, 3)).toEqual(["today", "profile", "compatibility"]);
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
