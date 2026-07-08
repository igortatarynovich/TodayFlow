"use client";

import { useEffect, useMemo, useState } from "react";
import { PROFILE_MAPS_PREVIEW_COPY as copy, buildProfileLivingObservation, buildProfileMapsLocalObservation } from "@/lib/profileMapsPreview";
import { fetchCycleMapObservation } from "@/lib/cycleMapModel";
import { ProfileMapsPreviewBlock } from "@/components/profile/ProfileMapsPreviewBlock";
import { ProfileMyDaysBlock } from "@/components/profile/ProfileMyDaysBlock";
import { useAuth } from "@/lib/useAuth";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";
import quickMapStyles from "@/components/profile/quickMap/profileQuickMap.module.css";

type Props = {
  className?: string;
  variant?: "editorial" | "quickMap";
  observationLine?: string | null;
  /** Pre-merged living + CUM line from profile page (Quick Map). */
  livingObservation?: string | null;
  showMyDays?: boolean;
};

export function ProfileLivingMapsSection({
  className,
  variant = "editorial",
  observationLine,
  livingObservation,
  showMyDays = false,
}: Props) {
  const { isAuthenticated } = useAuth();
  const styles = variant === "quickMap" ? quickMapStyles : editorialStyles;
  const [cycleObservation, setCycleObservation] = useState<string | null>(null);

  const localObservation = useMemo(() => buildProfileMapsLocalObservation(), []);

  useEffect(() => {
    if (!isAuthenticated) {
      setCycleObservation(null);
      return;
    }
    const todayISO = new Date().toISOString().split("T")[0];
    let cancelled = false;
    fetchCycleMapObservation(todayISO).then((line) => {
      if (!cancelled) setCycleObservation(line);
    });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  const resolvedObservation =
    observationLine ??
    livingObservation ??
    buildProfileLivingObservation({ cycleObservation }) ??
    localObservation;
  const bandClass =
    variant === "quickMap"
      ? `${quickMapStyles.quickMapLivingMapsBand} ${className ?? ""}`.trim()
      : `${editorialStyles.livingMapsSectionBand} ${className ?? ""}`.trim();

  return (
    <div className={bandClass} data-testid="profile-living-maps-section">
      <div
        className={variant === "quickMap" ? quickMapStyles.quickMapSectionDivider : editorialStyles.sectionDivider}
        aria-hidden="true"
      />
      <header className={variant === "quickMap" ? quickMapStyles.quickMapLivingMapsBandHeader : editorialStyles.livingMapsBandHeader}>
        <p className={variant === "quickMap" ? quickMapStyles.quickMapLivingMapsKicker : editorialStyles.livingMapsKicker}>
          {copy.sectionLabel}
        </p>
        <p className={variant === "quickMap" ? quickMapStyles.quickMapLivingMapsLead : editorialStyles.livingMapsLead}>
          {copy.sectionLead}
        </p>
      </header>
      {showMyDays ? <ProfileMyDaysBlock /> : null}
      <ProfileMapsPreviewBlock
        variant={variant}
        observationLine={resolvedObservation}
        showSectionLabel={false}
      />
    </div>
  );
}
