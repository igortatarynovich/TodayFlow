import {
  dayFactsIdAlias,
  formatAccuracyLine,
  mapSphereToDomain,
  resolveTapPromptFromContract,
} from "@/lib/todayTapWidget";
import type { TodayContractV1 } from "@/lib/todayContract";

describe("todayTapWidget", () => {
  const baseContract = {
    contract_version: "today_contract_v1",
    global_context: { period: "x" },
    personal_growth: { development_point: "y" },
    domains: {},
    primary_action: "z",
    progress: {},
    generation_id: "g",
  } as TodayContractV1;

  it("maps spheres to fixed domains", () => {
    expect(mapSphereToDomain("work_decisions")).toBe("work");
    expect(mapSphereToDomain("money")).toBe("money");
  });

  it("picks primary trap scene for tap prompt", () => {
    const contract: TodayContractV1 = {
      ...baseContract,
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "ok",
        theme: "T",
        day_scenario: {
          runtime_sot: true,
          ready: true,
          conflict: {
            short_name: "A или B",
            why_arose: "why",
            opposing_forces: { a: "a", b: "b" },
          },
          scenes: [
            {
              scene_id: "scene.support",
              sphere: "relationships",
              role_in_story: "support",
              trap: "Не то",
            },
            {
              scene_id: "scene.work_decisions",
              sphere: "work_decisions",
              role_in_story: "primary",
              trap: "Отложить и сделать вид, что выбора нет.",
            },
          ],
        },
      },
    };
    const prompt = resolveTapPromptFromContract(contract);
    expect(prompt?.sceneId).toBe("scene.work_decisions");
    expect(prompt?.domain).toBe("work");
    expect(prompt?.promptedText).toMatch(/Отложить/);
  });

  it("picks higher-magnitude domain trap when two highlighted (money > work)", () => {
    const contract: TodayContractV1 = {
      ...baseContract,
      day_story: {
        contract_version: "day_story_v1",
        interpretation_status: "ok",
        theme: "T",
        day_scenario: {
          runtime_sot: true,
          ready: true,
          conflict: {
            short_name: "День",
            why_arose: "why",
            opposing_forces: { a: "", b: "" },
          },
          scenes: [
            {
              scene_id: "scene.work",
              sphere: "work",
              role_in_story: "primary",
              trap: "Дожать ещё одну задачу.",
              opportunity: "Закрыть одно письмо.",
            },
            {
              scene_id: "scene.money",
              sphere: "money",
              role_in_story: "primary",
              trap: "Импульсная трата «для спокойствия».",
              opportunity: "Одна граница по трате.",
            },
          ],
        },
      },
    };
    const prompt = resolveTapPromptFromContract(contract);
    expect(prompt?.sceneId).toBe("scene.money");
    expect(prompt?.domain).toBe("money");
  });

  it("formats accuracy line", () => {
    expect(
      formatAccuracyLine({
        schema_version: "accuracy_summary_v1",
        window: "14d",
        from_date: "2026-07-01",
        to_date: "2026-07-14",
        overall: { correct: 8, total: 10 },
        by_domain: {},
      }),
    ).toMatch(/8 из 10/);
    expect(dayFactsIdAlias(42, "2026-07-29")).toBe("42:2026-07-29");
  });
});
