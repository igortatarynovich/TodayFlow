"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { DsBody, DsButton, DsTitle } from "@/design-system";
import { GUEST_ACCESS_COPY } from "@/components/guest/guestAccessCopy";
import { guestSignupHref } from "@/lib/guestAccessStore";
import { hasAuthSessionEnded } from "@/lib/authSession";
import s from "@/components/guest/guestAccessLimitGate.module.css";

export type GuestAccessLimitGateProps = {
  title: string;
  body: string;
  signupHref?: string;
  signupLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
  testId?: string;
};

export function GuestAccessLimitGate({
  title,
  body,
  signupHref,
  signupLabel,
  secondaryHref,
  secondaryLabel,
  testId = "guest-access-limit-gate",
}: GuestAccessLimitGateProps) {
  const [sessionEnded, setSessionEnded] = useState(false);
  useEffect(() => {
    setSessionEnded(hasAuthSessionEnded());
  }, []);

  const primaryHref =
    signupHref ?? (sessionEnded ? "/auth?mode=login" : guestSignupHref());
  const primaryLabel =
    signupLabel ??
    (sessionEnded ? GUEST_ACCESS_COPY.sessionEndedCta : "Создать мой Today");
  const resolvedBody =
    sessionEnded && signupHref == null ? GUEST_ACCESS_COPY.sessionEndedBody(body) : body;

  const resolvedSecondaryHref =
    secondaryHref ?? (sessionEnded ? guestSignupHref() : undefined);
  const resolvedSecondaryLabel =
    secondaryLabel ?? (sessionEnded ? "Создать новый Today" : undefined);

  return (
    <section className={s.gate} data-testid={testId}>
      <DsTitle as="h1">{title}</DsTitle>
      <DsBody muted>{resolvedBody}</DsBody>
      <div className={s.actions}>
        <DsButton href={primaryHref}>{primaryLabel}</DsButton>
        {resolvedSecondaryHref && resolvedSecondaryLabel ? (
          <Link href={resolvedSecondaryHref} className={s.secondaryLink}>
            {resolvedSecondaryLabel}
          </Link>
        ) : null}
      </div>
    </section>
  );
}
