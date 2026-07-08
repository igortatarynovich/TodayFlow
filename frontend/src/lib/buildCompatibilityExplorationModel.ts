import type { SignCompatProductSurface } from "@/components/compatibility/CompatibilityDynamicsSurface";
import type { CompatibilityPairInput } from "@/lib/buildCompatibilityPairReportModel";
import {
  getContinuationScenarios,
  getScenarioSkin,
  resolveScenarioId,
  scoreLabelRu,
  type ScenarioSkin,
  type ScenarioTone,
  type SubscoreKey,
  type ToneMode,
} from "@/lib/compatibilityScenarioSkins";
import { filterCompatibilityParagraphs, stripCompatibilityDisplayGarbage } from "@/lib/compatibilityCopySanitize";
import { playfulDimensionQuip, playfulScoreLabelRu } from "@/lib/compatibilityPlayfulStats";
import { scenarioScoreLabelRu } from "@/lib/compatibilityScenarioMetrics";
import {
  buildScenarioDeepSectionsFromBlocks,
  buildScenarioDeepSectionsFromPairDeep,
} from "@/lib/compatibilityScenarioDeepSections";

export type ExplorationPresentation = "serious" | "playful";

export type ExplorationDimension = {
  id: string;
  emoji: string;
  label: string;
  score: number;
  quip?: string;
};

export type ExplorationDeepSection = {
  id: string;
  title: string;
  subtitle?: string;
  takeaway: string;
  detail?: string;
  risk?: string;
  action?: string;
};

export type ExplorationContinuation = {
  id: string;
  emoji: string;
  title: string;
  hook: string;
  href: string;
  tone: ScenarioTone;
};

export type CompatibilityExplorationModel = {
  scenarioId: string;
  scenarioTitle: string;
  scenarioPoster: string;
  scenarioSubtitle: string;
  tone: ScenarioTone;
  toneMode: ToneMode;
  presentation: ExplorationPresentation;
  pairLine: string;
  score: number;
  scoreLabel: string;
  mainThought: string;
  dimensions: ExplorationDimension[];
  narrative: string[];
  strongestResource: string;
  mainRisk: string;
  tips: string[];
  deepSections: ExplorationDeepSection[];
  continuationScenarios: ExplorationContinuation[];
  roles?: SignCompatProductSurface["roles"];
  scenarioGroups?: SignCompatProductSurface["scenarios"];
  /** Playful-only: disclaimer that stats are not serious */
  playfulDisclaimer?: string;
};

function uniqueStrings(items: Array<string | null | undefined>, max: number): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of items) {
    const text = stripCompatibilityDisplayGarbage(raw);
    if (!text || seen.has(text.toLowerCase())) continue;
    seen.add(text.toLowerCase());
    out.push(text);
    if (out.length >= max) break;
  }
  return out;
}

function buildContinuation(
  skin: ScenarioSkin,
  hrefFor?: (scenarioId: string, defaultHref: string) => string,
): ExplorationContinuation[] {
  return getContinuationScenarios(skin.id).map((s) => ({
    id: s.id,
    emoji: s.emoji,
    title: s.title,
    hook: s.hook,
    href: hrefFor ? hrefFor(s.id, s.href) : s.href,
    tone: s.tone,
  }));
}

export type PairExplorationOverrides = {
  displayScore?: number;
  scenarioSubscores?: Partial<Record<SubscoreKey, number>>;
  continuationHref?: (scenarioId: string, defaultHref: string) => string;
  /** From scenario_context.deep_block_order — attachment reference ordering */
  deepBlockOrder?: string[];
};

function stripIronyPrefix(text: string): string {
  const t = stripCompatibilityDisplayGarbage(text);
  const low = t.toLowerCase();
  if (low.startsWith("с лёгкой иронией:")) return t.slice("с лёгкой иронией:".length).trim();
  if (low.startsWith("with a light wink:")) return t.slice("with a light wink:".length).trim();
  return t;
}

function buildPlayfulExploration(
  skin: ScenarioSkin,
  opts: {
    pairTitle: string;
    score: number;
    productSurface: SignCompatProductSurface;
  },
): CompatibilityExplorationModel {
  const ps = opts.productSurface;
  const mainThought = stripIronyPrefix(ps.score_tagline);

  const dimensions: ExplorationDimension[] = skin.dimensionLabels.map((d) => ({
    id: d.key,
    emoji: d.emoji,
    label: d.label,
    score: ps.subscores[d.key],
    quip: playfulDimensionQuip(skin.id, d.key, ps.subscores[d.key]),
  }));

  const narrative = filterCompatibilityParagraphs(ps.overview_paragraphs, 1);
  const topDim = [...dimensions].sort((a, b) => b.score - a.score)[0];
  const lowDim = [...dimensions].sort((a, b) => a.score - b.score)[0];

  return {
    scenarioId: skin.id,
    scenarioTitle: skin.title,
    scenarioPoster: skin.poster,
    scenarioSubtitle: skin.posterSubtitle,
    tone: skin.tone,
    toneMode: "playful",
    presentation: "playful",
    pairLine: opts.pairTitle,
    score: opts.score,
    scoreLabel: playfulScoreLabelRu(skin.id, opts.score),
    mainThought,
    dimensions,
    narrative,
    strongestResource: topDim ? `${topDim.emoji} ${topDim.label}: ${topDim.score}% — ${topDim.quip || "лидер по статистике"}` : "",
    mainRisk: lowDim ? `${lowDim.emoji} ${lowDim.label}: ${lowDim.score}% — ${lowDim.quip || "зона риска"}` : "",
    tips: [],
    deepSections: [],
    continuationScenarios: buildContinuation(skin),
    playfulDisclaimer: "Шуточная статистика — не серьёзный разбор отношений.",
  };
}

function buildSeriousExploration(
  skin: ScenarioSkin,
  opts: {
    pairTitle: string;
    score: number;
    productSurface: SignCompatProductSurface;
  },
): CompatibilityExplorationModel {
  const ps = opts.productSurface;

  const dimensions: ExplorationDimension[] = skin.dimensionLabels.map((d) => ({
    id: d.key,
    emoji: d.emoji,
    label: d.label,
    score: ps.subscores[d.key],
  }));

  const strengthBlock = ps.blocks.find((b) => b.key === "attraction") || ps.blocks[0];
  const conflictBlock = ps.blocks.find((b) => b.key === "conflicts") || ps.blocks[1] || ps.blocks[0];

  const tips = uniqueStrings(
    [...ps.blocks.map((b) => b.action), ...(ps.scenarios.flatMap((g) => g.bullets) || [])],
    3,
  );

  return {
    scenarioId: skin.id,
    scenarioTitle: skin.title,
    scenarioPoster: skin.poster,
    scenarioSubtitle: skin.posterSubtitle,
    tone: skin.tone,
    toneMode: "serious",
    presentation: "serious",
    pairLine: opts.pairTitle,
    score: opts.score,
    scoreLabel: scenarioScoreLabelRu(skin.id, opts.score),
    mainThought: stripCompatibilityDisplayGarbage(ps.score_tagline),
    dimensions,
    narrative: filterCompatibilityParagraphs(ps.overview_paragraphs, 3),
    strongestResource: strengthBlock?.takeaway || "Есть зона, где контакт даётся естественнее — опирайтесь на неё.",
    mainRisk: conflictBlock?.risk || conflictBlock?.takeaway || "Главный риск — повторяющийся сценарий без проговаривания.",
    tips: tips.length ? tips : ["Проясняйте ожидания заранее.", "Договаривайтесь о ролях в стрессе.", "Возвращайтесь к разговору, не к молчанию."],
    deepSections: buildScenarioDeepSectionsFromBlocks(skin, ps.blocks),
    continuationScenarios: buildContinuation(skin),
    roles: ps.roles,
    scenarioGroups: ps.scenarios,
  };
}

export function buildExplorationFromDynamics(opts: {
  topicId?: string | null;
  seriesId?: string | null;
  readingId?: string | null;
  pairTitle: string;
  score: number;
  productSurface: SignCompatProductSurface;
}): CompatibilityExplorationModel {
  const scenarioId = resolveScenarioId({
    topic: opts.topicId,
    series: opts.seriesId,
    reading: opts.readingId,
  });
  const skin = getScenarioSkin(scenarioId);
  const base = { pairTitle: opts.pairTitle, score: opts.score, productSurface: opts.productSurface };
  if (skin.toneMode === "playful") {
    return buildPlayfulExploration(skin, base);
  }
  return buildSeriousExploration(skin, base);
}

export function buildExplorationFromPairInput(
  input: CompatibilityPairInput,
  scenarioId = "love",
  overrides?: PairExplorationOverrides,
): CompatibilityExplorationModel {
  const skin = getScenarioSkin(scenarioId);
  const deep = input.deepDive;
  const editorial = input.editorial;
  const isPlayful = skin.toneMode === "playful";
  const displayScore = overrides?.displayScore ?? input.overallScore;
  const scenarioSubscores = overrides?.scenarioSubscores;

  const dimensionScores = new Map(
    (deep?.dimensions || []).map((d) => [d.key.toLowerCase(), { label: d.label, score: d.score, summary: d.summary }]),
  );

  const dimensions: ExplorationDimension[] = skin.dimensionLabels.map((d) => {
    const fromScenario = scenarioSubscores?.[d.key];
    const fromDeep = dimensionScores.get(d.key);
    const score =
      fromScenario ??
      fromDeep?.score ??
      (input.aspects || []).find((a) => a.type.toLowerCase().includes(d.key))?.score ??
      displayScore;
    const quip = isPlayful ? playfulDimensionQuip(skin.id, d.key, score) : undefined;
    if (fromDeep) {
      return { id: d.key, emoji: d.emoji, label: fromDeep.label || d.label, score, quip };
    }
    return { id: d.key, emoji: d.emoji, label: d.label, score, quip };
  });

  if (isPlayful) {
    const topDim = [...dimensions].sort((a, b) => b.score - a.score)[0];
    const lowDim = [...dimensions].sort((a, b) => a.score - b.score)[0];
    const mainThought =
      editorial?.pair_thesis ||
      input.summary ||
      skin.hook ||
      "Шуточная статистика по вашему сценарию — не серьёзный разбор.";

    return {
      scenarioId,
      scenarioTitle: skin.title,
      scenarioPoster: skin.poster,
      scenarioSubtitle: skin.posterSubtitle,
      tone: skin.tone,
      toneMode: "playful",
      presentation: "playful",
      pairLine: `${input.name1} × ${input.name2}`,
      score: displayScore,
      scoreLabel: playfulScoreLabelRu(skin.id, displayScore),
      mainThought,
      dimensions,
      narrative: uniqueStrings([editorial?.mode_focus, input.summary], 1),
      strongestResource: topDim ? `${topDim.emoji} ${topDim.label}: ${topDim.score}% — ${topDim.quip || ""}` : "",
      mainRisk: lowDim ? `${lowDim.emoji} ${lowDim.label}: ${lowDim.score}% — ${lowDim.quip || ""}` : "",
      tips: [],
      deepSections: [],
      continuationScenarios: buildContinuation(skin, overrides?.continuationHref),
      playfulDisclaimer: "Шуточная статистика — не серьёзный разбор отношений.",
    };
  }

  const mainThought =
    editorial?.pair_thesis ||
    input.summary ||
    deep?.relationship_archetype ||
    "Вы взаимно влияете друг на друга — главное увидеть живую динамику, а не один процент.";

  const narrative = uniqueStrings(
    [editorial?.mode_focus, deep?.relationship_archetype, input.summary, ...(deep?.strengths || []).slice(0, 1)],
    3,
  );

  const tips = uniqueStrings([...(deep?.guidance || []), ...(input.recommendations || []), editorial?.next_step], 3);

  const deepSections: ExplorationDeepSection[] = buildScenarioDeepSectionsFromPairDeep(
    skin,
    deep,
    input.aspects,
    overrides?.deepBlockOrder,
  );

  return {
    scenarioId,
    scenarioTitle: skin.title,
    scenarioPoster: skin.poster,
    scenarioSubtitle: skin.posterSubtitle,
    tone: skin.tone,
    toneMode: "serious",
    presentation: "serious",
    pairLine: `${input.name1} × ${input.name2}`,
    score: displayScore,
    scoreLabel: isPlayful ? playfulScoreLabelRu(skin.id, displayScore) : scenarioScoreLabelRu(scenarioId, displayScore),
    mainThought,
    dimensions,
    narrative: narrative.length ? narrative : ["Посмотрите, как эта динамика проявляется в конкретных ситуациях — не только в общих словах."],
    strongestResource:
      deep?.strengths?.[0] ||
      editorial?.strengths?.[0] ||
      deep?.strongest_axis ||
      "Есть опора, на которую можно опереться в сложные моменты.",
    mainRisk:
      deep?.challenges?.[0] ||
      editorial?.tensions?.[0] ||
      deep?.tension_axis ||
      "Главный риск — повторяющееся трение без нового разговора.",
    tips: tips.length ? tips : ["Проясняйте ожидания заранее.", "Договаривайтесь о ролях.", "Возвращайтесь к разговору."],
    deepSections,
    continuationScenarios: buildContinuation(skin, overrides?.continuationHref),
  };
}
