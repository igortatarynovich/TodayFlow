import { redirect } from "next/navigation";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";

export default function DashboardBirthChartRedirectPage() {
  redirect(PROFILE_CHART_DEEP_PATH);
}
