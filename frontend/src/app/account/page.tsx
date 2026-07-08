import { redirect } from "next/navigation";

/** Личный кабинет перенесён в `/profile`. Подстраницы `/account/*` (настройки, круг, подписки) сохраняются. */
export default function AccountRootRedirectPage() {
  redirect("/profile");
}
