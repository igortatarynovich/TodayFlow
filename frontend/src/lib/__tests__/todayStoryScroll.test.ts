import {
  findStoryBlockInStep,
  findStoryScrollContainer,
  scrollStoryBlockIntoStep,
} from "@/lib/todayStoryScroll";

describe("todayStoryScroll", () => {
  it("prefers a marked scroll container that can actually scroll", () => {
    const step = document.createElement("div");
    step.setAttribute("data-story-scroll", "step");
    Object.defineProperty(step, "scrollHeight", { value: 400, configurable: true });
    Object.defineProperty(step, "clientHeight", { value: 400, configurable: true });

    const pane = document.createElement("div");
    pane.setAttribute("data-story-scroll", "pane");
    Object.defineProperty(pane, "scrollHeight", { value: 800, configurable: true });
    Object.defineProperty(pane, "clientHeight", { value: 400, configurable: true });
    Object.defineProperty(pane, "style", {
      value: { overflowY: "auto" },
      configurable: true,
    });

    const target = document.createElement("div");
    step.appendChild(pane);
    pane.appendChild(target);
    document.body.appendChild(step);

    // Non-scrolling marked step is skipped; real pane wins via overflow walk.
    jest.spyOn(window, "getComputedStyle").mockImplementation((el) => {
      if (el === pane) {
        return { overflowY: "auto", scrollMarginTop: "0px" } as CSSStyleDeclaration;
      }
      return { overflowY: "visible", scrollMarginTop: "0px" } as CSSStyleDeclaration;
    });

    expect(findStoryScrollContainer(target)).toBe(pane);

    const scrollBy = jest.fn();
    pane.scrollBy = scrollBy as typeof pane.scrollBy;
    pane.getBoundingClientRect = () =>
      ({ top: 0, left: 0, bottom: 400, right: 300, width: 300, height: 400, x: 0, y: 0, toJSON: () => ({}) });
    target.getBoundingClientRect = () =>
      ({ top: 220, left: 0, bottom: 320, right: 300, width: 300, height: 100, x: 0, y: 220, toJSON: () => ({}) });

    scrollStoryBlockIntoStep(target);
    expect(scrollBy).toHaveBeenCalledWith({ top: 220, behavior: "smooth" });

    step.remove();
    jest.restoreAllMocks();
  });

  it("scopes block lookup to the active ScreenFlow step", () => {
    const stepA = document.createElement("section");
    stepA.setAttribute("data-screen-flow-step", "a");
    const foreign = document.createElement("div");
    foreign.setAttribute("data-story-block", "energy-flow");
    stepA.appendChild(foreign);

    const stepB = document.createElement("section");
    stepB.setAttribute("data-screen-flow-step", "b");
    const cue = document.createElement("button");
    const local = document.createElement("div");
    local.setAttribute("data-story-block", "energy-flow");
    stepB.appendChild(cue);
    stepB.appendChild(local);

    document.body.appendChild(stepA);
    document.body.appendChild(stepB);

    expect(findStoryBlockInStep(cue, "energy-flow")).toBe(local);

    stepA.remove();
    stepB.remove();
  });
});
