import { FIRST_TODAY_PATH } from "@/lib/firstTodayState";

const mockHasCompletedFirstToday = jest.fn<boolean, []>(() => false);
const mockFetchCoreProfileCached = jest.fn();

jest.mock("@/lib/firstTodayState", () => ({
  FIRST_TODAY_PATH: "/today?first=1",
  hasCompletedFirstToday: () => mockHasCompletedFirstToday(),
}));

jest.mock("@/lib/coreProfileCache", () => ({
  fetchCoreProfileCached: (...args: unknown[]) => mockFetchCoreProfileCached(...args),
}));

jest.mock("@/lib/claimGuestProfile", () => ({
  claimGuestProfileAfterAuth: jest.fn(async () => ({ status: "no_draft" })),
}));

import {
  hasUsableCoreProfileBase,
  resolvePostAuthTarget,
  resolvePostCoreAuthTarget,
} from "@/lib/authRedirect";

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
    mockHasCompletedFirstToday.mockReturnValue(true);
    mockFetchCoreProfileCached.mockReset();
  });

  it("does not force onboarding when birth data already exists", async () => {
    mockFetchCoreProfileCached.mockResolvedValue({
      is_ready: false,
      astro: { birth_date: "1990-05-15", profile_id: 7 },
    });
    await expect(resolvePostAuthTarget("/profile")).resolves.toBe("/profile");
  });

  it("does not treat transient fetch errors as missing profile", async () => {
    mockFetchCoreProfileCached.mockRejectedValue(new Error("network"));
    await expect(resolvePostAuthTarget(null)).resolves.toBe("/profile");
  });

  it("sends truly empty accounts to core onboarding", async () => {
    mockFetchCoreProfileCached.mockResolvedValue({ is_ready: false, astro: {} });
    await expect(resolvePostAuthTarget("/profile")).resolves.toBe("/onboarding/core");
  });
});
