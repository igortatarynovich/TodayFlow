"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { DsCelestialMoon } from "@/design-system";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";
import { celestialPhaseFromUtcDate } from "@/lib/celestialMoonPhase";
import l from "@/design-system/layouts/dsLayouts.module.css";

const MAX_YAW = 0.28;

/**
 * Landing signature: live lunar phase (astronomy), slow pointer yaw.
 * Phase never follows the cursor. FOUNDATION_UI §2.7 / §18.
 */
export function LandingSignatureMoon({ size = 440 }: { size?: number }) {
  const reduce = usePrefersReducedMotion();
  const phase = useMemo(() => celestialPhaseFromUtcDate(new Date()), []);
  const [longitude, setLongitude] = useState(0);
  const targetRef = useRef(0);

  useEffect(() => {
    if (reduce) {
      setLongitude(0);
      return;
    }

    let raf = 0;
    const currentRef = { current: 0 };
    const tick = () => {
      const current = currentRef.current;
      const next = current + (targetRef.current - current) * 0.06;
      currentRef.current = next;
      setLongitude(next);
      if (Math.abs(next - targetRef.current) > 0.0008) {
        raf = requestAnimationFrame(tick);
      } else {
        raf = 0;
      }
    };

    const onMove = (event: PointerEvent) => {
      const nx = event.clientX / Math.max(window.innerWidth, 1) - 0.5;
      const ny = event.clientY / Math.max(window.innerHeight, 1) - 0.5;
      targetRef.current = Math.max(-MAX_YAW, Math.min(MAX_YAW, nx * 0.48 + ny * 0.1));
      if (raf === 0) raf = requestAnimationFrame(tick);
    };

    window.addEventListener("pointermove", onMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", onMove);
      cancelAnimationFrame(raf);
    };
  }, [reduce]);

  return (
    <div className={l.heroMoonStage} data-testid="landing-hero-moon">
      <DsCelestialMoon
        phase={phase}
        size={size}
        spin={0}
        animated={false}
        longitude={reduce ? 0 : longitude}
        glow={0.72}
        testId="landing-hero-moon-sphere"
      />
    </div>
  );
}
