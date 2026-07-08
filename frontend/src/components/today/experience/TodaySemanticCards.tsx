"use client";

import type { TodaySemanticBlocks } from "@/lib/todayExperienceSemantic";
import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";

type Props = {
  blocks: TodaySemanticBlocks;
};

export function TodaySemanticCards({ blocks }: Props) {
  const hasManifestations = blocks.manifestations.length > 0;
  const hasQuestion = Boolean(blocks.question?.prompt);

  if (!hasManifestations && !hasQuestion) return null;

  return (
    <div
      data-testid="today-semantic-cards"
      style={{ display: "flex", flexDirection: "column", gap: "0.55rem" }}
    >
      {hasManifestations ? (
        <section
          className="todayflow-surface-soft todayflow-inset"
          data-testid="today-semantic-manifestations"
          style={{
            padding: "0.9rem 1rem",
            borderRadius: 14,
            border: "1px solid rgba(201,168,115,0.18)",
            background: "rgba(255,250,245,0.92)",
          }}
        >
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem" }}>
            {TODAY_CONTRACT_COPY.narrativeManifestationsEyebrow}
          </p>
          <ul style={{ margin: 0, padding: "0 0 0 1.1rem", color: "#2d241c" }}>
            {blocks.manifestations.map((line) => (
              <li key={line} className="orbit-body-sm" style={{ margin: "0.2rem 0", lineHeight: 1.5 }}>
                {line}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {hasQuestion && blocks.question ? (
        <section
          className="todayflow-surface-soft todayflow-inset"
          data-testid="today-semantic-question"
          style={{
            padding: "0.9rem 1rem",
            borderRadius: 14,
            border: "1px solid rgba(201,168,115,0.18)",
            background: "rgba(255,250,245,0.92)",
          }}
        >
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem" }}>
            {TODAY_CONTRACT_COPY.experienceQuestionEyebrow}
          </p>
          <p className="orbit-body" style={{ margin: 0, lineHeight: 1.55, color: "#2d241c", fontWeight: 600 }}>
            {blocks.question.prompt}
          </p>
          {blocks.question.options[0]?.response ? (
            <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a623d", lineHeight: 1.45 }}>
              {blocks.question.options[0].response}
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
