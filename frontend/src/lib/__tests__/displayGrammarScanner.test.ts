import { join } from "node:path";
import { inventorySlotIds, matchInventorySlot } from "@/lib/displayGrammar/inventoryCatalog";
import { readInventoryIndexSlotIds } from "@/lib/displayGrammar/parseInventoryMarkdown";
import { FORBIDDEN_RENDER_FIELDS } from "@/lib/displayGrammar/projectionManifest";
import { findingIds, scanDisplayGrammar } from "@/lib/displayGrammar/scanDisplayGrammar";
import { scanInventedFeCopy, scanPathComponentCopy } from "@/lib/displayGrammar/scanInventedFeCopy";
import type { DisplayAtom, DisplayScanInput } from "@/lib/displayGrammar/types";

const repoRoot = join(__dirname, "../../../..");
const frontendRoot = join(__dirname, "../../..");

const guestToday: DisplayScanInput = {
  capability: "guest",
  personal_day_persisted: false,
  evening_in_scroll: false,
  atoms: [
    {
      slot_id: "T1-hero.energy_word",
      surface: "today",
      text: "Заземление",
      origins: ["global"],
      text_class: "calc",
      fe_transform: "map_label",
    },
    {
      slot_id: "T1-hero.human_line",
      surface: "today",
      text: "День просит не спешить с резкими жестами.",
      origins: ["global"],
      text_class: "generated",
      fe_transform: "clip",
    },
    {
      slot_id: "T2.catalog_card",
      surface: "ritual",
      text: "Сила — внутренняя опора.",
      origins: ["catalog"],
      text_class: "catalog",
    },
  ],
};

function atom(partial: Partial<DisplayAtom> & Pick<DisplayAtom, "surface" | "origins">): DisplayAtom {
  return { text: "ok", ...partial };
}

describe("Inventory catalog sync", () => {
  it("catalog slot_ids match both Inventory §2 indexes", () => {
    const today = readInventoryIndexSlotIds(join(repoRoot, "docs/today/TODAY_DISPLAY_INVENTORY_V1.md"));
    const profile = readInventoryIndexSlotIds(join(repoRoot, "docs/profile/PROFILE_DISPLAY_INVENTORY_V1.md"));
    const md = new Set([...today, ...profile]);
    const catalog = new Set(inventorySlotIds());
    const missing = [...md].filter((id) => !catalog.has(id) && !matchInventorySlot(id));
    const extra = [...catalog].filter((id) => !md.has(id));
    expect({ missing, extra }).toEqual({ missing: [], extra: [] });
  });
});

describe("scanDisplayGrammar legal guest TODAY", () => {
  it("accepts Global T1 + ritual catalog without T3", () => {
    expect(scanDisplayGrammar(guestToday)).toEqual([]);
  });
});

describe("Grammar §9 findings", () => {
  it("1 — copy/slot not in Inventory", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              surface: "today",
              origins: ["chrome"],
              copy_key: "inventedKicker",
              text: "Совершенно новый лейбл дня",
              text_class: "chrome",
            }),
          ],
        }),
      ),
    ).toContain(1);
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [atom({ slot_id: "T9.invented", surface: "today", origins: ["global"] })],
        }),
      ),
    ).toContain(1);
  });

  it("2 — JSON field rendered without slot_id", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          vm_fields: [{ field: "storyNext.unused", filled: true, would_render: true }],
        }),
      ),
    ).toContain(2);
    expect(
      findingIds(
        scanDisplayGrammar({
          vm_fields: [{ field: "storyNext", filled: true, would_render: true }],
        }),
      ),
    ).toContain(2);
    expect(FORBIDDEN_RENDER_FIELDS).toContain("storyNext");
  });

  it("3 — generated over budget", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T1-hero.human_line",
              surface: "today",
              origins: ["global"],
              text_class: "generated",
              text: "а".repeat(161),
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(3);
  });

  it("4 — Personal/CE/natal on Global TODAY", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T1-hero.human_line",
              surface: "today",
              origins: ["ce"],
              text_class: "generated",
              json_field: "personal_growth.development_point",
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(4);
  });

  it("5 — ritual symbol in Global Day inputs", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T1-hero.energy_word",
              surface: "today",
              origins: ["card"],
              text_class: "calc",
            }),
          ],
        }),
      ),
    ).toContain(5);
  });

  it("6 — one source in two anti-dupe roles", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T3.headline",
              surface: "my_day",
              origins: ["personal_day"],
              text: "Сегодня твоя ось — одно обещание.",
              json_field: "why_personal",
              text_class: "generated",
              fe_transform: "clip",
            }),
            atom({
              slot_id: "T3.focus_body",
              surface: "my_day",
              origins: ["personal_day"],
              text: "Сегодня твоя ось — одно обещание.",
              json_field: "why_personal",
              text_class: "generated",
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(6);
  });

  it("8 — unknown text_class", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T1-hero.human_line",
              surface: "today",
              origins: ["global"],
              text_class: "poem",
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(8);
  });

  it("9 / 10 — T1 driver and chip counts", () => {
    const transits: DisplayAtom[] = [0, 1, 2, 3].map((i) =>
      atom({
        slot_id: "T1-clock.transit",
        surface: "today",
        origins: ["global"],
        text: `driver ${i} fact line`,
        transit_kind: "driver",
        text_class: "calc",
      }),
    );
    expect(findingIds(scanDisplayGrammar({ atoms: transits }))).toContain(9);
    const chips: DisplayAtom[] = [0, 1, 2, 3, 4].map((i) =>
      atom({
        slot_id: "T1-strength.chip",
        surface: "today",
        origins: ["global"],
        text: `chip${i}`,
        text_class: "calc",
        fe_transform: "map_label",
      }),
    );
    expect(findingIds(scanDisplayGrammar({ atoms: chips }))).toContain(10);
  });

  it("11 — Evening in scroll before time gate", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          evening_in_scroll: true,
          evening_time_ok: false,
          atoms: [],
        }),
      ),
    ).toContain(11);
  });

  it("13 — FE transform out of frame", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T1-hero.human_line",
              surface: "today",
              origins: ["global"],
              text_class: "generated",
              fe_transform: "invent",
            }),
          ],
        }),
      ),
    ).toContain(13);
  });

  it("14 — generated without inputs lock", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          atoms: [
            atom({
              slot_id: "T3.headline",
              surface: "my_day",
              origins: ["personal_day"],
              text_class: "generated",
              inputs_lock: false,
              fe_transform: "clip",
            }),
          ],
          capability: "deep",
          personal_day_persisted: true,
        }),
      ),
    ).toContain(14);
  });

  it("16 — CE field in Personal Day / T3", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          capability: "deep",
          personal_day_persisted: true,
          atoms: [
            atom({
              slot_id: "T3.focus_body",
              surface: "my_day",
              origins: ["ce"],
              text_class: "generated",
              json_field: "personal_growth.development_point",
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(16);
  });

  it("19 — slot-looking atoms but journey sentence fails", () => {
    expect(
      findingIds(
        scanDisplayGrammar({
          capability: "deep",
          personal_day_persisted: true,
          journey: { surface: "my_day", can_finish_sentence: false },
          atoms: [
            atom({
              slot_id: "T3.caution",
              surface: "my_day",
              origins: ["personal_day"],
              text: "Не тяни несколько тредов сразу.",
              text_class: "generated",
              fe_transform: "clip",
            }),
          ],
        }),
      ),
    ).toContain(19);
  });
});

describe("Grammar §9 regression 7 / 12 / 15 / 17 / 18", () => {
  it("merges todayDisplayLockAudit findings", () => {
    const findings = scanDisplayGrammar({
      capability: "guest",
      personal_day_persisted: false,
      today_lock: {
        lensText: "якорь дня",
        developmentPoint: "Замедлиться и услышать себя.",
        inventedTexts: ["Сегодня лучше двигаться последовательно, чем быстро."],
        headline: "Сегодня твоя ось — одно обещание без лишнего шума.",
        focusTitle: "Сегодня твоя ось — одно обещание без лишнего шума.",
        primaryAction: "Закрой одну задачу до 13:00",
        priorities: ["Закрой одну задачу до 13:00"],
        emptyTasksChrome: true,
      },
    });
    expect(findingIds(findings)).toEqual(expect.arrayContaining([7, 12, 15, 17, 18]));
  });
});

describe("negative fixtures", () => {
  it("Unknown field test — filled VM field without Inventory slot is rejected", () => {
    const findings = scanDisplayGrammar({
      vm_fields: [
        { field: "vm.brandNewHeroTagline", filled: true, would_render: true },
      ],
    });
    expect(findingIds(findings)).toContain(2);
    expect(findings.some((f) => f.detail === "vm.brandNewHeroTagline")).toBe(true);
  });

  it("Invented FE copy test — new meaning string in a component fails", () => {
    const findings = scanInventedFeCopy(
      `export function Demo() { return <p>{"Новый смысл дня прямо в компоненте."}</p>; }`,
      "Demo.tsx",
    );
    expect(findingIds(findings)).toEqual([1]);
  });

  it("registered chrome literal does not fail invented-copy scan", () => {
    expect(scanInventedFeCopy(`const x = "Нет соединения.";`)).toEqual([]);
    expect(scanInventedFeCopy(`const x = "Сегодня";`)).toEqual([]);
  });

  it("locked path components have no unregistered meaning literals", () => {
    expect(scanPathComponentCopy(frontendRoot)).toEqual([]);
  });
});
