"use client";

/**
 * Shared in-main states for Product App Shell (PR-2).
 * Structure only — no invented product cards or filler metrics.
 */
import type { ReactNode } from "react";
import { DsButton } from "@/design-system";
import { LoadingSpinner } from "@/components/orbit";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import pl from "@/design-system/layouts/productPageLayout.module.css";

export function ProductShellLoading({ label }: { label?: string }) {
  return (
    <div className={pl.centerState} data-testid="product-shell-loading">
      <LoadingSpinner size="lg" />
      {label ? <p className={v2.bodyLead}>{label}</p> : null}
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
