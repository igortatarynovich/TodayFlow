"use client";

import Link from "next/link";

export default function BillingCancelPage() {
  return (
    <main className="orbit-page" style={{ background: "#FAF9F7" }}>
      <section style={{
        paddingTop: "var(--orbit-space-4xl)",
        paddingBottom: "var(--orbit-space-4xl)",
        textAlign: "center"
      }}>
        <div style={{
          maxWidth: "600px",
          margin: "0 auto",
          padding: "0 var(--orbit-space-xl)"
        }}>
          <h1 className="orbit-display-sm" style={{
            marginBottom: "var(--orbit-space-lg)",
            color: "#0f172a",
            fontWeight: 500
          }}>
            Оплата отменена
          </h1>
          <p className="orbit-body" style={{
            fontSize: "1.125rem",
            lineHeight: 1.7,
            marginBottom: "var(--orbit-space-2xl)",
            color: "#334155"
          }}>
            Оплата не была завершена. Ты можешь вернуться к выбору тарифа или продолжить использование бесплатной версии.
          </p>

          <Link
            href="/pricing"
            className="orbit-button orbit-button-primary"
            style={{
              fontSize: "1.125rem",
              padding: "var(--orbit-space-lg) var(--orbit-space-2xl)",
              textDecoration: "none",
              display: "inline-block"
            }}
          >
            Вернуться к тарифам
          </Link>
        </div>
      </section>
    </main>
  );
}

