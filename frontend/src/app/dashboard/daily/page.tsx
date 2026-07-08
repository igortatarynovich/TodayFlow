import { redirect } from "next/navigation";

export default function LegacyDashboardDailyPage() {
  redirect("/today");
}

