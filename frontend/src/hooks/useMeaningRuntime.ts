"use client";

import { useCallback } from "react";
import type { MeaningEventSource, MeaningEventType } from "@/lib/types";
import { getStoredAccessToken } from "@/lib/api";
import { enqueueMeaningEvent, flushMeaningOutbox, refreshMeaningRings } from "@/lib/meaningRuntime";

type TrackMeaningInput = {
  event_type: MeaningEventType;
  event_source: MeaningEventSource;
  quality_score?: number;
  payload?: Record<string, unknown> | null;
  local_date?: string | null;
  idempotency_key?: string;
  refreshRings?: boolean;
};

export function useMeaningRuntime() {
  const trackMeaningEvent = useCallback((input: TrackMeaningInput) => {
    enqueueMeaningEvent({
      event_type: input.event_type,
      event_source: input.event_source,
      quality_score: input.quality_score,
      payload: input.payload,
      local_date: input.local_date,
      idempotency_key: input.idempotency_key,
    });
    if (getStoredAccessToken()) {
      flushMeaningOutbox().catch(() => undefined);
      if (input.refreshRings !== false) {
        refreshMeaningRings(28).catch(() => undefined);
      }
    }
  }, []);

  return { trackMeaningEvent };
}

