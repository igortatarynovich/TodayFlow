/**
 * TodayScreenBlock — Form Kit cluster (FOUNDATION_UI §16 + §15.8).
 */
"use client";

import type { ReactNode } from "react";
import { DsBody, DsCard, DsEyebrow } from "@/design-system";
import { joinClass } from "@/design-system/utils/joinClass";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type BlockProps = {
  eyebrow?: string | null;
  primary?: ReactNode;
  detail?: ReactNode;
  children?: ReactNode;
  className?: string;
  testId?: string;
  as?: "div" | "section" | "article" | "button";
  onClick?: () => void;
};

export function TodayScreenBlock({
  eyebrow = null,
  primary = null,
  detail = null,
  children = null,
  className,
  testId,
  as = "article",
  onClick,
}: BlockProps) {
  return (
    <DsCard
      tone="glass"
      size="compact"
      as={as}
      className={joinClass(layout.stack, className)}
      testId={testId}
      onClick={onClick}
    >
      {eyebrow ? <DsEyebrow>{eyebrow}</DsEyebrow> : null}
      {primary != null && primary !== false && primary !== "" ? (
        typeof primary === "string" || typeof primary === "number" ? (
          <DsBody>{String(primary)}</DsBody>
        ) : (
          <div>{primary}</div>
        )
      ) : null}
      {detail != null && detail !== false && detail !== "" ? (
        typeof detail === "string" || typeof detail === "number" ? (
          <DsBody size="sm">{String(detail)}</DsBody>
        ) : (
          <div>{detail}</div>
        )
      ) : null}
      {children}
    </DsCard>
  );
}

type StackProps = {
  children: ReactNode;
  className?: string;
  testId?: string;
};

export function TodayScreenBlockStack({ children, className, testId }: StackProps) {
  return (
    <div className={joinClass(layout.stack, className)} data-testid={testId}>
      {children}
    </div>
  );
}
