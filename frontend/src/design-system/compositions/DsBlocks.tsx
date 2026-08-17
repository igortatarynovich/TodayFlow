"use client";

import { useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { DsButton } from "@/design-system/primitives/DsButton";
import { DsCard } from "@/design-system/primitives/DsCard";
import type { DsSurfaceTone } from "@/design-system/primitives/DsSurface";
import { DsBody, DsCaption, DsDisplayTitle, DsEyebrow, DsHeadline, DsSectionTitle } from "@/design-system/primitives/DsTypography";
import { DsFab } from "@/design-system/primitives/DsFab";
import { DsChipCluster } from "@/design-system/primitives/DsChip";
import { DsStarDivider } from "@/design-system/primitives/DsStarDivider";
import { joinClass } from "@/design-system/utils/joinClass";
import c from "@/design-system/compositions/dsCompositions.module.css";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsHeroBlockProps = {
  eyebrow?: string;
  title: string;
  body?: string;
  /** Optional quiet line under body (e.g. lunar caption — not an uppercase eyebrow). */
  detail?: string;
  chips?: ReactNode;
  /** Between copy and chips (sky weather art — not nested in the title). */
  afterCopy?: ReactNode;
  bleed?: ReactNode;
  /** Layout class for bleed wrapper (e.g. cropped moon vs small asset). */
  bleedClassName?: string;
  fab?: ReactNode;
  /** Kit hero often sits light over atmosphere — default glass. */
  tone?: DsSurfaceTone;
  /** `feature` = dominant first viewport hero (display title, room for bleed). */
  size?: "default" | "feature";
  onOpen?: () => void;
  className?: string;
  testId?: string;
};

/** Kit Hero block: large copy + optional bleed visual + fab/chips. */
export function DsHeroBlock({
  eyebrow,
  title,
  body,
  detail,
  chips,
  afterCopy,
  bleed,
  bleedClassName,
  fab,
  tone = "glass",
  size = "default",
  onOpen,
  className,
  testId,
}: DsHeroBlockProps) {
  const feature = size === "feature";
  // FAB is already a button — wrapping the hero too nested-buttons iOS and
  // blocks first-screen scroll when the drag starts on the hero.
  const asButton = Boolean(onOpen) && !afterCopy && !fab;
  return (
    <DsCard
      tone={tone}
      size="default"
      as={asButton ? "button" : "article"}
      onClick={asButton ? onOpen : undefined}
      className={joinClass(c.heroInner, feature ? c.heroFeature : null, className)}
      testId={testId}
    >
      {bleed ? <div className={joinClass(c.heroBleed, bleedClassName)}>{bleed}</div> : null}
      <div className={joinClass(c.heroCopy, feature ? c.heroCopyFeature : null)}>
        {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
        {feature ? <DsDisplayTitle size="lg">{title}</DsDisplayTitle> : <DsHeadline>{title}</DsHeadline>}
        {body ? <DsBody size={feature ? "lg" : "sm"}>{body}</DsBody> : null}
        {detail ? (
          <DsBody size="sm" tone="quiet">
            {detail}
          </DsBody>
        ) : null}
      </div>
      {afterCopy ? <div className={c.heroAfterCopy}>{afterCopy}</div> : null}
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

type DsSectionHeaderProps = {
  title: string;
  eyebrow?: string;
  /** Optional trailing control (e.g. ghost “View all” button). */
  action?: ReactNode;
  withDivider?: boolean;
  className?: string;
  testId?: string;
};

/**
 * Form Kit section header — composition only (typography + optional action + star divider).
 * Not a visual primitive; no own skin beyond layout gap.
 */
export function DsSectionHeader({
  title,
  eyebrow,
  action,
  withDivider = false,
  className,
  testId,
}: DsSectionHeaderProps) {
  return (
    <header className={joinClass(c.sectionHeader, className)} data-testid={testId}>
      <div className={c.sectionHeaderRow}>
        <div className={c.sectionHeaderCopy}>
          {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
          <DsSectionTitle>{title}</DsSectionTitle>
        </div>
        {action ? <div className={c.sectionHeaderAction}>{action}</div> : null}
      </div>
      {withDivider ? <DsStarDivider /> : null}
    </header>
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
  /** Optional — omit when the CTA itself is the only message (no title dupe). */
  title?: string;
  body?: string;
  action: ReactNode;
  tone?: DsSurfaceTone;
  /** `bar` = compact horizontal CTA strip; `center` = kit poster. */
  layout?: "center" | "bar";
  className?: string;
  testId?: string;
};

/** Kit Action / CTA block: centered prompt + button/fab, or compact bar. */
export function DsActionCard({
  title,
  body,
  action,
  tone = "accent",
  layout = "center",
  className,
  testId,
}: DsActionCardProps) {
  return (
    <DsCard
      tone={tone}
      size={layout === "bar" ? "compact" : "default"}
      className={joinClass(layout === "bar" ? c.actionBar : c.actionCenter, className)}
      testId={testId}
    >
      {title || body ? (
        <div className={layout === "bar" ? c.actionBarCopy : undefined}>
          {title ? <DsHeadline>{title}</DsHeadline> : null}
          {body ? <DsBody size="sm">{body}</DsBody> : null}
        </div>
      ) : null}
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
  body?: string;
  kicker?: string;
  closeLabel: string;
  onClose: () => void;
  footer?: ReactNode;
  children?: ReactNode;
  testId?: string;
};

/**
 * Modal / detail sheet — always `overlay` (opaque). Never glass:
 * stacked imagery must not show through body text.
 * Portaled to `document.body` so ScreenFlow transform / container-type
 * cannot trap `position: fixed`.
 */
export function DsOverlaySheet({
  titleId,
  title,
  body,
  kicker,
  closeLabel,
  onClose,
  footer,
  children,
  testId = "ds-overlay-sheet",
}: DsOverlaySheetProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  if (!mounted) return null;

  return createPortal(
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      data-testid={testId}
      className={fk.overlayRoot}
      onPointerDown={(event) => event.stopPropagation()}
    >
      <button type="button" className={fk.overlayScrim} aria-label={closeLabel} onClick={onClose} />
      <DsCard tone="overlay" size="default" className={joinClass(fk.overlaySheet, c.stack)} testId={`${testId}-panel`}>
        {kicker ? <DsEyebrow>{kicker}</DsEyebrow> : null}
        <h3 id={titleId}>
          <DsBody>{title}</DsBody>
        </h3>
        {body ? <DsBody size="sm">{body}</DsBody> : null}
        {children}
        {footer}
        <DsButton variant="secondary" onClick={onClose}>
          {closeLabel}
        </DsButton>
      </DsCard>
    </div>,
    document.body,
  );
}
