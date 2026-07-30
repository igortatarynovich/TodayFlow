"use client";

import type { PracticeMusicLayerPrefs, PracticeSoundMode } from "@/lib/practicesPage/practiceMusicLayer";
import { practiceSessionCopy } from "@/components/practices/session/practiceSessionCopy";
import styles from "@/components/practices/session/practiceLiveSession.module.css";

export type PracticeMusicLayerPanelProps = {
  locale: "ru" | "en";
  prefs: PracticeMusicLayerPrefs;
  onChange: (next: PracticeMusicLayerPrefs) => void;
  open: boolean;
};

const MODES: PracticeSoundMode[] = ["with_voice", "music_only", "silent"];

export function PracticeMusicLayerPanel({
  locale,
  prefs,
  onChange,
  open,
}: PracticeMusicLayerPanelProps) {
  const copy = practiceSessionCopy(locale);
  if (!open) return null;

  const modeLabel = (mode: PracticeSoundMode) => {
    if (mode === "with_voice") return copy.modeWithVoice;
    if (mode === "music_only") return copy.modeMusicOnly;
    return copy.modeSilent;
  };

  const setVolume = (key: "voiceVolume" | "musicVolume" | "natureVolume", value: number) => {
    onChange({ ...prefs, [key]: value / 100 });
  };

  return (
    <div className={styles.musicPanel} data-testid="practice-music-layer">
      <p className={styles.musicPanelTitle}>{copy.musicLayerTitle}</p>
      <div className={styles.modeRow} role="group" aria-label={copy.musicLayerTitle}>
        {MODES.map((mode) => (
          <button
            key={mode}
            type="button"
            className={`${styles.modeChip} ${prefs.mode === mode ? styles.modeChipActive : ""}`}
            aria-pressed={prefs.mode === mode}
            onClick={() => onChange({ ...prefs, mode })}
          >
            {modeLabel(mode)}
          </button>
        ))}
      </div>

      <label className={styles.sliderRow}>
        <span>{copy.voiceVolume}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.voiceVolume * 100)}
          disabled={prefs.mode !== "with_voice"}
          onChange={(e) => setVolume("voiceVolume", Number(e.target.value))}
          data-testid="music-layer-voice"
        />
      </label>
      <label className={styles.sliderRow}>
        <span>{copy.musicVolume}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.musicVolume * 100)}
          disabled={prefs.mode === "silent"}
          onChange={(e) => setVolume("musicVolume", Number(e.target.value))}
          data-testid="music-layer-music"
        />
      </label>
      <label className={styles.sliderRow}>
        <span>{copy.natureVolume}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.natureVolume * 100)}
          disabled={prefs.mode === "silent"}
          onChange={(e) => setVolume("natureVolume", Number(e.target.value))}
          data-testid="music-layer-nature"
        />
      </label>

      <label className={styles.continueRow}>
        <input
          type="checkbox"
          checked={prefs.continueAfter}
          onChange={(e) => onChange({ ...prefs, continueAfter: e.target.checked })}
          data-testid="music-layer-continue"
        />
        <span>{copy.continueAfter}</span>
      </label>
      {prefs.continueAfter ? (
        <label className={styles.sliderRow}>
          <span>{copy.continueMinutes}</span>
          <input
            type="range"
            min={1}
            max={30}
            value={prefs.continueMinutes}
            onChange={(e) => onChange({ ...prefs, continueMinutes: Number(e.target.value) })}
            data-testid="music-layer-continue-minutes"
          />
          <span className={styles.continueValue}>{prefs.continueMinutes}</span>
        </label>
      ) : null}

      <p className={styles.layerHint}>{copy.layerHint}</p>
    </div>
  );
}
