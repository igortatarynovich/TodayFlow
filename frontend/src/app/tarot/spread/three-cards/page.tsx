import { redirect } from "next/navigation";

/** Legacy URL → question-first hub (canon §6.4). */
export default function LegacyTarotThreeCardsPage() {
  redirect("/tarot");
}
