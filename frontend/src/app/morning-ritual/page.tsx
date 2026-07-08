import { redirect } from "next/navigation";

export default function MorningRitualRedirectPage() {
  redirect("/today?slot=morning");
}
