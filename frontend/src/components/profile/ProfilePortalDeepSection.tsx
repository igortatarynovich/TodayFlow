"use client";

import { useCallback, useEffect, useState, type MouseEvent, type ReactNode } from "react";
import { ProfileMotionExpand, profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { MotionPulse } from "@/design-system/motion";
import { PROFILE_QUICK_MAP_COPY as copy } from "@/components/profile/quickMap/profileQuickMapCopy";
import styles from "./profilePortalDeepSection.module.css";

export function ProfilePortalDeepSection({
  id,
  defaultOpen = false,
  open: controlledOpen,
  onOpenChange,
  children,
}: {
  id?: string;
  defaultOpen?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: ReactNode;
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
      className={styles.root}
      data-testid="profile-portal-deep"
    >
      <summary className={`${styles.summary} ${profileMotionStyles.summaryCta}`} onClick={handleSummaryClick}>
        <SacredGeometryBackdrop emphasis="strong" preset="portal" tone="dark" />
        <span className={styles.slit} aria-hidden />
        <span className={styles.vignette} aria-hidden />
        <div className={styles.inner}>
          <p className={styles.kicker}>{copy.portalKicker}</p>
          <p className={styles.title}>{copy.portalTitle}</p>
          <p className={styles.sub}>{copy.portalSub}</p>
          <MotionPulse active={!isOpen} className={styles.ctaPulse}>
            <span className={styles.cta}>{isOpen ? copy.portalCollapse : copy.portalEnter}</span>
          </MotionPulse>
        </div>
      </summary>
      <ProfileMotionExpand open={isOpen}>
        <div className={styles.body}>{children}</div>
      </ProfileMotionExpand>
    </details>
  );
}
