import { ApiError } from "@/lib/api";
import {
  TODAY_NO_CONNECTION_COPY,
  TODAY_UNAVAILABLE_COPY,
  isHonestUnavailableCopy,
  todaySlotFailureCopy,
  todaySlotFailureFromError,
} from "@/lib/todaySlotAvailability";

describe("todaySlotAvailability", () => {
  it("names no connection plainly", () => {
    expect(todaySlotFailureCopy("no_connection")).toBe(TODAY_NO_CONNECTION_COPY);
    expect(TODAY_NO_CONNECTION_COPY).toMatch(/^Нет соединения\.?$/);
  });

  it("does not invent sphere/day content for unavailable", () => {
    expect(todaySlotFailureCopy("unavailable")).toBe(TODAY_UNAVAILABLE_COPY);
    expect(TODAY_UNAVAILABLE_COPY).not.toMatch(/спокойн|сигнал|сфер|calm/i);
    expect(isHonestUnavailableCopy(TODAY_UNAVAILABLE_COPY)).toBe(true);
    expect(isHonestUnavailableCopy(TODAY_NO_CONNECTION_COPY)).toBe(true);
    expect(isHonestUnavailableCopy("Ровный продуктивный ритм.")).toBe(false);
  });

  it("maps auth errors to unavailable, not no_connection", () => {
    expect(todaySlotFailureFromError(new ApiError("Неверный токен", 401, "/today/day-facts"))).toBe(
      "unavailable",
    );
    expect(todaySlotFailureFromError(new ApiError("forbidden", 403, "/today/day-facts"))).toBe(
      "unavailable",
    );
  });

  it("maps transport / status 0 to no_connection", () => {
    expect(todaySlotFailureFromError(new ApiError("Network error", 0, "/today/day-facts"))).toBe(
      "no_connection",
    );
    expect(todaySlotFailureFromError(new TypeError("Failed to fetch"))).toBe("no_connection");
  });

  it("maps client timeouts to unavailable (slow assemble ≠ lost connection)", () => {
    expect(
      todaySlotFailureFromError(new DOMException("Request timed out.", "TimeoutError")),
    ).toBe("unavailable");
    expect(
      todaySlotFailureFromError(new ApiError("Request timed out.", 0, "/today/day-facts")),
    ).toBe("unavailable");
    expect(
      todaySlotFailureFromError(new DOMException("Request timed out.", "AbortError")),
    ).toBe("unavailable");
  });

  it("ignores remount AbortError so callers do not paint false no_connection", () => {
    expect(
      todaySlotFailureFromError(new DOMException("The user aborted a request.", "AbortError")),
    ).toBeNull();
  });
});
