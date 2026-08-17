"use client";

import type { ReactNode } from "react";
import { DsBody, DsCard, DsCaption, DsDisplayTitle, DsEyebrow, DsHeadline } from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
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
  /** Optional dominate visual (e.g. tarot face kept after pick). */
  visual?: ReactNode;
};

/**
 * Shared shell: base (static) → bridge | fail → instruction.
 * Never invents bridge prose when unavailable.
 * Form Kit: DsCard glass + typography (FOUNDATION_UI §15.8 / §16).
 */
export function TodayHookRevealShell({
  kindLabel,
  title,
  subtitle = null,
  hook = null,
  fallbackBody = null,
  testId,
  variant = "default",
  visual = null,
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

  const titleText = orientation ? `${title} · ${orientation}` : title;

  return (
    <DsCard
      tone="glass"
      size="compact"
      as="section"
      className={layout.centerStack}
      testId={testId}
    >
      <div
        className={layout.centerStack}
        data-hook-kind={hook?.kind || undefined}
        data-hook-variant={variant !== "default" ? variant : undefined}
      >
        <DsEyebrow>{kindLabel}</DsEyebrow>
        {visual ? <div className={layout.hookVisual}>{visual}</div> : null}
        {variant === "numerology" ? (
          <DsDisplayTitle as="h2" size="xl">
            {titleText}
          </DsDisplayTitle>
        ) : (
          <DsHeadline as="h2">{titleText}</DsHeadline>
        )}
        {subtitle ? (
          <DsBody size="sm" muted>
            {subtitle}
          </DsBody>
        ) : null}

        {baseMeaning ? (
          <div className={layout.stackTight} data-layer="base">
            <DsCaption muted>Значение</DsCaption>
            <DsBody size="sm">
              {baseMeaning}
            </DsBody>
          </div>
        ) : fallbackBody ? (
          <DsBody size="sm">{fallbackBody}</DsBody>
        ) : null}

        {bridgeOk ? (
          <div className={layout.stackTight} data-layer="bridge">
            <DsCaption muted>Почему сегодня</DsCaption>
            <DsBody size="sm">{bridgeText}</DsBody>
          </div>
        ) : bridgeFail ? (
          <div role="status" data-bridge-status="unavailable">
            <DsBody size="sm" muted>
              {bridgeFail}
            </DsBody>
          </div>
        ) : null}

        {showInstruction ? (
          <div className={layout.stackTight} data-layer="instruction">
            <DsCaption muted>Как применить</DsCaption>
            <DsBody size="sm">{instruction}</DsBody>
          </div>
        ) : null}
      </div>
    </DsCard>
  );
}
