import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";

const mockHasCompletedFirstToday = jest.fn<boolean, []>(() => false);

jest.mock("@/lib/firstTodayState", () => ({
  FIRST_TODAY_PATH: "/today?first=1",
  hasCompletedFirstToday: () => mockHasCompletedFirstToday(),
}));

import { resolvePostCoreAuthTarget } from "@/lib/authRedirect";

describe("resolvePostCoreAuthTarget", () => {
  beforeEach(() => {
    mockHasCompletedFirstToday.mockReturnValue(false);
  });

  it("routes new users to First Today path", () => {
    expect(resolvePostCoreAuthTarget()).toBe(FIRST_TODAY_PATH);
  });

  it("routes after First Today to profile", () => {
    mockHasCompletedFirstToday.mockReturnValue(true);
    expect(resolvePostCoreAuthTarget()).toBe("/profile");
  });

  it("does not divert to /onboarding/intent (chips live in First Today)", () => {
    mockHasCompletedFirstToday.mockReturnValue(false);
    expect(resolvePostCoreAuthTarget()).toBe(FIRST_TODAY_PATH);
    expect(resolvePostCoreAuthTarget()).not.toContain("/onboarding/intent");
  });
});
