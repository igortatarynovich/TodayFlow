/**
 * Profile v0 · insight taxonomy (category gate).
 *
 * Canon: docs/status/PROFILE_V0_CONTENT_INSIGHT_AUDIT.md § «Taxonomy gate»
 *
 * Rule: a layer passes when every **required category** has a distinct insight —
 * not when it hits N strings. Five paraphrases of «ищет глубину» = 1 category filled.
 *
 * Pipeline shape (future): each slot carries `{ categoryId, text }`, not bare strings.
 * UI shows text only; categoryId is internal for QA + ledger dedup by dimension.
 */

import { PROFILE_INSIGHT_BUDGET } from "./profileInsightBudget";
import type { ProfileTaxonomyInsightSlot } from "./profileInsightTypes";

export type ProfileInsightSpatialWeight = "compact" | "standard" | "expanded";

export type ProfileInsightCategorySpec = {
  /** Stable id for pipeline + QA audit */
  id: string;
  /** Human dimension — what must be true for the slot to count */
  dimension: string;
  /** Reference hints (consumer never sees these labels) */
  referenceHints: string[];
};

export type ProfileLayerTaxonomy = {
  layer: keyof typeof PROFILE_INSIGHT_BUDGET;
  userQuestion: string;
  spatialWeight: ProfileInsightSpatialWeight;
  /** Required distinct categories — count must match PROFILE_INSIGHT_BUDGET[layer] */
  categories: ProfileInsightCategorySpec[];
};

/** Target scroll/text share: origin (Hero+Why+Core) vs application (Mirror+Life+Compass). */
export const PROFILE_SPATIAL_MIX = {
  /** Current risk ~30% origin — too much explanation */
  originMaxShare: 0.2,
  applicationMinShare: 0.8,
  compactLayers: ["hero", "why"] as const,
  expandedLayers: ["socialMirror", "love", "money"] as const,
} as const;

export const PROFILE_LAYER_TAXONOMY: ProfileLayerTaxonomy[] = [
  {
    layer: "hero",
    userQuestion: "Кто ты",
    spatialWeight: "compact",
    categories: [
      {
        id: "identity",
        dimension: "Идентичность — кто ты в одном образе",
        referenceHints: ["interpretation.identity", "archetype_seed", "life_path.essence"],
      },
      {
        id: "main_strength",
        dimension: "Главная сила — что у тебя работает лучше всего",
        referenceHints: ["interpretation.strengths[0]", "life_path.plus_side[0]", "sign.strengths[0]"],
      },
      {
        id: "main_conflict",
        dimension: "Главный конфликт — где ты застреваешь",
        referenceHints: ["interpretation.watchouts[0]", "life_path.minus_side[0]", "life_path.main_fear"],
      },
      {
        id: "life_theme",
        dimension: "Главная тема жизни — через что повторяется сценарий",
        referenceHints: ["life_path.pattern", "life_path.driver", "sign.themes[0]"],
      },
    ],
  },
  {
    layer: "why",
    userQuestion: "Почему сформировался такой профиль",
    spatialWeight: "compact",
    categories: [
      {
        id: "formation",
        dimension: "Что сформировало паттерн — причина, не пересказ Hero",
        referenceHints: ["life_path.pattern", "life_path.driver", "sign.portrait (causal slice)"],
      },
      {
        id: "helps",
        dimension: "Как это помогает — функция паттерна",
        referenceHints: ["life_path.growth", "life_path.plus_side", "sign.plus_side"],
      },
      {
        id: "breaks",
        dimension: "Где это ломается — цена паттерна",
        referenceHints: ["life_path.minus_side", "life_path.main_fear", "interpretation.watchouts"],
      },
    ],
  },
  {
    layer: "corePattern",
    userQuestion: "Что тобой движет",
    spatialWeight: "standard",
    categories: [
      {
        id: "driver",
        dimension: "Драйвер — что запускает движение",
        referenceHints: ["life_path.driver", "life_path.manifestation[0]"],
      },
      {
        id: "fear",
        dimension: "Страх — от чего защищается паттерн",
        referenceHints: ["life_path.main_fear"],
      },
      {
        id: "trap",
        dimension: "Ловушка — куда паттерн уводит в минус",
        referenceHints: ["life_path.minus_side", "life_path.watchouts"],
      },
      {
        id: "decisions",
        dimension: "Способ принятия решений",
        referenceHints: ["sign.decisions", "life_path.reading", "interpretation.life_areas.decisions"],
      },
      {
        id: "recovery",
        dimension: "Способ восстановления энергии",
        referenceHints: ["baseline.rhythm_style", "interpretation.life_areas.body", "moon_recovery_hint"],
      },
    ],
  },
  {
    layer: "socialMirror",
    userQuestion: "Как тебя видят другие",
    spatialWeight: "expanded",
    categories: [
      {
        id: "first_impression",
        dimension: "Первое впечатление — до контакта",
        referenceHints: ["sign.portrait", "name_number.personality", "sign.strengths"],
      },
      {
        id: "after_knowing",
        dimension: "Реальное впечатление после знакомства",
        referenceHints: ["name_number.expression", "sign.communication", "sign.intimacy"],
      },
      {
        id: "misread",
        dimension: "Что люди понимают неправильно",
        referenceHints: ["sign.watchouts", "sign.minus_side", "sign.hurts"],
      },
      {
        id: "trust",
        dimension: "Что вызывает доверие",
        referenceHints: ["sign.likes", "sign.friendship", "sign.support"],
      },
    ],
  },
  {
    layer: "love",
    userQuestion: "Что происходит в близости",
    spatialWeight: "expanded",
    categories: [
      {
        id: "seeks",
        dimension: "Что ищешь в отношениях",
        referenceHints: ["sign.intimacy", "sign.likes", "life_path.relationships[0]"],
      },
      {
        id: "fears",
        dimension: "Чего боишься в близости",
        referenceHints: ["sign.hurts", "life_path.main_fear (relational)", "sign.watchouts"],
      },
      {
        id: "loves",
        dimension: "Как любишь — стиль близости",
        referenceHints: ["sign.love", "sign.conflict", "interpretation.life_areas.love"],
      },
      {
        id: "destroys",
        dimension: "Что разрушает отношения",
        referenceHints: ["sign.dislikes", "life_path.relationships[2]", "sign.minus_side"],
      },
      {
        id: "strengthens",
        dimension: "Что укрепляет отношения",
        referenceHints: ["sign.plus_side", "life_path.relationships[1]", "interpretation.strengths (relational)"],
      },
    ],
  },
  {
    layer: "money",
    userQuestion: "Как ты реализуешься",
    spatialWeight: "expanded",
    categories: [
      {
        id: "growth_source",
        dimension: "Источник роста — откуда приходит масштаб",
        referenceHints: ["life_path.money_work[0]", "sign.career", "interpretation.life_areas.career"],
      },
      {
        id: "earning_style",
        dimension: "Стиль заработка",
        referenceHints: ["sign.money", "sign.work", "interpretation.life_areas.money"],
      },
      {
        id: "risk",
        dimension: "Риск — где теряешь деньги или энергию",
        referenceHints: ["life_path.money_work[2]", "sign.watchouts", "life_path.main_fear (money)"],
      },
      {
        id: "blind_spot",
        dimension: "Слепая зона в реализации",
        referenceHints: ["life_path.minus_side", "sign.decisions", "interpretation.watchouts (career)"],
      },
      {
        id: "catalyst",
        dimension: "Карьерный катализатор — что ускоряет",
        referenceHints: ["life_path.plus_side", "sign.strengths", "interpretation.life_areas.career"],
      },
    ],
  },
  {
    layer: "compass",
    userQuestion: "Что делать дальше",
    spatialWeight: "standard",
    categories: [
      {
        id: "amplify",
        dimension: "Что усилить сейчас",
        referenceHints: ["life_path.growth", "interpretation.life_areas.career", "baseline.rhythm_style"],
      },
      {
        id: "avoid",
        dimension: "Чего избегать",
        referenceHints: ["interpretation.watchouts", "life_path.minus_side[0]"],
      },
      {
        id: "energy_direction",
        dimension: "Куда направить энергию",
        referenceHints: ["life_path.driver", "interpretation.life_areas.decisions"],
      },
      {
        id: "skill",
        dimension: "Какой навык качать",
        referenceHints: ["life_path.lesson", "life_path.growth", "sign.growth"],
      },
      {
        id: "check_soon",
        dimension: "Что проверить в ближайшее время",
        referenceHints: ["today recommendation slice", "moon_recovery_hint", "interpretation.life_areas.body"],
      },
    ],
  },
];

/** Every layer's category count must match numeric budget (same N, different rule). */
export function assertTaxonomyMatchesBudget(): void {
  for (const spec of PROFILE_LAYER_TAXONOMY) {
    const budget = PROFILE_INSIGHT_BUDGET[spec.layer];
    if (spec.categories.length !== budget) {
      throw new Error(
        `Profile insight taxonomy: layer "${spec.layer}" has ${spec.categories.length} categories, budget is ${budget}`,
      );
    }
  }
}

/** Slot for typed pipeline output — UI shows text only. */
export type ProfileInsightSlot = ProfileTaxonomyInsightSlot;

export type ProfileLayerInsightPayload = {
  layer: ProfileInsightLayer;
  slots: ProfileTaxonomyInsightSlot[];
};

export type ProfileInsightLayer = keyof typeof PROFILE_INSIGHT_BUDGET;

/** @deprecated use profileInsightTypes.ProfileTaxonomyInsightSlot */
export type { ProfileTaxonomyInsightSlot } from "./profileInsightTypes";

/** Gate: all required category ids present; optional semantic dedup across slots in same layer. */
export function missingCategories(
  layer: ProfileInsightLayer,
  filledCategoryIds: string[],
): string[] {
  const spec = PROFILE_LAYER_TAXONOMY.find((s) => s.layer === layer);
  if (!spec) return [];
  const filled = new Set(filledCategoryIds);
  return spec.categories.filter((c) => !filled.has(c.id)).map((c) => c.id);
}

// Fail fast in dev if canon drift
if (process.env.NODE_ENV !== "production") {
  assertTaxonomyMatchesBudget();
}
