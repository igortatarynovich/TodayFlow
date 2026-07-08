"use client";

import { useEffect, useState } from "react";
import type { ProfileV0NumberRow, ProfileV0NumbersCard } from "@/lib/profilePage/buildProfileV0Data";
import styles from "./profileV0.module.css";

type SatelliteKey = "manifest" | "tension" | "bd" | "together";
type SatellitePlacement = "left" | "right" | "bottomRight";

function NumbersSatellite({
  row,
  placement,
  active,
  onSelect,
}: {
  row: ProfileV0NumberRow;
  placement: SatellitePlacement;
  active: boolean;
  onSelect: () => void;
}) {
  const placementClass = {
    left: styles.numbersSatelliteLeft,
    right: styles.numbersSatelliteRight,
    bottomRight: styles.numbersSatelliteBottomRight,
  }[placement];

  return (
    <button
      type="button"
      className={`${styles.numbersSatellite} ${placementClass} ${active ? styles.numbersSatelliteActive : ""}`}
      aria-expanded={active}
      aria-label={`${row.caption}: ${row.value}`}
      onClick={onSelect}
    >
      <span className={styles.numbersSatelliteKind}>Спутник</span>
      <span className={styles.numbersSatelliteCaption}>{row.caption}</span>
      <div className={styles.numbersSatelliteOrbit} aria-hidden>
        <span className={styles.numbersSatelliteDigit}>{row.value}</span>
      </div>
    </button>
  );
}

function resolveDetail(
  key: SatelliteKey,
  numbers: ProfileV0NumbersCard,
): { caption: string; body: string } | null {
  if (key === "together") {
    const body = numbers.expand.togetherDigest?.trim();
    if (!body) return null;
    return { caption: "Вместе", body };
  }

  const row =
    key === "manifest"
      ? numbers.second
      : key === "tension"
        ? numbers.third
        : numbers.expand.birthDay;
  if (!row?.blurb?.trim()) return null;
  return { caption: row.caption, body: row.blurb };
}

function satellitePlacement(key: string, hasBirthDay: boolean): SatellitePlacement {
  if (key === "manifest") return "left";
  if (key === "bd") return "right";
  if (key === "tension") return hasBirthDay ? "bottomRight" : "right";
  return "left";
}

const RING_PLACEMENTS = [
  styles.profileNumbersOrbitSatelliteTop,
  styles.profileNumbersOrbitSatelliteLeft,
  styles.profileNumbersOrbitSatelliteRight,
] as const;

export function ProfileV0NumbersMiniHero({
  numbers,
  onExpand,
  expanded,
}: {
  numbers: ProfileV0NumbersCard;
  onExpand: () => void;
  expanded: boolean;
}) {
  const { hero, expand } = numbers;
  const [activeKey, setActiveKey] = useState<SatelliteKey | null>(null);

  const hasSatellites = Boolean(numbers.second || numbers.third || expand.birthDay);
  const hasTogether = Boolean(expand.togetherDigest?.trim());
  const hasBirthDay = Boolean(expand.birthDay);

  useEffect(() => {
    if (!expanded) setActiveKey(null);
  }, [expanded]);

  const detail = activeKey ? resolveDetail(activeKey, numbers) : null;

  const toggleKey = (key: SatelliteKey) => {
    setActiveKey((prev) => (prev === key ? null : key));
  };

  const satelliteRows: ProfileV0NumberRow[] = [numbers.second, numbers.third, expand.birthDay].filter(
    (row): row is ProfileV0NumberRow => row != null,
  );

  return (
    <section className={`${styles.profileCard} ${styles.profileNumbersCard}`} aria-label="Что тобой движет">
      <p className={styles.profileCardLabel}>Что тобой движет</p>

      <div className={styles.profileNumbersOrbitCompact}>
        <div
          className={`${styles.profileNumbersOrbitCompactRing} ${styles.profileNumbersOrbitCompactRingOuter}`}
          aria-hidden
        />
        <div
          className={`${styles.profileNumbersOrbitCompactRing} ${styles.profileNumbersOrbitCompactRingInner}`}
          aria-hidden
        />
        <div className={styles.profileNumbersOrbitCompactCore}>
          <span className={styles.profileNumbersOrbitCompactValue}>{hero.value}</span>
        </div>

        {numbers.rings.slice(0, 3).map((ring, index) => (
          <div
            key={`${ring.label}-${ring.value}`}
            className={`${styles.profileNumbersOrbitSatellite} ${RING_PLACEMENTS[index] ?? RING_PLACEMENTS[2]}`}
          >
            <span className={styles.profileNumbersOrbitSatelliteDot}>{ring.value}</span>
            <span className={styles.profileNumbersOrbitSatelliteLabel}>{ring.label}</span>
          </div>
        ))}
      </div>

      <h3 className={styles.numbersMonumentCaption}>{hero.caption}</h3>
      {hero.blurb ? <p className={styles.numbersMonumentBlurb}>{hero.blurb}</p> : null}

      {expanded ? (
        <div className={styles.numbersMonumentCore}>
          {hasSatellites ? (
            <div className={styles.numbersSatelliteField}>
              {satelliteRows.map((row) => (
                <NumbersSatellite
                  key={row.key}
                  row={row}
                  placement={satellitePlacement(row.key, hasBirthDay)}
                  active={activeKey === row.key}
                  onSelect={() => toggleKey(row.key as SatelliteKey)}
                />
              ))}
            </div>
          ) : null}

          {detail ? (
            <div className={styles.numbersDetailPanel} role="region" aria-live="polite">
              <p className={styles.numbersDetailCaption}>{detail.caption}</p>
              <p className={styles.numbersDetailInsight}>{detail.body}</p>
            </div>
          ) : null}
        </div>
      ) : null}

      <button type="button" className={styles.profileCardCta} aria-expanded={expanded} onClick={onExpand}>
        {expanded ? "Свернуть" : "Посмотреть все числа"}
        {!expanded ? (
          <span className={styles.profileCardCtaArrow} aria-hidden>
            →
          </span>
        ) : null}
      </button>
    </section>
  );
}
