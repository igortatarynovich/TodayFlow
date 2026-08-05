import { findStoryScrollContainer, scrollStoryBlockIntoStep } from "@/lib/todayStoryScroll";

describe("todayStoryScroll", () => {
  it("prefers data-story-scroll=step as container", () => {
    const step = document.createElement("div");
    step.setAttribute("data-story-scroll", "step");
    Object.defineProperty(step, "scrollHeight", { value: 800, configurable: true });
    Object.defineProperty(step, "clientHeight", { value: 400, configurable: true });
    const inner = document.createElement("div");
    const target = document.createElement("div");
    step.appendChild(inner);
    inner.appendChild(target);
    document.body.appendChild(step);

    expect(findStoryScrollContainer(target)).toBe(step);

    const scrollBy = jest.fn();
    step.scrollBy = scrollBy as typeof step.scrollBy;
    step.getBoundingClientRect = () =>
      ({ top: 0, left: 0, bottom: 400, right: 300, width: 300, height: 400, x: 0, y: 0, toJSON: () => ({}) });
    target.getBoundingClientRect = () =>
      ({ top: 220, left: 0, bottom: 320, right: 300, width: 300, height: 100, x: 0, y: 220, toJSON: () => ({}) });

    scrollStoryBlockIntoStep(target);
    expect(scrollBy).toHaveBeenCalledWith({ top: 220, behavior: "smooth" });

    step.remove();
  });
});
