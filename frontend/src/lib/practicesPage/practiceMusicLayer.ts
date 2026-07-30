/**
 * Practices music layer prefs (canon §5) — client SoT until server prefs exist.
 */

export const PRACTICE_MUSIC_LAYER_KEY = "todayflow_practice_music_layer_v1";

export type PracticeSoundMode = "with_voice" | "music_only" | "silent";

export type PracticeMusicLayerPrefs = {
  mode: PracticeSoundMode;
  voiceVolume: number;
  musicVolume: number;
  natureVolume: number;
  /** Keep soft layers playing after session instruction ends. */
  continueAfter: boolean;
  continueMinutes: number;
};

export const DEFAULT_MUSIC_LAYER_PREFS: PracticeMusicLayerPrefs = {
  mode: "with_voice",
  voiceVolume: 0.7,
  musicVolume: 0.5,
  natureVolume: 0.8,
  continueAfter: false,
  continueMinutes: 10,
};

function clamp01(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(1, Math.max(0, value));
}

export function normalizeMusicLayerPrefs(
  raw: Partial<PracticeMusicLayerPrefs> | null | undefined,
): PracticeMusicLayerPrefs {
  const mode =
    raw?.mode === "music_only" || raw?.mode === "silent" || raw?.mode === "with_voice"
      ? raw.mode
      : DEFAULT_MUSIC_LAYER_PREFS.mode;
  return {
    mode,
    voiceVolume: clamp01(raw?.voiceVolume ?? DEFAULT_MUSIC_LAYER_PREFS.voiceVolume),
    musicVolume: clamp01(raw?.musicVolume ?? DEFAULT_MUSIC_LAYER_PREFS.musicVolume),
    natureVolume: clamp01(raw?.natureVolume ?? DEFAULT_MUSIC_LAYER_PREFS.natureVolume),
    continueAfter: Boolean(raw?.continueAfter ?? DEFAULT_MUSIC_LAYER_PREFS.continueAfter),
    continueMinutes: Math.min(
      60,
      Math.max(1, Math.round(raw?.continueMinutes ?? DEFAULT_MUSIC_LAYER_PREFS.continueMinutes)),
    ),
  };
}

export function readMusicLayerPrefs(): PracticeMusicLayerPrefs {
  if (typeof window === "undefined") return { ...DEFAULT_MUSIC_LAYER_PREFS };
  try {
    const raw = localStorage.getItem(PRACTICE_MUSIC_LAYER_KEY);
    if (!raw) return { ...DEFAULT_MUSIC_LAYER_PREFS };
    return normalizeMusicLayerPrefs(JSON.parse(raw) as Partial<PracticeMusicLayerPrefs>);
  } catch {
    return { ...DEFAULT_MUSIC_LAYER_PREFS };
  }
}

export function writeMusicLayerPrefs(prefs: PracticeMusicLayerPrefs): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(PRACTICE_MUSIC_LAYER_KEY, JSON.stringify(normalizeMusicLayerPrefs(prefs)));
}

/** Effective gains per layer for the active accompaniment mode. */
export function resolveLayerGains(prefs: PracticeMusicLayerPrefs): {
  voice: number;
  music: number;
  nature: number;
} {
  const p = normalizeMusicLayerPrefs(prefs);
  if (p.mode === "silent") return { voice: 0, music: 0, nature: 0 };
  if (p.mode === "music_only") return { voice: 0, music: p.musicVolume, nature: p.natureVolume };
  return { voice: p.voiceVolume, music: p.musicVolume, nature: p.natureVolume };
}
