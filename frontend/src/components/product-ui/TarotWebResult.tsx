"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton } from "@/design-system";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { TarotCardImage } from "@/components/product-ui/TarotCardImage";
import { tarotReadingStoryChromeBundle } from "@/components/guidance/tarotReadingStoryChrome";
import {
  ProductJourneyScene,
  ProductNarrativeBlock,
} from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
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

function ensurePeriod(text: string): string {
  const t0 = text.replace(/\s+/g, " ").trim();
  if (!t0) return "";
  return /[.!?…]$/.test(t0) ? t0 : `${t0}.`;
}

function splitParagraphs(text: string): string[] {
  const parts = text
    .split(/(?<=[.!?…])\s+/)
    .map((p) => ensurePeriod(p))
    .filter(Boolean);
  if (parts.length <= 1) return parts.length ? parts : [];
  if (parts.length === 2) return parts;
  return [parts.slice(0, 2).join(" "), ...parts.slice(2)].filter(Boolean);
}

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

  const answerParas = useMemo(
    () => (model.mainAnswer?.trim() ? splitParagraphs(model.mainAnswer) : []),
    [model.mainAnswer],
  );

  const whyParas = useMemo(() => {
    const paras: string[] = [];
    if (model.storyNarrative?.trim()) paras.push(ensurePeriod(model.storyNarrative));
    if (model.insights.holding?.trim()) {
      paras.push(ensurePeriod(`${chrome.insightHoldingTitle}: ${model.insights.holding}`));
    }
    if (model.insights.shifting?.trim()) {
      paras.push(ensurePeriod(`${chrome.insightShiftingTitle}: ${model.insights.shifting}`));
    }
    if (model.insights.attention?.trim()) {
      paras.push(ensurePeriod(`${chrome.insightAttentionTitle}: ${model.insights.attention}`));
    }
    return paras;
  }, [model.storyNarrative, model.insights, chrome]);

  const cardParas = useMemo(
    () =>
      model.cardInsights
        .map((card) => {
          const line = (card.line || "").trim();
          if (!line) return ensurePeriod(`${card.positionLabel} — ${card.cardNameRu}`);
          return ensurePeriod(`${card.positionLabel} · ${card.cardNameRu}: ${line}`);
        })
        .filter(Boolean),
    [model.cardInsights],
  );

  const hasStory =
    answerParas.length > 0 || whyParas.length > 0 || cardParas.length > 0 || Boolean(model.todaySuggestion?.trim());

  return (
    <div className={s.tarotWebLayout} data-testid="tarot-web-result">
      <ProductJourneyScene
        step={1}
        title="Вопрос"
        lead={spreadTitle || null}
        motif="today"
        testId="tarot-journey-question"
      >
        {model.isClarification ? (
          <p className={journeyStyles.pairScoreQuiet}>{chrome.clarificationBadge}</p>
        ) : null}
        {model.question ? <p className={journeyStyles.pairTitle}>«{model.question}»</p> : null}
        {model.cardInsights.length ? (
          <div className={journeyStyles.cardStrip} aria-label={cardsLabel}>
            {model.cardInsights.map((card, index) => (
              <div key={`${card.cardId}-${card.positionLabel}`} className={journeyStyles.cardStripItem}>
                <TarotCardImage
                  cardId={card.cardId}
                  cardName={card.cardNameRu}
                  width={120}
                  reversed={card.orientation === "reversed"}
                />
                <p className={journeyStyles.cardStripLabel}>
                  {index + 1}. {card.positionLabel}
                </p>
              </div>
            ))}
          </div>
        ) : null}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={2}
        title="История расклада"
        lead="Ответ, почему карты так легли на вопрос, и слой позиций."
        motif="why"
        testId="tarot-journey-story"
      >
        {hasStory ? (
          <div className={s.tarotResultNarrativeStack}>
            {answerParas.length ? (
              <ProductNarrativeBlock
                id="answer"
                kicker={chrome.mainAnswerEyebrow || "Ответ расклада"}
                lead={answerParas[0]}
                paragraphs={answerParas.slice(1)}
                accent="support"
                collapseAfter={answerParas.length > 3 ? 1 : undefined}
                testId="tarot-narrative-answer"
              />
            ) : null}

            {whyParas.length ? (
              <ProductNarrativeBlock
                id="why"
                kicker={whyEyebrow}
                lead={whyParas[0]}
                paragraphs={whyParas.slice(1)}
                accent="sky"
                collapseAfter={whyParas.length > 2 ? 1 : undefined}
                testId="tarot-narrative-why"
              />
            ) : null}

            {cardParas.length ? (
              <ProductNarrativeBlock
                id="cards"
                kicker={chrome.cardsEyebrow || "Слой карт"}
                paragraphs={cardParas}
                accent="default"
                collapseAfter={cardParas.length > 2 ? 2 : undefined}
                testId="tarot-narrative-cards"
              />
            ) : null}

            {model.todaySuggestion?.trim() ? (
              <ProductNarrativeBlock
                id="today"
                kicker={chrome.todayEyebrow || "На сегодня"}
                paragraphs={[ensurePeriod(model.todaySuggestion)]}
                accent="support"
                testId="tarot-narrative-today"
              />
            ) : null}
          </div>
        ) : (
          <DsBody muted>Пока нет полного рассказа — вернись к вопросу или открой карты ещё раз.</DsBody>
        )}
      </ProductJourneyScene>

      <ProductJourneyScene
        step={3}
        title="Мост"
        lead="Куда можно продолжить из этого расклада."
        motif="bridge"
        bridge
        testId="tarot-journey-bridge"
      >
        {model.actions.length || extraActions ? (
          <div className={journeyStyles.actionRow}>
            {model.actions.map((action) =>
              action.href ? (
                <Link key={action.id} href={action.href} className={journeyStyles.bridgeLink}>
                  → {action.label}
                </Link>
              ) : (
                <DsButton
                  key={action.id}
                  type="button"
                  variant="secondary"
                  onClick={action.onClick}
                  disabled={action.disabled}
                >
                  {action.label}
                </DsButton>
              ),
            )}
            {extraActions}
          </div>
        ) : null}
      </ProductJourneyScene>
    </div>
  );
}
