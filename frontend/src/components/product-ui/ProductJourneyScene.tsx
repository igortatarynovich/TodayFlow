"use client";

import type { CSSProperties, ReactNode } from "react";
import {
  profileMotionStaggerDelay,
  profileMotionStyles,
  useProfileMotionInView,
} from "@/components/foundation/ProfileMotion";
import { ProfileAtmosphere, type ProfileAtmosphereMotif } from "@/components/profile/v2/ProfileAtmosphere";
import styles from "@/components/product-ui/ProductJourneyScene.module.css";

type ProductJourneySceneProps = {
  step?: string | number;
  title: string;
  lead?: string | null;
  motif?: ProfileAtmosphereMotif;
  children: ReactNode;
  testId?: string;
  bridge?: boolean;
  className?: string;
};

export function ProductJourneyScene({
  step,
  title,
  lead,
  motif = "insight",
  children,
  testId,
  bridge = false,
  className = "",
}: ProductJourneySceneProps) {
  const motion = useProfileMotionInView<HTMLElement>(40);

  return (
    <section
      ref={motion.ref}
      className={`${styles.journeyScene} ${bridge ? styles.bridgeScene : ""} ${motion.className} ${className}`.trim()}
      style={motion.style}
      data-testid={testId}
    >
      <ProfileAtmosphere motif={motif} />
      <header className={styles.journeySceneHeader}>
        <p className={styles.journeyStepIndex}>
          {step != null ? <span className={styles.journeyStepBadge}>{step}</span> : null}
          <span>{title}</span>
        </p>
        {lead ? <p className={styles.journeySceneLead}>{lead}</p> : null}
      </header>
      {children}
    </section>
  );
}

export type ProductNarrativeChapter = {
  id: string;
  kicker: string;
  paragraphs: string[];
};

type ProductNarrativeScrollProps = {
  theme?: string | null;
  chapters: ProductNarrativeChapter[];
  softWhy?: string | null;
  softWhyLabel?: string;
  testId?: string;
};

export function ProductNarrativeScroll({
  theme,
  chapters,
  softWhy = null,
  softWhyLabel = "Почему это важно",
  testId = "product-narrative-scroll",
}: ProductNarrativeScrollProps) {
  return (
    <article className={`${styles.narrativeScroll} ${profileMotionStyles.staggerItem}`} data-testid={testId}>
      {theme ? <p className={styles.synthesisKicker}>{theme}</p> : null}
      {chapters.map((chapter, chapterIndex) => (
        <section
          key={chapter.id}
          className={styles.narrativeChapter}
          data-testid={`product-narrative-${chapter.id}`}
          style={profileMotionStaggerDelay(chapterIndex + 1, 70) as CSSProperties}
        >
          <p className={styles.narrativeKicker}>{chapter.kicker}</p>
          {chapter.paragraphs.map((paragraph) => {
            const isSoftWhy = Boolean(softWhy) && paragraph === softWhy;
            return (
              <p
                key={`${chapter.id}-${paragraph.slice(0, 40)}`}
                className={isSoftWhy ? `${styles.narrativeParagraph} ${styles.narrativeWhy}` : styles.narrativeParagraph}
                data-testid={isSoftWhy ? "product-soft-why" : undefined}
              >
                {isSoftWhy ? (
                  <>
                    <span className={styles.softWhyLabel}>{softWhyLabel}</span>
                    {paragraph}
                  </>
                ) : (
                  paragraph
                )}
              </p>
            );
          })}
        </section>
      ))}
    </article>
  );
}
