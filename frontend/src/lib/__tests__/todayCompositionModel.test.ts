import type { TodayContractV1 } from "@/lib/todayContract";
import {
  applyEngagementToViewModel,
  applyGuideNarrativeToCompositionViewModel,
  applyRecommendedPracticeToStrengthen,
  buildTodayCompositionViewModel,
} from "@/lib/todayCompositionModel";

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

describe("buildTodayCompositionViewModel", () => {
  it("builds day panel with deduped hero and entity cards", () => {
    const vm = buildTodayCompositionViewModel({
      contract: sampleContract,
      cardName: "Сила",
      cardMeaning: "внутренняя опора",
      numerologyValue: "4",
      numerologyMeaning: "структура и порядок",
      morningRitualData: {
        date: "2026-06-23",
        celestial_events: { lunar_phase: { name: "Полнолуние", themes: "эмоциональная ясность" } },
      },
      colorLine: "синий",
      stoneLine: "лазурит",
    });

    expect(vm.hero.centralThought).toMatch(/Сегодня/i);
    expect(vm.hero.themeShort).toBeTruthy();
    expect(vm.hero.themeHeadline).not.toMatch(/устойчивость через понятный ритм/i);
    expect(vm.hero.tagline).toBeTruthy();
    expect(vm.influences.some((i) => i.kind === "tarot")).toBe(true);
    expect(vm.influences.some((i) => i.kind === "moon")).toBe(true);
    expect(vm.supported.length).toBeGreaterThan(0);
    expect(vm.strengthen).toHaveLength(5);
    expect(vm.actions).toHaveLength(4);
    expect(vm.growthArc.length).toBeGreaterThan(0);

    const allPractice = vm.strengthen.find((t) => t.id === "practice")?.title ?? "";
    const allIntention = vm.strengthen.find((t) => t.id === "intention")?.title ?? "";
    expect(allPractice.toLowerCase()).not.toBe(allIntention.toLowerCase());
  });

  it("adjusts affirmation when user picks tarot", () => {
    const vm = buildTodayCompositionViewModel({
      contract: sampleContract,
      cardName: "Сила",
      cardMeaning: null,
      numerologyValue: "4",
      numerologyMeaning: null,
      morningRitualData: null,
    });

    const adjusted = applyEngagementToViewModel(vm, {
      dayGoal: null,
      practiceStarted: false,
      practiceCompleted: false,
      recommendedPracticeId: null,
      tarotPickedId: 8,
      tarotPickedName: "Отшельник",
      numberConfirmed: false,
      affirmationRead: false,
      todayOpened: false,
      morningMoodId: null,
      morningMoodCapturedAtMs: null,
      focusTopicId: null,
      focusTopicCapturedAtMs: null,
      eveningHighlightId: null,
      tarotResonance: null,
      numberResonance: null,
    });

    const affirmation = adjusted.strengthen.find((t) => t.id === "affirmation");
    expect(affirmation?.title).toMatch(/Отшельник/);
  });

  it("overlays catalog practice onto strengthen practice card", () => {
    const vm = buildTodayCompositionViewModel({
      contract: sampleContract,
      cardName: "Сила",
      cardMeaning: null,
      numerologyValue: "4",
      numerologyMeaning: null,
      morningRitualData: null,
    });

    const merged = applyRecommendedPracticeToStrengthen(vm.strengthen, {
      id: "breath-3",
      title: "Дыхание 4-7-8",
      description: "Успокоить нервную систему перед решением.",
      duration_minutes: 5,
    });

    const practice = merged.find((t) => t.id === "practice");
    expect(practice?.title).toBe("Дыхание 4-7-8");
    expect(practice?.duration).toBe("5 мин");
  });

  it("replaces generic rhythm cliché in hero headline", () => {
    const vm = buildTodayCompositionViewModel({
      contract: {
        ...sampleContract,
        global_context: {
          period: "Проживать день через устойчивость через понятный ритм и действовать ровно и без суеты.",
        },
      },
      cardName: "Сила",
      cardMeaning: "внутренняя опора",
      numerologyValue: "4",
      numerologyMeaning: "структура",
      morningRitualData: null,
    });
    expect(vm.hero.themeHeadline).not.toMatch(/устойчивость через понятный ритм/i);
    expect(vm.hero.centralThought).not.toMatch(/действовать/i);
  });

  it("overlays guide narrative headline and primary action", () => {
    const vm = buildTodayCompositionViewModel({
      contract: sampleContract,
      cardName: "Сила",
      cardMeaning: null,
      numerologyValue: "4",
      numerologyMeaning: null,
      morningRitualData: null,
    });
    const merged = applyGuideNarrativeToCompositionViewModel(vm, {
      headline: "Сегодня один приоритет в работе",
      core_message: {
        body: "День просит сфокусироваться на одной задаче до обеда.",
        best_move: "Закрой одну задачу до 13:00",
      },
    });
    expect(merged.hero.themeHeadline).toBe("Сегодня один приоритет в работе");
    expect(merged.focusTitle).toBe("Закрой одну задачу до 13:00");
  });
});
