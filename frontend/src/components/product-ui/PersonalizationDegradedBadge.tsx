"use client";

import {
  shouldShowTodayServiceUnavailableNotice,
  TODAY_SERVICE_UNAVAILABLE_MESSAGE,
} from "@/lib/personalizationQuality";
import type { TodayContractV1 } from "@/lib/todayContract";

type Props = {
  contract: TodayContractV1 | null | undefined;
  narrativeRequestFailed?: boolean;
  className?: string;
};

export function PersonalizationDegradedBadge({
  contract,
  narrativeRequestFailed,
  className,
}: Props) {
  if (!shouldShowTodayServiceUnavailableNotice({ contract, narrativeRequestFailed })) {
    return null;
  }
  return (
    <p
      className={className ?? "orbit-body-xs"}
      style={{ margin: "0 0 0.75rem", color: "var(--orbit-color-text-muted, #7a623d)" }}
      role="status"
    >
      {TODAY_SERVICE_UNAVAILABLE_MESSAGE}
    </p>
  );
}
