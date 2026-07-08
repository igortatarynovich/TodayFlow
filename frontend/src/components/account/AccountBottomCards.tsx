"use client";

import Link from "next/link";
import Image from "next/image";

interface AccountBottomCardsProps {
  showContent: boolean;
  transitionDelay?: string;
}

export function AccountBottomCards({ showContent, transitionDelay = "0.5s" }: AccountBottomCardsProps) {
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
        <Link href="/compatibility" className="orbit-card orbit-card-link">
          <h3 className="orbit-display-xs">Психологические игры</h3>
        </Link>

        <div className="orbit-card">
          <h3 className="orbit-display-xs">Блог</h3>
          <ul className="orbit-list-unstyled" style={{ marginTop: "var(--orbit-space-sm)" }}>
            <li className="orbit-body-sm">• Термины</li>
            <li className="orbit-body-sm">• И правила</li>
            <li className="orbit-body-sm">• Как моделировать расклад</li>
            <li className="orbit-body-sm">• + Q&A</li>
          </ul>
        </div>

        <Link href="/tarot" className="orbit-card orbit-card-link">
          <div className="orbit-account-card-icon">
            <Image src="/images/card-of-the-day.png" alt="Карта дня" width={48} height={48} />
          </div>
          <h3 className="orbit-display-xs">Карта дня/вопрос</h3>
          <p className="orbit-body-sm orbit-text-muted">Таро · Расклад</p>
        </Link>

        <Link href="/practices" className="orbit-card orbit-card-link">
          <div className="orbit-account-card-icon">
            <Image src="/images/Meditation.png" alt="Медитации" width={48} height={48} />
          </div>
          <h3 className="orbit-display-xs">Медитации и мантры</h3>
        </Link>

        <Link href="/habits" className="orbit-card orbit-card-link">
          <h3 className="orbit-display-xs">Упражнения для самосовершенствования</h3>
        </Link>

        <Link href="/catalog" className="orbit-card orbit-card-link">
          <h3 className="orbit-display-xs">Гайды (правила)</h3>
        </Link>
      </div>
    </section>
  );
}
