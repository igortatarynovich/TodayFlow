"use client";

import Link from "next/link";
import { DsButton, DsChipGroup, DsGlassCard } from "@/design-system";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import type { MakeYoursProposal } from "@/lib/todayMakeYoursProposals";
import styles from "@/components/today/composition/TodayMakeYoursBlock.module.css";

const CATEGORY_HREF: Record<string, string> = {
  practice: "/practices",
  ascetic: "/tracking/calendar?create=ascetic",
  affirmation: "/affirmations",
  mantra: "/affirmations",
  habit: "/tracking/calendar?create=habit",
  goal: "/tracking/calendar?create=goal",
};

const CATEGORY_CHIPS = [
  { id: "practice", label: "Практика" },
  { id: "ascetic", label: "Аскеза" },
  { id: "affirmation", label: "Аффирмация" },
  { id: "mantra", label: "Мантра" },
  { id: "habit", label: "Привычка" },
  { id: "goal", label: "Цель" },
] as const;

type Props = {
  progressRows: TodayProgressRow[];
  proposals: MakeYoursProposal[];
  occupiedCategoryIds: string[];
};

function shortTitle(text: string, max = 72): string {
  const t = text.replace(/\s+/g, " ").trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1).trimEnd()}…`;
}

/**
 * Make yours — tracker if set; short propose cards if empty.
 * No mechanism labels. Canon: TODAY_MAKE_YOURS_AND_WELCOME_SOT.
 */
export function TodayMakeYoursBlock({ progressRows, proposals, occupiedCategoryIds }: Props) {
  const occupied = new Set(occupiedCategoryIds);

  return (
    <div className={styles.root} data-testid="today-make-yours">
      <DsChipGroup
        options={CATEGORY_CHIPS.map((c) => ({
          id: c.id,
          label: c.label,
          sub: occupied.has(c.id) ? "есть" : undefined,
        }))}
        variant="outline"
        columns={2}
        testId="today-make-yours-categories"
        onSelect={(id) => {
          const href = CATEGORY_HREF[id];
          if (href && typeof window !== "undefined") window.location.assign(href);
        }}
      />

      {progressRows.length > 0 ? <TodayProgressTracker rows={progressRows} title="" /> : null}

      {proposals.length > 0 ? (
        <div className={styles.proposeList} data-testid="today-make-yours-proposals">
          {proposals.map((p) => (
            <DsGlassCard key={p.categoryId} className={styles.proposeCard} testId={`today-make-yours-propose-${p.categoryId}`}>
              <p className={styles.proposeKind}>{p.categoryLabel}</p>
              <p className={styles.proposeTitle}>{shortTitle(p.title)}</p>
              <DsButton href={p.href} variant="secondary" size="sm" className={styles.proposeCta}>
                {p.ctaLabel}
              </DsButton>
            </DsGlassCard>
          ))}
        </div>
      ) : null}

      {progressRows.length === 0 && proposals.length === 0 ? (
        <p className={styles.empty} data-testid="today-make-yours-empty">
          <Link href="/practices">Практики</Link>
          {" · "}
          <Link href="/tracking/calendar">Календарь</Link>
        </p>
      ) : null}
    </div>
  );
}
