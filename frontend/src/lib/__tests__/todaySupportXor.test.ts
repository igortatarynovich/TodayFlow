import type { TodayContractV1 } from "@/lib/todayContract";
import {
  pickLockedAffirmationLine,
  pickLockedSupportMode,
  pickLockedSupportSlot,
} from "@/lib/todaySupportXor";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "p" },
  personal_growth: { development_point: "d" },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
};

const persisted: TodayContractV1 = {
  ...base,
  personal_day: { natal_overlay: { focus_axis: "work" } },
};

describe("pickLockedSupportMode", () => {
  it("uses the existing F10 need-cell class, not catalog presence", () => {
    expect(pickLockedSupportMode(base)).toBeNull();
    expect(pickLockedSupportMode(persisted)).toBe("practice");
    expect(
      pickLockedSupportMode({
        ...persisted,
        day_story: {
          contract_version: "day_story_v1",
          practice_recommendation: {
            kind: "affirmation",
            text: "Я справлюсь с тем, что прямо сейчас.",
          },
        },
      }),
    ).toBe("practice");
  });

  it("omits guest, unavailable, and Global energy as a mode", () => {
    expect(
      pickLockedSupportMode({
        ...base,
        global_day: { primary_energy: "clarity" },
      }),
    ).toBeNull();
    expect(
      pickLockedSupportMode({
        ...persisted,
        day_story: { contract_version: "day_story_v1", interpretation_status: "unavailable" },
      }),
    ).toBeNull();
  });
});

describe("pickLockedSupportSlot", () => {
  it("paints practice XOR affirmation from the derived mode", () => {
    expect(pickLockedSupportSlot({ contract: persisted, practiceReady: true })).toBe("practice");
    expect(pickLockedSupportSlot({ contract: persisted, practiceReady: false })).toBeNull();
  });

  it("does not switch to scene affirmation when the practice branch is empty", () => {
    const withSceneAffirmation: TodayContractV1 = {
      ...persisted,
      day_story: {
        contract_version: "day_story_v1",
        practice_recommendation: {
          kind: "affirmation",
          text: "Я справлюсь с тем, что прямо сейчас.",
        },
        day_scenario: {
          props: {
            affirmations: [{ text: "Я справлюсь с тем, что прямо сейчас." }],
          },
          scenes: [{ recommended_action: "Назови одну вещь прямо.", trap: "Сгладить ради тишины." }],
        },
      },
    };
    expect(pickLockedAffirmationLine(withSceneAffirmation)).toBeNull();
    expect(pickLockedSupportSlot({ contract: withSceneAffirmation, practiceReady: false })).toBeNull();
    expect(pickLockedSupportSlot({ contract: withSceneAffirmation, practiceReady: true })).toBe("practice");
  });

  it("does not date-hash or fill from a leftover catalog item without F10", () => {
    expect(
      pickLockedSupportSlot({
        contract: {
          ...base,
          day_story: {
            contract_version: "day_story_v1",
            practice_recommendation: {
              kind: "affirmation",
              text: "Я спокоен.",
            },
          },
        },
        practiceReady: true,
      }),
    ).toBeNull();
  });
});
