import type { TodayContractV1 } from "@/lib/todayContract";
import { buildTodayNarrativeV1, splitPeriodNarrative } from "@/lib/todayNarrativeFromContract";

const sampleContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: {
    period: "Проживать день через устойчивость — лучше двигаться через понятный ритм, чем через резкие рывки.",
  },
  personal_growth: {
    development_point: "Сегодня полезно замечать момент, когда ты начинаешь ускоряться из тревоги.",
  },
  domains: {
    relationships: {
      status: "Сегодня в отношениях — прямой и спокойный контакт.",
      opportunity: "Прямой разговор поможет больше, чем попытка угадать настроение.",
      risk: "Молчание сегодня строит дистанцию.",
      action: "Скажи прямо одну вещь, которую обычно обходишь.",
    },
    money_work: {
      status: "Сегодня в работе и деньгах — один вектор.",
      opportunity: "Один завершённый результат сегодня полезнее пяти начатых задач.",
      risk: "Не бери новые обязательства из импульса.",
      action: "Выбери одну задачу и доведи её до видимого результата.",
    },
    family: {
      status: "Сегодня дома полезнее создавать спокойный ритм.",
      opportunity: "Спокойный ритм даст больше, чем контроль.",
      risk: "Не тащи контроль на близких.",
      action: "Сделай один бытовой шаг, который сделает дом спокойнее.",
    },
  },
  primary_action: "Выбери одну вещь, которую сегодня действительно доведёшь до конца.",
  progress: {},
  generation_id: "test-gen",
};

describe("splitPeriodNarrative", () => {
  it("splits em-dash period into headline and subline", () => {
    const out = splitPeriodNarrative(
      "Проживать день через устойчивость — лучше двигаться через понятный ритм, чем через резкие рывки.",
    );
    expect(out.headline.toLowerCase()).toContain("устойчив");
    expect(out.subline?.toLowerCase()).toContain("ритм");
  });
});

describe("buildTodayNarrativeV1", () => {
  it("builds unified story without slot labels", () => {
    const narrative = buildTodayNarrativeV1(sampleContract);
    expect(narrative.manifestations.length).toBe(3);
    expect(narrative.manifestations[0].line.toLowerCase()).toContain("отношения");
    expect(narrative.manifestations[1].line.toLowerCase()).toContain("работе");
    expect(narrative.manifestations[2].line.toLowerCase()).toContain("дома");
    expect(narrative.growthPoint.toLowerCase()).toContain("замечать");
    expect(narrative.primaryAction).toBe(sampleContract.primary_action);
  });

  it("does not repeat CRM slot structure in manifestation lines", () => {
    const narrative = buildTodayNarrativeV1(sampleContract);
    for (const item of narrative.manifestations) {
      expect(item.line).not.toMatch(/^(статус|возможность|риск|действие)/i);
    }
  });
});
