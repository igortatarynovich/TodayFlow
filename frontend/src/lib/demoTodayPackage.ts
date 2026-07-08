import { selectColdState, type ColdState } from "@/lib/coldStart";

export type GuestTodayPackage = {
  coldStateId: string;
  theme: {
    headline: string;
    body: string;
  };
  insight: {
    label: string;
    body: string;
  };
  action: {
    primary: string;
    afterComplete: string;
  };
  progress: {
    statusLabel: string;
    hint: string;
  };
};

function themeHeadline(state: ColdState): string {
  const phrase = state.keyPhrase.trim();
  if (!phrase) return "Сегодня полезно замедлиться и выбрать один фокус.";
  const first = phrase.charAt(0).toUpperCase() + phrase.slice(1);
  return `Сегодня может быть заметно: ${first}.`;
}

export function buildGuestTodayPackage(state: ColdState = selectColdState()): GuestTodayPackage {
  return {
    coldStateId: state.id,
    theme: {
      headline: themeHeadline(state),
      body: state.explanation,
    },
    insight: {
      label: "Ориентир без профиля",
      body: "Это общий ритм дня — без даты рождения и карты. После регистрации тот же формат станет персональным.",
    },
    action: {
      primary: state.microAction.instruction,
      afterComplete: state.microAction.completionMessage,
    },
    progress: {
      statusLabel: "Демо · без сохранения",
      hint: "Собери свой профиль — и здесь появится «День 1 · первый шаг впереди» с реальным прогрессом.",
    },
  };
}
