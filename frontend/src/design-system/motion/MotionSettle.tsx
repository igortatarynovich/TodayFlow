"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { MOTION } from "@/design-system/motion/tokens";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";

type MotionSettleProps = {
  children: ReactNode;
  className?: string;
  delayMs?: number;
  reducedMotion?: boolean;
};

/**
 * Settle — slight drop + spring stop (FOUNDATION_UI §7).
 * For practice/tracker list cards.
 */
export function MotionSettle({
  children,
  className,
  delayMs = 0,
  reducedMotion,
}: MotionSettleProps) {
  const systemReduce = usePrefersReducedMotion();
  const reduce = reducedMotion ?? systemReduce;

  if (reduce) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        type: "spring",
        stiffness: 380,
        damping: 28,
        delay: delayMs / 1000,
        mass: 0.85,
      }}
    >
      {children}
    </motion.div>
  );
}
