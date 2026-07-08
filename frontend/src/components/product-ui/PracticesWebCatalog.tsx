"use client";

import Link from "next/link";
import { DsCheckbox } from "@/design-system";
import { IconActivity, IconEye, IconSun, IconWaves } from "@/design-system/icons/DsIcons";
import type { ReactNode } from "react";
import s from "@/components/product-ui/productWebScreens.module.css";

export type PracticesTodayItem = {
  id: string;
  title: string;
  category: string;
  durationLabel: string;
  completed?: boolean;
};

export type PracticesProgramItem = {
  id: string;
  title: string;
  description: string;
  durationLabel: string;
  sessionsLabel?: string;
  icon?: "wind" | "eye" | "star" | "book";
  href: string;
};

export type PracticesCatalogTab = {
  id: string;
  label: string;
};

const PROGRAM_ICONS: Record<NonNullable<PracticesProgramItem["icon"]>, ReactNode> = {
  wind: <IconWaves className={s.practicesProgramIconSvg} />,
  eye: <IconEye className={s.practicesProgramIconSvg} />,
  star: <IconSun className={s.practicesProgramIconSvg} />,
  book: <IconActivity className={s.practicesProgramIconSvg} />,
};

function programIcon(icon?: PracticesProgramItem["icon"]) {
  if (!icon) return <IconWaves className={s.practicesProgramIconSvg} />;
  return PROGRAM_ICONS[icon];
}

export type PracticesWebCatalogProps = {
  todayLabel: string;
  progressOfLabel: string;
  categoriesAriaLabel: string;
  todayItems: PracticesTodayItem[];
  tabs: PracticesCatalogTab[];
  activeTabId: string;
  onTabChange: (tabId: string) => void;
  programs: PracticesProgramItem[];
  toolbar?: ReactNode;
};

export function PracticesWebCatalog({
  todayLabel,
  progressOfLabel,
  categoriesAriaLabel,
  todayItems,
  tabs,
  activeTabId,
  onTabChange,
  programs,
  toolbar,
}: PracticesWebCatalogProps) {
  const completedCount = todayItems.filter((item) => item.completed).length;

  return (
    <div className={s.practicesCatalogRoot}>
      {toolbar}

      <section className={s.practicesTodayCard} aria-labelledby="practices-today-heading">
        <header className={s.practicesTodayHeader}>
          <h2 id="practices-today-heading" className={s.practicesTodayEyebrow}>
            {todayLabel}
          </h2>
          <span className={s.practicesTodayProgress}>
            {completedCount} {progressOfLabel} {todayItems.length || 0}
          </span>
        </header>
        <ul className={s.practicesTodayList}>
          {todayItems.map((item) => (
            <li
              key={item.id}
              className={`${s.practicesTodayRow} ${item.completed ? s.practicesTodayRowDone : ""}`}
            >
              <DsCheckbox checked={item.completed} disabled aria-label={item.title} />
              <span className={s.practicesCategoryPill}>{item.category}</span>
              <span className={s.practicesTodayTitle}>{item.title}</span>
              <span className={s.practicesTodayDuration}>{item.durationLabel}</span>
            </li>
          ))}
        </ul>
      </section>

      <nav className={s.practicesTabs} aria-label={categoriesAriaLabel}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`${s.practicesTab} ${activeTabId === tab.id ? s.practicesTabActive : ""}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className={s.practicesProgramGrid}>
        {programs.map((program) => (
          <Link key={program.id} href={program.href} className={s.practicesProgramCard}>
            <div className={s.practicesProgramHead}>
              <div className={s.practicesProgramTitleRow}>
                {programIcon(program.icon)}
                <h3 className={s.practicesProgramTitle}>{program.title}</h3>
              </div>
              <span className={s.practicesProgramDuration}>{program.durationLabel}</span>
            </div>
            <p className={s.practicesProgramBody}>{program.description}</p>
            {program.sessionsLabel ? (
              <p className={s.practicesProgramMeta}>{program.sessionsLabel}</p>
            ) : null}
          </Link>
        ))}
      </div>
    </div>
  );
}
