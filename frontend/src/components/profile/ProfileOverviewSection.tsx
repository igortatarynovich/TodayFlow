"use client";

import { ProfileOverviewExpandables, type ProfileOverviewExpandablesProps } from "@/components/profile/ProfileOverviewExpandables";
import { ProfileOverviewIntro, type ProfileOverviewIntroProps } from "@/components/profile/ProfileOverviewIntro";
import { ProfileWhatNextCard, type ProfileWhatNextItem } from "@/components/profile/ProfileWhatNextCard";
import { ProfileSurfacePanel } from "@/components/profile/ProfileSurface";

export type ProfileOverviewSectionProps = ProfileOverviewIntroProps &
  ProfileOverviewExpandablesProps & {
    whatNextRoutes: ProfileWhatNextItem[];
    /** Одна нейтральная строка про живой слой без повторения «мало данных» везде */
    livingLayerHint?: string | null;
  };

export function ProfileOverviewSection(props: ProfileOverviewSectionProps) {
  const {
    whatNextRoutes,
    livingLayerHint,
    profileGuidance,
    strengths,
    cautions,
    workingRules,
    ...introProps
  } = props;

  return (
    <>
      <ProfileOverviewIntro {...introProps} />

      <ProfileOverviewExpandables profileGuidance={profileGuidance} strengths={strengths} cautions={cautions} workingRules={workingRules} />

      {livingLayerHint ? (
        <ProfileSurfacePanel eyebrow="Живой слой" panelClass="plain">
          <p className="orbit-body-sm" style={{ margin: 0, color: "#475569", lineHeight: 1.65 }}>
            {livingLayerHint}
          </p>
        </ProfileSurfacePanel>
      ) : null}

      <ProfileWhatNextCard routes={whatNextRoutes} />
    </>
  );
}
