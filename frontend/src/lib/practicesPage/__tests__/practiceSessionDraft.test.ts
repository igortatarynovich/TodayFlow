import {
  clearPracticeSessionDraft,
  isPracticeStateAfter,
  readPracticeSessionDraft,
  writePracticeSessionDraft,
} from "@/lib/practicesPage/practiceSessionDraft";

describe("practiceSessionDraft", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("round-trips draft and clears by id", () => {
    writePracticeSessionDraft({
      practiceId: "a",
      title: "Test",
      durationMinutes: 7,
      elapsedSeconds: 120,
      updatedAt: new Date().toISOString(),
    });
    expect(readPracticeSessionDraft()?.title).toBe("Test");
    clearPracticeSessionDraft("other");
    expect(readPracticeSessionDraft()?.practiceId).toBe("a");
    clearPracticeSessionDraft("a");
    expect(readPracticeSessionDraft()).toBeNull();
  });

  it("validates state_after", () => {
    expect(isPracticeStateAfter("better")).toBe(true);
    expect(isPracticeStateAfter("nope")).toBe(false);
  });
});
