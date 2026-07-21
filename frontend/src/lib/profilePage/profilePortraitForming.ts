import type { CoreProfile } from "@/lib/types";

export const PROFILE_PORTRAIT_FORMING_MESSAGE =
  "Живые формулировки портрета ещё появляются. Уже доступны факты рождения и базовые сигнатуры.";

export function isProfilePortraitForming(core: CoreProfile | null | undefined): boolean {
  const contract = core?.profile_contract_v1;
  if (!contract) return true;
  const status = String(contract.status || "").trim().toLowerCase();
  if (status === "forming" || status === "partial") return true;
  const spheres = contract.life_spheres;
  if (!spheres || typeof spheres !== "object") return true;
  return Object.keys(spheres).length < 9;
}

export function profilePortraitFormingMessage(core: CoreProfile | null | undefined): string {
  const msg = core?.profile_contract_v1?.forming_message?.trim();
  return msg || PROFILE_PORTRAIT_FORMING_MESSAGE;
}
