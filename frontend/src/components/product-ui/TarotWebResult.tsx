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
import { guestSignupHref } from "@/lib/guestAccessStore";
import { buildTarotDeepenHref, pickTarotDeepenOffers } from "@/lib/tarotDeepenOffers";
import { t } from "@/lib/i18n";
import s from "@/components/product-ui/productWebScreens.module.css";

export type TarotWebResultProps = {
  model: TarotReadingStoryModel;
  locale?: FlowPracticesChromeLocale;
  spreadTitle?: string;
  cardsAriaLabel?: string;
  storyEyebrow?: string;
  extraActions?: ReactNode;
  /** Paid/trial unlocks deepen chooser; guests and free get teaser. */
  isAuthenticated?: boolean;
  hasPaidAccess?: boolean;
  concernDomain?: string | null;
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
  isAuthenticated = false,
  hasPaidAccess = false,
  concernDomain = null,
}: TarotWebResultProps) {
  const chrome = useMemo(() => tarotReadingStoryChromeBundle(locale), [locale]);
  const loc = locale === "ru" ? "ru" : "en";
  const deepenOffers = useMemo(
    () => pickTarotDeepenOffers(concernDomain, { limit: 4 }),
    [concernDomain],
  );
  const cardsLabel =
    cardsAriaLabel ??
    t("tarot.story.cardsSpreadAria", loc === "ru" ? "Карты расклада" : "Spread cards", undefined, loc);

  const blocked = model.synthesisStatus === "unresolved_cards";
  const choice = model.choiceStory;

  const symbolsParas = useMemo(() => {
    if (blocked) return [];
    const raw = model.symbolsOverview?.trim();
    return raw ? splitParagraphs(raw) : [];
  }, [blocked, model.symbolsOverview]);

  const storyParas = useMemo(() => {
    if (blocked) return [];
    if (choice?.option_a_summary || choice?.option_b_summary) {
      return [choice.option_a_summary, choice.option_b_summary, model.storyNarrative]
        .map((p) => (p ? ensurePeriod(p) : ""))
        .filter(Boolean);
    }
    return model.storyNarrative?.trim() ? splitParagraphs(model.storyNarrative) : [];
  }, [blocked, choice, model.storyNarrative]);

  const answerParas = useMemo(
    () => (model.mainAnswer?.trim() ? splitParagraphs(model.mainAnswer) : []),
    [model.mainAnswer],
  );

  const hasStory =
    symbolsParas.length > 0 ||
    storyParas.length > 0 ||
    answerParas.length > 0 ||
    Boolean(model.todaySuggestion?.trim());

  return (
    <div className={s.tarotWebLayout} data-testid="tarot-web-result">
      <ProductJourneyScene
        step={1}
        title="Вопрос"
        lead={spreadTitle || null}
        motif="tarot"
        plate="tarot_quiet"
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
        title={blocked ? "Расклад" : "Разбор"}
        lead={
          blocked
            ? "Карты не удалось полностью распознать для интерпретации."
            : "Символы → связь с вопросом → ответ → шаг."
        }
        motif="tarot"
        plate="tarot_cards"
        testId="tarot-journey-story"
      >
        {hasStory ? (
          <div className={s.tarotResultNarrativeStack}>
            {symbolsParas.length ? (
              <ProductNarrativeBlock
                id="symbols"
                kicker="Что здесь показывают карты"
                lead={symbolsParas[0]}
                paragraphs={symbolsParas.slice(1)}
                accent="sky"
                collapseAfter={symbolsParas.length > 3 ? 2 : undefined}
                testId="tarot-narrative-symbols"
              />
            ) : null}

            {storyParas.length ? (
              <ProductNarrativeBlock
                id="story"
                kicker="Как это связано с твоим вопросом"
                lead={storyParas[0]}
                paragraphs={storyParas.slice(1)}
                accent="default"
                collapseAfter={storyParas.length > 3 ? 2 : undefined}
                testId="tarot-narrative-why"
              />
            ) : null}

            {answerParas.length ? (
              <ProductNarrativeBlock
                id="answer"
                kicker="Ответ на вопрос"
                lead={answerParas[0]}
                paragraphs={answerParas.slice(1)}
                accent="support"
                collapseAfter={answerParas.length > 3 ? 1 : undefined}
                testId="tarot-narrative-answer"
              />
            ) : null}

            {model.todaySuggestion?.trim() ? (
              <ProductNarrativeBlock
                id="today"
                kicker="Что сделать дальше"
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
            : "Один контекстный шаг из этого вывода — или углубить тему."
        }
        motif="tarot"
        plate="reflection"
        bridge
        testId="tarot-journey-bridge"
      >
        {!blocked ? (
          <div className={s.tarotDeepenBlock} data-testid="tarot-deepen-offers">
            {hasPaidAccess ? (
              <>
                <p className={s.tarotDeepenTitle}>Углубить тему</p>
                <p className={s.tarotDeepenLead}>
                  Выбери направление — новый расклад с практическим фокусом. Подписка открывает этот слой.
                </p>
                <div className={s.tarotDeepenGrid}>
                  {deepenOffers.map((offer) => (
                    <Link
                      key={offer.id}
                      href={buildTarotDeepenHref(offer)}
                      className={s.tarotDeepenCard}
                      data-testid={`tarot-deepen-${offer.id}`}
                    >
                      <span className={s.tarotDeepenCardLabel}>{offer.label}</span>
                      <span className={s.tarotDeepenCardHint}>{offer.hint}</span>
                    </Link>
                  ))}
                </div>
              </>
            ) : isAuthenticated ? (
              <>
                <p className={s.tarotDeepenTitle}>Углубить тему</p>
                <p className={s.tarotDeepenLead}>
                  С подпиской можно углубить деньги, близость или работу — с практическими подсказками поверх этого разбора.
                </p>
                <Link href="/pricing" className={journeyStyles.bridgeLink} data-testid="tarot-deepen-pricing">
                  → Сравнить подписку
                </Link>
              </>
            ) : (
              <>
                <p className={s.tarotDeepenTitle}>Углубить тему</p>
                <p className={s.tarotDeepenLead}>
                  Углубление тем (деньги, близость, работа) — слой подписки. Сначала создай аккаунт, затем открой доступ.
                </p>
                <Link href={guestSignupHref()} className={journeyStyles.bridgeLink}>
                  → Создать мой Today
                </Link>
              </>
            )}
          </div>
        ) : null}
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
