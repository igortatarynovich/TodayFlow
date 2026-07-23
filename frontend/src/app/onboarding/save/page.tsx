"use client";

import Link from "next/link";
import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { DsButton } from "@/design-system";
import { postJson } from "@/lib/api";
import { buildAuthHref } from "@/lib/authRedirect";
import { claimGuestProfileAfterAuth, prepareGuestClaimBeforeAuth } from "@/lib/claimGuestProfile";
import { beginAuthSession } from "@/lib/authSession";
import {
  hasGuestPreview,
  patchGuestProfileDraft,
  readGuestProfileDraft,
  VALUE_FIRST_PATHS,
} from "@/lib/guestProfileDraft";
import { hasGuestCompatPair, patchGuestCompatPair } from "@/lib/guestCompatPair";
import { ValueFirstOnboardingShell } from "@/components/onboarding/valueFirst/ValueFirstOnboardingShell";
import { VALUE_FIRST_COPY as copy } from "@/components/onboarding/valueFirst/valueFirstOnboardingCopy";
import styles from "@/components/onboarding/valueFirst/valueFirstOnboarding.module.css";

type EmailSignupResponse = {
  user_id: number;
  email: string;
  pending_email_confirmation?: boolean;
  email_sent?: boolean;
  token?: string;
  access_token?: string;
  refresh_token?: string;
  dev_magic_url?: string;
};

function OnboardingSavePageInner() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [devMagicUrl, setDevMagicUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!hasGuestPreview() && !hasGuestCompatPair()) {
      router.replace(VALUE_FIRST_PATHS.welcome);
      return;
    }
    void prepareGuestClaimBeforeAuth();
  }, [router]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes("@")) {
      setError("Введи корректный email.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      patchGuestProfileDraft({ save_ready_at: new Date().toISOString() });
      patchGuestCompatPair({ save_ready_at: new Date().toISOString() });
      await prepareGuestClaimBeforeAuth();
      const response = await postJson<EmailSignupResponse>("/auth/email-signup", { email: trimmed });

      // Persist drafts to server SoT before magic-link navigation (new tab).
      try {
        const { syncGuestProfilesToServer } = await import("@/lib/guestProfilesSync");
        await syncGuestProfilesToServer();
      } catch {
        /* local draft remains */
      }
      if (response.token || response.access_token) {
        beginAuthSession(response);
        let claimTarget: string | null = null;
        try {
          const claim = await claimGuestProfileAfterAuth();
          if (claim.status === "ready") {
            claimTarget = claim.profilePath;
          } else if (claim.status === "needs_refine") {
            claimTarget = claim.refinePath;
          } else {
            claimTarget = "/profile";
          }
        } catch {
          // Profile claim can fail independently; auth still valid for magic link retry.
          claimTarget = "/profile";
        }
        if (claimTarget) {
          router.replace(claimTarget);
          return;
        }
      }

      setPendingEmail(trimmed);
      if (response.dev_magic_url) {
        setDevMagicUrl(response.dev_magic_url);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Не удалось сохранить.";
      if (/exists|уже/i.test(message)) {
        setError("Этот email уже зарегистрирован — войди в аккаунт.");
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const draft = readGuestProfileDraft();

  if (pendingEmail) {
    return (
      <ValueFirstOnboardingShell
        step={5}
        turnId="save_pending"
        title={copy.save.pendingTitle}
        lead={copy.save.pendingLead}
        backHref={VALUE_FIRST_PATHS.preview}
      >
        <p className={styles.previewIntro}>{copy.save.pendingBody(pendingEmail)}</p>
        <p className={styles.hint}>{copy.save.pendingHint}</p>
        {devMagicUrl ? (
          <div className={styles.ctaRow}>
            <Link href={devMagicUrl}>
              <DsButton variant="primary">Открыть (dev magic link)</DsButton>
            </Link>
          </div>
        ) : null}
      </ValueFirstOnboardingShell>
    );
  }

  return (
    <ValueFirstOnboardingShell
      step={5}
      turnId="save_invite"
      title={copy.save.title}
      lead={copy.save.lead}
      backHref={VALUE_FIRST_PATHS.preview}
    >
      {draft?.first_name ? (
        <p className={styles.previewIntro}>{copy.save.personalIntro(draft.first_name)}</p>
      ) : null}
      <form onSubmit={(e) => void onSubmit(e)}>
        <input
          type="email"
          className={styles.field}
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setError(null);
          }}
          placeholder={copy.save.emailPlaceholder}
          autoComplete="email"
          data-testid="onboarding-save-email"
        />
        {error ? <p className={styles.error}>{error}</p> : null}
        <div className={styles.ctaRow}>
          <DsButton variant="primary" type="submit" disabled={loading} data-testid="onboarding-save-submit">
            {loading ? "Отправляем…" : copy.save.cta}
          </DsButton>
        </div>
      </form>
      <p className={styles.hint}>
        {copy.save.loginHint}{" "}
        <Link href={buildAuthHref("login", VALUE_FIRST_PATHS.save)}>{copy.save.loginLink}</Link>
      </p>
    </ValueFirstOnboardingShell>
  );
}

export default function OnboardingSavePage() {
  return (
    <Suspense fallback={null}>
      <OnboardingSavePageInner />
    </Suspense>
  );
}
