export type CompatibilityPairSection = {
  id: string;
  title: string;
  body: string;
  bullets?: string[];
};

export type CompatibilityPairReportModel = {
  pairLine: string;
  score: number;
  scoreLabel: string;
  mainConclusion: string;
  sections: CompatibilityPairSection[];
};

type CompatibilityAspect = {
  type: string;
  description: string;
  score: number;
};

type CompatibilityEditorial = {
  pair_thesis?: string | null;
  mode_focus?: string | null;
  strengths?: string[];
  tensions?: string[];
  next_step?: string | null;
} | null;

type CompatibilityDeepDive = {
  relationship_archetype?: string | null;
  strongest_axis?: string | null;
  tension_axis?: string | null;
  dimensions?: Array<{
    key: string;
    label: string;
    score: number;
    summary: string;
    indicators?: string[];
  }>;
  strengths?: string[];
  challenges?: string[];
  guidance?: string[];
} | null;

export type CompatibilityPairInput = {
  name1: string;
  name2: string;
  overallScore: number;
  summary?: string | null;
  aspects?: CompatibilityAspect[];
  editorial?: CompatibilityEditorial;
  deepDive?: CompatibilityDeepDive;
  recommendations?: string[];
};

function cleanLine(value: string | null | undefined): string {
  return (value || "").trim().replace(/\s+/g, " ");
}

function scoreLabel(score: number): string {
  if (score >= 78) return "Сильная связь";
  if (score >= 58) return "Нужна настройка";
  return "Сложная динамика";
}

function pickAspect(aspects: CompatibilityAspect[], keywords: string[]): CompatibilityAspect | null {
  const lower = keywords.map((k) => k.toLowerCase());
  return (
    aspects.find((a) => lower.some((k) => a.type.toLowerCase().includes(k) || a.description.toLowerCase().includes(k))) ||
    null
  );
}

function sectionFromParts(title: string, id: string, parts: Array<string | null | undefined>, bullets?: string[]): CompatibilityPairSection | null {
  const body = parts.map(cleanLine).filter(Boolean).join(" ");
  if (!body && (!bullets || !bullets.length)) return null;
  return { id, title, body, bullets: bullets?.filter(Boolean) };
}

export function buildCompatibilityPairReportModel(input: CompatibilityPairInput): CompatibilityPairReportModel {
  const aspects = input.aspects || [];
  const editorial = input.editorial;
  const deep = input.deepDive;

  const mainConclusion = cleanLine(
    editorial?.pair_thesis ||
      input.summary ||
      deep?.relationship_archetype ||
      "Вы взаимно влияете друг на друга — и в сильных, и в уязвимых местах. Главное — не искать один «верный» процент, а увидеть живую динамику.",
  );

  const dimensionMap = new Map((deep?.dimensions || []).map((d) => [d.key.toLowerCase(), d]));

  const dimText = (keys: string[], fallback: string) => {
    for (const key of keys) {
      const d = dimensionMap.get(key);
      if (d?.summary) return cleanLine(d.summary);
    }
    return fallback;
  };

  const aspectText = (keys: string[], fallback: string) => {
    const a = pickAspect(aspects, keys);
    return a ? cleanLine(a.description) : fallback;
  };

  const sections: CompatibilityPairSection[] = [];

  const push = (s: CompatibilityPairSection | null) => {
    if (s) sections.push(s);
  };

  push(
    sectionFromParts(
      "Любовь",
      "love",
      [dimText(["love", "romance"], aspectText(["love", "venus", "heart"], "Здесь читается притяжение, нежность и то, насколько вам легко быть рядом."))],
      editorial?.strengths?.slice(0, 3),
    ),
  );
  push(
    sectionFromParts(
      "Общение",
      "communication",
      [dimText(["communication", "mercury"], aspectText(["communication", "mercury", "dialogue"], "Как вы слышите друг друга — и где теряется смысл между словами."))],
    ),
  );
  push(
    sectionFromParts(
      "Конфликты",
      "conflicts",
      [
        dimText(["conflict", "tension"], aspectText(["conflict", "mars", "tension"], "Где вспыхивает напряжение и что повторяется из раза в раз.")),
        editorial?.tensions?.[0],
      ],
      deep?.challenges?.slice(0, 3),
    ),
  );
  push(sectionFromParts("Быт", "domestic", [dimText(["domestic", "home", "living"], "Ритм дома, границы и ощущение «на своём месте» рядом.")]));
  push(sectionFromParts("Работа", "work", [dimText(["work", "business"], aspectText(["work", "career", "business"], "Роли, темп решений и уважение к компетенции друг друга."))]));
  push(
    sectionFromParts(
      "Интимная совместимость",
      "intimacy",
      [dimText(["sex", "intimacy"], aspectText(["sex", "intimacy", "passion"], "Желание, телесность и то, что остаётся за пределами слов."))],
    ),
  );
  push(sectionFromParts("Финансы", "finance", [dimText(["money", "finance"], aspectText(["money", "finance"], "Как вы распределяете ресурсы и что для каждого значит безопасность."))]));
  push(sectionFromParts("Родительство", "parenting", [dimText(["parenting", "children"], "Опора, границы и разный темп в теме детей и семьи.")]));
  push(
    sectionFromParts(
      "Рост",
      "growth",
      [dimText(["growth", "evolution"], deep?.strongest_axis ? `Сильная ось: ${cleanLine(deep.strongest_axis)}` : "Где вы тянете друг друга вперёд, а не только утешаете.")],
      deep?.strengths?.slice(0, 3),
    ),
  );
  push(
    sectionFromParts(
      "Слабые места",
      "weaknesses",
      [deep?.tension_axis ? `Узел напряжения: ${cleanLine(deep.tension_axis)}` : editorial?.tensions?.join(" ")],
      deep?.challenges?.slice(0, 4) || editorial?.tensions,
    ),
  );
  push(
    sectionFromParts(
      "Советы",
      "tips",
      [editorial?.next_step, ...(deep?.guidance || []).slice(0, 2), ...(input.recommendations || []).slice(0, 2)],
    ),
  );
  push(
    sectionFromParts(
      "История отношений",
      "story",
      [cleanLine(deep?.relationship_archetype), cleanLine(input.summary), editorial?.mode_focus],
    ),
  );
  push(
    sectionFromParts(
      "Карты отношений",
      "cards",
      aspects.slice(0, 3).map((a) => `${cleanLine(a.type)}: ${cleanLine(a.description)}`),
    ),
  );

  return {
    pairLine: `${input.name1} ❤️ ${input.name2}`,
    score: input.overallScore,
    scoreLabel: scoreLabel(input.overallScore),
    mainConclusion,
    sections,
  };
}
