import type { ReactElement, ReactNode } from "react";
import type { SymbolicIconProps } from "./iconProps";
import { STROKE } from "./iconProps";
import type { ZodiacSlug } from "@/lib/visualIdentity/registry";

function IconSvg({ size = 28, className, stroke = "currentColor", children }: SymbolicIconProps & { children: ReactNode }) {
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

function AriesIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M8 20c0-4 2-8 6-10M20 20c0-4-2-8-6-10" />
      <path d="M14 10V6M11 8h6" />
    </IconSvg>
  );
}

function TaurusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="14" cy="15" r="6" />
      <path d="M10 9c1-3 3-4 4-4s3 1 4 4" />
    </IconSvg>
  );
}

function GeminiIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M10 6v16M18 6v16" />
      <path d="M10 10h8M10 18h8" />
    </IconSvg>
  );
}

function CancerIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M9 16c2 3 5 4 8 2 2-1 3-4 2-6" />
      <path d="M19 12c-2-3-5-4-8-2-2 1-3 4-2 6" />
    </IconSvg>
  );
}

function LeoIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <circle cx="14" cy="14" r="5" />
      <path d="M14 9V5M10 7l-2-2M18 7l2-2" />
    </IconSvg>
  );
}

function VirgoIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M10 8v12M14 8v8c0 3 2 4 4 4" />
      <path d="M18 8v4" />
    </IconSvg>
  );
}

function LibraIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M8 18h12" />
      <path d="M10 14h8" />
      <path d="M14 8v6" />
    </IconSvg>
  );
}

function ScorpioIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M10 8v10M14 8v6c0 3 2 4 4 4" />
      <path d="M18 18l3 3" />
    </IconSvg>
  );
}

function SagittariusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M8 20l10-10" />
      <path d="M12 10h6v6" />
    </IconSvg>
  );
}

function CapricornIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M9 8v10c0 3 3 4 6 2" />
      <path d="M15 8c2 0 4 2 4 5v5" />
    </IconSvg>
  );
}

function AquariusIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M7 10h4l2-2 2 2h4M7 16h4l2-2 2 2h4" />
    </IconSvg>
  );
}

function PiscesIcon(props: SymbolicIconProps) {
  return (
    <IconSvg {...props}>
      <path d="M10 8c-3 4-3 8 0 12M18 8c3 4 3 8 0 12" />
      <path d="M14 8v12" />
    </IconSvg>
  );
}

const ZODIAC_MAP: Record<ZodiacSlug, (p: SymbolicIconProps) => ReactElement> = {
  aries: AriesIcon,
  taurus: TaurusIcon,
  gemini: GeminiIcon,
  cancer: CancerIcon,
  leo: LeoIcon,
  virgo: VirgoIcon,
  libra: LibraIcon,
  scorpio: ScorpioIcon,
  sagittarius: SagittariusIcon,
  capricorn: CapricornIcon,
  aquarius: AquariusIcon,
  pisces: PiscesIcon,
};

export function InlineZodiacIcon({ slug, ...props }: SymbolicIconProps & { slug: ZodiacSlug }) {
  const C = ZODIAC_MAP[slug];
  return C ? <C {...props} /> : null;
}
