import { pickTodayDepthMenu } from "@/lib/todayDepthMenuToday";
import type { TodayContractV1 } from "@/lib/todayContract";

function menuRow(topic: string, label = topic) {
  return { topic, label, value: `${label} value` };
}

describe("pickTodayDepthMenu", () => {
  it("caps static menu when no scenes", () => {
    const menu = [
      menuRow("money"),
      menuRow("intimacy"),
      menuRow("love"),
      menuRow("career"),
      menuRow("family"),
    ];
    expect(pickTodayDepthMenu(menu, null, 3)).toHaveLength(3);
  });

  it("prefers strongest day sphere topic over dumping all four", () => {
    const contract = {
      day_story: {
        day_scenario: {
          ready: true,
          runtime_sot: true,
          conflict: { short_name: "Деньги или импульс" },
          scenes: [
            {
              sphere: "money",
              role_in_story: "primary",
              trap: "Импульс купить",
              opportunity: "Одна цифра",
              what_happens: "Счёт мигает",
            },
            {
              sphere: "energy",
              role_in_story: "support",
              trap: "",
              opportunity: "Сон",
              what_happens: "Тихий фон",
            },
          ],
        },
      },
    } as unknown as TodayContractV1;

    const picked = pickTodayDepthMenu(
      [menuRow("money"), menuRow("intimacy"), menuRow("love"), menuRow("career"), menuRow("family")],
      contract,
      3,
    );
    expect(picked[0]?.topic).toBe("money");
    expect(picked.length).toBeLessThanOrEqual(3);
    expect(picked.every((r) => ["money", "intimacy", "love", "career", "family"].includes(r.topic))).toBe(
      true,
    );
  });
});
