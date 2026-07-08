import {
  buildTodayCompatibilityHook,
  hasSavedCompatibilityPerson,
} from "@/lib/todayCompatibilityHook";
import type { CoreProfile } from "@/lib/types";

const coreWithPartner: CoreProfile = {
  person: { display_name: "Alex" },
  profiles: {
    primary_profile_id: 1,
    items: [
      { id: 1, label: "Я", relation: "self", is_primary: true },
      { id: 2, label: "Маша", relation: "partner" },
    ],
  },
} as CoreProfile;

const coreSolo: CoreProfile = {
  person: { display_name: "Alex" },
  profiles: {
    primary_profile_id: 1,
    items: [{ id: 1, label: "Я", relation: "self", is_primary: true }],
  },
} as CoreProfile;

describe("todayCompatibilityHook", () => {
  it("detects saved compatibility person when circle has a pair", () => {
    expect(hasSavedCompatibilityPerson(coreWithPartner)).toBe(true);
    expect(hasSavedCompatibilityPerson(coreSolo)).toBe(false);
    expect(hasSavedCompatibilityPerson(null)).toBe(false);
  });

  it("builds return CTA when saved person exists", () => {
    const hook = buildTodayCompatibilityHook(coreWithPartner);
    expect(hook.title).toBe("Совместимость");
    expect(hook.body).toMatch(/любви, быту/);
    expect(hook.cta).toBe("Вернуться к совместимости");
    expect(hook.href).toBe("/compatibility");
    expect(hook.hasSavedPerson).toBe(true);
  });

  it("builds new-user CTA when no saved person", () => {
    const hook = buildTodayCompatibilityHook(coreSolo);
    expect(hook.cta).toBe("Проверить совместимость");
    expect(hook.hasSavedPerson).toBe(false);
  });
});
