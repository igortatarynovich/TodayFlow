"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type MouseEvent, type ReactNode } from "react";
import { ProfileMotionExpand, profileMotionStyles } from "@/components/foundation/ProfileMotion";
import styles from "@/design-system/profile/dsProfileExpandable.module.css";

export function ProfileExpandableSection({
  id,
  title,
  subtitle,
  helpLink,
  defaultOpen = false,
  open: controlledOpen,
  onOpenChange,
  children,
  variant = "card",
}: {
  id?: string;
  title: string;
  subtitle?: string;
  helpLink?: { href: string; label: string };
  defaultOpen?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: ReactNode;
  /** `plain` — text toggle only, no nested card chrome. */
  variant?: "card" | "plain";
}) {
  const isControlled = controlledOpen !== undefined;
  const [internalOpen, setInternalOpen] = useState(defaultOpen);
  const isOpen = isControlled ? controlledOpen : internalOpen;

  useEffect(() => {
    if (!isControlled) {
      setInternalOpen(defaultOpen);
    }
  }, [defaultOpen, isControlled]);

  const handleSummaryClick = useCallback(
    (event: MouseEvent<HTMLElement>) => {
      event.preventDefault();
      const next = !isOpen;
      if (!isControlled) {
        setInternalOpen(next);
      }
      onOpenChange?.(next);
    },
    [isControlled, isOpen, onOpenChange],
  );

  return (
    <details
      id={id}
      open={isOpen}
      className={`${styles.root} ${variant === "plain" ? styles.rootPlain : ""}`.trim()}
    >
      <summary className={`${styles.summary} ${profileMotionStyles.summaryCta}`} onClick={handleSummaryClick}>
        <div>
          <p className={styles.title}>{title}</p>
          {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}
          {helpLink ? (
            <p className={styles.helpLink}>
              <Link href={helpLink.href}>{helpLink.label}</Link>
            </p>
          ) : null}
        </div>
        <span className={styles.toggle}>{isOpen ? "Свернуть" : "Развернуть"}</span>
      </summary>
      <ProfileMotionExpand open={isOpen}>
        <div className={styles.body}>{children}</div>
      </ProfileMotionExpand>
    </details>
  );
}
