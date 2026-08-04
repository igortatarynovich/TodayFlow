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

/** Split choice option prose into ≤2 short lines (gives / costs). */
function splitChoiceLines(text: string | undefined | null): string[] {
  const raw = (text || "").replace(/\s+/g, " ").trim();
  if (!raw) return [];
  const labeled = raw.match(
    /(?:даёт|дает|gain)\s*[:—-]?\s*(.+?)(?:\s*(?:стоит|цена|риск|cost|risk)\s*[:—-]?\s*(.+))?$/i,
  );
  if (labeled?.[1]) {
    const lines = [ensurePeriod(labeled[1].trim())];
    if (labeled[2]?.trim()) lines.push(ensurePeriod(labeled[2].trim()));
    return lines.slice(0, 2);
  }
  const parts = raw
    .split(/(?<=[.!?…;])\s+|\s+[—–-]\s+/)
    .map((p) => ensurePeriod(p.replace(/^даёт\s*[:—-]?\s*/i, "").replace(/^стоит\s*[:—-]?\s*/i, "")))
    .filter(Boolean);
  if (parts.length <= 2) return parts;
  return [parts[0], parts.slice(1).join(" ")].filter(Boolean).slice(0, 2);
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
    return model.storyNarrative?.trim() ? splitParagraphs(model.storyNarrative) : [];
  }, [blocked, model.storyNarrative]);

  const answerParas = useMemo(
    () => (model.mainAnswer?.trim() ? splitParagraphs(model.mainAnswer) : []),
    [model.mainAnswer],
  );

  const choiceALines = useMemo(
    () => (!blocked ? splitChoiceLines(choice?.option_a_summary) : []),
    [blocked, choice?.option_a_summary],
  );
  const choiceBLines = useMemo(
    () => (!blocked ? splitChoiceLines(choice?.option_b_summary) : []),
    [blocked, choice?.option_b_summary],
  );
  const confidenceNote = (!blocked && choice?.confidence_note?.trim()) || "";

  const hasWhy =
    symbolsParas.length > 0 || storyParas.length > 0 || model.cardInsights.length > 0;

  const hasStory =
    answerParas.length > 0 ||
    Boolean(model.todaySuggestion?.trim()) ||
    choiceALines.length > 0 ||
    choiceBLines.length > 0 ||
    Boolean(confidenceNote) ||
    hasWhy;

  const pathALabel = loc === "ru" ? "Путь A" : "Path A";
  const pathBLabel = loc === "ru" ? "Путь B" : "Path B";
  const givesLabel = loc === "ru" ? "даёт" : "gives";
  const costsLabel = loc === "ru" ? "стоит" : "costs";

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
            : chrome.answerFirstLead
        }
        motif="tarot"
        plate="tarot_cards"
        testId="tarot-journey-story"
      >
        {hasStory ? (
          <div className={s.tarotResultNarrativeStack}>
            {answerParas.length ? (
              <ProductNarrativeBlock
                id="answer"
                kicker={chrome.mainAnswerKicker}
                lead={answerParas[0]}
                paragraphs={answerParas.slice(1)}
                accent="support"
                collapseAfter={answerParas.length > 2 ? 1 : undefined}
                testId="tarot-narrative-answer"
              />
            ) : null}

            {model.todaySuggestion?.trim() ? (
              <ProductNarrativeBlock
                id="today"
                kicker={chrome.todayEyebrow}
                paragraphs={[ensurePeriod(model.todaySuggestion)]}
                accent="support"
                testId="tarot-narrative-today"
              />
            ) : null}

            {choiceALines.length || choiceBLines.length ? (
              <div className={s.tarotChoiceCompare} data-testid="tarot-choice-compare">
                <p className={s.tarotChoiceCompareKicker}>{chrome.choiceCompareKicker}</p>
                <div className={s.tarotChoiceCompareGrid}>
                  {choiceALines.length ? (
                    <article className={s.tarotChoicePath} data-testid="tarot-choice-a">
                      <p className={s.tarotChoicePathTitle}>{pathALabel}</p>
                      <ul className={s.tarotChoicePathLines}>
                        {choiceALines.map((line, idx) => (
                          <li key={`a-${idx}`}>
                            <span className={s.tarotChoicePathCue}>
                              {idx === 0 ? givesLabel : costsLabel}
                            </span>{" "}
                            {line}
                          </li>
                        ))}
                      </ul>
                    </article>
                  ) : null}
                  {choiceBLines.length ? (
                    <article className={s.tarotChoicePath} data-testid="tarot-choice-b">
                      <p className={s.tarotChoicePathTitle}>{pathBLabel}</p>
                      <ul className={s.tarotChoicePathLines}>
                        {choiceBLines.map((line, idx) => (
                          <li key={`b-${idx}`}>
                            <span className={s.tarotChoicePathCue}>
                              {idx === 0 ? givesLabel : costsLabel}
                            </span>{" "}
                            {line}
                          </li>
                        ))}
                      </ul>
                    </article>
                  ) : null}
                </div>
              </div>
            ) : null}

            {confidenceNote ? (
              <p className={s.tarotConfidenceNote} data-testid="tarot-confidence-note">
                {ensurePeriod(confidenceNote)}
              </p>
            ) : null}

            {hasWhy ? (
              <details className={s.tarotWhyDetails} data-testid="tarot-why-details">
                <summary className={s.tarotWhySummary}>{chrome.whyDetailsSummary}</summary>
                <div className={s.tarotWhyBody}>
                  {symbolsParas.length ? (
                    <ProductNarrativeBlock
                      id="symbols"
                      kicker={chrome.symbolsKicker}
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
                      kicker={chrome.storyKicker}
                      lead={storyParas[0]}
                      paragraphs={storyParas.slice(1)}
                      accent="default"
                      collapseAfter={storyParas.length > 3 ? 2 : undefined}
                      testId="tarot-narrative-why"
                    />
                  ) : null}
                </div>
              </details>
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
