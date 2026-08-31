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

function whySlotId(id: string, role: string): string {
  const key = id.toLowerCase();
  if (role === "selected" || key === "life_path") return "P2.selected_life_path";
  if (key === "sun") return "P2.anchor.sun";
  if (key === "element") return "P2.anchor.element";
  if (key === "rhythm") return "P2.anchor.rhythm";
  if (key === "moon") return "P2.anchor.moon";
  if (key === "asc" || key === "rising") return "P2.anchor.asc";
  if (key === "mc") return "P2.anchor.mc";
  return role === "selected" ? "P2.selected_life_path" : "P2.anchor.rhythm";
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

export type EmitProfileDisplayFrameInput = {
  core: CoreProfile | null | undefined;
};

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
      const natalOk = slot !== "P2.selected_life_path" && slot !== "P2.anchor.rhythm";
      pushAtom(atoms, {
        slot_id: slot,
        text: card.meaning || card.title,
        origins: natalOk ? ["natal", "ce"] : ["ce"],
        text_class: "calc",
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
  pushAtom(atoms, {
    slot_id: "P5.bridge_line",
    text: journey.bridge?.line,
    origins: ["ce"],
    text_class: "projected",
    fe_transform: "clip",
    json_field: "profile.bridge_line",
  });

  vm(vm_fields, "profile.recognition_line", rawLine, "P1.recognition_line", Boolean(lineText));
  vm(vm_fields, "profile.identity_core", core, "P1.identity_core", Boolean(deeper));
  vm(vm_fields, "profile.insight", node?.insight, "P3.insight", Boolean(node?.insight));
  vm(vm_fields, "profile.help", node?.help, "P3.help", Boolean(node?.help));
  vm(vm_fields, "profile.effort_vector", journey.effortVector, "P4.effort_vector", Boolean(journey.effortVector));
  vm(vm_fields, "profile.bridge_line", journey.bridge?.line, "P5.bridge_line", Boolean(journey.bridge?.line));

  return {
    atoms,
    vm_fields,
    journey: {
      surface: "profile",
      can_finish_sentence: Boolean(lineText || name || deeper),
    },
  };
}
