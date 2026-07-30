import type { ReactNode } from "react";
import type { Metadata } from "next";
import { GuestTodayDemoSsr } from "@/components/demo/GuestTodayDemoSsr";
import { SEO_INDEX } from "@/lib/seo/publicSeoPolicy";

export const metadata: Metadata = {
  title: "Демо · Сегодня",
  description:
    "Пример Today: тема, фокус, практика и место для памяти о вчера — без регистрации.",
  robots: SEO_INDEX,
  openGraph: {
    title: "Демо · Сегодня",
    description:
      "Пример Today: тема, фокус, практика и место для памяти о вчера — без регистрации.",
  },
};

export default function DemoTodayLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <GuestTodayDemoSsr />
      {children}
    </>
  );
}
