import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";

const mockHasCompletedFirstToday = jest.fn<boolean, []>(() => false);
const mockMarkFirstTodayCompleted = jest.fn();
const mockFetchCoreProfileCached = jest.fn();

jest.mock("@/lib/firstTodayState", () => ({
  FIRST_TODAY_PATH: "/today?first=1",
  hasCompletedFirstToday: () => mockHasCompletedFirstToday(),
  markFirstTodayCompleted: () => mockMarkFirstTodayCompleted(),
}));

jest.mock("@/lib/coreProfileCache", () => ({
  fetchCoreProfileCached: (...args: unknown[]) => mockFetchCoreProfileCached(...args),
}));

jest.mock("@/lib/claimGuestProfile", () => ({
  claimGuestProfileAfterAuth: jest.fn(async () => ({ status: "no_draft" })),
}));

import {
  getSafeRedirectTarget,
  hasUsableCoreProfileBase,
  POST_AUTH_HOME_PATH,
  resolvePostAuthTarget,
  resolvePostCoreAuthTarget,
} from "@/lib/authRedirect";

describe("getSafeRedirectTarget", () => {
  it("defaults login home to Today, not Profile or First Today", () => {
    expect(getSafeRedirectTarget(null)).toBe(POST_AUTH_HOME_PATH);
    expect(getSafeRedirectTarget(undefined)).toBe("/today");
    expect(getSafeRedirectTarget(null)).not.toBe(FIRST_TODAY_PATH);
  });
});

describe("resolvePostCoreAuthTarget", () => {
  beforeEach(() => {
    mockHasCompletedFirstToday.mockReturnValue(false);
  });

  it("opens Today after login instead of the First Today chip gate", () => {
    expect(resolvePostCoreAuthTarget()).toBe(POST_AUTH_HOME_PATH);
    expect(resolvePostCoreAuthTarget()).not.toBe(FIRST_TODAY_PATH);
  });

  it("does not send returning users to profile as the login home", () => {
    mockHasCompletedFirstToday.mockReturnValue(true);
    expect(resolvePostCoreAuthTarget()).toBe("/today");
  });

  it("does not divert to /onboarding/intent (chips live in First Today onboarding)", () => {
    expect(resolvePostCoreAuthTarget()).not.toContain("/onboarding/intent");
  });
});

describe("hasUsableCoreProfileBase", () => {
  it("accepts ready profiles", () => {
    expect(hasUsableCoreProfileBase({ is_ready: true })).toBe(true);
  });

  it("accepts birth facts even when soft fields keep is_ready false", () => {
    expect(
      hasUsableCoreProfileBase({
        is_ready: false,
        astro: { birth_date: "1990-05-15", profile_id: 12 },
      }),
    ).toBe(true);
  });

  it("rejects empty shells", () => {
    expect(hasUsableCoreProfileBase({ is_ready: false, astro: {} })).toBe(false);
    expect(hasUsableCoreProfileBase(null)).toBe(false);
  });
});

describe("resolvePostAuthTarget", () => {
  beforeEach(() => {
    mockHasCompletedFirstToday.mockReturnValue(false);
    mockMarkFirstTodayCompleted.mockReset();
    mockFetchCoreProfileCached.mockReset();
  });

  it("does not force onboarding when birth data already exists", async () => {
    mockFetchCoreProfileCached.mockResolvedValue({
      is_ready: false,
      astro: { birth_date: "1990-05-15", profile_id: 7 },
    });
    await expect(resolvePostAuthTarget("/profile")).resolves.toBe("/profile");
  });

  it("sends ready accounts to Today, not First Today chips", async () => {
    mockFetchCoreProfileCached.mockResolvedValue({
      is_ready: true,
      astro: { birth_date: "1990-02-13", profile_id: 2 },
    });
    await expect(resolvePostAuthTarget(null)).resolves.toBe("/today");
    await expect(resolvePostAuthTarget(FIRST_TODAY_PATH)).resolves.toBe("/today");
    expect(mockMarkFirstTodayCompleted).toHaveBeenCalled();
  });

  it("does not treat transient fetch errors as missing profile or First Today", async () => {
    mockFetchCoreProfileCached.mockRejectedValue(new Error("network"));
    await expect(resolvePostAuthTarget(null)).resolves.toBe("/today");
  });

  it("sends truly empty accounts to core onboarding", async () => {
    mockFetchCoreProfileCached.mockResolvedValue({ is_ready: false, astro: {} });
    await expect(resolvePostAuthTarget("/profile")).resolves.toBe("/onboarding/core");
  });
});
