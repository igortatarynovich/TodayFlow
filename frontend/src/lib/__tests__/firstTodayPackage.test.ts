import { buildFirstTodayPackage } from "@/lib/firstTodayPackage";
import type { CoreProfile } from "@/lib/types";
import type { TodayContractV1 } from "@/lib/todayContract";

const CORE_FIXTURE: CoreProfile = {
  status: "ready",
  is_ready: true,
  profile_hash: "abc",
  generated_at: "2026-06-23T00:00:00Z",
  missing_fields: [],
  has_snapshot: true,
  person: { first_name: "Вика", display_name: "Вика", gender: "female" },
  astro: { profile_id: 1, sun_sign: "Овен" },
  numerology: { life_path: 7 },
};

const CONTRACT_FIXTURE: TodayContractV1 = {
  contract_version: "today_contract_v1",
  global_context: { period: "июнь" },
  personal_growth: { development_point: "ясность" },
  domains: {
    relationships: { status: "контакт", opportunity: "мягкий разговор", risk: "давление", action: "написать" },
    money_work: { status: "фокус", opportunity: "одно решение", risk: "распыление", action: "закрыть задачу" },
    family: { status: "опора", opportunity: "домашний ритм", risk: "усталость", action: "отдых" },
  },
  primary_action: "Закрой одну задачу до обеда.",
  progress: {},
  generation_id: "gen-1",
};

describe("buildFirstTodayPackage", () => {
  it("builds theme-first package with identity and intent", () => {
    const pkg = buildFirstTodayPackage({
      coreProfile: CORE_FIXTURE,
      intentTheme: "clarity",
      realityState: "unclear",
      contract: CONTRACT_FIXTURE,
    });

    expect(pkg.theme.headline).toContain("Вика");
    expect(pkg.theme.headline).toMatch(/ясность|решений/i);
    expect(pkg.theme.body).toMatch(/Овен/);
    expect(pkg.progress.statusLabel).toMatch(/День 1/);
    expect(pkg.insight.spheres).toHaveLength(3);
    expect(pkg.action.primary).toContain("Закрой одну задачу");
    expect(pkg.why.lines.some((l) => l.includes("ясность"))).toBe(true);
  });

  it("uses empty progress copy and depth CTA to profile by default", () => {
    const pkg = buildFirstTodayPackage({
      coreProfile: CORE_FIXTURE,
      intentTheme: "focus",
      realityState: "stable",
    });

    expect(pkg.progress.hint).toMatch(/начало пути/i);
    expect(pkg.depth.href).toBe("/profile");
  });

  it("routes relationships depth to guidance", () => {
    const pkg = buildFirstTodayPackage({
      coreProfile: CORE_FIXTURE,
      intentTheme: "relationships",
      realityState: "motivated",
    });

    expect(pkg.depth.href).toContain("/tarot");
  });
});
