import type { PracticeStateAfter } from "@/lib/practicesPage/practiceSessionDraft";

export function practiceSessionCopy(locale: "ru" | "en") {
  if (locale === "en") {
    return {
      startCta: "Start",
      resumeCta: "Resume",
      closeAria: "Close session",
      pause: "Pause",
      resume: "Resume",
      soundOn: "Sound on",
      soundOff: "Sound off",
      finishEarly: "Finish",
      instructionFallback: "Follow the pace. Pause when you need to.",
      checkinTitle: "How do you feel now?",
      checkinBetter: "Better",
      checkinSame: "No change",
      checkinHarder: "Harder",
      saveToToday: "Save result to today",
      saving: "Saving…",
      savedTitle: "Saved to today",
      savedBody: "This practice is part of your day now.",
      openToday: "Open Today",
      backToPractices: "Back to Practices",
      loginToSave: "Sign in to save this into your day",
      loginCta: "Sign in",
      skipSave: "Close without saving",
      timerDone: "Done",
    };
  }

  return {
    startCta: "Начать",
    resumeCta: "Продолжить",
    closeAria: "Закрыть сессию",
    pause: "Пауза",
    resume: "Продолжить",
    soundOn: "Звук вкл.",
    soundOff: "Звук выкл.",
    finishEarly: "Завершить",
    instructionFallback: "Идите в своём темпе. Пауза — когда нужно.",
    checkinTitle: "Как вы себя чувствуете сейчас?",
    checkinBetter: "Лучше",
    checkinSame: "Без изменений",
    checkinHarder: "Сложнее",
    saveToToday: "Сохранить результат в сегодняшний день",
    saving: "Сохраняем…",
    savedTitle: "Сохранено в сегодняшний день",
    savedBody: "Практика теперь часть вашего дня.",
    openToday: "Открыть Сегодня",
    backToPractices: "К практикам",
    loginToSave: "Войдите, чтобы сохранить результат в день",
    loginCta: "Войти",
    skipSave: "Закрыть без сохранения",
    timerDone: "Готово",
  };
}

export function stateAfterLabel(
  locale: "ru" | "en",
  state: PracticeStateAfter,
): string {
  const copy = practiceSessionCopy(locale);
  if (state === "better") return copy.checkinBetter;
  if (state === "harder") return copy.checkinHarder;
  return copy.checkinSame;
}
