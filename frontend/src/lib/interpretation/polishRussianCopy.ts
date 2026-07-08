/** Post-process Russian copy — fix common generation glitches. */

export function polishRussianCopy(text: string): string {
  return text
    .replace(/\bТы слабеет\b/gi, "Ты слабеешь")
    .replace(/\bты слабеет\b/g, "ты слабеешь")
    .replace(/растёшьet/gi, "растёшь")
    .replace(/растешьet/gi, "растёшь")
    .replace(/\bс\s+воздушная\s+стих/i, "с воздушной стих")
    .replace(/\bс\s+огненная\s+стих/i, "с огненной стих")
    .replace(/\bс\s+земная\s+стих/i, "с земной стих")
    .replace(/\bс\s+водная\s+стих/i, "с водной стих")
    .replace(/\s+/g, " ")
    .trim();
}
