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
  ProductNarrativeScroll,
  type ProductNarrativeChapter,
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

  const storyChapters = useMemo((): ProductNarrativeChapter[] => {
    const chapters: ProductNarrativeChapter[] = [];

    if (model.mainAnswer?.trim()) {
      const parts = model.mainAnswer.split(/(?<=[.!?…])\s+/).filter(Boolean);
      chapters.push({
        id: "answer",
        kicker: chrome.mainAnswerEyebrow || "Ответ расклада",
        paragraphs: parts.length > 1 ? [parts.slice(0, 2).join(" "), parts.slice(2).join(" ")].filter(Boolean).map(ensurePeriod) : [ensurePeriod(model.mainAnswer)],
      });
    }

    if (model.storyNarrative?.trim()) {
      chapters.push({
        id: "why",
        kicker: whyEyebrow,
        paragraphs: [ensurePeriod(model.storyNarrative)],
      });
    }

    if (model.cardInsights.length) {
      const cardParas = model.cardInsights
        .map((card) => {
          const line = (card.line || "").trim();
          if (!line) return ensurePeriod(`${card.positionLabel} — ${card.cardNameRu}`);
          return ensurePeriod(`${card.positionLabel} · ${card.cardNameRu}: ${line}`);
        })
        .filter(Boolean);
      if (cardParas.length) {
        chapters.push({
          id: "cards",
          kicker: "Слой карт",
          paragraphs: cardParas,
        });
      }
    }

    const layers: string[] = [];
    if (model.insights.holding?.trim()) {
      layers.push(ensurePeriod(`${chrome.insightHoldingTitle}: ${model.insights.holding}`));
    }
    if (model.insights.shifting?.trim()) {
      layers.push(ensurePeriod(`${chrome.insightShiftingTitle}: ${model.insights.shifting}`));
    }
    if (model.insights.attention?.trim()) {
      layers.push(ensurePeriod(`${chrome.insightAttentionTitle}: ${model.insights.attention}`));
    }
    if (layers.length) {
      chapters.push({ id: "layers", kicker: "Что держит и что сдвигается", paragraphs: layers });
    }

    if (model.todaySuggestion?.trim()) {
      chapters.push({
        id: "today",
        kicker: chrome.todayEyebrow || "На сегодня",
        paragraphs: [ensurePeriod(model.todaySuggestion)],
      });
    }

    return chapters;
  }, [model, chrome, whyEyebrow]);

  const softWhy = model.storyNarrative ? ensurePeriod(model.storyNarrative) : null;

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
        lead="Ответ, почему так, слой карт и что с этим делать."
        motif="why"
        testId="tarot-journey-story"
      >
        {storyChapters.length ? (
          <ProductNarrativeScroll
            theme={spreadTitle || null}
            chapters={storyChapters}
            softWhy={softWhy}
            softWhyLabel={whyEyebrow}
            testId="tarot-narrative-scroll"
          />
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
