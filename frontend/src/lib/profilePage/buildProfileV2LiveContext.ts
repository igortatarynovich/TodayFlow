import { formatDelta30dLabel } from "@/lib/profileCumInsights";
import type { CompactUserModel, CoreProfile } from "@/lib/types";
import { elementRuName } from "@/lib/zodiacKnowledge";
import {
  buildProfileJourneyProjection,
  type ProfileJourneyProjection,
} from "@/lib/profilePage/buildProfileJourneyProjection";
import { filterProfileCopyList } from "@/lib/profilePage/profileCopySafety";
import {
  PROFILE_SLOT_HELPS,
  profileSlotInResult,
  profileSlotRevealed,
  profileUserMessages,
} from "@/lib/profilePage/profileMatrixAccess";
import { getLocale } from "@/lib/i18n";

export type ObservationAccuracyLevel = "initial" | "forming" | "stable";

/** Aligns with backend profile_content_v1.source_depth (client mirror for Evidence UI). */
export type ProfileSourceDepth =
  | "birth_data_only"
  | "onboarding_answers"
  | "profile_plus_checkins"
  | "longitudinal_profile";

export type ProfileV2LiveContext = {
  /** Qualitative maturity of personal observations — never a fabricated precise %. */
  observationAccuracyLevel: ObservationAccuracyLevel;
  observationAccuracyLabel: string;
  sourceDepth: ProfileSourceDepth;
  /** Evidence title — why the portrait holds. */
  evidenceTitle: string;
  /** Honesty line from source_depth. */
  evidenceBody: string;
  /** What would strengthen the portrait (no day agenda). */
  evidenceNextStep: string | null;
  /** Stable helps only when L3 is revealed for this access tier. */
  helps: string[];
  /** True when helps exist in the saved result but are access-gated. */
  helpsAccessGated: boolean;
  /** Resolver CTAs for missing name / time / place / L3. */
  userMessages: Array<{ code: string; text: string }>;
  elementLabel: string | null;
  /** Journey Steps 1–5 — read-path projections mapped for UI. */
  journey: ProfileJourneyProjection;
};

const ACCURACY_LABELS: Record<ObservationAccuracyLevel, string> = {
  initial: "первые контуры",
  forming: "появляются повторы",
  stable: "повторы уже видны",
};

const DEPTH_HONESTY: Record<ProfileSourceDepth, string> = {
  birth_data_only:
    "Портрет по дате рождения показывает общие черты. Повторяющиеся жизненные закономерности проявляются со временем.",
  onboarding_answers:
    "Часть формулировок опирается на ваши ответы при старте. Закрытые дни покажут, что из этого держится в жизни.",
  profile_plus_checkins:
    "По отметкам уже видны первые тенденции. С накоплением дней закономерности вашей жизни становятся яснее.",
  longitudinal_profile:
    "Портрет опирается на ваши ответы и повторяющиеся дни — не только на дату рождения.",
};

const DEPTH_NEXT: Record<ProfileSourceDepth, string | null> = {
  birth_data_only:
    "Отмечайте своё состояние, чтобы увидеть, какие решения, эмоции и события повторяются именно в вашей жизни.",
  onboarding_answers:
    "Закрытые дни и отметки покажут, какие формулировки действительно держатся в жизни.",
  profile_plus_checkins:
    "Ещё несколько недель отметок укрепят повторяющиеся паттерны вашей жизни.",
  longitudinal_profile: null,
};

export function resolveProfileSourceDepth(input: {
  coreProfile: CoreProfile | null;
  cum: CompactUserModel | null;
  localClosedDays?: number;
}): ProfileSourceDepth {
  const hasBirth = Boolean(
    input.coreProfile?.astro?.profile_id ||
      input.coreProfile?.astro?.sun_sign ||
      input.coreProfile?.astro?.birth_date ||
      input.coreProfile?.numerology?.birth_date,
  );
  const checkinDays =
    (typeof input.coreProfile?.living?.signal_profile?.signals_days === "number"
      ? input.coreProfile.living.signal_profile.signals_days
      : 0) + (input.localClosedDays ?? 0);
  const longitudinalDays = checkinDays;
  const hasOnboarding = Boolean(
    input.coreProfile?.profile_contract_v1?.identity_core ||
      input.coreProfile?.baseline?.archetype_seed,
  );

  if (longitudinalDays >= 14 && checkinDays >= 7) return "longitudinal_profile";
  if (checkinDays >= 3 || longitudinalDays >= 7) return "profile_plus_checkins";
  if (hasOnboarding) return "onboarding_answers";
  if (hasBirth) return "birth_data_only";
  return "birth_data_only";
}

/** @deprecated Prefer resolveObservationAccuracy — kept for callers that need a 0–100 from real confidence only. */
export function resolveProfileV2AwarenessPercent(input: {
  cum: CompactUserModel | null;
  coreProfile: CoreProfile | null;
  localClosedDays?: number;
}): number | null {
  const overall = input.cum?.confidence?.overall;
  if (typeof overall === "number" && !Number.isNaN(overall)) {
    return Math.round(Math.max(0, Math.min(1, overall)) * 100);
  }
  return null;
}

export function resolveObservationAccuracy(input: {
  cum: CompactUserModel | null;
  coreProfile: CoreProfile | null;
  localClosedDays?: number;
}): { level: ObservationAccuracyLevel; label: string; percent: number | null } {
  const overall = input.cum?.confidence?.overall;
  if (typeof overall === "number" && !Number.isNaN(overall)) {
    const clamped = Math.max(0, Math.min(1, overall));
    const percent = Math.round(clamped * 100);
    const level: ObservationAccuracyLevel =
      clamped >= 0.6 ? "stable" : clamped >= 0.3 ? "forming" : "initial";
    return { level, label: ACCURACY_LABELS[level], percent };
  }

  const signalsDays = input.coreProfile?.living?.signal_profile?.signals_days;
  const filled = input.localClosedDays ?? 0;
  const evidence =
    (typeof signalsDays === "number" && signalsDays > 0 ? signalsDays : 0) + filled;

  let level: ObservationAccuracyLevel = "initial";
  if (evidence >= 10) level = "stable";
  else if (evidence >= 3) level = "forming";

  return { level, label: ACCURACY_LABELS[level], percent: null };
}

/** character_helps passport: contract helps only — never taxonomy thriveAreas mix-in. */
function buildStableHelps(_thriveAreas: string[], contractHelps: string[] = []): string[] {
  return filterProfileCopyList([...(contractHelps ?? [])], 4, getLocale());
}

function buildElementLabel(coreProfile: CoreProfile | null): string | null {
  const element = elementRuName(coreProfile?.astro?.sun_element?.trim());
  const moonElement = coreProfile?.baseline?.element_focus?.trim() ?? "";
  if (element && moonElement && element !== moonElement) {
    return `Стихия: ${element} + ${moonElement}`;
  }
  if (element) return `Стихия: ${element}`;
  if (moonElement) return `Стихия: ${moonElement}`;
  return null;
}

function evidenceTitleFor(depth: ProfileSourceDepth, level: ObservationAccuracyLevel): string {
  if (depth === "longitudinal_profile" || level === "stable") {
    return "На чём держится портрет";
  }
  if (depth === "profile_plus_checkins" || level === "forming") {
    return "Картина ещё складывается";
  }
  return "Пока общий портрет";
}

export function buildProfileV2LiveContext(input: {
  coreProfile: CoreProfile | null;
  cum: CompactUserModel | null;
  thriveAreas?: string[];
  localClosedDays?: number;
}): ProfileV2LiveContext {
  const accuracy = resolveObservationAccuracy(input);
  const sourceDepth = resolveProfileSourceDepth(input);
  const contractHelps = input.coreProfile?.profile_contract_v1?.helps ?? [];
  const delta = formatDelta30dLabel(input.cum?.confidence?.delta_30d);
  const nextBase = DEPTH_NEXT[sourceDepth];
  const evidenceNextStep =
    nextBase && delta ? `${nextBase} (${delta})` : nextBase;
  const helpsRevealed = profileSlotRevealed(input.coreProfile, PROFILE_SLOT_HELPS);
  const helpsInResult = profileSlotInResult(input.coreProfile, PROFILE_SLOT_HELPS);
  const stableHelps = helpsRevealed
    ? buildStableHelps(input.thriveAreas ?? [], contractHelps)
    : [];

  return {
    observationAccuracyLevel: accuracy.level,
    observationAccuracyLabel: accuracy.label,
    sourceDepth,
    evidenceTitle: evidenceTitleFor(sourceDepth, accuracy.level),
    evidenceBody: DEPTH_HONESTY[sourceDepth],
    evidenceNextStep,
    helps: stableHelps,
    helpsAccessGated: Boolean(helpsInResult && !helpsRevealed && (contractHelps.length > 0 || (input.thriveAreas?.length ?? 0) > 0)),
    userMessages: profileUserMessages(input.coreProfile),
    elementLabel: buildElementLabel(input.coreProfile),
    journey: buildProfileJourneyProjection(input.coreProfile),
  };
}
