import { Children, useEffect, useRef, useState, type CSSProperties, type ReactElement, type ReactNode } from "react";
import motionStyles from "./profileMotion.module.css";

export function profileMotionStaggerDelay(index: number, baseMs = 0): CSSProperties {
  return { "--pm-stagger": `${baseMs + index * 45}ms` } as CSSProperties;
}

export function ProfileMotionReveal({
  children,
  className,
  delayMs = 0,
  variant = "reveal",
}: {
  children: ReactNode;
  className?: string;
  delayMs?: number;
  variant?: "reveal" | "heroEnter";
}) {
  const motionClass = variant === "heroEnter" ? motionStyles.heroEnter : motionStyles.reveal;
  return (
    <div
      className={[motionClass, className ?? ""].filter(Boolean).join(" ")}
      style={profileMotionStaggerDelay(0, delayMs)}
    >
      {children}
    </div>
  );
}

/** Once-per-element scroll reveal — attach ref + className to the scene root. */
export function useProfileMotionInView<T extends HTMLElement = HTMLElement>(delayMs = 0): {
  ref: React.RefObject<T>;
  className: string;
  style: CSSProperties;
} {
  const ref = useRef<T | null>(null);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const reduce =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
    if (reduce || typeof IntersectionObserver === "undefined") {
      setShown(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setShown(true);
          observer.disconnect();
        }
      },
      { rootMargin: "0px 0px -10% 0px", threshold: 0.14 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return {
    ref: ref as React.RefObject<T>,
    className: shown ? motionStyles.reveal : motionStyles.inViewPending,
    style: profileMotionStaggerDelay(0, delayMs),
  };
}

export function ProfileMotionStagger({
  children,
  className,
  baseDelayMs = 0,
}: {
  children: ReactNode;
  className?: string;
  baseDelayMs?: number;
}) {
  const items = Children.toArray(children).filter(Boolean);
  return (
    <div className={[motionStyles.staggerGroup, className ?? ""].filter(Boolean).join(" ")}>
      {items.map((child, index) => (
        <div
          key={getStaggerKey(child, index)}
          className={motionStyles.staggerItem}
          style={profileMotionStaggerDelay(index, baseDelayMs)}
        >
          {child}
        </div>
      ))}
    </div>
  );
}

export function ProfileMotionExpand({
  open,
  children,
  className,
}: {
  open: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={[motionStyles.expandShell, open ? motionStyles.expandShellOpen : "", className ?? ""].filter(Boolean).join(" ")}>
      <div className={motionStyles.expandInner}>
        {open ? <div className={motionStyles.expandContent}>{children}</div> : null}
      </div>
    </div>
  );
}

function getStaggerKey(child: ReactNode, index: number): string {
  if (typeof child === "object" && child !== null && "key" in child) {
    const key = (child as ReactElement).key;
    if (key != null) return String(key);
  }
  return `stagger-${index}`;
}

export { motionStyles as profileMotionStyles };
