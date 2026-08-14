"use client";

import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsTarotFaceProps = {
  /** Absolute or app path to face art. */
  src: string;
  alt?: string;
  className?: string;
  testId?: string;
};

/** Rounded tarot face tile — Form Kit visual container. */
export function DsTarotFace({ src, alt = "", className, testId }: DsTarotFaceProps) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- static public card faces
    <img
      src={src}
      alt={alt}
      className={joinClass(fk.tarotFace, className)}
      data-testid={testId}
      draggable={false}
    />
  );
}
