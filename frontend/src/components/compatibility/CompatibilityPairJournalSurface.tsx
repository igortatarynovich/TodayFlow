"use client";

import { useMemo } from "react";
import { CompatibilityExplorationResult } from "@/components/compatibility/CompatibilityExplorationResult";
import { buildExplorationFromPairInput } from "@/lib/buildCompatibilityExplorationModel";
import type { CompatibilityPairReportModel } from "@/lib/buildCompatibilityPairReportModel";

type CompatibilityPairJournalSurfaceProps = {
  model: CompatibilityPairReportModel;
  scenarioId?: string;
  onRefresh?: () => void;
  refreshing?: boolean;
  guidanceHref?: string;
  onGuidanceClick?: () => void;
};

export function CompatibilityPairJournalSurface({
  model,
  scenarioId = "love",
  onRefresh,
  refreshing,
  onGuidanceClick,
}: CompatibilityPairJournalSurfaceProps) {
  const explorationModel = useMemo(
    () =>
      buildExplorationFromPairInput(
        {
          name1: model.pairLine.split("❤️")[0]?.trim() || model.pairLine.split("×")[0]?.trim() || "Ты",
          name2: model.pairLine.split("❤️")[1]?.trim() || model.pairLine.split("×")[1]?.trim() || "Партнёр",
          overallScore: model.score,
          summary: model.mainConclusion,
          aspects: [],
          editorial: { pair_thesis: model.mainConclusion },
          deepDive: {
            dimensions: model.sections.slice(0, 8).map((s) => ({
              key: s.id,
              label: s.title,
              score: model.score,
              summary: s.body,
              indicators: s.bullets,
            })),
            strengths: model.sections.find((s) => s.id === "tips")?.bullets,
            guidance: model.sections.find((s) => s.id === "tips")?.body ? [model.sections.find((s) => s.id === "tips")!.body] : [],
          },
          recommendations: model.sections.find((s) => s.id === "tips")?.bullets,
        },
        scenarioId,
      ),
    [model, scenarioId],
  );

  return (
    <CompatibilityExplorationResult
      model={{
        ...explorationModel,
        pairLine: model.pairLine.replace("❤️", "×"),
        mainThought: model.mainConclusion,
        score: model.score,
        scoreLabel: model.scoreLabel,
        deepSections: model.sections.map((s) => ({
          id: s.id,
          title: s.title,
          takeaway: s.body,
          detail: s.bullets?.join(" · "),
        })),
      }}
      onRefresh={onRefresh}
      refreshing={refreshing}
      guidancePrefill={null}
    />
  );
}
