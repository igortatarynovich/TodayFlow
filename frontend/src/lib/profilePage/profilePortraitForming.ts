import type { CoreProfile } from "@/lib/types";

/** Voice §0 / §0.05 — person + what opens; never pipeline («генерация», «тексты», «состояние профиля»). */
export const PROFILE_PORTRAIT_FORMING_MESSAGE =
  "Первые контуры характера уже читаются. Повторяющиеся опоры и линии решений проясняются через отмеченные дни.";

const BANNED_FORMING_COPY =
  /генерац|сгенерир|живые\s+текст|живые\s+формулировк|после\s+генерац|live\s+copy|after\s+generation|портрет\s+ещё\s+формир|portrait\s+is\s+still\s+forming|стабильн(?:ое|ого)?\s+состояни|собираем\s+стабильн/i;

/** CE consumption ships 7 stable sphere ids; full funnel historically aimed at 9. */
const MIN_USABLE_SPHERE_COUNT = 3;

export function isProfilePortraitForming(core: CoreProfile | null | undefined): boolean {
  const contract = core?.profile_contract_v1;
  if (!contract) return true;
  // Usable portrait copy exists — show it even while status is partial / spheres slice incomplete.
  // Birth-only publish currently ships identity+styles+3 natal spheres as partial forever;
  // blanking the UI on partial left newly created profiles looking empty.
  const identity = String(contract.identity_core || "").trim();
  if (identity) return false;
  const ce = core?.character_engine_consumption_v0;
  if (ce && (ce.applied === true || Boolean(String(ce.recognition_label || "").trim()))) {
    return false;
  }
  const status = String(contract.status || "").trim().toLowerCase();
  if (status === "forming") return true;
  const spheres = contract.life_spheres;
  if (!spheres || typeof spheres !== "object") {
    return status === "partial" || status === "";
  }
  // CE / partial natal slice (≥3) is enough to show; do not wait for legacy 9.
  return Object.keys(spheres).length < MIN_USABLE_SPHERE_COUNT;
}

export function profilePortraitFormingMessage(core: CoreProfile | null | undefined): string {
  const msg = core?.profile_contract_v1?.forming_message?.trim();
  if (msg && !BANNED_FORMING_COPY.test(msg)) return msg;
  return PROFILE_PORTRAIT_FORMING_MESSAGE;
}
