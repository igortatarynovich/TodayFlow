import {
  TODAY_NO_CONNECTION_COPY,
  TODAY_UNAVAILABLE_COPY,
  todaySlotFailureCopy,
} from "@/lib/todaySlotAvailability";

describe("todaySlotAvailability", () => {
  it("names no connection plainly", () => {
    expect(todaySlotFailureCopy("no_connection")).toBe(TODAY_NO_CONNECTION_COPY);
    expect(TODAY_NO_CONNECTION_COPY).toMatch(/^Нет соединения\.?$/);
  });

  it("does not invent sphere/day content for unavailable", () => {
    expect(todaySlotFailureCopy("unavailable")).toBe(TODAY_UNAVAILABLE_COPY);
    expect(TODAY_UNAVAILABLE_COPY).not.toMatch(/спокойн|сигнал|сфер|calm/i);
  });
});
