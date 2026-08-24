import { getStoredAccessToken, requestTimeoutMs, shouldClearAuthSessionOn401 } from "@/lib/api";

describe("401 session clear gate", () => {
  it("clears only on /auth/me 401 when request bearer matches current token", () => {
    expect(shouldClearAuthSessionOn401("/auth/me", "tok-a", "tok-a")).toBe(true);
  });

  it("does not clear when stale /auth/me 401 uses an old bearer after login", () => {
    expect(shouldClearAuthSessionOn401("/auth/me", "tok-old", "tok-new")).toBe(false);
  });

  it("does not clear when storage was already wiped or request had no bearer", () => {
    expect(shouldClearAuthSessionOn401("/auth/me", "tok-a", null)).toBe(false);
    expect(shouldClearAuthSessionOn401("/auth/me", null, "tok-a")).toBe(false);
  });

  it("does not clear on login challenge", () => {
    expect(shouldClearAuthSessionOn401("/auth/login", "tok-a", "tok-a")).toBe(false);
  });

  it("does not clear on practices or guest claim 401", () => {
    expect(shouldClearAuthSessionOn401("/practices/progress", "tok-a", "tok-a")).toBe(false);
    expect(shouldClearAuthSessionOn401("/today/guest/claim", "tok-a", "tok-a")).toBe(false);
    expect(shouldClearAuthSessionOn401("/today/contract", "tok-a", "tok-a")).toBe(false);
  });
});

describe("requestTimeoutMs", () => {
  it("caps hung login and session probes so the UI cannot spin forever", () => {
    expect(requestTimeoutMs("/auth/me", false)).toBe(5_000);
    expect(requestTimeoutMs("/auth/login", false)).toBe(15_000);
    expect(requestTimeoutMs("/today/opening", false)).toBe(15_000);
    expect(requestTimeoutMs("/today/bundle", false)).toBe(15_000);
  });

  it("does not override a caller AbortSignal", () => {
    expect(requestTimeoutMs("/auth/login", true)).toBeNull();
    expect(requestTimeoutMs("/today/contract?timezone=UTC", true)).toBeNull();
  });
});

describe("getStoredAccessToken", () => {
  it("returns null when storage throws (iOS private mode)", () => {
    const original = window.localStorage.getItem;
    window.localStorage.getItem = () => {
      throw new Error("blocked");
    };
    expect(getStoredAccessToken()).toBeNull();
    window.localStorage.getItem = original;
  });
});
