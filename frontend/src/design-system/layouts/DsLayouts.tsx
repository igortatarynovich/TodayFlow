import type { ReactNode } from "react";
import l from "@/design-system/layouts/dsLayouts.module.css";

export function DsMarketingPage({ nav, children, footer }: { nav: ReactNode; children: ReactNode; footer?: ReactNode }) {
  return (
    <div className={l.page}>
      {nav}
      {children}
      {footer}
    </div>
  );
}

export function DsMarketingSection({
  children,
  tight,
  testId,
}: {
  children: ReactNode;
  tight?: boolean;
  testId?: string;
}) {
  return (
    <section className={`${l.section} ${tight ? l.sectionTight : ""}`} data-testid={testId}>
      {children}
    </section>
  );
}

export function DsAppShell({
  sidebar,
  main,
  rail,
  testId,
  fullMain = false,
}: {
  sidebar: ReactNode;
  main: ReactNode;
  rail?: ReactNode;
  testId?: string;
  /** Page draws its own internal columns (profile v2): main spans both tracks. */
  fullMain?: boolean;
}) {
  return (
    <div className={l.appShell} data-testid={testId}>
      {sidebar}
      <div className={l.appBody}>
        <div className={`${l.appMain} ${fullMain ? l.appMainFull : ""}`.trim()}>{main}</div>
        {rail ? <aside className={l.appRail}>{rail}</aside> : null}
      </div>
    </div>
  );
}

export function DsCompositionSlot({ children }: { children: ReactNode }) {
  return <div className={l.compositionSlot}>{children}</div>;
}
