/**
 * Scroll a story block inside the active ScreenFlow step — never the page / track.
 */

export function findStoryScrollContainer(from: HTMLElement): HTMLElement | null {
  let el: HTMLElement | null = from.parentElement;
  while (el && el !== document.documentElement) {
    if (el.getAttribute("data-story-scroll") === "step") {
      return el;
    }
    const style = window.getComputedStyle(el);
    const oy = style.overflowY;
    if (
      (oy === "auto" || oy === "scroll" || oy === "overlay") &&
      el.scrollHeight > el.clientHeight + 2
    ) {
      return el;
    }
    el = el.parentElement;
  }
  return null;
}

/** Smooth-scroll `target` into view within its step scroll container. */
export function scrollStoryBlockIntoStep(target: HTMLElement): void {
  const container = findStoryScrollContainer(target);
  const marginRaw = window.getComputedStyle(target).scrollMarginTop;
  const margin = Number.parseFloat(marginRaw) || 0;

  if (!container) {
    // Fallback: nearest, avoids yanking the ScreenFlow track when possible.
    target.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    return;
  }

  const cRect = container.getBoundingClientRect();
  const tRect = target.getBoundingClientRect();
  const delta = tRect.top - cRect.top - margin;
  if (Math.abs(delta) < 2) return;
  container.scrollBy({ top: delta, behavior: "smooth" });
}
