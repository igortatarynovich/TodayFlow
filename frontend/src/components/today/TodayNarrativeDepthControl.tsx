"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import {
  type NarrativeDepthLevel,
  narrativeDepthLabelRu,
} from "@/lib/todayNarrativeDepthUi";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export type TodayNarrativeDepthControlProps = {
  value: NarrativeDepthLevel;
  disabled?: boolean;
  saving?: boolean;
  canPickDeep: boolean;
  onChange: (next: NarrativeDepthLevel) => void;
  style?: CSSProperties;
};

/** DE-8: выбор глубины на экране Today (сервер: `user_settings.today_narrative_depth_level`). */
export function TodayNarrativeDepthControl(props: TodayNarrativeDepthControlProps) {
  const { value, disabled, saving, canPickDeep, onChange, style } = props;
  return (
    <div
      className="todayflow-surface-soft todayflow-inset"
      style={{
        padding: "0.55rem 0.75rem",
        borderRadius: 14,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: "0.5rem 0.75rem",
        ...style,
      }}
    >
      <span className="orbit-body-xs" style={{ color: "#5c4a38", fontWeight: 600 }}>
        {RITUAL_COPY.narrativeDepthControlEyebrow}
      </span>
      <select
        aria-label={RITUAL_COPY.narrativeDepthControlEyebrow}
        value={value}
        disabled={disabled || saving}
        onChange={(e) => onChange(e.target.value as NarrativeDepthLevel)}
        className="orbit-body-xs"
        style={{
          padding: "0.35rem 0.5rem",
          borderRadius: 10,
          border: "1px solid rgba(201,168,115,0.35)",
          background: "rgba(255,255,255,0.92)",
          color: "#2d1f18",
          fontWeight: 600,
          minWidth: "9.5rem",
        }}
      >
        <option value="quick">{narrativeDepthLabelRu("quick")}</option>
        <option value="normal">{narrativeDepthLabelRu("normal")}</option>
        {canPickDeep ? <option value="deep">{narrativeDepthLabelRu("deep")}</option> : null}
      </select>
      {saving ? (
        <span className="orbit-body-xs" style={{ color: "#7a6a52" }}>
          {RITUAL_COPY.narrativeDepthControlSaving}
        </span>
      ) : (
        <span className="orbit-body-xs" style={{ color: "#7a6a52", lineHeight: 1.45 }}>
          {RITUAL_COPY.narrativeDepthControlHint}
        </span>
      )}
      <Link
        href="/account/settings#today-narrative-depth-settings"
        className="orbit-body-xs"
        style={{ color: "#8a4a1b", fontWeight: 600, marginLeft: "auto" }}
      >
        {RITUAL_COPY.narrativeDepthControlAllSettingsCta}
      </Link>
    </div>
  );
}
