import { redirect } from "next/navigation";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";

export default function BirthChartRedirectPage() {
  redirect(PROFILE_CHART_DEEP_PATH);
}
