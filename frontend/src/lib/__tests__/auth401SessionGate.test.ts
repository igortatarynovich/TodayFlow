import { ApiError } from "@/lib/api";

/**
 * Mirrors the session-clear gate in api.ts performRequest (401 branch).
 * Keep in sync when changing logout-on-401 rules.
 */
function shouldClearAuthSessionOn401(path: string): boolean {
  const isCredentialChallenge =
    path.includes("/auth/login") ||
    path.includes("/auth/email-signup") ||
    path.includes("/auth/signup") ||
    path.includes("/auth/magic");
  const isAuthMeProbe = path === "/auth/me" || path.startsWith("/auth/me?");
  return !isCredentialChallenge && isAuthMeProbe;
}

describe("401 session clear gate", () => {
  it("clears only on /auth/me 401", () => {
    expect(shouldClearAuthSessionOn401("/auth/me")).toBe(true);
  });

  it("does not clear on login challenge", () => {
    expect(shouldClearAuthSessionOn401("/auth/login")).toBe(false);
  });

  it("does not clear on practices or guest claim 401", () => {
    expect(shouldClearAuthSessionOn401("/practices/progress")).toBe(false);
    expect(shouldClearAuthSessionOn401("/today/guest/claim")).toBe(false);
    expect(shouldClearAuthSessionOn401("/today/contract")).toBe(false);
  });

  it("ApiError still carries guest claim detail without implying session wipe", () => {
    const err = new ApiError("invalid_claim_token", 400, "/today/guest/claim", {
      detail: "invalid_claim_token",
    });
    expect(err.status).toBe(400);
    expect(err.path).toContain("/today/guest/");
  });
});
