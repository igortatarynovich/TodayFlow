"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { postJson } from "@/lib/api";
import { saveActiveDaySpineContext, saveActiveJTBDContext } from "@/lib/jtbdFeedback";

const JTBD_PARAMS = [
  "jtbd_log_id",
  "jtbd_signal",
  "jtbd_lane",
  "jtbd_surface",
  "jtbd_route",
] as const;

const DAY_SPINE_PARAMS = [
  "day_spine_log_id",
  "day_spine_action",
  "day_spine_label",
  "day_spine_surface",
  "day_spine_target",
] as const;

export function JTBDRouteArrivalLogger() {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const loggedKeyRef = useRef<string | null>(null);

  useEffect(() => {
    const generationLogIdRaw = searchParams.get("jtbd_log_id");
    const signal = searchParams.get("jtbd_signal");
    const lane = searchParams.get("jtbd_lane");
    const sourceSurface = searchParams.get("jtbd_surface");
    const route = searchParams.get("jtbd_route");
    const daySpineLogIdRaw = searchParams.get("day_spine_log_id");
    const daySpineAction = searchParams.get("day_spine_action");
    const daySpineLabel = searchParams.get("day_spine_label");
    const daySpineSurface = searchParams.get("day_spine_surface");
    const daySpineTarget = searchParams.get("day_spine_target");
    const daySpineLogId = daySpineLogIdRaw ? Number(daySpineLogIdRaw) : null;

    if (daySpineAction || daySpineLabel || daySpineSurface || daySpineTarget) {
      if (daySpineLogId && Number.isFinite(daySpineLogId) && daySpineLogId > 0) {
        const daySpineDedupeKey = `day-spine:${daySpineLogId}:${pathname}:${daySpineAction || ""}`;
        if (loggedKeyRef.current !== daySpineDedupeKey) {
          loggedKeyRef.current = daySpineDedupeKey;
          void postJson("/learning/feedback", {
            generation_log_id: daySpineLogId,
            signal: "day_spine_route_completed",
            metadata: {
              source_surface: daySpineSurface,
              arrived_path: pathname,
              day_spine_action_kind: daySpineAction,
              day_spine_action_label: daySpineLabel,
              day_spine_target_href: daySpineTarget,
            },
          }).catch((error) => {
            console.error("Failed to log day spine route arrival", error);
          });
        }
      }

      const cleanParams = new URLSearchParams(searchParams.toString());
      DAY_SPINE_PARAMS.forEach((param) => cleanParams.delete(param));
      const cleanUrl = cleanParams.toString() ? `${pathname}?${cleanParams.toString()}` : pathname;

      saveActiveDaySpineContext({
        generation_log_id: daySpineLogId,
        action_kind: daySpineAction,
        action_label: daySpineLabel,
        source_surface: daySpineSurface,
        arrived_path: pathname,
        target_href: daySpineTarget,
        arrived_at: new Date().toISOString(),
      });

      if (!generationLogIdRaw || !signal) {
        router.replace(cleanUrl, { scroll: false });
        return;
      }
    }

    if (!generationLogIdRaw || !signal) return;

    const generationLogId = Number(generationLogIdRaw);
    if (!Number.isFinite(generationLogId) || generationLogId <= 0) return;

    const dedupeKey = `${generationLogId}:${signal}:${pathname}`;
    if (loggedKeyRef.current === dedupeKey) return;
    loggedKeyRef.current = dedupeKey;

    const cleanParams = new URLSearchParams(searchParams.toString());
    JTBD_PARAMS.forEach((param) => cleanParams.delete(param));
    DAY_SPINE_PARAMS.forEach((param) => cleanParams.delete(param));
    const cleanUrl = cleanParams.toString() ? `${pathname}?${cleanParams.toString()}` : pathname;

    void postJson("/learning/feedback", {
      generation_log_id: generationLogId,
      signal,
      metadata: {
        lane,
        source_surface: sourceSurface,
        arrived_path: pathname,
        arrived_route: route,
      },
    }).catch((error) => {
      console.error("Failed to log JTBD route arrival", error);
    });

    saveActiveJTBDContext({
      generation_log_id: generationLogId,
      lane,
      source_surface: sourceSurface,
      arrived_path: pathname,
      arrived_route: route,
      arrived_at: new Date().toISOString(),
    });

    router.replace(cleanUrl, { scroll: false });
  }, [pathname, router, searchParams]);

  return null;
}
