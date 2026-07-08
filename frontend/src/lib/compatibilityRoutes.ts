import type { AstroProfile, CoreProfile } from "@/lib/types";

type CompatibilityRelationMode = "romantic" | "family" | "parent_child" | "business";
type CompatibilityPreference = CompatibilityRelationMode | "any";

export type CompatibilityProfileLike = {
  id: number;
  label: string;
  relation?: "self" | "partner" | "child" | "close_person" | null;
  is_primary?: boolean;
  is_selected?: boolean;
  birth_date?: string | null;
  birth_time?: string | null;
  time_unknown?: boolean | null;
  location_name?: string | null;
  sun_sign?: string | null;
  birth_facts_corrections_used?: number;
  birth_facts_corrections_max?: number;
  birth_facts_corrections_remaining?: number;
  birth_facts_cooldown_remaining_seconds?: number;
};

export type CompatibilityRoute = {
  href: string;
  label: string;
};

const BUSINESS_HINTS = ["коллег", "работ", "босс", "команда", "проект", "клиент"];

function isSelfProfile(profile: CompatibilityProfileLike, primaryProfileId?: number | null) {
  if (profile.relation === "self" || profile.is_primary) return true;
  if (primaryProfileId && profile.id === primaryProfileId) return true;
  return false;
}

export function inferCompatibilityRelationMode(profile: CompatibilityProfileLike): CompatibilityRelationMode {
  if (profile.relation === "child") return "parent_child";
  if (profile.relation === "partner") return "romantic";
  const normalized = profile.label.toLowerCase();
  if (BUSINESS_HINTS.some((hint) => normalized.includes(hint))) {
    return "business";
  }
  return "family";
}

function relationPriority(mode: CompatibilityRelationMode, preferred: CompatibilityPreference): number {
  if (preferred === "any") {
    if (mode === "romantic") return 0;
    if (mode === "parent_child") return 1;
    if (mode === "family") return 2;
    return 3;
  }
  if (mode === preferred) return 0;
  if (preferred === "family" && mode === "parent_child") return 1;
  if (preferred === "romantic" && mode === "family") return 2;
  if (preferred === "family" && mode === "romantic") return 2;
  return 3;
}

function routeLabelByMode(mode: CompatibilityRelationMode): string {
  if (mode === "parent_child" || mode === "family") return "Открыть семейную динамику";
  if (mode === "business") return "Открыть рабочую динамику";
  return "Открыть совместимость";
}

export function buildPairCompatibilityRoute(
  profile: CompatibilityProfileLike,
  primaryProfileId?: number | null,
): CompatibilityRoute {
  const relationMode = inferCompatibilityRelationMode(profile);
  if (!primaryProfileId) {
    return {
      href: "/account/profiles",
      label: "Открыть круг людей",
    };
  }

  return {
    href: `/compatibility?profile1=${primaryProfileId}&profile2=${profile.id}&relation_mode=${relationMode}`,
    label: routeLabelByMode(relationMode),
  };
}

export function buildQuickCompatibilityRoute({
  profiles,
  primaryProfileId,
  preferred = "any",
}: {
  profiles: CompatibilityProfileLike[];
  primaryProfileId?: number | null;
  preferred?: CompatibilityPreference;
}): CompatibilityRoute {
  const candidates = profiles
    .filter((profile) => !isSelfProfile(profile, primaryProfileId))
    .map((profile) => ({
      profile,
      mode: inferCompatibilityRelationMode(profile),
    }))
    .sort((left, right) => {
      const leftPriority = relationPriority(left.mode, preferred);
      const rightPriority = relationPriority(right.mode, preferred);
      if (leftPriority !== rightPriority) return leftPriority - rightPriority;
      return left.profile.label.localeCompare(right.profile.label, "ru-RU");
    });

  const winner = candidates[0];
  if (!winner || !primaryProfileId) {
    return {
      href: "/account/profiles",
      label: "Открыть круг людей",
    };
  }

  return {
    href: `/compatibility?profile1=${primaryProfileId}&profile2=${winner.profile.id}&relation_mode=${winner.mode}`,
    label: routeLabelByMode(winner.mode),
  };
}

export function getCoreProfileCircle(coreProfile: CoreProfile | null | undefined): CompatibilityProfileLike[] {
  return Array.isArray(coreProfile?.profiles?.items) ? coreProfile.profiles.items : [];
}

export function getPrimaryProfileId(
  profiles: CompatibilityProfileLike[],
  fallbackId?: number | null,
): number | null {
  return profiles.find((profile) => profile.is_primary || profile.relation === "self")?.id || fallbackId || null;
}

export function getPrimaryProfileIdFromCore(coreProfile: CoreProfile | null | undefined): number | null {
  return coreProfile?.profiles?.primary_profile_id || getPrimaryProfileId(getCoreProfileCircle(coreProfile));
}

export function normalizeProfilesForCompatibility(profiles: AstroProfile[]): CompatibilityProfileLike[] {
  return profiles.map((profile) => ({
    id: profile.id,
    label: profile.label,
    relation: profile.relation || null,
    is_primary: Boolean(profile.is_primary),
  }));
}
