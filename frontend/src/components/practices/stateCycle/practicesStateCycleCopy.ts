import type { PracticeCanonLocale } from "@/lib/practicesPage/practicesCanon";

export function practicesStateCycleCopy(locale: PracticeCanonLocale) {
  if (locale === "en") {
    return {
      pageTitle: "Practices",
      pageSubtitle: "Choose what you need right now",
      favoritesAria: "Saved practices",
      recommendedEyebrow: "Recommended now",
      startCta: "Start",
      continueEyebrow: "Continue",
      continueProgress: (done: number, total: number) => `${done} of ${total} min done`,
      continueCta: "Resume",
      momentTitle: "For this moment",
      seeAll: "See all",
      formatsTitle: "Formats",
      practiceOfDayEyebrow: "Practice of the day",
      practiceOfDayFallbackEyebrow: "From the catalog",
      myPracticesTitle: "My practices",
      myRecent: "Recent",
      mySaved: "Saved",
      minutesShort: "min",
      catalogFailed: "Couldn’t load practices.",
      retry: "Retry",
      emptyMoment: "No matches for this need yet — try another or open Formats below.",
      emptyLibrary: "Finish or save a practice — your library will appear here.",
      todayRailTitle: "Today",
      todayRailMood: "Mood",
      todayRailGoal: "Day focus",
      todayRailDone: "Practice done",
      todayRailEmpty: "Open Today to set the day’s tone.",
      resultLineFallback: "A practice for your current need",
    };
  }

  return {
    pageTitle: "Практики",
    pageSubtitle: "Выберите, что вам сейчас нужно",
    favoritesAria: "Сохранённые практики",
    recommendedEyebrow: "Рекомендовано сейчас",
    startCta: "Начать",
    continueEyebrow: "Продолжить",
    continueProgress: (done: number, total: number) => `Пройдено ${done} из ${total} минут`,
    continueCta: "Продолжить",
    momentTitle: "Практики для текущего момента",
    seeAll: "Смотреть все",
    formatsTitle: "Форматы",
    practiceOfDayEyebrow: "Практика дня",
    practiceOfDayFallbackEyebrow: "Из каталога",
    myPracticesTitle: "Мои практики",
    myRecent: "Недавние",
    mySaved: "Сохранённые",
    minutesShort: "мин",
    catalogFailed: "Не удалось загрузить практики.",
    retry: "Повторить",
    emptyMoment: "Пока нет совпадений под это состояние — выберите другое или откройте форматы ниже.",
    emptyLibrary: "Пройдите или сохраните практику — библиотека появится здесь.",
    todayRailTitle: "Сегодня",
    todayRailMood: "Настроение",
    todayRailGoal: "Цель дня",
    todayRailDone: "Практика",
    todayRailEmpty: "Откройте Сегодня, чтобы задать тон дня.",
    resultLineFallback: "Практика под текущую потребность",
  };
}

export type PracticesStateCycleCopy = ReturnType<typeof practicesStateCycleCopy>;
