import type { LifeMapSection } from "@/components/profile/profilePanelTypes";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { ProfileQuickMapViewModel } from "./buildProfileQuickMapData";
import type { ProfileV0ViewModel } from "./buildProfileV0Data";
import { textsOverlap } from "./profileContentLedger";
import {
  collectProfileV0UiStrings,
  findProfileUiDuplicates,
  type ProfileUiDuplicatePair,
  type ProfileUiStringEntry,
} from "./profileV0UiStringsAudit";

export type { ProfileUiDuplicatePair, ProfileUiStringEntry };

function isVerbatimHouseCopy(sphereText: string, houseSummary: string): boolean {
  const house = houseSummary.trim().toLowerCase();
  const sphere = sphereText.trim().toLowerCase();
  if (!house || !sphere || house.length < 16) return false;
  return sphere.includes(house);
}

function push(out: ProfileUiStringEntry[], layer: string, field: string, text: string | null | undefined) {
  const t = text?.trim();
  if (t) out.push({ layer, field, text: t });
}

export function collectProfileQuickMapUiStrings(model: ProfileQuickMapViewModel): ProfileUiStringEntry[] {
  const out: ProfileUiStringEntry[] = [];

  push(out, "hero", "archetype", model.archetype);
  push(out, "hero", "identitySummary", model.identitySummary);
  for (const item of model.strengthens) push(out, "resume", "strengthen", item);
  for (const item of model.drains) push(out, "resume", "drain", item);
  push(out, "decisions", "style", model.decisionStyle);
  for (const item of model.perceivedAs) push(out, "perceived", "tag", item);
  for (const item of model.thriveAreas) push(out, "thrive", "tag", item);
  push(out, "mission", "text", model.lifeMission);
  push(out, "relationship", "style", model.relationshipStyle);
  push(out, "money", "style", model.moneyStyle);
  push(out, "framework", "lead", model.frameworkLead);
  for (const anchor of model.frameworkAnchors) push(out, "framework", "anchor", anchor.label);
  for (const card of model.frameworkCards) {
    push(out, "framework", `${card.id}.body`, card.body);
    push(out, "framework", `${card.id}.anchor`, card.anchor);
  }

  return out;
}

export function findQuickMapUiDuplicates(model: ProfileQuickMapViewModel): ProfileUiDuplicatePair[] {
  return findProfileUiDuplicates(collectProfileQuickMapUiStrings(model));
}

/** Portrait love/money must not repeat collapsed natal house summaries (PM-1). */
export function findPortraitHouseCopyOverlaps(
  portrait: ProfileV0ViewModel,
  lifeMapSections: LifeMapSection[],
): ProfileUiDuplicatePair[] {
  const portraitEntries = collectProfileV0UiStrings(portrait).filter((entry) =>
    ["love", "money", "socialMirror"].includes(entry.layer),
  );
  const houseEntries: ProfileUiStringEntry[] = lifeMapSections.map((section) => ({
    layer: `house_${section.house}`,
    field: "summary",
    text: section.summary,
  }));

  const pairs: ProfileUiDuplicatePair[] = [];
  for (const house of houseEntries) {
    for (const sphere of portraitEntries) {
      if (textsOverlap(house.text, sphere.text)) {
        pairs.push({ a: house, b: sphere });
      }
    }
  }
  return pairs;
}

/** Life sphere `how` must not repeat collapsed natal house summaries (PM-1). */
export function findLifeSphereHouseCopyOverlaps(
  spheres: ProfileLifeSphere[],
  lifeMapSections: LifeMapSection[],
): ProfileUiDuplicatePair[] {
  const sphereEntries: ProfileUiStringEntry[] = spheres.map((sphere) => ({
    layer: `sphere_${sphere.id}`,
    field: "how",
    text: sphere.how,
  }));
  const houseEntries: ProfileUiStringEntry[] = lifeMapSections.map((section) => ({
    layer: `house_${section.house}`,
    field: "summary",
    text: section.summary,
  }));

  const pairs: ProfileUiDuplicatePair[] = [];
  for (const house of houseEntries) {
    for (const sphere of sphereEntries) {
      if (isVerbatimHouseCopy(sphere.text, house.text)) {
        pairs.push({ a: house, b: sphere });
      }
    }
  }
  return pairs;
}
