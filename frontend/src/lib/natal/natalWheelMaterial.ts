/**
 * Natal wheel material hierarchy — strong aspects closer/heavier; soft farther/thinner.
 * CSS/SVG depth pass (no WebGL).
 */

export type NatalAspectKind =
  | "conjunction"
  | "opposition"
  | "square"
  | "trine"
  | "sextile"
  | "other";

export type NatalAspectWeight = "strong" | "medium" | "soft";

export type NatalAspectRenderStyle = {
  kind: NatalAspectKind;
  weight: NatalAspectWeight;
  /** Paint order: higher = drawn later (in front). */
  stack: number;
  color: string;
  dash: string;
  opacity: number;
  width: number;
  label: string;
};

const LABELS_RU: Record<NatalAspectKind, string> = {
  conjunction: "Соединение",
  opposition: "Оппозиция",
  square: "Квадрат",
  trine: "Трин",
  sextile: "Секстиль",
  other: "Связь",
};

const BASE: Record<
  NatalAspectKind,
  Omit<NatalAspectRenderStyle, "kind" | "weight" | "stack" | "label">
> = {
  conjunction: { color: "#8b6a3e", dash: "none", opacity: 0.86, width: 2.8 },
  opposition: { color: "#6b5340", dash: "9 5", opacity: 0.8, width: 2.9 },
  square: { color: "#a67c52", dash: "7 5", opacity: 0.78, width: 2.7 },
  trine: { color: "#c9a96e", dash: "none", opacity: 0.48, width: 1.55 },
  sextile: { color: "#b8956a", dash: "4 5", opacity: 0.42, width: 1.35 },
  other: { color: "#9a8b78", dash: "3 5", opacity: 0.36, width: 1.2 },
};

export function classifyAspectKind(aspectId: string | undefined | null, label?: string | null): NatalAspectKind {
  const id = String(aspectId || "").toLowerCase();
  const lb = String(label || "").toLowerCase();
  const hay = `${id} ${lb}`;
  if (hay.includes("conjunction") || hay.includes("соединен")) return "conjunction";
  if (hay.includes("opposition") || hay.includes("оппозиц")) return "opposition";
  if (hay.includes("square") || hay.includes("квадрат")) return "square";
  if (hay.includes("trine") || hay.includes("трин")) return "trine";
  if (hay.includes("sextile") || hay.includes("секстил")) return "sextile";
  return "other";
}

function weightFor(
  kind: NatalAspectKind,
  tension: string | undefined | null,
): NatalAspectWeight {
  const t = String(tension || "").toLowerCase();
  if (t === "high" || t === "hard") return "strong";
  if (t === "low" || t === "soft") return "soft";
  if (kind === "conjunction" || kind === "opposition" || kind === "square") return "strong";
  if (kind === "trine" || kind === "sextile") return "soft";
  return "medium";
}

function stackFor(weight: NatalAspectWeight, kind: NatalAspectKind): number {
  const w = weight === "strong" ? 30 : weight === "medium" ? 15 : 5;
  const k =
    kind === "opposition" || kind === "square"
      ? 3
      : kind === "conjunction"
        ? 2
        : kind === "trine"
          ? 1
          : 0;
  return w + k;
}

/**
 * Resolve stroke style for an aspect line — hierarchy by kind + optional tension_level.
 */
export function resolveNatalAspectRenderStyle(input: {
  aspect_id?: string | null;
  label?: string | null;
  tension_level?: string | null;
}): NatalAspectRenderStyle {
  const kind = classifyAspectKind(input.aspect_id, input.label);
  const weight = weightFor(kind, input.tension_level);
  const base = BASE[kind];
  let { opacity, width } = base;
  if (weight === "strong") {
    opacity = Math.min(opacity + 0.08, 0.95);
    width += 0.45;
  } else if (weight === "soft") {
    opacity = Math.max(opacity - 0.06, 0.28);
    width = Math.max(width - 0.15, 1.05);
  }
  return {
    kind,
    weight,
    stack: stackFor(weight, kind),
    color: base.color,
    dash: base.dash,
    opacity,
    width,
    label: LABELS_RU[kind] === "Связь" && input.label?.trim() ? input.label.trim() : LABELS_RU[kind],
  };
}
