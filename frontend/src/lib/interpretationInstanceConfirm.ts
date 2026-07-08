import type { CompactUserModel } from "@/lib/types";
import type { InterpretationResonance } from "@/lib/todayInterpretationConfirm";

export type InterpretationInstanceRow = NonNullable<
  CompactUserModel["interpretation_instances_top_k"]
>[number];

export function mapInterpretationResonance(
  resonance: InterpretationResonance,
): "confirm" | "partial" | "reject" {
  if (resonance === "yes") return "confirm";
  if (resonance === "partial") return "partial";
  return "reject";
}

export function isCompatInterpretationRef(refId: string | undefined | null): boolean {
  return Boolean(refId?.startsWith("beh.compat_"));
}

export function pendingInterpretationInstances(
  rows: InterpretationInstanceRow[] | undefined,
  refIdFilter: (refId: string | undefined) => boolean,
  limit = 2,
): InterpretationInstanceRow[] {
  return (rows ?? [])
    .filter(
      (row) =>
        refIdFilter(row.interpretation_ref_id) &&
        !row.user_verdict &&
        Boolean(row.summary?.trim()) &&
        Boolean(row.instance_id),
    )
    .slice(0, limit);
}
