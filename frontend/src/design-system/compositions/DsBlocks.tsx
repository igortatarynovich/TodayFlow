import type { ReactNode } from "react";
import { DsButton } from "@/design-system/primitives/DsButton";
import { DsCard } from "@/design-system/primitives/DsCard";
import type { DsSurfaceTone } from "@/design-system/primitives/DsSurface";
import { DsBody, DsCaption, DsEyebrow, DsHeadline } from "@/design-system/primitives/DsTypography";
import { DsFab } from "@/design-system/primitives/DsFab";
import { DsChipCluster } from "@/design-system/primitives/DsChip";
import { joinClass } from "@/design-system/utils/joinClass";
import c from "@/design-system/compositions/dsCompositions.module.css";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsHeroBlockProps = {
  eyebrow?: string;
  title: string;
  body?: string;
  chips?: ReactNode;
  bleed?: ReactNode;
  /** Layout class for bleed wrapper (e.g. cropped moon vs small asset). */
  bleedClassName?: string;
  fab?: ReactNode;
  /** Kit hero often sits light over atmosphere — default glass. */
  tone?: DsSurfaceTone;
  onOpen?: () => void;
  className?: string;
  testId?: string;
};

/** Kit Hero block: large copy + optional bleed visual + fab/chips. */
export function DsHeroBlock({
  eyebrow,
  title,
  body,
  chips,
  bleed,
  bleedClassName,
  fab,
  tone = "glass",
  onOpen,
  className,
  testId,
}: DsHeroBlockProps) {
  return (
    <DsCard
      tone={tone}
      size="default"
      as={onOpen ? "button" : "article"}
      onClick={onOpen}
      className={joinClass(c.heroInner, className)}
      testId={testId}
    >
      {bleed ? <div className={joinClass(c.heroBleed, bleedClassName)}>{bleed}</div> : null}
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
  tone?: DsSurfaceTone;
  className?: string;
  testId?: string;
};

/** Kit Feature / window block: time range + spectrum. */
export function DsWindowCard({
  title,
  startLabel,
  endLabel,
  spectrum,
  tone = "solid",
  className,
  testId,
}: DsWindowCardProps) {
  return (
    <DsCard tone={tone} size="compact" className={joinClass(c.stack, className)} testId={testId}>
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
  tone?: DsSurfaceTone;
  className?: string;
  testId?: string;
};

/** Kit Data / metric block: large value + radial/meter. */
export function DsMetricCard({
  value,
  label,
  meter,
  tone = "solid",
  className,
  testId,
}: DsMetricCardProps) {
  return (
    <DsCard tone={tone} size="compact" className={joinClass(c.metricRow, className)} testId={testId}>
      <div className={c.metricStack}>
        <DsHeadline>{value}</DsHeadline>
        {label ? <DsCaption>{label}</DsCaption> : null}
      </div>
      {meter}
    </DsCard>
  );
}

type DsContentCardProps = {
  eyebrow?: string;
  title?: string;
  body?: string;
  chips?: ReactNode;
  tone?: DsSurfaceTone;
  as?: "div" | "section" | "article" | "button";
  onClick?: () => void;
  className?: string;
  testId?: string;
};

/** Kit Content block: prose + optional chips footer (not a metric/list/hero). */
export function DsContentCard({
  eyebrow,
  title,
  body,
  chips,
  tone = "subtle",
  as = "article",
  onClick,
  className,
  testId,
}: DsContentCardProps) {
  return (
    <DsCard
      tone={tone}
      size="compact"
      as={as}
      onClick={onClick}
      className={joinClass(c.contentBody, className)}
      testId={testId}
    >
      {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
      {title ? <DsBody>{title}</DsBody> : null}
      {body ? <DsBody size="sm">{body}</DsBody> : null}
      {chips ? <div className={c.contentFooter}>{chips}</div> : null}
    </DsCard>
  );
}

type DsActionCardProps = {
  title: string;
  body?: string;
  action: ReactNode;
  tone?: DsSurfaceTone;
  className?: string;
  testId?: string;
};

/** Kit Action / CTA block: centered prompt + button/fab. */
export function DsActionCard({
  title,
  body,
  action,
  tone = "accent",
  className,
  testId,
}: DsActionCardProps) {
  return (
    <DsCard tone={tone} size="default" className={joinClass(c.actionCenter, className)} testId={testId}>
      <DsHeadline>{title}</DsHeadline>
      {body ? <DsBody size="sm">{body}</DsBody> : null}
      {action}
    </DsCard>
  );
}

type DsListPanelProps = {
  title?: string;
  children: ReactNode;
  tone?: DsSurfaceTone;
  className?: string;
  testId?: string;
};

/** Kit list container — rows inside one panel (not a grid of twin cards). */
export function DsListPanel({
  title,
  children,
  tone = "glass",
  className,
  testId,
}: DsListPanelProps) {
  return (
    <DsCard tone={tone} size="compact" className={joinClass(c.listPanel, className)} testId={testId}>
      {title ? <DsEyebrow>{title}</DsEyebrow> : null}
      {children}
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

type DsOverlaySheetProps = {
  titleId: string;
  title: string;
  body: string;
  kicker?: string;
  closeLabel: string;
  onClose: () => void;
  footer?: ReactNode;
  testId?: string;
};

/**
 * Modal / detail sheet — always `overlay` (opaque). Never glass:
 * stacked imagery must not show through body text.
 */
export function DsOverlaySheet({
  titleId,
  title,
  body,
  kicker,
  closeLabel,
  onClose,
  footer,
  testId = "ds-overlay-sheet",
}: DsOverlaySheetProps) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      data-testid={testId}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 40,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
        padding: "var(--tf-ds-space-4, 1rem)",
      }}
    >
      <button type="button" className={fk.overlayScrim} aria-label={closeLabel} onClick={onClose} />
      <DsCard tone="overlay" size="default" className={joinClass(fk.overlaySheet, c.stack)} testId={`${testId}-panel`}>
        {kicker ? <DsEyebrow>{kicker}</DsEyebrow> : null}
        <h3 id={titleId}>
          <DsBody>{title}</DsBody>
        </h3>
        <DsBody size="sm">{body}</DsBody>
        {footer}
        <DsButton variant="secondary" onClick={onClose}>
          {closeLabel}
        </DsButton>
      </DsCard>
    </div>
  );
}
