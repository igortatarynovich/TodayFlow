"use client";

import Link from "next/link";

interface BirthChartCTAProps {
  showResults: boolean;
  isAuthenticated: boolean;
}

export function BirthChartCTA({ showResults, isAuthenticated }: BirthChartCTAProps) {
  return (
    <section 
      className="orbit-cta-final"
      style={{
        opacity: showResults ? 1 : 0,
        transform: showResults ? "translateY(0)" : "translateY(20px)",
        transition: "opacity 0.8s ease 0.8s, transform 0.8s ease 0.8s"
      }}
    >
      {isAuthenticated ? (
        <>
          <Link href="/profile" className="orbit-button orbit-button-primary orbit-button-large">
            Перейти в профиль
          </Link>
          <p className="orbit-cta-subtext">
            Твой профиль уже создан. Перейди в личный кабинет для просмотра детального расчета.
          </p>
        </>
      ) : (
        <>
          <Link href="/auth" className="orbit-button orbit-button-primary orbit-button-large">
            Зарегистрироваться
          </Link>
          <p className="orbit-cta-subtext">
            чтобы получить детальный рассчет по судьбе и сферам жизни
          </p>
        </>
      )}
    </section>
  );
}
