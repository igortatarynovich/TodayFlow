/**
 * Today ActShell — Wave 1 layout contract (review checklist).
 *
 * When adding content to Today acts:
 * 1. Render through `TodayActShell` (or nest only readable text measure ≤42ch).
 * 2. Do NOT add act-level max-width or extra horizontal padding outside ActShell.
 * 3. Media + text = vertical stack (visual full-width → text), never 5 nested cards.
 * 4. Opportunity/trap dual panels stay vertical (no side-by-side columns).
 * 5. New modules (natal, chart) must use ActShell full-bleed stack.
 * 6. QA: remove text — composition must still look intentional (Foundation UI).
 *
 * Reserved Wave 2 slots (do not remove testids):
 * - today-slot-verdict-strip (deeper acts / Plot — not Glance hero)
 * - today-slot-glance-nearest / today-slot-glance-timeline
 * - today-slot-tap-widget (Response)
 */
export const TODAY_ACT_SHELL_REVIEW_CHECKLIST = [
  "Uses TodayActShell for the act",
  "No nested max-width / padding shells",
  "Media stacked full-bleed above text on mobile",
  "Dual panels vertical always",
  "Wave 2 slots keep their testids",
] as const;
