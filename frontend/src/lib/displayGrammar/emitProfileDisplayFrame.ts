/**
 * Live Profile path frame — the same fields ProfileV2SystemScreen paints.
 * Explore / Character warehouse are not path acts.
 * Canon: DISPLAY_CONSTRUCTION_GRAMMAR_V1 §9 · PROFILE_DISPLAY_INVENTORY_V1
 */

import { compactProfileCopy } from "@/lib/profilePage/truncateProfileCopy";
import {
  buildProfileJourneyProjection,
  type ProfileJourneyNode,
} from "@/lib/profilePage/buildProfileJourneyProjection";
import { buildWhyFormationCards } from "@/lib/profilePage/buildWhyFormationCards";
import { profileHeaderFacts } from "@/lib/profilePage/profileHeaderFacts";
import { buildProfileLifeSpheresFromProfileData } from "@/lib/profilePage/profileLifeSpheres";
import type { CoreProfile } from "@/lib/types";
import type {
  DisplayAtom,
  DisplayScanInput,
  DisplaySurface,
  ExposedVmField,
  FeTransform,
  SemanticOrigin,
  TextClass,
} from "@/lib/displayGrammar/types";

const LINE_MAX = 120;

function trim(value: unknown): string {
  return String(value ?? "").trim();
}

function sameLine(a: string, b: string): boolean {
  return a.trim().toLowerCase() === b.trim().toLowerCase();
}

function pushAtom(
  atoms: DisplayAtom[],
  partial: {
    slot_id: string;
    surface?: DisplaySurface;
    text?: string | null;
    origins: SemanticOrigin[];
    text_class: TextClass;
    fe_transform?: FeTransform;
    json_field?: string;
    copy_key?: string;
  },
): void {
  const text = trim(partial.text);
  if (!text) return;
  atoms.push({
    slot_id: partial.slot_id,
    surface: partial.surface ?? "profile",
    text,
    origins: partial.origins,
    text_class: partial.text_class,
    fe_transform: partial.fe_transform ?? "none",
    json_field: partial.json_field,
    copy_key: partial.copy_key,
  });
}

function vm(
  fields: ExposedVmField[],
  field: string,
  value: unknown,
  slot_id?: string,
  would_render?: boolean,
): void {
  const filled = value != null && trim(value) !== "";
  fields.push({
    field,
    filled,
    slot_id,
    would_render: would_render ?? Boolean(filled && slot_id),
  });
}

function whySlotId(id: string, _role: string): string | null {
  const key = id.toLowerCase();
  if (key.startsWith("planet_in_sign:") || key.startsWith("planet_in_house:")) return null;
  if (key.includes("planet_in_sign:") || key.includes("planet_in_house:")) return null;
  if (key === "sun") return "P2.anchor.sun";
  if (key === "element") return "P2.anchor.element";
  if (key === "rhythm") return "P2.anchor.rhythm";
  if (key === "moon") return "P2.anchor.moon";
  if (key === "asc" || key === "rising") return "P2.anchor.asc";
  if (key === "mc") return "P2.anchor.mc";
  if (key === "life_path" || key === "archetype_from_life_path") return "P2.selected_life_path";
  return null;
}

function insightForScroll(
  node: ProfileJourneyNode | null,
  effortVector: string | null,
): ProfileJourneyNode | null {
  if (!node) return null;
  const help = node.help?.trim() || "";
  const effort = effortVector?.trim() || "";
  if (help && effort && help.toLowerCase() === effort.toLowerCase()) {
    return { ...node, help: null };
  }
  return node;
}

export type NatalDecodeEmitInput = {
  patternThesis?: string | null;
  sections?: Array<{ thesis?: string | null }>;
};

export type EmitProfileDisplayFrameInput = {
  core: CoreProfile | null | undefined;
  /** Explore only. Path frame must omit P6 — Decode / K16 tips are not path acts. */
  natalDecode?: NatalDecodeEmitInput | null;
  practicalTips?: string[] | null;
  /** Explore only. PIC-K03 ASC/MC + occupied-house how/do. */
  appliedHowDo?: {
    asc?: { how?: string | null; do?: string | null } | null;
    mc?: { how?: string | null; do?: string | null } | null;
    houses?: Record<string, { how?: string | null; do?: string | null } | undefined> | null;
  } | null;
};

export function natalDecodeSlotText(decode?: NatalDecodeEmitInput | null): string {
  const thesis = trim(decode?.patternThesis);
  if (thesis) return thesis;
  for (const section of decode?.sections ?? []) {
    const text = trim(section.thesis);
    if (text) return text;
  }
  return "";
}

/**
 * Project the production Profile path into a Grammar §9 scan frame.
 * Recognition may disclose identity_core behind the signal — not as the line.
 */
export function emitProfileDisplayFrame(input: EmitProfileDisplayFrameInput): DisplayScanInput {
  const journey = buildProfileJourneyProjection(input.core);
  const atoms: DisplayAtom[] = [];
  const vm_fields: ExposedVmField[] = [];

  const name = journey.recognition.name;
  const rawLine = journey.recognition.line;
  const core = journey.recognition.identityCore;
  const lineText = compactProfileCopy(rawLine || "", LINE_MAX) || null;
  const deeper = core && lineText && !sameLine(core, lineText) ? core : core && !lineText ? core : null;

  pushAtom(atoms, {
    slot_id: "P1.recognition_name",
    text: name,
    origins: ["ce"],
    text_class: "calc",
    fe_transform: "map_label",
  });
  pushAtom(atoms, {
    slot_id: "P1.recognition_line",
    text: lineText,
    origins: ["ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.recognition_line",
  });
  pushAtom(atoms, {
    slot_id: "P1.identity_core",
    text: deeper,
    origins: ["ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.identity_core",
  });
  if (journey.recognition.archetypeSeed) {
    pushAtom(atoms, {
      slot_id: "P1.visual",
      text: journey.recognition.archetypeSeed,
      origins: ["catalog"],
      text_class: "catalog",
    });
  }

  if (journey.why) {
    const { selected, influenced } = buildWhyFormationCards(
      [...journey.why.selectedBy, ...journey.why.influencedBy],
      {
        core: input.core,
        recognitionLine: rawLine,
        identityCore: core,
      },
    );
    for (const card of [...selected, ...influenced]) {
      const slot = whySlotId(card.id, card.role);
      if (!slot) continue;
      if (slot === "P2.selected_life_path" && !String(card.meaning || "").trim()) continue;
      const natalOk = slot !== "P2.selected_life_path" && slot !== "P2.anchor.rhythm";
      const selectedText =
        slot === "P2.selected_life_path"
          ? [card.title, card.meaning].filter(Boolean).join(" · ")
          : card.meaning || card.title;
      pushAtom(atoms, {
        slot_id: slot,
        text: selectedText,
        origins: natalOk ? ["natal", "ce"] : ["product"],
        text_class: "calc",
      });
    }
    for (const fact of profileHeaderFacts(input.core)) {
      pushAtom(atoms, {
        slot_id: fact.slot_id,
        text: fact.text,
        origins: fact.slot_id === "P2.correspondence" ? ["catalog"] : ["ce", "product"],
        text_class: fact.slot_id === "P2.correspondence" ? "catalog" : "calc",
      });
    }
  }

  const node = insightForScroll(journey.insightNode, journey.effortVector);
  if (node) {
    pushAtom(atoms, {
      slot_id: "P3.node_title",
      text: node.title,
      origins: ["ce"],
      text_class: "generated",
      fe_transform: "clip",
    });
    pushAtom(atoms, {
      slot_id: "P3.insight",
      text: node.insight,
      origins: ["ce"],
      text_class: "generated",
      fe_transform: "clip",
      json_field: "profile.insight",
    });
    for (const g of node.groundedOn) {
      pushAtom(atoms, {
        slot_id: "P3.grounded_on",
        text: g.label,
        origins: ["natal"],
        text_class: "calc",
      });
    }
    pushAtom(atoms, {
      slot_id: "P3.help",
      text: node.help,
      origins: ["ce"],
      text_class: "generated",
      fe_transform: "clip",
      json_field: "profile.help",
    });
    for (const q of node.livingEvidence) {
      pushAtom(atoms, {
        slot_id: "P3.living_evidence",
        text: q,
        origins: ["user"],
        text_class: "user",
      });
    }
  }

  pushAtom(atoms, {
    slot_id: "P4.effort_vector",
    text: journey.effortVector,
    origins: ["ce"],
    text_class: "projected",
    fe_transform: "clip",
    json_field: "profile.effort_vector",
  });
  if (journey.effortVector) {
    const pathSpheres = buildProfileLifeSpheresFromProfileData(null, input.core ?? null).slice(0, 2);
    for (const sphere of pathSpheres) {
      pushAtom(atoms, {
        slot_id: "P4.sphere.teaser",
        text: sphere.need || sphere.how,
        origins: ["ce"],
        text_class: "generated",
        fe_transform: "clip",
        json_field: "profile.life_spheres.need",
      });
      const expand = [sphere.how, sphere.risk].map((part) => trim(part)).filter(Boolean);
      const expandText = expand.join(" ");
      const teaser = trim(sphere.need || sphere.how);
      pushAtom(atoms, {
        slot_id: "P4.sphere.expand",
        text: expandText && expandText !== teaser ? expandText : sphere.how,
        origins: ["ce"],
        text_class: "generated",
        fe_transform: "clip",
        json_field: "profile.life_spheres.how",
      });
    }
  }
  pushAtom(atoms, {
    slot_id: "P5.bridge_line",
    text: journey.bridge?.line,
    origins: ["ce"],
    text_class: "projected",
    fe_transform: "clip",
    json_field: "profile.bridge_line",
  });

  const decodeText = natalDecodeSlotText(input.natalDecode);
  pushAtom(atoms, {
    slot_id: "P6.natal_decode",
    surface: "explore",
    text: decodeText,
    origins: ["natal", "ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.natal_decode",
  });
  const tipText = (input.practicalTips ?? [])
    .map((row) => trim(row))
    .filter(Boolean)
    .slice(0, 2)
    .join(" ");
  pushAtom(atoms, {
    slot_id: "P6.practical_tips",
    surface: "explore",
    text: tipText,
    origins: ["ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.practical_tips",
  });

  vm(vm_fields, "profile.recognition_line", rawLine, "P1.recognition_line", Boolean(lineText));
  vm(vm_fields, "profile.identity_core", core, "P1.identity_core", Boolean(deeper));
  vm(vm_fields, "profile.insight", node?.insight, "P3.insight", Boolean(node?.insight));
  vm(vm_fields, "profile.help", node?.help, "P3.help", Boolean(node?.help));
  vm(vm_fields, "profile.effort_vector", journey.effortVector, "P4.effort_vector", Boolean(journey.effortVector));
  vm(vm_fields, "profile.bridge_line", journey.bridge?.line, "P5.bridge_line", Boolean(journey.bridge?.line));
  vm(vm_fields, "profile.natal_decode", decodeText, "P6.natal_decode", Boolean(decodeText));
  const applied = input.appliedHowDo;
  const appliedAsc = [trim(applied?.asc?.how), trim(applied?.asc?.do)].filter(Boolean).join(" ");
  pushAtom(atoms, {
    slot_id: "P6.applied.asc",
    surface: "explore",
    text: appliedAsc,
    origins: ["natal", "ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.applied.asc",
  });
  const appliedMc = [trim(applied?.mc?.how), trim(applied?.mc?.do)].filter(Boolean).join(" ");
  pushAtom(atoms, {
    slot_id: "P6.applied.mc",
    surface: "explore",
    text: appliedMc,
    origins: ["natal", "ce"],
    text_class: "generated",
    fe_transform: "clip",
    json_field: "profile.applied.mc",
  });
  const houseRows = Object.entries(applied?.houses ?? {})
    .map(([id, row]) => {
      const text = [trim(row?.how), trim(row?.do)].filter(Boolean).join(" ");
      return { id, text };
    })
    .filter((row) => row.text)
    .slice(0, 8);
  for (const row of houseRows) {
    pushAtom(atoms, {
      slot_id: "P6.applied.house",
      surface: "explore",
      text: row.text,
      origins: ["natal", "ce"],
      text_class: "generated",
      fe_transform: "clip",
      json_field: "profile.applied.house",
    });
  }

  vm(vm_fields, "profile.practical_tips", tipText, "P6.practical_tips", Boolean(tipText));
  vm(vm_fields, "profile.applied.asc", appliedAsc, "P6.applied.asc", Boolean(appliedAsc));
  vm(vm_fields, "profile.applied.mc", appliedMc, "P6.applied.mc", Boolean(appliedMc));
  vm(
    vm_fields,
    "profile.applied.house",
    houseRows.map((row) => row.text).join(" "),
    "P6.applied.house",
    houseRows.length > 0,
  );

  return {
    atoms,
    vm_fields,
    journey: {
      surface: "profile",
      can_finish_sentence: Boolean(lineText || name || deeper),
    },
  };
}
