"use client";

import Link from "next/link";
import { DsBody, DsButton, DsTitle } from "@/design-system";
import { guestSignupHref } from "@/lib/guestAccessStore";
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
  signupHref = guestSignupHref(),
  signupLabel = "Построить мой профиль",
  secondaryHref,
  secondaryLabel,
  testId = "guest-access-limit-gate",
}: GuestAccessLimitGateProps) {
  return (
    <section className={s.gate} data-testid={testId}>
      <DsTitle as="h1">{title}</DsTitle>
      <DsBody muted>{body}</DsBody>
      <div className={s.actions}>
        <DsButton href={signupHref}>{signupLabel}</DsButton>
        {secondaryHref && secondaryLabel ? (
          <Link href={secondaryHref} className={s.secondaryLink}>
            {secondaryLabel}
          </Link>
        ) : null}
      </div>
    </section>
  );
}
