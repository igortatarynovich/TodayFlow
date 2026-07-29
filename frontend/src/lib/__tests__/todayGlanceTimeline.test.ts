import {
  formatGlanceClock,
  isGlanceLiveNow,
} from "@/lib/todayGlanceTimeline";

describe("todayGlanceTimeline", () => {
  it("formats ISO clock to HH:MM", () => {
    expect(formatGlanceClock("2026-08-01T14:30:00+03:00")).toBe("14:30");
    expect(formatGlanceClock("09:05")).toBe("09:05");
  });

  it("detects live-now within 45 minutes", () => {
    const now = new Date("2026-08-01T14:20:00+03:00");
    expect(isGlanceLiveNow("2026-08-01T14:30:00+03:00", now)).toBe(true);
    expect(isGlanceLiveNow("2026-08-01T12:00:00+03:00", now)).toBe(false);
  });
});
