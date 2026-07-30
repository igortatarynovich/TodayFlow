import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { lookupPracticeDetail } from "@/lib/practices/fetchPracticeDetailServer";

type Params = { id: string };

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const lookup = await lookupPracticeDetail(params.id);
  if (lookup.status === "missing") {
    return {
      title: "Практика не найдена",
      description: "Эта практика недоступна или была удалена.",
      robots: { index: false, follow: false },
    };
  }
  if (lookup.status === "unavailable") {
    return {
      title: "Практика",
      robots: { index: false, follow: true },
    };
  }
  const { practice } = lookup;
  const title = practice.title;
  const description =
    practice.description?.trim() ||
    "Короткая практика TodayFlow — шаг в теле и внимании без длинного разбора.";
  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `/practices/${practice.id}`,
    },
    twitter: {
      card: "summary",
      title,
      description,
    },
  };
}

/** Hard 404 when the catalog has no such id — avoids indexing empty «Практика не найдена» shells. */
export default async function PracticeDetailLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Params;
}) {
  const lookup: Awaited<ReturnType<typeof lookupPracticeDetail>> = await lookupPracticeDetail(
    params.id,
  );
  if (lookup.status === "missing") {
    notFound();
  }
  return <>{children}</>;
}
