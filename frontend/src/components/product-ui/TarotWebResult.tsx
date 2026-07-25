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
  extraActions,
}: TarotWebResultProps) {
  const chrome = useMemo(() => tarotReadingStoryChromeBundle(locale), [locale]);
  const loc = locale === "ru" ? "ru" : "en";
  const cardsLabel =
    cardsAriaLabel ??
    t("tarot.story.cardsSpreadAria", loc === "ru" ? "Карты расклада" : "Spread cards", undefined, loc);

  const blocked = model.synthesisStatus === "unresolved_cards";
  const choice = model.choiceStory;

  const answerParas = useMemo(
    () => (model.mainAnswer?.trim() ? splitParagraphs(model.mainAnswer) : []),
    [model.mainAnswer],
  );

  const compareParas = useMemo(() => {
    if (blocked) return [];
    if (choice) {
      return [
        choice.option_a_summary,
        choice.option_b_summary,
        choice.confidence_note,
      ]
        .map((p) => (p ? ensurePeriod(p) : ""))
        .filter(Boolean);
    }
    if (model.storyNarrative?.trim()) return [ensurePeriod(model.storyNarrative)];
    return [];
  }, [blocked, choice, model.storyNarrative]);

  const tensionParas = useMemo(() => {
    if (blocked) return [];
    const holding = model.insights.holding?.trim() || choice?.hidden_tension?.trim() || "";
    return holding ? [ensurePeriod(holding)] : [];
  }, [blocked, model.insights.holding, choice]);

  const hasStory =
    answerParas.length > 0 ||
    compareParas.length > 0 ||
    tensionParas.length > 0 ||
    Boolean(model.todaySuggestion?.trim());

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
                  width={160}
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
        title={blocked ? "Расклад" : "Ответ"}
        lead={
          blocked
            ? "Карты не удалось полностью распознать для интерпретации."
            : choice
              ? "Сравнение двух путей и следующий шаг."
              : "Главный вывод и что с ним делать."
        }
        motif="why"
        testId="tarot-journey-story"
      >
        {hasStory ? (
          <div className={s.tarotResultNarrativeStack}>
            {answerParas.length ? (
              <ProductNarrativeBlock
                id="answer"
                kicker={blocked ? "Что случилось" : "Главный вывод"}
                lead={answerParas[0]}
                paragraphs={answerParas.slice(1)}
                accent="support"
                collapseAfter={answerParas.length > 3 ? 1 : undefined}
                testId="tarot-narrative-answer"
              />
            ) : null}

            {compareParas.length ? (
              <ProductNarrativeBlock
                id="compare"
                kicker={choice ? "Сравнение вариантов" : "Как карты складываются"}
                lead={compareParas[0]}
                paragraphs={compareParas.slice(1)}
                accent="sky"
                collapseAfter={compareParas.length > 2 ? 1 : undefined}
                testId="tarot-narrative-why"
              />
            ) : null}

            {tensionParas.length ? (
              <ProductNarrativeBlock
                id="tension"
                kicker="Что мешает увидеть решение"
                paragraphs={tensionParas}
                accent="default"
                testId="tarot-narrative-tension"
              />
            ) : null}

            {model.todaySuggestion?.trim() ? (
              <ProductNarrativeBlock
                id="today"
                kicker={chrome.todayEyebrow || "Следующий шаг"}
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
        title="Дальше"
        lead={
          blocked
            ? "Можно пересобрать расклад или открыть карты снова."
            : "Один контекстный шаг из этого вывода."
        }
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
