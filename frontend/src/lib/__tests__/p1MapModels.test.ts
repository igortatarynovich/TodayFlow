import {
  buildAsceticDayStory,
  buildAsceticJourneyArcs,
  buildAsceticJourneyObservation,
  buildAsceticShareLine,
  type AsceticContractIn,
} from "@/lib/asceticMapModel";
import { recordRelationshipMapVisit, readRelationshipMapCircles } from "@/lib/relationshipMapStore";
import { buildRelationshipMapObservation } from "@/lib/relationshipMapModel";
import { mergeWishAnchorsFromGoals, saveLocalWishAnchor } from "@/lib/wishMapStore";
import { buildWishMapObservation } from "@/lib/wishMapModel";

describe("asceticMapModel", () => {
  it("builds journey arcs from contracts and calendar tracks", () => {
    const contracts: AsceticContractIn[] = [
      {
        id: 1,
        title: "Без сахара",
        start_date: "2026-06-01",
        status: "active",
        streak_days: 4,
        longest_streak_days: 7,
      },
    ];
    const tracks = [
      {
        asceticism_id: "sugar",
        title: "Без сахара",
        entries: [
          { date: "2026-06-18", completed: true },
          { date: "2026-06-19", completed: true },
        ],
      },
    ];
    const arcs = buildAsceticJourneyArcs(contracts, tracks, "2026-06-19");
    expect(arcs).toHaveLength(1);
    expect(arcs[0].steps.filter((s) => s.completed).length).toBeGreaterThanOrEqual(1);
    expect(buildAsceticJourneyObservation(arcs, "ru")).toMatch(/Без сахара/);
    expect(buildAsceticDayStory(arcs[0], "2026-06-18", "ru")).toMatch(/отмечен/i);
    expect(buildAsceticShareLine(arcs, "ru")).toMatch(/TodayFlow/);
  });
});

describe("wishMapStore", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("merges month goals with local anchors", () => {
    saveLocalWishAnchor("Мечта");
    const merged = mergeWishAnchorsFromGoals([
      {
        id: 2,
        title: "Мечта",
        scope: "month",
        completed: false,
        step_dates: ["2026-06-10"],
      },
    ]);
    expect(merged).toHaveLength(1);
    expect(merged[0].stepCount).toBe(1);
    expect(buildWishMapObservation(merged, "ru")).toMatch(/Мечта/);
  });
});

describe("relationshipMapStore", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("records visits and builds observation", () => {
    recordRelationshipMapVisit({
      label: "Аня × Боря",
      scenarioId: "love",
      theme: "Любовь",
    });
    recordRelationshipMapVisit({
      label: "Аня × Боря",
      scenarioId: "love",
      theme: "Любовь",
    });
    const circles = readRelationshipMapCircles();
    expect(circles[0].visitCount).toBe(2);
    expect(buildRelationshipMapObservation(circles, "ru")).toMatch(/Аня × Боря/);
  });
});
