import { redirect } from "next/navigation";

/** Карта дня живёт только в ритуале «Сегодня». */
export default function TarotCardOfDayPage() {
  redirect("/today");
}
