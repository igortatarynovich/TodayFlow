import type { ReactNode } from "react";
import type { Metadata } from "next";
import helpUsingProfile from "@/data/helpUsingProfile.ru.json";

export const metadata: Metadata = {
  title: helpUsingProfile.title,
  description: helpUsingProfile.lead.slice(0, 160),
};

export default function HelpUsingProfileLayout({ children }: { children: ReactNode }) {
  return children;
}
