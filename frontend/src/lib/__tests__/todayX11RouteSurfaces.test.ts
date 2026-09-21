/**
 * X11 — product `/today` never mounts leftover stacked surfaces.
 * Physical delete of leftover files is out of gate; this locks the route.
 * Canon: TODAY_PRODUCT_FLOW_V1 X11
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

const pageSrc = readFileSync(join(__dirname, "../../app/today/page.tsx"), "utf8");

describe("X11 product /today route", () => {
  it("does not import leftover experience or ritual-flow as product Today", () => {
    expect(pageSrc).not.toMatch(/from ["']@\/components\/today\/experience\/TodayExperienceSurface["']/);
    expect(pageSrc).not.toMatch(/from ["']@\/components\/today\/TodayRitualFlow["']/);
    expect(pageSrc).not.toMatch(/<TodayExperienceSurface/);
    expect(pageSrc).not.toMatch(/<TodayRitualFlow/);
  });

  it("does not keep a NODE_ENV / query-param switch onto leftover surfaces", () => {
    expect(pageSrc).not.toMatch(/allowLegacyTodaySurfaces/);
    expect(pageSrc).not.toMatch(/searchParams\.get\(["']full["']\)/);
    expect(pageSrc).not.toMatch(/searchParams\.get\(["']experience["']\)/);
  });
});
