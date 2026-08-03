import type { TodayContractV1 } from "@/lib/todayContract";
import { pickGlanceSphereChips } from "@/lib/todayGlanceSphereChips";
import { buildPlotConflictNarrative } from "@/lib/todayPlotNarrative";

function contractWith(scenes: Array<Record<string, unknown>>, why = "Луна держит ровный темп без надрыва."): TodayContractV1 {
  return {
    day_story: {
      interpretation_status: "ready",
      day_scenario: {
        ready: true,
        runtime_sot: true,
        conflict: {
          short_name: "Расчистка от устаревшего",
          why_arose: why,
          opposing_forces: { a: "Инерция и желание сохранить статус-кво", b: "Потребность в ясности" },
          thesis: { mode: "stability" },
        },
        scenes,
      },
    },
  } as unknown as TodayContractV1;
}

describe("pickGlanceSphereChips", () => {
  it("returns up to 2 distinct domains by magnitude", () => {
    const chips = pickGlanceSphereChips(
      contractWith([
        { sphere: "work", role_in_story: "support", what_happens: "a" },
        { sphere: "relationships", role_in_story: "primary", trap: "сгладить", what_happens: "b" },
        { sphere: "energy", role_in_story: "caution", opportunity: "пауза", what_happens: "c" },
      ]),
    );
    expect(chips.length).toBeLessThanOrEqual(2);
    expect(chips.length).toBeGreaterThan(0);
    expect(new Set(chips.map((c) => c.domain)).size).toBe(chips.length);
  });

  it("returns empty when no scenes", () => {
    expect(pickGlanceSphereChips(contractWith([]))).toEqual([]);
  });
});

describe("buildPlotConflictNarrative", () => {
  it("does not invent Натяжение между opener from opposing_forces", () => {
    const n = buildPlotConflictNarrative(
      contractWith([{ sphere: "work", what_happens: "x", role_in_story: "primary" }]),
    );
    expect(n?.tension).toBeNull();
    expect(n?.why).toMatch(/Луна/);
    expect(n?.why).not.toMatch(/Натяжение между/);
  });

  it("strips baked binary opener from why_arose", () => {
    const n = buildPlotConflictNarrative(
      contractWith(
        [{ sphere: "work", what_happens: "x", role_in_story: "primary" }],
        "Натяжение между «Инерция» и «Ясность». Луна держит ровный темп.",
      ),
    );
    expect(n?.tension).toBeNull();
    expect(n?.why).toBe("Луна держит ровный темп.");
  });
});
