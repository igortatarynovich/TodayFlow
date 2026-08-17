"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";

type MotionDriftProps = {
  children: ReactNode;
  className?: string;
  reducedMotion?: boolean;
  /** Full loop duration in seconds (very slow by default). */
  durationSec?: number;
};

/**
 * Drift — almost imperceptible idle motion.
 * FOUNDATION_UI §18: in-app idle décor is over budget (2–3/10). Prefer landing only.
 * Do not use for particles / starfield.
 */
export function MotionDrift({
  children,
  className,
  reducedMotion,
  durationSec = 14,
}: MotionDriftProps) {
  const systemReduce = usePrefersReducedMotion();
  const reduce = reducedMotion ?? systemReduce;

  if (reduce) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      className={className}
      animate={{ y: [0, -6, 0], rotate: [0, 0.6, 0] }}
      transition={{
        duration: durationSec,
        ease: "easeInOut",
        repeat: Infinity,
      }}
    >
      {children}
    </motion.div>
  );
}
