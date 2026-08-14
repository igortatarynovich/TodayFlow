"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import type { TodayContractDepthLayerV1, TodayDepthTopicId } from "@/lib/todayContract";
import { fetchTodayNarrativeCached } from "@/lib/todayNarrativeCache";
import { narrativeString, narrativeStringArray } from "@/lib/todayNarrativeApi";
import { DsButton, DsChip, DsChipCluster, DsOverlaySheet } from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";

type Props = {
  dateISO: string;
  depthLayer: TodayContractDepthLayerV1;
  guideGenerationId?: number | null;
  preferredTopic?: TodayDepthTopicId | string | null;
  autoPickPreferred?: boolean;
  isActive?: boolean;
};

function formatDeepenBrief(payload: Record<string, unknown> | null | undefined): string {
  if (!payload) return "";
  const title = narrativeString(payload.title);
  const body = narrativeString(payload.body);
  const bullets = narrativeStringArray(payload.bullets, []);
  const closing = narrativeString(payload.closing_line);

  const why =
    (body ? firstSentences(body, 2) : null) ||
    (bullets[0] ? firstSentences(bullets[0], 1) : null) ||
    (closing ? firstSentences(closing, 1) : null);

  const chunks: string[] = [];
  if (title) chunks.push(title);
  if (why && why !== title) chunks.push(why);
  return chunks.join("\n\n").trim();
}

function firstSentences(text: string, max: number): string {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (!cleaned) return "";
  const parts = cleaned.split(/(?<=[.!?…])\s+/).filter(Boolean);
  const take = parts.slice(0, Math.max(1, max)).join(" ");
  if (take.length <= 280) return take;
  return `${take.slice(0, 277).trimEnd()}…`;
}

function shortLabel(label: string, value?: string | null): string {
  const base = label.replace(/\s+/g, " ").trim();
  if (!value) return base.length > 42 ? `${base.slice(0, 40)}…` : base;
  const head = base.split(/[—–-]/)[0]?.trim() || base;
  return head.length > 28 ? `${head.slice(0, 26)}…` : head;
}

/**
 * Depth topics as Form Kit chips; detail = opaque overlay sheet.
 */
export function TodayDepthLayerSection({
  dateISO,
  depthLayer,
  guideGenerationId = null,
  preferredTopic = null,
  autoPickPreferred = false,
  isActive = true,
}: Props) {
  const menu = Array.isArray(depthLayer.menu) ? depthLayer.menu : [];
  const canGenerate = Boolean(depthLayer.can_generate);
  const [activeTopic, setActiveTopic] = useState<TodayDepthTopicId | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resultText, setResultText] = useState<string | null>(null);
  const [isCta, setIsCta] = useState(false);
  const autoPickedRef = useRef<string | null>(null);
  const titleId = useId();

  const onPick = useCallback(
    async (topic: TodayDepthTopicId) => {
      setActiveTopic(topic);
      setPanelOpen(true);
      setLoading(true);
      setResultText(null);
      setIsCta(false);
      try {
        const r = await fetchTodayNarrativeCached(
          {
            target_date: dateISO,
            surface: "deepen",
            deepen_topic: topic,
            parent_generation_id: guideGenerationId ?? undefined,
          },
          { force: false },
        );
        const meta = r.payload?.depth_layer;
        const access =
          meta && typeof meta === "object" && !Array.isArray(meta)
            ? String((meta as { access?: unknown }).access || "")
            : "";
        setIsCta(access === "cta" || !canGenerate);
        const text = formatDeepenBrief(r.payload);
        setResultText(
          text ||
            (canGenerate
              ? "Не удалось собрать разбор. Попробуйте ещё раз."
              : "Тематический разбор доступен в подписке."),
        );
      } catch {
        setResultText("Не удалось загрузить разбор. Попробуйте позже.");
        setIsCta(!canGenerate);
      } finally {
        setLoading(false);
      }
    },
    [canGenerate, dateISO, guideGenerationId],
  );

  useEffect(() => {
    if (!autoPickPreferred || !preferredTopic || menu.length === 0) return;
    const topic = String(preferredTopic).trim();
    if (!topic || autoPickedRef.current === topic) return;
    const inMenu = menu.some((row) => String(row.topic) === topic);
    if (!inMenu) return;
    autoPickedRef.current = topic;
    void onPick(topic as TodayDepthTopicId);
  }, [autoPickPreferred, preferredTopic, menu, onPick]);

  useEffect(() => {
    if (!isActive) {
      setPanelOpen(false);
      setLoading(false);
    }
  }, [isActive]);

  if (menu.length === 0) return null;
  if (!isActive) return null;

  const activeLabel =
    menu.find((row) => row.topic === activeTopic)?.label ??
    (activeTopic ? String(activeTopic) : "");

  return (
    <section className={layout.stack} data-testid="today-depth-layer">
      <DsChipCluster>
        {menu.map((row) => {
          const topic = row.topic as TodayDepthTopicId;
          const selected = activeTopic === topic && panelOpen;
          return (
            <DsChip
              key={topic}
              selected={selected}
              disabled={loading && activeTopic === topic}
              onClick={() => void onPick(topic)}
              testId={`today-depth-topic-${topic}`}
            >
              {shortLabel(row.label, row.value)}
            </DsChip>
          );
        })}
      </DsChipCluster>

      {panelOpen ? (
        <DsOverlaySheet
          testId="today-depth-layer-overlay"
          titleId={titleId}
          title={activeLabel}
          body={loading ? "…" : resultText || ""}
          closeLabel="Закрыть"
          onClose={() => setPanelOpen(false)}
          footer={
            <>
              {resultText ? (
                <span data-testid="today-depth-layer-result" hidden>
                  {resultText}
                </span>
              ) : null}
              {isCta && !loading ? (
                <DsButton href={depthLayer.subscribe_path || "/account/subscriptions"}>
                  Подписка и trial
                </DsButton>
              ) : null}
            </>
          }
        />
      ) : null}
    </section>
  );
}
