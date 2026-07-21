"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useMemo } from "react";
import { DsBody, DsButton } from "@/design-system";
import { ProductWebShellConfigBridge, type ProductWebShellConfig } from "@/components/product-ui/productWebShellConfig";
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
                {history.map((item) => (
                  <li key={item.id} className={s.tarotHistoryItem}>
                    <div className={s.tarotHistoryMeta}>
                      <span>{item.dateLabel}</span>
                      <span>{item.domainLabel}</span>
                    </div>
                    <p>{item.summary}</p>
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

  return (
    <>
      <ProductWebShellConfigBridge config={shellConfig} />
      <div className={l.productWebContentV2}>
        <div className={v2.pageRoot}>
          <header className={pl.pageHeader}>
            <h1 className={v2.displayTitle}>{hub.pageTitle}</h1>
            <p className={v2.bodyLead}>{hub.pageSubtitle}</p>
          </header>

          <label className={pl.questionCard} htmlFor="tarot-hub-question">
            <textarea
              id="tarot-hub-question"
              className={pl.questionInput}
              value={customQuestion}
              onChange={(e) => onCustomQuestionChange?.(e.target.value)}
              placeholder={resolvedPlaceholder}
              rows={2}
            />
          </label>

          {domainChips.length > 0 ? (
            <div className={pl.domainChips}>
              {domainChips.map((chip) => (
                <button
                  key={chip.id}
                  type="button"
                  className={`${pl.domainChip} ${selectedDomainId === chip.id ? pl.domainChipActive : ""}`}
                  onClick={() => onDomainSelect?.(chip.id)}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          ) : null}

          {flowContent}

          {!hideSpreadSection && spreads.length > 0 ? (
            <section className={pl.spreadSection} aria-labelledby="tarot-spreads">
              <h2 id="tarot-spreads" className={v2.eyebrow}>
                {hub.spreadSectionTitle}
              </h2>
              <div className={pl.spreadList}>
                {spreads.map((spread) => {
                  const selected = selectedSpreadId === spread.id;
                  const body = (
                    <>
                      <span className={pl.spreadCount}>{spread.countLabel}</span>
                      <div>
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
                      <button
                        key={spread.id}
                        type="button"
                        className={`${pl.spreadOption} ${pl.spreadOptionButton} ${selected ? pl.spreadOptionSelected : ""}`}
                        onClick={() => onSpreadSelect(spread.id)}
                      >
                        {body}
                      </button>
                    );
                  }

                  return (
                    <Link key={spread.id} href={spread.href ?? "/tarot"} className={pl.spreadOption}>
                      {body}
                    </Link>
                  );
                })}
              </div>
            </section>
          ) : null}

          {onSubmitQuestion ? (
            <DsButton variant="primary" size="block" onClick={onSubmitQuestion} disabled={submitDisabled}>
              {resolvedSubmitLabel}
            </DsButton>
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
