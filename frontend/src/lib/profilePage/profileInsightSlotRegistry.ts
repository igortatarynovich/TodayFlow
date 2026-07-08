import { ProfileContentLedger, textsOverlap } from "./profileContentLedger";
import type { ProfileInsightLayer } from "./profileInsightBudget";
import { PROFILE_LAYER_TAXONOMY } from "./profileInsightTaxonomy";
import type {
  ProfileInsightSourceKind,
  ProfileTaxonomyInsightSlot,
} from "./profileInsightTypes";
import { compactProfileCopy, firstSentence } from "./truncateProfileCopy";

const DEFAULT_MIN_LEN = 20;

export type ClaimSlotInput = {
  layer: ProfileInsightLayer;
  categoryId: string;
  raw: string | null | undefined;
  sourceKind: ProfileInsightSourceKind;
  sourceKey: string;
  maxChars?: number;
  minLen?: number;
};

export class ProfileInsightSlotRegistry {
  private readonly ledger = new ProfileContentLedger();

  private readonly slots: ProfileTaxonomyInsightSlot[] = [];

  /** Fallback rule: no text → gap, never filler. */
  claimSlot(input: ClaimSlotInput): ProfileTaxonomyInsightSlot | null {
    const minLen = input.minLen ?? DEFAULT_MIN_LEN;
    const raw = input.raw?.trim();
    if (!raw || raw.length < minLen) return null;

    const max = input.maxChars ?? 240;
    const text = max >= 200 ? compactProfileCopy(raw, max) : compactProfileCopy(firstSentence(raw), max);
    if (!text || text.length < minLen) return null;
    if (this.ledger.hasOverlap(text)) return null;

    this.ledger.claim(text);
    const slot: ProfileTaxonomyInsightSlot = {
      layer: input.layer,
      categoryId: input.categoryId,
      text,
      sourceKind: input.sourceKind,
      sourceKey: input.sourceKey,
    };
    this.slots.push(slot);
    return slot;
  }

  seed(text: string | null | undefined): void {
    this.ledger.seed(text);
  }

  hasOverlap(text: string | null | undefined): boolean {
    return this.ledger.hasOverlap(text);
  }

  getSlots(): ProfileTaxonomyInsightSlot[] {
    return [...this.slots];
  }

  getSlotsForLayer(layer: ProfileInsightLayer): ProfileTaxonomyInsightSlot[] {
    return this.slots.filter((s) => s.layer === layer);
  }

  slotByCategory(layer: ProfileInsightLayer, categoryId: string): ProfileTaxonomyInsightSlot | null {
    return this.slots.find((s) => s.layer === layer && s.categoryId === categoryId) ?? null;
  }

  requiredCategoryIds(layer: ProfileInsightLayer): string[] {
    const spec = PROFILE_LAYER_TAXONOMY.find((s) => s.layer === layer);
    return spec?.categories.map((c) => c.id) ?? [];
  }

  missingCategoryIds(layer: ProfileInsightLayer): string[] {
    const filled = new Set(this.getSlotsForLayer(layer).map((s) => s.categoryId));
    return this.requiredCategoryIds(layer).filter((id) => !filled.has(id));
  }
}

export function formatSlotSource(slot: ProfileTaxonomyInsightSlot): string {
  return `${slot.sourceKind}:${slot.sourceKey}`;
}

/** Same-layer semantic duplicates (e.g. three «глубина» lines in Love). */
export function findSameLayerSemanticDuplicates(
  slots: ProfileTaxonomyInsightSlot[],
): Map<string, string> {
  const dup = new Map<string, string>();
  for (let i = 0; i < slots.length; i++) {
    for (let j = 0; j < i; j++) {
      if (slots[i].layer !== slots[j].layer) continue;
      if (textsOverlap(slots[i].text, slots[j].text)) {
        dup.set(`${slots[i].layer}:${slots[i].categoryId}`, `${slots[j].layer}:${slots[j].categoryId}`);
      }
    }
  }
  return dup;
}

export function findCrossLayerDuplicate(
  slot: ProfileTaxonomyInsightSlot,
  allSlots: ProfileTaxonomyInsightSlot[],
): ProfileTaxonomyInsightSlot | null {
  for (const other of allSlots) {
    if (other.layer === slot.layer && other.categoryId === slot.categoryId) continue;
    if (textsOverlap(slot.text, other.text)) return other;
  }
  return null;
}

const WEAK_TEMPLATE_KEYS = new Set([
  "compass.default_rules",
  "corePattern.fallback_blurb",
  "compass.fallback_main",
  "compass.fallback_today",
]);

export function isWeakSlot(slot: ProfileTaxonomyInsightSlot): boolean {
  if (slot.sourceKind === "template") return true;
  if (WEAK_TEMPLATE_KEYS.has(slot.sourceKey)) return true;
  if (slot.text.length < DEFAULT_MIN_LEN) return true;
  return false;
}
