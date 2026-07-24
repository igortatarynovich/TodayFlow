"use client";

/**
 * Shared in-main states for Product App Shell (PR-2).
 * Loading uses page-geometry skeleton (FOUNDATION_UI §10) — never bare text alone.
 */
import type { ReactNode } from "react";
import { DsButton } from "@/design-system";
import { SkeletonLoader } from "@/components/orbit/SkeletonLoader";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export function ProductShellLoading({ label }: { label?: string }) {
  return (
    <div
      className={pl.pageSkeleton}
      data-testid="product-shell-loading"
      role="status"
      aria-busy="true"
      aria-label={label || "Loading"}
    >
      <div className={pl.pageSkeletonHeader}>
        <SkeletonLoader height="2.25rem" width="42%" />
        <SkeletonLoader height="1.75rem" width="7.5rem" />
      </div>
      <SkeletonLoader height="7.5rem" width="100%" className={pl.pageSkeletonHero} />
      <div className={pl.pageSkeletonGrid}>
        <SkeletonLoader height="5.5rem" width="100%" />
        <SkeletonLoader height="5.5rem" width="100%" />
        <SkeletonLoader height="5.5rem" width="100%" />
      </div>
      {label ? <p className={pl.pageSkeletonLabel}>{label}</p> : null}
    </div>
  );
}

export function ProductShellEmpty({
  message,
  action,
}: {
  message: string;
  action?: ReactNode;
}) {
  return (
    <div className={pl.centerState} data-testid="product-shell-empty">
      <p className={v2.bodyLead}>{message}</p>
      {action ?? null}
    </div>
  );
}

export function ProductShellError({
  message,
  retryLabel,
  onRetry,
}: {
  message: string;
  retryLabel?: string;
  onRetry?: () => void;
}) {
  return (
    <div className={pl.centerState} data-testid="product-shell-error">
      <p className={v2.bodyLead}>{message}</p>
      {onRetry && retryLabel ? (
        <DsButton type="button" onClick={onRetry}>
          {retryLabel}
        </DsButton>
      ) : null}
    </div>
  );
}
