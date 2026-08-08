"use client";

import { useCallback, useEffect, useState } from "react";
import { getJson, postJson } from "@/lib/api";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import {
  PROFILE_DECODE_PATTERN_WAVE_EVENT,
  consumeProfileMotionOnce,
} from "@/lib/profile/profileMotionOnce";
import { DsButton } from "@/design-system";
import { joinClass } from "@/design-system/utils/joinClass";
import styles from "@/components/profile/v2/profileV2System.module.css";

export type NatalDecodeOffer = {
  layer?: string;
  version?: string;
  access?: "offer" | "blocked" | "ready" | string;
  reason?: string | null;
  cta?: string | null;
  can_generate?: boolean;
  identity_thesis?: string;
  note?: string;
  status?: string;
  pattern_thesis?: string | null;
  sections?: NatalDecodeSection[];
  day_hooks?: string[];
  limits?: string | null;
};

export type NatalDecodeSection = {
  id?: string;
  title?: string;
  thesis?: string;
  because_core?: string;
};

export type NatalDecodeResult = {
  layer?: string;
  version?: string;
  status?: string;
  reason?: string;
  cta?: string;
  pattern_thesis?: string | null;
  sections?: NatalDecodeSection[];
  day_hooks?: string[];
  limits?: string | null;
  identity_core?: { thesis_key?: string; surface_text?: string };
  sot_role?: string;
  writes_character_engine?: boolean;
  access?: string;
  can_generate?: boolean;
};

function isGroundedResult(res: NatalDecodeResult | NatalDecodeOffer | null | undefined): boolean {
  return Boolean(
    res &&
      res.status === "grounded" &&
      Array.isArray(res.sections) &&
      res.sections.length > 0,
  );
}

/**
 * Natal Decode Depth — one-shot story.
 * First explicit POST generates; thereafter GET serves ready artifact (no re-generate CTA).
 */
export function ProfileNatalDecodePanel() {
  const [offer, setOffer] = useState<NatalDecodeOffer | null>(null);
  const [result, setResult] = useState<NatalDecodeResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patternWave, setPatternWave] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getJson<NatalDecodeOffer>("/account/profile/natal-decode")
      .then((res) => {
        if (cancelled || !res) return;
        setOffer(res);
        if (isGroundedResult(res)) {
          setResult(res as NatalDecodeResult);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setOffer({
            access: "blocked",
            can_generate: false,
            cta: "Расшифровка карты станет доступна после устойчивого портрета.",
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const grounded = isGroundedResult(result);

  useEffect(() => {
    if (!grounded) return;
    if (!consumeProfileMotionOnce("decode-pattern-wave")) return;
    setPatternWave(true);
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(PROFILE_DECODE_PATTERN_WAVE_EVENT));
    }
    const t = window.setTimeout(() => setPatternWave(false), 1300);
    return () => window.clearTimeout(t);
  }, [grounded]);

  const generate = useCallback(async () => {
    if (!offer?.can_generate || busy || grounded) return;
    setBusy(true);
    setError(null);
    try {
      const res = await postJson<NatalDecodeResult>("/account/profile/natal-decode", {
        force_refresh: false,
      });
      setResult(res);
      if (isGroundedResult(res)) {
        setOffer((prev) => ({
          ...(prev || {}),
          access: "ready",
          can_generate: false,
          note: "Карта уже расшифрована — это готовая история, не кнопка «ещё раз».",
        }));
      } else if (res.status === "blocked" || res.status === "unavailable") {
        setError(res.cta || res.reason || "Сейчас расшифровку открыть не удалось.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось открыть расшифровку.");
    } finally {
      setBusy(false);
    }
  }, [busy, offer?.can_generate, grounded]);

  const showBreathe = Boolean(offer?.can_generate && !grounded && !busy);
  const leadDefault = grounded
    ? "Целостная история карты — планеты, углы и числа вокруг твоего ядра характера."
    : "Один раз собираем целостную историю карты вокруг твоего ядра — не второй портрет и не кнопка «ещё раз».";
  const lead =
    !grounded && offer?.can_generate && offer.cta ? offer.cta : leadDefault;

  return (
    <div className={styles.deepThemesBlock} data-testid="profile-natal-decode">
      <p className={styles.deepThemesTitle}>Расшифровка натальной карты</p>
      <p className={styles.deepThemesLead}>{lead}</p>
      {offer?.note ? <p className={styles.deepThemesHint}>{offer.note}</p> : null}

      {!grounded ? (
        <div className={styles.deepThemesActions}>
          {offer?.can_generate ? (
            <DsButton
              variant="primary"
              className={joinClass(
                styles.natalDecodeAction,
                showBreathe ? profileMotionStyles.attentionBreathe : null,
              )}
              onClick={() => void generate()}
              disabled={busy}
              data-testid="profile-natal-decode-generate"
              data-motion={showBreathe ? "attention-breathe" : undefined}
            >
              {busy ? "Собираем расшифровку…" : "Открыть расшифровку"}
            </DsButton>
          ) : (
            <p className={styles.deepThemesHint} data-testid="profile-natal-decode-blocked">
              {offer?.cta || "Пока недоступно."}
            </p>
          )}
        </div>
      ) : null}

      {error ? (
        <p className={styles.deepThemesError} role="alert">
          {error}
        </p>
      ) : null}

      {grounded ? (
        <div className={styles.natalDecodeBody} data-testid="profile-natal-decode-result">
          {result?.pattern_thesis ? (
            <p
              className={[
                styles.natalDecodePattern,
                patternWave ? profileMotionStyles.patternSweep : "",
              ]
                .filter(Boolean)
                .join(" ")}
              data-testid="profile-natal-decode-pattern"
              data-motion={patternWave ? "pattern-sweep" : undefined}
            >
              {result.pattern_thesis}
            </p>
          ) : null}
          {(result?.sections || []).map((section, idx) => (
            <article
              key={`${section.id || "sec"}-${idx}`}
              className={styles.natalDecodeSection}
            >
              {section.title ? <h3 className={styles.natalDecodeSectionTitle}>{section.title}</h3> : null}
              {section.thesis ? <p className={styles.natalDecodeThesis}>{section.thesis}</p> : null}
              {section.because_core ? (
                <p className={styles.natalDecodeBecause}>
                  <span className={styles.natalDecodeBecauseLabel}>Связь с ядром. </span>
                  {section.because_core}
                </p>
              ) : null}
            </article>
          ))}
          {result?.day_hooks && result.day_hooks.length > 0 ? (
            <div className={styles.natalDecodeHooks}>
              <p className={styles.natalDecodeHooksTitle}>Для дня</p>
              <ul>
                {result.day_hooks.map((hook, i) => (
                  <li key={`hook-${i}`}>{hook}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {result?.limits ? <p className={styles.natalDecodeLimits}>{result.limits}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
