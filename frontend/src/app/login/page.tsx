import { redirect } from "next/navigation";

export default function LoginAliasPage({
  searchParams,
}: {
  searchParams?: Record<string, string | string[] | undefined>;
}) {
  const query = new URLSearchParams();
  query.set("mode", "login");
  Object.entries(searchParams || {}).forEach(([key, value]) => {
    if (key === "mode") return;
    if (Array.isArray(value)) {
      value.forEach((v) => query.append(key, v));
    } else if (typeof value === "string") {
      query.set(key, value);
    }
  });
  const suffix = query.toString();
  redirect(suffix ? `/auth?${suffix}` : "/auth");
}
