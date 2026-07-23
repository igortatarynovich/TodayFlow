"use client";

import Link from "next/link";
import { useState, type ReactNode } from "react";
import { DsButton } from "@/design-system";
import type { FirstResultModel } from "@/lib/buildFirstResultModel";
import { ConversationThread } from "@/components/conversation/ConversationThread";
import { ConversationTurn } from "@/components/conversation/ConversationTurn";
import { FirstResultOrb } from "@/components/onboarding/valueFirst/FirstResultOrb";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import styles from "@/components/onboarding/valueFirst/firstResult.module.css";

type Props = {
  preview: FirstResultModel;
  saveHref: string;
  refineHref: string;
};

function WhyToggle({ explanation }: { explanation: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className={styles.whyBlock}>
      <button type="button" className={styles.whyButton} onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        {open ? "Скрыть" : "Почему?"}
      </button>
      {open ? <p className={styles.whyText}>{explanation}</p> : null}
    </div>
  );
}

function DeepenContent({ preview, showMore, onShowMore }: { preview: FirstResultModel; showMore: boolean; onShowMore: () => void }) {
  return (
    <>
      <section className={styles.section}>
        <p className={styles.sectionLabel}>{copy.preview.keyInfluencesLabel}</p>
        <div className={styles.keyGrid}>
          {preview.keyInfluences.map((tile) => (
            <article key={tile.id} className={styles.keyTile} data-testid={`key-influence-${tile.id}`}>
              <p className={styles.keyTileLabel}>{tile.label}</p>
              <p className={styles.keyTileValue}>{tile.value}</p>
              <p className={styles.keyTileTraits}>{tile.traits.join(" • ")}</p>
            </article>
          ))}
        </div>
      </section>

      {preview.nameInsight ? (
        <section className={styles.section} data-testid="name-insight-section">
          <p className={styles.sectionLabel}>{copy.preview.nameInsightLabel}</p>
          <p className={styles.nameHeadline}>{preview.nameInsight.headline}</p>
          <div className={styles.nameGrid}>
            {preview.nameInsight.tiles.map((tile) => (
              <article key={tile.id} className={styles.nameTile} data-testid={`name-tile-${tile.id}`}>
                <p className={styles.nameTileLabel}>{tile.label}</p>
                <p className={styles.nameTileValue}>{tile.value}</p>
                <p className={styles.nameTileMeaning}>{tile.meaning}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}

      {preview.miniPortrait.length > 0 ? (
        <article className={styles.miniPortraitCard}>
          <p className={styles.sectionLabel}>{copy.preview.miniPortraitLabel}</p>
          <ul className={styles.miniList}>
            {preview.miniPortrait.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
          <p className={styles.globalWhy}>{preview.globalWhySummary}</p>
        </article>
      ) : null}

      <section className={styles.section}>
        <p className={styles.sectionLabel}>{copy.preview.observationsLabel}</p>
        <div className={styles.portraitGrid}>
          {preview.portraitCards.map((card) => (
            <article
              key={card.id}
              className={styles.portraitCard}
              data-testid={`portrait-card-${card.id}`}
              data-card-type={card.cardType}
            >
              <p className={styles.portraitTitle}>
                <span aria-hidden>{card.icon}</span> {card.title}
              </p>
              <p className={styles.portraitBody}>{card.body}</p>
              <WhyToggle explanation={card.whyExplanation} />
            </article>
          ))}
        </div>

        {preview.moreObservations.length > 0 ? (
          <div className={styles.moreSection}>
            {!showMore ? (
              <button type="button" className={styles.moreToggle} data-testid="show-more-observations" onClick={onShowMore}>
                {copy.preview.showMoreObservations}
              </button>
            ) : (
              <div className={styles.portraitGrid}>
                {preview.moreObservations.map((card) => (
                  <article
                    key={card.id}
                    className={styles.portraitCard}
                    data-testid={`portrait-card-more-${card.id}`}
                    data-card-type={card.cardType}
                  >
                    <p className={styles.portraitTitle}>
                      <span aria-hidden>{card.icon}</span> {card.title}
                    </p>
                    <p className={styles.portraitBody}>{card.body}</p>
                    <WhyToggle explanation={card.whyExplanation} />
                  </article>
                ))}
              </div>
            )}
          </div>
        ) : null}
      </section>

      {preview.surprise ? (
        <article className={styles.surpriseCard} data-testid="surprise-card">
          <p className={styles.surpriseLabel}>{preview.surprise.label}</p>
          <p className={styles.surpriseBody}>{preview.surprise.body}</p>
          <WhyToggle explanation={preview.surprise.whyExplanation} />
        </article>
      ) : null}
    </>
  );
}

export function FirstResultScreen({ preview, saveHref, refineHref }: Props) {
  const [showMore, setShowMore] = useState(false);
  const elementTile = preview.keyInfluences.find((t) => t.id === "element");

  const openingMessage: ReactNode = (
    <>
      <div className={styles.hero}>
        <div className={styles.heroCopy}>
          <h2 className={styles.heroTitle}>{preview.heroTitle}</h2>
          <p className={styles.heroSubtitle}>{preview.heroSubtitle}</p>
        </div>
        <FirstResultOrb element={elementTile?.value ?? null} className={styles.heroOrb} />
      </div>
      <p className={styles.dominantHeadline}>{preview.dominantTrait.headline}</p>
      {preview.dominantTrait.supporting.slice(0, 1).map((line) => (
        <p key={line} className={styles.dominantSupport}>
          {line}
        </p>
      ))}
      <WhyToggle explanation={preview.dominantTrait.whyExplanation} />
    </>
  );

  return (
    <div className={styles.screen} data-testid="first-result-screen">
      <ConversationThread testId="onboarding-thread-preview">
        <ConversationTurn
          turnId="preview_recognition"
          message={openingMessage}
          deepen={
            <DeepenContent preview={preview} showMore={showMore} onShowMore={() => setShowMore(true)} />
          }
          deepenLabel={copy.preview.deepenLabel}
          response={
            <section className={styles.ctaSection}>
              <p className={styles.closingMessage}>{preview.closingMessage}</p>
              <div className={styles.ctaRow}>
                <Link href={saveHref} data-testid="onboarding-preview-save">
                  <DsButton variant="primary" size="block" className={styles.primaryCta}>
                    {preview.saveCtaLabel}
                  </DsButton>
                </Link>
                <Link href={refineHref} data-testid="onboarding-preview-refine">
                  <DsButton variant="secondary" size="block" className={styles.primaryCta}>
                    {preview.refineCtaLabel}
                  </DsButton>
                </Link>
              </div>
              {preview.limitationsLabels.length > 0 ? (
                <p className={styles.refineHint} data-testid="onboarding-preview-limitations">
                  Пока закрыто без времени и места: {preview.limitationsLabels.join(", ")}. Уточнение откроет
                  эти линии — сохранение закрепит основу.
                </p>
              ) : (
                <p className={styles.refineHint}>{preview.refineHint}</p>
              )}
            </section>
          }
        />
      </ConversationThread>
    </div>
  );
}
