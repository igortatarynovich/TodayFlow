import type { ReactNode } from "react";
import type { Metadata } from "next";
import help from "@/data/growthIndexHelp.ru.json";

export const metadata: Metadata = {
  title: help.title,
  description: help.lead.slice(0, 155),
};

export default function HelpProgressLayout({ children }: { children: ReactNode }) {
  return children;
}
