"use client";

import { useEffect, useState } from "react";
import type { PracticeMusicLayerPrefs, PracticeSoundMode } from "@/lib/practicesPage/practiceMusicLayer";
import {
  DEFAULT_MUSIC_LAYER_PREFS,
  readMusicLayerPrefs,
  writeMusicLayerPrefs,
} from "@/lib/practicesPage/practiceMusicLayer";
import styles from "@/components/practices/stateCycle/practicesStateCycle.module.css";

export type HubMusicLayerProps = {
  locale: "ru" | "en";
};

const MODES: PracticeSoundMode[] = ["with_voice", "music_only", "silent"];

function copyFor(locale: "ru" | "en") {
  if (locale === "en") {
    return {
      title: "Musical accompaniment",
      withVoice: "With voice",
      musicOnly: "Music only",
      silent: "Silent",
      voice: "Voice",
      music: "Music",
      nature: "Nature sounds",
    };
  }
  return {
    title: "Музыкальное сопровождение",
    withVoice: "С голосом",
    musicOnly: "Только музыка",
    silent: "Без звука",
    voice: "Голос",
    music: "Музыка",
    nature: "Звуки природы",
  };
}

export function HubMusicLayer({ locale }: HubMusicLayerProps) {
  const copy = copyFor(locale);
  const [prefs, setPrefs] = useState<PracticeMusicLayerPrefs>(DEFAULT_MUSIC_LAYER_PREFS);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setPrefs(readMusicLayerPrefs());
    setReady(true);
  }, []);

  const update = (next: PracticeMusicLayerPrefs) => {
    setPrefs(next);
    writeMusicLayerPrefs(next);
  };

  const modeLabel = (mode: PracticeSoundMode) => {
    if (mode === "with_voice") return copy.withVoice;
    if (mode === "music_only") return copy.musicOnly;
    return copy.silent;
  };

  if (!ready) return null;

  return (
    <section className={styles.musicHub} aria-labelledby="psc-music-title" data-testid="practices-music-hub">
      <h2 id="psc-music-title" className={styles.sectionTitle}>
        {copy.title}
      </h2>
      <div className={styles.musicModeRow} role="group" aria-label={copy.title}>
        {MODES.map((mode) => (
          <button
            key={mode}
            type="button"
            className={`${styles.musicMode} ${prefs.mode === mode ? styles.musicModeActive : ""}`}
            aria-pressed={prefs.mode === mode}
            onClick={() => update({ ...prefs, mode })}
          >
            {modeLabel(mode)}
          </button>
        ))}
      </div>
      <label className={styles.musicSlider}>
        <span>{copy.voice}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.voiceVolume * 100)}
          disabled={prefs.mode !== "with_voice"}
          onChange={(e) => update({ ...prefs, voiceVolume: Number(e.target.value) / 100 })}
        />
        <span className={styles.musicPct}>{Math.round(prefs.voiceVolume * 100)}%</span>
      </label>
      <label className={styles.musicSlider}>
        <span>{copy.music}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.musicVolume * 100)}
          disabled={prefs.mode === "silent"}
          onChange={(e) => update({ ...prefs, musicVolume: Number(e.target.value) / 100 })}
        />
        <span className={styles.musicPct}>{Math.round(prefs.musicVolume * 100)}%</span>
      </label>
      <label className={styles.musicSlider}>
        <span>{copy.nature}</span>
        <input
          type="range"
          min={0}
          max={100}
          value={Math.round(prefs.natureVolume * 100)}
          disabled={prefs.mode === "silent"}
          onChange={(e) => update({ ...prefs, natureVolume: Number(e.target.value) / 100 })}
        />
        <span className={styles.musicPct}>{Math.round(prefs.natureVolume * 100)}%</span>
      </label>
    </section>
  );
}
