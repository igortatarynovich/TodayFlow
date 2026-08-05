/**
 * Scroll a story block inside the active ScreenFlow step — never the page / track.
 */

function canScrollY(el: HTMLElement): boolean {
  return el.scrollHeight > el.clientHeight + 2;
}

export function findStoryScrollContainer(from: HTMLElement): HTMLElement | null {
  let el: HTMLElement | null = from.parentElement;
  while (el && el !== document.documentElement) {
    const marked = el.getAttribute("data-story-scroll");
    if ((marked === "pane" || marked === "step") && canScrollY(el)) {
      return el;
    }
    const style = window.getComputedStyle(el);
    const oy = style.overflowY;
    if ((oy === "auto" || oy === "scroll" || oy === "overlay") && canScrollY(el)) {
      return el;
    }
    el = el.parentElement;
  }
  return null;
}

/** Resolve target inside the same ScreenFlow step as `from` (avoids inactive sibling steps). */
export function findStoryBlockInStep(from: HTMLElement, targetId: string): HTMLElement | null {
  const step = from.closest<HTMLElement>("[data-screen-flow-step]");
  const scope: ParentNode = step ?? document;
  return scope.querySelector<HTMLElement>(`[data-story-block="${CSS.escape(targetId)}"]`);
}

/** Smooth-scroll `target` into view within its step scroll container. */
export function scrollStoryBlockIntoStep(target: HTMLElement): void {
  const container = findStoryScrollContainer(target);
  const marginRaw = window.getComputedStyle(target).scrollMarginTop;
  const margin = Number.parseFloat(marginRaw) || 0;

  if (!container) {
    target.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
    return;
  }

  const cRect = container.getBoundingClientRect();
  const tRect = target.getBoundingClientRect();
  const delta = tRect.top - cRect.top - margin;
  if (Math.abs(delta) < 2) return;
  container.scrollBy({ top: delta, behavior: "smooth" });
}
