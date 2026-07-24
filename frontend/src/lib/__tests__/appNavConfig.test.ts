import {
  APP_NAV_GUEST_ORDER,
  APP_NAV_PRIMARY_ORDER,
  buildAppNavItems,
  buildAppNavLinks,
  resolveAppNavLabel,
} from "@/lib/appNavConfig";

describe("appNavConfig", () => {
  it("defines four primary nav items without practices hub", () => {
    const items = buildAppNavItems("ru", "authenticated");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_PRIMARY_ORDER);
    expect(items).toHaveLength(4);
    expect(items.map((i) => i.id)).not.toContain("practices");
    expect(items[0].href).toBe("/today");
    expect(items[1].label).toBe("Моя карта");
  });

  it("defines two guest nav items", () => {
    const items = buildAppNavItems("en", "guest");
    expect(items.map((i) => i.id)).toEqual(APP_NAV_GUEST_ORDER);
    expect(items).toHaveLength(2);
    expect(items[0].label).toBe("Tarot");
  });

  it("buildAppNavLinks returns href + label without icons", () => {
    const links = buildAppNavLinks("ru", "guest");
    expect(links).toEqual([
      { href: "/tarot", label: "Таро" },
      { href: "/compatibility", label: "Совместимость" },
    ]);
  });

  it("resolveAppNavLabel uses locale defaults", () => {
    expect(resolveAppNavLabel("profile", "ru")).toBe("Моя карта");
    expect(resolveAppNavLabel("profile", "en")).toBe("My map");
  });
});
