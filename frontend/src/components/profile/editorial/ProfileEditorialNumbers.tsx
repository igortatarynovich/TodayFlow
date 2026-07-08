"use client";

import { useMemo, useState } from "react";
import type { ProfileV0NumbersCard } from "@/lib/profilePage/buildProfileV0Data";
import styles from "./profileEditorial.module.css";

const RING_PLACEMENT = [
  styles.numOrbitNodeTop,
  styles.numOrbitNodeLeft,
  styles.numOrbitNodeRight,
] as const;

export function ProfileEditorialNumbers({ numbers }: { numbers: ProfileV0NumbersCard }) {
  const defaultId = numbers.rings[0]?.id ?? "lp";
  const [activeId, setActiveId] = useState<string>(defaultId);
  const [patternOpen, setPatternOpen] = useState(false);

  const activeGuide = useMemo(
    () => numbers.guides.find((g) => g.id === activeId) ?? numbers.guides[0] ?? null,
    [activeId, numbers.guides],
  );

  const patternGuides = numbers.guides.filter((g) =>
    ["trap", "decisions", "recovery", "fear"].includes(g.id),
  );

  return (
    <section className={styles.numbersMonument} aria-labelledby="profile-numbers-title">
      <p id="profile-numbers-title" className={styles.sectionLabel}>
        Что тобой движет
      </p>

      <div className={styles.numOrbitStage}>
        <div className={styles.numOrbitRingOuter} aria-hidden />
        <div className={styles.numOrbitRingInner} aria-hidden />

        <button
          type="button"
          className={`${styles.numOrbitCore} ${activeId === "lp" ? styles.numOrbitNodeActive : ""}`}
          aria-pressed={activeId === "lp"}
          onClick={() => setActiveId("lp")}
        >
          <span className={styles.numOrbitCoreValue}>{numbers.hero.value}</span>
          <span className={styles.numOrbitCoreLabel}>Путь</span>
        </button>

        {numbers.rings.slice(0, 3).map((ring, index) => (
          <button
            key={ring.id}
            type="button"
            className={`${styles.numOrbitNode} ${RING_PLACEMENT[index] ?? styles.numOrbitNodeRight} ${
              activeId === ring.id ? styles.numOrbitNodeActive : ""
            }`}
            aria-pressed={activeId === ring.id}
            aria-label={`${ring.label}: ${ring.value}`}
            onClick={() => setActiveId(ring.id)}
          >
            <span className={styles.numOrbitNodeValue}>{ring.value}</span>
            <span className={styles.numOrbitNodeCaption}>{ring.label}</span>
          </button>
        ))}
      </div>

      <h2 className={styles.numbersPathTitle}>{numbers.hero.caption}</h2>

      {numbers.coreInsight ? (
        <p className={styles.numbersCoreInsight}>{numbers.coreInsight}</p>
      ) : numbers.hero.blurb ? (
        <p className={styles.numbersCoreInsight}>{numbers.hero.blurb}</p>
      ) : null}

      {activeGuide ? (
        <div className={styles.numbersMeaningPanel} role="region" aria-live="polite">
          <p className={styles.numbersMeaningKicker}>
            {activeGuide.value ? (
              <>
                <span className={styles.numbersMeaningDigit}>{activeGuide.value}</span>
                {activeGuide.title}
              </>
            ) : (
              activeGuide.title
            )}
          </p>
          <p className={styles.numbersMeaningBody}>{activeGuide.body}</p>
        </div>
      ) : null}

      {patternGuides.length ? (
        <>
          <button
            type="button"
            className={styles.numbersPatternBtn}
            aria-expanded={patternOpen}
            onClick={() => setPatternOpen((v) => !v)}
          >
            {patternOpen ? "Свернуть паттерн" : "Как числа ведут тебя в жизни"}
          </button>

          {patternOpen ? (
            <ul className={styles.numbersPatternList}>
              {patternGuides.map((guide) => (
                <li key={guide.id} className={styles.numbersPatternItem}>
                  <p className={styles.numbersPatternTitle}>{guide.title}</p>
                  <p className={styles.numbersPatternBody}>{guide.body}</p>
                </li>
              ))}
            </ul>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
