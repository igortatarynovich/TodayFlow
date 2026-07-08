import { buildProfileV0ViewModel } from "@/lib/profilePage/buildProfileV0Data";
import {
  IGOR_SAGE_7_FIXTURE,
  IGOR_SAGE_7_LABEL,
} from "@/lib/profilePage/fixtures/igorSage7ProfileFixture";
import {
  collectProfileV0UiStrings,
  findProfileUiDuplicates,
  looksTruncated,
} from "@/lib/profilePage/profileV0UiStringsAudit";

describe("Profile v0 UI strings audit (Igor)", () => {
  const model = buildProfileV0ViewModel({
    core: IGOR_SAGE_7_FIXTURE,
    displayName: "Igor",
    auditProfileLabel: IGOR_SAGE_7_LABEL,
  });

  const entries = collectProfileV0UiStrings(model);
  const duplicates = findProfileUiDuplicates(entries);
  const truncated = entries.filter((e) => looksTruncated(e.text, e.field));

  it("renders compass layer despite amplify/energy gaps", () => {
    expect(model.action).not.toBeNull();
    expect(model.action?.rules.length).toBeGreaterThan(0);
    expect(model.action?.recommendation).toBeTruthy();
  });

  it("has no overlapping UI copy across layers", () => {
    if (duplicates.length) {
      // eslint-disable-next-line no-console
      console.log("UI duplicates:", duplicates);
    }
    expect(duplicates).toEqual([]);
  });

  it("has no visibly truncated insight lines", () => {
    if (truncated.length) {
      // eslint-disable-next-line no-console
      console.log("Truncated:", truncated);
    }
    expect(truncated).toEqual([]);
  });

  it("fills love strengthens without mid-word cut", () => {
    expect(model.love?.strength).toMatch(/[.!?]$/);
    expect(model.love?.strength).toContain("крепнет");
  });
});
