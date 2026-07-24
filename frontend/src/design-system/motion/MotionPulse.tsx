"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { MOTION } from "@/design-system/motion/tokens";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";

type MotionPulseProps = {
  children: ReactNode;
  className?: string;
  reducedMotion?: boolean;
  /** Pause pulse (e.g. after user acted). */
  active?: boolean;
};

/**
 * Pulse — soft CTA waiting for action (FOUNDATION_UI §7).
 */
export function MotionPulse({
  children,
  className,
  reducedMotion,
  active = true,
}: MotionPulseProps) {
  const systemReduce = usePrefersReducedMotion();
  const reduce = reducedMotion ?? systemReduce;

  if (reduce || !active) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      className={className}
      animate={{ scale: [1, 1.03, 1], opacity: [1, 0.92, 1] }}
      transition={{
        duration: (MOTION.revealMs * 8) / 1000,
        ease: "easeInOut",
        repeat: Infinity,
      }}
    >
      {children}
    </motion.div>
  );
}
