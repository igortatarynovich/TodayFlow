"use client";

import type { ReactNode } from "react";
import {
  ProfileAtmosphere,
  type ProfileAtmosphereMotif,
} from "@/components/profile/v2/ProfileAtmosphere";
import styles from "@/components/today/composition/TodayActShell.module.css";

/**
 * Today ActShell — Wave 1 layout contract.
 *
 * One full-bleed act width + one page gutter. Do not wrap children in extra
 * max-width / padding shells (readable measure on text lines only is OK).
 * Future natal / media modules: stack visual → text inside this shell only.
 *
 * Review checklist: no padding/max-width outside ActShell for Today acts.
 */
export type TodayActShellAccent = "default" | "sky" | "support" | "action";

export type TodayActShellProps = {
  step?: string | number;
  title?: string;
  lead?: string | null;
  accent?: TodayActShellAccent;
  /** page = one mobile gutter; none = edge-to-edge children (hero wash). */
  gutter?: "page" | "none";
  motif?: ProfileAtmosphereMotif | null;
  bridge?: boolean;
  children?: ReactNode;
  /** Reserved Wave 2 slot above body (e.g. verdict strip). */
  slotBefore?: ReactNode;
  /** Reserved Wave 2 slot below body (e.g. tap widget). */
  slotAfter?: ReactNode;
  testId?: string;
  className?: string;
};

export function TodayActShell({
  step,
  title,
  lead = null,
  accent = "default",
  gutter = "page",
  motif = null,
  bridge = false,
  children,
  slotBefore = null,
  slotAfter = null,
  testId,
  className = "",
}: TodayActShellProps) {
  const accentClass =
    accent === "sky"
      ? styles.accentSky
      : accent === "support"
        ? styles.accentSupport
        : accent === "action"
          ? styles.accentAction
          : styles.accentDefault;

  return (
    <section
      className={[
        styles.shell,
        accentClass,
        gutter === "none" ? styles.gutterNone : styles.gutterPage,
        bridge ? styles.bridge : "",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      data-testid={testId}
      data-today-act-shell="true"
      data-act-gutter={gutter}
      data-act-accent={accent}
    >
      {motif ? <ProfileAtmosphere motif={motif} /> : null}
      {title ? (
        <header className={styles.header}>
          <p className={styles.stepIndex}>
            {step != null ? <span className={styles.stepBadge}>{step}</span> : null}
            <span>{title}</span>
          </p>
          {lead ? <p className={styles.lead}>{lead}</p> : null}
        </header>
      ) : null}
      {slotBefore}
      {children ? <div className={styles.body}>{children}</div> : null}
      {slotAfter}
    </section>
  );
}
