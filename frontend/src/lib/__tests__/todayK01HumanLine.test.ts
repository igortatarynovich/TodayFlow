import { DAY_VISUAL_MODES } from "@/lib/dayAtmosphere";
import {
  formulateSharedDayHumanLine,
  SHARED_DAY_HUMAN_LINES,
} from "@/lib/todayK01HumanLine";

const STEM: Record<(typeof DAY_VISUAL_MODES)[number], RegExp> = {
  grounded: /заземлен/i,
  flow: /поток/i,
  radiance: /сияни/i,
  momentum: /импульс/i,
  clarity: /ясност/i,
  tension: /напряжен/i,
  renewal: /обновлен/i,
  depth: /глубин/i,
};

describe("formulateSharedDayHumanLine", () => {
  it("formulates each closed 8-set energy as a distinct human line", () => {
    const lines = DAY_VISUAL_MODES.map((id) => formulateSharedDayHumanLine(id));
    expect(DAY_VISUAL_MODES).toHaveLength(8);
    expect(new Set(lines).size).toBe(8);
    for (let i = 0; i < DAY_VISUAL_MODES.length; i += 1) {
      const id = DAY_VISUAL_MODES[i]!;
      const line = lines[i];
      expect(line).toBe(SHARED_DAY_HUMAN_LINES[id]);
      expect(line).toMatch(STEM[id]);
      expect(line).toMatch(/^Общий день /);
      expect(line!.length).toBeLessThanOrEqual(160);
      const words = line!.trim().split(/\s+/).length;
      expect(words).toBeGreaterThanOrEqual(12);
      expect(words).toBeLessThanOrEqual(22);
    }
  });

  it("omits unknown, missing, and generic values", () => {
    expect(formulateSharedDayHumanLine(null)).toBeNull();
    expect(formulateSharedDayHumanLine(undefined)).toBeNull();
    expect(formulateSharedDayHumanLine("")).toBeNull();
    expect(formulateSharedDayHumanLine("calm")).toBeNull();
    expect(formulateSharedDayHumanLine("Сегодня")).toBeNull();
    expect(formulateSharedDayHumanLine("clarity ")).toBe("Общий день про ясность: меньше шума вокруг, и больше одного чёткого контура.");
  });
});
