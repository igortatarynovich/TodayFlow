"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DsButton } from "@/design-system";
import { postJson } from "@/lib/api";
import {
  hasGuestBirthDate,
  hasGuestName,
  patchGuestProfileDraft,
  readGuestProfileDraft,
  VALUE_FIRST_PATHS,
} from "@/lib/guestProfileDraft";
import type { NatalFactsApiResponse } from "@/lib/natalFacts";
import { sunSignFromIsoDate } from "@/lib/sunSignFromDate";
import { ValueFirstOnboardingShell } from "@/components/onboarding/valueFirst/ValueFirstOnboardingShell";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

type LifePathResponse = {
  output: { number: number };
};

export default function OnboardingBirthPage() {
  const router = useRouter();
  const [birthDate, setBirthDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!hasGuestName()) {
      router.replace(VALUE_FIRST_PATHS.welcome);
      return;
    }
    const draft = readGuestProfileDraft();
    if (draft?.birth_date) setBirthDate(draft.birth_date);
    if (hasGuestBirthDate(draft) && draft?.preview_seen_at) {
      router.replace(VALUE_FIRST_PATHS.preview);
    }
  }, [router]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!birthDate) {
      setError(copy.birth.errorEmpty);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const draft = readGuestProfileDraft();
      const sunSign = sunSignFromIsoDate(birthDate);
      let lifePath: number | null = null;
      try {
        const lp = await postJson<LifePathResponse>("/numerology/life-path", { birth_date: birthDate });
        lifePath = lp.output?.number ?? null;
      } catch {
        lifePath = null;
      }

      let natalFacts = null;
      let resolvedSun = sunSign;
      try {
        const nf = await postJson<NatalFactsApiResponse>("/profile/natal-facts", {
          birth_date: birthDate,
          birth_time: draft?.time_unknown === false ? draft.birth_time : null,
          time_unknown: draft?.time_unknown ?? true,
          location_name: draft?.location_name,
          latitude: draft?.latitude,
          longitude: draft?.longitude,
          display_name: draft?.first_name || null,
        });
        natalFacts = nf.natal_facts;
        const sunFromFacts = natalFacts?.planets?.find((p) => p.id === "sun")?.sign;
        if (sunFromFacts) {
          resolvedSun = sunFromFacts.charAt(0).toUpperCase() + sunFromFacts.slice(1);
        }
      } catch {
        natalFacts = null;
      }

      patchGuestProfileDraft({
        birth_date: birthDate,
        sun_sign: resolvedSun,
        life_path: lifePath,
        natal_facts: natalFacts,
      });
      router.push(VALUE_FIRST_PATHS.preview);
    } catch {
      setError("Не удалось посчитать базу — проверь дату и попробуй ещё раз.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ValueFirstOnboardingShell
      step={2}
      turnId="birth_date"
      title={copy.birth.title}
      lead={copy.birth.lead}
      backHref={VALUE_FIRST_PATHS.welcome}
    >
      <form onSubmit={(e) => void onSubmit(e)}>
        <input
          type="date"
          className={styles.field}
          value={birthDate}
          onChange={(e) => {
            setBirthDate(e.target.value);
            setError(null);
          }}
          data-testid="onboarding-birth-input"
        />
        {error ? <p className={styles.error}>{error}</p> : null}
        <div className={styles.ctaRow}>
          <DsButton variant="primary" type="submit" disabled={loading} data-testid="onboarding-birth-continue">
            {loading ? copy.birth.loading : copy.birth.cta}
          </DsButton>
        </div>
      </form>
    </ValueFirstOnboardingShell>
  );
}
