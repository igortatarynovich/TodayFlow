import { ApiError, isTransportFailure } from "@/lib/api";

describe("isTransportFailure", () => {
  it("treats any TypeError as transport failure", () => {
    expect(isTransportFailure(new TypeError("Failed to fetch"))).toBe(true);
    expect(isTransportFailure(new TypeError("Load failed"))).toBe(true);
  });

  it("treats AbortError as transport failure", () => {
    expect(isTransportFailure(new DOMException("Aborted", "AbortError"))).toBe(true);
  });

  it("does not treat ApiError HTTP statuses as transport", () => {
    expect(isTransportFailure(new ApiError("nope", 401, "/auth/login"))).toBe(false);
    expect(isTransportFailure(new ApiError("nope", 429, "/auth/login"))).toBe(false);
  });
});
