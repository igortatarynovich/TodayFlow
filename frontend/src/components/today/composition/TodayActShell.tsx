"use client";

import type { ReactNode } from "react";
import {
  ProfileAtmosphere,
  type ProfileAtmosphereMotif,
} from "@/components/profile/v2/ProfileAtmosphere";
import { DsBody, DsEyebrow, DsPill } from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
import { joinClass } from "@/design-system/utils/joinClass";

/**
 * Today ActShell — Wave 1 layout contract.
 *
 * One full-bleed act width + one page gutter. Do not wrap children in extra
 * max-width / padding shells (readable measure on text lines only is OK).
 * Future natal / media modules: stack visual → text inside this shell only.
 *
 * Form Kit: layout classes live in design-system (FOUNDATION_UI §15.8).
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
  /** Media / plate above the act title (visual → text). */
  visual?: ReactNode;
  /** Reserved Wave 2 slot above body (e.g. verdict strip). */
  slotBefore?: ReactNode;
  /** Reserved Wave 2 slot below body (e.g. tap widget). */
  slotAfter?: ReactNode;
  testId?: string;
  className?: string;
  /** Stable DOM id for act nav anchors (`today-act-1` …). */
  id?: string;
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
  visual = null,
  slotBefore = null,
  slotAfter = null,
  testId,
  className = "",
  id,
}: TodayActShellProps) {
  const actId =
    id ??
    (step != null && String(step).trim() !== ""
      ? `today-act-${String(step).trim()}`
      : undefined);

  return (
    <section
      id={actId}
      className={joinClass(
        layout.actShell,
        layout.actScreen,
        gutter === "none" ? layout.actGutterNone : layout.actGutterPage,
        bridge ? layout.actBridge : null,
        className,
      )}
      data-testid={testId}
      data-today-act-shell="true"
      data-act-gutter={gutter}
      data-act-accent={accent}
      data-act-step={step != null ? String(step) : undefined}
    >
      {motif ? <ProfileAtmosphere motif={motif} /> : null}
      {visual ? <div className={layout.actVisual}>{visual}</div> : null}
      {title ? (
        <header className={layout.actHeader}>
          <DsEyebrow>
            {step != null ? <DsPill>{step}</DsPill> : null}
            {step != null ? " " : null}
            {title}
          </DsEyebrow>
          {lead ? <DsBody size="sm" muted>{lead}</DsBody> : null}
        </header>
      ) : null}
      {slotBefore}
      {children ? <div className={layout.actBody}>{children}</div> : null}
      {slotAfter}
    </section>
  );
}
