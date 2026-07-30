"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties } from "react";
import {
  clearPracticeSessionDraft,
  writePracticeSessionDraft,
  type PracticeStateAfter,
} from "@/lib/practicesPage/practiceSessionDraft";
import {
  readMusicLayerPrefs,
  resolveLayerGains,
  writeMusicLayerPrefs,
  type PracticeMusicLayerPrefs,
} from "@/lib/practicesPage/practiceMusicLayer";
import { PracticeMusicLayerPanel } from "@/components/practices/session/PracticeMusicLayerPanel";
import { practiceSessionCopy } from "@/components/practices/session/practiceSessionCopy";
import styles from "@/components/practices/session/practiceLiveSession.module.css";

export type PracticeLiveSessionProps = {
  locale: "ru" | "en";
  practiceId: string;
  title: string;
  instruction: string;
  durationMinutes: number;
  /** Resume from draft. */
  initialElapsedSeconds?: number;
  audioUrl?: string | null;
  musicUrl?: string | null;
  natureUrl?: string | null;
  imageUrl?: string | null;
  isAuthenticated: boolean;
  saving?: boolean;
  onClose: () => void;
  onSaveToToday: (input: {
    stateAfter: PracticeStateAfter;
    elapsedSeconds: number;
  }) => void | Promise<void>;
};

type Phase = "running" | "checkin" | "saved";

function formatClock(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const m = Math.floor(safe / 60);
  const s = safe % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function PracticeLiveSession({
  locale,
  practiceId,
  title,
  instruction,
  durationMinutes,
  initialElapsedSeconds = 0,
  audioUrl = null,
  musicUrl = null,
  natureUrl = null,
  imageUrl = null,
  isAuthenticated,
  saving = false,
  onClose,
  onSaveToToday,
}: PracticeLiveSessionProps) {
  const copy = practiceSessionCopy(locale);
  const totalSeconds = Math.max(60, Math.round(durationMinutes * 60));
  const [phase, setPhase] = useState<Phase>("running");
  const [elapsed, setElapsed] = useState(() =>
    Math.min(totalSeconds, Math.max(0, Math.floor(initialElapsedSeconds))),
  );
  const [paused, setPaused] = useState(false);
  const [musicOpen, setMusicOpen] = useState(false);
  const [prefs, setPrefs] = useState<PracticeMusicLayerPrefs>(() => readMusicLayerPrefs());
  const [stateAfter, setStateAfter] = useState<PracticeStateAfter | null>(null);
  const [softContinueUntil, setSoftContinueUntil] = useState<number | null>(null);
  const voiceRef = useRef<HTMLAudioElement | null>(null);
  const musicRef = useRef<HTMLAudioElement | null>(null);
  const natureRef = useRef<HTMLAudioElement | null>(null);
  const endedRef = useRef(false);

  const remaining = Math.max(0, totalSeconds - elapsed);
  const progressPct = Math.min(100, Math.round((elapsed / totalSeconds) * 100));
  const gains = useMemo(() => resolveLayerGains(prefs), [prefs]);

  const persistDraft = useCallback(
    (nextElapsed: number) => {
      writePracticeSessionDraft({
        practiceId,
        title,
        durationMinutes,
        elapsedSeconds: nextElapsed,
        updatedAt: new Date().toISOString(),
      });
    },
    [practiceId, title, durationMinutes],
  );

  const updatePrefs = useCallback((next: PracticeMusicLayerPrefs) => {
    setPrefs(next);
    writeMusicLayerPrefs(next);
  }, []);

  useEffect(() => {
    persistDraft(elapsed);
  }, [elapsed, persistDraft]);

  useEffect(() => {
    if (phase !== "running" || paused) return;
    const id = window.setInterval(() => {
      setElapsed((prev) => {
        const next = prev + 1;
        if (next >= totalSeconds) {
          endedRef.current = true;
          return totalSeconds;
        }
        return next;
      });
    }, 1000);
    return () => window.clearInterval(id);
  }, [phase, paused, totalSeconds]);

  useEffect(() => {
    if (phase === "running" && elapsed >= totalSeconds && !endedRef.current) {
      endedRef.current = true;
    }
    if (phase === "running" && elapsed >= totalSeconds) {
      if (prefs.continueAfter) {
        setSoftContinueUntil(Date.now() + prefs.continueMinutes * 60_000);
      }
      setPhase("checkin");
      setMusicOpen(false);
    }
  }, [elapsed, totalSeconds, phase, prefs.continueAfter, prefs.continueMinutes]);

  useEffect(() => {
    if (softContinueUntil == null) return;
    const id = window.setInterval(() => {
      if (Date.now() >= softContinueUntil) {
        setSoftContinueUntil(null);
      }
    }, 1000);
    return () => window.clearInterval(id);
  }, [softContinueUntil]);

  const softLayersActive =
    phase === "running" || (Boolean(prefs.continueAfter) && softContinueUntil != null);

  useEffect(() => {
    const voice = voiceRef.current;
    const music = musicRef.current;
    const nature = natureRef.current;

    if (voice) {
      voice.volume = gains.voice;
      voice.muted = gains.voice <= 0;
    }
    if (music) {
      music.volume = gains.music;
      music.muted = gains.music <= 0;
    }
    if (nature) {
      nature.volume = gains.nature;
      nature.muted = gains.nature <= 0;
    }

    const runningVoice = phase === "running" && !paused && gains.voice > 0 && Boolean(audioUrl);
    const runningSoft =
      softLayersActive && !paused && phase === "running"
        ? true
        : softLayersActive && phase !== "running";

    if (voice) {
      if (runningVoice) void voice.play().catch(() => undefined);
      else voice.pause();
    }
    if (music) {
      if (runningSoft && gains.music > 0 && musicUrl) void music.play().catch(() => undefined);
      else music.pause();
    }
    if (nature) {
      if (runningSoft && gains.nature > 0 && natureUrl) void nature.play().catch(() => undefined);
      else nature.pause();
    }
  }, [
    audioUrl,
    musicUrl,
    natureUrl,
    gains,
    paused,
    phase,
    softLayersActive,
  ]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const bgStyle = useMemo(
    () => (imageUrl ? ({ ["--pls-bg-image"]: `url(${imageUrl})` } as CSSProperties) : undefined),
    [imageUrl],
  );

  const finishToCheckin = () => {
    if (prefs.continueAfter) {
      setSoftContinueUntil(Date.now() + prefs.continueMinutes * 60_000);
    }
    setMusicOpen(false);
    setPhase("checkin");
  };

  const handleSave = async () => {
    if (!stateAfter || saving) return;
    try {
      await onSaveToToday({ stateAfter, elapsedSeconds: elapsed });
      clearPracticeSessionDraft(practiceId);
      setPhase("saved");
    } catch {
      /* parent surfaces toast */
    }
  };

  const handleClose = () => {
    if (phase === "saved") {
      clearPracticeSessionDraft(practiceId);
    }
    onClose();
  };

  return (
    <div
      className={styles.overlay}
      style={bgStyle}
      role="dialog"
      aria-modal="true"
      aria-label={title}
      data-testid="practice-live-session"
      data-phase={phase}
    >
      <div className={styles.bg} data-image={imageUrl ? "1" : "0"} aria-hidden />

      {audioUrl ? (
        <audio ref={voiceRef} className={styles.audioHidden} src={audioUrl} loop preload="none" />
      ) : null}
      {musicUrl ? (
        <audio ref={musicRef} className={styles.audioHidden} src={musicUrl} loop preload="none" />
      ) : null}
      {natureUrl ? (
        <audio ref={natureRef} className={styles.audioHidden} src={natureUrl} loop preload="none" />
      ) : null}

      <div className={styles.chrome}>
        <button type="button" className={styles.closeBtn} aria-label={copy.closeAria} onClick={handleClose}>
          ✕
        </button>
        {phase === "running" ? (
          <button
            type="button"
            className={styles.soundBtn}
            aria-pressed={musicOpen}
            aria-label={copy.soundPanelAria}
            onClick={() => setMusicOpen((v) => !v)}
            data-testid="practice-session-sound"
          >
            ♪
          </button>
        ) : (
          <span />
        )}
      </div>

      {phase === "running" && musicOpen ? (
        <div className={styles.musicDock}>
          <PracticeMusicLayerPanel
            locale={locale}
            prefs={prefs}
            onChange={updatePrefs}
            open={musicOpen}
          />
        </div>
      ) : null}

      {phase === "running" ? (
        <div className={styles.body}>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.instruction}>{instruction || copy.instructionFallback}</p>
          <p className={styles.timer} data-testid="practice-session-timer">
            {formatClock(remaining)}
          </p>
          <div className={styles.progressTrack} aria-hidden>
            <div className={styles.progressFill} style={{ width: `${progressPct}%` }} />
          </div>
          <button
            type="button"
            className={styles.pauseBtn}
            onClick={() => setPaused((v) => !v)}
            data-testid="practice-session-pause"
          >
            {paused ? copy.resume : copy.pause}
          </button>
          <button type="button" className={styles.finishBtn} onClick={finishToCheckin}>
            {copy.finishEarly}
          </button>
        </div>
      ) : null}

      {phase === "checkin" ? (
        <div className={styles.panel} data-testid="practice-session-checkin">
          <h2 className={styles.panelTitle}>{copy.checkinTitle}</h2>
          <div className={styles.checkinRow}>
            {(
              [
                ["better", copy.checkinBetter],
                ["same", copy.checkinSame],
                ["harder", copy.checkinHarder],
              ] as const
            ).map(([id, label]) => (
              <button
                key={id}
                type="button"
                className={`${styles.checkinChip} ${stateAfter === id ? styles.checkinChipActive : ""}`}
                aria-pressed={stateAfter === id}
                onClick={() => setStateAfter(id)}
              >
                {label}
              </button>
            ))}
          </div>
          {isAuthenticated ? (
            <button
              type="button"
              className={styles.primaryCta}
              disabled={!stateAfter || saving}
              onClick={() => void handleSave()}
              data-testid="practice-session-save"
            >
              {saving ? copy.saving : copy.saveToToday}
            </button>
          ) : (
            <>
              <p className={styles.panelBody}>{copy.loginToSave}</p>
              <Link href="/auth" className={styles.primaryCta}>
                {copy.loginCta}
              </Link>
            </>
          )}
          <button type="button" className={styles.secondaryCta} onClick={handleClose}>
            {copy.skipSave}
          </button>
        </div>
      ) : null}

      {phase === "saved" ? (
        <div className={styles.panel} data-testid="practice-session-saved">
          <h2 className={styles.panelTitle}>{copy.savedTitle}</h2>
          <p className={styles.panelBody}>{copy.savedBody}</p>
          <Link href="/today" className={styles.primaryCta}>
            {copy.openToday}
          </Link>
          <Link href="/practices" className={styles.secondaryCta}>
            {copy.backToPractices}
          </Link>
        </div>
      ) : null}
    </div>
  );
}
