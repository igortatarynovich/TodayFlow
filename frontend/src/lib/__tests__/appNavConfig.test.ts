import {
  APP_NAV_GUEST_ORDER,
  APP_NAV_GUEST_PRODUCT_ORDER,
  APP_NAV_GUEST_PRODUCT_PRIMARY,
  APP_NAV_GUEST_PRODUCT_SECONDARY,
  APP_NAV_PRIMARY_ORDER,
  buildAppNavItems,
  buildAppNavLinks,
  resolveAppNavLabel,
} from "@/lib/appNavConfig";

describe("appNavConfig", () => {
  it("defines four primary nav items (practices is deep-link only, not a tab)", () => {
    const items = buildAppNavItems("ru", "authenticated");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_PRIMARY_ORDER);
    expect(items).toHaveLength(4);
    expect(items.map((i) => i.id)).toEqual([
      "today",
      "profile",
      "compatibility",
      "tarot",
    ]);
    expect(items[0].href).toBe("/today");
    expect(items[1].label).toBe("Моя карта");
    expect(items.some((i) => i.id === "practices")).toBe(false);
  });

  it("authenticated chrome exposes the launch nav set", () => {
    const required = ["today", "profile", "compatibility", "tarot"] as const;
    expect(APP_NAV_PRIMARY_ORDER).toEqual([...required]);
    const en = buildAppNavItems("en", "authenticated");
    expect(en.map((i) => i.id)).toEqual([...required]);
  });

  it("defines two guest marketing nav items with Compatibility first", () => {
    const items = buildAppNavItems("en", "guest");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_GUEST_ORDER);
    expect(items).toHaveLength(2);
    expect(items[0].label).toBe("Compatibility");
    expect(items[1].label).toBe("Tarot");
  });

  it("defines guestProduct shell nav with Today·Profile·Compatibility primary", () => {
    const items = buildAppNavItems("ru", "guestProduct");
    expect(APP_NAV_GUEST_PRODUCT_PRIMARY).toEqual(["today", "profile", "compatibility"]);
    expect(APP_NAV_GUEST_PRODUCT_SECONDARY).toEqual(["tarot"]);
    expect(items.map((i) => i.id)).toEqual(APP_NAV_GUEST_PRODUCT_ORDER);
    expect(items.map((i) => i.href)).toEqual([
      "/today",
      "/profile",
      "/compatibility",
      "/tarot",
    ]);
  });

  it("buildAppNavLinks returns href + label without icons", () => {
    const links = buildAppNavLinks("ru", "guest");
    expect(links).toEqual([
      { href: "/#compatibility", label: "Совместимость" },
      { href: "/#tarot", label: "Таро" },
    ]);
  });

  it("resolveAppNavLabel uses locale defaults", () => {
    expect(resolveAppNavLabel("profile", "ru")).toBe("Моя карта");
    expect(resolveAppNavLabel("profile", "en")).toBe("My map");
  });
});
