import {
  isRitualSpineComplete,
  normalizeRitualPersistedPayload,
  ritualPersistedStorageKey,
} from "@/lib/todayRitualPersisted";

describe("ritualPersistedStorageKey", () => {
  it("scopes by date ISO", () => {
    expect(ritualPersistedStorageKey("2026-04-26")).toBe("todayflow.ritual.v1.2026-04-26");
  });
});

describe("normalizeRitualPersistedPayload", () => {
  it("returns defaults for empty object", () => {
    const s = normalizeRitualPersistedPayload({});
    expect(s.opened).toBe(false);
    expect(s.numberRevealed).toBe(false);
    expect(s.mood).toBeNull();
    expect(s.tarotMainId).toBeNull();
    expect(s.tarotContinueAck).toBe(false);
    expect(s.checkInSubmitted).toBe(false);
  });

  it("migrates tarotContinueAck when card and number already done", () => {
    const s = normalizeRitualPersistedPayload({
      tarotMainId: 3,
      numberRevealed: true,
      tarotContinueAck: false,
    });
    expect(s.tarotContinueAck).toBe(true);
  });

  it("does not force tarotContinueAck when number not revealed", () => {
    const s = normalizeRitualPersistedPayload({
      tarotMainId: 3,
      numberRevealed: false,
      tarotContinueAck: false,
    });
    expect(s.tarotContinueAck).toBe(false);
  });

  it("migrates checkInSubmitted from mood when field missing", () => {
    const s = normalizeRitualPersistedPayload({ mood: "calm" });
    expect(s.checkInSubmitted).toBe(true);
  });

  it("respects explicit checkInSubmitted false with mood (edge)", () => {
    const s = normalizeRitualPersistedPayload({ mood: "calm", checkInSubmitted: false });
    expect(s.checkInSubmitted).toBe(false);
  });

  it("treats non-object input as empty", () => {
    const s = normalizeRitualPersistedPayload(null);
    expect(s.mood).toBeNull();
  });
});

describe("isRitualSpineComplete", () => {
  const base = {
    tarotMainId: 1 as number | null,
    tarotContinueAck: true,
    numberRevealed: true,
    mood: "calm" as string | null,
    checkInSubmitted: true,
  };

  it("is true when all gates pass", () => {
    expect(isRitualSpineComplete(base)).toBe(true);
  });

  it("is false without tarotContinueAck", () => {
    expect(isRitualSpineComplete({ ...base, tarotContinueAck: false })).toBe(false);
  });

  it("is false without checkInSubmitted", () => {
    expect(isRitualSpineComplete({ ...base, checkInSubmitted: false })).toBe(false);
  });

  it("is true without mood (R18 — mood chips removed)", () => {
    expect(isRitualSpineComplete({ ...base, mood: null })).toBe(true);
  });

  it("is false without tarotMainId", () => {
    expect(isRitualSpineComplete({ ...base, tarotMainId: null })).toBe(false);
  });

  it("is false without numberRevealed", () => {
    expect(isRitualSpineComplete({ ...base, numberRevealed: false })).toBe(false);
  });
});
