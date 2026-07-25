"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MOTION } from "@/design-system/motion/tokens";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";
import styles from "@/components/today/TodayDayReveal.module.css";

type Props = {
  /** Data already in hand — theatrical open, not a real wait. */
  ready: boolean;
  /** Optional label while waiting for first cold paint. */
  waitingLabel?: string;
  readyLabel?: string;
  openLabel?: string;
  /** Minimum theatrical duration once ready (ms). */
  minReadyMs?: number;
  onComplete: () => void;
};

/**
 * Premium day curtain: the day is already assembled; we stage the opening.
 */
export function TodayDayReveal({
  ready,
  waitingLabel = "День собирается…",
  readyLabel = "День уже собран",
  openLabel = "Открываю…",
  minReadyMs = 1600,
  onComplete,
}: Props) {
  const reduce = usePrefersReducedMotion();
  const [phase, setPhase] = useState<"wait" | "ready" | "open" | "done">(ready ? "ready" : "wait");

  useEffect(() => {
    if (reduce) {
      if (ready) onComplete();
      return;
    }
    if (!ready) {
      setPhase("wait");
      return;
    }
    setPhase("ready");
    const t1 = window.setTimeout(() => setPhase("open"), Math.min(700, minReadyMs * 0.4));
    const t2 = window.setTimeout(() => {
      setPhase("done");
      onComplete();
    }, minReadyMs);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [ready, reduce, minReadyMs, onComplete]);

  const label = phase === "wait" ? waitingLabel : phase === "open" || phase === "done" ? openLabel : readyLabel;

  return (
    <AnimatePresence>
      {phase !== "done" ? (
        <motion.div
          className={styles.root}
          data-testid="today-day-reveal"
          data-ready={ready ? "1" : "0"}
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: MOTION.pageMs / 1000, ease: MOTION.easeOut }}
          aria-live="polite"
          aria-busy={!ready}
        >
          <div className={styles.atmosphere} aria-hidden />
          <div className={styles.orbWrap} aria-hidden>
            <span className={`${styles.ring} ${styles.ringOuter}`} />
            <span className={`${styles.ring} ${styles.ringMid}`} />
            <span className={`${styles.ring} ${styles.ringInner}`} />
            <span className={styles.core} />
          </div>
          <motion.p
            key={label}
            className={styles.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: MOTION.revealMs / 1000, ease: MOTION.easeOut }}
          >
            {label}
          </motion.p>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
