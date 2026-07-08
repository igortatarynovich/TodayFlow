import type { ReactNode } from "react";
import type { Metadata } from "next";
import helpHub from "@/data/helpHub.ru.json";

export const metadata: Metadata = {
  title: helpHub.ringsCardTitle,
  description: helpHub.ringsCardBody.slice(0, 160),
};

export default function HelpRingsLayout({ children }: { children: ReactNode }) {
  return children;
}
