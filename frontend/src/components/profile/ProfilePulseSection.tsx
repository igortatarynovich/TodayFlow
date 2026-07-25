"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import type { CoreProfile } from "@/lib/types";
import { livingClarityLabel, livingClosureLabel } from "@/components/profile/livingLabels";
import { ProfileSurfacePanel, ProfileSurfaceTile, profileSurfaceStyles } from "@/components/profile/ProfileSurface";
import { scrubUserFacingText } from "@/lib/todayValueGate";

type Living = NonNullable<CoreProfile["living"]>;

function isLivingSparse(living: Living | null | undefined) {
  if (!living) return true;
  const days = living.signal_profile?.signals_days ?? 0;
  const insights = Array.isArray(living.recent_insights) ? living.recent_insights.length : 0;
  const week = living.weekly_state?.integration_text?.trim();
  const ctx = living.learning_context;
  return days < 1 && insights < 1 && !week && !ctx;
}

function LivingStatTile({ label, children }: { label: string; children: ReactNode }) {
  return (
    <ProfileSurfaceTile tone="sm" className={profileSurfaceStyles.tileSolid}>
      <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        {label}
      </p>
      <p className="orbit-body-sm" style={{ margin: "0.4rem 0 0", color: "#334155", lineHeight: 1.7 }}>
        {children}
      </p>
    </ProfileSurfaceTile>
  );
}

function isRawFocusKey(focus: string | null | undefined): boolean {
  const t = (focus ?? "").trim();
  return Boolean(t && /^[a-z][a-z0-9_]{0,32}$/.test(t));
}

export function ProfilePulseSection({ living }: { living: Living | null | undefined }) {
  const livingProfile = living;
  const sparse = isLivingSparse(livingProfile);

  if (sparse || !livingProfile) {
    // Missing depth → absence CTA, not pipeline status (Voice §0.05–0.06).
    return (
      <ProfileSurfacePanel eyebrow="Как это проявляется сейчас" panelClass="living">
        <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a", fontWeight: 700, lineHeight: 1.65 }}>
          Повторяющиеся жизненные закономерности проявляются через отмеченные дни — ответы, действия и вечернюю фиксацию.
        </p>
        <div style={{ marginTop: "0.85rem" }}>
          <Link href="/today" className="orbit-button orbit-button-primary orbit-button-sm" style={{ textDecoration: "none" }}>
            Открыть Today
          </Link>
        </div>
      </ProfileSurfacePanel>
    );
  }

  const livingSignals = livingProfile.signal_profile;
  const livingWeeklyState = livingProfile.weekly_state;
  const livingInsights = Array.isArray(livingProfile.recent_insights) ? livingProfile.recent_insights : [];
  const learningContext = livingProfile.learning_context;

  const summary = scrubUserFacingText(livingProfile.summary);
  const closure = livingClosureLabel(livingSignals?.closure_state);
  const clarity = livingClarityLabel(livingSignals?.clarity_state);
  const focusRaw = livingSignals?.dominant_focus?.trim() || "";
  const focus = !isRawFocusKey(focusRaw) ? scrubUserFacingText(focusRaw) : null;
  const weekText = scrubUserFacingText(livingWeeklyState?.integration_text);
  const safeInsights = livingInsights
    .map((item) => ({ ...item, text: scrubUserFacingText(item.text) }))
    .filter((item): item is typeof item & { text: string } => Boolean(item.text));

  const hasBody = Boolean(summary || closure || clarity || focus || weekText || safeInsights.length);
  if (!hasBody) {
    return null;
  }

  return (
    <ProfileSurfacePanel eyebrow="Как это проявляется сейчас" panelClass="living">
      {summary ? (
        <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a", fontWeight: 700 }}>
          {summary}
        </p>
      ) : null}
      <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginTop: summary ? "0.85rem" : 0 }}>
        {(livingSignals?.signals_days || 0) > 0 ? (
          <LivingStatTile label="Последние 14 дней">
            {livingSignals?.signals_days} дней с живым откликом — настроение, темы и действия.
          </LivingStatTile>
        ) : null}
        {closure ? <LivingStatTile label="Собранность дня">{closure}</LivingStatTile> : null}
        {clarity ? <LivingStatTile label="Ясность решений">{clarity}</LivingStatTile> : null}
        {focus ? <LivingStatTile label="Что чаще всплывает">{focus}</LivingStatTile> : null}
      </div>
      {weekText || safeInsights.length ? (
        <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", marginTop: "0.85rem" }}>
          {weekText ? (
            <ProfileSurfaceTile tone="solid">
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Последние 7 дней
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.42rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {weekText}
              </p>
              <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <Link href="/weekly/integration" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                  Открыть неделю
                </Link>
              </div>
            </ProfileSurfaceTile>
          ) : null}
          {safeInsights.length ? (
            <ProfileSurfaceTile tone="solid">
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Повтор за 30 дней
              </p>
              <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.45rem" }}>
                {safeInsights.slice(0, 2).map((item) => (
                  <p key={item.id} className="orbit-body-xs" style={{ margin: 0, color: "#475569", lineHeight: 1.7 }}>
                    • {item.text}
                  </p>
                ))}
              </div>
              <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <Link href="/tracking/insights" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                  Открыть инсайты
                </Link>
              </div>
            </ProfileSurfaceTile>
          ) : null}
        </div>
      ) : null}
      {learningContext && scrubUserFacingText(learningContext.summary) ? (
        <div style={{ marginTop: "0.85rem" }}>
          <ProfileSurfaceTile tone="solid">
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Как тебе сейчас полезнее получать ответ
            </p>
            <p className="orbit-body-xs" style={{ margin: "0.42rem 0 0", color: "#475569", lineHeight: 1.7 }}>
              {scrubUserFacingText(learningContext.summary)}
            </p>
          </ProfileSurfaceTile>
        </div>
      ) : null}
    </ProfileSurfacePanel>
  );
}
