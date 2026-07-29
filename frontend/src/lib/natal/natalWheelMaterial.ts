/**
 * Natal wheel aspect hierarchy — color + weight (not thickness alone).
 * Soft (harmonious) = warm amber; hard (tension) = cool slate — readable on cream plate.
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

/**
 * Warm = harmonious; cool slate = tension. Contrast must read in ~0.3s on parchment.
 */
const BASE: Record<
  NatalAspectKind,
  Omit<NatalAspectRenderStyle, "kind" | "weight" | "stack" | "label">
> = {
  conjunction: { color: "#3d3228", dash: "none", opacity: 0.92, width: 3.0 },
  opposition: { color: "#4a5d73", dash: "8 5", opacity: 0.9, width: 2.95 },
  square: { color: "#5a6878", dash: "6 5", opacity: 0.88, width: 2.8 },
  trine: { color: "#c4782a", dash: "none", opacity: 0.78, width: 2.15 },
  sextile: { color: "#b0892e", dash: "4 4", opacity: 0.7, width: 1.85 },
  other: { color: "#7a6e5c", dash: "3 5", opacity: 0.5, width: 1.35 },
};

export function classifyAspectKind(aspectId: string | undefined | null, label?: string | null): NatalAspectKind {
  const id = String(aspectId || "").toLowerCase();
  const lb = String(label || "").toLowerCase();
  const hay = `${id} ${lb}`;
  if (hay.includes("conjunction") || hay.includes("соединен")) return "conjunction";
  if (hay.includes("opposition") || hay.includes("оппозиц")) return "opposition";
  // Minors before "square"/"квадрат" — sesquiquadrate / semisquare must not become Квадрат.
  if (
    hay.includes("sesqui") ||
    hay.includes("semi-square") ||
    hay.includes("semisquare") ||
    hay.includes("semi_square") ||
    hay.includes("полутораквадрат") ||
    hay.includes("полуквадрат") ||
    hay.includes("quin") ||
    hay.includes("inconjunct") ||
    hay.includes("quincunx") ||
    hay.includes("квиконс")
  ) {
    return "other";
  }
  if (hay.includes("square") || hay.includes("квадрат")) return "square";
  if (hay.includes("trine") || hay.includes("трин")) return "trine";
  if (hay.includes("sextile") || hay.includes("секстил")) return "sextile";
  return "other";
}

/** Legend + wheel + decode panel SoT: five Ptolemaic majors only. */
export const NATAL_MAJOR_ASPECT_KINDS: readonly NatalAspectKind[] = [
  "conjunction",
  "opposition",
  "square",
  "trine",
  "sextile",
] as const;

export function isMajorNatalAspect(kind: NatalAspectKind): boolean {
  return kind !== "other" && (NATAL_MAJOR_ASPECT_KINDS as readonly string[]).includes(kind);
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
  let { opacity, width, color } = base;
  if (weight === "strong") {
    opacity = Math.min(opacity + 0.05, 0.96);
    width += 0.35;
  } else if (weight === "soft") {
    opacity = Math.max(opacity - 0.04, 0.55);
    width = Math.max(width - 0.1, 1.5);
  }
  return {
    kind,
    weight,
    stack: stackFor(weight, kind),
    color,
    dash: base.dash,
    opacity,
    width,
    // Never surface raw EN labels (e.g. "Sun Sesquiquadrate Moon") in RU UI.
    label: LABELS_RU[kind],
  };
}

/** Legend swatches — same SoT as live strokes. */
export function natalAspectLegendItems(): Array<{
  kind: NatalAspectKind;
  label: string;
  color: string;
  dash: string;
}> {
  const order: NatalAspectKind[] = ["conjunction", "trine", "sextile", "square", "opposition"];
  return order.map((kind) => ({
    kind,
    label: LABELS_RU[kind],
    color: BASE[kind].color,
    dash: BASE[kind].dash,
  }));
}
