import {
  applyTodayRitualSpineReducer,
  executeRitualSpineAnalytics,
  isRitualSpineSnapshotComplete,
  mapRitualSpineScrollToDomId,
  ritualSpineConsistencyIssues,
  ritualSpinePhaseForSnapshot,
  ritualSpineTransitionAllows,
  withOptionalGuideGenerationId,
  type TodayRitualSpineSnapshot,
} from "@/lib/todayRitualSpineMachine";

const base = (): TodayRitualSpineSnapshot => ({
  dayOpened: false,
  tarotContinueAck: false,
  numberRevealed: false,
  tarotMainId: null,
  tarotMainResolved: false,
  selectedMoodId: null,
  checkInSubmitted: false,
  guideNarrativeLoading: false,
});

describe("todayRitualSpineMachine", () => {
  it("phase notStarted", () => {
    expect(ritualSpinePhaseForSnapshot(base()).kind).toBe("notStarted");
  });

  it("reducer openedDay", () => {
    const out = applyTodayRitualSpineReducer({ type: "openedDay" }, base());
    expect(out?.after.dayOpened).toBe(true);
    expect(out?.effects.saveOpenedDay).toBe(true);
    expect(out?.effects.scrollToAnchorId).toBe("ritualDeck");
    expect(out?.effects.analyticsHint).toEqual({ kind: "none" });
    expect(mapRitualSpineScrollToDomId("ritualDeck")).toBe("today-ritual-card");
  });

  it("rejects double open", () => {
    const opened = { ...base(), dayOpened: true };
    expect(applyTodayRitualSpineReducer({ type: "openedDay" }, opened)).toBeNull();
  });

  it("continuedPastTarot from tarotInteractive", () => {
    const s = { ...base(), dayOpened: true, tarotContinueAck: false };
    expect(ritualSpinePhaseForSnapshot(s).kind).toBe("tarotInteractive");
    const out = applyTodayRitualSpineReducer({ type: "continuedPastTarot" }, s);
    expect(out?.after.tarotContinueAck).toBe(true);
    expect(out?.effects.scrollToAnchorId).toBe("ritualNumber");
    expect(out?.effects.analyticsHint).toEqual({ kind: "none" });
  });

  it("revealedNumber after ack", () => {
    const s = { ...base(), dayOpened: true, tarotContinueAck: true, numberRevealed: false };
    expect(ritualSpinePhaseForSnapshot(s).kind).toBe("numberSelecting");
    const out = applyTodayRitualSpineReducer({ type: "revealedNumber" }, s);
    expect(out?.after.numberRevealed).toBe(true);
    expect(out?.effects.resetNumberExtraSteps).toBe(true);
    expect(out?.effects.analyticsHint).toEqual({ kind: "numberRevealed" });
  });

  it("selectedMood in checkIn", () => {
    const s = {
      ...base(),
      dayOpened: true,
      tarotContinueAck: true,
      numberRevealed: true,
      tarotMainId: 1,
      tarotMainResolved: true,
      selectedMoodId: null,
      checkInSubmitted: false,
    };
    expect(ritualSpinePhaseForSnapshot(s).kind).toBe("checkIn");
    const out = applyTodayRitualSpineReducer({ type: "selectedMood", moodId: "tired" }, s);
    expect(out?.after.selectedMoodId).toBe("tired");
    expect(out?.effects.persistRitualExtras).toBe(true);
    expect(out?.effects.analyticsHint).toEqual({ kind: "moodSelected", moodId: "tired" });
  });

  it("submittedCheckIn requires mood and resolved tarot", () => {
    const bad = {
      ...base(),
      dayOpened: true,
      tarotContinueAck: true,
      numberRevealed: true,
      tarotMainId: 1,
      tarotMainResolved: true,
      selectedMoodId: null,
      checkInSubmitted: false,
    };
    expect(applyTodayRitualSpineReducer({ type: "submittedCheckIn" }, bad)).toBeNull();
    const ok = { ...bad, selectedMoodId: "tired" as const };
    const out = applyTodayRitualSpineReducer({ type: "submittedCheckIn" }, ok);
    expect(out?.after.checkInSubmitted).toBe(true);
    expect(out?.effects.scrollAfterNarrativeRefresh).toBe("ritualYourDay");
    expect(out?.effects.analyticsHint).toEqual({ kind: "none" });
  });

  it("isRitualSpineSnapshotComplete requires tarotContinueAck", () => {
    const almost = {
      ...base(),
      dayOpened: true,
      tarotContinueAck: false,
      numberRevealed: true,
      tarotMainId: 3,
      tarotMainResolved: true,
      selectedMoodId: "tired",
      checkInSubmitted: true,
    };
    expect(isRitualSpineSnapshotComplete(almost)).toBe(false);
  });

  it("isRitualSpineSnapshotComplete matches web isRitualSpineComplete shape", () => {
    const complete = {
      ...base(),
      dayOpened: true,
      tarotContinueAck: true,
      numberRevealed: true,
      tarotMainId: 3,
      tarotMainResolved: true,
      selectedMoodId: "tired",
      checkInSubmitted: true,
    };
    expect(isRitualSpineSnapshotComplete(complete)).toBe(true);
    expect(ritualSpinePhaseForSnapshot(complete).kind).toBe("dayReady");
  });

  it("consistency detects broken checkin", () => {
    const s = {
      ...base(),
      dayOpened: true,
      tarotContinueAck: true,
      numberRevealed: false,
      tarotMainId: 1,
      tarotMainResolved: true,
      selectedMoodId: null,
      checkInSubmitted: true,
    };
    expect(ritualSpineConsistencyIssues(s)).toContain("checkin_without_number");
  });

  it("ritualSpineTransitionAllows matches reducer gate", () => {
    const s = { ...base(), dayOpened: true, tarotContinueAck: false };
    expect(ritualSpineTransitionAllows({ type: "continuedPastTarot" }, s)).toBe(true);
    expect(applyTodayRitualSpineReducer({ type: "continuedPastTarot" }, s)).not.toBeNull();
  });
});

describe("withOptionalGuideGenerationId", () => {
  it("adds generation_id when guide id is positive", () => {
    expect(withOptionalGuideGenerationId({ a: 1 }, 99)).toEqual({ a: 1, generation_id: 99 });
  });
  it("omits generation_id when guide id missing or non-positive", () => {
    expect(withOptionalGuideGenerationId({ a: 1 }, null)).toEqual({ a: 1 });
    expect(withOptionalGuideGenerationId({ a: 1 }, 0)).toEqual({ a: 1 });
  });
});

describe("executeRitualSpineAnalytics", () => {
  it("none does not call track or onTrackMood", () => {
    const trackMeaningEvent = jest.fn();
    const onTrackMood = jest.fn();
    executeRitualSpineAnalytics(
      { kind: "none" },
      { numerologyValue: "7", trackMeaningEvent, onTrackMood },
    );
    expect(trackMeaningEvent).not.toHaveBeenCalled();
    expect(onTrackMood).not.toHaveBeenCalled();
  });

  it("numberRevealed sends number_selected with numerology_value", () => {
    const trackMeaningEvent = jest.fn();
    executeRitualSpineAnalytics(
      { kind: "numberRevealed" },
      { numerologyValue: "3", trackMeaningEvent },
    );
    expect(trackMeaningEvent).toHaveBeenCalledTimes(1);
    expect(trackMeaningEvent).toHaveBeenCalledWith({
      event_type: "number_selected",
      event_source: "today",
      payload: { revealed: true, numerology_value: "3" },
    });
  });

  it("numberRevealed adds generation_id when guideGenerationId is set", () => {
    const trackMeaningEvent = jest.fn();
    executeRitualSpineAnalytics(
      { kind: "numberRevealed" },
      { numerologyValue: "3", guideGenerationId: 9001, trackMeaningEvent },
    );
    expect(trackMeaningEvent).toHaveBeenCalledWith({
      event_type: "number_selected",
      event_source: "today",
      payload: { revealed: true, numerology_value: "3", generation_id: 9001 },
    });
  });

  it("moodSelected calls onTrackMood before trackMeaningEvent", () => {
    const order: string[] = [];
    const trackMeaningEvent = jest.fn(() => {
      order.push("track");
    });
    const onTrackMood = jest.fn(() => {
      order.push("onTrackMood");
    });
    executeRitualSpineAnalytics(
      { kind: "moodSelected", moodId: "tired" },
      { numerologyValue: "", trackMeaningEvent, onTrackMood },
    );
    expect(onTrackMood).toHaveBeenCalledWith("tired");
    expect(trackMeaningEvent).toHaveBeenCalledWith({
      event_type: "mood_selected",
      event_source: "today",
      payload: { mood_id: "tired", source: "today_ritual" },
    });
    expect(order).toEqual(["onTrackMood", "track"]);
  });

  it("moodSelected adds generation_id when guideGenerationId is set", () => {
    const trackMeaningEvent = jest.fn();
    executeRitualSpineAnalytics(
      { kind: "moodSelected", moodId: "tired" },
      { numerologyValue: "1", guideGenerationId: 42, trackMeaningEvent },
    );
    expect(trackMeaningEvent).toHaveBeenCalledWith({
      event_type: "mood_selected",
      event_source: "today",
      payload: { mood_id: "tired", source: "today_ritual", generation_id: 42 },
    });
  });

  it("moodSelected works without onTrackMood", () => {
    const trackMeaningEvent = jest.fn();
    executeRitualSpineAnalytics(
      { kind: "moodSelected", moodId: "calm" },
      { numerologyValue: "1", trackMeaningEvent },
    );
    expect(trackMeaningEvent).toHaveBeenCalledWith({
      event_type: "mood_selected",
      event_source: "today",
      payload: { mood_id: "calm", source: "today_ritual" },
    });
  });
});
