/**
 * Grammar §9 Inventory scanner — legality of origin and placement, not prose quality.
 * Findings 7 / 12 / 15 / 17 / 18 stay in todayDisplayLockAudit and are merged here.
 * Canon: docs/foundation/DISPLAY_CONSTRUCTION_GRAMMAR_V1.md §9
 */

import { chromeSlotForLiteral } from "@/lib/displayGrammar/chromeRegistry";
import { isKnownTextClass, matchInventorySlot } from "@/lib/displayGrammar/inventoryCatalog";
import {
  FORBIDDEN_RENDER_FIELDS,
  projectionSlotForField,
} from "@/lib/displayGrammar/projectionManifest";
import type {
  DisplayAtom,
  DisplayGrammarFinding,
  DisplayScanInput,
  GrammarFindingId,
} from "@/lib/displayGrammar/types";
import {
  auditTodayActionSlotLock,
  auditTodayFocusSplitLock,
  auditTodayInventedFallback,
  auditTodayRitualLensLock,
} from "@/lib/todayDisplayLockAudit";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayCapabilityDepth } from "@/lib/todayScreenFlowCapability";

const T1_CONTAMINATION = new Set([
  "natal",
  "ce",
  "personal_day",
  "ritual_identity",
  "card",
  "number",
  "goals",
  "behavior",
]);

const RITUAL_AS_GLOBAL = new Set(["ritual_identity", "card", "number"]);

function push(
  out: DisplayGrammarFinding[],
  grammar: GrammarFindingId,
  code: string,
  extra: Partial<DisplayGrammarFinding> = {},
): void {
  if (out.some((f) => f.grammar === grammar && f.slot_id === extra.slot_id && f.code === code)) return;
  out.push({ grammar, code, ...extra });
}

function norm(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

function isMeaningAtom(atom: DisplayAtom): boolean {
  if (atom.text_class === "chrome") return false;
  return Boolean(String(atom.text ?? "").trim() || atom.json_field);
}

export function scanDisplayGrammar(input: DisplayScanInput): DisplayGrammarFinding[] {
  const out: DisplayGrammarFinding[] = [];
  const atoms = input.atoms ?? [];

  for (const field of input.vm_fields ?? []) {
    if (!field.filled || field.would_render === false) continue;
    if (FORBIDDEN_RENDER_FIELDS.includes(field.field as (typeof FORBIDDEN_RENDER_FIELDS)[number])) {
      if (field.would_render) {
        push(out, 2, "legacy_field_rendered", { detail: field.field, slot_id: field.slot_id });
      }
      continue;
    }
    const mapped = field.slot_id || projectionSlotForField(field.field);
    if (field.would_render && !mapped) {
      push(out, 2, "json_without_slot", { detail: field.field });
    }
  }

  for (const atom of atoms) {
    scanAtom(atom, input, out);
  }

  scanCounts(atoms, out);
  scanAntiDupe(atoms, out);
  scanEveningGate(input, out);
  scanJourney(input, atoms, out);
  mergeTodayLockRegression(input, out);
  return out;
}

function scanAtom(atom: DisplayAtom, input: DisplayScanInput, out: DisplayGrammarFinding[]): void {
  const text = String(atom.text ?? "").trim();
  const slotId = String(atom.slot_id ?? "").trim();

  if (atom.empty_filled && (text || atom.json_field)) {
    push(out, 7, "invented_fallback", { slot_id: slotId || undefined, detail: "empty filled" });
  }

  if (atom.copy_key && text && !chromeSlotForLiteral(text) && !slotId) {
    push(out, 1, "copy_key_not_in_inventory", { detail: atom.copy_key });
  }

  if (!slotId) {
    if (isMeaningAtom(atom)) {
      push(out, 2, "json_without_slot", { detail: atom.json_field || atom.copy_key });
    }
    return;
  }

  const record = matchInventorySlot(slotId);
  if (!record) {
    push(out, 1, "slot_not_in_inventory", { slot_id: slotId });
    return;
  }

  if (atom.surface !== record.surface && record.surface !== "chrome-shared") {
    push(out, 1, "surface_mismatch", {
      slot_id: slotId,
      detail: `${atom.surface}≠${record.surface}`,
    });
  }

  const klass = atom.text_class || record.text_class;
  if (atom.text_class && !isKnownTextClass(atom.text_class)) {
    push(out, 8, "unknown_text_class", { slot_id: slotId, detail: atom.text_class });
  } else if (!isKnownTextClass(klass)) {
    push(out, 8, "unknown_text_class", { slot_id: slotId, detail: klass });
  }

  if (record.surface === "today") {
    for (const origin of atom.origins) {
      if (T1_CONTAMINATION.has(origin)) {
        push(out, RITUAL_AS_GLOBAL.has(origin) ? 5 : 4, "global_contamination", {
          slot_id: slotId,
          detail: origin,
        });
      }
    }
  }

  if (record.surface === "my_day") {
    for (const origin of atom.origins) {
      if (origin === "ce") {
        push(out, 16, "ce_in_personal_day", { slot_id: slotId, detail: atom.json_field });
      }
    }
    if (atom.json_field === "personal_growth.development_point") {
      push(out, 16, "ce_in_personal_day", { slot_id: slotId, detail: atom.json_field });
    }
  }

  for (const origin of atom.origins) {
    if (
      record.allowed_origins.length > 0 &&
      !record.allowed_origins.includes(origin) &&
      origin !== "chrome" &&
      origin !== "product"
    ) {
      if (record.surface === "today" && T1_CONTAMINATION.has(origin)) continue;
      if (record.surface === "my_day" && origin === "ce") continue;
      push(out, 2, "source_not_allowed", { slot_id: slotId, detail: origin });
    }
  }

  if ((record.text_class === "generated" || record.text_class === "projected") && atom.inputs_lock === false) {
    push(out, 14, "generated_without_inputs_lock", { slot_id: slotId });
  }

  const transform = atom.fe_transform ?? "none";
  const allowed = record.may_fe_transform;
  if (transform === "invent" || transform === "paraphrase" || transform === "fill_empty" || transform === "other") {
    push(out, 13, "fe_transform_out_of_frame", { slot_id: slotId, detail: transform });
  } else if (transform !== "none" && !allowed.includes(transform)) {
    push(out, 13, "fe_transform_out_of_frame", { slot_id: slotId, detail: transform });
  }

  if (record.text_class === "generated" && text && record.budget_chars && text.length > record.budget_chars) {
    push(out, 3, "over_budget", { slot_id: slotId, detail: `${text.length}>${record.budget_chars}` });
  }

  const depth = input.capability;
  if (slotId.startsWith("T2.lens_") && text) {
    if (depth === "guest" || depth === "general") {
      push(out, 12, "guest_or_general_lens", { slot_id: slotId });
    }
    if (input.personal_day_persisted === false) {
      push(out, 15, "lens_without_persist", { slot_id: slotId });
    }
  }
  if (slotId.startsWith("T3.") && slotId !== "T3.unavailable" && record.text_class !== "chrome" && text) {
    if (depth === "guest" || depth === "general") {
      push(out, 12, "guest_or_general_lens", { slot_id: slotId, detail: "T3 meaning" });
    }
  }
}

function scanCounts(atoms: DisplayAtom[], out: DisplayGrammarFinding[]): void {
  const drivers = atoms.filter((a) => a.slot_id === "T1-clock.transit" && a.transit_kind !== "moon" && String(a.text ?? "").trim());
  if (drivers.length > 3) {
    push(out, 9, "too_many_t1_drivers", { slot_id: "T1-clock.transit", detail: String(drivers.length) });
  }
  const strength = atoms.filter((a) => a.slot_id === "T1-strength.chip" && String(a.text ?? "").trim());
  if (strength.length > 4) {
    push(out, 10, "too_many_strength_chips", { slot_id: "T1-strength.chip", detail: String(strength.length) });
  }
  const risk = atoms.filter((a) => a.slot_id === "T1-risk.chip" && String(a.text ?? "").trim());
  if (risk.length > 3) {
    push(out, 10, "too_many_risk_chips", { slot_id: "T1-risk.chip", detail: String(risk.length) });
  }
}

function scanAntiDupe(atoms: DisplayAtom[], out: DisplayGrammarFinding[]): void {
  const visible = atoms.filter((a) => a.slot_id && String(a.text ?? "").trim());
  for (let i = 0; i < visible.length; i += 1) {
    const a = visible[i]!;
    const recA = matchInventorySlot(a.slot_id!);
    if (!recA) continue;
    for (let j = i + 1; j < visible.length; j += 1) {
      const b = visible[j]!;
      if (a.slot_id === b.slot_id) continue;
      const recB = matchInventorySlot(b.slot_id!);
      if (!recB) continue;
      const shared = recA.anti_dupe_groups.filter((g) => recB.anti_dupe_groups.includes(g));
      if (!shared.length) continue;
      const sameText = norm(String(a.text)) === norm(String(b.text));
      const sameField = Boolean(a.json_field && a.json_field === b.json_field);
      if (sameText || sameField) {
        push(out, 6, "anti_dupe_collision", {
          slot_id: a.slot_id,
          detail: `${a.slot_id} ∩ ${b.slot_id} [${shared.join(",")}]`,
        });
      }
    }
  }
}

function scanEveningGate(input: DisplayScanInput, out: DisplayGrammarFinding[]): void {
  if (input.evening_in_scroll && input.evening_time_ok === false) {
    push(out, 11, "evening_before_time_gate", { slot_id: "T4.title" });
  }
}

function scanJourney(input: DisplayScanInput, atoms: DisplayAtom[], out: DisplayGrammarFinding[]): void {
  if (!input.journey) return;
  if (input.journey.can_finish_sentence) return;
  const onSurface = atoms.filter(
    (a) => a.surface === input.journey!.surface && String(a.text ?? "").trim() && a.text_class !== "chrome",
  );
  if (onSurface.length > 0) {
    push(out, 19, "journey_sentence_fail", { detail: input.journey.surface });
  }
}

function mergeTodayLockRegression(input: DisplayScanInput, out: DisplayGrammarFinding[]): void {
  const lock = input.today_lock;
  if (!lock) return;
  const depth = (input.capability ?? "guest") as TodayCapabilityDepth;
  const contract = {
    contract_version: "today_contract_v1",
    global_context: { period: "" },
    personal_growth: { development_point: lock.developmentPoint ?? "" },
    domains: {
      work: { status: "", opportunity: "", risk: "", action: "" },
      money: { status: "", opportunity: "", risk: "", action: "" },
      relationships: { status: "", opportunity: "", risk: "", action: "" },
      energy: { status: "", opportunity: "", risk: "", action: "" },
    },
    primary_action: lock.primaryAction ?? "",
    progress: {},
    generation_id: "scan",
    personal_day: input.personal_day_persisted ? { natal_overlay: { activations: [{ id: "scan" }] } } : undefined,
  } as TodayContractV1;

  for (const f of auditTodayInventedFallback({
    texts: lock.inventedTexts,
    developmentPoint: lock.developmentPoint,
  })) {
    push(out, f.grammar, f.code);
  }
  for (const f of auditTodayRitualLensLock({
    depth,
    contract,
    lensText: lock.lensText,
  })) {
    push(out, f.grammar, f.code);
  }
  for (const f of auditTodayActionSlotLock({
    focusTitle: lock.focusTitle,
    primaryAction: lock.primaryAction,
    priorities: lock.priorities,
    emptyTasksChrome: lock.emptyTasksChrome,
  })) {
    push(out, f.grammar, f.code);
  }
  for (const f of auditTodayFocusSplitLock({
    headline: lock.headline,
    focusTitle: lock.focusTitle,
  })) {
    push(out, f.grammar, f.code);
  }
}

export function findingIds(findings: DisplayGrammarFinding[]): GrammarFindingId[] {
  return Array.from(new Set(findings.map((f) => f.grammar))).sort((a, b) => a - b);
}
