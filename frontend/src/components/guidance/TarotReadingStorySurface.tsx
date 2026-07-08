"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import type { TarotFollowUpChip, TarotReadingStoryModel } from "@/lib/buildTarotReadingStoryModel";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { tarotReadingStoryChromeBundle } from "@/components/guidance/tarotReadingStoryChrome";
import { postJson } from "@/lib/api";
import { tarotCardBackSrc, tarotCardDisplayHeightPx, tarotCardFaceSrc } from "@/lib/tarotCardAssets";
import styles from "@/components/guidance/TarotReadingStorySurface.module.css";

type TarotReadingStorySurfaceProps = {
  model: TarotReadingStoryModel;
  locale: FlowPracticesChromeLocale;
  generationLogId?: number | null;
  spreadId?: string | null;
  onFollowUpTracked?: (chip: TarotFollowUpChip) => void;
};

export function TarotReadingStorySurface({
  model,
  locale,
  generationLogId,
  spreadId,
  onFollowUpTracked,
}: TarotReadingStorySurfaceProps) {
  const chrome = useMemo(() => tarotReadingStoryChromeBundle(locale), [locale]);
  const [selectedChipId, setSelectedChipId] = useState<string | null>(null);
  const [followUpSaved, setFollowUpSaved] = useState(false);

  const insights = [
    { key: "holding" as const, title: chrome.insightHoldingTitle, text: model.insights.holding },
    { key: "shifting" as const, title: chrome.insightShiftingTitle, text: model.insights.shifting },
    { key: "attention" as const, title: chrome.insightAttentionTitle, text: model.insights.attention },
  ].filter((item) => item.text?.trim());

  const handleFollowUp = async (chip: TarotFollowUpChip) => {
    if (followUpSaved) return;
    setSelectedChipId(chip.id);
    onFollowUpTracked?.(chip);
    if (generationLogId) {
      try {
        await postJson("/learning/feedback", {
          generation_log_id: generationLogId,
          signal: "tarot_reading_follow_up",
          metadata: {
            source_surface: "tarot_question_flow",
            chip_id: chip.id,
            chip_label: chip.label,
            spread_id: spreadId,
            question: model.question,
          },
        });
      } catch {
        /* meaning event still tracked by parent */
      }
    }
    setFollowUpSaved(true);
  };

  return (
    <div className={styles.root}>
      <section className={styles.blockHero} aria-labelledby="tarot-story-question">
        {model.isClarification ? <span className={styles.clarificationBadge}>{chrome.clarificationBadge}</span> : null}
        <p id="tarot-story-question" className={styles.eyebrow}>
          {chrome.questionEyebrow}
        </p>
        <p className={styles.questionText}>«{model.question}»</p>
      </section>

      {model.mainAnswer ? (
        <section className={styles.blockMainAnswer} aria-labelledby="tarot-story-answer">
          {chrome.mainAnswerEyebrow ? (
            <p id="tarot-story-answer" className={styles.eyebrow}>
              {chrome.mainAnswerEyebrow}
            </p>
          ) : (
            <p id="tarot-story-answer" className={styles.srOnly}>
              Главный ответ
            </p>
          )}
          <p className={styles.mainAnswer}>{model.mainAnswer}</p>
        </section>
      ) : null}

      {model.storyNarrative ? (
        <section className={styles.block} aria-labelledby="tarot-story-why">
          {chrome.storyEyebrow ? (
            <p id="tarot-story-why" className={styles.eyebrow}>
              {chrome.storyEyebrow}
            </p>
          ) : null}
          <p className={styles.bodyText}>{model.storyNarrative}</p>
        </section>
      ) : null}

      {model.cardInsights.length ? (
        <section className={styles.blockCards} aria-labelledby="tarot-story-cards">
          <p id="tarot-story-cards" className={styles.eyebrow}>
            {chrome.cardsEyebrow}
          </p>
          <div className={styles.cardInsightList}>
            {model.cardInsights.map((card) => {
              const thumbW = 56;
              const thumbH = tarotCardDisplayHeightPx(thumbW);
              const faceSrc = Number.isFinite(card.cardId) ? tarotCardFaceSrc(card.cardId) : null;
              const imgSrc = faceSrc ?? tarotCardBackSrc();
              const isReversed = card.orientation === "reversed";
              return (
                <article key={`${card.cardId}-${card.positionLabel}`} className={styles.cardInsightRow}>
                  <div
                    className={`${styles.cardInsightThumb} ${isReversed && faceSrc ? styles.cardInsightThumbReversed : ""}`}
                    style={{ width: `${thumbW}px`, height: `${thumbH}px` }}
                  >
                    <Image src={imgSrc} alt="" fill sizes={`${thumbW}px`} draggable={false} style={{ objectFit: "contain" }} />
                  </div>
                  <div className={styles.cardInsightBody}>
                    <p className={styles.cardInsightMeta}>
                      {card.positionLabel} · {card.cardNameRu}
                    </p>
                    <p className={styles.cardInsightLine}>{card.line}</p>
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      ) : null}

      {insights.length ? (
        <section className={styles.blockInsights} aria-labelledby="tarot-story-insights">
          <p id="tarot-story-insights" className={styles.srOnly}>
            Что это помогает увидеть
          </p>
          <div className={styles.insightGrid}>
            {insights.map((item) => (
              <article key={item.key} className={styles.insightCard}>
                <h3 className={styles.insightTitle}>{item.title}</h3>
                <p className={styles.insightText}>{item.text}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {model.todaySuggestion ? (
        <section className={styles.blockToday} aria-labelledby="tarot-story-today">
          <p id="tarot-story-today" className={styles.eyebrow}>
            {chrome.todayEyebrow}
          </p>
          <p className={styles.todayText}>{model.todaySuggestion}</p>
        </section>
      ) : null}

      {model.followUpChips.length ? (
        <section className={styles.blockFollowUp} aria-labelledby="tarot-story-follow-up">
          <p id="tarot-story-follow-up" className={styles.followUpPrompt}>
            {model.followUpPrompt}
          </p>
          <div className={styles.chipRow}>
            {model.followUpChips.map((chip) => (
              <button
                key={chip.id}
                type="button"
                className={
                  selectedChipId === chip.id
                    ? `${styles.chip} ${styles.chipSelected}`
                    : styles.chip
                }
                disabled={followUpSaved && selectedChipId !== chip.id}
                onClick={() => void handleFollowUp(chip)}
              >
                {chip.label}
              </button>
            ))}
          </div>
          {followUpSaved ? <p className={styles.followUpThanks}>{chrome.followUpThanks}</p> : null}
        </section>
      ) : null}

      {model.actions.length ? (
        <section className={styles.blockNext} aria-labelledby="tarot-story-next">
          <p id="tarot-story-next" className={styles.eyebrow}>
            {chrome.nextEyebrow}
          </p>
          <div className={styles.actionList}>
            {model.actions.map((action) => (
              <div key={action.id} className={styles.actionItem}>
                {action.href && !action.disabled ? (
                  <Link href={action.href} className={`orbit-button orbit-button-secondary orbit-button-sm ${styles.actionButton}`}>
                    {action.label}
                  </Link>
                ) : (
                  <button
                    type="button"
                    className={`orbit-button orbit-button-secondary orbit-button-sm ${styles.actionButton}`}
                    disabled={action.disabled}
                    onClick={action.onClick}
                  >
                    {action.label}
                  </button>
                )}
                {action.description ? <p className={styles.actionDescription}>{action.description}</p> : null}
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
