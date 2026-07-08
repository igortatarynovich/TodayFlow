import type { ArchetypeSlug } from "@/lib/visualIdentity/registry";
import type { ReactElement, ReactNode } from "react";
import type { SymbolicIconProps } from "./iconProps";
import { STROKE } from "./iconProps";

function ArchetypeSvg({ size = 56, className, stroke = "currentColor", children }: SymbolicIconProps & { children: ReactNode }) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" className={className} aria-hidden>
      <g stroke={stroke} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round">
        {children}
      </g>
    </svg>
  );
}

function SageIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M16 38V18l12-6 12 6v20" />
      <path d="M22 32h12M28 26v12" />
    </ArchetypeSvg>
  );
}

function ExplorerIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <circle cx="28" cy="28" r="12" />
      <path d="M28 16v6M28 34v6M16 28h6M34 28h6" />
      <path d="M28 22l4 6h-8l4-6z" fill="currentColor" stroke="none" opacity="0.35" />
    </ArchetypeSvg>
  );
}

function ArchitectIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M16 40V16h24v24" />
      <path d="M16 28h24M28 16v24" />
    </ArchetypeSvg>
  );
}

function HarmonizerIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M18 34h20" />
      <path d="M22 34V22h4l2 4 2-4h4v12" />
      <path d="M34 34V22h4l2 4 2-4h4v12" />
    </ArchetypeSvg>
  );
}

function ObserverIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <circle cx="28" cy="28" r="10" />
      <circle cx="28" cy="28" r="4" />
    </ArchetypeSvg>
  );
}

function CreatorIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M28 14l3 8h8l-6 5 2 8-7-5-7 5 2-8-6-5h8l3-8z" />
    </ArchetypeSvg>
  );
}

function StrategistIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M20 38l8-22 8 22" />
      <path d="M24 30h8" />
    </ArchetypeSvg>
  );
}

function UnknownIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <circle cx="28" cy="28" r="14" />
      <path d="M22 28h12" />
    </ArchetypeSvg>
  );
}

function SeekerIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <circle cx="24" cy="24" r="8" />
      <path d="M30 30l8 8" />
      <path d="M28 14v4M28 38v4M14 28h4M38 28h4" />
    </ArchetypeSvg>
  );
}

function MentorIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M18 18v20M38 18v20" />
      <path d="M18 24h20M18 32h20" />
      <path d="M28 14v4" />
      <circle cx="28" cy="12" r="2" />
    </ArchetypeSvg>
  );
}

function GuardianIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M28 12l10 4v12c0 6-10 12-10 12s-10-6-10-12V16l10-4z" />
      <path d="M28 20v12" />
    </ArchetypeSvg>
  );
}

function VisionaryIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M16 28c0-8 5-14 12-14s12 6 12 14-5 14-12 14-12-6-12-14z" />
      <circle cx="28" cy="28" r="4" />
      <path d="M28 8v4M20 12l2 3M36 12l-2 3" />
    </ArchetypeSvg>
  );
}

function CatalystIcon(props: SymbolicIconProps) {
  return (
    <ArchetypeSvg {...props}>
      <path d="M28 12l-6 14h4l-2 14 10-16h-4l8-12z" />
      <circle cx="18" cy="38" r="2" />
      <circle cx="38" cy="38" r="2" />
    </ArchetypeSvg>
  );
}

const MAP: Record<ArchetypeSlug, (p: SymbolicIconProps) => ReactElement> = {
  sage: SageIcon,
  explorer: ExplorerIcon,
  architect: ArchitectIcon,
  harmonizer: HarmonizerIcon,
  observer: ObserverIcon,
  creator: CreatorIcon,
  strategist: StrategistIcon,
  seeker: SeekerIcon,
  mentor: MentorIcon,
  guardian: GuardianIcon,
  visionary: VisionaryIcon,
  catalyst: CatalystIcon,
  unknown: UnknownIcon,
};

export function InlineArchetypeIcon({ slug, ...props }: SymbolicIconProps & { slug: ArchetypeSlug }) {
  const C = MAP[slug] || UnknownIcon;
  return <C {...props} />;
}
