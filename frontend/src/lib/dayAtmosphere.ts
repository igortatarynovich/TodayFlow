/**
 * Day Atmosphere — contracts (FOUNDATION_UI §12).
 *
 * Third, independent atmosphere axis — driven by the day's narrative
 * (`visual_mode`), not by the clock. Sits alongside, and does not replace:
 * - `productMoodTheme.ts` (`data-mood`) — emotional palette, driven by time of day + pin
 * - `dayPhaseAtmosphere.ts` (`data-day-phase`) — procedural time-of-day texture
 * See FOUNDATION_UI §11.1 for the layer priority: Day Atmosphere → Day-phase → Mood.
 *
 * This module defines the engine → frontend contract only, plus a deterministic
 * mapping from that contract to design tokens. It intentionally does not import
 * React, does not touch the DOM (aside from the pin helpers), and does not ship
 * a CSS file or bridge component — those are FOUNDATION_UI §13 (implementation).
 *
 * The day-narrative engine (LLM / astro engine) is only ever allowed to produce
 * a `DayAtmosphereContract`-shaped value — never raw colors or CSS. `resolveDayAtmosphere`
 * is the single choke point that turns arbitrary/untrusted engine output into a
 * closed, safe config; unknown or missing fields fall back to a neutral default
 * rather than throwing, so a bad engine response degrades gracefully instead of
 * breaking the shell.
 */

/** Closed set — FOUNDATION_UI §11.3. Do not widen without a doc update first. */
export type DayVisualMode =
  | "grounded"
  | "flow"
  | "radiance"
  | "momentum"
  | "clarity"
  | "tension"
  | "renewal"
  | "depth";

export const DAY_VISUAL_MODES: readonly DayVisualMode[] = [
  "grounded",
  "flow",
  "radiance",
  "momentum",
  "clarity",
  "tension",
  "renewal",
  "depth",
] as const;

export type DayMotion = "none" | "low";
export type DayContrast = "soft" | "medium" | "strong";
export type DayTimePhase = "morning" | "day" | "evening" | "night";

/**
 * What the day-narrative engine is allowed to output. Nothing else — no colors,
 * no CSS, no free-form strings besides `decor_variant` (which is looked up
 * against a closed per-mode set, see `resolveDecorVariant`).
 */
export interface DayAtmosphereContract {
  visual_mode: DayVisualMode;
  /** 0..1 — how strongly the mode's glow/decor reads. Clamped on resolve. */
  intensity: number;
  /** 0..1 — cool ↔ warm bias within the mode's palette. Clamped on resolve. */
  warmth: number;
  motion: DayMotion;
  contrast: DayContrast;
  decor_variant: string;
  /** Cross-checked against `data-day-phase`, not a duplicate generator. */
  time_phase: DayTimePhase;
}

export type ResolveDayAtmosphereInput = Partial<DayAtmosphereContract> & {
  /** Manual pin — mirrors `productMoodTheme`'s pin; wins over engine output. */
  pinnedMode?: DayVisualMode | null;
};

export const DAY_ATMOSPHERE_DEFAULT: DayAtmosphereContract = {
  visual_mode: "clarity",
  intensity: 0.4,
  warmth: 0.5,
  motion: "low",
  contrast: "medium",
  decor_variant: "default",
  time_phase: "day",
};

/** FOUNDATION_UI §11.3 — two decor compositions per mode, named not numbered. */
export const DAY_MODE_DECOR_VARIANTS: Record<DayVisualMode, readonly [string, string]> = {
  grounded: ["contour", "stones"],
  flow: ["ripple", "current"],
  radiance: ["rays", "bloom"],
  momentum: ["diagonal", "trail"],
  clarity: ["grid", "orbit"],
  tension: ["fracture", "crossline"],
  renewal: ["sprout", "horizon"],
  depth: ["still", "drift"],
};

export const DAY_MODE_LABELS_RU: Record<DayVisualMode, string> = {
  grounded: "Заземление",
  flow: "Поток",
  radiance: "Сияние",
  momentum: "Импульс",
  clarity: "Ясность",
  tension: "Напряжение",
  renewal: "Обновление",
  depth: "Глубина",
};

function isDayVisualMode(value: unknown): value is DayVisualMode {
  return typeof value === "string" && (DAY_VISUAL_MODES as readonly string[]).includes(value);
}

function clamp01(n: number | undefined, fallback: number): number {
  if (n === undefined || Number.isNaN(n)) return fallback;
  return Math.min(1, Math.max(0, n));
}

/** First variant is the default decor for a mode unless the engine names one explicitly. */
function resolveDecorVariant(mode: DayVisualMode, requested: string | undefined): string {
  const variants = DAY_MODE_DECOR_VARIANTS[mode];
  if (requested && (variants as readonly string[]).includes(requested)) return requested;
  return variants[0];
}

const CONTRASTS: readonly DayContrast[] = ["soft", "medium", "strong"];
const MOTIONS: readonly DayMotion[] = ["none", "low"];
const TIME_PHASES: readonly DayTimePhase[] = ["morning", "day", "evening", "night"];

/**
 * Pure resolver: partial/untrusted engine output (+ optional manual pin) →
 * closed `DayAtmosphereContract`. Never throws. Never returns a `visual_mode`
 * outside `DAY_VISUAL_MODES`.
 */
export function resolveDayAtmosphere(input: ResolveDayAtmosphereInput = {}): DayAtmosphereContract {
  const requestedMode = input.pinnedMode ?? input.visual_mode;
  const visual_mode = isDayVisualMode(requestedMode) ? requestedMode : DAY_ATMOSPHERE_DEFAULT.visual_mode;

  const contrast = input.contrast && CONTRASTS.includes(input.contrast) ? input.contrast : DAY_ATMOSPHERE_DEFAULT.contrast;
  const motion = input.motion && MOTIONS.includes(input.motion) ? input.motion : DAY_ATMOSPHERE_DEFAULT.motion;
  const time_phase =
    input.time_phase && TIME_PHASES.includes(input.time_phase) ? input.time_phase : DAY_ATMOSPHERE_DEFAULT.time_phase;

  return {
    visual_mode,
    intensity: clamp01(input.intensity, DAY_ATMOSPHERE_DEFAULT.intensity),
    warmth: clamp01(input.warmth, DAY_ATMOSPHERE_DEFAULT.warmth),
    motion,
    contrast,
    decor_variant: resolveDecorVariant(visual_mode, input.decor_variant),
    time_phase,
  };
}

/* ————————————————————————————————————————————————————————————————————— *
 * Manual pin — mirrors `productMoodTheme.ts`'s readMoodPin/writeMoodPin.
 * ————————————————————————————————————————————————————————————————————— */

/** Exported so DayAtmosphereBridge can listen for cross-tab pin changes. */
export const DAY_MODE_PIN_STORAGE_KEY = "todayflow_day_mode_pin_v1";

export function readDayModePin(): DayVisualMode | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(DAY_MODE_PIN_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { mode?: string };
    return isDayVisualMode(parsed?.mode) ? parsed.mode : null;
  } catch {
    return null;
  }
}

export function writeDayModePin(mode: DayVisualMode | null): void {
  if (typeof window === "undefined") return;
  if (mode == null) {
    localStorage.removeItem(DAY_MODE_PIN_STORAGE_KEY);
    return;
  }
  localStorage.setItem(DAY_MODE_PIN_STORAGE_KEY, JSON.stringify({ mode }));
}

/* ————————————————————————————————————————————————————————————————————— *
 * Contract → tokens. Light appearance only — dark variant + real CSS wiring
 * is FOUNDATION_UI §13, not this contract. Values here are the ones named
 * in FOUNDATION_UI §11.8 (`--day-*`); keys match the custom property names.
 * ————————————————————————————————————————————————————————————————————— */

export interface DayAtmosphereTokens {
  "--day-bg-base": string;
  "--day-bg-glow-primary": string;
  "--day-bg-glow-secondary": string;
  "--day-decor-color": string;
  "--day-decor-opacity": string;
  "--day-accent-soft": string;
  "--day-motion-duration": string;
  "--day-motion-distance": string;
  "--day-surface-tint": string;
}

/** Stable key list — for applying/cleaning up inline custom properties (DayAtmosphereBridge). */
export const DAY_ATMOSPHERE_TOKEN_KEYS: readonly (keyof DayAtmosphereTokens)[] = [
  "--day-bg-base",
  "--day-bg-glow-primary",
  "--day-bg-glow-secondary",
  "--day-decor-color",
  "--day-decor-opacity",
  "--day-accent-soft",
  "--day-motion-duration",
  "--day-motion-distance",
  "--day-surface-tint",
] as const;

type DayModeBaseTokens = Omit<
  DayAtmosphereTokens,
  "--day-decor-opacity" | "--day-motion-duration" | "--day-motion-distance"
>;

/** One base palette per mode (light appearance). §11.3 description → hex. */
const DAY_MODE_BASE_TOKENS: Record<DayVisualMode, DayModeBaseTokens> = {
  grounded: {
    "--day-bg-base": "#f3ede1",
    "--day-bg-glow-primary": "rgba(155, 138, 94, 0.22)",
    "--day-bg-glow-secondary": "rgba(107, 122, 90, 0.12)",
    "--day-decor-color": "#6b5a3f",
    "--day-accent-soft": "rgba(155, 138, 94, 0.28)",
    "--day-surface-tint": "rgba(243, 237, 225, 0.9)",
  },
  flow: {
    "--day-bg-base": "#eef1f5",
    "--day-bg-glow-primary": "rgba(140, 165, 196, 0.24)",
    "--day-bg-glow-secondary": "rgba(176, 158, 201, 0.14)",
    "--day-decor-color": "#5b7590",
    "--day-accent-soft": "rgba(140, 165, 196, 0.3)",
    "--day-surface-tint": "rgba(238, 241, 245, 0.9)",
  },
  radiance: {
    "--day-bg-base": "#fdf1e0",
    "--day-bg-glow-primary": "rgba(230, 175, 100, 0.32)",
    "--day-bg-glow-secondary": "rgba(240, 140, 110, 0.14)",
    "--day-decor-color": "#c9873a",
    "--day-accent-soft": "rgba(230, 175, 100, 0.32)",
    "--day-surface-tint": "rgba(253, 241, 224, 0.9)",
  },
  momentum: {
    "--day-bg-base": "#f6e2d8",
    "--day-bg-glow-primary": "rgba(196, 90, 60, 0.34)",
    "--day-bg-glow-secondary": "rgba(150, 60, 45, 0.18)",
    "--day-decor-color": "#a4432a",
    "--day-accent-soft": "rgba(196, 90, 60, 0.32)",
    "--day-surface-tint": "rgba(246, 226, 216, 0.9)",
  },
  clarity: {
    "--day-bg-base": "#f1f2f4",
    "--day-bg-glow-primary": "rgba(120, 130, 145, 0.12)",
    "--day-bg-glow-secondary": "rgba(120, 130, 145, 0.06)",
    "--day-decor-color": "#5b6472",
    "--day-accent-soft": "rgba(120, 130, 145, 0.2)",
    "--day-surface-tint": "rgba(241, 242, 244, 0.92)",
  },
  tension: {
    "--day-bg-base": "#221f22",
    "--day-bg-glow-primary": "rgba(120, 40, 50, 0.28)",
    "--day-bg-glow-secondary": "rgba(70, 60, 90, 0.16)",
    "--day-decor-color": "#8a5a63",
    "--day-accent-soft": "rgba(120, 40, 50, 0.22)",
    "--day-surface-tint": "rgba(34, 31, 34, 0.9)",
  },
  renewal: {
    "--day-bg-base": "#fdf6ee",
    "--day-bg-glow-primary": "rgba(240, 200, 190, 0.26)",
    "--day-bg-glow-secondary": "rgba(190, 215, 175, 0.18)",
    "--day-decor-color": "#a3b592",
    "--day-accent-soft": "rgba(240, 200, 190, 0.28)",
    "--day-surface-tint": "rgba(253, 246, 238, 0.92)",
  },
  depth: {
    "--day-bg-base": "#171622",
    "--day-bg-glow-primary": "rgba(70, 60, 110, 0.22)",
    "--day-bg-glow-secondary": "rgba(40, 45, 70, 0.16)",
    "--day-decor-color": "#524a72",
    "--day-accent-soft": "rgba(90, 80, 140, 0.2)",
    "--day-surface-tint": "rgba(23, 22, 34, 0.9)",
  },
};

/** Quiet modes move less and slower than active ones at the same intensity. */
const MOTION_PROFILE: Record<DayVisualMode, { baseDuration: number; baseDistance: number }> = {
  grounded: { baseDuration: 34, baseDistance: 3 },
  flow: { baseDuration: 30, baseDistance: 4 },
  radiance: { baseDuration: 24, baseDistance: 5 },
  momentum: { baseDuration: 18, baseDistance: 6 },
  clarity: { baseDuration: 28, baseDistance: 3 },
  tension: { baseDuration: 32, baseDistance: 2 },
  renewal: { baseDuration: 26, baseDistance: 4 },
  depth: { baseDuration: 38, baseDistance: 2 },
};

const CONTRAST_OPACITY_RANGE: Record<DayContrast, [number, number]> = {
  soft: [0.06, 0.12],
  medium: [0.1, 0.2],
  strong: [0.18, 0.3],
};

/** Deterministic contract → CSS custom properties. No randomness, no free color input. */
export function dayAtmosphereTokens(contract: DayAtmosphereContract): DayAtmosphereTokens {
  const base = DAY_MODE_BASE_TOKENS[contract.visual_mode];
  const [minOpacity, maxOpacity] = CONTRAST_OPACITY_RANGE[contract.contrast];
  const decorOpacity = minOpacity + (maxOpacity - minOpacity) * contract.intensity;

  if (contract.motion === "none") {
    return {
      ...base,
      "--day-decor-opacity": decorOpacity.toFixed(3),
      "--day-motion-duration": "0s",
      "--day-motion-distance": "0px",
    };
  }

  const profile = MOTION_PROFILE[contract.visual_mode];
  // Higher intensity → slightly faster, slightly larger travel, clamped to the
  // FOUNDATION_UI §11.4 bounds (15–40s cycle, a few px of travel).
  const duration = Math.min(40, Math.max(15, profile.baseDuration - contract.intensity * 8));
  const distance = profile.baseDistance + contract.intensity * 3;

  return {
    ...base,
    "--day-decor-opacity": decorOpacity.toFixed(3),
    "--day-motion-duration": `${duration.toFixed(1)}s`,
    "--day-motion-distance": `${distance.toFixed(1)}px`,
  };
}
