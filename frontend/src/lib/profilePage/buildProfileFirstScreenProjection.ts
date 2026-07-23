/**
 * Profile first-screen slots (Pattern-style recognition surface).
 * Pure reshape of existing CoreProfile / contract fields — no new LLM step.
 *
 * Passport:
 * | Slot            | Source                         | Appear when        |
 * | who             | recognition_line               | non-empty          |
 * | decisions       | decision_style                 | usable copy        |
 * | intimacy        | relationship_style             | usable copy        |
 * | self_friction   | growth_zones[0] ‖ patterns[0]  | usable copy        |
 * | contradiction   | insight_nodes_v0.nodes[0]      | title+insight      |
 * | helps           | effort_vector ‖ helps[0]       | non-empty          |
 */
import type { CoreProfile } from "@/lib/types";
import { getLocale } from "@/lib/i18n";
import { isUsableProfileCopy } from "@/lib/profilePage/profileCopySafety";
import { profileHelpsLineFromMatrix, profileSlotRevealed, PROFILE_SLOT_HELPS } from "@/lib/profilePage/profileMatrixAccess";
import { compactProfileCopy, firstSentence } from "@/lib/profilePage/truncateProfileCopy";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";

export type ProfileFirstScreenTraitId = "decisions" | "intimacy" | "self_friction";

export type ProfileFirstScreenTrait = {
  id: ProfileFirstScreenTraitId;
  label: string;
  line: string;
};

export type ProfileFirstScreenContradiction = {
  title: string;
  insight: string;
};

export type ProfileFirstScreenProjection = {
  whoLine: string | null;
  archetypeLabel: string | null;
  archetypeSeed: string | null;
  traits: ProfileFirstScreenTrait[];
  contradiction: ProfileFirstScreenContradiction | null;
  helpsLine: string | null;
  bridgeLine: string | null;
  hasFullProfileBody: boolean;
};

const TRAIT_LABELS: Record<ProfileFirstScreenTraitId, string> = {
  decisions: "Как принимаешь решения",
  intimacy: "Как строишь близость",
  self_friction: "Где сам себе мешаешь",
};

const TRAIT_MAX = 160;

function shortTraitLine(raw: string | null | undefined): string | null {
  const locale = getLocale();
  if (!isUsableProfileCopy(raw, locale)) return null;
  return compactProfileCopy(firstSentence(String(raw).trim()), TRAIT_MAX) || null;
}

export function buildProfileFirstScreenProjection(
  core: CoreProfile | null | undefined,
  opts?: { hasDeepSources?: boolean; hasDirectionOrCharacter?: boolean },
): ProfileFirstScreenProjection {
  const contract = core?.profile_contract_v1;
  const seed = core?.baseline?.archetype_seed?.trim() || null;
  const archetypeLabel = seed ? archetypeDisplayLabel(seed, "ru") : null;
  const whoLine = contract?.recognition_line?.trim() || null;

  const traits: ProfileFirstScreenTrait[] = [];
  const decisions = shortTraitLine(contract?.decision_style);
  if (decisions) {
    traits.push({ id: "decisions", label: TRAIT_LABELS.decisions, line: decisions });
  }
  const intimacy = shortTraitLine(contract?.relationship_style);
  if (intimacy) {
    traits.push({ id: "intimacy", label: TRAIT_LABELS.intimacy, line: intimacy });
  }
  const frictionRaw =
    contract?.growth_zones?.[0]?.trim() ||
    contract?.recurring_patterns?.[0]?.trim() ||
    null;
  const friction = shortTraitLine(frictionRaw);
  if (friction) {
    traits.push({ id: "self_friction", label: TRAIT_LABELS.self_friction, line: friction });
  }

  const rawNode = core?.insight_nodes_v0?.nodes?.[0];
  let contradiction: ProfileFirstScreenContradiction | null = null;
  if (rawNode?.insight?.trim() && rawNode.title?.trim()) {
    contradiction = {
      title: rawNode.title.trim(),
      insight: compactProfileCopy(rawNode.insight.trim(), 280) || rawNode.insight.trim(),
    };
  }

  const helpsLineRaw =
    profileHelpsLineFromMatrix(core) ||
    core?.effort_vector_v0?.effort_vector?.trim() ||
    contract?.helps?.[0]?.trim() ||
    rawNode?.help?.trim() ||
    null;
  const helpsLine = profileSlotRevealed(core, PROFILE_SLOT_HELPS) ? helpsLineRaw : null;

  const bridgeLine = core?.bridge_line_v0?.bridge_line?.trim() || null;

  return {
    whoLine,
    archetypeLabel,
    archetypeSeed: seed,
    traits,
    contradiction,
    helpsLine,
    bridgeLine,
    hasFullProfileBody: Boolean(opts?.hasDeepSources || opts?.hasDirectionOrCharacter),
  };
}
