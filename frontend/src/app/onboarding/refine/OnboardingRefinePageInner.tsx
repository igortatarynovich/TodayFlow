"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DsButton } from "@/design-system";
import { CityAutocompleteInput } from "@/components/CityAutocompleteInput";
import { claimGuestProfileAfterAuth } from "@/lib/claimGuestProfile";
import { useAuth } from "@/lib/useAuth";
import {
  hasGuestPreview,
  patchGuestProfileDraft,
  readGuestProfileDraft,
  VALUE_FIRST_PATHS,
} from "@/lib/guestProfileDraft";
import { ValueFirstOnboardingShell } from "@/components/onboarding/valueFirst/ValueFirstOnboardingShell";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

export default function OnboardingRefinePageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const afterSave = searchParams.get("after") === "save";
  const { isAuthenticated } = useAuth();
  const draft = readGuestProfileDraft();

  const [locationName, setLocationName] = useState(draft?.location_name || "");
  const [latitude, setLatitude] = useState<number | null>(draft?.latitude ?? null);
  const [longitude, setLongitude] = useState<number | null>(draft?.longitude ?? null);
  const [birthTime, setBirthTime] = useState(draft?.birth_time || "");
  const [timeUnknown, setTimeUnknown] = useState(draft?.time_unknown ?? true);
  const [error, setError] = useState<string | null>(null);
  const [claiming, setClaiming] = useState(false);

  useEffect(() => {
    if (!hasGuestPreview()) {
      router.replace(VALUE_FIRST_PATHS.welcome);
    }
  }, [router]);

  const persistAndContinue = async (skipLocation: boolean) => {
    patchGuestProfileDraft({
      location_name: skipLocation ? null : locationName.trim() || null,
      latitude: skipLocation ? null : latitude,
      longitude: skipLocation ? null : longitude,
      birth_time: timeUnknown ? null : birthTime || null,
      time_unknown: timeUnknown,
    });

    if (afterSave && isAuthenticated) {
      setClaiming(true);
      try {
        const result = await claimGuestProfileAfterAuth();
        if (result.status === "ready") {
          router.push(result.profilePath);
          return;
        }
        if (result.status === "needs_refine" && !skipLocation && locationName.trim()) {
          router.push(VALUE_FIRST_PATHS.save);
          return;
        }
      } finally {
        setClaiming(false);
      }
    }

    const nextPath = afterSave ? VALUE_FIRST_PATHS.save : VALUE_FIRST_PATHS.firstToday;
    if (!afterSave) {
      patchGuestProfileDraft({ first_today_started_at: new Date().toISOString() });
    }
    router.push(nextPath);
  };

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!locationName.trim()) {
      setError("Выбери город из подсказок — так карта будет точнее.");
      return;
    }
    if (!latitude || !longitude) {
      setError("Выбери город из выпадающего списка, чтобы сохранить координаты.");
      return;
    }
    void persistAndContinue(false);
  };

  return (
    <ValueFirstOnboardingShell
      step={4}
      turnId="refine_optional"
      title={copy.refine.title}
      lead={copy.refine.lead}
      backHref={VALUE_FIRST_PATHS.preview}
    >
      <form onSubmit={onSubmit}>
        <label className={styles.hint}>{copy.refine.placeLabel}</label>
        <CityAutocompleteInput
          value={locationName}
          onChange={(value) => {
            setLocationName(value);
            setLatitude(null);
            setLongitude(null);
            setError(null);
          }}
          onSelect={(item) => {
            setLocationName(item.display_name || item.local_name || item.name);
            setLatitude(item.latitude);
            setLongitude(item.longitude);
            setError(null);
          }}
          placeholder="Город, страна"
          disabled={claiming}
        />
        <label style={{ display: "flex", alignItems: "center", gap: "0.55rem", marginTop: "0.65rem" }}>
          <input
            type="checkbox"
            checked={!timeUnknown}
            onChange={(e) => setTimeUnknown(!e.target.checked)}
            disabled={claiming}
          />
          <span className={styles.hint}>{copy.refine.timeToggle}</span>
        </label>
        {!timeUnknown ? (
          <input
            type="time"
            className={styles.field}
            value={birthTime}
            onChange={(e) => setBirthTime(e.target.value)}
            disabled={claiming}
          />
        ) : null}
        {error ? <p className={styles.error}>{error}</p> : null}
        <div className={styles.ctaRow}>
          <DsButton variant="primary" type="submit" disabled={claiming}>
            {claiming ? "Сохраняем…" : afterSave ? "Продолжить" : copy.refine.cta}
          </DsButton>
          {!afterSave ? (
            <>
              <DsButton variant="secondary" type="button" disabled={claiming} onClick={() => void persistAndContinue(true)}>
                {copy.refine.skipCta}
              </DsButton>
              <Link href={VALUE_FIRST_PATHS.firstToday}>
                <DsButton variant="secondary">{copy.refine.firstTodayLink}</DsButton>
              </Link>
            </>
          ) : (
            <>
              <DsButton variant="secondary" type="button" disabled={claiming} onClick={() => void persistAndContinue(true)}>
                {copy.refine.skipCta}
              </DsButton>
              <Link href={VALUE_FIRST_PATHS.firstToday}>
                <DsButton variant="secondary">{copy.refine.firstTodayLink}</DsButton>
              </Link>
            </>
          )}
        </div>
      </form>
    </ValueFirstOnboardingShell>
  );
}
