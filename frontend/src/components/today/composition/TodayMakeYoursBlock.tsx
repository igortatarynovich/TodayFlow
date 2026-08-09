"use client";

import Link from "next/link";
import { DsButton, DsChipGroup, DsGlassCard, DsBody, DsEyebrow } from "@/design-system";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import type { TodayProgressRow } from "@/lib/todayGrowthTrackers";
import type { MakeYoursProposal } from "@/lib/todayMakeYoursProposals";
import styles from "@/components/today/composition/TodayMakeYoursBlock.module.css";

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

/**
 * Make yours — tracker for what user already set; propose cards for empty slots.
 * Canon: docs/today/TODAY_MAKE_YOURS_AND_WELCOME_SOT.md
 */
export function TodayMakeYoursBlock({ progressRows, proposals, occupiedCategoryIds }: Props) {
  const occupied = new Set(occupiedCategoryIds);

  return (
    <div className={styles.root} data-testid="today-make-yours">
      <DsChipGroup
        options={CATEGORY_CHIPS.map((c) => ({
          id: c.id,
          label: c.label,
          sub: occupied.has(c.id) ? "стоит" : "можно поставить",
        }))}
        variant="outline"
        columns={2}
        testId="today-make-yours-categories"
      />

      {progressRows.length > 0 ? <TodayProgressTracker rows={progressRows} /> : null}

      {proposals.length > 0 ? (
        <div className={styles.proposeList} data-testid="today-make-yours-proposals">
          <DsEyebrow>Предложить из дня</DsEyebrow>
          {proposals.map((p) => (
            <DsGlassCard key={p.categoryId} className={styles.proposeCard} testId={`today-make-yours-propose-${p.categoryId}`}>
              <p className={styles.proposeKind}>{p.categoryLabel}</p>
              <p className={styles.proposeTitle}>{p.title}</p>
              {p.reason ? (
                <DsBody size="sm" tone="secondary">
                  {p.reason}
                </DsBody>
              ) : null}
              <DsButton href={p.href} variant="secondary" size="sm" className={styles.proposeCta}>
                {p.ctaLabel}
              </DsButton>
            </DsGlassCard>
          ))}
        </div>
      ) : null}

      {progressRows.length === 0 && proposals.length === 0 ? (
        <p className={styles.empty} data-testid="today-make-yours-empty">
          Нет опоры на сегодня — добавь в <Link href="/practices">Практиках</Link> или{" "}
          <Link href="/tracking/calendar">Календаре</Link>.
        </p>
      ) : null}
    </div>
  );
}
