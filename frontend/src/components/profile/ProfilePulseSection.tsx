"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import type { CoreProfile } from "@/lib/types";
import { livingClarityLabel, livingClosureLabel } from "@/components/profile/livingLabels";
import { ProfileSurfacePanel, ProfileSurfaceTile, profileSurfaceStyles } from "@/components/profile/ProfileSurface";

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

export function ProfilePulseSection({ living }: { living: Living | null | undefined }) {
  const livingProfile = living;
  const sparse = isLivingSparse(livingProfile);

  if (sparse || !livingProfile) {
    return (
      <ProfileSurfacePanel eyebrow="Живой слой" panelClass="living">
        <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a", fontWeight: 700, lineHeight: 1.65 }}>
          Сейчас система знает твою карту рождения. Живой слой появится, когда накопятся ответы и действия в «Я сегодня», подсказках и вечерней фиксации.
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

  return (
    <ProfileSurfacePanel eyebrow="Живой слой" panelClass="living">
      <p className="orbit-body-sm" style={{ margin: 0, color: "#0f172a", fontWeight: 700 }}>
        {livingProfile.summary ||
          "Здесь собирается то, что система видит по твоим ответам, вечерней фиксации и действиям — честно и привязано к поведению."}
      </p>
      <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginTop: "0.85rem" }}>
        <LivingStatTile label="Последние 14 дней">
          {livingSignals?.signals_days || 0} дней с живым откликом — настроение, темы и действия.
        </LivingStatTile>
        <LivingStatTile label="Собранность дня">{livingClosureLabel(livingSignals?.closure_state)}</LivingStatTile>
        <LivingStatTile label="Ясность решений">{livingClarityLabel(livingSignals?.clarity_state)}</LivingStatTile>
        <LivingStatTile label="Что чаще всплывает">
          {livingSignals?.dominant_focus || "Тема проявится, когда накопится больше ответов дня."}
        </LivingStatTile>
      </div>
      {livingWeeklyState || livingInsights.length ? (
        <div style={{ display: "grid", gap: "0.75rem", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", marginTop: "0.85rem" }}>
          {livingWeeklyState ? (
            <ProfileSurfaceTile tone="solid">
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Последние 7 дней
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.42rem 0 0", color: "#475569", lineHeight: 1.7 }}>
                {livingWeeklyState.integration_text}
              </p>
              <div style={{ marginTop: "0.6rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <Link href="/weekly/integration" className="orbit-button orbit-button-secondary orbit-button-sm" style={{ textDecoration: "none" }}>
                  Открыть неделю
                </Link>
              </div>
            </ProfileSurfaceTile>
          ) : null}
          {livingInsights.length ? (
            <ProfileSurfaceTile tone="solid">
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Повтор за 30 дней
              </p>
              <div style={{ display: "grid", gap: "0.45rem", marginTop: "0.45rem" }}>
                {livingInsights.slice(0, 2).map((item) => (
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
      {learningContext ? (
        <div style={{ marginTop: "0.85rem" }}>
          <ProfileSurfaceTile tone="solid">
          <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
            Как тебе сейчас полезнее получать ответ
          </p>
          <p className="orbit-body-xs" style={{ margin: "0.42rem 0 0", color: "#475569", lineHeight: 1.7 }}>
            {learningContext.summary}
          </p>
          <div style={{ display: "grid", gap: "0.7rem", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", marginTop: "0.75rem" }}>
            <div>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Как лучше давать ответ
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                {learningContext.response_style || "Станет яснее после нескольких дней с ответами."}
              </p>
            </div>
            <div>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Что сейчас помогает сильнее
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                {learningContext.support_style || "Отметь пару вечеров подряд — поддержка станет точнее."}
              </p>
            </div>
            <div>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#8f7756", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                Что повторяется чаще всего
              </p>
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.7 }}>
                {learningContext.dominant_lanes?.length
                  ? learningContext.dominant_lanes.join(", ")
                  : learningContext.dominant_diary_topics?.length
                    ? learningContext.dominant_diary_topics.join(", ")
                    : "Повторы станут видны после нескольких закрытий дня."}
              </p>
            </div>
          </div>
          </ProfileSurfaceTile>
        </div>
      ) : null}
    </ProfileSurfacePanel>
  );
}
