import type { ProfileV0ViewModel } from "./buildProfileV0Data";
import { textsOverlap } from "./profileContentLedger";

export type ProfileUiStringEntry = {
  layer: string;
  field: string;
  text: string;
};

function push(out: ProfileUiStringEntry[], layer: string, field: string, text: string | null | undefined) {
  const t = text?.trim();
  if (t) out.push({ layer, field, text: t });
}

/** All user-visible copy on Profile v0 at default (collapsed) state. */
export function collectProfileV0UiStrings(model: ProfileV0ViewModel): ProfileUiStringEntry[] {
  const out: ProfileUiStringEntry[] = [];
  const { header, who, numbers, socialMirror, love, money, action } = model;

  push(out, "hero", "poeticCaption", header.poeticCaption);
  push(out, "hero", "intro", header.intro);
  push(out, "hero", "metaLine", header.metaLine);
  for (const q of header.qualities) {
    push(out, "hero", "quality", `${q.title} ${q.subtitle}`.trim());
  }

  if (who) {
    push(out, "why", "manifest", who.whyManifest);
    for (const line of who.whyInsights.slice(1)) push(out, "why", "insight", line);
  }

  if (numbers) {
    push(out, "corePattern", "heroBlurb", numbers.hero.blurb);
    push(out, "corePattern", "trap", numbers.second?.blurb);
    push(out, "corePattern", "decisions", numbers.third?.blurb);
    push(out, "corePattern", "recovery", numbers.expand.birthDay?.blurb);
    push(out, "corePattern", "together", numbers.expand.togetherDigest);
  }

  if (socialMirror) {
    push(out, "socialMirror", "lead", socialMirror.lead);
    for (const obs of socialMirror.observations) push(out, "socialMirror", "observation", obs);
  }

  if (love) {
    push(out, "love", "style", love.style);
    push(out, "love", "whatMatters", love.whatMatters);
    push(out, "love", "strength", love.strength);
    push(out, "love", "watchout", love.watchout);
  }

  if (money) {
    push(out, "money", "approach", money.approach);
    push(out, "money", "helps", money.helps);
    push(out, "money", "blocks", money.blocks);
    push(out, "money", "workStyle", money.workStyle);
  }

  if (action) {
    push(out, "compass", "title", action.title);
    push(out, "compass", "mainText", action.mainText);
    for (const rule of action.rules) push(out, "compass", "rule", rule);
    push(out, "compass", "recommendation", action.recommendation);
  }

  return out;
}

export type ProfileUiDuplicatePair = {
  a: ProfileUiStringEntry;
  b: ProfileUiStringEntry;
};

export function findProfileUiDuplicates(entries: ProfileUiStringEntry[]): ProfileUiDuplicatePair[] {
  const pairs: ProfileUiDuplicatePair[] = [];
  for (let i = 0; i < entries.length; i++) {
    for (let j = 0; j < i; j++) {
      if (textsOverlap(entries[i].text, entries[j].text)) {
        pairs.push({ a: entries[j], b: entries[i] });
      }
    }
  }
  return pairs;
}

/** Detect mid-word truncation on insight lines (not meta labels). */
export function looksTruncated(text: string, field?: string): boolean {
  if (field === "metaLine") return false;
  const t = text.trim();
  if (!t) return false;
  if (/[.!?…]$/.test(t)) return false;
  const words = t.split(/\s+/);
  const last = words[words.length - 1] ?? "";
  if (last.length <= 2) return true;
  if (/^(и|а|но|не|в|на|к|с|о|у|за|по|от|до|из|что|как|или|для|при|без|под|над|между|через|когда|где|если|чтобы|ли|бы|же|то|это|тот|та|те|тем|том|так|ещё|еще|уже|очень|более|менее|может|можно|нужно|важно|важнее|сильнее|лучше|хуже|больше|меньше)$/i.test(last)) {
    return true;
  }
  return false;
}
