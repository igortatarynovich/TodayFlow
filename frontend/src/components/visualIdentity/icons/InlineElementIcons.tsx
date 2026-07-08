import type { ReactElement, ReactNode } from "react";
import type { SymbolicIconProps } from "./iconProps";
import { STROKE } from "./iconProps";
import type { ElementSlug } from "@/lib/visualIdentity/registry";

function IconSvg({ size = 24, className, stroke = "currentColor", children }: SymbolicIconProps & { children: ReactNode }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 28"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <g stroke={stroke} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round">
        {children}
      </g>
    </svg>
  );
}

function FireIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M14 23V9" />
      <path d="M10 21c0-4 2-7 4-9" />
      <path d="M18 21c0-4-2-7-4-9" />
      <path d="M14 7l-3 4h6z" />
    </IconSvg>
  );
}

function EarthIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="14" cy="14" r="6" />
      <path d="M14 8v12M8 14h12" />
    </IconSvg>
  );
}

function AirIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M6 10h16" />
      <path d="M8 14h12" />
      <path d="M6 18h16" />
      <path d="M20 10l2-2M20 18l2 2" />
    </IconSvg>
  );
}

function WaterIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M6 12c2-2 4-2 6 0s4 2 6 0 4-2 6 0" />
      <path d="M6 17c2-2 4-2 6 0s4 2 6 0 4-2 6 0" />
      <path d="M14 8v12" />
    </IconSvg>
  );
}

const ELEMENT_MAP: Record<ElementSlug, (p: SymbolicIconProps) => ReactElement> = {
  fire: FireIcon,
  earth: EarthIcon,
  air: AirIcon,
  water: WaterIcon,
};

export function InlineElementIcon({ slug, ...props }: SymbolicIconProps & { slug: ElementSlug }) {
  const C = ELEMENT_MAP[slug];
  return C ? <C {...props} /> : null;
}
