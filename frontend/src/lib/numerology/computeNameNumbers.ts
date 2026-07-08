const LETTER_MAP: Record<string, number> = {
  A: 1, B: 2, C: 3, D: 4, E: 5, F: 6, G: 7, H: 8, I: 9,
  J: 1, K: 2, L: 3, M: 4, N: 5, O: 6, P: 7, Q: 8, R: 9,
  S: 1, T: 2, U: 3, V: 4, W: 5, X: 6, Y: 7, Z: 8,
};

const VOWELS = new Set(["A", "E", "I", "O", "U", "Y"]);
const MASTER = new Set([11, 22, 33]);

const CYRILLIC_TO_LATIN: Record<string, string> = {
  А: "A", Б: "B", В: "V", Г: "G", Д: "D", Е: "E", Ё: "E", Ж: "ZH", З: "Z",
  И: "I", Й: "I", К: "K", Л: "L", М: "M", Н: "N", О: "O", П: "P", Р: "R",
  С: "S", Т: "T", У: "U", Ф: "F", Х: "H", Ц: "TS", Ч: "CH", Ш: "SH", Щ: "SH",
  Ъ: "", Ы: "Y", Ь: "", Э: "E", Ю: "YU", Я: "YA",
  а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "e", ж: "zh", з: "z",
  и: "i", й: "i", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r",
  с: "s", т: "t", у: "u", ф: "f", х: "h", ц: "ts", ч: "ch", ш: "sh", щ: "sh",
  ъ: "", ы: "y", ь: "", э: "e", ю: "yu", я: "ya",
  І: "I", і: "i", Ї: "I", ї: "i", Є: "E", є: "e",
};

export type NameNumbers = {
  expression: number;
  soulUrge: number;
  personality: number;
};

function transliterateName(value: string): string {
  let out = "";
  for (const ch of value) {
    if (CYRILLIC_TO_LATIN[ch] != null) {
      out += CYRILLIC_TO_LATIN[ch];
      continue;
    }
    out += ch;
  }
  return out;
}

function lettersFromName(name: string): string[] {
  const latin = transliterateName(name).toUpperCase();
  return Array.from(latin).filter((ch) => ch in LETTER_MAP);
}

function reduceNumber(total: number): number {
  if (total <= 0) return 0;
  let value = total;
  while (value > 9 && !MASTER.has(value)) {
    value = Array.from(String(value)).reduce((sum, d) => sum + Number(d), 0);
  }
  return value;
}

function sumLetters(letters: string[]): number {
  return letters.reduce((sum, ch) => sum + (LETTER_MAP[ch] ?? 0), 0);
}

export function computeNameNumbers(firstName: string): NameNumbers | null {
  const letters = lettersFromName(firstName.trim());
  if (letters.length === 0) return null;

  const vowels = letters.filter((ch) => VOWELS.has(ch));
  const consonants = letters.filter((ch) => !VOWELS.has(ch));

  return {
    expression: reduceNumber(sumLetters(letters)),
    soulUrge: reduceNumber(sumLetters(vowels.length ? vowels : letters)),
    personality: reduceNumber(sumLetters(consonants.length ? consonants : letters)),
  };
}
