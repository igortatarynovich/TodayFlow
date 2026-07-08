"use client";

import { t } from "@/lib/i18n";

import Link from "next/link";
import type { AstroProfile } from "@/lib/types";

interface ThematicReportFormProps {
  profiles: AstroProfile[];
  selectedProfileId: number | null;
  onProfileChange: (profileId: number) => void;
  onGenerate: () => void;
  generating: boolean;
  showContent: boolean;
}

export function ThematicReportForm({
  profiles,
  selectedProfileId,
  onProfileChange,
  onGenerate,
  generating,
  showContent,
}: ThematicReportFormProps) {
  return (
    <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-2xl)" }}>
      <div className="orbit-hero-content-container" style={{ maxWidth: "700px", margin: "0 auto" }}>
        <div
          className="orbit-card"
          style={{
            opacity: showContent ? 1 : 0,
            transform: showContent ? "translateY(0)" : "translateY(30px)",
            transition: "opacity 0.8s ease 0.3s, transform 0.8s ease 0.3s"
          }}
        >
          <h2 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-md)" }}>
            Создать разбор
          </h2>
          <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-lg)" }}>
            Выберите астрологический профиль для создания разбора
          </p>

          {profiles.length > 0 ? (
            <>
              <div style={{ marginBottom: "var(--orbit-space-lg)" }}>
                <label className="orbit-body-sm" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-sm)", display: "block" }}>
                  Астрологический профиль
                </label>
                <select
                  value={selectedProfileId || ""}
                  onChange={(e) => onProfileChange(Number(e.target.value))}
                  className="orbit-input"
                  style={{ width: "100%" }}
                >
                  <option value="">Выберите профиль</option>
                  {profiles.map((profile) => (
                    <option key={profile.id} value={profile.id}>
                      {profile.label} {profile.is_primary ? "(Основной)" : ""}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={onGenerate}
                disabled={generating || !selectedProfileId}
                className="orbit-button orbit-button-primary"
                style={{ width: "100%" }}
              >
                {generating ? t("reports.creating", "Создаю разбор...") : t("reports.create", "Создать разбор →")}
              </button>
            </>
          ) : (
            <div style={{ textAlign: "center", padding: "var(--orbit-space-xl)" }}>
              <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-md)" }}>
                У вас нет астрологических профилей
              </p>
              <Link href="/onboarding/core" className="orbit-button orbit-button-primary">
                Создать профиль →
              </Link>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
