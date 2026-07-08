"use client";

import type { ReactNode } from "react";
import { PROFILE_PORTRAIT_SECTION_COPY as copy } from "@/lib/profilePortraitSection";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";
import quickMapStyles from "@/components/profile/quickMap/profileQuickMap.module.css";
import v0Styles from "@/components/profile/v0/profileV0.module.css";

type Props = {
  className?: string;
  variant?: "editorial" | "quickMap" | "v0";
  children: ReactNode;
};

export function ProfilePortraitSection({ className, variant = "editorial", children }: Props) {
  const bandClass =
    variant === "quickMap"
      ? `${quickMapStyles.quickMapPortraitBand} ${className ?? ""}`.trim()
      : variant === "v0"
        ? `${v0Styles.portraitSectionBand} ${className ?? ""}`.trim()
        : `${editorialStyles.portraitSectionBand} ${className ?? ""}`.trim();

  const headerClass =
    variant === "quickMap"
      ? quickMapStyles.quickMapPortraitBandHeader
      : variant === "v0"
        ? v0Styles.portraitBandHeader
        : editorialStyles.portraitBandHeader;
  const kickerClass =
    variant === "quickMap"
      ? quickMapStyles.quickMapPortraitKicker
      : variant === "v0"
        ? v0Styles.portraitKicker
        : editorialStyles.portraitKicker;
  const leadClass =
    variant === "quickMap"
      ? quickMapStyles.quickMapPortraitLead
      : variant === "v0"
        ? v0Styles.portraitLead
        : editorialStyles.portraitLead;

  return (
    <section className={bandClass} data-testid="profile-portrait-section" aria-label={copy.sectionLabel}>
      <header className={headerClass}>
        <p className={kickerClass}>{copy.sectionLabel}</p>
        <p className={leadClass}>{copy.sectionLead}</p>
      </header>
      {children}
    </section>
  );
}
