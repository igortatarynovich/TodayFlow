import { redirect } from "next/navigation";
import { VALUE_FIRST_PATHS } from "@/lib/guestProfileDraft";

/** Alias → canonical soft registration only (no password signup). */
export default function SignupAliasPage({
  searchParams,
}: {
  searchParams?: Record<string, string | string[] | undefined>;
}) {
  const query = new URLSearchParams();
  query.set("fresh", "1");
  const redirectParam = searchParams?.redirect;
  if (typeof redirectParam === "string" && redirectParam.startsWith("/") && !redirectParam.startsWith("//")) {
    query.set("redirect", redirectParam);
  }
  const suffix = query.toString();
  redirect(suffix ? `${VALUE_FIRST_PATHS.welcome}?${suffix}` : `${VALUE_FIRST_PATHS.welcome}?fresh=1`);
}
