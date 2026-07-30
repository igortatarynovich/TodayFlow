import { ApiError } from "@/lib/api";
import { mapLoginFailure, shouldFocusLoginFieldError } from "@/lib/mapLoginFailure";

describe("mapLoginFailure", () => {
  it("maps ApiError status 0 to network copy on password", () => {
    const mapped = mapLoginFailure(new ApiError("Network error", 0, "/auth/login"));
    expect(mapped.password).toMatch(/Не удалось подключиться/);
    expect(mapped.email).toBeUndefined();
  });

  it("maps raw TypeError (Failed to fetch) to network copy", () => {
    const mapped = mapLoginFailure(new TypeError("Failed to fetch"));
    expect(mapped.password).toMatch(/Не удалось подключиться/);
  });

  it("maps TypeError without 'fetch' in the message (Safari-style)", () => {
    const mapped = mapLoginFailure(new TypeError("Load failed"));
    expect(mapped.password).toMatch(/Не удалось подключиться/);
  });

  it("maps AbortError to network copy", () => {
    const mapped = mapLoginFailure(new DOMException("Aborted", "AbortError"));
    expect(mapped.password).toMatch(/Не удалось подключиться/);
  });

  it("maps 429 to rate-limit copy", () => {
    const mapped = mapLoginFailure(new ApiError("Too many", 429, "/auth/login"));
    expect(mapped.password).toMatch(/Слишком много попыток/);
  });

  it("maps 401 to invalid credentials on both fields", () => {
    const mapped = mapLoginFailure(new ApiError("Unauthorized", 401, "/auth/login"));
    expect(mapped.email).toMatch(/Неверный email или пароль/);
    expect(mapped.password).toMatch(/Неверный email или пароль/);
  });

  it("does not steal focus for transport failures", () => {
    const err = new TypeError("Failed to fetch");
    const mapped = mapLoginFailure(err);
    expect(shouldFocusLoginFieldError(mapped, err)).toBe(false);
  });

  it("focuses for credential failures", () => {
    const err = new ApiError("bad", 401, "/auth/login");
    const mapped = mapLoginFailure(err);
    expect(shouldFocusLoginFieldError(mapped, err)).toBe(true);
  });
});
