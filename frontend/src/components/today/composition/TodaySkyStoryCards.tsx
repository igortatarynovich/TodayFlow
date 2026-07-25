"use client";

import { useState, type ComponentType, type SVGProps } from "react";
import type { TodaySkyCard, TodaySkyIconKey } from "@/lib/todayDaySpine";
import {
  IconCompass,
  IconGem,
  IconHash,
  IconMoon,
  IconMountain,
  IconOrbitalGlyph,
  IconPalette,
  IconRefresh,
  IconSparkles,
  IconStar,
  IconSun,
  IconTarot,
} from "@/design-system/icons/DsIcons";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";

type Props = {
  cards: TodaySkyCard[];
  testId?: string;
};

const SKY_ICONS: Record<TodaySkyIconKey, ComponentType<SVGProps<SVGSVGElement>>> = {
  moon: IconMoon,
  sparkles: IconSparkles,
  star: IconStar,
  refresh: IconRefresh,
  compass: IconCompass,
  sun: IconSun,
  orbital: IconOrbitalGlyph,
  tarot: IconTarot,
  hash: IconHash,
  mountain: IconMountain,
  gem: IconGem,
  palette: IconPalette,
};

/**
 * Summary grid: icon + label + short title.
 * Tap expands the story in-place — no second full card elsewhere for the same fact.
 */
export function TodaySkyStoryCards({ cards, testId = "today-zone-sky-cards" }: Props) {
  const [openId, setOpenId] = useState<string | null>(null);
  if (cards.length === 0) return null;

  return (
    <div className={styles.skyCardGrid} data-testid={testId}>
      {cards.map((card) => {
        const Icon = SKY_ICONS[card.icon] ?? IconSparkles;
        const open = openId === card.id;
        return (
          <button
            key={card.id}
            type="button"
            className={`${styles.skyCard} ${open ? styles.skyCardOpen : ""}`.trim()}
            data-testid={`today-sky-${card.id}`}
            aria-expanded={open}
            onClick={() => setOpenId(open ? null : card.id)}
          >
            <span className={styles.skyCardIcon} aria-hidden>
              <Icon className={styles.skyCardIconSvg} />
            </span>
            <p className={styles.skyCardLabel}>{card.label}</p>
            <p className={styles.skyCardTitle}>{card.title}</p>
            {open ? <p className={styles.skyCardStory}>{card.story}</p> : null}
          </button>
        );
      })}
    </div>
  );
}
