import type { ReactNode } from "react";
import l from "@/design-system/layouts/dsLayouts.module.css";

export function DsMarketingPage({
  nav,
  children,
  footer,
  "data-landing-page": dataLandingPage,
}: {
  nav: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  "data-landing-page"?: boolean | string;
}) {
  return (
    <div className={l.page} data-landing-page={dataLandingPage ? "" : undefined}>
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
  id,
  screen = false,
  tone,
  "aria-labelledby": ariaLabelledBy,
  "data-landing-screen": dataLandingScreen,
}: {
  children: ReactNode;
  tight?: boolean;
  testId?: string;
  id?: string;
  /** Full-viewport marketing block (min 100dvh under sticky nav). */
  screen?: boolean;
  tone?: "default" | "hero" | "muted";
  "aria-labelledby"?: string;
  /** Landing scenario screen id (Plan v4). */
  "data-landing-screen"?: string;
}) {
  const toneClass =
    tone === "hero" ? l.sectionHero : tone === "muted" ? l.sectionMuted : "";
  return (
    <section
      id={id}
      className={`${l.section} ${tight ? l.sectionTight : ""} ${screen ? l.sectionScreen : ""} ${toneClass}`.trim()}
      data-testid={testId}
      data-landing-screen={dataLandingScreen}
      aria-labelledby={ariaLabelledBy}
    >
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
  const hasRail = Boolean(rail) && !fullMain;
  return (
    <div className={l.appShell} data-testid={testId}>
      {sidebar}
      <div className={`${l.appBody} ${hasRail ? l.appBodyWithRail : ""}`.trim()}>
        <div className={`${l.appMain} ${fullMain ? l.appMainFull : ""}`.trim()}>{main}</div>
        {hasRail ? <aside className={l.appRail}>{rail}</aside> : null}
      </div>
    </div>
  );
}

export function DsCompositionSlot({ children }: { children: ReactNode }) {
  return <div className={l.compositionSlot}>{children}</div>;
}
