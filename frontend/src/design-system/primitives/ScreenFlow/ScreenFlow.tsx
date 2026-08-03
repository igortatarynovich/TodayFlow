"use client";

import {
  Children,
  cloneElement,
  isValidElement,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type HTMLAttributes,
  type KeyboardEvent,
  type ReactElement,
  type ReactNode,
  type TouchEvent,
} from "react";
import { usePrefersReducedMotion } from "@/design-system/motion/usePrefersReducedMotion";
import { joinClass } from "@/design-system/utils/joinClass";
import styles from "@/design-system/primitives/ScreenFlow/ScreenFlow.module.css";

/** Product Today locks `TODAY_SCREEN_FLOW_AXIS`; primitive still accepts x|y. */
export type ScreenFlowAxis = "x" | "y";

/** Locked SoT for product Today ScreenFlow (see SCREEN_FLOW_V1 §2). */
export const TODAY_SCREEN_FLOW_AXIS: ScreenFlowAxis = "x";

/** Left-edge ignore band for axis=x — reduces clash with iOS edge-back. */
export const SCREEN_FLOW_EDGE_DEADZONE_PX = 24;

export type ScreenFlowStepStatus =
  | "pending"
  | "ready"
  | "empty"
  | "failed"
  | "degraded";

export type ScreenFlowChangeReason =
  | "next"
  | "prev"
  | "select"
  | "swipe"
  | "keyboard"
  | "deep_link";

export type ScreenFlowStepProps = {
  id: string;
  label: string;
  status?: ScreenFlowStepStatus;
  scrollable?: boolean;
  children?: ReactNode;
  /** When false, step title is sr-only (Today product chrome). */
  showTitle?: boolean;
  __sfIndex?: number;
  __sfActive?: boolean;
  __sfAxis?: ScreenFlowAxis;
  __sfHeadingId?: string;
  __sfHeadingRef?: (el: HTMLHeadingElement | null) => void;
};

export type ScreenFlowProps = {
  activeIndex: number;
  onIndexChange: (
    index: number,
    meta: { reason: ScreenFlowChangeReason },
  ) => void;
  axis?: ScreenFlowAxis;
  children: ReactNode;
  className?: string;
  edgeDeadzonePx?: number;
  testId?: string;
  showChrome?: boolean;
  /** Prev/Next text buttons — optional per SCREEN_FLOW_V1 §1.4; Today product keeps false. */
  showStepControls?: boolean;
};

const FAILURE_COPY: Record<"failed" | "degraded", string> = {
  failed: "Нет соединения.",
  degraded: "Не удалось загрузить.",
};

const SWIPE_THRESHOLD_PX = 48;

export function ScreenFlowStep({
  id,
  label,
  status = "ready",
  scrollable = false,
  children,
  showTitle = false,
  __sfIndex = 0,
  __sfActive = false,
  __sfAxis = "x",
  __sfHeadingId,
  __sfHeadingRef,
}: ScreenFlowStepProps) {
  const showSkeleton = status === "pending";
  const showFail = status === "failed" || status === "degraded";
  const showEmpty = status === "empty";

  return (
    <section
      className={joinClass(
        styles.step,
        scrollable ? styles.stepScrollable : styles.stepLocked,
        __sfActive ? styles.stepActive : styles.stepInactive,
      )}
      data-screen-flow-step={id}
      data-step-index={__sfIndex}
      data-step-status={status}
      data-step-active={__sfActive ? "true" : "false"}
      data-axis={__sfAxis}
      aria-hidden={__sfActive ? undefined : true}
      {...(__sfActive ? {} : ({ inert: true } as HTMLAttributes<HTMLElement>))}
    >
      <h2
        id={__sfHeadingId}
        ref={__sfHeadingRef}
        className={joinClass(styles.stepHeading, showTitle ? null : styles.srOnly)}
        tabIndex={-1}
        data-testid={`screen-flow-heading-${id}`}
      >
        {label}
      </h2>
      <div className={styles.stepBody}>
        {showSkeleton ? (
          <div
            className={styles.skeleton}
            data-testid={`screen-flow-skeleton-${id}`}
            aria-busy="true"
            aria-label="Загрузка"
          />
        ) : null}
        {showFail ? (
          <p className={styles.failCopy} role="status" data-testid={`screen-flow-fail-${id}`}>
            {FAILURE_COPY[status]}
          </p>
        ) : null}
        {showEmpty ? (
          <div className={styles.emptySlot} data-testid={`screen-flow-empty-${id}`} aria-hidden />
        ) : null}
        {status === "ready" ? children : null}
      </div>
    </section>
  );
}

export function ScreenFlow({
  activeIndex,
  onIndexChange,
  axis = "x",
  children,
  className,
  edgeDeadzonePx = SCREEN_FLOW_EDGE_DEADZONE_PX,
  testId = "screen-flow",
  showChrome = true,
  showStepControls = false,
}: ScreenFlowProps) {
  const reduceMotion = usePrefersReducedMotion();
  const liveId = useId();
  const headingRefs = useRef<Array<HTMLHeadingElement | null>>([]);
  const touchStart = useRef<{ x: number; y: number; edge: boolean } | null>(null);
  const [liveText, setLiveText] = useState("");

  const steps = useMemo(() => {
    const list: ReactElement<ScreenFlowStepProps>[] = [];
    const walk = (nodes: ReactNode) => {
      Children.forEach(nodes, (child) => {
        if (!isValidElement(child)) return;
        if (child.type === ScreenFlowStep) {
          list.push(child as ReactElement<ScreenFlowStepProps>);
          return;
        }
        const nested = (child.props as { children?: ReactNode })?.children;
        if (nested != null) walk(nested);
      });
    };
    walk(children);
    return list;
  }, [children]);

  const count = steps.length;
  const clamped = count === 0 ? 0 : Math.max(0, Math.min(activeIndex, count - 1));

  const goTo = useCallback(
    (next: number, reason: ScreenFlowChangeReason) => {
      if (count === 0) return;
      const target = Math.max(0, Math.min(next, count - 1));
      if (target === clamped) return;
      onIndexChange(target, { reason });
    },
    [clamped, count, onIndexChange],
  );

  useEffect(() => {
    if (count === 0) return;
    const step = steps[clamped];
    const label = step?.props.label ?? "";
    setLiveText(`Шаг ${clamped + 1} из ${count}: ${label}`);
    const heading = headingRefs.current[clamped];
    if (heading) heading.focus({ preventScroll: true });
  }, [clamped, count, steps]);

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const forward = axis === "x" ? e.key === "ArrowRight" || e.key === "PageDown" : e.key === "ArrowDown" || e.key === "PageDown";
    const back = axis === "x" ? e.key === "ArrowLeft" || e.key === "PageUp" : e.key === "ArrowUp" || e.key === "PageUp";
    if (forward) {
      e.preventDefault();
      goTo(clamped + 1, "keyboard");
    } else if (back) {
      e.preventDefault();
      goTo(clamped - 1, "keyboard");
    } else if (e.key === "Home") {
      e.preventDefault();
      goTo(0, "keyboard");
    } else if (e.key === "End") {
      e.preventDefault();
      goTo(count - 1, "keyboard");
    }
  };

  const onTouchStart = (e: TouchEvent) => {
    const t = e.changedTouches[0];
    if (!t) return;
    touchStart.current = {
      x: t.clientX,
      y: t.clientY,
      edge: axis === "x" && t.clientX <= edgeDeadzonePx,
    };
  };

  const onTouchEnd = (e: TouchEvent) => {
    const start = touchStart.current;
    touchStart.current = null;
    if (!start || start.edge) return;
    const t = e.changedTouches[0];
    if (!t) return;
    const dx = t.clientX - start.x;
    const dy = t.clientY - start.y;
    if (axis === "x") {
      if (Math.abs(dx) < SWIPE_THRESHOLD_PX || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0) goTo(clamped + 1, "swipe");
      else goTo(clamped - 1, "swipe");
    } else {
      if (Math.abs(dy) < SWIPE_THRESHOLD_PX || Math.abs(dy) < Math.abs(dx)) return;
      if (dy < 0) goTo(clamped + 1, "swipe");
      else goTo(clamped - 1, "swipe");
    }
  };

  const trackStyle =
    axis === "x"
      ? { transform: `translate3d(${-clamped * 100}%, 0, 0)`, transition: reduceMotion ? "none" : undefined }
      : { transform: `translate3d(0, ${-clamped * 100}%, 0)`, transition: reduceMotion ? "none" : undefined };

  return (
    <div
      className={joinClass(styles.root, className)}
      data-testid={testId}
      data-screen-flow="true"
      data-axis={axis}
      data-active-index={clamped}
      data-reduce-motion={reduceMotion ? "true" : "false"}
    >
      <div className={styles.live} id={liveId} aria-live="polite" aria-atomic="true" data-testid="screen-flow-live">
        {liveText}
      </div>

      {showChrome ? (
        <div
          className={styles.chrome}
          data-controls={showStepControls ? "true" : "false"}
        >
          <div className={styles.dots} role="tablist" aria-label="Шаги">
            {steps.map((step, i) => (
              <button
                key={step.props.id}
                type="button"
                role="tab"
                aria-selected={i === clamped}
                className={i === clamped ? styles.dotActive : styles.dot}
                data-testid={`screen-flow-dot-${i}`}
                onClick={() => goTo(i, "select")}
              >
                <span className={styles.srOnly}>{step.props.label}</span>
              </button>
            ))}
          </div>
          {showStepControls ? (
            <div className={styles.controls}>
              <button
                type="button"
                className={styles.controlBtn}
                data-testid="screen-flow-prev"
                disabled={clamped <= 0}
                onClick={() => goTo(clamped - 1, "prev")}
              >
                Назад
              </button>
              <button
                type="button"
                className={styles.controlBtn}
                data-testid="screen-flow-next"
                disabled={clamped >= count - 1}
                onClick={() => goTo(clamped + 1, "next")}
              >
                Далее
              </button>
            </div>
          ) : null}
        </div>
      ) : null}

      <div
        className={styles.viewport}
        data-testid="screen-flow-viewport"
        tabIndex={0}
        onKeyDown={onKeyDown}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <div
          className={joinClass(styles.track, axis === "x" ? styles.trackX : styles.trackY)}
          data-testid="screen-flow-track"
          style={trackStyle}
        >
          {steps.map((step, i) =>
            cloneElement(step, {
              key: step.props.id,
              __sfIndex: i,
              __sfActive: i === clamped,
              __sfAxis: axis,
              __sfHeadingId: `${liveId}-h-${step.props.id}`,
              __sfHeadingRef: (el: HTMLHeadingElement | null) => {
                headingRefs.current[i] = el;
              },
            }),
          )}
        </div>
      </div>
    </div>
  );
}

/** Ordinary visit → 0. Explicit deep-link only when sf=1|true + step. */
export function resolveScreenFlowEntryIndex(args: {
  searchParams: URLSearchParams | { get(name: string): string | null };
  stepCount: number;
  defaultIndex?: number;
}): number {
  const fallback = args.defaultIndex ?? 0;
  if (args.stepCount <= 0) return 0;
  const intent = (args.searchParams.get("sf") || "").trim().toLowerCase();
  const explicit = intent === "1" || intent === "true" || intent === "yes";
  if (!explicit) return Math.max(0, Math.min(fallback, args.stepCount - 1));
  const raw = args.searchParams.get("step");
  if (raw == null || raw.trim() === "") return fallback;
  const n = Number.parseInt(raw, 10);
  if (!Number.isFinite(n) || n < 0) return fallback;
  return Math.min(n, args.stepCount - 1);
}
