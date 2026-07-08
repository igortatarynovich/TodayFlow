import { isFlowRoute, isNavRouteActive, NAV_PATHS } from "@/lib/navRoutes";

describe("navRoutes", () => {
  it("treats flow and calendar as the same nav section", () => {
    expect(isFlowRoute("/flow")).toBe(true);
    expect(isFlowRoute("/tracking/calendar")).toBe(true);
    expect(isFlowRoute("/tracking/calendar?create=habit")).toBe(true);
    expect(isFlowRoute("/today")).toBe(false);
  });

  it("highlights Flow for calendar pathname", () => {
    expect(isNavRouteActive("/tracking/calendar", NAV_PATHS.flow)).toBe(true);
    expect(isNavRouteActive("/flow", NAV_PATHS.flow)).toBe(true);
    expect(isNavRouteActive("/today", NAV_PATHS.flow)).toBe(false);
  });
});
