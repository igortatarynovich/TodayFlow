import fs from "node:fs";

const enPath = new URL("../../CONTENT/i18n/app.en.json", import.meta.url).pathname;
const ruPath = new URL("../../CONTENT/i18n/app.ru.json", import.meta.url).pathname;

const en = {
  "natal.map.error.loadFailed": "Could not load natal chart",
  "natal.map.gate.unauth": "Sign in to view your chart",
  "natal.map.gate.errorFallback": "Your chart isn’t available right now",
  "natal.map.gate.fillCore": "Complete core birth data",
  "natal.map.gate.retry": "Try again",
  "natal.map.loading.title": "Loading natal chart",
  "natal.map.loading.elapsed": "{seconds}s elapsed",
  "natal.map.loading.phase1": "Building your chart…",
  "natal.map.loading.phase2": "Almost there—this can take up to a minute…",
  "natal.map.loading.phase3": "Check your connection and try refreshing the page.",
  "natal.map.loading.aria": "Loading natal chart",
  "natal.map.hero.eyebrow": "Personal Map",
  "natal.map.hero.title": "My natal chart",
  "natal.map.hero.lead":
    "The foundation for interpretations: positions, houses, and aspects. Portrait and “who you are” live in Profile; Today is for the day—without duplicating it here.",
  "natal.map.hero.profileCta": "My profile",
  "natal.map.hero.metric.displayName": "Name in the app",
  "natal.map.hero.metric.displayNameFallback": "My profile",
  "natal.map.hero.metric.displayNameHint": "Main anchor for personalized interpretations.",
  "natal.map.hero.metric.lifePath": "Life path number",
  "natal.map.hero.metric.lifePathHint": "Numerology line used across personal layers.",
  "natal.map.hero.metric.sun": "Sun",
  "natal.map.hero.metric.sunHint": "Core expression style and the chart’s lead sign.",
  "natal.map.hero.metric.asc": "Ascendant",
  "natal.map.hero.metric.ascHintSet": "How you show up, connect, and make a first impression.",
  "natal.map.hero.metric.ascHintMissing": "Exact birth time and place are needed for a reliable Ascendant.",
  "natal.map.hero.metric.mc": "MC",
  "natal.map.hero.metric.mcHintSet": "Career direction, responsibility, and public vector.",
  "natal.map.hero.metric.mcHintMissing": "MC depends on chart angles and may be missing without an exact birth time.",
  "natal.map.hero.metric.archetype": "Archetype",
  "natal.map.hero.metric.archetypePending": "Forming",
  "natal.map.hero.metric.archetypeHintFallback": "Will fold into future personalized reads.",
  "natal.map.next.title": "What’s next?",
  "natal.map.next.lead":
    "Profile (portrait and life areas), Guidance on a theme, or Flow for rhythm. This screen isn’t about “today”.",
  "natal.map.next.step": "Step {step}",
  "natal.map.wheel.title": "Chart wheel",
  "natal.map.wheel.subtitle":
    "A visual map of planets, houses, and aspects—the geometry your interpretations build on.",
  "natal.map.wheel.cached": "From cache",
  "natal.map.lifeAreas.title": "The four angles",
  "natal.map.lifeAreas.subtitle":
    "A cut across houses 1, 4, 7, and 10—structural anchors. Thematic life areas (love, money, intimacy, body, etc.) are composed in Profile from several chart factors, not only these four cells.",
  "natal.map.houseSuffix": "House {house}",
  "natal.map.planets.title": "Personal planets",
  "natal.map.planets.subtitle":
    "Sun, Moon, Mercury, Venus, Mars, Jupiter, and Saturn—the most useful layer for character and patterns.",
  "natal.map.planet.signPending": "sign pending",
  "natal.map.planet.visibleNow": "Currently visible: {sign}{housePart}.",
  "natal.map.planet.housePart": ", house {house}",
  "natal.map.planet.noRow": "Planet data didn’t arrive. Check birth date, time, and place, then refresh the chart.",
  "natal.map.allHouses.title": "All houses",
  "natal.map.allHouses.subtitle": "Full map of life areas. Kept expandable so the main view stays light.",
  "natal.map.aspects.title": "Aspects between planets",
  "natal.map.aspects.subtitle": "Key links that show inner harmony, tension, and how you react.",
  "natal.map.aspects.geometryNote": "Showing basic aspects from geometry. Refresh the chart later for a fuller pass.",
  "natal.map.aspectStrength.exact": "Exact",
  "natal.map.aspectStrength.tight": "Tight",
  "natal.map.aspectStrength.soft": "Soft",
  "natal.map.aspects.empty.beforeLink":
    "We need ecliptic longitudes (or sign + degree in sign) to compute aspects. Usually fixed by recalculating the chart:",
  "natal.map.aspects.empty.link": "check your profile core data",
  "natal.map.aspects.empty.afterLink": "and reload this page. If the chart cache is stale, saving the profile will refresh it.",
  "natal.map.angles.title": "My baseline",
  "natal.map.angles.subtitle":
    "Ascendant and MC—how you’re read on first contact and how your visible path of achievement forms.",
  "natal.map.angles.ascEyebrow": "How you show up",
  "natal.map.angles.ascWithSign":
    "Ascendant in {sign} describes your first impulse, how you connect with people, and how you enter new situations.",
  "natal.map.angles.ascFallback":
    "Ascendant isn’t defined precisely enough yet—usually the chart needs an exact birth time or reliable angles.",
  "natal.map.angles.mcEyebrow": "Where achievement points",
  "natal.map.angles.mcWithSign": "MC in {sign} shows how you realize yourself in career, responsibility, and public role.",
  "natal.map.angles.mcFallback":
    "MC isn’t defined precisely enough yet—often tied to missing birth time or incomplete angles.",
  "natal.map.editorial.titleFallback": "Chart essence",
  "natal.map.editorial.subtitle":
    "A tight read of chart structure. Long portrait and life areas stay in Profile—no daily copy here.",
  "natal.map.editorial.summaryFallback": "A fuller chart essence will appear after the full interpretation.",
  "natal.map.editorial.giftsEyebrow": "Lean on",
  "natal.map.editorial.giftsEmpty": "Chart strengths will sharpen as personal reading accumulates.",
  "natal.map.editorial.tensionsEyebrow": "Stay mindful here",
  "natal.map.editorial.tensionsEmpty": "Growth edges get clearer after houses and aspects are fully read.",
  "natal.map.editorial.nextEyebrow": "What to explore next",
  "natal.map.prompt.title": "What the system uses in prompts",
  "natal.map.prompt.subtitle":
    "Short and transparent: the same chart elements are blended into Today, Guidance, and Compatibility—not the whole screen, only relevant nodes.",
  "natal.map.prompt.body":
    "These signals help keep tone coherent: Moon—emotional rhythm and sensitivity; Venus—love style and harmony; Mars—action and desire; 7th house—partnership and agreements; 8th house—intimacy, trust, shared resources; 6th house—body and daily rhythm; MC and 10th house—achievement and status. The profile selector picks a slice for the day’s task or question.",
  "natal.map.bridge.title": "Portrait and strengths",
  "natal.map.bridge.subtitle":
    "“Who you are”, growth edges, and life areas live in Profile—here we keep the chart as the foundation.",
  "natal.map.bridge.leadBefore": "To avoid repeating the same copy in Today and Guidance, see fuller character reads in",
  "natal.map.bridge.leadLink": "Profile — life areas",
  "natal.map.bridge.leadAfter": ".",
  "natal.map.bridge.openProfile": "Open profile",
  "natal.map.expand.summary": "Open",
  "natal.map.profileLens.label": "How this reads in the chart",
};

const ru = {
  "natal.map.error.loadFailed": "Ошибка при загрузке натальной карты",
  "natal.map.gate.unauth": "Войдите, чтобы просмотреть личную карту",
  "natal.map.gate.errorFallback": "Личная карта пока недоступна",
  "natal.map.gate.fillCore": "Заполнить данные ядра",
  "natal.map.gate.retry": "Попробовать снова",
  "natal.map.loading.title": "Загружаем натальную карту",
  "natal.map.loading.elapsed": "Прошло {seconds} с",
  "natal.map.loading.phase1": "Собираем карту…",
  "natal.map.loading.phase2": "Почти готово, это может занять до минуты…",
  "natal.map.loading.phase3": "Проверь соединение и попробуй обновить экран.",
  "natal.map.loading.aria": "Загрузка натальной карты",
  "natal.map.hero.eyebrow": "Personal Map",
  "natal.map.hero.title": "Моя натальная карта",
  "natal.map.hero.lead":
    "Основание интерпретаций: положения, дома и аспекты. Портрет и «кто ты» — в профиле; день — на экране Today, без дублирования здесь.",
  "natal.map.hero.profileCta": "Мой профиль",
  "natal.map.hero.metric.displayName": "Имя в системе",
  "natal.map.hero.metric.displayNameFallback": "Мой профиль",
  "natal.map.hero.metric.displayNameHint": "Главная точка сборки персональных интерпретаций.",
  "natal.map.hero.metric.lifePath": "Число пути",
  "natal.map.hero.metric.lifePathHint": "Нумерологическая линия, которая учитывается во всех персональных слоях.",
  "natal.map.hero.metric.sun": "Солнце",
  "natal.map.hero.metric.sunHint": "Базовый стиль проявления и главный знак карты.",
  "natal.map.hero.metric.asc": "Асцендент",
  "natal.map.hero.metric.ascHintSet": "Как ты входишь в контакт и какое первое впечатление создаёшь.",
  "natal.map.hero.metric.ascHintMissing": "Нужны точные время и место рождения, чтобы асцендент показался корректно.",
  "natal.map.hero.metric.mc": "MC",
  "natal.map.hero.metric.mcHintSet": "Куда тянется взрослая реализация, карьера и внешний вектор.",
  "natal.map.hero.metric.mcHintMissing": "MC зависит от углов карты и может не определиться без точного времени рождения.",
  "natal.map.hero.metric.archetype": "Архетип",
  "natal.map.hero.metric.archetypePending": "Формируется",
  "natal.map.hero.metric.archetypeHintFallback": "Станет частью дальнейших персональных выводов.",
  "natal.map.next.title": "Что дальше?",
  "natal.map.next.lead":
    "Дальше — профиль (портрет и сферы), Guidance по теме или Flow для ритма. Этот экран не про «сегодня».",
  "natal.map.next.step": "Шаг {step}",
  "natal.map.wheel.title": "Круг карты",
  "natal.map.wheel.subtitle":
    "Визуальная схема планет, домов и аспектов. Это геометрия твоей карты, на которой строятся все остальные интерпретации.",
  "natal.map.wheel.cached": "Из кеша",
  "natal.map.lifeAreas.title": "Четыре угла карты",
  "natal.map.lifeAreas.subtitle":
    "Срез по домам 1, 4, 7 и 10 — структурные опоры. Тематические жизненные сферы (любовь, деньги, близость, тело и др.) собираются в профиле из нескольких элементов карты, а не дублируют только эти четыре ячейки.",
  "natal.map.houseSuffix": "{house} дом",
  "natal.map.planets.title": "Личные планеты",
  "natal.map.planets.subtitle":
    "Солнце, Луна, Меркурий, Венера, Марс, Юпитер и Сатурн. Это самый полезный слой для чтения своего характера и паттернов.",
  "natal.map.planet.signPending": "знак уточняется",
  "natal.map.planet.visibleNow": "Сейчас видно: {sign}{housePart}.",
  "natal.map.planet.housePart": ", {house} дом",
  "natal.map.planet.noRow": "Данные по планете не пришли. Проверь дату, время и место рождения, затем обнови карту.",
  "natal.map.allHouses.title": "Все дома",
  "natal.map.allHouses.subtitle":
    "Полная карта жизненных сфер. Этот блок оставлен раскрываемым, чтобы не перегружать основной экран.",
  "natal.map.aspects.title": "Аспекты между планетами",
  "natal.map.aspects.subtitle": "Ключевые связи, которые показывают внутреннюю гармонию, напряжение и механизм твоих реакций.",
  "natal.map.aspects.geometryNote":
    "Сейчас показаны базовые аспекты. Для более точного разбора обнови карту позже.",
  "natal.map.aspectStrength.exact": "Точный",
  "natal.map.aspectStrength.tight": "Тесный",
  "natal.map.aspectStrength.soft": "Мягкий",
  "natal.map.aspects.empty.beforeLink":
    "Не хватает эклиптических долгот планет (или знака с градусом в знаке), чтобы посчитать аспекты. Обычно это лечится пересчётом карты:",
  "natal.map.aspects.empty.link": "проверь ядро профиля",
  "natal.map.aspects.empty.afterLink":
    "и обнови эту страницу. Если кеш карты старый, после сохранения профиля данные подтянутся заново.",
  "natal.map.angles.title": "Моя базовая линия",
  "natal.map.angles.subtitle":
    "Асцендент и MC — два опорных угла: как тебя «читают» при входе в контакт и как складывается видимая линия реализации.",
  "natal.map.angles.ascEyebrow": "Как ты проявляешься",
  "natal.map.angles.ascWithSign":
    "Асцендент в {sign} описывает твой первый импульс, стиль контакта с людьми и то, как ты входишь в новые процессы.",
  "natal.map.angles.ascFallback":
    "Асцендент пока не определился достаточно точно. Обычно это значит, что карте не хватает точного времени рождения или надёжно собранных углов.",
  "natal.map.angles.mcEyebrow": "Куда ведет реализация",
  "natal.map.angles.mcWithSign":
    "MC в {sign} показывает, как ты реализуешься в карьере, ответственности и публичной роли.",
  "natal.map.angles.mcFallback":
    "MC пока не определился достаточно точно. Обычно это тоже связано с отсутствием точного времени рождения или неполными углами карты.",
  "natal.map.editorial.titleFallback": "Суть карты",
  "natal.map.editorial.subtitle":
    "Краткая выжимка по структуре карты. Длинный портрет и сферы жизни — в профиле; здесь без дневных формулировок.",
  "natal.map.editorial.summaryFallback": "Подробная суть карты появится после полной интерпретации.",
  "natal.map.editorial.giftsEyebrow": "На что опираться",
  "natal.map.editorial.giftsEmpty": "Опоры карты будут уточняться по мере накопления персонального чтения.",
  "natal.map.editorial.tensionsEyebrow": "Где важна осознанность",
  "natal.map.editorial.tensionsEmpty": "Зоны роста станут точнее после чтения всех домов и аспектов.",
  "natal.map.editorial.nextEyebrow": "Что смотреть дальше",
  "natal.map.prompt.title": "Что система использует в промптах",
  "natal.map.prompt.subtitle":
    "Коротко и прозрачно: те же элементы карты подмешиваются в Today, Guidance и Compatibility — не весь экран целиком, а релевантные узлы.",
  "natal.map.prompt.body":
    "Эти данные помогают системе держать связный тон: Луна — эмоциональный ритм и чувствительность; Венера — стиль любви и гармонии; Марс — действие и желание; 7 дом — партнёрство и договорённости; 8 дом — близость, доверие и общие ресурсы; 6 дом — тело и повседневный режим; MC и 10 дом — реализация и статус. Селектор профиля отбирает срез под задачу дня или вопроса.",
  "natal.map.bridge.title": "Портрет и сильные стороны",
  "natal.map.bridge.subtitle":
    "Сводка «кто ты», точки роста и жизненные сферы собираются в профиле — здесь только карта как основание.",
  "natal.map.bridge.leadBefore":
    "Чтобы не плодить одинаковый текст в Today и Guidance, развёрнутые выводы по характеру и сценариям смотри в",
  "natal.map.bridge.leadLink": "профиле — блок жизненных сфер",
  "natal.map.bridge.leadAfter": ".",
  "natal.map.bridge.openProfile": "Открыть профиль",
  "natal.map.expand.summary": "Открыть",
  "natal.map.profileLens.label": "Как это читается в карте",
};

function merge(path, add) {
  const o = JSON.parse(fs.readFileSync(path, "utf8"));
  for (const [k, v] of Object.entries(add)) {
    if (Object.prototype.hasOwnProperty.call(o, k)) {
      throw new Error(`duplicate key: ${k}`);
    }
    o[k] = v;
  }
  fs.writeFileSync(path, JSON.stringify(o, null, 2) + "\n");
}

merge(enPath, en);
merge(ruPath, ru);
console.log("natal.map.* merged:", Object.keys(en).length);
