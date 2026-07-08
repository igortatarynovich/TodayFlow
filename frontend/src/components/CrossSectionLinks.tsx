"use client";

import Link from "next/link";
import { t } from "@/lib/i18n";
import { useAuth } from "@/lib/useAuth";

type SectionLink = {
  href: string;
  title: string;
  description: string;
  icon: string;
};

const getSections = (t: (key: string, fallback?: string) => string): Record<string, SectionLink[]> => ({
  today: [
    {
      href: "/today",
      title: t("crossSection.dashboard.cardOfDay", "Карта дня"),
      description: t("crossSection.dashboard.cardOfDayDesc", "Ежедневные инсайты: таро, аффирмация, астрология"),
      icon: "🔮",
    },
    {
      href: "/practices",
      title: t("crossSection.dashboard.practices", "Практики"),
      description: t("crossSection.dashboard.practicesDesc", "Подобранные практики для твоих паттернов"),
      icon: "🧘",
    },
    {
      href: "/journal",
      title: t("crossSection.dashboard.journals", "Журналы"),
      description: t("crossSection.dashboard.journalsDesc", "Записывай желания и благодарности"),
      icon: "📔",
    },
    {
      href: "/challenges",
      title: t("crossSection.dashboard.marathons", "Марафоны"),
      description: t("crossSection.dashboard.marathonsDesc", "Структурированные программы развития"),
      icon: "🏃",
    },
  ],
  daily: [
    {
      href: "/profile",
      title: t("crossSection.daily.discover", "Узнай себя"),
      description: t("crossSection.daily.discoverDesc", "Персональный профиль и паттерны"),
      icon: "🔍",
    },
    {
      href: "/practices",
      title: t("crossSection.daily.practices", "Практики"),
      description: t("crossSection.daily.practicesDesc", "Практики, связанные с картой дня"),
      icon: "🧘",
    },
    {
      href: "/journal",
      title: t("crossSection.daily.journals", "Журналы"),
      description: t("crossSection.daily.journalsDesc", "Запиши инсайты из карты дня"),
      icon: "📔",
    },
    {
      href: "/challenges",
      title: t("crossSection.daily.marathons", "Марафоны"),
      description: t("crossSection.daily.marathonsDesc", "Примени знания в структурированной программе"),
      icon: "🏃",
    },
  ],
  practices: [
    {
      href: "/profile",
      title: t("crossSection.practices.discover", "Узнай себя"),
      description: t("crossSection.practices.discoverDesc", "Понять паттерны, которые влияют на практики"),
      icon: "🔍",
    },
    {
      href: "/today",
      title: t("crossSection.practices.cardOfDay", "Карта дня"),
      description: t("crossSection.practices.cardOfDayDesc", "Сегодняшние инсайты для практик"),
      icon: "🔮",
    },
    {
      href: "/journal",
      title: t("crossSection.practices.journals", "Журналы"),
      description: t("crossSection.practices.journalsDesc", "Отслеживай прогресс практик"),
      icon: "📔",
    },
    {
      href: "/challenges",
      title: t("crossSection.practices.marathons", "Марафоны"),
      description: t("crossSection.practices.marathonsDesc", "Систематические программы практик"),
      icon: "🏃",
    },
  ],
  journal: [
    {
      href: "/profile",
      title: t("crossSection.journal.discover", "Узнай себя"),
      description: t("crossSection.journal.discoverDesc", "Связь записей с твоими паттернами"),
      icon: "🔍",
    },
    {
      href: "/today",
      title: t("crossSection.journal.cardOfDay", "Карта дня"),
      description: t("crossSection.journal.cardOfDayDesc", "Вдохновение для записей"),
      icon: "🔮",
    },
    {
      href: "/practices",
      title: t("crossSection.journal.practices", "Практики"),
      description: t("crossSection.journal.practicesDesc", "Практики для работы с записями"),
      icon: "🧘",
    },
    {
      href: "/challenges",
      title: t("crossSection.journal.marathons", "Марафоны"),
      description: t("crossSection.journal.marathonsDesc", "Задания из марафонов в журнал"),
      icon: "🏃",
    },
  ],
  challenges: [
    {
      href: "/profile",
      title: t("crossSection.challenges.discover", "Узнай себя"),
      description: t("crossSection.challenges.discoverDesc", "Паттерны, которые влияют на марафоны"),
      icon: "🔍",
    },
    {
      href: "/today",
      title: t("crossSection.challenges.cardOfDay", "Карта дня"),
      description: t("crossSection.challenges.cardOfDayDesc", "Ежедневная поддержка в марафоне"),
      icon: "🔮",
    },
    {
      href: "/practices",
      title: t("crossSection.challenges.practices", "Практики"),
      description: t("crossSection.challenges.practicesDesc", "Практики из марафонов"),
      icon: "🧘",
    },
    {
      href: "/journal",
      title: t("crossSection.challenges.journals", "Журналы"),
      description: t("crossSection.challenges.journalsDesc", "Записывай прогресс марафона"),
      icon: "📔",
    },
  ],
});

type CrossSectionLinksProps = {
  currentSection: "today" | "daily" | "practices" | "journal" | "challenges";
  title?: string;
  compact?: boolean;
};

export function CrossSectionLinks({ currentSection, title, compact = false }: CrossSectionLinksProps) {
  const { isAuthenticated } = useAuth();
  const sections = getSections(t);
  const links = sections[currentSection] || [];

  if (!isAuthenticated || links.length === 0) {
    return null;
  }

  return (
    <section className="orbit-hero-content-block" style={{ paddingTop: "var(--orbit-space-2xl)", paddingBottom: "var(--orbit-space-2xl)", background: "var(--orbit-color-mist)" }}>
      <div className="orbit-hero-content-container" style={{ maxWidth: "1200px", margin: "0 auto" }}>
        {title && (
          <div style={{ textAlign: "center", marginBottom: "var(--orbit-space-xl)" }}>
            <h2 className="orbit-display-sm" style={{ marginBottom: "var(--orbit-space-sm)" }}>
              {title}
            </h2>
            <p className="orbit-body-sm orbit-text-muted" style={{ maxWidth: "600px", margin: "0 auto" }}>
              {t("crossSection.relatedSections", "Связанные разделы, которые дополняют этот")}
            </p>
          </div>
        )}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: compact ? "repeat(auto-fit, minmax(200px, 1fr))" : "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "var(--orbit-space-lg)",
          }}
        >
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="orbit-card"
              style={{
                padding: compact ? "var(--orbit-space-md)" : "var(--orbit-space-lg)",
                textDecoration: "none",
                color: "inherit",
                display: "flex",
                flexDirection: "column",
                transition: "all var(--orbit-transition-base)",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "var(--orbit-shadow-warm)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "var(--orbit-shadow-card)";
              }}
            >
              <div style={{ fontSize: "2rem", marginBottom: "var(--orbit-space-sm)", textAlign: "center" }}>
                {link.icon}
              </div>
              <h3 className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)", textAlign: "center" }}>
                {link.title}
              </h3>
              <p className="orbit-body-xs orbit-text-muted" style={{ lineHeight: 1.5, textAlign: "center" }}>
                {link.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
