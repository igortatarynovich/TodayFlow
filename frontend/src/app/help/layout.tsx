import type { ReactNode } from "react";
import type { Metadata } from "next";
import helpHub from "@/data/helpHub.ru.json";

export const metadata: Metadata = {
  title: helpHub.title,
  description: helpHub.intro.slice(0, 160),
};

export default function HelpLayout({ children }: { children: ReactNode }) {
  return children;
}
