"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton, DsEyebrow } from "@/design-system";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { TarotCardImage } from "@/components/product-ui/TarotCardImage";
import { tarotReadingStoryChromeBundle } from "@/components/guidance/tarotReadingStoryChrome";
import type { TarotReadingStoryModel } from "@/lib/buildTarotReadingStoryModel";
import { t } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

export type TarotWebResultProps = {
  model: TarotReadingStoryModel;
  locale?: FlowPracticesChromeLocale;
  spreadTitle?: string;
  cardsAriaLabel?: string;
  storyEyebrow?: string;
  extraActions?: ReactNode;
};

export function TarotWebResult({
  model,
  locale = "ru",
  spreadTitle,
  cardsAriaLabel,
  storyEyebrow,
  extraActions,
}: TarotWebResultProps) {
  const chrome = useMemo(() => tarotReadingStoryChromeBundle(locale), [locale]);
  const loc = locale === "ru" ? "ru" : "en";
  const cardsLabel =
    cardsAriaLabel ??
    t("tarot.story.cardsSpreadAria", loc === "ru" ? "Карты расклада" : "Spread cards", undefined, loc);
  const whyEyebrow =
    storyEyebrow ??
    t("tarot.story.whyNowEyebrow", loc === "ru" ? "Почему это важно сейчас" : "Why this matters now", undefined, loc);

  const [verdictLead, verdictSub] = model.mainAnswer.split(/(?<=\.)\s+/).concat([""]).slice(0, 2);

  const insightRows = [
    { label: chrome.insightHoldingTitle, text: model.insights.holding },
    { label: chrome.insightShiftingTitle, text: model.insights.shifting },
    { label: chrome.insightAttentionTitle, text: model.insights.attention },
  ].filter((row) => row.text?.trim());

  return (
    <div className={s.tarotWebLayout} data-testid="tarot-web-result">
      <aside className={s.tarotWebCards} aria-label={cardsLabel}>
        {spreadTitle ? <span className={s.tarotWebTopicChip}>{spreadTitle}</span> : null}
        {model.cardInsights.map((card, index) => (
          <div key={`${card.cardId}-${card.positionLabel}`} className={s.tarotWebCardSlot}>
            <TarotCardImage
              cardId={card.cardId}
              cardName={card.cardNameRu}
              width={160}
              reversed={card.orientation === "reversed"}
            />
            <p className={s.tarotWebCardLabel}>
              {index + 1} {card.positionLabel}
            </p>
          </div>
        ))}
      </aside>

      <article className={s.tarotWebStory}>
        {model.question ? <p className={s.tarotWebQuestion}>«{model.question}»</p> : null}

        <div>
          <p className={s.tarotWebVerdict}>{verdictLead || model.mainAnswer}</p>
          {verdictSub ? <p className={s.tarotWebVerdictSub}>{verdictSub}</p> : null}
        </div>

        {model.storyNarrative ? (
          <section>
            <DsEyebrow>{whyEyebrow}</DsEyebrow>
            <div style={{ marginTop: "0.75rem" }}>
              <DsBody>{model.storyNarrative}</DsBody>
            </div>
          </section>
        ) : null}

        {insightRows.length ? (
          <div className={s.tarotWebInsightGrid}>
            {insightRows.map((row) => (
              <div key={row.label} className={s.tarotWebInsightRow}>
                <p className={s.tarotWebInsightLabel}>{row.label}</p>
                <DsBody size="sm">{row.text}</DsBody>
              </div>
            ))}
          </div>
        ) : null}

        {model.todaySuggestion ? (
          <section className={s.tarotWebActionBox}>
            <DsEyebrow>{chrome.todayEyebrow}</DsEyebrow>
            <div style={{ marginTop: "0.75rem" }}>
              <DsBody>{model.todaySuggestion}</DsBody>
            </div>
          </section>
        ) : null}

        {model.actions.length ? (
          <div className={s.tarotWebChipRow}>
            {model.actions.map((action) =>
              action.href ? (
                <Link key={action.id} href={action.href} className={s.tarotWebChip}>
                  {action.label}
                </Link>
              ) : (
                <button
                  key={action.id}
                  type="button"
                  className={s.tarotWebChip}
                  onClick={action.onClick}
                  disabled={action.disabled}
                >
                  {action.label}
                </button>
              ),
            )}
          </div>
        ) : null}

        {extraActions}
      </article>
    </div>
  );
}
