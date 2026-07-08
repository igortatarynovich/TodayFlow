export type TodayDayPhase = "morning" | "day" | "evening" | "night";

export type TodayDayGreeting = {
  salutation: string;
  line: string;
};

export function resolveTodayDayPhase(hour = new Date().getHours()): TodayDayPhase {
  if (hour >= 5 && hour < 11) return "morning";
  if (hour >= 11 && hour < 17) return "day";
  if (hour >= 17 && hour < 22) return "evening";
  return "night";
}

function formatName(name: string | null | undefined): string | null {
  const trimmed = name?.trim();
  if (!trimmed) return null;
  return trimmed.split(/\s+/)[0] ?? trimmed;
}

function salutationForPhase(phase: TodayDayPhase, name: string | null): string {
  const who = name ? `, ${name}` : "";
  switch (phase) {
    case "morning":
      return `Доброе утро${who}`;
    case "day":
      return `Добрый день${who}`;
    case "evening":
      return `Добрый вечер${who}`;
    case "night":
      return `Доброй ночи${who}`;
  }
}

export function buildTodayDayGreeting(input: {
  phase: TodayDayPhase;
  userName?: string | null;
  tagline: string;
  yesterdayClosed: boolean;
  todayOpened: boolean;
  isEveningSurface?: boolean;
  isFirstToday?: boolean;
}): TodayDayGreeting {
  const name = formatName(input.userName);
  const salutation = salutationForPhase(input.phase, name);

  if (input.isEveningSurface) {
    return {
      salutation,
      line: input.todayOpened
        ? "Сегодняшний день почти завершён. Осталось понять, что стоит забрать с собой в завтра."
        : "День подходит к концу. Несколько минут — и ты увидишь, что он уже рассказал о тебе.",
    };
  }

  if (input.isFirstToday && !input.todayOpened) {
    return {
      salutation,
      line: "Мы только что сверили первые линии карты — теперь посмотрим, как звучит твой день.",
    };
  }

  if (input.phase === "morning" && !input.todayOpened) {
    if (input.yesterdayClosed) {
      return {
        salutation,
        line: "Вчерашний день закрыт — сегодня можно начать с ясного темпа. " + softenTagline(input.tagline),
      };
    }
    return {
      salutation,
      line: "Сегодня многое будет зависеть от того, насколько спокойно ты задашь темп самому себе.",
    };
  }

  if (input.phase === "morning" || input.phase === "day") {
    return {
      salutation,
      line: input.todayOpened ? softenTagline(input.tagline) : "Начни с одной главной мысли — остальное подстроится под неё.",
    };
  }

  return {
    salutation,
    line: "Сегодняшний день уже многое показал. Сейчас важнее не ускоряться, а собрать итог.",
  };
}

function softenTagline(tagline: string): string {
  const t = tagline.replace(/[.!?]+$/, "").trim();
  if (!t) return "Сегодня лучше двигаться последовательно, чем быстро.";
  return t.charAt(0).toUpperCase() + t.slice(1) + ".";
}
