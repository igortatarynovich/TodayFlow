"use client";

import styles from "@/components/today/composition/TodayHookRevealShell.module.css";

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
  instruction?: string | null;
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
};

/**
 * Shared shell: base (static) → bridge | fail → instruction.
 * Never invents bridge prose when unavailable.
 */
export function TodayHookRevealShell({
  kindLabel,
  title,
  subtitle = null,
  hook = null,
  fallbackBody = null,
  testId,
}: Props) {
  const baseMeaning = hook?.base?.meaning?.trim() || null;
  const bridgeOk = hook?.bridge_status === "ok" && Boolean(hook?.bridge_to_day?.trim());
  const bridgeFail =
    hook && hook.bridge_status === "unavailable"
      ? (hook.bridge_fail_copy || "Не удалось раскрыть день.").trim()
      : null;
  const instruction = hook?.instruction?.trim() || null;
  const orientation =
    hook?.identity?.orientation === "reversed"
      ? "перевёрнутая"
      : hook?.identity?.orientation === "upright"
        ? "прямая"
        : null;

  return (
    <section className={styles.root} data-testid={testId} data-hook-kind={hook?.kind || undefined}>
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
          <p className={styles.layerBody}>{hook!.bridge_to_day}</p>
        </div>
      ) : bridgeFail ? (
        <p className={styles.fail} role="status" data-bridge-status="unavailable">
          {bridgeFail}
        </p>
      ) : null}

      {instruction && bridgeOk ? (
        <div className={styles.layer} data-layer="instruction">
          <p className={styles.layerLabel}>Как применить</p>
          <p className={styles.layerBody}>{instruction}</p>
        </div>
      ) : null}
    </section>
  );
}
