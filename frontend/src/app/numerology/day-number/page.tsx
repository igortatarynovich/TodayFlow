import { redirect } from "next/navigation";

/** Число дня открывается только в ритуале «Сегодня». */
export default function NumerologyDayNumberPage() {
  redirect("/today");
}
