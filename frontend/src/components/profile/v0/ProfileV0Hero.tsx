"use client";

import { ArchetypeSymbol } from "@/components/visualIdentity/ArchetypeSymbol";
import { ZodiacIcon } from "@/components/visualIdentity/ZodiacIcon";
import type { ProfileV0Header } from "@/lib/profilePage/buildProfileV0Data";
import type { Element } from "@/lib/zodiac-utils";
import styles from "./profileV0.module.css";

const HERO_SCENE_TONE: Record<Element, string> = {
  Fire: styles.heroSceneFire,
  Earth: styles.heroSceneEarth,
  Air: styles.heroSceneAir,
  Water: styles.heroSceneWater,
};

export function ProfileV0Hero({
  header,
  onOpenBirthData,
  onScrollDeeper,
}: {
  header: ProfileV0Header;
  onOpenBirthData: () => void;
  onScrollDeeper?: () => void;
}) {
  const toneClass = header.element ? HERO_SCENE_TONE[header.element] : styles.heroSceneNeutral;

  return (
    <section className={`${styles.profileCard} ${styles.profileHeroCard} ${toneClass}`} aria-label="Карта личности">
      <div className={styles.heroSceneTop}>
        <p className={styles.heroSceneKicker}>Карта личности</p>
        <button
          type="button"
          className={styles.topBarGhost}
          onClick={onOpenBirthData}
          aria-label="Данные рождения"
        >
          Данные рождения
        </button>
      </div>

      <div className={styles.profileHeroCardLayout}>
        <div className={styles.profileHeroCardCopy}>
          <p className={styles.profileCardLabel}>Твой архетип</p>
          <p className={styles.heroArchetypeTitle}>{header.archetypeLabel}</p>

          {header.poeticCaption ? (
            <p className={styles.heroIdentityLine}>{header.poeticCaption}</p>
          ) : header.tagline ? (
            <p className={styles.heroIdentityLine}>{header.tagline}</p>
          ) : null}

          {(header.sunSignDisplay || header.lifePath != null) && (
            <div className={styles.profileMetaPills}>
              {header.sunSignDisplay && header.sunSign ? (
                <span className={styles.profileMetaPill}>
                  <ZodiacIcon sign={header.sunSign} size={16} stroke="#6b5344" />
                  {header.sunSignDisplay}
                </span>
              ) : null}
              {header.lifePath != null ? (
                <span className={`${styles.profileMetaPill} ${styles.profileMetaPillAccent}`}>
                  {header.lifePath} · Число пути
                </span>
              ) : null}
            </div>
          )}

          {header.intro ? <p className={styles.profileHeroIntro}>{header.intro}</p> : null}

          {header.qualities.length ? (
            <ul className={styles.heroQualityMarks}>
              {header.qualities.map((q) => (
                <li key={`${q.title}-${q.subtitle}`} className={styles.heroQualityMark}>
                  <span className={styles.heroQualityTitle}>{q.title}</span>
                  <span className={styles.heroQualitySub}>{q.subtitle}</span>
                </li>
              ))}
            </ul>
          ) : null}

          <div className={styles.profileHeroDeepLink}>
            <button type="button" className={styles.profileHeroDeepBtn} onClick={onScrollDeeper}>
              Узнать себя глубже
              <span className={styles.profileCardCtaArrow} aria-hidden>
                →
              </span>
            </button>
          </div>
        </div>

        <div className={styles.profileHeroCardVisual}>
          <div className={styles.heroEmblemObject}>
            <div className={styles.heroEmblemGlow} aria-hidden />
            <div className={styles.heroOrbitOuter} aria-hidden />
            <div className={styles.heroOrbitMid} aria-hidden />
            <div className={styles.heroOrbitInner} aria-hidden />
            <div className={styles.heroOrbitCore} aria-hidden />
            <div className={styles.heroSymbolFrame}>
              <ArchetypeSymbol seed={header.archetypeLabel} size={96} stroke="#5b4630" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
