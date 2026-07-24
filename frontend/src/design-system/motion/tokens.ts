/**
 * Motion kit tokens — parity with `todayflow-foundation.css` `--tf-motion-*`.
 * FOUNDATION_UI §7: do not invent per-screen durations.
 */
export const MOTION = {
  microMs: 150,
  revealMs: 280,
  cardMs: 320,
  pageMs: 420,
  staggerMs: 45,
  easeOut: [0.22, 1, 0.36, 1] as const,
  easeInOut: [0.45, 0, 0.55, 1] as const,
} as const;

export type MotionEase = typeof MOTION.easeOut | typeof MOTION.easeInOut;
