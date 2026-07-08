import {
  buildCompatibilityCheckKey,
  canGuestAccessCompatibility,
  canGuestAccessTarotSpread,
  guestCompatibilityRemaining,
  guestTarotRemaining,
  isGuestPracticeAllowed,
  tryConsumeGuestCompatibility,
  tryConsumeGuestTarotSpread,
} from "@/lib/guestAccessStore";

describe("guestAccessStore", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("consumes tarot spread once per session key", () => {
    expect(tryConsumeGuestTarotSpread("spread-a")).toBe(true);
    expect(guestTarotRemaining()).toBe(0);
    expect(tryConsumeGuestTarotSpread("spread-a")).toBe(true);
    expect(tryConsumeGuestTarotSpread("spread-b")).toBe(false);
  });

  it("allows reopening consumed tarot session when limit reached", () => {
    tryConsumeGuestTarotSpread("spread-a");
    expect(canGuestAccessTarotSpread("spread-a")).toBe(true);
    expect(canGuestAccessTarotSpread("spread-b")).toBe(false);
  });

  it("consumes up to four compatibility checks", () => {
    for (let i = 0; i < 4; i += 1) {
      expect(tryConsumeGuestCompatibility(`pair-${i}`)).toBe(true);
    }
    expect(guestCompatibilityRemaining()).toBe(0);
    expect(tryConsumeGuestCompatibility("pair-5")).toBe(false);
  });

  it("builds stable compatibility keys", () => {
    const key = buildCompatibilityCheckKey({
      mode: "precise",
      birth_date_1: "1990-01-01",
      birth_date_2: "1992-05-05",
    });
    expect(key).toContain("birth_date_1:1990-01-01");
    expect(canGuestAccessCompatibility(key)).toBe(true);
  });

  it("filters guest practices to basic free tier", () => {
    expect(isGuestPracticeAllowed({ is_free: true, access_level: "basic" })).toBe(true);
    expect(isGuestPracticeAllowed({ is_free: true, is_personalized: true })).toBe(false);
    expect(isGuestPracticeAllowed({ is_free: false, access_level: "basic" })).toBe(false);
  });
});
