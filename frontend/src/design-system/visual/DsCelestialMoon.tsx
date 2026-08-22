"use client";

import { CelestialMoon, type CelestialMoonProps } from "@/components/celestial/CelestialMoon";

/** DS visual: live lunar sphere (FOUNDATION_UI §2.7). Phase is data; not décor. */
export function DsCelestialMoon(props: CelestialMoonProps) {
  return <CelestialMoon {...props} />;
}
