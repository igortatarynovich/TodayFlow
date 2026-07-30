import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { lookupPracticeDetail } from "@/lib/practices/fetchPracticeDetailServer";
import styles from "@/app/practices/PracticesPage.module.css";

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

/** Hard 404 when missing; SSR body so crawlers see the practice, not only the shell. */
export default async function PracticeDetailLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Params;
}) {
  const lookup = await lookupPracticeDetail(params.id);
  if (lookup.status === "missing") {
    notFound();
  }

  const practice = lookup.status === "ok" ? lookup.practice : null;
  const instructions = (practice?.instructions || []).filter((step) => step?.trim());

  return (
    <>
      {practice ? (
        <article className={styles.ssrPracticeArticle} data-testid="practice-ssr-body">
          <h1 className={styles.ssrPracticeTitle}>{practice.title}</h1>
          {practice.description ? (
            <p className={styles.ssrPracticeLead}>{practice.description}</p>
          ) : null}
          <p className={styles.ssrPracticeMeta}>
            {[
              practice.duration_minutes != null ? `${practice.duration_minutes} мин` : null,
              practice.difficulty || null,
              practice.is_free ? "бесплатно" : null,
            ]
              .filter(Boolean)
              .join(" · ")}
          </p>
          {instructions.length > 0 ? (
            <ol className={styles.ssrPracticeSteps}>
              {instructions.map((step, index) => (
                <li key={`${practice.id}-step-${index}`}>{step}</li>
              ))}
            </ol>
          ) : null}
        </article>
      ) : null}
      {children}
    </>
  );
}
