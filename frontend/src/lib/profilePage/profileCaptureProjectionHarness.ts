/**
 * Production-faithful FE projection for Profile capture packs.
 * Uses the same builders as /profile (QuickMap + V2 live context).
 * No alternate projection logic.
 */

import type { CoreProfile } from "@/lib/types";
import { zodiacRuName } from "@/lib/zodiacKnowledge";
import { archetypeDisplayLabel } from "@/lib/visualIdentity/registry";
import { buildProfileV0ViewModel } from "./buildProfileV0Data";
import {
  buildProfileChartFrameworkInput,
  buildProfileQuickMapViewModel,
  type ProfileQuickMapViewModel,
} from "./buildProfileQuickMapData";
import { buildProfileV2LiveContext } from "./buildProfileV2LiveContext";
import { buildProfileLifeSpheresFromProfileData } from "./profileLifeSpheres";

export type CaptureVisibleBlocks = {
  identity: string[];
  character: string[];
  direction: string[];
  /** Contract life_spheres as shown on Profile V2 Direction cards. */
  life_spheres: string[];
  evidence: string[];
  sources: string[];
};

export type CaptureFrontendProjection = {
  quick_map: ProfileQuickMapViewModel;
  v2_live: ReturnType<typeof buildProfileV2LiveContext>;
  display_name: string | null;
};

function sunDisplay(core: CoreProfile): string | null {
  const raw = core.astro?.sun_sign;
  if (!raw || typeof raw !== "string") return null;
  return zodiacRuName(raw) || raw;
}

function collectVisibleBlocks(
  quick: ProfileQuickMapViewModel,
  live: ReturnType<typeof buildProfileV2LiveContext>,
  core: CoreProfile,
): CaptureVisibleBlocks {
  const contract = core.profile_contract_v1;
  const sphereCards = buildProfileLifeSpheresFromProfileData(null, core);
  const lifeSphereLines = sphereCards.flatMap((s) => [
    `${s.id}:${s.title}`,
    s.how,
    s.need,
    s.risk,
    s.turnsOn,
    s.turnsOff,
    s.helps,
  ]);
  return {
    identity: [
      quick.archetype,
      quick.identitySummary,
      ...(quick.frameworkAnchors?.map((a) => a.label) ?? []),
    ].filter((x): x is string => Boolean(x?.trim())),
    character: [
      ...quick.strengthens,
      ...quick.drains,
      quick.decisionStyle,
      ...(contract?.relationship_style ? [String(contract.relationship_style)] : []),
      ...(contract?.money_style ? [String(contract.money_style)] : []),
    ].filter((x): x is string => Boolean(x?.trim())),
    direction: [
      quick.lifeMission,
      ...quick.thriveAreas,
      ...(Array.isArray(contract?.recurring_patterns)
        ? contract.recurring_patterns.map(String)
        : []),
      ...(contract?.living_changes ? [String(contract.living_changes)] : []),
      ...lifeSphereLines,
    ].filter((x): x is string => Boolean(x?.trim())),
    life_spheres: lifeSphereLines.filter((x): x is string => Boolean(x?.trim())),
    evidence: [live.evidenceTitle, live.evidenceBody, live.evidenceNextStep, live.sourceDepth]
      .filter((x): x is string => Boolean(x && String(x).trim())),
    sources: [
      ...(quick.frameworkCards?.map((c) => `${c.title}: ${c.body}`) ?? []),
      core.astro?.sun_sign ? `sun:${core.astro.sun_sign}` : null,
      core.numerology?.life_path != null ? `life_path:${core.numerology.life_path}` : null,
      core.astro?.time_unknown === false ? "birth_time:known" : "birth_time:unknown_or_missing",
      core.astro?.location_name ? `location:${core.astro.location_name}` : "location:missing",
    ].filter((x): x is string => Boolean(x?.trim())),
  };
}

function findDivergences(
  core: CoreProfile,
  quick: ProfileQuickMapViewModel,
): Array<{ claim: string; from: string; to: string; class: string; note: string }> {
  const out: Array<{ claim: string; from: string; to: string; class: string; note: string }> = [];
  const contract = core.profile_contract_v1;
  const decision = contract?.decision_style ? String(contract.decision_style).trim() : "";
  if (decision && quick.decisionStyle && decision !== quick.decisionStyle) {
    const overlap =
      decision.includes(quick.decisionStyle.slice(0, 40)) ||
      quick.decisionStyle.includes(decision.slice(0, 40));
    if (!overlap) {
      out.push({
        claim: decision.slice(0, 120),
        from: "API.profile_contract_v1.decision_style",
        to: "QuickMap.decisionStyle",
        class: "PROJECTION",
        note: "decision_style rewritten or replaced by taxonomy/CUM",
      });
    }
  }
  const patterns = Array.isArray(contract?.recurring_patterns) ? contract.recurring_patterns : [];
  for (const p of patterns) {
    const text = String(p || "").trim();
    if (!text) continue;
    const blob = JSON.stringify(quick);
    if (!blob.includes(text.slice(0, 48))) {
      out.push({
        claim: text.slice(0, 120),
        from: "API.recurring_patterns",
        to: "QuickMap",
        class: "UI_GATE",
        note: "pattern present in contract but not visible in QuickMap strings",
      });
    }
  }
  const spheres = contract?.life_spheres;
  if (spheres && typeof spheres === "object") {
    const uiSpheres = buildProfileLifeSpheresFromProfileData(null, core);
    const uiBlob = JSON.stringify(uiSpheres);
    for (const [sid, row] of Object.entries(spheres)) {
      if (!row || typeof row !== "object") continue;
      const need = String((row as { need?: string }).need || "").trim();
      if (!need) continue;
      const shown = uiSpheres.some((s) => s.id === sid);
      if (!shown) {
        out.push({
          claim: `${sid}.need`,
          from: `API.life_spheres.${sid}`,
          to: "Direction.life_spheres",
          class: "UI_GATE",
          note: "sphere in contract but omitted from Profile V2 Direction cards",
        });
        continue;
      }
      if (!uiBlob.includes(need.slice(0, Math.min(40, need.length)))) {
        out.push({
          claim: need.slice(0, 120),
          from: `API.life_spheres.${sid}.need`,
          to: "Direction.life_spheres",
          class: "PROJECTION",
          note: "sphere need missing from UI projection",
        });
      }
    }
  }
  return out;
}

/** Project a CoreProfile GET body the same way Profile page does (minus natal card extras). */
export function projectCoreProfileForCapture(core: CoreProfile): {
  frontend_projection: CaptureFrontendProjection;
  visible_blocks: CaptureVisibleBlocks;
  divergences: Array<{ claim: string; from: string; to: string; class: string; note: string }>;
} {
  const displayName =
    (core.person?.first_name as string | undefined) ||
    (core.person?.display_name as string | undefined) ||
    null;
  const v0 = buildProfileV0ViewModel({
    core,
    displayName: displayName || undefined,
  });
  const sun = sunDisplay(core);
  const lifePath = core.numerology?.life_path ?? null;
  const archetypeLabel = archetypeDisplayLabel(core.baseline?.archetype_seed, "ru", "") || "";
  const framework = buildProfileChartFrameworkInput({
    sunSignDisplay: sun,
    risingSign: null,
    mcSign: null,
    lifePath: typeof lifePath === "number" ? lifePath : null,
    archetypeLabel,
    chartCards: [],
  });
  const quick = buildProfileQuickMapViewModel(v0, framework, null, core.profile_contract_v1);
  const live = buildProfileV2LiveContext({
    coreProfile: core,
    cum: null,
    thriveAreas: quick.thriveAreas,
  });
  return {
    frontend_projection: {
      quick_map: quick,
      v2_live: live,
      display_name: displayName,
    },
    visible_blocks: collectVisibleBlocks(quick, live, core),
    divergences: findDivergences(core, quick),
  };
}
