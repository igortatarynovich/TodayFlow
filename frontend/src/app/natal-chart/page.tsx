import { redirect } from "next/navigation";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";

/** Legacy Personal Map URL — natal chart is layer 3 of `/profile`. */
export default function NatalChartRedirectPage() {
  redirect(PROFILE_CHART_DEEP_PATH);
}
