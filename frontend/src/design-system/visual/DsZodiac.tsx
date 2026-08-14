"use client";

import { ZodiacIcon, type ZodiacIconProps } from "@/components/visualIdentity/ZodiacIcon";

/** DS-only zodiac entrypoint (Form Kit visual contract). */
export function DsZodiac(props: ZodiacIconProps) {
  return <ZodiacIcon {...props} />;
}
