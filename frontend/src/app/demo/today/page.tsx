"use client";

import Link from "next/link";
import { useAuth } from "@/lib/useAuth";

/** Guest demo body ships from layout SSR; page only adds authed shortcut. */
export default function DemoTodayPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return (
    <p
      data-testid="demo-today-authed-banner"
      style={{
        maxWidth: "42rem",
        margin: "0 auto 1.5rem",
        padding: "0.85rem 1rem",
        borderRadius: "14px",
        background: "rgba(236, 253, 245, 0.92)",
        border: "1px solid rgba(52, 211, 153, 0.24)",
        color: "#166534",
        lineHeight: 1.55,
      }}
    >
      Ты уже в аккаунте.{" "}
      <Link href="/today" style={{ color: "#15803d", fontWeight: 700 }}>
        Открыть свой Today →
      </Link>
    </p>
  );
}
