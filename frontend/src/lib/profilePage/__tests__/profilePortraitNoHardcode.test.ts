import { readFileSync } from "node:fs";
import { join } from "node:path";
import { buildProfileLifeSpheresFromProfileData } from "../profileLifeSpheres";
import { isProfilePortraitForming, PROFILE_PORTRAIT_FORMING_MESSAGE } from "../profilePortraitForming";
import type { CoreProfile } from "@/lib/types";

const FORBIDDEN_UI_SNIPPETS = [
  "Видит связи, когда остальные видят события",
  "Медленное планирование и один сложный разговор до 14:00",
  "Помогает держать фокус без внутренней спешки",
  "Здесь видно, как ты входишь в близость",
  "Этот слой показывает, в какой роли ты становишься заметной",
  "Через этот слой читается не только тема денег",
];

describe("profile portrait no hardcode DoD", () => {
  it("forming contract yields empty spheres (no template fill)", () => {
    const core = {
      profile_contract_v1: {
        contract_version: "profile_contract_v1",
        status: "forming",
        forming_message: PROFILE_PORTRAIT_FORMING_MESSAGE,
        identity_core: "",
        strengths: [],
        growth_zones: [],
        relationship_style: "",
        money_style: "",
        decision_style: "",
        recurring_patterns: [],
        life_spheres: {},
      },
    } as CoreProfile;

    expect(isProfilePortraitForming(core)).toBe(true);
    expect(buildProfileLifeSpheresFromProfileData(null, core)).toEqual([]);
  });

  it("partial contract with projected slice spheres surfaces those fields", () => {
    const sphere = {
      how: "Как проявляется: конкретная сцена недели в любви.",
      need: "Нужна ясность и один честный шаг.",
      risk: "Риск — взять лишнее обещание.",
      turns_on: "Включает спокойный разговор.",
      turns_off: "Выключает давление и сравнения.",
      helps: "Помогает короткий слот в календаре.",
    };
    const core = {
      profile_contract_v1: {
        contract_version: "profile_contract_v1",
        status: "partial",
        identity_core: "Живой портрет человека с ясным фокусом.",
        relationship_style: "style long enough",
        money_style: "money style here",
        decision_style: "decision style ok",
        recurring_patterns: [],
        life_spheres: {
          love: sphere,
          money: { ...sphere, how: "Деньги: спокойный шаг без импульса." },
          decisions: { ...sphere, how: "Решения: один критерий и дедлайн." },
        },
      },
    } as CoreProfile;

    const spheres = buildProfileLifeSpheresFromProfileData(null, core);
    expect(isProfilePortraitForming(core)).toBe(false);
    expect(spheres).toHaveLength(3);
    expect(spheres.map((s) => s.id).sort()).toEqual(["decisions", "love", "money"]);
    expect(spheres.some((s) => s.how.includes("Здесь видно, как ты входишь"))).toBe(false);
  });

  it("ready contract with 9 spheres surfaces LLM fields only", () => {
    const sphere = {
      how: "Как проявляется: конкретная сцена недели.",
      need: "Нужна ясность и один честный шаг.",
      risk: "Риск — взять лишнее обещание.",
      turns_on: "Включает спокойный разговор.",
      turns_off: "Выключает давление и сравнения.",
      helps: "Помогает короткий слот в календаре.",
    };
    const ids = ["love", "sex", "money", "work", "family", "kids", "body", "friends", "decisions"];
    const life_spheres = Object.fromEntries(ids.map((id) => [id, { ...sphere, how: `${id}: ${sphere.how}` }]));
    const core = {
      profile_contract_v1: {
        contract_version: "profile_contract_v1",
        status: "ready",
        identity_core: "Живой портрет человека с ясным фокусом.",
        strengths: ["a", "b", "c"],
        growth_zones: ["d", "e", "f"],
        relationship_style: "style",
        money_style: "money",
        decision_style: "decision",
        recurring_patterns: ["pattern"],
        living_changes: "changes now",
        life_mission: "mission",
        helps: ["h1", "h2"],
        life_spheres,
      },
    } as CoreProfile;

    expect(isProfilePortraitForming(core)).toBe(false);
    const spheres = buildProfileLifeSpheresFromProfileData(null, core);
    expect(spheres).toHaveLength(9);
    expect(spheres.every((s) => s.need === sphere.need)).toBe(true);
    expect(spheres.some((s) => s.how.includes("Здесь видно, как ты входишь"))).toBe(false);
  });

  it("profile V2 screen source does not contain banned fake-live snippets", () => {
    const root = join(process.cwd(), "src");
    const files = [
      "components/profile/v2/ProfileV2SystemScreen.tsx",
      "lib/profilePage/buildProfileV2LiveContext.ts",
      "lib/profilePage/profileLifeSpheres.ts",
    ];
    for (const rel of files) {
      const text = readFileSync(join(root, rel), "utf8");
      for (const snippet of FORBIDDEN_UI_SNIPPETS) {
        expect(text.includes(snippet)).toBe(false);
      }
    }
  });
});
