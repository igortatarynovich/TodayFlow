import { redirect } from "next/navigation";

export default function TrackingRitualRedirectPage() {
  redirect("/today?slot=evening");
}
