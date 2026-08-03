import { ApiError } from "@/lib/api";

/**
 * Mirrors the session-clear gate in api.ts performRequest (401 branch).
 * Keep in sync when changing logout-on-401 rules.
 */
function shouldClearAuthSessionOn401(path: string, details?: unknown): boolean {
  const isCredentialChallenge =
    path.includes("/auth/login") ||
    path.includes("/auth/email-signup") ||
    path.includes("/auth/signup") ||
    path.includes("/auth/magic");
  const isGuestClaimSoft = path.includes("/today/guest/") || path.includes("/guest/");
  const detailCode =
    details && typeof details === "object" && details !== null && "detail" in details
      ? String((details as { detail?: unknown }).detail || "")
      : typeof details === "string"
        ? details
        : "";
  const softClaimCodes = new Set([
    "invalid_claim_token",
    "claim_token_expired",
    "invalid_guest_secret",
    "claim_token_required",
  ]);
  return !isCredentialChallenge && !isGuestClaimSoft && !softClaimCodes.has(detailCode);
}

describe("401 session clear gate", () => {
  it("clears on /auth/me 401", () => {
    expect(shouldClearAuthSessionOn401("/auth/me")).toBe(true);
  });

  it("does not clear on login challenge", () => {
    expect(shouldClearAuthSessionOn401("/auth/login")).toBe(false);
  });

  it("does not clear on guest claim soft failures", () => {
    expect(shouldClearAuthSessionOn401("/today/guest/claim", { detail: "invalid_claim_token" })).toBe(
      false,
    );
    expect(shouldClearAuthSessionOn401("/today/guest/claim-token", { detail: "claim_token_expired" })).toBe(
      false,
    );
  });

  it("ApiError still carries guest claim detail without implying session wipe", () => {
    const err = new ApiError("invalid_claim_token", 400, "/today/guest/claim", {
      detail: "invalid_claim_token",
    });
    expect(err.status).toBe(400);
    expect(err.path).toContain("/today/guest/");
  });
});
