import { shouldClearAuthSessionOn401 } from "@/lib/api";

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
