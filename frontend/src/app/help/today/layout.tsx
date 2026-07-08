import type { ReactNode } from "react";
import type { Metadata } from "next";
import helpToday from "@/data/helpToday.ru.json";

export const metadata: Metadata = {
  title: helpToday.title,
  description: helpToday.lead.slice(0, 160),
};

export default function HelpTodayLayout({ children }: { children: ReactNode }) {
  return children;
}
