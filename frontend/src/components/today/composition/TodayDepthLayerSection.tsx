"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import type { TodayContractDepthLayerV1, TodayDepthTopicId } from "@/lib/todayContract";
import { fetchTodayNarrativeCached } from "@/lib/todayNarrativeCache";
import { narrativeString, narrativeStringArray } from "@/lib/todayNarrativeApi";
import styles from "@/components/today/composition/TodayDepthLayerSection.module.css";

type Props = {
  dateISO: string;
  depthLayer: TodayContractDepthLayerV1;
  guideGenerationId?: number | null;
  /** Prefer this topic when CTA lands here (must be in menu). */
  preferredTopic?: TodayDepthTopicId | string | null;
  /** When true, auto-fetch preferredTopic once per topic value. */
  autoPickPreferred?: boolean;
};

function formatDeepenPayload(payload: Record<string, unknown> | null | undefined): string {
  if (!payload) return "";
  const title = narrativeString(payload.title);
  const body = narrativeString(payload.body);
  const bullets = narrativeStringArray(payload.bullets, []);
  const closing = narrativeString(payload.closing_line);
  const chunks: string[] = [];
  if (title) chunks.push(title);
  if (body) chunks.push(body);
  if (bullets.length) chunks.push(bullets.map((b) => `• ${b}`).join("\n"));
  if (closing) chunks.push(closing);
  return chunks.join("\n\n").trim();
}

export function TodayDepthLayerSection({
  dateISO,
  depthLayer,
  guideGenerationId = null,
  preferredTopic = null,
  autoPickPreferred = false,
}: Props) {
  const menu = Array.isArray(depthLayer.menu) ? depthLayer.menu : [];
  const canGenerate = Boolean(depthLayer.can_generate);
  const [activeTopic, setActiveTopic] = useState<TodayDepthTopicId | null>(null);
  const [loading, setLoading] = useState(false);
  const [resultText, setResultText] = useState<string | null>(null);
  const [isCta, setIsCta] = useState(false);
  const autoPickedRef = useRef<string | null>(null);

  const onPick = useCallback(
    async (topic: TodayDepthTopicId) => {
      setActiveTopic(topic);
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
          { force: true },
        );
        const meta = r.payload?.depth_layer;
        const access =
          meta && typeof meta === "object" && !Array.isArray(meta)
            ? String((meta as { access?: unknown }).access || "")
            : "";
        setIsCta(access === "cta" || !canGenerate);
        const text = formatDeepenPayload(r.payload);
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

  if (menu.length === 0) return null;

  return (
    <section className={styles.root} data-testid="today-depth-layer">
      <h2 className={styles.title}>Разобрать тему точнее</h2>
      <div className={styles.chips} role="list">
        {menu.map((row) => {
          const topic = row.topic as TodayDepthTopicId;
          const selected = activeTopic === topic;
          return (
            <button
              key={topic}
              type="button"
              role="listitem"
              className={selected ? styles.chipActive : styles.chip}
              disabled={loading}
              onClick={() => void onPick(topic)}
              data-testid={`today-depth-topic-${topic}`}
            >
              <span className={styles.chipLabel}>{row.label}</span>
              {row.value ? <span className={styles.chipValue}>{row.value}</span> : null}
            </button>
          );
        })}
      </div>
      {loading ? <p className={styles.status}>Собираем разбор…</p> : null}
      {resultText ? (
        <div
          className={isCta ? styles.resultCta : styles.result}
          data-testid="today-depth-layer-result"
        >
          <p className={styles.resultBody}>{resultText}</p>
          {isCta ? (
            <Link
              href={depthLayer.subscribe_path || "/account/subscriptions"}
              className={styles.subscribeLink}
            >
              Подписка и trial
            </Link>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
