// Утилиты для вычисления Personal Lens из данных пользователя

import type { InternalModelSnapshot } from "./types";

export interface PersonalLensData {
  core_archetype: string[];
  top_axes: Array<{
    axis_id: string;
    value: number;
    pole: "left" | "right";
    absValue: number;
  }>;
  stress_profile: {
    sensitivity: number;
    adaptation_speed: number;
    reflection_capacity: number;
    external_pressure: number;
  };
  dominant_domains: string[];
  relational_style?: string;
  decision_style?: string;
}

export interface LensChip {
  id: string;
  category: "ТЕМА" | "ПАТТЕРН" | "СТРЕСС" | "ОТНОШЕНИЯ" | "РЕШЕНИЯ";
  name: string;
  description?: string;
  content?: {
    whatItMeans: string;
    howItManifests: string[];
    whatToDo: {
      text: string;
      cta: string;
      href: string;
    };
    whereUsed: string[];
  };
}

const axisNames: Record<string, string> = {
  A1: "Ориентация идентичности",
  A2: "Выражение эмоций",
  A3: "Принятие решений",
  A4: "Отношение к изменениям",
  A5: "Стиль контроля",
  A6: "Ориентация в отношениях",
  A7: "Управление энергией",
};

const axisPoles: Record<string, { left: string; right: string }> = {
  A1: { left: "Внутренняя ориентация", right: "Внешняя ориентация" },
  A2: { left: "Сдержанный", right: "Экспрессивный" },
  A3: { left: "Интуитивный", right: "Аналитический" },
  A4: { left: "Стабильность", right: "Изменения" },
  A5: { left: "Адаптивный", right: "Директивный" },
  A6: { left: "Независимый", right: "Ориентированный на связи" },
  A7: { left: "Консервативный", right: "Экспансивный" },
};

const coreThemes: Record<string, string[]> = {
  // Темы на основе комбинаций осей
  stability_seeker: ["Поиск опоры", "Нужна стабильность"],
  change_seeker: ["Открытость к изменениям", "Гибкость"],
  external_focus: ["Ориентация на внешнюю реакцию", "Обратная связь важна"],
  internal_focus: ["Внутренние ориентиры", "Самоопределение"],
  expressive: ["Эмоциональная открытость", "Выражение чувств"],
  contained: ["Эмоциональная сдержанность", "Внутренняя обработка"],
};

/**
 * Вычисляет Personal Lens из данных пользователя
 */
export function computePersonalLens(
  internalModel: InternalModelSnapshot | undefined,
  sun?: string,
  moon?: string,
  rising?: string
): PersonalLensData | null {
  if (!internalModel || !internalModel.axes || internalModel.axes.length === 0) {
    return null;
  }

  // Топ-2 оси по выраженности
  const topAxes = [...internalModel.axes]
    .map((axis) => ({
      ...axis,
      absValue: Math.abs(axis.value),
    }))
    .sort((a, b) => b.absValue - a.absValue)
    .slice(0, 2)
    .map((axis) => ({
      axis_id: axis.axis_id,
      value: axis.value,
      pole: axis.value > 0 ? ("right" as const) : ("left" as const),
      absValue: Math.abs(axis.value),
    }));

  // Core archetype на основе топ-осей и знаков
  const coreArchetype: string[] = [];
  const topAxis = topAxes[0];
  
  if (topAxis) {
    if (topAxis.axis_id === "A4" && topAxis.value < 0) {
      coreArchetype.push("Поиск опоры");
    } else if (topAxis.axis_id === "A4" && topAxis.value > 0) {
      coreArchetype.push("Открытость к изменениям");
    } else if (topAxis.axis_id === "A1" && topAxis.value > 0) {
      coreArchetype.push("Ориентация на внешнюю реакцию");
    } else if (topAxis.axis_id === "A1" && topAxis.value < 0) {
      coreArchetype.push("Внутренние ориентиры");
    } else if (topAxis.axis_id === "A2" && topAxis.value > 0) {
      coreArchetype.push("Эмоциональная открытость");
    } else if (topAxis.axis_id === "A2" && topAxis.value < 0) {
      coreArchetype.push("Эмоциональная сдержанность");
    }
  }

  // Если нет темы, используем общую
  if (coreArchetype.length === 0) {
    coreArchetype.push("Уникальная комбинация паттернов");
  }

  // Stress profile из модуляторов
  const modulators = internalModel.modulators || [];
  const m1 = modulators.find((m) => m.modulator_id === "M1");
  const m2 = modulators.find((m) => m.modulator_id === "M2");
  const m3 = modulators.find((m) => m.modulator_id === "M3");
  const m4 = modulators.find((m) => m.modulator_id === "M4");

  const stressProfile = {
    sensitivity: m1 ? normalizeModulator(m1.value) : 0.5,
    adaptation_speed: m2 ? normalizeModulator(m2.value) : 0.5,
    reflection_capacity: m3 ? normalizeModulator(m3.value) : 0.5,
    external_pressure: m4 ? normalizeModulator(m4.value) : 0.5,
  };

  // Dominant domains на основе осей
  const dominantDomains: string[] = [];
  const a6 = internalModel.axes.find((a) => a.axis_id === "A6");
  const a5 = internalModel.axes.find((a) => a.axis_id === "A5");
  const a4 = internalModel.axes.find((a) => a.axis_id === "A4");

  if (a6 && Math.abs(a6.value) > 0.5) {
    dominantDomains.push("Любовь");
  }
  if (a5 && Math.abs(a5.value) > 0.5) {
    dominantDomains.push("Карьера");
  }
  if (a4 && Math.abs(a4.value) > 0.5) {
    dominantDomains.push("Деньги");
  }
  if (a6 && Math.abs(a6.value) > 0.3) {
    dominantDomains.push("Семья");
  }
  if (dominantDomains.length === 0) {
    dominantDomains.push("Жизненные темы");
  }

  // Relational style из A6
  let relationalStyle: string | undefined;
  if (a6) {
    relationalStyle = a6.value > 0.5
      ? "Ориентированный на связи"
      : a6.value < -0.5
      ? "Независимый"
      : "Балансирующий";
  }

  // Decision style из A3
  const a3 = internalModel.axes.find((a) => a.axis_id === "A3");
  let decisionStyle: string | undefined;
  if (a3) {
    decisionStyle = a3.value > 0.5
      ? "Аналитический"
      : a3.value < -0.5
      ? "Интуитивный"
      : "Сбалансированный";
  }

  return {
    core_archetype: coreArchetype,
    top_axes: topAxes,
    stress_profile: stressProfile,
    dominant_domains: dominantDomains.slice(0, 3),
    relational_style: relationalStyle,
    decision_style: decisionStyle,
  };
}

/**
 * Нормализует значение модулятора от -100/+100 к 0-1
 */
function normalizeModulator(value: number): number {
  return (value + 100) / 200;
}

/**
 * Преобразует PersonalLensData в массив LensChip для UI
 */
export function lensDataToChips(
  lens: PersonalLensData,
  axes: InternalModelSnapshot["axes"] = []
): LensChip[] {
  const chips: LensChip[] = [];

  // Core Theme (обязательный)
  if (lens.core_archetype.length > 0) {
    const theme = lens.core_archetype[0];
    chips.push({
      id: "core-theme",
      category: "ТЕМА",
      name: theme,
      description: "Главная жизненная тема",
      content: {
        whatItMeans: getThemeDescription(theme, lens),
        howItManifests: getThemeManifestations(theme, lens),
        whatToDo: {
          text: getThemeAction(theme),
          cta: "Открыть практику",
          href: "/practices",
        },
        whereUsed: ["Практики", "Карта дня", "Журналы"],
      },
    });
  }

  // Top Axis (обязательный)
  if (lens.top_axes.length > 0) {
    const topAxis = lens.top_axes[0];
    const axisName = axisNames[topAxis.axis_id] || topAxis.axis_id;
    const pole = axisPoles[topAxis.axis_id]?.[topAxis.pole] || "";
    
    chips.push({
      id: "top-axis",
      category: "ПАТТЕРН",
      name: `${axisName}: ${pole}`,
      description: "Доминирующая ось личности",
      content: {
        whatItMeans: getAxisDescription(topAxis.axis_id, topAxis.value),
        howItManifests: getAxisManifestations(topAxis.axis_id, topAxis.value),
        whatToDo: {
          text: `Практики для поддержки паттерна ${axisName}`,
          cta: "Смотреть практики",
          href: `/practices?axis=${topAxis.axis_id}`,
        },
        whereUsed: ["Практики", "Карта дня", "Отчёты"],
      },
    });
  }

  // Stress Mode (обязательный)
  const stressLevel = lens.stress_profile.sensitivity;
  const stressName = stressLevel > 0.7 ? "Высокая реактивность" : stressLevel > 0.4 ? "Умеренная реактивность" : "Низкая реактивность";
  
  chips.push({
    id: "stress-mode",
    category: "СТРЕСС",
    name: stressName,
    description: "Реакция под давлением",
    content: {
      whatItMeans: getStressDescription(stressLevel),
      howItManifests: getStressManifestations(stressLevel),
      whatToDo: {
        text: "Практики для управления стрессом",
        cta: "Открыть практики",
        href: "/practices?category=stress",
      },
      whereUsed: ["Практики", "Карта дня"],
    },
  });

  // Relational Style (опциональный)
  if (lens.relational_style && Math.abs(lens.top_axes.find(a => a.axis_id === "A6")?.value || 0) > 0.5) {
    chips.push({
      id: "relational-style",
      category: "ОТНОШЕНИЯ",
      name: lens.relational_style,
      description: "Как в отношениях",
    });
  }

  // Decision Style (опциональный)
  if (lens.decision_style && Math.abs(lens.top_axes.find(a => a.axis_id === "A3")?.value || 0) > 0.5) {
    chips.push({
      id: "decision-style",
      category: "РЕШЕНИЯ",
      name: lens.decision_style,
      description: "Как принимаешь решения",
    });
  }

  return chips;
}

// Вспомогательные функции для генерации текстов

function getThemeDescription(theme: string, lens: PersonalLensData): string {
  if (theme.includes("опоры") || theme.includes("стабильность")) {
    return "Тема опоры: тебе важно чувствовать устойчивость перед тем, как двигаться дальше.";
  }
  if (theme.includes("изменения") || theme.includes("Гибкость")) {
    return "Тема изменений: ты открыт к трансформациям и новым возможностям.";
  }
  if (theme.includes("внешнюю") || theme.includes("реакцию")) {
    return "Тема обратной связи: ты определяешь себя через взаимодействие с миром и реакции других.";
  }
  if (theme.includes("внутренние") || theme.includes("ориентиры")) {
    return "Тема самоопределения: ты опираешься на внутренние ценности и собственные критерии.";
  }
  return `Тема ${theme.toLowerCase()}: это определяет твой основной способ взаимодействия с миром.`;
}

function getThemeManifestations(theme: string, lens: PersonalLensData): string[] {
  if (theme.includes("опоры") || theme.includes("стабильность")) {
    return [
      "Усиление контроля над деталями",
      "Тревога при неопределённости",
      "Желание \"понять заранее\"",
    ];
  }
  if (theme.includes("изменения")) {
    return [
      "Открытость к новому",
      "Гибкость в планах",
      "Стремление к разнообразию",
    ];
  }
  if (theme.includes("внешнюю")) {
    return [
      "Опора на обратную связь",
      "Адаптация к окружению",
      "Чувствительность к реакциям других",
    ];
  }
  return [
    "Проявление через паттерны",
    "Влияние на решения",
    "Отражение в отношениях",
  ];
}

function getThemeAction(theme: string): string {
  if (theme.includes("опоры")) {
    return "Практика: 60 секунд на фиксацию того, что уже работает.";
  }
  if (theme.includes("изменения")) {
    return "Практика: осознанное принятие текущего момента.";
  }
  return "Практика для поддержки твоей основной темы.";
}

function getAxisDescription(axisId: string, value: number): string {
  const axisName = axisNames[axisId] || axisId;
  const pole = axisPoles[axisId]?.[value > 0 ? "right" : "left"] || "";
  
  if (value > 0.5) {
    return `Ты склонен к ${pole.toLowerCase()}. Это определяет твой стиль ${axisName.toLowerCase()} и влияет на все сферы жизни.`;
  } else if (value < -0.5) {
    return `Ты склонен к ${pole.toLowerCase()}. Это определяет твой стиль ${axisName.toLowerCase()} и влияет на все сферы жизни.`;
  }
  return `Ты балансируешь между полюсами ${axisName.toLowerCase()}, что даёт тебе гибкость, но может создавать внутренние противоречия.`;
}

function getAxisManifestations(axisId: string, value: number): string[] {
  if (axisId === "A1") {
    return value > 0
      ? [
          "В реакциях: быстро адаптируешься к внешним сигналам",
          "В отношениях: ценишь обратную связь и взаимодействие",
          "В решениях: учитываешь внешние факторы",
        ]
      : [
          "В реакциях: опираешься на внутренние ощущения",
          "В отношениях: нужна автономия и пространство",
          "В решениях: опираешься на внутренние критерии",
        ];
  }
  if (axisId === "A2") {
    return value > 0
      ? [
          "В реакциях: открыто выражаешь эмоции",
          "В отношениях: делишься чувствами",
          "В решениях: эмоции влияют на выбор",
        ]
      : [
          "В реакциях: обрабатываешь эмоции внутри",
          "В отношениях: предпочитаешь сдержанность",
          "В решениях: отделяешь эмоции от логики",
        ];
  }
  return [
    "Проявляется в реакциях",
    "Влияет на отношения",
    "Определяет стиль решений",
  ];
}

function getStressDescription(level: number): string {
  if (level > 0.7) {
    return "Высокая чувствительность к стрессу: ты остро реагируешь на давление и неопределённость, что может приводить к быстрому истощению.";
  }
  if (level > 0.4) {
    return "Умеренная чувствительность к стрессу: ты замечаешь давление, но можешь с ним справляться при наличии ресурсов.";
  }
  return "Низкая чувствительность к стрессу: ты относительно устойчив к давлению, но важно не игнорировать сигналы тела.";
}

function getStressManifestations(level: number): string[] {
  if (level > 0.7) {
    return [
      "Резкая реактивность на изменения",
      "Быстрое истощение при перегрузке",
      "Потребность в восстановлении",
    ];
  }
  if (level > 0.4) {
    return [
      "Заметная реакция на давление",
      "Потребность в балансе",
      "Важность профилактики",
    ];
  }
  return [
    "Относительная устойчивость",
    "Медленная реакция на стресс",
    "Важность осознанности",
  ];
}

/**
 * Генерирует Signature строку из Core Trio и осей
 */
export function generateSignature(
  sun?: string,
  moon?: string,
  rising?: string,
  axes?: InternalModelSnapshot["axes"]
): string {
  const parts: string[] = [];

  // Добавляем информацию о знаках
  if (sun) {
    parts.push(`Солнце в ${sun}`);
  }
  if (moon) {
    parts.push(`Луна в ${moon}`);
  }
  if (rising) {
    parts.push(`Асцендент в ${rising}`);
  }

  // Добавляем информацию о топ-оси
  if (axes && axes.length > 0) {
    const topAxis = [...axes]
      .map((a) => ({ ...a, absValue: Math.abs(a.value) }))
      .sort((a, b) => b.absValue - a.absValue)[0];

    if (topAxis && Math.abs(topAxis.value) > 0.5) {
      const axisName = axisNames[topAxis.axis_id] || topAxis.axis_id;
      const pole = axisPoles[topAxis.axis_id]?.[topAxis.value > 0 ? "right" : "left"] || "";
      
      if (parts.length > 0) {
        parts.push(`склонен к ${pole.toLowerCase()}`);
      } else {
        parts.push(`Склонен к ${pole.toLowerCase()}`);
      }
    }
  }

  // Формируем предложение
  if (parts.length === 0) {
    return "Твоя уникальная карта личности формируется через сочетание паттернов и энергий.";
  }

  if (parts.length === 1) {
    return `${parts[0]}.`;
  }

  if (parts.length === 2) {
    return `Ты ${parts[0].toLowerCase()} и ${parts[1]}.`;
  }

  // Для 3+ частей формируем более сложное предложение
  const firstPart = parts[0];
  const restParts = parts.slice(1);
  
  if (restParts.length === 1) {
    return `Ты ${firstPart.toLowerCase()}, ${restParts[0]}.`;
  }

  return `Ты ${firstPart.toLowerCase()}, ${restParts.slice(0, -1).join(", ")} и ${restParts[restParts.length - 1]}.`;
}

