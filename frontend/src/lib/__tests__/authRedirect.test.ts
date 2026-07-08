import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";

const mockHasCompletedFirstToday = jest.fn<boolean, []>(() => false);
const mockHasOnboardingIntent = jest.fn<boolean, []>(() => true);
const mockHasOnboardingReality = jest.fn<boolean, []>(() => true);

jest.mock("@/lib/firstTodayState", () => ({
  FIRST_TODAY_PATH: "/today?first=1",
  hasCompletedFirstToday: () => mockHasCompletedFirstToday(),
}));

jest.mock("@/lib/onboardingContext", () => ({
  hasOnboardingIntent: () => mockHasOnboardingIntent(),
  hasOnboardingReality: () => mockHasOnboardingReality(),
}));

import { resolvePostCoreAuthTarget } from "@/lib/authRedirect";

describe("resolvePostCoreAuthTarget", () => {
  beforeEach(() => {
    mockHasCompletedFirstToday.mockReturnValue(false);
    mockHasOnboardingIntent.mockReturnValue(true);
    mockHasOnboardingReality.mockReturnValue(true);
  });

  it("routes new users to First Today path", () => {
    expect(resolvePostCoreAuthTarget()).toBe(FIRST_TODAY_PATH);
  });

  it("routes after First Today to profile", () => {
    mockHasCompletedFirstToday.mockReturnValue(true);
    expect(resolvePostCoreAuthTarget()).toBe("/profile");
  });

  it("routes to intent onboarding when missing", () => {
    mockHasOnboardingIntent.mockReturnValue(false);
    expect(resolvePostCoreAuthTarget()).toBe("/onboarding/intent");
  });
});
