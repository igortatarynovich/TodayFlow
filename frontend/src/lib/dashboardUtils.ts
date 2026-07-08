import type { MoonPhaseResponse } from "@/lib/types";
import type { Practice } from "@/lib/dashboardTypes";
import { t } from "@/lib/i18n";

export function getEnergyLevel(moonPhase: MoonPhaseResponse | null): { dots: number; total: number; tempo: string; mode: string } {
  if (!moonPhase?.current) {
    return { dots: 3, total: 5, tempo: t("dashboard.energy.tempo.calm", "спокойный"), mode: t("dashboard.energy.mode.focus", "Фокус") };
  }

  // Используем human_text из Content System, если есть (для анализа)
  const humanText = moonPhase.current.human_text?.toLowerCase() || "";
  const themes = moonPhase.current.themes?.toLowerCase() || "";
  const textToAnalyze = humanText || themes;
  const keywords = moonPhase.current.keywords || [];
  
  // Определяем уровень энергии на основе текста и ключевых слов
  let dots = 3;
  if (textToAnalyze.includes("активн") || textToAnalyze.includes("энерги") || keywords.some(k => k.toLowerCase().includes("активн"))) {
    dots = 4;
  } else if (textToAnalyze.includes("спокойн") || textToAnalyze.includes("медленн") || keywords.some(k => k.toLowerCase().includes("спокойн"))) {
    dots = 2;
  }

  // Определяем темп
  let tempo = t("dashboard.energy.tempo.calm", "спокойный");
  if (textToAnalyze.includes("быстр") || keywords.some(k => k.toLowerCase().includes("быстр"))) {
    tempo = t("dashboard.energy.tempo.active", "активный");
  } else if (textToAnalyze.includes("медленн") || keywords.some(k => k.toLowerCase().includes("медленн"))) {
    tempo = t("dashboard.energy.tempo.slow", "медленный");
  }

  // Определяем режим дня
  let mode = t("dashboard.energy.mode.focus", "Фокус");
  if (textToAnalyze.includes("отдых") || keywords.some(k => k.toLowerCase().includes("отдых"))) {
    mode = t("dashboard.energy.mode.rest", "Отдых");
  } else if (textToAnalyze.includes("творчеств") || keywords.some(k => k.toLowerCase().includes("творчеств"))) {
    mode = t("dashboard.energy.mode.creativity", "Творчество");
  }

  return { dots, total: 5, tempo, mode };
}

export function getWorthToday(moonPhase: MoonPhaseResponse | null): string[] {
  if (!moonPhase?.current) return [];
  
  // Используем human_text из Content System, если есть
  const humanText = moonPhase.current.human_text || "";
  const guidance = moonPhase.current.guidance || "";
  const textToUse = humanText || guidance;
  const keywords = moonPhase.current.keywords || [];
  
  // Пытаемся извлечь "что стоит делать" из текста
  const worthPatterns = [
    /(?:стоит|лучше|важно|рекомендуется|следует|можно)[\s:]+([^.;]+)/gi,
    /(?:фокус|сосредоточиться|концентрация)[\s]+(?:на|на\s+том,\s+чтобы)[\s]+([^.;]+)/gi,
  ];
  
  const worthItems: string[] = [];
  
  // Извлекаем из текста
  for (const pattern of worthPatterns) {
    const matches = Array.from(textToUse.matchAll(pattern));
    for (const match of matches) {
      if (match[1]) {
        const item = match[1].trim().toLowerCase();
        if (item.length > 10 && item.length < 60) {
          worthItems.push(item);
        }
      }
    }
  }
  
  // Если не нашли, используем keywords как fallback (извлекаем из keywords, если есть)
  if (worthItems.length === 0 && keywords.length > 0) {
    // Пытаемся использовать keywords как основу, но без хардкода
    const relevantKeywords = keywords.filter(k => 
      k.toLowerCase().includes("фокус") || 
      k.toLowerCase().includes("концентрация") ||
      k.toLowerCase().includes("решение") ||
      k.toLowerCase().includes("выбор")
    );
    if (relevantKeywords.length > 0) {
      worthItems.push(...relevantKeywords.slice(0, 2).map(k => k.toLowerCase()));
    }
  }
  
  // Fallback если ничего не нашли - используем первые предложения из текста как рекомендации
  if (worthItems.length < 2) {
    const sentences = textToUse.split(/[.!?]+/).filter(s => s.trim().length > 20 && s.trim().length < 100);
    if (sentences.length > 0) {
      worthItems.push(...sentences.slice(0, 2).map(s => s.trim().toLowerCase()));
    }
  }
  
  return worthItems.slice(0, 2);
}

export function getBetterNotToday(moonPhase: MoonPhaseResponse | null): string[] {
  if (!moonPhase?.current) return [];
  
  // Используем human_text из Content System, если есть
  const humanText = moonPhase.current.human_text || "";
  const guidance = moonPhase.current.guidance || "";
  const textToUse = humanText || guidance;
  const keywords = moonPhase.current.keywords || [];
  
  // Пытаемся извлечь "что лучше не делать" из текста
  const avoidPatterns = [
    /(?:не\s+стоит|лучше\s+не|не\s+рекомендуется|избегать|не\s+следует)[\s:]+([^.;]+)/gi,
    /(?:спешить|суетиться|поспешн|торопиться)[\s]+([^.;]+)/gi,
  ];
  
  const avoidItems: string[] = [];
  
  // Извлекаем из текста
  for (const pattern of avoidPatterns) {
    const matches = Array.from(textToUse.matchAll(pattern));
    for (const match of matches) {
      if (match[1]) {
        const item = match[1].trim().toLowerCase();
        if (item.length > 10 && item.length < 60) {
          avoidItems.push(item);
        }
      }
    }
  }
  
  // Если не нашли, используем keywords как fallback (извлекаем из keywords, если есть)
  if (avoidItems.length === 0 && keywords.length > 0) {
    // Пытаемся использовать keywords как основу, но без хардкода
    const relevantKeywords = keywords.filter(k => 
      k.toLowerCase().includes("спеш") || 
      k.toLowerCase().includes("сует") ||
      k.toLowerCase().includes("поспеш") ||
      k.toLowerCase().includes("вывод")
    );
    if (relevantKeywords.length > 0) {
      avoidItems.push(...relevantKeywords.slice(0, 2).map(k => k.toLowerCase()));
    }
  }
  
  // Fallback если ничего не нашли - оставляем пустым
  
  return avoidItems.slice(0, 2);
}

export function getFocusToday(currentPractice: Practice | null): { title: string; description: string } {
  if (currentPractice?.target_axis) {
    const axisNames: Record<string, string> = {
      "A1": "Опора на себя",
      "A2": "Эмоциональная обработка",
      "A3": "Принятие решений",
      "A4": "Стабильность и изменения",
      "A5": "Ориентация контроля",
      "A6": "Реляционная ориентация",
      "A7": "Управление энергией",
    };
    return {
      title: axisNames[currentPractice.target_axis] || currentPractice.title,
      description: currentPractice.description || currentPractice.title,
    };
  }
  return {
    title: currentPractice?.title || "",
    description: currentPractice?.description || "",
  };
}

