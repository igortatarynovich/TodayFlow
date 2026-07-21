"use client";

import { useEffect, useState } from "react";
import {
  PROFILE_MAPS_PREVIEW_COPY as copy,
  buildProfileMapsPreviewModel,
  focusMapSeedTone,
  type ProfileMapsPreviewModel,
} from "@/lib/profileMapsPreview";
import {
  buildProfileMapDayStory,
  buildProfileMapsHeatmapPreview,
  type ProfileMapHeatmapId,
} from "@/lib/profileMapsHeatmapPreview";
import { ProfileMapHeatmapMini } from "@/components/profile/ProfileMapHeatmapMini";
import { ProfileHabitWeaveMini } from "@/components/profile/ProfileHabitWeaveMini";
import {
  buildProfileHabitDrillStory,
  fetchProfileHabitWeavePreview,
  type ProfileHabitWeavePreview,
} from "@/lib/profileHabitWeavePreview";
import { ProfileMapExploreGrid } from "@/components/profile/ProfileMapExploreGrid";
import { useAuth } from "@/lib/useAuth";
import editorialStyles from "@/components/profile/editorial/profileEditorial.module.css";
import quickMapStyles from "@/components/profile/quickMap/profileQuickMap.module.css";

type Props = {
  className?: string;
  variant?: "editorial" | "quickMap";
  observationLine?: string | null;
  /** When false, section band supplies the Living Maps label (MP-1). */
  showSectionLabel?: boolean;
};

export function ProfileMapsPreviewBlock({
  className,
  variant = "editorial",
  observationLine,
  showSectionLabel = true,
}: Props) {
  const { isAuthenticated } = useAuth();
  const [model, setModel] = useState<ProfileMapsPreviewModel | null>(null);
  const [heatmapModel, setHeatmapModel] = useState<ReturnType<typeof buildProfileMapsHeatmapPreview> | null>(null);
  const [habitWeave, setHabitWeave] = useState<ProfileHabitWeavePreview | null>(null);
  const [selectedMapId, setSelectedMapId] = useState<ProfileMapHeatmapId | `habit-${number}` | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const labelClass = variant === "quickMap" ? quickMapStyles.quickMapSectionLabel : editorialStyles.sectionLabel;
  const titleClass = variant === "quickMap" ? quickMapStyles.quickMapMapsTitle : editorialStyles.sectionTitle;
  const subtitleClass = variant === "quickMap" ? quickMapStyles.quickMapMapsSubtitle : editorialStyles.sectionSubtitle;
  const leadClass = variant === "quickMap" ? quickMapStyles.quickMapSectionLead : editorialStyles.sectionLead;
  const observationClass = variant === "quickMap" ? quickMapStyles.quickMapMapsObservation : editorialStyles.sectionLead;

  useEffect(() => {
    const todayISO = new Date().toISOString().split("T")[0];
    setModel(buildProfileMapsPreviewModel(7));
    setHeatmapModel(buildProfileMapsHeatmapPreview(todayISO));
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setHabitWeave(null);
      return;
    }
    const todayISO = new Date().toISOString().split("T")[0];
    let cancelled = false;
    fetchProfileHabitWeavePreview(todayISO).then((preview) => {
      if (!cancelled) setHabitWeave(preview);
    });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  if (!model) return null;

  const drillStory = (() => {
    if (!selectedMapId || !selectedDate) return null;
    if (selectedMapId.startsWith("habit-") && habitWeave) {
      const habitId = Number(selectedMapId.replace("habit-", ""));
      return Number.isFinite(habitId)
        ? buildProfileHabitDrillStory(habitWeave, habitId, selectedDate)
        : null;
    }
    if (selectedMapId === "mood" || selectedMapId === "energy" || selectedMapId === "promise") {
      return buildProfileMapDayStory(selectedMapId, selectedDate);
    }
    return null;
  })();

  const habitWeaveStackClass =
    variant === "quickMap" ? quickMapStyles.profileMapHeatmapStack : editorialStyles.profileMapHeatmapStack;
  const habitSectionTitleClass =
    variant === "quickMap" ? quickMapStyles.profileHabitWeaveSectionTitle : editorialStyles.profileHabitWeaveSectionTitle;

  const sectionClass =
    variant === "quickMap"
      ? `${quickMapStyles.quickMapMapsSection} ${className ?? ""}`.trim()
      : `${editorialStyles.section} ${editorialStyles.mapsPreview} ${className ?? ""}`.trim();

  return (
    <section
      className={sectionClass}
      aria-labelledby="profile-maps-preview"
      data-testid="profile-maps-preview"
    >
      {showSectionLabel ? (
        <p id="profile-maps-preview" className={labelClass}>
          {copy.sectionLabel}
        </p>
      ) : null}
      {showSectionLabel ? (
        <p className={titleClass}>{copy.title}</p>
      ) : (
        <p id="profile-maps-preview" className={titleClass}>
          {copy.title}
        </p>
      )}
      <p className={subtitleClass}>{copy.focusMapTitle}</p>
      <p className={leadClass}>
        {model.hasSeeds ? copy.seededLead(model.totalSeeds) : copy.emptyLead}
      </p>
      {observationLine ? (
        <p className={observationClass}>{observationLine}</p>
      ) : null}

      {model.hasSeeds ? (
        <>
          <div
            className={editorialStyles.mapsSeedStrip}
            role="img"
            aria-label={`${model.totalSeeds} закрытых дней на карте фокуса`}
          >
            {model.recentSeeds.map((seed) => {
              const tone = focusMapSeedTone(seed.outcome);
              const toneClass =
                tone === "done"
                  ? editorialStyles.mapsSeedDotDone
                  : tone === "partial"
                    ? editorialStyles.mapsSeedDotPartial
                    : editorialStyles.mapsSeedDotNotDone;
              return (
                <span
                  key={seed.dateISO}
                  className={`${editorialStyles.mapsSeedDot} ${toneClass}`}
                  data-testid={`profile-maps-seed-${seed.dateISO}`}
                  title={seed.dateISO}
                />
              );
            })}
          </div>
          <ul className={editorialStyles.mapsLegend}>
            <li className={editorialStyles.mapsLegendItem}>
              <span className={`${editorialStyles.mapsSeedDot} ${editorialStyles.mapsSeedDotDone}`} aria-hidden />
              {copy.legendDone}
            </li>
            <li className={editorialStyles.mapsLegendItem}>
              <span className={`${editorialStyles.mapsSeedDot} ${editorialStyles.mapsSeedDotPartial}`} aria-hidden />
              {copy.legendPartial}
            </li>
            <li className={editorialStyles.mapsLegendItem}>
              <span className={`${editorialStyles.mapsSeedDot} ${editorialStyles.mapsSeedDotNotDone}`} aria-hidden />
              {copy.legendNotDone}
            </li>
          </ul>
        </>
      ) : (
        <div className={editorialStyles.mapsSeedStripEmpty} aria-hidden>
          {Array.from({ length: 7 }).map((_, index) => (
            <span key={index} className={editorialStyles.mapsSeedDotGhost} />
          ))}
        </div>
      )}

      {heatmapModel?.hasAnyMarks ? (
        <div className={variant === "quickMap" ? quickMapStyles.profileMapHeatmapStack : editorialStyles.profileMapHeatmapStack}>
          <p className={leadClass}>{copy.heatmapsLead}</p>
          {heatmapModel.rows.map((row) => (
            <ProfileMapHeatmapMini
              key={row.id}
              row={row}
              variant={variant}
              selectedDate={selectedMapId === row.id ? selectedDate : null}
              storyLine={
                selectedMapId === row.id
                  ? drillStory ?? (selectedDate ? copy.heatmapDrillEmpty : null)
                  : null
              }
              onSelectDate={(mapId, dateISO) => {
                setSelectedMapId(mapId);
                setSelectedDate(dateISO);
              }}
            />
          ))}
        </div>
      ) : null}

      {habitWeave?.rows.length ? (
        <div className={habitWeaveStackClass} data-testid="profile-habit-weave">
          <p className={habitSectionTitleClass}>{copy.habitWeaveTitle}</p>
          <p className={leadClass}>{copy.habitWeaveLead}</p>
          {habitWeave.rows.map((row) => (
            <ProfileHabitWeaveMini
              key={row.habitId}
              row={row}
              variant={variant}
              selectedDate={selectedMapId === `habit-${row.habitId}` ? selectedDate : null}
              storyLine={
                selectedMapId === `habit-${row.habitId}`
                  ? drillStory ?? (selectedDate ? copy.heatmapDrillEmpty : null)
                  : null
              }
              onSelectDate={(habitId, dateISO) => {
                setSelectedMapId(`habit-${habitId}`);
                setSelectedDate(dateISO);
              }}
            />
          ))}
        </div>
      ) : null}

      <ProfileMapExploreGrid variant={variant} ariaLabel={copy.exploreLabel} />
    </section>
  );
}
