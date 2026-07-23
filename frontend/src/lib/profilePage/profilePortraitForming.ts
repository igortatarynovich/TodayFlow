import type { CoreProfile } from "@/lib/types";

/** Voice §0 / §0.05 — person + what opens; never pipeline («генерация», «тексты», «состояние профиля»). */
export const PROFILE_PORTRAIT_FORMING_MESSAGE =
  "Первые контуры характера уже читаются. Повторяющиеся опоры и линии решений проясняются через отмеченные дни.";

const BANNED_FORMING_COPY =
  /генерац|сгенерир|живые\s+текст|живые\s+формулировк|после\s+генерац|live\s+copy|after\s+generation|портрет\s+ещё\s+формир|portrait\s+is\s+still\s+forming|стабильн(?:ое|ого)?\s+состояни|собираем\s+стабильн/i;

export function isProfilePortraitForming(core: CoreProfile | null | undefined): boolean {
  const contract = core?.profile_contract_v1;
  if (!contract) return true;
  // Usable portrait copy exists — show it even while status is partial / spheres slice < 9.
  // Birth-only publish currently ships identity+styles+3 natal spheres as partial forever;
  // blanking the UI on partial left newly created profiles looking empty.
  const identity = String(contract.identity_core || "").trim();
  if (identity) return false;
  const status = String(contract.status || "").trim().toLowerCase();
  if (status === "forming" || status === "partial") return true;
  const spheres = contract.life_spheres;
  if (!spheres || typeof spheres !== "object") return true;
  return Object.keys(spheres).length < 9;
}

export function profilePortraitFormingMessage(core: CoreProfile | null | undefined): string {
  const msg = core?.profile_contract_v1?.forming_message?.trim();
  if (msg && !BANNED_FORMING_COPY.test(msg)) return msg;
  return PROFILE_PORTRAIT_FORMING_MESSAGE;
}
