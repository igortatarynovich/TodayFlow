"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { MOTION } from "@/design-system/motion/tokens";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";
import styles from "@/design-system/motion/motionFlip.module.css";

type MotionFlipProps = {
  /** Face (front after flip). */
  front: ReactNode;
  /** Back (shown before flip). */
  back: ReactNode;
  /**
   * When true, animate to face. When false, stay on back.
   * Mount with `flipped={false}` then set true to play the flip.
   */
  flipped: boolean;
  className?: string;
  reducedMotion?: boolean;
  onAnimationComplete?: () => void;
  /** test id on the 3D stage */
  testId?: string;
};

/**
 * Flip — 3D rotateY card turn (FOUNDATION_UI §7).
 * Duration: `--tf-motion-card` (320ms). Not a crossfade.
 */
export function MotionFlip({
  front,
  back,
  flipped,
  className,
  reducedMotion,
  onAnimationComplete,
  testId = "motion-flip",
}: MotionFlipProps) {
  const systemReduce = usePrefersReducedMotion();
  const reduce = reducedMotion ?? systemReduce;

  if (reduce) {
    return (
      <div className={`${styles.stage} ${className ?? ""}`} data-testid={testId} data-flipped={flipped ? "true" : "false"}>
        <div className={styles.face}>{flipped ? front : back}</div>
      </div>
    );
  }

  return (
    <div className={`${styles.perspective} ${className ?? ""}`} data-testid={testId}>
      <motion.div
        className={styles.card}
        initial={false}
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{
          duration: MOTION.cardMs / 1000,
          ease: MOTION.easeOut,
        }}
        onAnimationComplete={() => {
          if (flipped) onAnimationComplete?.();
        }}
        style={{ transformStyle: "preserve-3d" }}
        data-flipped={flipped ? "true" : "false"}
      >
        <div className={`${styles.face} ${styles.faceBack}`}>{back}</div>
        <div className={`${styles.face} ${styles.faceFront}`}>{front}</div>
      </motion.div>
    </div>
  );
}
