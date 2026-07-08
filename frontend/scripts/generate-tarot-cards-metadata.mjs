/**
 * Генерирует `public/images/cards/tarot/tarot_cards_metadata.json`:
 * метаданные для LLM по всем 78 картам (deck_index 0…77 как в tarotCardAssets.ts).
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.join(__dirname, "..");

const majorArcana = JSON.parse(fs.readFileSync(path.join(frontendRoot, "src/data/tarotMajorArcana.json"), "utf8"));

const MAJOR_IDS = [
  "fool",
  "magician",
  "high_priestess",
  "empress",
  "emperor",
  "hierophant",
  "lovers",
  "chariot",
  "strength",
  "hermit",
  "wheel_of_fortune",
  "justice",
  "hanged_one",
  "death",
  "temperance",
  "devil",
  "tower",
  "star",
  "moon",
  "sun",
  "judgement",
  "world",
];

const MAJOR_NAMES_RU = [
  "Шут",
  "Маг",
  "Верховная Жрица",
  "Императрица",
  "Император",
  "Иерофант",
  "Влюблённые",
  "Колесница",
  "Сила",
  "Отшельник",
  "Колесо Фортуны",
  "Справедливость",
  "Повешенный",
  "Смерть",
  "Умеренность",
  "Дьявол",
  "Башня",
  "Звезда",
  "Луна",
  "Солнце",
  "Суд",
  "Мир",
];

/** Ключевые слова RU для промптов (3 шт.); Звезда — как в продуктовом примере. */
const MAJOR_KEYWORDS_RU = [
  ["начало", "доверие", "риск"],
  ["намерение", "речь", "фокус"],
  ["интуиция", "тишина", "тайна"],
  ["забота", "творение", "изобилие"],
  ["структура", "границы", "ответственность"],
  ["традиция", "учение", "ценности"],
  ["выбор", "союз", "согласование"],
  ["воля", "направление", "движение"],
  ["мужество", "нежность", "тело"],
  ["размышление", "мудрость", "уединение"],
  ["циклы", "поворот", "случайность"],
  ["правда", "баланс", "последствия"],
  ["пауза", "угол", "отпускание"],
  ["завершение", "переход", "обновление"],
  ["смешение", "умеренность", "исцеление"],
  ["зависимость", "тень", "соблазн"],
  ["потрясение", "правда", "разрушение"],
  ["надежда", "вдохновение", "восстановление"],
  ["туман", "интуиция", "страх"],
  ["ясность", "радость", "жизнь"],
  ["пробуждение", "итог", "призвание"],
  ["целостность", "завершение", "путь"],
];

const MAJOR_ENERGY = [
  "soft_positive",
  "dynamic",
  "reflective",
  "fertile",
  "structured",
  "neutral",
  "relational",
  "dynamic",
  "soft_positive",
  "reflective",
  "liminal",
  "neutral",
  "reflective",
  "transformative",
  "integrating",
  "shadow",
  "disruptive",
  "soft_positive",
  "liminal",
  "bright_positive",
  "transformative",
  "integrating",
];

const SUIT_KEYS = ["wands", "cups", "swords", "pentacles"];
const SUIT_FOLDERS = ["Suit of Wands", "Suit of Cups", "Suit of Swords", "Suit of Pentacles"];
const SUIT_EN = ["Wands", "Cups", "Swords", "Pentacles"];
const SUIT_RU = ["жезлов", "кубков", "мечей", "пентаклей"];
const RANK_EN = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"];
const RANK_RU = [
  "Туз",
  "Двойка",
  "Тройка",
  "Четвёрка",
  "Пятёрка",
  "Шестёрка",
  "Семёрка",
  "Восьмёрка",
  "Девятка",
  "Десятка",
  "Паж",
  "Рыцарь",
  "Королева",
  "Король",
];
const RANK_ID = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "page", "knight", "queen", "king"];

const RANK_NUANCE_RU = [
  "потенциал",
  "баланс",
  "рост",
  "опора",
  "напряжение",
  "гармония",
  "выбор",
  "движение",
  "граница",
  "итог",
  "новости",
  "скорость",
  "забота",
  "мастерство",
];

const SUIT_BASE_KW = {
  wands: ["инициатива", "воля", "творчество"],
  cups: ["чувства", "связь", "интуиция"],
  swords: ["мысль", "конфликт", "ясность"],
  pentacles: ["материя", "работа", "ресурс"],
};

const SUIT_ENERGY = {
  wands: "dynamic",
  cups: "soft_positive",
  swords: "tense",
  pentacles: "grounding",
};

function majorAssetPath(i) {
  return `Major Arcana/${i}.png`;
}

function minorAssetPath(suitIndex, rankIndex) {
  return `${SUIT_FOLDERS[suitIndex]}/${rankIndex + 1}.png`;
}

function minorId(suitKey, rankIndex) {
  return `${suitKey}_${RANK_ID[rankIndex]}`;
}

const cards = [];

for (let i = 0; i < 22; i++) {
  const m = majorArcana[i];
  cards.push({
    deck_index: i,
    id: MAJOR_IDS[i],
    name_ru: MAJOR_NAMES_RU[i],
    name_en: m.name,
    type: "major",
    keywords: MAJOR_KEYWORDS_RU[i],
    energy: MAJOR_ENERGY[i],
    asset_path: majorAssetPath(i),
  });
}

for (let suitIndex = 0; suitIndex < 4; suitIndex++) {
  const sk = SUIT_KEYS[suitIndex];
  const base = SUIT_BASE_KW[sk];
  for (let r = 0; r < 14; r++) {
    const deckIndex = 22 + suitIndex * 14 + r;
    const nameRu = `${RANK_RU[r]} ${SUIT_RU[suitIndex]}`;
    const nameEn = `${RANK_EN[r]} of ${SUIT_EN[suitIndex]}`;
    const kw = [base[0], base[1], RANK_NUANCE_RU[r]];
    cards.push({
      deck_index: deckIndex,
      id: minorId(sk, r),
      name_ru: nameRu,
      name_en: nameEn,
      type: "minor",
      suit: sk,
      rank: RANK_ID[r],
      keywords: kw,
      energy: SUIT_ENERGY[sk],
      asset_path: minorAssetPath(suitIndex, r),
    });
  }
}

const outPath = path.join(frontendRoot, "public/images/cards/tarot/tarot_cards_metadata.json");
const payload = {
  version: 1,
  description:
    "Метаданные колоды для LLM и сервисов; deck_index совпадает с tarotCardFaceSrc() (0…77). Поле energy — грубая окраска тона карты для промптов: soft_positive | bright_positive | fertile | structured | neutral | relational | dynamic | reflective | liminal | tense | grounding | shadow | disruptive | transformative | integrating.",
  cards,
};

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf8");
console.log("Wrote", outPath, "(" + cards.length + " cards)");
