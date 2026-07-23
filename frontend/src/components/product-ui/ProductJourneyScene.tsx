"use client";

import type { CSSProperties, ReactNode } from "react";
import { useId, useState } from "react";
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

export type ProductNarrativeMedia =
  | { kind: "image"; src: string; alt?: string }
  | { kind: "color"; hex: string; label?: string }
  | { kind: "node"; node: ReactNode };

export type ProductNarrativeBlockProps = {
  id?: string;
  kicker: string;
  lead?: string | null;
  paragraphs?: string[];
  /** Extra body when paragraphs alone are not enough (chips, dual panels). */
  children?: ReactNode;
  media?: ProductNarrativeMedia | null;
  accent?: "default" | "dual" | "support" | "sky";
  /** Collapse long body behind «раскрыть» when more than collapseAfter paragraphs. */
  collapseAfter?: number;
  expandLabel?: string;
  collapseLabel?: string;
  testId?: string;
  className?: string;
  style?: CSSProperties;
};

export function ProductNarrativeBlock({
  id,
  kicker,
  lead = null,
  paragraphs = [],
  children,
  media = null,
  accent = "default",
  collapseAfter,
  expandLabel = "Раскрыть",
  collapseLabel = "Свернуть",
  testId,
  className = "",
  style,
}: ProductNarrativeBlockProps) {
  const reactId = useId();
  const panelId = id ?? `narrative-block-${reactId}`;
  const canCollapse =
    typeof collapseAfter === "number" &&
    collapseAfter >= 0 &&
    paragraphs.length > collapseAfter;
  const [expanded, setExpanded] = useState(!canCollapse);
  const visibleParagraphs = canCollapse && !expanded ? paragraphs.slice(0, collapseAfter) : paragraphs;
  const accentClass =
    accent === "dual"
      ? styles.narrativeBlockDual
      : accent === "support"
        ? styles.narrativeBlockSupport
        : accent === "sky"
          ? styles.narrativeBlockSky
          : "";

  return (
    <section
      className={`${styles.narrativeBlock} ${accentClass} ${profileMotionStyles.staggerItem} ${className}`.trim()}
      data-testid={testId ?? `product-narrative-block-${panelId}`}
      style={style}
    >
      <div className={styles.narrativeBlockMain}>
        <p className={styles.narrativeBlockKicker}>{kicker}</p>
        {lead ? <p className={styles.narrativeBlockLead}>{lead}</p> : null}
        {visibleParagraphs.map((paragraph) => (
          <p key={`${panelId}-${paragraph.slice(0, 48)}`} className={styles.narrativeBlockBody}>
            {paragraph}
          </p>
        ))}
        {children}
        {canCollapse ? (
          <button
            type="button"
            className={styles.narrativeExpandBtn}
            aria-expanded={expanded}
            onClick={() => setExpanded((v) => !v)}
          >
            {expanded ? collapseLabel : expandLabel}
          </button>
        ) : null}
      </div>
      {media ? (
        <div className={styles.narrativeBlockMedia} aria-hidden={media.kind !== "image"}>
          {media.kind === "image" ? (
            // eslint-disable-next-line @next/next/no-img-element -- static public inventory
            <img className={styles.narrativeMediaImage} src={media.src} alt={media.alt ?? ""} />
          ) : null}
          {media.kind === "color" ? (
            <span className={styles.narrativeColorChip} style={{ background: media.hex }} title={media.label}>
              {media.label ? <span className={styles.narrativeColorLabel}>{media.label}</span> : null}
            </span>
          ) : null}
          {media.kind === "node" ? media.node : null}
        </div>
      ) : null}
    </section>
  );
}

/** Resolve planet icon from public inventory when name matches. */
export function planetIconSrc(planetRuOrEn: string | null | undefined): string | null {
  const raw = (planetRuOrEn ?? "").trim().toLowerCase();
  if (!raw) return null;
  const map: Record<string, string> = {
    sun: "sun",
    солнце: "sun",
    moon: "moon",
    луна: "moon",
    mercury: "mercury",
    меркурий: "mercury",
    venus: "venus",
    венера: "venus",
    mars: "mars",
    марс: "mars",
    jupiter: "jupiter",
    юпитер: "jupiter",
    saturn: "saturn",
    сатурн: "saturn",
    uranus: "uranus",
    уран: "uranus",
    neptune: "neptune",
    нептун: "neptune",
    pluto: "pluto",
    плутон: "pluto",
  };
  for (const [key, file] of Object.entries(map)) {
    if (raw.includes(key)) return `/images/icons/planets/${file}.svg`;
  }
  return null;
}
