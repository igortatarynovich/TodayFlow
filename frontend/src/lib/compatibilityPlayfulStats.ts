import type { SubscoreKey } from "@/lib/compatibilityScenarioSkins";

type ScoreBand = "high" | "mid" | "low";

function band(score: number): ScoreBand {
  if (score >= 72) return "high";
  if (score >= 52) return "mid";
  return "low";
}

type QuipTable = Record<SubscoreKey, Record<ScoreBand, string>>;

const PLAYFUL_QUIPS: Record<string, QuipTable> = {
  partner_in_crime: {
    attraction: {
      high: "Оба готовы к безумию без прогрева",
      mid: "Риск есть, но кто-то всё же спросит «а точно?»",
      low: "Скучнее, чем очередь в МФЦ",
    },
    stability: {
      high: "План «Б» найдётся даже в 3 ночи",
      mid: "Иногда один тащит, второй делает вид, что помогает",
      low: "После авантюры — «это был не я»",
    },
    conflicts: {
      high: "Ссоритесь, кто первым полез в огонь",
      mid: "Спорите, чья идея была хуже",
      low: "Даже спорить ленитесь — редкий дар",
    },
    sexuality: {
      high: "Адреналин и химия — один коктейль",
      mid: "Искра есть, но не всегда вовремя",
      low: "Больше напарники, чем романтики",
    },
  },
  after_wine: {
    attraction: {
      high: "После второго бокала флирт уже в эфире",
      mid: "Флирт включается через «ну ладно, один»",
      low: "Даже вино не спасает от awkward silence",
    },
    stability: {
      high: "Уютный вечер без сюрпризов — почти",
      mid: "Кто-то рано хочет домой, кто-то — ещё бокал",
      low: "Вечер заканчивается «завтра всё объясню»",
    },
    conflicts: {
      high: "Правда вылетает быстрее, чем закуска",
      mid: "Лишнее сказали — утром делают вид, что нет",
      low: "Фильтры держатся лучше, чем ожидали",
    },
    sexuality: {
      high: "Искра зажигается раньше, чем выключат свет",
      mid: "Намёки есть — исполнение зависит от настроения",
      low: "Романтика уступает место сериалу",
    },
  },
  home_renovation: {
    attraction: {
      high: "Вкус совпадает — чудо, не иначе",
      mid: "«Серый» vs «тёплый беж» — вечная война",
      low: "Один Pinterest, другой «и так сойдёт»",
    },
    stability: {
      high: "План ремонта держится дольше плитки",
      mid: "Сроки плывут, но никто не сдаётся официально",
      low: "Ремонт «на паузе» уже третий месяц",
    },
    conflicts: {
      high: "Нервы на пределе — зато характер виден",
      mid: "Ссора из-за розетки — классика жанра",
      low: "Удивительно спокойно. Подозрительно.",
    },
    sexuality: {
      high: "Выживаете вместе — это почти романтика",
      mid: "Страсть уступает место шуруповёрту",
      low: "Ремонт убил всё, кроме усталости",
    },
  },
  best_friends: {
    attraction: {
      high: "Лёгкость, от которой хочется тусить каждый день",
      mid: "Весело, но иногда слишком по-дружески",
      low: "Скорее соседи по чату, чем besties",
    },
    stability: {
      high: "Опора — позвонишь в 4 утра, ответят",
      mid: "Помогут, но сначала пошутят",
      low: "Дружба на «ну посмотрим»",
    },
    conflicts: {
      high: "Ревнуете друг к другу с силой подростков",
      mid: "Иногда бесит, что друг(подруга) важнее",
      low: "Конфликтов мало — может, и не так уж близко",
    },
    sexuality: {
      high: "Граница чёткая — и это плюс",
      mid: "Иногда намёк, но вы оба делаете вид, что нет",
      low: "Химия есть, но вы оба её игнорируете",
    },
  },
  rule_breaker: {
    attraction: {
      high: "Оба любите ставки — опасное сочетание",
      mid: "Риск привлекает, но кто-то считает до трёх",
      low: "Вы оба слишком законопослушны для этого сценария",
    },
    stability: {
      high: "Договорённости держатся… до первого соблазна",
      mid: "«Мы так решили» живёт ровно до среды",
      low: "Правила для вас — рекомендации",
    },
    conflicts: {
      high: "Спор, кто нарушил первым — ваш спорт",
      mid: "Виноватый найдётся, но не сразу",
      low: "Даже нарушать правила ленитесь",
    },
    sexuality: {
      high: "Запретный плод сладок — вы это знаете",
      mid: "Флирт с правилами — ваш жанр",
      low: "Скандалы не ваш формат",
    },
  },
  living_together: {
    attraction: {
      high: "Дома всё ещё приятно друг на друга смотреть",
      mid: "Тепло есть, но пижама побеждает",
      low: "Соседи по квартире — точнее некуда",
    },
    stability: {
      high: "Быт не разрушил — уже победа",
      mid: "Расписание «чья очередь мыть» — вечная тема",
      low: "Холодильник — поле битвы",
    },
    conflicts: {
      high: "Мелочи бесят с эпичной силой",
      mid: "Ссора из-за шумного чайника — норма",
      low: "Удивительно мирно. Проверьте счета.",
    },
    sexuality: {
      high: "Близость жива даже среди носков",
      mid: "Иногда забываете, что вы не только быт",
      low: "Романтика проиграла пылесосу",
    },
  },
  vacation: {
    attraction: {
      high: "В путешествии друг на друга смотрите иначе",
      mid: "Романтика включается между пересадками",
      low: "Отпуск не спас от «хочу домой»",
    },
    stability: {
      high: "Маршрут согласован — почти как в кино",
      mid: "Один планирует, второй «по настроению»",
      low: "Логистика — главный враг отношений",
    },
    conflicts: {
      high: "Срывы эпичны, но потом смешно",
      mid: "Спор «куда идём» — каждый день",
      low: "Даже в отпуске не ругаетесь. Подозрительно.",
    },
    sexuality: {
      high: "Новая локация = новый настрой",
      mid: "Искра есть, но усталость сильнее",
      low: "Отель — только для сна",
    },
  },
};

const PLAYFUL_SCORE_LABELS: Record<string, Record<ScoreBand, string>> = {
  partner_in_crime: {
    high: "Союз авантюристов",
    mid: "Осторожные напарники",
    low: "Лучше не в одной машине",
  },
  after_wine: {
    high: "Вечер точно запомнится",
    mid: "Будет смешно — потом",
    low: "Лучше без третьего бокала",
  },
  home_renovation: {
    high: "Переживёте ремонт вместе",
    mid: "Кто-то сдастся на плитке",
    low: "Развод на этапе штукатурки",
  },
  best_friends: {
    high: "Besties level unlocked",
    mid: "Дружба с подколами",
    low: "Скорее знакомые",
  },
  rule_breaker: {
    high: "Оба нарушите — вопрос кто первый",
    mid: "Ставки приняты, дисциплина сомнительна",
    low: "Слишком правильные для этого сценария",
  },
  living_together: {
    high: "Дом — ваша крепость",
    mid: "Быт держит, но нервы тоже",
    low: "Соседи по квартире",
  },
  vacation: {
    high: "Dream team в пути",
    mid: "Отпуск выживете — с мемами",
    low: "Лучше ехать отдельно",
  },
};

const DEFAULT_PLAYFUL_SCORE_LABELS: Record<ScoreBand, string> = {
  high: "Статистика на вашей стороне",
  mid: "50 на 50 — как в хорошей шутке",
  low: "Цифры просят пересмотреть сценарий",
};

export function playfulDimensionQuip(scenarioId: string, key: SubscoreKey, score: number): string {
  const table = PLAYFUL_QUIPS[scenarioId]?.[key];
  if (!table) return "";
  return table[band(score)] ?? "";
}

export function playfulScoreLabelRu(scenarioId: string, score: number): string {
  const table = PLAYFUL_SCORE_LABELS[scenarioId] ?? DEFAULT_PLAYFUL_SCORE_LABELS;
  return table[band(score)] ?? DEFAULT_PLAYFUL_SCORE_LABELS[band(score)];
}

export function isPlayfulScenarioId(scenarioId: string): boolean {
  return scenarioId in PLAYFUL_QUIPS || scenarioId in PLAYFUL_SCORE_LABELS;
}
