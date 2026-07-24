"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton, MotionSettle } from "@/design-system";
import { MOTION } from "@/design-system/motion/tokens";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
import { ProductJourneyScene } from "@/components/product-ui/ProductJourneyScene";
import journeyStyles from "@/components/product-ui/ProductJourneyScene.module.css";
import { tarotWebHubChromeBundle } from "@/components/product-ui/tarotWebHubChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import type { CoreProfile } from "@/lib/types";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import l from "@/design-system/layouts/dsLayouts.module.css";
import s from "@/components/product-ui/productWebScreens.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export type TarotSpreadOption = {
  id: string;
  countLabel: string;
  title: string;
  description: string;
  href?: string;
  recommended?: boolean;
};

export type TarotDomainChip = {
  id: string;
  label: string;
};

export type TarotHistoryItem = {
  id: string;
  dateLabel: string;
  domainLabel: string;
  summary: string;
};

export type TarotWebHubProps = {
  locale?: FlowPracticesChromeLocale;
  displayName?: string | null;
  profileMeta?: string | null;
  coreProfile?: CoreProfile | null;
  customQuestion?: string;
  onCustomQuestionChange?: (value: string) => void;
  questionPlaceholder?: string;
  domainChips?: TarotDomainChip[];
  selectedDomainId?: string | null;
  onDomainSelect?: (domainId: string) => void;
  spreads?: TarotSpreadOption[];
  selectedSpreadId?: string | null;
  onSpreadSelect?: (spreadId: string) => void;
  onSubmitQuestion?: () => void;
  submitDisabled?: boolean;
  submitLabel?: string;
  cardOfDayHint?: ReactNode;
  cardOfDayHref?: string;
  history?: TarotHistoryItem[];
  lastQuestion?: { text: string; href: string };
  flowContent?: ReactNode;
  hideSpreadSection?: boolean;
};

export function TarotWebHub({
  locale = "ru",
  displayName,
  profileMeta,
  coreProfile,
  customQuestion = "",
  onCustomQuestionChange,
  questionPlaceholder,
  domainChips = [],
  selectedDomainId,
  onDomainSelect,
  spreads = [],
  selectedSpreadId,
  onSpreadSelect,
  onSubmitQuestion,
  submitDisabled,
  submitLabel,
  cardOfDayHint,
  cardOfDayHref = "/today",
  history = [],
  lastQuestion,
  flowContent,
  hideSpreadSection = false,
}: TarotWebHubProps) {
  const hub = useMemo(() => tarotWebHubChromeBundle(locale), [locale]);
  const resolvedPlaceholder = questionPlaceholder ?? hub.questionPlaceholder;
  const resolvedSubmitLabel = submitLabel ?? hub.submitLabel;

  const shellConfig = useMemo((): ProductWebShellConfig => {
    const rail =
      history.length > 0 || lastQuestion ? (
        <>
          {history.length > 0 ? (
            <section className={s.tarotHubRailSection} aria-labelledby="tarot-history">
              <h2 id="tarot-history" className={v2.eyebrow}>
                {hub.historyTitle}
              </h2>
              <ul className={s.tarotHistoryList}>
                {history.map((item, index) => (
                  <li key={item.id} className={s.tarotHistoryItem}>
                    <MotionSettle delayMs={index * MOTION.staggerMs}>
                      <div className={s.tarotHistoryMeta}>
                        <span>{item.dateLabel}</span>
                        <span>{item.domainLabel}</span>
                      </div>
                      <p>{item.summary}</p>
                    </MotionSettle>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
          {lastQuestion ? (
            <section className={s.tarotLastQuestion} aria-label={hub.lastQuestionLabel}>
              <p className={v2.eyebrow}>{hub.lastQuestionLabel}</p>
              <p className={s.tarotLastQuestionText}>{lastQuestion.text}</p>
              <Link href={lastQuestion.href} className={s.tarotLastQuestionLink}>
                {hub.openLink}
              </Link>
            </section>
          ) : null}
        </>
      ) : undefined;

    return {
      testId: "tarot-web-hub",
      mainWide: true,
      displayName,
      profileMeta,
      coreProfile,
      rail,
    };
  }, [
    coreProfile,
    displayName,
    history,
    hub.historyTitle,
    hub.lastQuestionLabel,
    hub.openLink,
    lastQuestion,
    profileMeta,
  ]);

  const showSpreads = !hideSpreadSection && spreads.length > 0;

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={l.productWebContentV2}>
        <div className={`${v2.pageRoot} ${s.tarotHubQuiet}`} data-testid="tarot-web-hub-journey">
          <header className={pl.pageHeader}>
            <h1 className={v2.displayTitle}>{hub.pageTitle}</h1>
            <p className={v2.bodyLead}>{hub.pageSubtitle}</p>
          </header>

          <ProductJourneyScene
            step={1}
            title={hub.questionStepTitle}
            lead={hub.questionStepLead}
            motif="today"
            testId="tarot-hub-step-question"
          >
            <label className={pl.questionCardQuiet} htmlFor="tarot-hub-question">
              <textarea
                id="tarot-hub-question"
                className={pl.questionInput}
                value={customQuestion}
                onChange={(e) => onCustomQuestionChange?.(e.target.value)}
                placeholder={resolvedPlaceholder}
                rows={2}
              />
            </label>
          </ProductJourneyScene>

          {domainChips.length > 0 ? (
            <ProductJourneyScene
              step={2}
              title={hub.directionStepTitle}
              lead={hub.directionStepLead}
              motif="insight"
              testId="tarot-hub-step-direction"
            >
              <div className={journeyStyles.tabRow} role="group" aria-label={hub.directionStepTitle}>
                {domainChips.map((chip) => {
                  const active = selectedDomainId === chip.id;
                  return (
                    <button
                      key={chip.id}
                      type="button"
                      className={`${journeyStyles.tabChip} ${active ? journeyStyles.tabChipActive : ""}`.trim()}
                      aria-pressed={active}
                      onClick={() => onDomainSelect?.(chip.id)}
                    >
                      {chip.label}
                    </button>
                  );
                })}
              </div>
            </ProductJourneyScene>
          ) : null}

          {flowContent}

          {showSpreads ? (
            <ProductJourneyScene
              step={domainChips.length > 0 ? 3 : 2}
              title={hub.spreadStepTitle}
              lead={hub.spreadStepLead}
              motif="effort"
              testId="tarot-hub-step-spread"
            >
              <ol className={pl.spreadStepList} aria-label={hub.spreadSectionTitle}>
                {spreads.map((spread, index) => {
                  const selected = selectedSpreadId === spread.id;
                  const body = (
                    <>
                      <span className={pl.spreadStepIndex} aria-hidden>
                        {spread.countLabel || index + 1}
                      </span>
                      <div className={pl.spreadStepBody}>
                        <p className={pl.spreadTitle}>{spread.title}</p>
                        <DsBody size="sm" muted>
                          {spread.description}
                        </DsBody>
                        {spread.recommended ? (
                          <span className={pl.spreadRecommended}>{hub.spreadRecommended}</span>
                        ) : null}
                      </div>
                    </>
                  );

                  if (onSpreadSelect) {
                    return (
                      <li key={spread.id}>
                        <MotionSettle delayMs={index * MOTION.staggerMs}>
                          <button
                            type="button"
                            className={`${pl.spreadStepOption} ${selected ? pl.spreadStepOptionSelected : ""}`.trim()}
                            onClick={() => onSpreadSelect(spread.id)}
                            aria-pressed={selected}
                          >
                            {body}
                          </button>
                        </MotionSettle>
                      </li>
                    );
                  }

                  return (
                    <li key={spread.id}>
                      <MotionSettle delayMs={index * MOTION.staggerMs}>
                        <Link href={spread.href ?? "/tarot"} className={pl.spreadStepOption}>
                          {body}
                        </Link>
                      </MotionSettle>
                    </li>
                  );
                })}
              </ol>
            </ProductJourneyScene>
          ) : null}

          {onSubmitQuestion ? (
            <ProductJourneyScene
              step={(domainChips.length > 0 ? 3 : 2) + (showSpreads ? 1 : 0)}
              title="Дальше"
              lead="Когда вопрос и формат ясны — к ритуалу."
              motif="bridge"
              bridge
              testId="tarot-hub-step-bridge"
            >
              <div className={journeyStyles.actionRow}>
                <DsButton variant="primary" size="block" onClick={onSubmitQuestion} disabled={submitDisabled}>
                  {resolvedSubmitLabel}
                </DsButton>
              </div>
            </ProductJourneyScene>
          ) : null}

          {cardOfDayHint ? (
            <p className={pl.cardOfDayHint}>
              {cardOfDayHint}{" "}
              <Link href={cardOfDayHref} className={s.tarotLastQuestionLink}>
                {hub.openLink}
              </Link>
            </p>
          ) : null}
        </div>
      </div>
    </>
  );
}
