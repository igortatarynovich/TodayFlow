"use client";

import { t } from "@/lib/i18n";

import Link from "next/link";
import { NAV_PATHS } from "@/lib/navRoutes";

interface AccountCardsGridProps {
  showContent: boolean;
  transitionDelay?: string;
}

export function AccountCardsGrid({ showContent, transitionDelay = "0.3s" }: AccountCardsGridProps) {
  return (
    <section 
      className="orbit-account-section"
      style={{
        opacity: showContent ? 1 : 0,
        transform: showContent ? "translateY(0)" : "translateY(30px)",
        transition: `opacity 0.8s ease ${transitionDelay}, transform 0.8s ease ${transitionDelay}`
      }}
    >
      <div className="orbit-account-grid">
        <Link href={NAV_PATHS.journal} className="orbit-card orbit-card-link">
          <div className="orbit-account-card-icon">
            <span aria-hidden="true" style={{ fontSize: 34, lineHeight: 1 }}>📓</span>
          </div>
          <h3 className="orbit-display-xs">Мои Дневники</h3>
          <p className="orbit-body-sm orbit-text-muted">Дневники</p>
        </Link>

        <Link href={NAV_PATHS.journal} className="orbit-card orbit-card-link">
          <div className="orbit-account-card-icon">
            <span aria-hidden="true" style={{ fontSize: 34, lineHeight: 1 }}>🙏</span>
          </div>
          <h3 className="orbit-display-xs">Благодарности</h3>
          <p className="orbit-body-sm orbit-text-muted">Дневники Благодарности</p>
        </Link>

        <Link href={NAV_PATHS.today} className="orbit-card orbit-card-link">
          <div className="orbit-account-card-icon">
            <span aria-hidden="true" style={{ fontSize: 34, lineHeight: 1 }}>🎯</span>
          </div>
          <h3 className="orbit-display-xs">Цели</h3>
          <p className="orbit-body-sm orbit-text-muted">Карта желаний</p>
        </Link>

        <Link href={NAV_PATHS.flow} className="orbit-card orbit-card-link">
          <h3 className="orbit-display-xs">Тренеры</h3>
          <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-sm)" }}>
            <li className="orbit-body-sm">• Привычек</li>
            <li className="orbit-body-sm">• Аскеза</li>
            <li className="orbit-body-sm">• Медитации</li>
          </ul>
        </Link>

        <Link href="/practices" className="orbit-card orbit-card-link">
          <h3 className="orbit-display-xs">Мои практики</h3>
          <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-sm)" }}>
            <li className="orbit-body-sm">• Медитацию</li>
            <li className="orbit-body-sm">• Йога (добавлять ссылки)</li>
            <li className="orbit-body-sm">• Дыхание</li>
            <li className="orbit-body-sm">• Мантры</li>
          </ul>
        </Link>
      </div>
    </section>
  );
}
