import { buildProfileLivingObservation, buildProfileMapsLocalObservation, buildProfileMapsPreviewModel } from "@/lib/profileMapsPreview";
import { saveDayContinuity } from "@/lib/todayDayContinuity";
import { saveDayEngagement } from "@/lib/todayDayEngagement";

describe("profileMapsPreview", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("returns empty model when no closed days", () => {
    const model = buildProfileMapsPreviewModel();
    expect(model.hasSeeds).toBe(false);
    expect(model.totalSeeds).toBe(0);
    expect(model.recentSeeds).toHaveLength(0);
  });

  it("builds chronological seed strip from closed evenings", () => {
    saveDayContinuity({
      dateISO: "2026-06-20",
      mainFocus: "A",
      outcome: "done",
      closedAt: "2026-06-20T20:00:00.000Z",
    });
    saveDayContinuity({
      dateISO: "2026-06-22",
      mainFocus: "B",
      outcome: "partial",
      closedAt: "2026-06-22T20:00:00.000Z",
    });

    const model = buildProfileMapsPreviewModel(7);
    expect(model.totalSeeds).toBe(2);
    expect(model.recentSeeds.map((s) => s.dateISO)).toEqual(["2026-06-20", "2026-06-22"]);
    expect(model.recentSeeds[1]?.outcome).toBe("partial");
  });

  it("prefers living summary for observation line", () => {
    expect(
      buildProfileLivingObservation({
        livingSummary: "  Вечерний ритм уже заметен. ",
        cum: { active_themes: [{ id: "discipline" }] },
      }),
    ).toBe("Вечерний ритм уже заметен.");
  });

  it("falls back to CUM theme when no living summary", () => {
    expect(
      buildProfileLivingObservation({
        cum: { active_themes: [{ id: "work_focus" }] },
      }),
    ).toContain("фокус на работе");
  });

  it("uses cycle observation after CUM when no living summary", () => {
    expect(
      buildProfileLivingObservation({
        cum: { behavioral_patterns: { hints: [] }, active_themes: [] },
        cycleObservation: "Несколько циклов на карте — ритм месяца начинает влиять на узор дней.",
      }),
    ).toContain("Несколько циклов");
  });

  it("prefers CUM hint over cycle observation", () => {
    expect(
      buildProfileLivingObservation({
        cum: { behavioral_patterns: { hints: ["Вечерний ритм стабилен"] } },
        cycleObservation: "Несколько циклов на карте",
      }),
    ).toBe("Вечерний ритм стабилен");
  });

  it("builds local cross-map observation from mood marks", () => {
    for (let i = 0; i < 4; i += 1) {
      const dateISO = `2026-06-${String(19 - i).padStart(2, "0")}`;
      saveDayEngagement(dateISO, {
        morningMoodId: "calm",
        morningMoodCapturedAtMs: Date.now(),
      });
    }
    expect(buildProfileMapsLocalObservation()).toMatch(/calm|Спокой/i);
  });
});
