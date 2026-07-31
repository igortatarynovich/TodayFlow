import type { ReactNode } from "react";
import type { PracticeFormatId, PracticeNeedId } from "@/lib/practicesPage/practicesCanon";

type IconProps = { className?: string };

function Svg({ className, children }: IconProps & { children: ReactNode }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function PracticeNeedIcon({ id, className }: { id: PracticeNeedId; className?: string }) {
  switch (id) {
    case "calm":
      return (
        <Svg className={className}>
          <path
            d="M8 2.2c.4 1.6 1.6 2.8 3.2 3.2C9.6 5.8 8.4 7 8 8.6 7.6 7 6.4 5.8 4.8 5.4 6.4 5 7.6 3.8 8 2.2Z"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinejoin="round"
          />
          <path d="M3.5 11.5h9" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
          <path d="M5 13.5h6" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
        </Svg>
      );
    case "focus":
      return (
        <Svg className={className}>
          <rect x="3.5" y="3.5" width="9" height="9" rx="2" stroke="currentColor" strokeWidth="1.25" />
          <circle cx="8" cy="8" r="1.6" fill="currentColor" />
        </Svg>
      );
    case "recover":
      return (
        <Svg className={className}>
          <circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.25" />
          <circle cx="8" cy="8" r="1.5" fill="currentColor" />
        </Svg>
      );
    case "body":
      return (
        <Svg className={className}>
          <path
            d="M8 13.2S3.8 10.2 3.8 6.9A2.4 2.4 0 0 1 8 5.2a2.4 2.4 0 0 1 4.2 1.7c0 3.3-4.2 6.3-4.2 6.3Z"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinejoin="round"
          />
        </Svg>
      );
    case "understand":
      return (
        <Svg className={className}>
          <circle cx="8" cy="6" r="2.4" stroke="currentColor" strokeWidth="1.25" />
          <path
            d="M3.8 13c.7-2 2.2-3 4.2-3s3.5 1 4.2 3"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinecap="round"
          />
        </Svg>
      );
    case "sleep":
      return (
        <Svg className={className}>
          <path
            d="M10.8 3.4A5.2 5.2 0 1 0 12.6 11 4.4 4.4 0 0 1 10.8 3.4Z"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinejoin="round"
          />
        </Svg>
      );
    default:
      return null;
  }
}

export function PracticeFormatIcon({ id, className }: { id: PracticeFormatId; className?: string }) {
  switch (id) {
    case "meditation":
      return (
        <Svg className={className}>
          <path
            d="M8 12.5c-2.2 0-4-1.4-4-3.2C4 7.2 5.8 5.5 8 3.5c2.2 2 4 3.7 4 5.8 0 1.8-1.8 3.2-4 3.2Z"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinejoin="round"
          />
        </Svg>
      );
    case "breath":
      return (
        <Svg className={className}>
          <path
            d="M4 8h8M5.5 5.5A3.5 3.5 0 0 1 12 7M5.5 10.5A3.5 3.5 0 0 0 12 9"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinecap="round"
          />
        </Svg>
      );
    case "yoga":
      return (
        <Svg className={className}>
          <circle cx="8" cy="3.8" r="1.4" stroke="currentColor" strokeWidth="1.2" />
          <path d="M8 5.4v3.2M5 14l3-5.4L11 14M5.2 9.2h5.6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </Svg>
      );
    case "stretch":
      return (
        <Svg className={className}>
          <path d="M3.5 11.5 8 4.5l4.5 7" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M5.5 11.5h5" stroke="currentColor" strokeWidth="1.25" strokeLinecap="round" />
        </Svg>
      );
    case "visualization":
      return (
        <Svg className={className}>
          <ellipse cx="8" cy="8" rx="5.2" ry="3.2" stroke="currentColor" strokeWidth="1.25" />
          <circle cx="8" cy="8" r="1.5" fill="currentColor" />
        </Svg>
      );
    case "affirmation":
      return (
        <Svg className={className}>
          <path
            d="M8 12.8S4.2 10.2 4.2 7.4A2.1 2.1 0 0 1 8 5.9a2.1 2.1 0 0 1 3.8 1.5c0 2.8-3.8 5.4-3.8 5.4Z"
            stroke="currentColor"
            strokeWidth="1.25"
          />
        </Svg>
      );
    case "reflection":
      return (
        <Svg className={className}>
          <path d="M4.5 3.5h5.5L12 6v6.5H4.5V3.5Z" stroke="currentColor" strokeWidth="1.25" strokeLinejoin="round" />
          <path d="M6.2 8h3.6M6.2 10.2h2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
        </Svg>
      );
    case "music":
      return (
        <Svg className={className}>
          <path d="M6.2 12.2a1.6 1.6 0 1 1-1.5-1.6" stroke="currentColor" strokeWidth="1.25" />
          <path d="M6.2 12.2V4.5l5.6-1.2v6.8" stroke="currentColor" strokeWidth="1.25" strokeLinejoin="round" />
          <path d="M11.8 10.1a1.6 1.6 0 1 1-1.5-1.6" stroke="currentColor" strokeWidth="1.25" />
        </Svg>
      );
    case "sleep":
      return (
        <Svg className={className}>
          <path
            d="M10.8 3.4A5.2 5.2 0 1 0 12.6 11 4.4 4.4 0 0 1 10.8 3.4Z"
            stroke="currentColor"
            strokeWidth="1.25"
            strokeLinejoin="round"
          />
        </Svg>
      );
    default:
      return null;
  }
}
