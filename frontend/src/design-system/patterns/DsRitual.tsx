/**
 * DsRitual — mobile Today ritual building blocks from design handoff
 * (`docs/design/design_handoff_todayflow` · DsRitual.prompt.md).
 *
 * Mood color SoT remains Day Atmosphere (`--day-*` via `html[data-day-mode]`).
 * These components consume foundation glass tokens (`--tf-ds-glass-*`) — no page hex.
 */

"use client";

import type { CSSProperties, ReactNode } from "react";
import { DsCard } from "@/design-system/primitives/DsCard";
import { joinClass } from "@/design-system/utils/joinClass";
import type { DayVisualMode } from "@/lib/dayAtmosphere";
import styles from "@/design-system/patterns/dsRitual.module.css";

const DARK_MOODS: ReadonlySet<string> = new Set(["tension", "depth"]);

export function isDsRitualDarkMood(mood?: string | null): boolean {
  return Boolean(mood && DARK_MOODS.has(mood));
}

/** Optional scoped mood plane — prefers live `--day-*` when mood matches document. */
export function DsMoodBackground({
  mood,
  children,
  className,
  style,
  testId,
}: {
  mood?: DayVisualMode | string | null;
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  testId?: string;
}) {
  return (
    <div
      className={joinClass(styles.moodBackground, className)}
      data-ds-mood={mood || undefined}
      data-ds-mood-dark={isDsRitualDarkMood(mood) ? "true" : undefined}
      data-testid={testId}
      style={style}
    >
      {children}
    </div>
  );
}

/** Frosted glass over Day Atmosphere — handoff `DsGlassCard`. */
export function DsGlassCard({
  mood,
  children,
  className,
  testId,
  size = "compact",
}: {
  mood?: DayVisualMode | string | null;
  children: ReactNode;
  className?: string;
  testId?: string;
  size?: "default" | "compact";
}) {
  return (
    <DsCard
      variant="glass"
      size={size}
      testId={testId}
      className={joinClass(
        styles.glassCard,
        isDsRitualDarkMood(mood) ? styles.glassCardDark : null,
        className,
      )}
    >
      {children}
    </DsCard>
  );
}

export type DsChipOption = {
  id?: string;
  label: string;
  sub?: string;
};

/** Selectable or display chip grid — Priority / mood / activity tags. */
export function DsChipGroup({
  options,
  selected,
  onSelect,
  variant = "solid",
  columns = 2,
  className,
  testId,
}: {
  options: DsChipOption[];
  selected?: string | null;
  onSelect?: (id: string) => void;
  variant?: "solid" | "outline";
  columns?: 2 | 3;
  className?: string;
  testId?: string;
}) {
  const interactive = typeof onSelect === "function";
  return (
    <div
      className={joinClass(
        styles.chipGroup,
        columns === 3 ? styles.chipGroup3 : styles.chipGroup2,
        className,
      )}
      data-variant={variant}
      data-testid={testId}
      role={interactive ? "listbox" : undefined}
    >
      {options.map((opt) => {
        const id = opt.id ?? opt.label;
        const isSelected = selected != null && selected === id;
        const Tag = interactive ? "button" : "span";
        return (
          <Tag
            key={id}
            type={interactive ? "button" : undefined}
            role={interactive ? "option" : undefined}
            aria-selected={interactive ? isSelected : undefined}
            className={joinClass(
              styles.chip,
              variant === "outline" ? styles.chipOutline : styles.chipSolid,
              isSelected ? styles.chipSelected : null,
              opt.sub ? styles.chipWithSub : null,
            )}
            data-testid={interactive ? `ds-chip-${id}` : undefined}
            onClick={interactive ? () => onSelect?.(id) : undefined}
          >
            <span className={styles.chipLabel}>{opt.label}</span>
            {opt.sub ? <span className={styles.chipSub}>{opt.sub}</span> : null}
          </Tag>
        );
      })}
    </div>
  );
}

/** Habit / practice / ascesis streak row with 7-day dots. */
export function DsHabitStreakRow({
  name,
  kind,
  streakLabel,
  days,
  className,
  testId,
}: {
  name: string;
  kind: string;
  streakLabel: string;
  /** Length 7 preferred; true = completed. */
  days: boolean[];
  className?: string;
  testId?: string;
}) {
  return (
    <div className={joinClass(styles.streakRow, className)} data-testid={testId}>
      <div className={styles.streakHead}>
        <p className={styles.streakName}>{name}</p>
        <p className={styles.streakMeta}>{streakLabel}</p>
      </div>
      <p className={styles.streakKind}>{kind}</p>
      <div className={styles.streakDots} aria-hidden>
        {days.map((done, i) => (
          <span key={i} className={styles.streakDot} data-done={done ? "true" : "false"} />
        ))}
      </div>
    </div>
  );
}
