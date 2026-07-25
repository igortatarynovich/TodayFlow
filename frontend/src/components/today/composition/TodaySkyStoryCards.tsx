"use client";

import type { ComponentType, SVGProps } from "react";
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

export function TodaySkyStoryCards({ cards, testId = "today-zone-sky-cards" }: Props) {
  if (cards.length === 0) return null;

  return (
    <div className={styles.skyCardGrid} data-testid={testId}>
      {cards.map((card) => {
        const Icon = SKY_ICONS[card.icon] ?? IconSparkles;
        return (
          <article key={card.id} className={styles.skyCard} data-testid={`today-sky-${card.id}`}>
            <span className={styles.skyCardIcon} aria-hidden>
              <Icon className={styles.skyCardIconSvg} />
            </span>
            <p className={styles.skyCardLabel}>{card.label}</p>
            <p className={styles.skyCardTitle}>{card.title}</p>
            <p className={styles.skyCardStory}>{card.story}</p>
          </article>
        );
      })}
    </div>
  );
}
