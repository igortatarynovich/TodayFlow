import {
  consumeProfileMotionOnce,
  hasProfileMotionOnce,
  resetProfileMotionOnceForTests,
} from "@/lib/profile/profileMotionOnce";

describe("profileMotionOnce", () => {
  beforeEach(() => {
    resetProfileMotionOnceForTests();
  });

  it("consumes a key only once", () => {
    expect(hasProfileMotionOnce("decode-pattern-wave")).toBe(false);
    expect(consumeProfileMotionOnce("decode-pattern-wave")).toBe(true);
    expect(hasProfileMotionOnce("decode-pattern-wave")).toBe(true);
    expect(consumeProfileMotionOnce("decode-pattern-wave")).toBe(false);
  });

  it("keeps keys independent", () => {
    expect(consumeProfileMotionOnce("act2-selected-by-reveal")).toBe(true);
    expect(consumeProfileMotionOnce("decode-pattern-wave")).toBe(true);
    expect(consumeProfileMotionOnce("act2-selected-by-reveal")).toBe(false);
  });
});
