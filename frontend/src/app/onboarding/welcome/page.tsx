"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DsButton } from "@/design-system";
import {
  beginGuestOnboardingSession,
  hasGuestName,
  patchGuestProfileDraft,
  VALUE_FIRST_PATHS,
} from "@/lib/guestProfileDraft";
import { ValueFirstOnboardingShell } from "@/components/onboarding/valueFirst/ValueFirstOnboardingShell";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

function WelcomeForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams.get("fresh") === "1") {
      beginGuestOnboardingSession();
      router.replace(VALUE_FIRST_PATHS.welcome);
      return;
    }

    if (hasGuestName()) {
      const draft = patchGuestProfileDraft({});
      if (draft.first_name) setName(draft.first_name);
    }
  }, [router, searchParams]);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError(copy.welcome.errorEmpty);
      return;
    }
    patchGuestProfileDraft({ first_name: trimmed });
    router.push(VALUE_FIRST_PATHS.birth);
  };

  return (
    <ValueFirstOnboardingShell
      step={1}
      turnId="welcome_name"
      title={copy.welcome.title}
      lead={copy.welcome.lead}
      backHref="/"
    >
      <form onSubmit={onSubmit}>
        <input
          className={styles.field}
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError(null);
          }}
          placeholder={copy.welcome.placeholder}
          autoComplete="given-name"
          data-testid="onboarding-name-input"
        />
        {error ? <p className={styles.error}>{error}</p> : null}
        <div className={styles.ctaRow}>
          <DsButton variant="primary" type="submit" data-testid="onboarding-name-continue">
            {copy.welcome.cta}
          </DsButton>
        </div>
      </form>
    </ValueFirstOnboardingShell>
  );
}

export default function OnboardingWelcomePage() {
  return (
    <Suspense fallback={null}>
      <WelcomeForm />
    </Suspense>
  );
}
