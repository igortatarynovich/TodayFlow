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
  it("proposes practice from practice_recommendation when empty", () => {
    const proposals = buildMakeYoursProposals({
      contract: stubContract({
        practice_recommendation: {
          kind: "practice",
          text: "Дыхание 4-7-8",
          reason: "Снизить темп",
        },
      }),
      occupied: {},
    });
    expect(proposals.find((p) => p.categoryId === "practice")?.title).toBe("Дыхание 4-7-8");
  });

  it("skips occupied practice and does not invent mantra", () => {
    const proposals = buildMakeYoursProposals({
      contract: stubContract({
        do: ["Короткая прогулка"],
        practice_recommendation: { kind: "practice", text: "Йога", reason: null },
      }),
      occupied: { practice: true, habit: true },
    });
    expect(proposals.some((p) => p.categoryId === "practice")).toBe(false);
    expect(proposals.some((p) => p.categoryId === "mantra")).toBe(false);
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
  it("maps progress kinds and extras", () => {
    expect(makeYoursOccupiedFromProgress(["habit", "practice"], { goal: true })).toEqual({
      habit: true,
      practice: true,
      goal: true,
    });
  });
});
