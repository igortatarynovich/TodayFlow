"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { MOTION } from "@/design-system/motion/tokens";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";

type MotionRevealProps = {
  children: ReactNode;
  className?: string;
  delayMs?: number;
  /** When true, skip motion regardless of system preference. */
  reducedMotion?: boolean;
  as?: "div" | "span" | "section";
};

/**
 * Reveal — text/insight rises with fade (FOUNDATION_UI §7).
 * `--tf-motion-reveal` + ease-out.
 */
export function MotionReveal({
  children,
  className,
  delayMs = 0,
  reducedMotion,
  as = "div",
}: MotionRevealProps) {
  const systemReduce = usePrefersReducedMotion();
  const reduce = reducedMotion ?? systemReduce;
  const Tag = motion[as];

  if (reduce) {
    const Static = as;
    return <Static className={className}>{children}</Static>;
  }

  return (
    <Tag
      className={className}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: MOTION.revealMs / 1000,
        ease: MOTION.easeOut,
        delay: delayMs / 1000,
      }}
    >
      {children}
    </Tag>
  );
}
