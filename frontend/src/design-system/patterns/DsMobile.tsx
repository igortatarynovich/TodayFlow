import Link from "next/link";
import type { ReactNode } from "react";
import { DsBody, DsEyebrow } from "@/design-system/primitives/DsTypography";
import { joinClass } from "@/design-system/utils/joinClass";
import m from "@/design-system/patterns/dsMobile.module.css";

export type DsRitualGateKind = "tarot" | "number";

export function DsRitualGateSection({
  eyebrow,
  hint,
  children,
  className,
  testId,
}: {
  eyebrow?: string;
  hint?: string;
  children: ReactNode;
  className?: string;
  testId?: string;
}) {
  return (
    <section className={joinClass(m.ritualSection, className)} data-testid={testId ?? "ds-ritual-gate-section"}>
      {eyebrow || hint ? (
        <div className={m.ritualSectionHead}>
          {eyebrow ? <DsEyebrow className={m.ritualEyebrow}>{eyebrow}</DsEyebrow> : null}
          {hint ? (
            <DsBody size="sm" className={m.ritualHint}>
              {hint}
            </DsBody>
          ) : null}
        </div>
      ) : null}
      <div className={m.ritualGateRow}>{children}</div>
    </section>
  );
}

export function DsRitualGate({
  kind,
  title,
  hint,
  step,
  body,
  cta,
  onClick,
  testId,
}: {
  kind: DsRitualGateKind;
  title: string;
  hint?: string;
  step?: string;
  body?: string;
  cta?: string;
  onClick?: () => void;
  testId?: string;
}) {
  const actionLabel = cta ?? hint ?? "";
  return (
    <button
      type="button"
      className={joinClass(m.ritualGate, kind === "tarot" ? m.ritualGateTarot : m.ritualGateNumber)}
      onClick={onClick}
      data-testid={testId}
    >
      {step ? <span className={m.gateStep}>{step}</span> : null}
      {kind === "tarot" && !step ? (
        <span className={m.tarotSilhouette} aria-hidden />
      ) : null}
      {kind === "number" && !step ? (
        <span className={m.numberTiles} aria-hidden>
          {[0, 1, 2].map((i) => (
            <span key={i} className={m.numberTile}>
              ?
            </span>
          ))}
        </span>
      ) : null}
      <span className={m.gateTitle}>{title}</span>
      {body ? <span className={m.gateBody}>{body}</span> : null}
      {actionLabel ? <span className={m.gateHint}>{actionLabel}</span> : null}
    </button>
  );
}

export function DsPulseCard({
  label,
  value,
  hint,
  className,
}: {
  label: string;
  value: string;
  hint?: string;
  className?: string;
}) {
  return (
    <div className={joinClass(m.pulseCard, className)} data-testid="ds-pulse-card">
      <p className={m.pulseLabel}>{label}</p>
      <p className={m.pulseValue}>{value}</p>
      {hint ? <p className={m.pulseHint}>{hint}</p> : null}
    </div>
  );
}

export function DsInsightRow({
  label,
  title,
  body,
  className,
  testId,
}: {
  label?: string;
  title: string;
  body?: string;
  className?: string;
  testId?: string;
}) {
  return (
    <article className={joinClass(m.insightRow, className)} data-testid={testId}>
      {label ? <p className={m.insightRowLabel}>{label}</p> : null}
      <h3 className={m.insightRowTitle}>{title}</h3>
      {body ? <p className={m.insightRowBody}>{body}</p> : null}
    </article>
  );
}

export function DsMobileTabBar({
  items,
  activeHref,
}: {
  items: Array<{ href: string; label: string; icon: ReactNode }>;
  activeHref: string;
}) {
  return (
    <nav className={m.tabBar} aria-label="Основная навигация">
      {items.map((item) => {
        const active = activeHref === item.href || activeHref.startsWith(`${item.href}/`);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={joinClass(m.tabItem, active ? m.tabItemActive : null)}
          >
            <span className={m.tabIcon}>{item.icon}</span>
            <span className={m.tabLabel}>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

export function DsCtaBar({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={joinClass(m.ctaBar, className)}>{children}</div>;
}

export function DsMobileShell({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={joinClass(m.mobileShell, className)}>{children}</div>;
}
