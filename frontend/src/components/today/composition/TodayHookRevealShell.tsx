"use client";

import styles from "@/components/today/composition/TodayHookRevealShell.module.css";
import { DsCard } from "@/design-system/primitives/DsCard";
import { asTrimmedText, formatColorWhereToUse } from "@/lib/hookRevealText";

export type HookRevealPayload = {
  kind?: string;
  identity?: {
    id?: number;
    name_ru?: string | null;
    orientation?: string | null;
    value?: number;
    title?: string | null;
    name?: string | null;
  };
  base?: { meaning?: string | null; keywords?: string[]; name?: string | null } | null;
  bridge_to_day?: string | null;
  bridge_status?: "ok" | "unavailable" | string;
  bridge_fail_copy?: string | null;
  /** String SoT; object where_to_use may leak before symbols hydrate — coerced safely. */
  instruction?: string | Record<string, unknown> | null;
  instruction_status?: string;
};

type Props = {
  kindLabel: string;
  title: string;
  subtitle?: string | null;
  hook?: HookRevealPayload | null;
  /** Fallback body when hook_reveal absent (legacy impact). */
  fallbackBody?: string | null;
  testId: string;
  /** Visual differentiation — tarot image accent vs numerology digit. */
  variant?: "tarot" | "numerology" | "default";
};

/**
 * Shared shell: base (static) → bridge | fail → instruction.
 * Never invents bridge prose when unavailable.
 * Surface: Today Block = DsCard glass compact (FOUNDATION_UI §16).
 */
export function TodayHookRevealShell({
  kindLabel,
  title,
  subtitle = null,
  hook = null,
  fallbackBody = null,
  testId,
  variant = "default",
}: Props) {
  const baseMeaning = asTrimmedText(hook?.base?.meaning);
  const bridgeText = asTrimmedText(hook?.bridge_to_day);
  const bridgeOk = hook?.bridge_status === "ok" && Boolean(bridgeText);
  const bridgeFail =
    hook && hook.bridge_status === "unavailable"
      ? asTrimmedText(hook.bridge_fail_copy) || "Не удалось раскрыть день."
      : null;
  const instruction =
    asTrimmedText(hook?.instruction) || formatColorWhereToUse(hook?.instruction);
  // v3.1: card/number have no instruction slot (Move owns action; color apply lives on Move guide).
  const showInstruction = Boolean(instruction && bridgeOk && hook?.kind === "color");
  const orientation =
    hook?.identity?.orientation === "reversed"
      ? "перевёрнутая"
      : hook?.identity?.orientation === "upright"
        ? "прямая"
        : null;

  return (
    <DsCard
      variant="glass"
      size="compact"
      as="section"
      className={`${styles.root} ${variant === "tarot" ? styles.variantTarot : ""} ${variant === "numerology" ? styles.variantNumerology : ""}`.trim()}
      testId={testId}
    >
      <div data-hook-kind={hook?.kind || undefined} data-hook-variant={variant !== "default" ? variant : undefined}>
        <p className={styles.kind}>{kindLabel}</p>
        <h2 className={styles.title}>
          {title}
          {orientation ? <span className={styles.orient}> · {orientation}</span> : null}
        </h2>
        {subtitle ? <p className={styles.subtitle}>{subtitle}</p> : null}

        {baseMeaning ? (
          <div className={styles.layer} data-layer="base">
            <p className={styles.layerLabel}>Значение</p>
            <p className={styles.layerBody}>{baseMeaning}</p>
          </div>
        ) : fallbackBody ? (
          <p className={styles.layerBody}>{fallbackBody}</p>
        ) : null}

        {bridgeOk ? (
          <div className={styles.layer} data-layer="bridge">
            <p className={styles.layerLabel}>Почему сегодня</p>
            <p className={styles.layerBody}>{bridgeText}</p>
          </div>
        ) : bridgeFail ? (
          <p className={styles.fail} role="status" data-bridge-status="unavailable">
            {bridgeFail}
          </p>
        ) : null}

        {showInstruction ? (
          <div className={styles.layer} data-layer="instruction">
            <p className={styles.layerLabel}>Как применить</p>
            <p className={styles.layerBody}>{instruction}</p>
          </div>
        ) : null}
      </div>
    </DsCard>
  );
}
