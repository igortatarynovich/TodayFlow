import { normalizeIdempotencyKey } from "@/lib/meaningRuntime";

describe("normalizeIdempotencyKey", () => {
  it("passes through keys within backend limit", () => {
    const key = "onboarding_recognition_shown:2000-01-20:abc";
    expect(normalizeIdempotencyKey(key)).toBe(key);
  });

  it("shortens keys longer than 128 characters", () => {
    const longKey = `onboarding_recognition_shown:2000-01-20:${"x".repeat(200)}`;
    const normalized = normalizeIdempotencyKey(longKey);
    expect(normalized.length).toBeLessThanOrEqual(128);
    expect(normalized).not.toBe(longKey);
  });
});
