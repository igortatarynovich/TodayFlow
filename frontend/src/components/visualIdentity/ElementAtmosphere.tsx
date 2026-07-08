"use client";

import type { ComponentPropsWithoutRef, CSSProperties, ElementType, ReactNode } from "react";
import type { Element } from "@/lib/zodiac-utils";
import { elementPatternAssetPath } from "@/lib/visualIdentity/registry";
import styles from "./elementAtmosphere.module.css";

export type ElementAtmosphereProps<T extends ElementType = "div"> = {
  element: Element | null;
  children: ReactNode;
  className?: string;
  as?: T;
} & Omit<ComponentPropsWithoutRef<T>, "className" | "children">;

const CLASS: Record<Element, string> = {
  Fire: styles.fire,
  Earth: styles.earth,
  Air: styles.air,
  Water: styles.water,
};

export function ElementAtmosphere<T extends ElementType = "div">({
  element,
  children,
  className,
  as,
  ...rest
}: ElementAtmosphereProps<T>) {
  const Tag = (as ?? "div") as ElementType;
  const tone = element ? CLASS[element] : styles.neutral;
  const patternStyle: CSSProperties | undefined = element
    ? ({ ["--tf-element-pattern" as string]: `url(${elementPatternAssetPath(element)})` } as CSSProperties)
    : undefined;

  return (
    <Tag
      className={[styles.wrap, tone, className].filter(Boolean).join(" ")}
      style={patternStyle}
      data-element={element ?? undefined}
      {...rest}
    >
      {children}
    </Tag>
  );
}
