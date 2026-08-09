import {
  buildMakeYoursProposals,
  makeYoursOccupiedFromProgress,
} from "@/lib/todayMakeYoursProposals";
import type { TodayContractV1 } from "@/lib/todayContract";

function stubContract(partial: Partial<TodayContractV1["day_story"]> & { primary_action?: string }): TodayContractV1 {
  return {
    primary_action: partial.primary_action ?? null,
    day_story: {
      do: partial.do ?? [],
      avoid: partial.avoid ?? [],
      today_move: partial.today_move ?? null,
      practice_recommendation: partial.practice_recommendation ?? null,
    },
  } as TodayContractV1;
}

describe("buildMakeYoursProposals", () => {
  it("does not propose practice (practices have their own step)", () => {
    const proposals = buildMakeYoursProposals({
      contract: stubContract({
        practice_recommendation: {
          kind: "practice",
          text: "Дыхание 4-7-8",
          reason: "Снизить темп",
        },
        do: ["Сделай паузу в 15 минут"],
        today_move: "Сделай паузу в 15 минут",
      }),
      occupied: {},
    });
    expect(proposals.some((p) => (p as { categoryId: string }).categoryId === "practice")).toBe(
      false,
    );
    expect(proposals.some((p) => p.categoryId === "habit")).toBe(false);
    expect(proposals.some((p) => p.categoryId === "affirmation")).toBe(false);
  });

  it("proposes ascetic from practice_recommendation when empty", () => {
    const proposals = buildMakeYoursProposals({
      contract: stubContract({
        practice_recommendation: {
          kind: "ascetic",
          text: "Без сахара",
          reason: "Снять шум",
        },
      }),
      occupied: {},
    });
    expect(proposals.find((p) => p.categoryId === "ascetic")?.title).toBe("Без сахара");
  });

  it("does not invent mantra or habit from day move", () => {
    const proposals = buildMakeYoursProposals({
      contract: stubContract({
        do: ["Короткая прогулка"],
        today_move: "Короткая прогулка",
      }),
      occupied: {},
    });
    expect(proposals.some((p) => p.categoryId === "mantra")).toBe(false);
    expect(proposals.some((p) => p.categoryId === "habit")).toBe(false);
  });

  it("proposes goal from dayGoal without inventing when signals empty", () => {
    expect(
      buildMakeYoursProposals({
        contract: stubContract({}),
        occupied: {},
      }),
    ).toEqual([]);
    const withGoal = buildMakeYoursProposals({
      contract: stubContract({}),
      occupied: {},
      dayGoal: "Дойти до вечера спокойно",
    });
    expect(withGoal.find((p) => p.categoryId === "goal")?.title).toBe("Дойти до вечера спокойно");
  });
});

describe("makeYoursOccupiedFromProgress", () => {
  it("maps habit/ascetic and extras; ignores practice kind for Make yours", () => {
    expect(makeYoursOccupiedFromProgress(["habit", "practice"], { goal: true })).toEqual({
      habit: true,
      goal: true,
    });
  });
});
