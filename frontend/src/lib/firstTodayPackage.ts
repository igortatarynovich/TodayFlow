import type { CoreProfile } from "@/lib/types";
import type { TodayContractV1, TodayContractDomainId } from "@/lib/todayContract";
import type { IntentTheme, RealityState } from "@/lib/onboardingContext";

export type FirstTodayInsightSphere = {
  id: TodayContractDomainId;
  label: string;
  line: string;
};

export type FirstTodayPackage = {
  theme: {
    headline: string;
    body: string;
  };
  progress: {
    dayNumber: 1;
    statusLabel: string;
    hint: string;
    nextMicroWin: string;
  };
  insight: {
    spheres: FirstTodayInsightSphere[];
  };
  action: {
    primary: string;
    afterComplete: string;
    supports: string[];
  };
  why: {
    lines: string[];
  };
  depth: {
    label: string;
    href: string;
  };
  symbolic: {
    tarot: string | null;
    number: string | null;
  };
};

const INTENT_ANGLE: Record<IntentTheme, string> = {
  focus: "день одной главной задачи",
  energy: "день энергии и темпа",
  relationships: "день контакта и близости",
  money: "день ясности по ресурсам",
  clarity: "день решений без шума",
  calm: "день спокойного ритма",
};

const INTENT_ACTION: Record<IntentTheme, string> = {
  focus: "Выбери одну главную задачу и закрой её до обеда — без переключений.",
  energy: "Сделай 10 минут движения или прогулки, чтобы вернуть телу темп.",
  relationships: "Напиши или позвони одному человеку, с кем важно быть на связи сегодня.",
  money: "Открой одну цифру или счёт и прими одно конкретное решение по ресурсам.",
  clarity: "Запиши три варианта — вычеркни один лишний и оставь два для сравнения.",
  calm: "Отложи лишнее на 30 минут и сделай одно дело в тишине, без уведомлений.",
};

const INTENT_LABEL: Record<IntentTheme, string> = {
  focus: "фокус",
  energy: "энергия",
  relationships: "отношения",
  money: "деньги",
  clarity: "ясность",
  calm: "спокойствие",
};

const REALITY_LABEL: Record<RealityState, string> = {
  overloaded: "перегруз",
  stable: "стабильный ритм",
  unclear: "нет ясности",
  tired: "усталость",
  motivated: "есть энергия",
  sensitive: "чувствительность",
};

const DOMAIN_LABEL: Record<TodayContractDomainId, string> = {
  relationships: "Отношения",
  money_work: "Деньги и работа",
  family: "Дом и опора",
};

const INTENT_DOMAIN_ORDER: Record<IntentTheme, TodayContractDomainId[]> = {
  focus: ["money_work", "relationships", "family"],
  energy: ["family", "money_work", "relationships"],
  relationships: ["relationships", "family", "money_work"],
  money: ["money_work", "relationships", "family"],
  clarity: ["money_work", "family", "relationships"],
  calm: ["family", "relationships", "money_work"],
};

const REALITY_THEME_TAIL: Partial<Record<RealityState, string>> = {
  overloaded: " Сегодня лучше не разгонять темп — один шаг за раз.",
  tired: " Береги силы: достаточно одного честного шага.",
  motivated: " Есть запас — направь его в выбранный фокус.",
  sensitive: " День может быть тоньше обычного — без резких решений.",
  unclear: " Не нужно всё понять сразу — достаточно одного ориентира.",
};

const REALITY_ACTION_TAIL: Partial<Record<RealityState, string>> = {
  overloaded: " Если тяжело — сократи шаг до 5 минут, но сделай его.",
  tired: " Можно упростить до минимума, главное — начать.",
};

const DEFAULT_INTENT: IntentTheme = "focus";
const DEFAULT_REALITY: RealityState = "stable";

function displayName(coreProfile: CoreProfile | null): string | null {
  const name =
    coreProfile?.person?.first_name?.trim() ||
    coreProfile?.person?.display_name?.trim() ||
    null;
  return name;
}

function identitySlice(coreProfile: CoreProfile | null): string {
  const sun = coreProfile?.astro?.sun_sign?.trim();
  const lifePath = coreProfile?.numerology?.life_path;
  const parts: string[] = [];
  if (sun) parts.push(`Солнце в ${sun}`);
  if (lifePath != null) parts.push(`число пути ${lifePath}`);
  if (parts.length === 0) return "Твоя карта уже собрана — Today опирается на дату и место рождения.";
  return `Опора дня — ${parts.join(" и ")}.`;
}

function domainLine(contract: TodayContractV1 | null | undefined, id: TodayContractDomainId): string {
  const domain = contract?.domains?.[id];
  const candidate = domain?.opportunity?.trim() || domain?.status?.trim();
  if (candidate) return candidate;
  if (id === "relationships") return "Контакт и близость — зона, где сегодня полезно быть внимательнее.";
  if (id === "money_work") return "Работа и ресурсы — место для одного ясного решения.";
  return "Дом и опора — опирайся на то, что уже поддерживает.";
}

function depthCta(intent: IntentTheme): { label: string; href: string } {
  if (intent === "relationships") {
    return { label: "Разобрать отношения глубже", href: "/tarot?topic=relationships" };
  }
  if (intent === "money") {
    return { label: "Разобрать деньги и работу", href: "/tarot?topic=money" };
  }
  return { label: "Открыть карту личности", href: "/profile" };
}

export function buildFirstTodayPackage(input: {
  coreProfile: CoreProfile | null;
  intentTheme?: IntentTheme | null;
  realityState?: RealityState | null;
  contract?: TodayContractV1 | null;
  cardName?: string | null;
  numerologyValue?: string | null;
}): FirstTodayPackage {
  const intent = input.intentTheme ?? DEFAULT_INTENT;
  const reality = input.realityState ?? DEFAULT_REALITY;
  const name = displayName(input.coreProfile);
  const angle = INTENT_ANGLE[intent];
  const headline = name ? `${name}, сегодня — ${angle}.` : `Сегодня — ${angle}.`;

  const realityTail = REALITY_THEME_TAIL[reality] ?? "";
  const body = `${identitySlice(input.coreProfile)} Ты выбрал(а) ${INTENT_LABEL[intent]} как приоритет.${realityTail}`;

  let primaryAction = INTENT_ACTION[intent];
  const contractAction = input.contract?.primary_action?.trim();
  if (contractAction && contractAction.length > 12) {
    primaryAction = contractAction;
  }
  primaryAction += REALITY_ACTION_TAIL[reality] ?? "";

  const domainOrder = INTENT_DOMAIN_ORDER[intent];
  const spheres: FirstTodayInsightSphere[] = domainOrder.map((id) => ({
    id,
    label: DOMAIN_LABEL[id],
    line: domainLine(input.contract, id),
  }));

  const whyLines = [
    identitySlice(input.coreProfile),
    `Приоритет дня: ${INTENT_LABEL[intent]}.`,
    `Состояние: ${REALITY_LABEL[reality]}.`,
  ];

  const depth = depthCta(intent);

  return {
    theme: { headline, body },
    progress: {
      dayNumber: 1,
      statusLabel: "День 1 · первый шаг впереди",
      hint: "Прогресс появится после первых отметок — сегодня начало пути.",
      nextMicroWin: primaryAction.split(".")[0]?.trim() || primaryAction,
    },
    insight: { spheres },
    action: {
      primary: primaryAction,
      afterComplete: "Шаг зафиксирован. Завтра Today станет точнее — продолжим с этого места.",
      supports: [
        "Один шаг без давления — этого достаточно для первого дня.",
        "Вечером можно коротко отметить итог — это улучшит завтрашний ориентир.",
      ],
    },
    why: { lines: whyLines },
    depth,
    symbolic: {
      tarot: input.cardName?.trim() || null,
      number: input.numerologyValue?.trim() || null,
    },
  };
}
