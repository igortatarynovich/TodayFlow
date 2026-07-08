"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActionObject,
  DisclosureLine,
  PageShell,
  PortalPreview,
  ProgressLine,
  SceneHeader,
  SceneStack,
  todayFlowSceneStyles,
} from "@/components/foundation/TodayFlowScene";
import {
  buildTodayExperienceActionLine,
  buildTodayExperienceProgress,
  buildTodayExperienceTheme,
} from "@/components/today/todayExperienceModel";
import { parseCoreMessageForUi } from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

type Props = {
  displayDate: string;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  themeHeadlineFallback: string;
  actionFallback: readonly string[];
  actionDoneInitial?: boolean;
  streakDays?: number;
  cardName?: string | null;
  numerologyValue?: string | null;
  moonName?: string | null;
  currentHour: number;
  eveningReflectionInput: string;
  eveningSaving: boolean;
  eveningDone: boolean;
  onActionComplete?: () => void;
  onVisible?: () => void;
  onEveningReflectionChange: (value: string) => void;
  onSaveEvening: () => void;
};

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function compactDateLabel(displayDate: string) {
  return `${RITUAL_COPY.todayExperienceDayEyebrow} · ${displayDate}`.toUpperCase();
}

function markerValueFromMeta(meta: string | null, kind: "tempo" | "risk") {
  if (!meta) return null;
  const parts = meta.split("·").map((p) => p.trim()).filter(Boolean);
  if (kind === "tempo") {
    const part = parts.find((p) => /темп/i.test(p));
    return part?.replace(/темп/gi, "").trim().toLowerCase() || null;
  }
  const risk = parts.find((p) => /риск/i.test(p));
  return risk?.replace(/^риск\s*[—:-]?\s*/i, "").trim().toLowerCase() || null;
}

function actionReason(payload: Record<string, unknown> | null | undefined) {
  const raw = payload?.action_options;
  if (Array.isArray(raw)) {
    const first = raw[0];
    if (first && typeof first === "object" && !Array.isArray(first)) {
      const o = first as Record<string, unknown>;
      const reason = typeof o.reason === "string" ? o.reason.trim() : typeof o.why === "string" ? o.why.trim() : "";
      if (reason) return reason;
    }
  }
  return RITUAL_COPY.todayExperienceActionBodyFallback;
}

function whyLines({
  payload,
  cardName,
  numerologyValue,
  moonName,
}: {
  payload: Record<string, unknown> | null;
  cardName?: string | null;
  numerologyValue?: string | null;
  moonName?: string | null;
}) {
  const lines: string[] = [];
  const card = cardName && cardName !== RITUAL_COPY.cardEyebrow ? cardName : null;
  const number = numerologyValue && numerologyValue !== "—" ? numerologyValue : null;
  if (card) lines.push(`Карта дня: ${card}. Держи фокус на интеграции, а не на рывке.`);
  if (number) lines.push(`Число дня ${number} поддерживает завершение одного понятного шага.`);
  if (moonName) lines.push(`Луна: ${moonName}. Темп лучше держать ровным.`);

  const core = parseCoreMessageForUi(payload);
  if (core?.kind === "structured") {
    if (core.body && lines.length < 3) lines.push(core.body);
    if (core.risk && lines.length < 3) lines.push(`Главный риск: ${core.risk}.`);
  } else if (core?.kind === "paragraphs") {
    for (const p of core.paragraphs) {
      if (lines.length >= 3) break;
      lines.push(p);
    }
  }

  if (!lines.length) {
    lines.push(RITUAL_COPY.todayExperienceWhyFallback);
  }
  return lines.slice(0, 3);
}

export function TodayDailySurface({
  displayDate,
  guideNarrativeLoading,
  guideNarrativePayload,
  themeHeadlineFallback,
  actionFallback,
  actionDoneInitial = false,
  streakDays = 0,
  cardName,
  numerologyValue,
  moonName,
  currentHour,
  eveningReflectionInput,
  eveningSaving,
  eveningDone,
  onActionComplete,
  onVisible,
  onEveningReflectionChange,
  onSaveEvening,
}: Props) {
  const [actionDone, setActionDone] = useState(actionDoneInitial);

  useEffect(() => {
    setActionDone(actionDoneInitial);
  }, [actionDoneInitial]);

  useEffect(() => {
    onVisible?.();
  }, [onVisible]);

  const theme = useMemo(
    () => buildTodayExperienceTheme(guideNarrativePayload, themeHeadlineFallback),
    [guideNarrativePayload, themeHeadlineFallback],
  );
  const actionLine = useMemo(
    () => buildTodayExperienceActionLine(guideNarrativePayload, actionFallback),
    [guideNarrativePayload, actionFallback],
  );
  const progress = useMemo(
    () => buildTodayExperienceProgress({ actionDone: actionDone || eveningDone, streakDays }),
    [actionDone, eveningDone, streakDays],
  );
  const markers = useMemo(() => {
    const tempo = markerValueFromMeta(theme.meta, "tempo") || RITUAL_COPY.todayExperienceTempoMarkerFallback;
    const risk = markerValueFromMeta(theme.meta, "risk") || RITUAL_COPY.todayExperienceRiskMarkerFallback;
    return [
      { label: RITUAL_COPY.todayExperienceTempoMarkerLabel, value: tempo },
      { label: RITUAL_COPY.todayExperienceRiskMarkerLabel, value: risk },
    ];
  }, [theme.meta]);
  const lead =
    narrativeString(guideNarrativePayload, "subline") ||
    (parseCoreMessageForUi(guideNarrativePayload)?.kind === "structured"
      ? (parseCoreMessageForUi(guideNarrativePayload) as { kind: "structured"; body: string }).body
      : null) ||
    RITUAL_COPY.todayExperienceHeroLeadFallback;
  const why = useMemo(
    () => whyLines({ payload: guideNarrativePayload, cardName, numerologyValue, moonName }),
    [guideNarrativePayload, cardName, numerologyValue, moonName],
  );
  const symbolFacts = [
    cardName && cardName !== RITUAL_COPY.cardEyebrow ? { label: RITUAL_COPY.todayExperienceSymbolCardLabel, value: cardName } : null,
    numerologyValue && numerologyValue !== "—"
      ? { label: RITUAL_COPY.todayExperienceSymbolNumberLabel, value: numerologyValue }
      : null,
    moonName ? { label: RITUAL_COPY.todayExperienceSymbolMoonLabel, value: moonName } : null,
  ].filter(Boolean) as Array<{ label: string; value: string }>;

  const eveningMode = currentHour >= 18;

  const onMarkDone = useCallback(() => {
    if (actionDone) return;
    setActionDone(true);
    onActionComplete?.();
  }, [actionDone, onActionComplete]);

  return (
    <PageShell>
      <SceneStack>
        <SceneHeader
          eyebrow={compactDateLabel(displayDate)}
          title={guideNarrativeLoading ? RITUAL_COPY.todayExperienceThemeFallback : theme.headline}
          lead={lead}
          markers={markers}
        />

        {eveningMode ? (
          <ActionObject
            eyebrow={RITUAL_COPY.todayExperienceEveningEyebrow}
            title={RITUAL_COPY.todayExperienceEveningTitle}
            body={RITUAL_COPY.todayExperienceEveningQuestion}
          >
            <textarea
              className={todayFlowSceneStyles.textarea}
              value={eveningReflectionInput}
              onChange={(event) => onEveningReflectionChange(event.target.value)}
              placeholder={RITUAL_COPY.todayExperienceEveningPlaceholder}
              aria-label={RITUAL_COPY.todayExperienceEveningQuestion}
            />
            <button
              type="button"
              className="orbit-button orbit-button-primary"
              onClick={onSaveEvening}
              disabled={eveningSaving}
            >
              {eveningSaving ? RITUAL_COPY.todayExperienceEveningSavingCta : RITUAL_COPY.todayExperienceEveningCta}
            </button>
          </ActionObject>
        ) : (
          <ActionObject eyebrow={RITUAL_COPY.todayExperienceActionLabel} title={actionLine} body={actionReason(guideNarrativePayload)}>
            <button
              type="button"
              onClick={onMarkDone}
              disabled={guideNarrativeLoading || actionDone}
              className="orbit-button orbit-button-primary"
            >
              {actionDone ? RITUAL_COPY.todayExperienceActionDoneCta : RITUAL_COPY.todayExperienceActionCta}
            </button>
          </ActionObject>
        )}

        <ProgressLine
          active={actionDone || eveningDone}
          primary={eveningMode && (actionDone || eveningDone) ? RITUAL_COPY.todayExperienceEveningProgressDone : progress.primary}
          secondary={progress.secondary}
        />

        <DisclosureLine summary={RITUAL_COPY.todayExperienceWhySummary}>
          {why.map((line) => (
            <p key={line}>{line}</p>
          ))}
        </DisclosureLine>

        <PortalPreview
          eyebrow={RITUAL_COPY.todayExperienceSymbolEyebrow}
          facts={symbolFacts}
          links={[
            { href: "/profile", label: RITUAL_COPY.todayExperienceDepthProfile },
            { href: "/calendar", label: RITUAL_COPY.todayExperienceDepthCalendar },
            { href: "/tarot", label: RITUAL_COPY.todayExperienceDepthTarot },
          ]}
        />
      </SceneStack>
    </PageShell>
  );
}
