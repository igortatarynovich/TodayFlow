"use client";

import { chartAngleAssetPath, type ChartAngleSlug } from "@/lib/visualIdentity/registry";
import { joinClass } from "@/design-system/utils/joinClass";
import fk from "@/design-system/primitives/dsFormKit.module.css";

type DsAngleProps = {
  angle: ChartAngleSlug | "ASC" | "DSC" | "MC" | "IC";
  size?: number;
  className?: string;
  testId?: string;
};

function resolveSlug(angle: DsAngleProps["angle"]): ChartAngleSlug {
  const key = String(angle).toLowerCase();
  if (key === "asc" || key === "dsc" || key === "mc" || key === "ic") return key;
  return "asc";
}

/** DS-only chart-angle badge entrypoint. */
export function DsAngle({ angle, size = 28, className, testId }: DsAngleProps) {
  const slug = resolveSlug(angle);
  return (
    <span
      className={joinClass(fk.angleBadge, className)}
      style={{ width: size, height: size }}
      data-testid={testId}
      aria-hidden
    >
      {/* eslint-disable-next-line @next/next/no-img-element -- static public WebP */}
      <img src={chartAngleAssetPath(slug)} alt="" width={size} height={size} draggable={false} />
    </span>
  );
}
