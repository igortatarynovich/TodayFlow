import type { ComponentType, CSSProperties, ReactNode } from "react";
import { joinClass } from "@/design-system/utils/joinClass";
import {
  IconFlag,
  IconHeart,
  IconHourglass,
  IconMoon,
  IconSparkles,
  IconSun,
  IconArrowDown,
} from "@/design-system/icons/DsIcons";
import c from "@/design-system/primitives/dsCallout.module.css";

/** Tone = type of conclusion (rail + wash). Independent of label. */
export type DsCalloutTone = "insight" | "practice" | "help" | "avoid";

/** Label = life-theme capsule. Independent of tone. */
export type DsCalloutLabel =
  | "main"
  | "attention"
  | "help"
  | "practice"
  | "relations"
  | "money"
  | "thought"
  | "emotions"
  | "next_step";

export type DsCalloutIcon = "sun" | "moon" | "heart" | "spark" | "flag" | "hourglass" | "arrowDown";

export const DS_CALLOUT_LABEL_COPY: Record<DsCalloutLabel, string> = {
  main: "Главное",
  attention: "На что обратить внимание",
  help: "Что поможет",
  practice: "Практика",
  relations: "Отношения",
  money: "Деньги",
  thought: "Мысль",
  emotions: "Эмоции",
  next_step: "Следующий шаг",
};

const TONE_CLASS: Record<DsCalloutTone, string> = {
  insight: c.toneInsight,
  practice: c.tonePractice,
  help: c.toneHelp,
  avoid: c.toneAvoid,
};

const ICON_MAP: Record<DsCalloutIcon, ComponentType<{ className?: string }>> = {
  sun: IconSun,
  moon: IconMoon,
  heart: IconHeart,
  spark: IconSparkles,
  flag: IconFlag,
  hourglass: IconHourglass,
  arrowDown: IconArrowDown,
};

type DsCapsuleProps = {
  label: DsCalloutLabel;
  icon?: DsCalloutIcon;
  className?: string;
  /** Override RU capsule text when needed; prefer catalog keys. */
  children?: ReactNode;
};

/** Theme capsule — uppercase label, optional linear icon. */
export function DsCapsule({ label, icon, className, children }: DsCapsuleProps) {
  const Icon = icon ? ICON_MAP[icon] : null;
  return (
    <span className={joinClass(c.capsule, className)} data-label={label}>
      {Icon ? <Icon className={c.capsuleIcon} /> : null}
      <span className={c.capsuleText}>{children ?? DS_CALLOUT_LABEL_COPY[label]}</span>
    </span>
  );
}

type DsCalloutProps = {
  tone?: DsCalloutTone;
  label?: DsCalloutLabel;
  icon?: DsCalloutIcon;
  /** Large takeaway — one short phrase, not a paragraph. */
  title?: ReactNode;
  children?: ReactNode;
  className?: string;
  style?: CSSProperties;
  testId?: string;
};

/**
 * Semantic insight block — FOUNDATION_UI §5.1.
 * Vertical rail (tone) + optional capsule (label) are independent axes.
 */
export function DsCallout({
  tone = "insight",
  label,
  icon,
  title,
  children,
  className,
  style,
  testId,
}: DsCalloutProps) {
  return (
    <aside
      className={joinClass(c.callout, TONE_CLASS[tone], className)}
      style={style}
      data-tone={tone}
      data-testid={testId ?? "ds-callout"}
    >
      {label ? <DsCapsule label={label} icon={icon} /> : null}
      {title ? <p className={c.title}>{title}</p> : null}
      {children ? <div className={c.body}>{children}</div> : null}
    </aside>
  );
}

type DsQuoteProps = {
  children: ReactNode;
  /** Quiet eyebrow above the quote (e.g. «Сегодня»). */
  kicker?: ReactNode;
  /** Form Kit highlight plate (day wash + large quote mark). */
  highlight?: boolean;
  className?: string;
  testId?: string;
};

/** Large pull-quote — breaks reading rhythm between body paragraphs. */
export function DsQuote({ children, kicker, highlight = false, className, testId }: DsQuoteProps) {
  return (
    <blockquote
      className={joinClass(c.quote, highlight ? c.quoteHighlight : null, className)}
      data-testid={testId ?? "ds-quote"}
    >
      {kicker ? <p className={c.quoteKicker}>{kicker}</p> : null}
      <p className={c.quoteText}>{children}</p>
    </blockquote>
  );
}

/** Emphasize at most 2–3 words — never whole sentences. */
export function DsEmph({ children, className }: { children: ReactNode; className?: string }) {
  return <strong className={joinClass(c.emph, className)}>{children}</strong>;
}
