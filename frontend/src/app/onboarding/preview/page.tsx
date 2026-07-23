"use client";

import Link from "next/link";
import { FirstResultScreen } from "@/components/onboarding/valueFirst/FirstResultScreen";
import { OnboardingWebScreen } from "@/components/product-ui/OnboardingWebScreen";
import s from "@/components/product-ui/productWebScreens.module.css";
import { buildOnboardingPreviewModel } from "@/lib/buildOnboardingPreview";
import {
  hasGuestBirthDate,
  hasGuestName,
  patchGuestProfileDraft,
  readGuestProfileDraft,
  VALUE_FIRST_PATHS,
} from "@/lib/guestProfileDraft";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function OnboardingPreviewPage() {
  const router = useRouter();
  const { trackMeaningEvent } = useMeaningRuntime();
  const trackedRef = useRef(false);

  useEffect(() => {
    if (!hasGuestName()) {
      router.replace(VALUE_FIRST_PATHS.welcome);
      return;
    }
    if (!hasGuestBirthDate()) {
      router.replace(VALUE_FIRST_PATHS.birth);
      return;
    }

    const draft = readGuestProfileDraft();
    if (!draft || !hasGuestBirthDate(draft)) return;

    const preview = buildOnboardingPreviewModel(draft);
    patchGuestProfileDraft({
      preview_seen_at: new Date().toISOString(),
      preview_recognition_audit: preview.audit,
    });

    if (trackedRef.current) return;
    trackedRef.current = true;
    trackMeaningEvent({
      event_type: "onboarding_recognition_shown",
      event_source: "onboarding",
      payload: {
        selected_ids: preview.audit.selectedIds,
        candidate_count: preview.audit.candidateCount,
        key_influences: preview.keyInfluences.map((k) => k.id),
      },
      idempotency_key: `onboarding_recognition_shown:${draft.birth_date}:${preview.audit.selectedIds.join(",")}`,
    });
  }, [router, trackMeaningEvent]);

  const draft = readGuestProfileDraft();
  if (!draft || !hasGuestBirthDate(draft)) {
    return null;
  }

  const preview = buildOnboardingPreviewModel(draft);

  return (
    <OnboardingWebScreen step={3} totalSteps={5} title={preview.heroTitle} lead={preview.heroSubtitle}>
      <Link href={VALUE_FIRST_PATHS.birth} className={s.practiceSessionBack}>
        ← Назад
      </Link>
      <div className={styles.shellWide}>
        <FirstResultScreen
          preview={preview}
          saveHref={VALUE_FIRST_PATHS.save}
          refineHref={`${VALUE_FIRST_PATHS.refine}?after=save`}
        />
      </div>
    </OnboardingWebScreen>
  );
}
