import type { ReactNode } from "react";
import { DsCard } from "@/design-system/primitives/DsCard";
import { DsBody, DsCaption, DsEyebrow, DsHeadline } from "@/design-system/primitives/DsTypography";
import { DsFab } from "@/design-system/primitives/DsFab";
import { DsChipCluster } from "@/design-system/primitives/DsChip";
import { joinClass } from "@/design-system/utils/joinClass";
import c from "@/design-system/compositions/dsCompositions.module.css";

type DsHeroBlockProps = {
  eyebrow?: string;
  title: string;
  body?: string;
  chips?: ReactNode;
  bleed?: ReactNode;
  fab?: ReactNode;
  onOpen?: () => void;
  className?: string;
  testId?: string;
};

/** Composition: Surface(card) + text + bleed visual + fab/chips — no private skin. */
export function DsHeroBlock({
  eyebrow,
  title,
  body,
  chips,
  bleed,
  fab,
  onOpen,
  className,
  testId,
}: DsHeroBlockProps) {
  return (
    <DsCard
      tone="glass"
      size="compact"
      as={onOpen ? "button" : "article"}
      onClick={onOpen}
      className={joinClass(c.heroInner, className)}
      testId={testId}
    >
      {bleed ? <div className={c.heroBleed}>{bleed}</div> : null}
      <div className={c.heroCopy}>
        {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
        <DsHeadline>{title}</DsHeadline>
        {body ? <DsBody size="sm">{body}</DsBody> : null}
      </div>
      {(chips || fab) && (
        <div className={c.heroFooter}>
          {chips ? <DsChipCluster>{chips}</DsChipCluster> : <span />}
          {fab}
        </div>
      )}
    </DsCard>
  );
}

export function DsHeroFabArrow(props: { onClick?: () => void; ariaLabel: string; testId?: string }) {
  return (
    <DsFab ariaLabel={props.ariaLabel} onClick={props.onClick} size="sm" testId={props.testId}>
      →
    </DsFab>
  );
}

type DsWindowCardProps = {
  title?: string;
  startLabel: string;
  endLabel: string;
  spectrum: ReactNode;
  className?: string;
  testId?: string;
};

export function DsWindowCard({
  title,
  startLabel,
  endLabel,
  spectrum,
  className,
  testId,
}: DsWindowCardProps) {
  return (
    <DsCard tone="glass" size="compact" className={joinClass(c.stack, className)} testId={testId}>
      {title ? <DsCaption>{title}</DsCaption> : null}
      <div className={c.windowTimes}>
        <DsBody size="sm">{startLabel}</DsBody>
        <DsBody size="sm">{endLabel}</DsBody>
      </div>
      {spectrum}
    </DsCard>
  );
}

type DsMetricCardProps = {
  value: string;
  label?: string;
  meter?: ReactNode;
  className?: string;
  testId?: string;
};

export function DsMetricCard({ value, label, meter, className, testId }: DsMetricCardProps) {
  return (
    <DsCard tone="glass" size="compact" className={joinClass(c.metricRow, className)} testId={testId}>
      <div>
        <DsHeadline>{value}</DsHeadline>
        {label ? <DsCaption>{label}</DsCaption> : null}
      </div>
      {meter}
    </DsCard>
  );
}

type DsActionCardProps = {
  title: string;
  body?: string;
  action: ReactNode;
  className?: string;
  testId?: string;
};

export function DsActionCard({ title, body, action, className, testId }: DsActionCardProps) {
  return (
    <DsCard tone="glass" size="compact" className={joinClass(c.actionCenter, className)} testId={testId}>
      <DsHeadline>{title}</DsHeadline>
      {body ? <DsBody size="sm">{body}</DsBody> : null}
      {action}
    </DsCard>
  );
}

type DsListRowProps = {
  leading?: ReactNode;
  title: string;
  subtitle?: string;
  onClick?: () => void;
  className?: string;
  testId?: string;
};

export function DsListRow({ leading, title, subtitle, onClick, className, testId }: DsListRowProps) {
  const Comp = onClick ? "button" : "div";
  return (
    <Comp
      type={onClick ? "button" : undefined}
      className={joinClass(c.listRow, className)}
      onClick={onClick}
      data-testid={testId}
    >
      {leading}
      <span className={c.listRowBody}>
        <DsBody size="sm">{title}</DsBody>
        {subtitle ? <DsCaption>{subtitle}</DsCaption> : null}
      </span>
      {onClick ? (
        <span className={c.listRowChevron} aria-hidden>
          ›
        </span>
      ) : null}
    </Comp>
  );
}
