import { pickInstructionPersonalBridge } from "@/lib/todayInstructionBridge";
import type { TodayContractV1 } from "@/lib/todayContract";

const base: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "Пауза" },
  personal_growth: { development_point: "Оставлять темп ровным." },
  domains: {
    work: { status: "s", opportunity: "o", risk: "r", action: "a" },
    money: { status: "s", opportunity: "o", risk: "r", action: "a" },
    relationships: { status: "s", opportunity: "o", risk: "r", action: "a" },
    energy: { status: "s", opportunity: "o", risk: "r", action: "a" },
  },
};

describe("pickInstructionPersonalBridge", () => {
  it("prefers why_personal over kitchen astrology summary", () => {
    const lead = pickInstructionPersonalBridge({
      ...base,
      day_story: {
        contract_version: "day_story_v1",
        day_personal: {
          personal_astrology: {
            summary_ru:
              "Профекция года (возраст 36): 1-й дом, управитель Сатурн. Solar return 2026.",
            beats: [
              {
                kind: "natal_transit",
                story_ru: "Создаёт напряжение, которое просит осознанного выбора.",
              },
            ],
          },
        },
        day_scenario: {
          conflict: {
            why_personal:
              "У тебя отклик на задачи идёт через тело — «угу» или «у-у» в животе раньше, чем мысль.",
          },
        },
      },
    });
    expect(lead).toContain("через тело");
    expect(lead).not.toMatch(/профекц|Solar return|управител/i);
  });

  it("falls back to soft natal transit when why_personal empty", () => {
    const lead = pickInstructionPersonalBridge({
      ...base,
      day_story: {
        contract_version: "day_story_v1",
        day_personal: {
          personal_astrology: {
            beats: [
              {
                kind: "natal_transit",
                story_ru: "Создаёт напряжение, которое просит осознанного выбора.",
              },
            ],
          },
        },
      },
    });
    expect(lead).toContain("осознанного выбора");
  });

  it("omits when only kitchen dump is available", () => {
    const lead = pickInstructionPersonalBridge({
      ...base,
      personal_growth: { development_point: "" },
      day_story: {
        contract_version: "day_story_v1",
        day_personal: {
          summary_ru: "Профекция года (возраст 36): управитель Сатурн. 1.1°.",
        },
      },
    });
    expect(lead).toBeNull();
  });
});
