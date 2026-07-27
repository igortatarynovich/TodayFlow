import { hasPaidSubscriptionAccess, insightDepthFromProfile } from "@/lib/insightDepth";
import type { AccountProfile } from "@/lib/types";

function profile(partial: Partial<AccountProfile>): AccountProfile {
  return {
    user_id: 1,
    email: "a@b.c",
    is_paid: false,
    has_lite_report: false,
    has_full_report: false,
    ...partial,
  };
}

describe("hasPaidSubscriptionAccess", () => {
  it("is false for guest/null and free", () => {
    expect(hasPaidSubscriptionAccess(null)).toBe(false);
    expect(hasPaidSubscriptionAccess(profile({ subscription_level: "free" }))).toBe(false);
  });

  it("is true for lite, pro, legacy is_paid, and trialing", () => {
    expect(hasPaidSubscriptionAccess(profile({ subscription_level: "lite" }))).toBe(true);
    expect(hasPaidSubscriptionAccess(profile({ subscription_level: "pro" }))).toBe(true);
    expect(hasPaidSubscriptionAccess(profile({ is_paid: true }))).toBe(true);
    expect(
      hasPaidSubscriptionAccess(profile({ subscription_status: "trialing", subscription_level: "free" })),
    ).toBe(true);
  });

  it("aligns insight depth free vs paid", () => {
    expect(insightDepthFromProfile(profile({ subscription_level: "free" }))).toBe("free");
    expect(insightDepthFromProfile(profile({ subscription_level: "lite" }))).toBe("pro");
  });
});
