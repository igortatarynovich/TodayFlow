import { buildTodayCompositionViewModel, applyGuideNarrativeToCompositionViewModel } from "@/lib/todayCompositionModel";
import {
  applySupplementaryNarrativesToDayStory,
  buildTodayDayStoryViewModel,
} from "@/lib/todayDayStoryModel";
import type { TodayContractV1 } from "@/lib/todayContract";
import { createEmptyDayEngagement } from "@/lib/todayDayEngagement";

const sampleContract: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "День ясности — спокойный ритм и одна главная линия." },
  personal_growth: { development_point: "Замедлиться и услышать себя." },
  domains: {
    relationships: {
      status: "сегодня в отношениях — больше слушать",
      opportunity: "мягкий контакт без давления",
      risk: "спешить с выводами",
      action: "Напиши одному близкому человеку.",
    },
    money_work: {
      status: "сегодня в работе — ясность",
      opportunity: "закрыть одну задачу",
      risk: "распыление",
      action: "Выбери одну задачу и закрой до обеда.",
    },
    family: {
      status: "сегодня дома — тишина",
      opportunity: "короткий разговор",
      risk: "перегруз",
      action: "Удели 10 минут семье без экрана.",
    },
  },
  primary_action: "Сделай одну главную задачу до обеда.",
  progress: {},
  generation_id: "test-gen",
};

const sampleContractWithDayStory: TodayContractV1 = {
  ...sampleContract,
  day_story: {
    contract_version: "day_story_v1",
    theme: "Один приоритет без суеты.",
    direction: "Сегодня выигрывает ясность одного выбора.",
    story: "Утром лучше не распыляться. Выбери одну линию и держи её до вечера.",
    do: ["Закрыть одну задачу до обеда"],
    avoid: ["Брать лишние созвоны"],
  },
};

describe("applySupplementaryNarrativesToDayStory", () => {
  function buildStory() {
    const vm = applyGuideNarrativeToCompositionViewModel(
      buildTodayCompositionViewModel({
        contract: sampleContract,
        cardName: "Сила",
        cardMeaning: null,
        numerologyValue: "4",
        numerologyMeaning: null,
        morningRitualData: null,
      }),
      { headline: "Один приоритет в работе" },
    );
    const engagement = {
      ...createEmptyDayEngagement(),
      tarotPickedId: 8,
      tarotPickedName: "Сила",
      numberConfirmed: true,
    };
    return buildTodayDayStoryViewModel({
      base: vm,
      contract: sampleContract,
      dateISO: "2026-07-05",
      cardName: "Сила",
      cardMeaning: null,
      numerologyValue: "4",
      numerologyMeaning: null,
      morningRitualData: null,
      yesterdayClosed: false,
      todayOpened: true,
      engagement,
    });
  }

  it("overlays day_layer nudge into pulse", () => {
    const story = applySupplementaryNarrativesToDayStory(buildStory(), sampleContract, {
      dayLayerPayload: { nudge_message: "Сегодня лучше держать один темп." },
    });
    expect(story.pulse).toBe("Сегодня лучше держать один темп.");
  });

  it("overlays spheres scenario tie-ins into sphere focus", () => {
    const story = applySupplementaryNarrativesToDayStory(buildStory(), sampleContract, {
      spheresPayload: {
        scenario_tie_ins: {
          career: "В работе — завершение, а не новый заход.",
          love: "В любви — ясность намерения.",
        },
      },
    });
    const peak = story.sphereFocus.cards.find((c) => c.role === "peak");
    expect(peak?.body).toMatch(/работе|любви/i);
  });

  it("overlays evening closure into reflection prompt", () => {
    const story = applySupplementaryNarrativesToDayStory(buildStory(), sampleContract, {
      eveningPayload: { closure_invitation: "Закрой день: что получилось и что оставить на завтра." },
    });
    expect(story.eveningReflectionPrompt).toMatch(/закрой день/i);
  });

  it("skips supplementary overlays when day_story is authoritative", () => {
    function buildStoryWithDayStory() {
      const vm = buildTodayCompositionViewModel({
        contract: sampleContractWithDayStory,
        cardName: "Сила",
        cardMeaning: null,
        numerologyValue: "4",
        numerologyMeaning: null,
        morningRitualData: null,
      });
      const engagement = {
        ...createEmptyDayEngagement(),
        tarotPickedId: 8,
        tarotPickedName: "Сила",
        numberConfirmed: true,
      };
      return buildTodayDayStoryViewModel({
        base: vm,
        contract: sampleContractWithDayStory,
        dateISO: "2026-07-05",
        cardName: "Сила",
        cardMeaning: null,
        numerologyValue: "4",
        numerologyMeaning: null,
        morningRitualData: null,
        yesterdayClosed: false,
        todayOpened: true,
        engagement,
      });
    }

    const before = buildStoryWithDayStory();
    const after = applySupplementaryNarrativesToDayStory(before, sampleContractWithDayStory, {
      dayLayerPayload: { nudge_message: "Другой голос из day_layer." },
      spheresPayload: {
        scenario_tie_ins: { career: "Чужая линия про работу." },
      },
      eveningPayload: { closure_invitation: "Чужой вечерний текст." },
    });
    expect(after.pulse).toBe(before.pulse);
    expect(after.eveningReflectionPrompt).toBe(before.eveningReflectionPrompt);
  });
});
