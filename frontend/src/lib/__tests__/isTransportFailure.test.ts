import { ApiError, isRequestAborted, isTransportFailure } from "@/lib/api";

describe("isTransportFailure", () => {
  it("treats any TypeError as transport failure", () => {
    expect(isTransportFailure(new TypeError("Failed to fetch"))).toBe(true);
    expect(isTransportFailure(new TypeError("Load failed"))).toBe(true);
  });

  it("treats AbortError as transport failure", () => {
    expect(isTransportFailure(new DOMException("Aborted", "AbortError"))).toBe(true);
  });

  it("treats abort message ApiError as transport failure", () => {
    expect(
      isTransportFailure(new ApiError("signal is aborted without reason", 0, "/auth/me")),
    ).toBe(true);
  });

  it("does not treat ApiError HTTP statuses as transport", () => {
    expect(isTransportFailure(new ApiError("nope", 401, "/auth/login"))).toBe(false);
    expect(isTransportFailure(new ApiError("nope", 429, "/auth/login"))).toBe(false);
  });
});

describe("isRequestAborted", () => {
  it("detects AbortError / TimeoutError DOMExceptions", () => {
    expect(isRequestAborted(new DOMException("Aborted", "AbortError"))).toBe(true);
    expect(isRequestAborted(new DOMException("Request timed out.", "TimeoutError"))).toBe(true);
  });

  it("detects status-0 ApiError abort/timeout messages", () => {
    expect(isRequestAborted(new ApiError("signal is aborted without reason", 0, "/auth/me"))).toBe(
      true,
    );
    expect(isRequestAborted(new ApiError("Request timed out.", 0, "/today/contract"))).toBe(true);
  });

  it("does not treat ordinary HTTP ApiErrors as aborted", () => {
    expect(isRequestAborted(new ApiError("Unauthorized", 401, "/auth/me"))).toBe(false);
  });
});
