/**
 * Канон пользовательских строк сценария Today (рус.).
 * Нативные клиенты: `ios/.../TodayRitualCopy.swift` и `TodayExperienceChromeCopy.swift` (RU/EN лейаут) — **те же формулировки дословно**.
 * Меняем текст здесь → сразу зеркалим в Swift (без «пересказа»).
 *
 * Голос: обращение на «ты», от имени сценария — «я», не «мы». Род по умолчанию нейтрален;
 * при известном поле `coreProfile.person.gender` для заголовка «чего не дожимать» см. `ritualAvoidHeadingForUserGender`.
 */
import type { TrackerEntityKind } from "@/app/tracking/calendar/trackerEntityCatalog";

export { ritualAvoidHeadingForDeclension, ritualAvoidHeadingForUserGender, type RuUserDeclension } from "@/lib/ruUserGender";

export const RITUAL_COPY = {
  heroShortDayTitle: "Коротко о дне",
  /** Убрано с экрана v5 — оставлено для iOS/легаси-ссылок. */
  heroWhyPrompt: "Почему так?",
  heroFocusLabel: "Фокус",
  heroTempoLabel: "Темп",
  heroRiskLabel: "Риск",
  /** Подзаголовок блока core message в сводке дня (паритет `TodayRitualFlow`). */
  heroBestMoveLabel: "Лучший ход",
  heroWindowLabel: "Лучшее окно",
  summarySituationEyebrow: "Ориентиры дня",
  deeperRoutesEyebrow: "Если нужна глубина",
  deeperRoutesSub:
    "Today показывает направление. Если есть конкретный вопрос — разбери его отдельно.",
  deeperGuidanceTitle: "Проводник",
  deeperGuidanceBody:
    "Когда нужно выбрать, решить или понять, что делать дальше: открытые вопросы, работа, деньги, внутренний конфликт.",
  deeperGuidanceCta: "Разобрать вопрос",
  deeperCompatibilityTitle: "Совместимость",
  deeperCompatibilityBody:
    "Когда вопрос связан с человеком, отношениями, притяжением или сексуальной динамикой.",
  deeperCompatibilityCta: "Разобрать отношения",
  deeperPortraitTitle: "Портрет",
  deeperPortraitBody:
    "Обнови факты о себе — подсказки про любовь, деньги и сильные стороны будут ближе к жизни, а не к шаблону.",
  deeperPortraitCta: "Обновить портрет",
  checkInTitle: "Как ты сейчас?",
  moodCheckSubDone: "Состояние выбрано. Ниже — уточнение темы или сразу переход к сводке дня.",
  headTopicSavedLabel: "Тема дня",
  checkInEyebrow: "Сейчас",
  checkInHint:
    "Отметь состояние — так разбор дня лучше совпадёт с тем, что ты реально чувствуешь. Без оценок и «нормы».",
  moodAck: "Принято. Сегодня лучше не перегружать тебя задачами — выбери один ясный шаг.",
  moodAckDrive: "Принято. У тебя есть энергия, но важно не разнести её на десять направлений.",
  checkInMicroEyebrow: "Уточнение",
  checkInMicroHint: "Что сегодня сильнее всего занимает голову?",
  summaryEyebrow: "Подсказки на день",
  summaryIntro:
    "Это не инструкция и не приговор — просто дружеские ориентиры. Возьми то, что откликается; остальное смело отпусти.",
  possibleHeading: "Что может зайти полегче",
  avoidHeading: "Чего сегодня лучше не дожимать",
  supportHeading: "На что можно опереться",
  whyCTA: "Откуда это всё — простыми словами",
  whySheetTitle: "Почему сегодня так написано",
  whyAstroEyebrow: "Твоя карта и небо сегодня",
  whyAstroIntro:
    "Коротко: что из твоей карты и неба на сегодня поддерживает этот день — не развлечение и не общие фразы.",
  whyPatternEyebrow: "Как складывается день",
  whyLifeContextEyebrow: "Твой контекст",
  whyFallback:
    "Это не готовый текст из журнала: он опирается на твои ответы о себе и о дне.",
  areasEyebrow: "Сферы",
  areasTitle: "Куда смотреть сегодня",
  areasIntroToday:
    "Три линии: где движение уместно, где лучше не давить, где держать нейтралитет. Нажми строку — коротко по теме и по твоему ритму.",
  /** O11: мало колец Meaning и мало опор Flow — проценты у сфер приблизительные. */
  areasScoresProvisionalHint:
    "Проценты у сфер сейчас приблизительные: по кольцам Meaning мало данных, а в Flow пока немного опор. Пара честных отметок сделает картину точнее.",
  areasBeforeMoodHint:
    "Если отметишь настроение выше, строка «опора в ритме» у сферы станет ближе к тому, как ты реально живёшь тему.",
  areaTodayEyebrow: "Сегодня по теме",
  areaRhythmEyebrow: "Опора в ритме",
  areaRhythmExpanded:
    "Число у сферы — про твои недавние шаги в Flow по этой теме, а не про «оценку звёзд».",
  areasScenarioMissing:
    "Отдельной подсказки по этой сфере в тексте дня нет — загляни в блок «Ориентиры дня» выше.",
  /** Когда мало данных по сферам (iOS compact); держим формулировку здесь для паритета. */
  areasFallback:
    "Пока мало твоих отметок по сферам — ниже общий ориентир. Одна честная запись в течение дня уже сделает следующий разбор точнее.",
  areaSignal: "Что может усилить тему",
  areaNuance: "На что не рассчитывать",
  heroRhythmCaption: "Твой ритм по отметкам",
  /** Когда нет ни `decision_engine.hero.energy_score`, ни fusion — не показываем выдуманный 50/100. */
  heroRhythmScorePending: "появится, когда накопится несколько твоих отметок в Flow",
  heroRhythmHint:
    "Не про судьбу: насколько в последние дни ты опираешься на свои отметки и шаги в Flow. Строка ниже — про настроение сегодня.",
  essentialsProgressLabel: (done: number, total: number) => `Отмечено: ${done} из ${total}`,
  essentialsProgressExplain: "Полоска — только для тебя, без оценки «молодец / не молодец».",
  focusEyebrow: "Что сделать",
  /** Канон TODAY_WEB §4 — заголовок секции «Главный шаг». */
  focusTitle: "Главный шаг на сегодня",
  essentialsEyebrow: "Базовые опоры",
  essentialsTitle: "Чтобы не слететь",
  essentialsSub: "Четыре опоры — отметь по факту, без отчёта.",
  essentialsPurposeHint:
    "Не чеклист «успешного человека». Галочка — знак, что это сделано для себя, без отчёта никому.",
  essentialsMoodAdaptHint:
    "Четыре опоры на каждый день — отметь то, что для тебя честно: уже сделано, в процессе или точно запланировано на сегодня.",
  supportEyebrow: "Поддержка",
  /** Заголовок секции поддержки после ритуала (паритет iOS `TodayRitualFlowView.supportBlock`). */
  supportSectionTitle: "Поддержка на сегодня",
  /** Когда в Flow ещё нет целей — текст под `supportSectionTitle`. */
  supportIntroNoStructure:
    "Так Today сможет подстраивать рекомендации под реальные действия, а не только под настроение. Добавь цель, привычку, короткую практику или аскезу в Flow.",
  buildDayEyebrow: "Собрать день",
  buildDayTitle: "С чего начать",
  buildDayBody:
    "Добавь в Flow цель, привычку или короткую практику — разбор дня сможет опираться на твой реальный план, а не только на символы.",
  buildDayIdeasTitle: "Идеи на сегодня",
  buildDayIdeasIntro:
    "Без обязаловки — коротко, зачем это может помочь именно сегодня.",
  buildDayCalendarHint:
    "Если занесёшь в календарь Flow привычку, цель или аскезу, проще держать один якорь и не расползаться по задачам.",
  eveningHookTitle: "Вечерняя фиксация",
  eveningHookBody:
    "Вечером можно отметить, что совпало, что не сработало и что стало понятнее. Удобно после 19:00.",
  /** До 19:00 — короче, чем `eveningHookBody` (`TodayResultView`). */
  eveningHookBodyCompact:
    "Вечером вернёмся к этому: что совпало, что не сработало, что стало понятнее.",
  eveningDetails: "Открыть форму",
  todaySummaryEyebrow: "Сводка дня",
  numberDayCaptionSystem: "Число дня уже рассчитано",
  tarotDayCaptionInteractive: "Вытяни карту дня",
  cardEyebrow: "Карта дня",
  tarotCardSubhead: "Вытяни карту — она задаст акцент твоего дня",
  tarotCardSubheadAfterPick: "Карта уже выбрана — дальше число дня и короткий чек состояния.",
  tarotCompactHint: "Развёрнутый текст скрыт, чтобы не дублировать экран — сводка дня выше.",
  numberCompactFootnote: "Число зафиксировано — полный блок скрыт, чтобы не занимать место.",
  tarotIdleHint: "Нажми, чтобы вытянуть карту",
  /** После раскрытия карты — явный переход к числу (без автоскролла). */
  tarotRevealContinueCta: "Продолжить",
  tarotSkipAnimationCta: "Показать карту сразу",
  tarotGridLead: "Сконцентрируйся",
  tarotGridSub: "и выбери одну карту",
  /** Одна строка — для узких мест; на экране сетки лучше primary + secondary. */
  tarotGridPickHint: "Выбирай ту, что откликается больше всего.",
  tarotGridPickHintPrimary: "Выбирай ту, что откликается",
  tarotGridPickHintSecondary: "Правильного выбора не бывает.",
  tarotGridPickFooter: "Прислушайся к первому импульсу.",
  numberDayLead: "Число дня",
  numberDaySubPick: "Выбери число от 1 до 6",
  numberCircleHint: "Интуитивно выбери своё число",
  /** Панель «i» под кругом — как в макете. */
  numberDayEnergyInfo: "Число — это энергия дня. Оно подскажет твой ритм и фокус.",
  moodCheckSub: "Это поможет сделать разбор точнее.",
  tarotClosedLead:
    "Иногда день становится понятнее, когда есть один символ, через который можно на него посмотреть.",
  tarotClosedBody:
    "Вытяни карту — станет яснее, какую тему она подсвечивает сегодня: в действиях, отношениях, деньгах, энергии и решениях.",
  tarotDrawIntro:
    "Вытяни одну карту Таро для сегодняшнего дня. Это не «готовый ответ», а символ, через который можно посмотреть на день: где действовать, где быть осторожнее, что не игнорировать и какой вопрос себе задать.",
  tarotDrawCta: "Вытянуть карту",
  tarotApplyToTodayCta: "Применить к Today",
  tarotDrawAnotherCta: "Вытянуть другую",
  tarotDrawAnotherHint: "Можно добавить одну уточняющую карту за день — второй раз уже без нового перетягивания.",
  tarotYourCardPrefix: "Твоя карта дня — ",
  tarotAppliedAck:
    "Карта учтена: сферы и шаг подстроены под её смысл. Вечером можно честно отметить, что сработало.",
  tarotQuestionEyebrow: "Главный вопрос карты",
  tarotClarifierEyebrow: "Уточняющая карта",
  cardClosedHint:
    "Иногда день становится понятнее, когда есть один символ, через который можно на него посмотреть.",
  cardRevealedHint:
    "Карта работает как личный символ дня: через неё проще заметить тему, риск и один честный шаг.",
  continueToNumber: "Продолжить",
  numberClosedHint:
    "Число задаёт ритм дня рядом с картой. Открой блок — увидишь цифру и короткий смысл.",
  numberRevealCta: "Открыть число дня",
  guidanceTitle: "Если хочется разобраться глубже",
  guidanceCta: "Открыть проводник",
  guidanceLoveFollowup:
    "Если тема про любовь или отношения — после разбора можно зайти в совместимость и посмотреть вас как пару.",
  guidanceWorkFollowup:
    "Если день про работу или деньги — задай вопрос в Проводнике своими словами: так проще получить следующий шаг, а не общую фразу.",
  guidanceNeutralFollowup:
    "Сформулируй вопрос как тебе удобно — так Проводник даст шаг по живой теме, а не воду.",
  guidanceCompatEyebrow: "Если дальше про пару",
  compatibilityCta: "Совместимость",
  suggestedQuestionLove: "Что сейчас происходит в этой связи и что мне лучше сделать?",
  suggestedQuestionWork: "Какой один шаг сейчас даст движ без лишнего шума?",
  suggestedQuestionNeutral: "Что мне сегодня важно увидеть про свой день?",
  ritualOpenDay: "Открыть день",
  ritualDayAlreadyOpen: "День уже открыт",
  /** Сырой индекс 0–100 для мягкой подстройки текстов (транзиты, число дня, недавние отметки) — не «рост дня ото дня». */
  heroScoreFootnote: (n: number) => `По желанию: насколько день ощущается цельным — ${n} из 100.`,
  numerologyBestTimeLabel: "Удачное окно сегодня",
  numerologyColorLabel: "Цвет дня",
  numerologyStoneLabel: "Камень на поддержку",
  guidanceExamplePrefix: "Можно спросить так:",
  dayLayerEyebrow: "Твой ритм в Flow",
  dayLayerIntro:
    "Короткие строки из твоих отметок и контекста — рядом с картой дня, чтобы не искать это в другом месте.",
  dayLayerNudgeLabel: "Ориентир",
  dayLayerWeeklyLabel: "Неделя",
  dayLayerDisciplineLabel: "Дисциплина дня",
  dayLayerQuestionLabel: "Мягкий вопрос",
  dayLayerContextLabel: "К решениям дня",
  cardHonestStepQuestion: "Что сегодня больше всего похоже на твой честный шаг?",
  cardWhatMeansButton: "Что значит эта карта?",
  cardMeaningPopoverTitle: "Что значит эта карта?",
  cardMeaningPopoverBody:
    "Карта задаёт тему дня: на что смотреть внимательнее, что не игнорировать и какой один шаг ближе всего к правде — без буквального «предсказания».",
  cardSaveFocus: "Сохранить как фокус дня",
  cardSaveFocusDone: "Сохранено. Фокус дня можно держать в голове или перенести в Flow как одну задачу.",
  numberRhythmQuestion: "Сегодня тебе больше нужно:",
  spherePercentPrompt: (n: number) => `Что значит ${n}%?`,
  spherePercentExplainerTitle: "Про процент у сферы",
  spherePercentExplainerBody:
    "Это не предсказание и не «шанс события». Процент показывает, насколько сегодня комфортно действовать в теме с учётом твоего числа, отметок и карты, если она уже включена в разбор. Низкий процент — повод не спешить или выбрать вариант полегче, а не «нельзя».",
  focusPickStep: "Выбрать мой шаг",
  focusStart20: "Начать 20 минут",
  focusStart20Hint:
    "Намерение записано: 20 минут на один понятный кусок. Таймер — как тебе удобно; главное — один слот без переключений.",
  focusPickHint: "Что выберешь?",
  focusChooseOneHint: "Выбери один вариант — потом можно зафиксировать в Flow или взять 20 минут.",
  /** Заголовок блока DE-7 над чипами завершённых шагов (паритет iOS). */
  guideMeaningCompletionsEyebrow: "Сегодня в Flow",
  /** Когда сервер отдал счётчики, но все нули за день. */
  guideMeaningCompletionsEmpty:
    "Пока нет завершённых шагов — выбери вариант ниже или открой календарь Flow.",
  /** @deprecated Используй `guideMeaningCompletionsEyebrow` + чипы; оставлено для совместимости копирайта. */
  mainStepMeaningProgressIntro: "Сегодня в Flow уже отмечено:",
  focusFallbackLine:
    "Закрой одну вещь, которая давно висит: письмо, решение, оплата, короткий разговор. Цель — не гнаться за образом «идеального дня», а убрать один висящий кусок с поля внимания.",
  /** Макет: экран входа в пошаговый ритуал. */
  ritualEntryTitle: "Твой день",
  ritualEntryBody:
    "Ответы уже внутри тебя. Я помогу их увидеть и подсветить ясный шаг.",
  ritualEntryCta: "Начать",
  ritualEntryTiming: "Это займёт 1–2 минуты",
  tarotRevealScreenTitle: "Твоя карта дня",
  numberRevealScreenTitle: "Твоё число дня",
  /** После карты / числа — как на макете. */
  ritualContinueCta: "Продолжить",
  /** Шаг настроения — финальная кнопка сетки (референс TODAY). */
  ritualMoodDoneCta: "Готово",
  heroCoreEyebrow: "Сегодня",
  ritualDayReadyTitle: "Твой день",
  /** Заголовок верхнего блока после ритуала (веб). */
  todayYourDayTitle: "Твой день",
  todayShowCardNumberCta: "Показать карту и число",
  ritualDayReadyIntro: "Карта и число уже заданы — ниже смысл в одном месте.",
  ritualDayReadyFootnote:
    "Карта и число остаются в сводке и в «Почему так?» — я не дублирую их большими блоками, чтобы экран не перегружать.",
  daySummaryMarkersEyebrow: "Маркеры дня",
  daySummaryShortEyebrow: "Короткая сводка",
  /** Паритет iOS `TodayRitualFlowView` / веб `TodayGuideSection` — сворачиваемый вторичный блок. */
  guideAdditionalDisclosureTitle: "Дополнительно",
  /** Подзаголовок в `TodayGuideSection` (сферы, шаги, мини-план…). */
  guideAdditionalDisclosureSubtitleWeb:
    "Сферы в кольцах, шаги, вопрос дня, мини-план и быстрые инструменты",
  /** Подзаголовок в ритуальной карточке «Твой день» на iOS. */
  guideAdditionalDisclosureSubtitleRitualCard:
    "Короткая сводка, ориентиры «делать / не делать» и практические подсказки",
  /** DE-9: полоска «вчера / дельта» из fusion.day_history (паритет iOS). */
  dayHistoryEyebrow: "Ритм и вчера",
  dayHistoryHint: "По отметкам в Flow: вчерашние баллы и сдвиг к сегодняшнему дню.",
  /** DE-9 v1.3: при нулевой дельте не показываем «к сегодня: энергия 0…» — хвост вместо второй половины строки. */
  dayHistoryDeltaAllZeroTail:
    "Сдвига к сегодняшнему дню по отметкам пока нет — когда появятся сегодняшние баллы в Flow, строка станет точнее.",
  dayHistoryDeltaAllZeroTailEn:
    "No shift toward today in Flow yet—once today's scores are logged, this line will read clearer.",
  /** O7: одна строка без ложных «вчера 50/50/50» — если вчера не было опоры под fusion. */
  dayHistoryDeltaUntrustworthyTail:
    "Вчера в Flow не было отметок для сравнения с сегодня. Когда появятся вчерашний ритм — настроение, дневник или практики — здесь будут баллы и сдвиг «к сегодня».",
  dayHistoryDeltaUntrustworthyTailEn:
    "No Flow markers yesterday to compare with today. Once you log mood, diary, or practice for that day, scores and the toward-today line will show here.",
  /** Серверная «опора дня» до генерации текста — тот же ключ, что в payload API (паритет iOS). */
  dayEngineBriefEyebrow: "Опора дня",
  /** Детерминированный каркас `day_model_v0` — один фокус и вектор (паритет iOS). */
  dayModelBriefEyebrow: "Одна ось дня",
  dayModelOneFocusLabel: "Фокус",
  daySummaryDoTitle: "Что делать",
  /** Короткий нейтральный вариант; в ритуальной сводке дня заголовок берётся из `ritualAvoidHeadingForUserGender`. */
  daySummaryDontTitle: "Чего не делать",
  daySummaryPracticalEyebrow: "Практичные ориентиры",
  daySummaryWhyCta: "Почему так?",
  daySummaryWhyCollapse: "Свернуть объяснение",
  dayMarkerCard: "Карта",
  dayMarkerNumber: "Число",
  dayMarkerMoon: "Луна и фон дня",
  dayMarkerPhase: "Фаза Луны",
  dayMarkerMood: "Состояние",
  spheresTodayTitle: "Сферы сегодня",
  spheresSeeAll: "Подробнее по сферам",
  /** Заголовок шита / aria сферы (паритет iOS `sphereSheetNavTitle`). */
  sphereSheetNavTitle: "Сфера дня",
  /** Под строкой сферы в треугольнике guide — тап открывает модалку (`TodayResultView`). */
  areasTriadModalDetailHint: "Подробнее в окне",
  /** Подпись сферы «love» в компактной строке макета. */
  relationshipSphereLabel: "Отношения",
  /** Оболочка `/today`: загрузка, ошибки, фоновая подгрузка (§5.3). */
  todayPageLoadingSession: "Сессия…",
  todayPageLoadingDay: "Собираю твой день…",
  todayPageRefreshingDay: "Обновляю твой день…",
  todayPageAuthRequired: "Войдите, чтобы использовать цикл дня",
  todayPageDataMissing: "Данные не найдены",
  todayPageRetryCta: "Попробовать снова",
  todayPageLoadError: "Ошибка при загрузке дня",
  todaySupplementaryLoadingHint: "Календарь и ритм подгружаются в фоне",
  todayDailyStepMeaningLabel: "Смысл дня",
  todayDailyStepFocusLabel: "Опора и действие",
  todayDailyStepClosingLabel: "Итог дня",
  narrativeDepthControlEyebrow: "Глубина текстов дня",
  narrativeDepthControlSaving: "Сохраняю и обновляю…",
  narrativeDepthControlHint: "Влияет на следующую генерацию guide и связанных блоков.",
  narrativeDepthControlAllSettingsCta: "Все настройки",
  /** Подписи уровней в селекте (`todayNarrativeDepthUi`, iOS `TodayView` / `ProfileView`). */
  narrativeDepthOptionQuick: "Короче",
  narrativeDepthOptionNormal: "Обычно",
  narrativeDepthOptionDeep: "Глубже",
  /** iOS: хвост подсказки вместо ссылки «Все настройки». */
  narrativeDepthControlHintSettingsTail: "Полный список — Профиль → Настройки.",
  focusTimerToastInfo: "20 минут на выбранный шаг — один слот без переключений.",
  focusTimerChromeLine: (timeLabel: string) => `Фокус ${timeLabel}`,
  focusTimerPauseCta: "Пауза",
  focusTimerStopCta: "Стоп",
  /** Редирект с экрана разбора на `/today?from_guidance=1`. */
  todayToastGuidanceFollowup:
    "После разбора: закрепи один конкретный шаг в дневном ритме ниже.",
  narrativeDepthDeepSubscriptionRequired: "Режим «Глубже» доступен с подпиской Plus или Pro.",
  narrativeDepthSaveSuccessToast: "Глубина сохранена — обновляю тексты дня.",
  narrativeDepthSaveErrorToast: "Не удалось сохранить глубину",
  todaySaveDayConnectionError: "Не удалось сохранить ответ дня",
  todayCompletePracticeError: "Не удалось отметить практику",
  todaySaveEveningCloseError: "Не удалось сохранить закрытие дня",
  /** Когда нет оси дня / заголовка guide из данных. */
  ritualGuideDayLabelFallback: "День выбора",
  /** Когда сервер не отдал краткое значение числа для героя. */
  numerologyMeaningFallbackShort: "Пауза. Правда. Сбор внимания.",
  todayActionPlanRingCloseness: "близость",
  todayActionPlanRingFocus: "фокус",
  todayActionPlanRingMoney: "деньги",
  /** Кольцо пункта плана, подсвеченного фокусом карты (перед списком с бэка). */
  todayActionPlanRingTarot: "таро",
  refreshDayCta: "Обновить день",
  ritualProgressHint: "Карта → число → настроение — шаги ниже.",
  /** Фрагмент подсказки на входе в ритуал: «Карта: …». */
  ritualProgressCardLabel: "Карта",
  /** Фрагмент подсказки на входе в ритуал: «Число: …». */
  ritualProgressNumberLabel: "Число",
  /** Пока пользователь не прошёл шаг «число», не подставляем серверную цифру в герой. */
  ritualProgressNumberPending: "Число дня откроешь на следующем шаге.",
  ritualComposeLoadingTitle: "Собираю твой день",
  ritualComposeLoadingBody: "Секунда — оформляю день.",
  tarotBridgeToNumber: "Карта зафиксирована. Дальше — число дня.",
  tarotAnimationTroubleHint: "Проблемы с анимацией?",
  tarotCommitWithoutRitualCta: "Зафиксировать карту без ритуала",
  /** После выбора настроения в чек-ине. */
  checkInMoodMarkedTail: "— отмечено",
  /** Заголовок шита «карта + число» (не путать с `ritualDayReadyIntro`). */
  ritualCardNumberDetailTitle: "Карта и число",
  /** Универсальная кнопка закрытия шита/модалки в ритуале. */
  sheetCloseCta: "Закрыть",
  /** Подтверждение прочтения пояснения к карте. */
  cardMeaningAckCta: "Поняла",

  // --- Quick actions (`TodayQuickActions.tsx`) ---
  quickStateCheckNeedScaleOrNote: "Выбери хотя бы шкалу или короткую заметку",
  quickStateCheckSavedToast: "Состояние сохранено",
  quickStateCheckSaveErrorToast: "Не удалось сохранить состояние. Попробуй еще раз.",
  quickStateCheckLoading: "Загрузка состояния…",
  quickStateCheckMoodLabel: "Настроение (1–5)",
  quickStateCheckEnergyLabel: "Энергия (1–5)",
  quickStateCheckStressLabel: "Стресс (1–5, выше — сильнее)",
  quickStateCheckNotePlaceholder: "Одна строка — что чувствуешь сейчас",
  quickStateCheckSaveCta: "Сохранить состояние",
  quickStateCheckSavingCta: "Сохраняю…",
  quickJournalEntryErrorToast: "Ошибка при сохранении записи",
  quickJournalOpenCta: "✍️ Записать в дневник",
  quickJournalTabObservation: "👁️ Наблюдение",
  quickJournalTabGratitude: "🙏 Благодарность",
  quickJournalTabInsight: "💡 Вывод",
  quickJournalPlaceholderObservation: "Что ты заметил сегодня?",
  quickJournalPlaceholderGratitude: "За что ты благодарен?",
  quickJournalPlaceholderInsight: "Какой вывод ты сделал?",
  formSaveCta: "Сохранить",
  formCancelCta: "Отмена",
  formSavingShort: "Сохранение...",
  quickTrackerEntryErrorToast: "Ошибка при сохранении состояния",
  quickTrackerOpenCta: "📍 Отметить состояние",
  quickTrackerHowYouFeelPrompt: "Как ты себя чувствуешь?",
  quickTrackerNotePlaceholder: "Коротко опиши своё состояние...",

  // --- Guide tab (`TodayGuideSection.tsx`) ---
  guidePanelEyebrowToday: "Сегодня",
  guideNarrativeRefiningLine: "Уточняем формулировку дня…",
  guideWhyTodayCta: "Почему сегодня?",
  /** O9: главный CTA ведёт к шагу дня; «Почему» — вторичный. */
  guidePrimaryNavigateCta: "К шагу дня",
  guideEmotionalRingsSectionTitle: "Сферы в кольцах",
  guideOpenSphereForDetailHint: "Чувствуешь блок? Открой сферу и посмотри подробный разбор.",
  guideWhatToDoTodayTitle: "Что сделать сегодня",
  guidePrimaryDoFallback: "Закрыть одну рабочую задачу",
  /** Phase 3 · G1-surface — Core Loop Viability Test (`?core_loop=1` / `?first=1`). */
  coreLoopViabilityExperimentEyebrow: "фокус дня",
  coreLoopViabilityThemeEyebrow: "Главное сегодня",
  coreLoopViabilityActionEyebrow: "Сделать сейчас",
  coreLoopViabilityProgressEyebrow: "Что будет дальше",
  coreLoopViabilityProgressDayOne: "День 1 · первый шаг",
  coreLoopViabilityProgressAfterHint:
    "После шага здесь появится отметка прогресса; вечером можно подвести итог дня.",
  coreLoopViabilityThemeFallback: "Сегодня — один понятный фокус и один шаг.",
  coreLoopViabilityOptionalRitualCta: "Символический слой (необязательно)",

  /** Today experience v0 — default compressed Today. */
  todayExperienceDayEyebrow: "День",
  experiencePickCardEyebrow: "Выбери карту дня",
  experiencePickNumberEyebrow: "Выбери число дня",
  experienceTarotGridSub: "Нажми на одну из закрытых карт",
  todayExperienceActionLabel: "Главный шаг",
  todayExperienceActionCta: "Сделано",
  todayExperienceActionDoneCta: "Сделано",
  todayExperienceProgressLabel: "Прогресс",
  todayExperienceProgressDayStarted: "День начался",
  todayExperienceProgressBeforeActionHint: "",
  todayExperienceProgressAfterAction: "Главный шаг закрыт",
  todayExperienceProgressReturnHint: "",
  todayExperienceProgressStreakLine: (days: number) => `${days} ${days === 1 ? "день" : days < 5 ? "дня" : "дней"} подряд с Today`,
  todayExperienceThemeFallback: "День ясности",
  todayExperienceHeroLeadFallback: "Сегодня выигрывает не скорость, а один точный выбор.",
  todayExperienceTempoMarkerLabel: "Темп",
  todayExperienceTempoMarkerFallback: "спокойный",
  todayExperienceRiskMarkerLabel: "Риск",
  todayExperienceRiskMarkerFallback: "распылиться",
  todayExperienceActionBodyFallback:
    "Выбери одну задачу, которую можно реально завершить сегодня. Не начинай пять новых.",
  todayExperienceTempoPrefix: "Темп ",
  todayExperienceTempoCalm: "Спокойный темп",
  todayExperienceTempoActive: "Активный темп",
  todayExperienceRiskPrefix: "риск — ",
  todayExperienceWhySummary: "Почему сегодня так?",
  todayExperienceWhyFallback:
    "Сегодняшний фокус собран из твоего профиля, состояния дня и текущего контекста. Подробные символические блоки скрыты, чтобы не мешать главному шагу.",
  todayExperienceSymbolEyebrow: "Символ дня",
  todayExperienceSymbolCardLabel: "Карта",
  todayExperienceSymbolNumberLabel: "Число",
  todayExperienceSymbolMoonLabel: "Луна",
  todayExperienceDepthProfile: "Профиль",
  todayExperienceDepthCalendar: "Календарь",
  todayExperienceDepthTarot: "Таро",
  todayExperienceEveningEyebrow: "Закрыть день",
  todayExperienceEveningTitle: "Что сегодня стало понятнее?",
  todayExperienceEveningQuestion: "Одна фраза — без отчёта и разбора всего дня.",
  todayExperienceEveningPlaceholder: "Одна фраза",
  todayExperienceEveningCta: "Сохранить итог",
  todayExperienceEveningSavingCta: "Сохраняю…",
  todayExperienceEveningProgressDone: "1 шаг сделан · день можно закрыть",
  guideOpenDayStepCta: "Открыть шаг дня",
  guideShortQuestionAboutYouTitle: "Короткий вопрос о тебе",
  guideMiniPlanTitle: "Мини-план",
  guideMiniFlowWater: "Вода",
  guideMiniFlowMovement: "Движение",
  guideMiniFlowReflection: "Рефлексия",
  guideMiniFlowFocusSession: "Фокус-сессия",
  guideOpenFullCalendarCta: "Открыть полный план дня",
  /** Строка прогресса: «Прогресс дня: N% (a из b)» — склейка в `formatGuideDayProgressLine`. */
  guideDayProgressIntro: "Прогресс дня:",
  guideDayProgressOutOf: "из",
  guideEmotionalTriggersTitle: "Эмоциональные триггеры",
  guideTriggerDayCard: "Карта дня",
  guideTriggerRelationshipEnergy: "Энергия отношений",
  guideTriggerQuickDiary: "Быстрый дневник",
  guideShowDayDetailsSummary: "Показать детали дня",
  guideDetailEnergyPrefix: "Энергия:",
  guideDetailFocusPrefix: "Фокус:",
  guideDetailRiskPrefix: "Риск:",
  guideDetailMoonPrefix: "Луна:",
  guideEmotionalRingLove: "Любовь",
  guideEmotionalRingFocus: "Фокус",
  guideEmotionalRingMoney: "Деньги",
  guideEmotionalRingState: "Состояние",

  // --- Четыре сферы ритуала (`todayFourAreas.ts` ⇄ `RitualFourAreaBuilder` в iOS) ---
  fourAreaLabelLove: "Любовь",
  fourAreaLabelWork: "Работа",
  fourAreaLabelMoney: "Деньги",
  fourAreaLabelEnergy: "Энергия",
  fourAreaEnergyHeadlineFallback: "Темп и ресурс",
  /** Склейка с `main_risk` — см. `formatFourAreaEnergyRiskChunk`. */
  fourAreaEnergyRiskChunkPrefix: "Напряжение редко уходит само, пока на фоне: ",
  fourAreaMoodSuffixCautious: " Сейчас особенно важно не форсировать.",
  fourAreaMoodSuffixFuel: " Это можно использовать как топливо, если держать темп.",
  fourAreaLoveInsightFallback: "В близости честный контакт полезнее красивой картинки.",
  fourAreaLoveWatch: "Не пытайся угадать другого человека — лучше сказать прямо.",
  fourAreaLoveReasonBase:
    "Подсказка опирается на твой гороскоп дня и настроение: чем честнее ты с собой в чек-ине, тем меньше «угадайку» в тексте.",
  fourAreaWorkInsightFallback: "Один понятный вектор обычно спокойнее, чем десять задач «на потом».",
  fourAreaWorkWatch: "Сложное лучше расписать или взять в один спокойный слот.",
  fourAreaWorkReasonNoFirstMoveFallback:
    "Если в Flow есть цели и привычки — опираюсь на них; иначе на ось дня из гороскопа, без выдуманных задач.",
  fourAreaMoneyInsightFallback: "Полезно отличить спешку от того, что правда нужно — и не кормить шум.",
  fourAreaMoneyWatch: "Импульсивная трата? Попробуй паузу до вечера.",
  fourAreaMoneyReasonNoAvoidFallback:
    "Фокус на цифрах и границах: что уже есть в твоём дне и что гороскоп помечает как риск импульса.",
  fourAreaEnergyInsightSoftDay: "Собери день мягко, без скачков «на рывок».",
  fourAreaEnergyInsightNoBestModeFallback:
    "Энергия дня не про рывок, а про ровный ритм — чтобы потом не разбирать последствия.",
  fourAreaEnergyWatch: "Сон, еда и вода — раньше новых обещаний кому-то.",
  fourAreaEnergyReasonFallback:
    "Энергия — про сон, нагрузку и эмоциональный фон; собираю это из твоего контекста.",

  // --- Ритуальный поток iOS (`TodayRitualFlowView`) — те же строки в каноне ---
  ritualFlowHeroMetricsDisclaimerRu: "Это метрики в приложении, не предсказание судьбы.",
  ritualFlowHeroMetricsDisclaimerEn: "These are in-app metrics—not a prediction of fate.",
  ritualFlowSphereRhythmA11y: (title: string, pct: number) =>
    `Опора в ритме по теме «${title}»: ${pct} из 100`,
  ritualFlowProtectionSaving: "Сохраняю...",
  ritualFlowProtectionSaveCta: "Защитить это сегодня",
  ritualFlowEveningNarrativeLoading: "Собираю вечерний смысл…",
  ritualFlowEveningHeadlineFallback: "Короткий вечерний вектор",
  ritualFlowHeroSubtitleFallback: "Сегодня важен не контроль, а ясность.",
  ritualFlowNumerologyLinePrefix: "Число: ",
  ritualFlowNumerologyEmpty: "Число: —",
  ritualFlowTriadStrongNoTail: " — сейчас лучшее место для движения.",
  ritualFlowTriadStrongWithTail: " — сейчас лучшее место для движения: ",
  ritualFlowTriadWeakNoTail: " — аккуратно, не дави — лучше сказать прямо, чем угадывать.",
  ritualFlowTriadWeakWithTail: " — аккуратно, не дави: ",
  ritualFlowTriadNeutralNoTail: " — нейтрально, без лишнего импульса.",
  ritualFlowTriadNeutralWithTail: " — нейтрально: ",
  ritualFlowNatalMoonPrefix: "Луна в натале: ",
  ritualFlowProtectionSavedPrefix: "Сохранили. Теперь день собран вокруг: ",
  ritualFlowProtectionSavedSuffix: ".",
  ritualFlowProtectionSaveError: "Не удалось сохранить цель дня. Попробуй ещё раз.",
  ritualFlowProtectionDisciplineTitle: "Дисциплину",
  ritualFlowProtectionDisciplineReason:
    "Если день рассыпается, мягкая дисциплина возвращает тебе управление без жёсткости.",
  ritualFlowProtectionDisciplinePrompt:
    "Сегодня я защищаю дисциплину: один ясный шаг важнее трёх незавершённых.",
  ritualFlowProtectionMoneyReason:
    "Подходит, когда фон дня про ресурс, траты или решения под давлением.",
  ritualFlowProtectionMoneyPrompt:
    "Сегодня я защищаю деньги: не трачу на эмоции и сначала даю себе паузу.",
  ritualFlowProtectionLoveReason:
    "Если день про отношения, лучше беречь честность и темп разговора, а не форсировать ответ.",
  ritualFlowProtectionLovePrompt:
    "Сегодня я защищаю любовь: выбираю честный контакт вместо догадок и напряжения.",
  ritualFlowProtectionBalanceTitle: "Баланс",
  ritualFlowProtectionBalanceReason:
    "Когда внутри тяжело или тревожно, лучше строить день вокруг эмоциональной устойчивости.",
  ritualFlowProtectionBalancePrompt:
    "Сегодня я защищаю баланс: не перегружаю себя и возвращаюсь к телу, если начинает качать.",
  ritualFlowGoalLoveHonestTalkTitle: "Один честный разговор",
  ritualFlowGoalLoveHonestTalkReason:
    "Если день про отношения — не распахивать всё сразу, а прояснить одну вещь, которая болит.",
  ritualFlowGoalLovePauseReplyTitle: "Пауза перед ответом",
  ritualFlowGoalLovePauseReplyReason:
    "Так проще не ответить из обиды или тревоги — и услышать себя.",
  ritualFlowGoalWorkCalmBlockTitle: "Один спокойный рабочий блок",
  ritualFlowGoalWorkCalmBlockReason:
    "Внимание не расползается между задачами — к вечеру легче заметить, что главное для тебя сдвинулось.",
  ritualFlowGoalWorkPauseSpendTitle: "Пауза перед импульсной тратой",
  ritualFlowGoalWorkPauseSpendReason:
    "Если фон про деньги, это часто даёт опору быстрее, чем новые списки планов.",
  ritualFlowGoalNeutralMorningTitle: "Утренний ритм",
  ritualFlowGoalNeutralMorningReason:
    "Вода, чуть движения и один понятный старт — без давления «успеть всё».",
  ritualFlowGoalNeutralOneStepTitle: "Один завершённый шаг",
  ritualFlowGoalNeutralOneStepReason:
    "Конкретика вместо туманного «надо» — так проще почувствовать опору: я справляюсь.",

  // --- Working layer (`TodayWorkingLayerSection.tsx`) ---
  workingLayerDayStepLoading: "Готовим шаг дня…",
  workingLayerNudgeRecsSummary: "Что поможет",
  workingLayerExtraStepTitle: "Добавить ещё один шаг?",
  workingLayerExtraStepLead: "Добавляешь ещё один шаг сегодня?",
  workingLayerExtraStepCaptionPrefix: "На сегодня:",
  workingLayerQuickDecisionYes: "Да, добавляю",
  workingLayerQuickDecisionNo: "Нет, оставлю так",
  workingLayerQuickDecisionUnclear: "Пока не решил(а)",
  workingLayerHintSummary: "Подсказка",
  workingLayerDecisionAckYes: "Хорошо. Добавь только шаг по главному фокусу.",
  workingLayerDecisionAckNo: "Отлично. Так ты сохраняешь энергию для главного.",
  workingLayerDecisionAckUnclear: "Нормально. Сделай паузу и вернись позже.",
  workingLayerRingImpactDecisionDefault: "Каждый такой ответ помогает точнее подбирать подсказки.",
  workingLayerRingImpactDecisionYes: "Отлично. Такой выбор обычно помогает быстрее продвигаться в делах.",
  workingLayerRingImpactDecisionNo: "Отлично. Так ты бережешь силы и не перегружаешь день.",
  workingLayerRingImpactDecisionUnclear: "Нормально. Честная фиксация состояния уже полезна.",
  workingLayerRingImpactQuestionDefault: "Ответы на короткие вопросы помогают лучше подбирать рекомендации.",
  workingLayerRingImpactQuestionLove: "Принято: для тебя сейчас важнее контакт и поддержка.",
  workingLayerRingImpactQuestionMotion: "Принято: тебе лучше заходят короткие действия и движение.",
  workingLayerRingImpactQuestionQuiet: "Принято: тебе нужен более спокойный и бережный режим.",
  workingLayerRingImpactQuestionFallback: "Принято: учту это в следующих подсказках.",
  /** Компактный блок «быстрый ответ» на iOS `TodayView` (паритет `TodayWebWorkingLayerCopy`). */
  workingLayerQuickDecisionSaving: "Сохраняю...",
  workingLayerQuickDecisionSaveCta: "Сохранить быстрый ответ",
  workingLayerQuickDecisionSavedBannerPrefix: "Последний быстрый ответ: ",
  workingLayerQuestionOfDaySavedContextPrefix: "Текущий контекст: ",
  /** Компактный блок «Быстрый ответ» в iOS `TodayView` (`TodayQuickAnswerSection`). */
  workingLayerCompactQuickAnswerEyebrow: "Быстрый ответ",
  workingLayerCompactQuickAnswerTitle: "Спроси о своей ситуации",
  workingLayerCompactQuickAnswerSubtitle:
    "Быстрый ответ нужен не для длинной консультации, а чтобы снять неопределенность и собрать контекст.",
  workingLayerCompactQuickAnswerToneLabel: "Выбери тон ответа",
  workingLayerCompactQuickAnswerYes: "Да",
  workingLayerCompactQuickAnswerNo: "Нет",
  workingLayerCompactQuickAnswerUnclear: "Неясно",
  workingLayerCompactQuickAnswerContextLabel: "Это про отношения или работу?",
  workingLayerCompactQuickAnswerContextRelationships: "Отношения",
  workingLayerCompactQuickAnswerContextWork: "Работа",
  workingLayerCompactQuickAnswerSuccessStatus:
    "Быстрый ответ сохранен. Следующие подсказки станут точнее по твоему контексту.",
  workingLayerPracticeTitle: "Практика дня",
  workingLayerPracticeSubtitle: "Один короткий шаг с таймером.",
  workingLayerPracticeChip: "практика",
  workingLayerPracticeDurationHintPrefix: "Ориентир по времени: ~",
  workingLayerPracticeDurationHintSuffix: " мин",
  workingLayerTimerPauseWord: "Пауза",
  workingLayerTimerStartWord: "Старт",
  workingLayerPracticeMarkDone: "Отметить выполнение",
  workingLayerPracticeCompleting: "…",
  workingLayerPracticeDone: "Готово",
  workingLayerTimerReset: "Сбросить таймер",
  workingLayerPracticeMissing: "Практика не выбрана. Добавь одну на сегодня.",
  workingLayerPracticeCatalogCta: "Каталог практик",
  workingLayerWeeklyFocusTitle: "Фокус недели",
  workingLayerWeeklyFocusSubtitle: "Удержи один приоритет и один шаг.",
  workingLayerWeeklyFocusChip: "фокус",
  workingLayerWeeklyGoalUnset: "Ещё не задан",
  workingLayerWeeklyGoalClosed: "Фокус уже закрыт. Можно поставить следующий.",
  workingLayerWeeklyGoalInProgress: "Фокус уже в работе. Если сегодня шага ещё не было, отметь один.",
  workingLayerWeeklyGoalHasFocus: "Фокус уже есть. Закрепи его сегодня одним небольшим шагом.",
  workingLayerWeeklyGoalEmpty: "Зафиксируй один недельный фокус прямо отсюда.",
  workingLayerQuickAddTitle: "Добавить на месте",
  workingLayerEntityGoal: "Цель",
  workingLayerEntityHabit: "Привычка",
  workingLayerEntityAscetic: "Аскеза",
  workingLayerWizardOpensOverlay: "Откроется поверх этого экрана.",
  workingLayerDailyTrailTitle: "След дня",
  workingLayerUnderstandYouTitle: "Понять тебя точнее",
  workingLayerUnderstandYouSubtitle: "Пара коротких ответов для более точных рекомендаций.",
  workingLayerOptionalChip: "по желанию",
  workingLayerWeeklyStateMapTitle: "Недельная карта состояния",
  workingLayerWeeklyStateMapBody:
    "Сравниваем отметки состояния и дневник, чтобы понять, что улучшает или ухудшает неделю.",
  workingLayerTrendUp: "тренд вверх",
  workingLayerTrendDown: "тренд вниз",
  workingLayerTrendFlat: "стабильно",
  workingLayerAvgStateLabel: "Среднее состояние",
  workingLayerTrackedDaysLabel: "Дней с отметками",
  workingLayerJournalDaysLabel: "Дней с дневником",
  workingLayerInsufficientData: "недостаточно данных",
  workingLayerRecommendationPrefix: "Рекомендация:",

  // --- Сферы на `/today` (`TodayLifeSpheresSection.tsx`) ---
  lifeSpheresDeepenFallbackBody: "Текст пока не готов.",
  lifeSpheresDeepenLoadError: "Не удалось загрузить текст. Попробуй еще раз.",
  lifeSpheresMorningRefreshHint: "Сферы дня загружаются. Открой «Утро» и нажми «Обновить день».",
  lifeSpheresHubTitle: "Сферы дня: что происходит и что делать",
  lifeSpheresHubLead: "Выбери 1 сферу с наибольшим напряжением и сделай один шаг.",
  lifeSpheresScenarioTitleFallback: "Тема",
  lifeSpheresFocusLineFallback: "Открыть чтобы посмотреть прогноз сферы",
  lifeSpheresDeepenLoading: "Загрузка…",
  lifeSpheresDeepenRefreshWhyCta: "Обновить почему",
  lifeSpheresDeepenWhyCta: "Почему это важно",
  lifeSpheresScenarioActionCta: "Что делать",
  lifeSpheresLoveDeepCompatibilityHint: "Для глубокой проверки связи используй экран Совместимость.",

  /** Общие подписи кнопок секций (`TodaySectionPrimitives`, аккордеон сфер). */
  todayUiCollapseCta: "Свернуть",
  todayUiExpandCta: "Развернуть",
  todayUiOpenCta: "Открыть",
  daySectionHeaderHintWhenDone: "Блок уже заполнен, но его можно дополнять в любой момент.",
  daySectionHeaderHintNextStep: "Открой этот блок, когда будешь готов(а) к следующему шагу дня.",

  // --- Вкладка «День» (`TodayDaySection.tsx`) ---
  daySectionTitle: "Шаг дня",
  dayStepLogicEyebrow: "Логика шага дня",
  dayStepLogicBody: "1) Отметь текущее состояние 2) Сделай одну короткую фиксацию 3) Закрой день вечером.",
  dayIntentionEyebrow: "Намерение дня",
  dayPhaseCheckInTitle: "Шаг 1: состояние сейчас",
  dayPhaseCheckInHint: "Коротко зафиксируй, как ты сейчас в середине дня.",
  dayPhaseJournalTitle: "Шаг 2: одна короткая отметка",
  dayPhaseJournalSubtitle: "Достаточно одного действия.",
  dayJournalFixedSummary: "Что уже зафиксировано",
  dayJournalTypeObservation: "Наблюдение",
  dayJournalTypeGratitude: "Благодарность",
  dayJournalTypeInsight: "Инсайт",
  dayJournalPromptObservation: "Что ты сейчас замечаешь в себе или в дне?",
  dayJournalPromptGratitude: "За что сегодня хочется поблагодарить?",
  dayJournalPromptInsight: "Какой вывод или поворот появился?",
  /** Префикс ссылки «Открыть ещё N …»; склонение в `formatDayJournalMoreEntriesCta`. */
  dayJournalMoreEntriesIntro: "Открыть ещё",
  dayEmptyNoMarkers: "Пока нет отметок за день. Добавь состояние или короткую запись.",

  // --- iOS `TodayView` композеры (утро / чек-ин / дневник / вечер) — паритет `TodayWebTodayViewComposerCopy` ---
  todayViewComposerSaving: "Сохраняю...",
  todayViewMorningComposerEyebrow: "Утро",
  todayViewMorningComposerTitle: "Что сейчас важнее всего?",
  todayViewMorningComposerSubtitle:
    "Одна короткая фраза. Не манифест, а реальный ориентир, вокруг которого держится день.",
  todayViewMorningComposerPlaceholder: "Например: не распыляться и держать ровный темп",
  todayViewMorningComposerSaveCta: "Сохранить фокус",
  todayViewMorningComposerSuccessStatus:
    "Фокус сохранен. Теперь день привязан к твоей реальной задаче.",
  todayViewPulseEyebrow: "Чек-ин",
  todayViewPulseTitle: "Как ты себя чувствуешь сегодня?",
  todayViewPulseSubtitle:
    "Один тап уже помогает понять, стоит ли усилить действие или, наоборот, смягчить день.",
  todayViewPulseNotePlaceholder: "Что сильнее всего влияет на тебя прямо сейчас?",
  todayViewPulseSaveCta: "Отметить состояние",
  todayViewPulseLastSignalBannerPrefix: "Последний сигнал: ",
  todayViewPulseComposedEnergyPrefix: "Энергия: ",
  todayViewPulseComposedMoodPrefix: "Настроение: ",
  todayViewPulseComposedStressPrefix: "Стресс: ",
  todayViewPulseComposedSeparator: " · ",
  todayViewPulseEnergyLow: "Низкая",
  todayViewPulseEnergyMedium: "Средняя",
  todayViewPulseEnergyHigh: "Высокая",
  todayViewPulseMoodCalm: "Спокойно",
  todayViewPulseMoodOpen: "Открыто",
  todayViewPulseMoodTense: "Напряжённо",
  todayViewPulseStressLow: "Низкий",
  todayViewPulseStressMedium: "Средний",
  todayViewPulseStressHigh: "Высокий",
  todayViewPulseSuccessStatus: "Состояние сохранено. Рекомендации уже могут подстроиться точнее.",
  todayViewJournalEyebrow: "Дневник",
  todayViewJournalTitle: "Одна полезная заметка",
  todayViewJournalSubtitle:
    "Короткая запись помогает лучше видеть не только день, но и повторяющиеся ситуации.",
  todayViewJournalPickerLabel: "Тип записи",
  todayViewJournalSaveCta: "Сохранить заметку",
  todayViewJournalSuccessStatus: "Запись сохранена. Это поможет давать тебе более точные подсказки.",
  todayViewEveningComposerEyebrow: "Вечер",
  todayViewEveningComposerTitle: "Как прошел день?",
  todayViewEveningComposerSubtitle:
    "Вечером нужен короткий итог: что оказалось лучше, где было трудно и какой сигнал стоит запомнить.",
  todayViewEveningComposerReflectionPlaceholder: "Что в итоге оказался этот день для тебя?",
  todayViewEveningComposerNoticedTitle: "Что заметила",
  todayViewEveningComposerHardestTitle: "Где было сложнее",
  todayViewEveningComposerEasierTitle: "Что оказалось легче",
  todayViewEveningComposerMarkClosedToggle: "Отметить день как закрытый",
  todayViewEveningComposerSaveCta: "Сохранить рефлексию",
  todayViewEveningComposerSuccessStatus:
    "Рефлексия сохранена. Следующие дни станут точнее на основе этого сигнала.",

  // --- Навигация шагов (`TodayFlowTabs.tsx`, `TODAY_FLOW_TABS` в `todayPageUtils.ts`) ---
  todayFlowTabsNavAriaLabel: "Шаги дня",
  todayFlowTabGuideLabel: "Главное",
  todayFlowTabGuideDesc: "Сейчас и следующий шаг",
  todayFlowTabSpheresLabel: "Сферы",
  todayFlowTabSpheresDesc: "Где усилить день",
  todayFlowTabMorningLabel: "Утро",
  todayFlowTabMorningDesc: "Старт и намерение",
  todayFlowTabDayLabel: "День",
  todayFlowTabDayDesc: "Ритм и действия",
  todayFlowTabEveningLabel: "Вечер",
  todayFlowTabEveningDesc: "Закрытие и вывод",

  /** Прогрев первой загрузки / обновления (`thinkingMessages` в `todayPageUtils.ts`). */
  todayPageThinkingInitialTitle: "Открываем день",
  todayPageThinkingInitialMessage: "Подожди немного. Загружаю твой сегодняшний экран.",
  todayPageThinkingInitialStatus: "Загружаем данные дня",
  todayPageThinkingRefreshTitle: "Обновляем день",
  todayPageThinkingRefreshMessage: "Подожди немного. Обновляю сегодняшние материалы.",
  todayPageThinkingRefreshStatus: "Обновляем содержимое дня",
  todayPageThinkingRevealTitle: "Готовим день",
  todayPageThinkingRevealMessage: "Подожди немного. Скоро всё появится.",
  todayPageThinkingRevealStatus: "Готовим материалы дня",

  /** Персональные ссылки «продолжить тему» из сферы (`getHoroscopeScenarioRoute`). */
  horoscopeScenarioRouteLove: "Разобрать тему любви для себя",
  horoscopeScenarioRouteFamily: "Записать про семью в дневник",
  horoscopeScenarioRouteCareer: "Вопросы про карьеру",
  horoscopeScenarioRouteMoney: "Вопросы про деньги",
  horoscopeScenarioRouteDefault: "Открыть профиль",

  // --- Контекст дня для нарратива и карточки «Твой день» (`todayPageUtils.ts`) ---
  dayEventsMorningFocusPrefix: "Фокус утра: ",
  dayEventsIntentionPrefix: "Намерение: ",
  dayEventsTrackerPrefix: "Шаг дня: ",
  dayEventsDayCycleCompleted: "Дневной цикл отмечен как завершённый",
  ritualEntrySublineClosing:
    "Дальше — карта дня, число и короткий чек состояния: так Today опирается на твои данные, а не на общие фразы.",

  rhythmTooltipProgressMark: "• Отметка прогресса",
  rhythmTooltipStateMark: "• Состояние зафиксировано",
  rhythmTooltipNoteMark: "• Есть заметка",
  rhythmTooltipPracticeMark: "• Выполнена практика",
  rhythmTooltipJournalMark: "• Есть запись в дневнике",
  rhythmTooltipNoActivity: "• Активности не зафиксированы",
  rhythmTooltipClickUnmarkDay: "Клик: снять отметку в карте",
  rhythmTooltipClickMarkDay: "Клик: отметить день в карте",

  dailyRewardBadgePractice: "Практика дня",
  dailyRewardBadgeWeeklyStep: "Шаг недельного фокуса",
  dailyRewardBadgeDayClosed: "День закрыт",
  dailyRewardGoldTitle: "День в опоре",
  dailyRewardGoldMessage: "Хороший темп. Продолжай по текущему фокусу и не добавляй лишнего.",
  dailyRewardGoldFallbackBadge: "Стабильный фокус",
  dailyRewardSilverTitle: "Ровный ход",
  dailyRewardSilverMessage: "Ровный ход. Закрой один небольшой шаг и двигайся дальше.",
  dailyRewardSilverFallbackBadge: "Ровный ритм",
  dailyRewardBronzeTitle: "Точка старта",
  dailyRewardBronzeMessage: "Начни с одного простого шага и доведи его до конца.",
  dailyRewardBronzeFallbackBadge: "Первый шаг",

  rewardsCardTitleGold: "Высокий уровень",
  rewardsCardTitleSilver: "Уверенный уровень",
  rewardsCardTitleBronze: "Стартовый уровень",

  personalInsightLocalNameFallback: "Ты",
  personalInsightTitleHigh: "Опора через профиль",
  personalInsightTitleMid: "День держится",
  personalInsightTitleStart: "Старт дня",
  personalInsightChipFallbackLow: "Низкий порог входа",
  personalInsightChipFallbackStable: "Стабильный ритм",
  personalInsightChipFallbackStep: "Один шаг сейчас",
  personalInsightCtaReturnMap: "Вернуться к карте профиля",
  personalInsightCtaOpenMap: "Открыть карту профиля",
  personalInsightCtaViewMap: "Посмотреть карту профиля",

  nextActionChooseFocusLabel: "Выбрать фокус дня",
  nextActionChooseFocusMessage: "Назови одной фразой, что для тебя главное сегодня.",
  nextActionDoPracticeLabel: "Сделать практику",
  nextActionChoosePracticeLabel: "Выбрать практику",
  nextActionPracticeMessage: "Сделай одно короткое действие.",
  nextActionWeeklyStepLabel: "Шаг по недельному фокусу",
  nextActionWeeklyStepMessage: "Отметь один шаг по недельному фокусу.",
  nextActionEveningLabel: "Подвести итог дня",
  nextActionEveningMessage: "Коротко подведи итог дня.",
  nextActionStateLabel: "Отметить состояние",
  nextActionStateMessage: "Отметь состояние дня.",

  dailyNudgeHighMessage: "Сбавь темп. Выбери одно короткое действие и отметь состояние.",
  dailyNudgeHighCta: "Сделать одно действие",
  dailyNudgeMediumMessage: "Сделай один шаг и сразу отметь его.",
  dailyNudgeMediumCta: "Зафиксировать шаг",
  dailyNudgeLowMorningMessage: "Для старта выбери одну главную задачу.",
  dailyNudgeLowMorningCta: "Открыть утро",
  dailyNudgeLowDayMessage: "Сделай один точный шаг.",
  dailyNudgeLowDayCta: "Сделать один шаг",
  dailyNudgeLowEveningMessage: "Подведи итог и закрой день.",
  dailyNudgeLowEveningCta: "Закрыть день",

  dayEnergyLabelCareful: "бережный режим",
  dayEnergyGuidanceCareful: "Сбавь темп и двигайся короткими шагами.",
  dayEnergyLabelStable: "стабильный день",
  dayEnergyGuidanceStable: "Держи ровный темп и закрывай задачи по одной.",
  dayEnergyLabelActive: "день действий",
  dayEnergyGuidanceActive: "Ресурса больше обычного. Держи фокус на главном.",

  // --- Фокус, риск, план, недельный паттерн, «сейчас в жизни», ритм возврата (`todayPageUtils.ts`) ---
  dayFocusThemeWork: "работа",
  dayFocusThemeMoney: "деньги",
  dayFocusThemeRelationships: "отношения",
  dayFocusThemeRecovery: "восстановление",
  dayFocusThemeClosure: "завершение",
  dayFocusFallbackPrimary1: "работа",
  dayFocusFallbackPrimary2: "восстановление",
  dayFocusFallbackLabel: "работа, восстановление",

  dayRiskFusionEmotionalLabel: "конфликт и перегрев",
  dayRiskFusionEmotionalDetail: "Сегодня легче, чем обычно, уйти в резкость и эмоциональные реакции.",
  dayRiskFusionFocusLabel: "ошибки от расфокуса",
  dayRiskFusionFocusDetail: "Главный риск дня не в событиях, а в том, что внимание распадётся на мелочи.",
  dayRiskFusionEnergyLabel: "усталость",
  dayRiskFusionEnergyDetail: "Лучше не перегружать себя и не путать усталость с отсутствием мотивации.",
  dayRiskFusionDefaultLabel: "импульсивные решения",
  dayRiskFusionDefaultDetail: "Сегодня не спеши там, где важна спокойная проверка деталей.",

  todayCriticalLimitAmplifyPrefix: "не усиливать: ",

  weeklyPatternMoodUp: "Настроение к концу недели стало выше.",
  weeklyPatternMoodDown: "Настроение к концу недели снизилось.",
  weeklyPatternTrackedOften: "Состояние отслеживается регулярно.",
  weeklyPatternTrackedRare: "Мало отметок состояния — паттерны читаются слабо.",
  weeklyPatternJournalHelps: "Дневник помогает фиксировать контекст изменений.",
  weeklyPatternJournalNone: "Нет записей в дневнике — сложнее понять причины скачков.",
  weeklyPatternRecCareful3d:
    "Сделай ближайшие 3 дня в бережном режиме: 1 приоритет, вечерняя рефлексия и минимум перегруза.",
  weeklyPatternRecKeepRhythm:
    "Сохрани рабочий ритм: повтори действия, которые давали улучшение, и не добавляй лишние задачи.",
  weeklyPatternRecNeutral:
    "Паттерн недели нейтральный: чтобы понять триггеры, добавь 1 короткую отметку состояния и 1 запись в дневник в день.",

  lifeNowWeeklyCompletedBody: "Эта недельная линия уже закрыта. Сегодня можно не возвращаться к ней.",
  lifeNowWeeklyProgressStaleBody: "Чтобы не потерять недельный фокус, отметь сегодня один реальный шаг.",
  lifeNowWeeklyProgressFreshBody: "Отметь один короткий шаг по недельному фокусу.",
  lifeNowDisciplineTitleFallback: "Ритм дисциплины",
  lifeNowDisciplineBodyPractice: "Это короткая опора на сегодня. Выполни и зафиксируй.",

  dailyReturnMorningEarlyTitle: "Начни с фокуса дня",
  dailyReturnMorningLateTitle: "Вернись к фокусу дня",
  dailyReturnMorningEarlyMessage: "Сначала выбери фокус, потом переходи к действиям.",
  dailyReturnMorningLateMessage: "Коротко вернись к фокусу.",
  dailyReturnMorningCta: "Открыть утро",
  dailyReturnMorningChip: "Первый заход",
  dailyReturnDayTitle: "Коротко отметь шаг за день",
  dailyReturnDayMessageEarly: "Когда появятся 3-5 минут, отметь один реальный шаг.",
  dailyReturnDayMessageDefault: "Отметь один сделанный шаг.",
  dailyReturnDayCta: "Отметить шаг",
  dailyReturnDayChip: "Короткий возврат",
  dailyReturnEveningTitleLate: "Позже стоит вернуться за коротким итогом",
  dailyReturnEveningTitlePrepare: "На вечер оставь только честный короткий итог",
  dailyReturnEveningMessageLate: "Заверши день спокойно: одна фраза и пара наблюдений.",
  dailyReturnEveningMessageDefault: "Когда завершишь основное, вернись сюда на короткий итог.",
  dailyReturnEveningCta: "Открыть итог дня",
  dailyReturnEveningChip: "Поздний возврат",
  dailyReturnAllSetTitle: "На сегодня всё",
  dailyReturnAllSetMessage: "На сегодня достаточно. Если вернёшься, проверь фокус и состояние.",
  dailyReturnAllSetCta: "Открыть утро",
  dailyReturnAllSetChip: "День закрыт",

  // --- Утро на `/today` (`TodayMorningSection.tsx`) ---
  morningSectionTitle: "Утро и опора дня",
  morningTarotRevealCta: "Открыть карту дня",
  morningTarotClosedHint: "Карта пока закрыта. Открой её.",
  morningTarotEyebrow: "Карта дня",
  morningTarotNameFallback: "Карта дня",
  morningNumerologyClosedHint: "Число пока скрыто. Открой его.",
  morningNumerologyEyebrow: "Число дня",
  morningDetailsHideCta: "Скрыть детали",
  morningDetailsShowCta: "Детали",
  morningCombinedSummaryEyebrow: "Коротко на сегодня",
  morningCombinedBothOpenLine: "Карта и число уже дают понятную опору на день.",
  morningCombinedTarotOnlyLine: "Карта дня уже открыта. Держи фокус на главном.",
  morningCombinedNumberOnlyLine: "Число дня открыто. Держи спокойный темп и не перегружай себя.",
  morningHoroscopeHintSummary: "Подсказка утра",
  morningPhaseCheckInTitle: "Состояние: утро",
  morningPhaseCheckInHint: "Коротко отметь настроение, энергию и напряжение.",
  morningIntentionEyebrow: "Намерение на день",
  morningIntentionLead: "Одна фраза для дня",
  morningIntentionHint: "Коротко: что важно удержать до вечера.",
  morningIntentionPlaceholder: "Например: сегодня держу спокойный темп в важных разговорах.",
  morningEmptyStateLine: "Начни с карты и короткого намерения.",
  morningRefreshingShort: "Обновляю...",
  morningRefreshBlockCta: "Обновить утро",
  morningTarotDetailWhyCard: "Почему эта карта",
  morningDetailHowDay: "Как может складываться день",
  morningDetailPossibleEvents: "Что может проявиться",
  morningDetailWhatSupports: "Что поддержит",
  morningDetailWhatNotAmplify: "Чего не усиливать",
  morningTarotKeywordsLabel: "Ключевые слова",
  morningNumerologyDetailWhyNumber: "Почему это число",
  morningNumerologyDetailSupplement: "Дополнение",

  // --- Вечер на `/today` (`TodayEveningSection.tsx`) ---
  eveningSectionTitle: "Закрыть день",
  eveningOutlookLoadError: "Не удалось загрузить итог. Попробуй еще раз.",
  eveningOutlookLoading: "Загружаем итог дня…",
  eveningNarrativePreparing: "Готовим итог дня…",
  eveningOutlookSummaryEyebrow: "Сводка",
  eveningOutlookMapTitle: "Карта состояния дня",
  eveningOutlookPreambleDefault: "Утро, день и вечер — на одной линии. Ниже короткий итог по дню.",
  eveningOutlookPhaseMorning: "Утро",
  eveningOutlookPhaseDay: "День",
  eveningOutlookPhaseEvening: "Вечер",
  eveningPhaseNoCheckinYet: "ещё нет отметки",
  eveningScaleMoodLabel: "Настроение",
  eveningScaleEnergyLabel: "Энергия",
  eveningScaleStressLabel: "Стресс",
  eveningPhaseHasNote: "есть заметка",
  eveningChipDayLine: "линия дня",
  eveningChipIntentionSaved: "намерение записано",
  eveningChipGoalStepsPrefix: "шаги по целям:",
  eveningChipHabitsPrefix: "привычки:",
  eveningTextSectionEyebrow: "Текстом",
  eveningOpenCalendarCta: "Открыть в календаре",
  eveningClosureCardTitle: "Завершение дня",
  eveningClosingPhrasePlaceholder: "Завершающая фраза дня (по желанию)",
  eveningMarkedDoneCheckbox: "День завершён",
  eveningMarkedDoneEncouragement: "На сегодня достаточно. Возьми с собой главное.",
  eveningPhaseCheckInHint: "Коротко отметь состояние перед итогом дня.",
  eveningOpenStateMapSummary: "Открыть карту состояния дня",
  eveningReflectionTitle: "Итог дня",
  eveningReflectionPlaceholder: "Что сработало сегодня и что берешь в завтра?",
  eveningExtraDetailsSummary: "Если хочешь добавить детали",
  eveningObsPlaceholderNoticed: "Что сегодня особенно заметил",
  eveningObsPlaceholderHardest: "Где было сложнее всего",
  eveningObsPlaceholderEasier: "Что далось легче",
  eveningSaveSummaryCta: "Сохранить итог",
  eveningRefreshBlockCta: "Обновить блок",
  eveningCompletedCheckLine: "✓ День завершён",
  eveningDayStartLinkSummary: "Связь с началом дня",
  eveningMorningIntentionRecall: "🌅 В начале дня ты хотел:",
  eveningObservationsHeading: "👁️ Наблюдения:",
  eveningObsStrongNoticed: "Заметил:",
  eveningObsStrongHardest: "Сложнее всего:",
  eveningObsStrongEasier: "Легче, чем ожидал:",
  eveningReflectionBlockHeading: "💭 Рефлексия:",
  eveningThreadBlockHeading: "🧵 Главная линия:",
  eveningEmptyClosingHint: "Закрой день в любой момент: одна фраза и пара наблюдений.",

  numberRevealDoneCta: "Готово",
} as const;

/** Карточка «вопрос дня» в блоке «Понять тебя точнее» (`TodayWorkingLayerSection`, `buildQuestionOfDay`). */
export type RitualQuestionOfDayCard = {
  prompt: string;
  options: { id: string; label: string; response: string }[];
};

/** Набор вопросов при низкой энергии (fusion.scores.energy < 45). */
export const RITUAL_QUESTION_OF_DAY_LOW_ENERGY_CARDS: RitualQuestionOfDayCard[] = [
  {
    prompt: "Когда сил мало, что чаще всего помогает тебе удержаться?",
    options: [
      { id: "restore_boundary", label: "пауза и границы", response: "Зафиксировали: опора через паузу и бережные границы." },
      {
        id: "tiny_step",
        label: "один конкретный шаг",
        response: "Записано: для тебя сейчас лучше срабатывает один полностью завершённый фрагмент дела.",
      },
      { id: "people_warmth", label: "теплый контакт", response: "Зафиксировали: ресурс возвращают люди и поддержка." },
      { id: "unclear_low", label: "по-разному, зависит от дня", response: "Отметили вариативность. Будем точнее подбирать формат опоры." },
    ],
  },
  {
    prompt: "Что чаще всего ухудшает твое состояние в такие дни?",
    options: [
      { id: "noise_overload", label: "шум и перегруз стимулами", response: "Принято. Добавим акцент на тихие окна и паузы." },
      { id: "unclear_tasks", label: "непонятные задачи", response: "Принято. Усилим рекомендацию на один ясный шаг." },
      { id: "people_pressure", label: "давление от общения", response: "Принято. Учтем границы в социальных сценариях." },
      { id: "late_sleep", label: "сбитый сон и режим", response: "Принято. Будем чаще предлагать бережный вечерний ритуал." },
    ],
  },
];

/** Три карточки при обычной энергии; третья зависит от fusion.scores.focus. */
export function buildRitualQuestionOfDayDefaultCards(lowFocus: boolean): RitualQuestionOfDayCard[] {
  const third: RitualQuestionOfDayCard = lowFocus
    ? {
        prompt: "Что чаще всего мешает держать фокус?",
        options: [
          { id: "focus_notifications", label: "уведомления и отвлечения", response: "Учли: добавим рекомендации по защите фокуса." },
          { id: "focus_anxiety", label: "внутреннее напряжение", response: "Учли: добавим бережные антистресс-шаги." },
          { id: "focus_unclear_priority", label: "нет одного приоритета", response: "Учли: усилим блок с одним главным шагом." },
          { id: "focus_fatigue", label: "усталость к середине дня", response: "Учли: чаще предложим восстановление перед задачами." },
        ],
      }
    : {
        prompt: "Что сегодня важнее всего продвинуть?",
        options: [
          { id: "priority_money", label: "деньги и работа", response: "Принято. Усилю прикладные шаги по деньгам и задачам." },
          { id: "priority_relationships", label: "отношения и коммуникация", response: "Принято. Усилю рекомендации по общению и границам." },
          { id: "priority_health", label: "состояние и энергия", response: "Принято. Усилю восстановительный контур дня." },
          { id: "priority_self", label: "я и внутренний порядок", response: "Принято. Предложу более спокойный и сфокусированный ритм." },
        ],
      };

  return [
    {
      prompt: "Что сейчас лучше всего помогает тебе восстанавливаться?",
      options: [
        { id: "rhythm_home", label: "ритм, дом, бытовая опора", response: "Зафиксировали: опора в устойчивом ритме и простых действиях." },
        { id: "people_exchange", label: "люди и живой обмен", response: "Зафиксировали: тебе помогает контакт и диалог." },
        { id: "quiet_depth", label: "тишина и глубокий фокус", response: "Зафиксировали: тебе нужен тихий режим и глубина." },
        { id: "motion_change", label: "движение и смена обстановки", response: "Зафиксировали: ресурс приходит через движение и новизну." },
      ],
    },
    {
      prompt: "Какой формат рекомендаций тебе удобнее сегодня?",
      options: [
        { id: "format_short", label: "очень коротко: 1-2 пункта", response: "Принято. Дадим более компактные подсказки." },
        { id: "format_structured", label: "структурно: что/почему/как", response: "Принято. Дадим рекомендации в структурном формате." },
        { id: "format_emotional", label: "через смысл и поддержку", response: "Принято. Усилим эмоциональную часть рекомендаций." },
        { id: "format_action", label: "только действия без лишнего", response: "Принято. Приоритет на прикладные шаги." },
      ],
    },
    third,
  ];
}

/** Три варианта «удачного окна» для блока числа (цикл по дате; паритет iOS `NumerologyLuckyDayPresets`). */
export const NUMEROLOGY_LUCKY_DAY_PRESETS = [
  { time: "8:00–10:00", color: "Лазурь", stone: "Сапфир" },
  { time: "14:00–16:00", color: "Глубокий синий", stone: "Лунный камень" },
  { time: "19:00–21:00", color: "Индиго", stone: "Аметист" },
] as const;

/** Связка «карта + число» до интерактивного выбора (паритет iOS `formatRitualCardNumberBridgePageFallback`). */
export function formatRitualCardNumberBridgePageFallback(cardName: string, numerologyValue: string): string {
  return `«${cardName}» и число ${numerologyValue} просят одного: внутренняя честность — раньше внешнего «надо».`;
}

/** После вытягивания карты из каталога (паритет iOS `formatRitualCardNumberBridgeWithTarotPicked`). */
export function formatRitualCardNumberBridgeWithTarotPicked(
  cardNameRu: string,
  numerologyValue: string,
  rhythmSuffix: string,
  clarifierNameRu: string | null | undefined,
): string {
  const c = clarifierNameRu != null ? String(clarifierNameRu).trim() : "";
  const extra = c ? ` Уточнение — «${c}»: второй акцент к символу дня.` : "";
  return `«${cardNameRu}» и число ${numerologyValue}: картой задаёшь акцент дня; ${rhythmSuffix}.${extra}`;
}

/** Вторая строка героя входа в ритуал: шаги + опционально карта/число (паритет iOS). */
export function formatRitualEntryProgressTarotNumberHint(input: {
  drawnTarotNameRu: string | null | undefined;
  numerologyValue: string;
  numberRevealed: boolean;
}): string {
  const name = input.drawnTarotNameRu != null ? String(input.drawnTarotNameRu).trim() : "";
  const cardPart = name ? `${RITUAL_COPY.ritualProgressCardLabel}: «${name}». ` : "";
  const numPart = input.numberRevealed
    ? `${RITUAL_COPY.ritualProgressNumberLabel}: ${input.numerologyValue}.`
    : RITUAL_COPY.ritualProgressNumberPending;
  return `${RITUAL_COPY.ritualProgressHint} ${cardPart}${numPart}`;
}

/** Подзаголовок блока числа в шите «карта и число». */
export function formatRitualCardNumberDetailEyebrow(numerologyValue: string): string {
  return `${RITUAL_COPY.ritualProgressNumberLabel} ${numerologyValue}`;
}

/** Хвост подписи варианта главного шага с оценкой длительности. */
export function formatActionOptionEstimatedMinutesSuffix(minutes: number): string {
  return ` · ~${minutes} мин`;
}

export function formatGuideDayProgressLine(percent: number, completed: number, total: number): string {
  return `${RITUAL_COPY.guideDayProgressIntro} ${percent}% (${completed} ${RITUAL_COPY.guideDayProgressOutOf} ${total})`;
}

/** Риск в блоке детали сферы «Энергия» — паритет iOS `RitualFourAreaBuilder.energyToday`. */
export function formatFourAreaEnergyRiskChunk(risk: string): string {
  return `${RITUAL_COPY.fourAreaEnergyRiskChunkPrefix}${risk}`;
}

export function formatRitualFlowSphereRhythmA11y(title: string, pct: number): string {
  return RITUAL_COPY.ritualFlowSphereRhythmA11y(title, pct);
}

export function formatRitualFlowTriadLine(head: string, tail: string, stance: "up" | "down" | "neutral"): string {
  const t = tail.trim();
  if (stance === "up") {
    return t.length === 0
      ? `${head}${RITUAL_COPY.ritualFlowTriadStrongNoTail}`
      : `${head}${RITUAL_COPY.ritualFlowTriadStrongWithTail}${t}`;
  }
  if (stance === "down") {
    return t.length === 0
      ? `${head}${RITUAL_COPY.ritualFlowTriadWeakNoTail}`
      : `${head}${RITUAL_COPY.ritualFlowTriadWeakWithTail}${t}`;
  }
  return t.length === 0
    ? `${head}${RITUAL_COPY.ritualFlowTriadNeutralNoTail}`
    : `${head}${RITUAL_COPY.ritualFlowTriadNeutralWithTail}${t}`;
}

export function formatRitualFlowProtectionSaved(titleLowercased: string): string {
  return `${RITUAL_COPY.ritualFlowProtectionSavedPrefix}${titleLowercased}${RITUAL_COPY.ritualFlowProtectionSavedSuffix}`;
}

export function formatRitualFlowNumerologyLine(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return RITUAL_COPY.ritualFlowNumerologyEmpty;
  }
  return `${RITUAL_COPY.ritualFlowNumerologyLinePrefix}${value}`;
}

export function formatRitualFlowNatalMoon(sign: string): string {
  return `${RITUAL_COPY.ritualFlowNatalMoonPrefix}${sign}`;
}

export function fourAreaMoodSuffix(mood: string | null | undefined): string {
  if (!mood) return "";
  switch (mood) {
    case "anxious":
    case "heavy":
    case "confused":
      return RITUAL_COPY.fourAreaMoodSuffixCautious;
    case "motivated":
    case "hopeful":
    case "driven":
      return RITUAL_COPY.fourAreaMoodSuffixFuel;
    default:
      return "";
  }
}

export function formatWorkingLayerPracticeDurationHint(minutes: number): string {
  return `${RITUAL_COPY.workingLayerPracticeDurationHintPrefix}${minutes}${RITUAL_COPY.workingLayerPracticeDurationHintSuffix}`;
}

export function formatWorkingLayerMiniDecisionCaption(caption: string): string {
  return `${RITUAL_COPY.workingLayerExtraStepCaptionPrefix} ${caption}`;
}

export function formatWeeklyPatternRecommendation(recommendation: string): string {
  return `${RITUAL_COPY.workingLayerRecommendationPrefix} ${recommendation}`;
}

/** Склонение «запись» после числа для ссылки в дневник (`TodayDaySection`). */
export function formatDayJournalMoreEntriesCta(count: number): string {
  const suffix = count === 1 ? "ь" : count < 5 ? "и" : "ей";
  return `${RITUAL_COPY.dayJournalMoreEntriesIntro} ${count} запис${suffix}`;
}

/** Баннер «текущее намерение» в композере утра (`TodayView` iOS). */
export function formatTodayViewMorningComposerSavedBanner(saved: string): string {
  return `Текущее намерение: “${saved}”`;
}

/** Склонение «запись» в баннере счётчика дневника на `TodayView` (iOS). */
export function formatTodayViewJournalSavedCountBanner(count: number): string {
  const mod100 = count % 100;
  const mod10 = count % 10;
  let word: string;
  if (mod100 >= 11 && mod100 <= 14) word = "записей";
  else if (mod10 === 1) word = "запись";
  else if (mod10 >= 2 && mod10 <= 4) word = "записи";
  else word = "записей";
  return `Сегодня уже сохранено ${count} ${word}.`;
}

/** `buildDayEventsForNarrative` — паритет iOS `TodayWebTodayPageDataCopy.formatDayEventsJournalCount`. */
export function formatDayEventsJournalCount(count: number): string {
  return `Дневник: записей сегодня — ${count}`;
}

/** Паритет iOS `TodayWebTodayPageDataCopy.formatRitualEntrySublineFocusSnippet`. */
export function formatRitualEntrySublineFocusSnippet(s: string): string {
  return `В приложении уже есть фокус: «${s}»`;
}

export function formatRitualEntrySublineIntentionSnippet(s: string): string {
  return `Намерение на день: «${s}»`;
}

export function formatRitualEntrySublineCalendarLine(title: string): string {
  return `В календаре сегодня: ${title}`;
}

export function formatRitualEntrySublineProfileSunMoon(sun: string, lunarName: string): string {
  return `По профилю: Солнце в ${sun}; луна сейчас — ${lunarName}.`;
}

export function formatRitualEntrySublineProfileSunOnly(sun: string): string {
  return `По профилю: Солнце в ${sun}.`;
}

export function formatRitualEntrySublineLunarOnly(lunarName: string): string {
  return `Лунный фон дня: ${lunarName}.`;
}

export function formatDailyRewardStreakBadge(streakDays: number): string {
  return `Серия ${streakDays} дней`;
}

export function formatRewardsCardStreakBadge(n: number): string {
  return `Стрик ${n} дн.`;
}

export function formatRewardsCardArchetypeBadge(level: string): string {
  return `Архетип ${level}`;
}

export function formatRewardsCardDisciplineBadge(score: number): string {
  return `Дисциплина ${score}`;
}

export function formatRewardsCardHabitsBadge(n: number): string {
  return `Привычки ${n}`;
}

export function formatRewardsCardAsceticBadge(n: number): string {
  return `Аскеза ${n}`;
}

export function formatPersonalInsightChipTarot(name: string): string {
  return `Таро: ${name}`;
}

export function formatPersonalInsightChipNumber(value: string | number): string {
  return `Число дня: ${value}`;
}

export function formatPersonalInsightChipEnergy(tier: string): string {
  return `Энергия: ${tier}`;
}

export function formatPersonalInsightChipFocus(tier: string): string {
  return `Фокус: ${tier}`;
}

export function formatPersonalInsightChipStreak(days: number): string {
  return `Серия ${days} дн.`;
}

export function formatPersonalInsightMessageHighWithAnchor(localName: string, profileAnchor: string): string {
  return `${localName}, спокойный темп на сегодня: ${profileAnchor} Выбери одно короткое действие и закрой его.`;
}

export function formatPersonalInsightMessageHighNoAnchor(localName: string): string {
  return `${localName}, держи спокойный темп. Одно короткое действие и отметка состояния — достаточно.`;
}

export function formatPersonalInsightMessageMidWithAnchor(localName: string, profileAnchor: string): string {
  return `${localName}, день держится на базе: ${profileAnchor} Доведи один главный приоритет до результата.`;
}

export function formatPersonalInsightMessageMidNoAnchor(localName: string): string {
  return `${localName}, день держится хорошо. Доведи один главный приоритет до результата.`;
}

export function formatPersonalInsightMessageStartWithAnchor(localName: string, profileAnchor: string): string {
  return `${localName}, начни с базы: ${profileAnchor} Выбери одно действие на 5-10 минут и сразу отметь результат.`;
}

export function formatPersonalInsightMessageStartNoAnchor(localName: string): string {
  return `${localName}, начни с одного действия на 5-10 минут и сразу отметь результат.`;
}

export function formatActionPlanWeeklyStep(title: string): string {
  return `закрыть один шаг по недельному фокусу: ${title}`;
}

export function formatActionPlanQuickPractice(title: string): string {
  return `сделать короткую практику: ${title}`;
}

export function formatTodayCriticalLimitAmplify(riskLabel: string): string {
  return `${RITUAL_COPY.todayCriticalLimitAmplifyPrefix}${riskLabel}`;
}

export function formatLifeNowDisciplineBodyAscetic(days: number): string {
  return `Лучшая серия аскезы: ${days} дн. Удержи ритм до вечера.`;
}

export function formatLifeNowDisciplineBodyHabit(days: number): string {
  return `Лучшая серия привычки: ${days} дн. Удержи ритм.`;
}

export function formatLifeNowDisciplineStatusMinutes(minutes: number): string {
  return `${minutes} мин`;
}

export function formatLifeNowDisciplineStatusAscetic(n: number): string {
  return `Аскеза ${n}`;
}

export function formatLifeNowDisciplineStatusHabit(n: number): string {
  return `Привычка ${n}`;
}

export function formatEveningOutlookGoalStepsChip(n: number): string {
  return `${RITUAL_COPY.eveningChipGoalStepsPrefix} ${n}`;
}

export function formatEveningOutlookHabitsChip(n: number): string {
  return `${RITUAL_COPY.eveningChipHabitsPrefix} ${n}`;
}

export function formatWorkingLayerTimerButton(mode: "pause" | "start", formattedTime: string): string {
  const word = mode === "pause" ? RITUAL_COPY.workingLayerTimerPauseWord : RITUAL_COPY.workingLayerTimerStartWord;
  return `${word} ${formattedTime}`;
}

export function workingLayerRingImpactForDecision(answer: "yes" | "no" | "unclear" | null): string {
  if (answer === "yes") return RITUAL_COPY.workingLayerRingImpactDecisionYes;
  if (answer === "no") return RITUAL_COPY.workingLayerRingImpactDecisionNo;
  if (answer === "unclear") return RITUAL_COPY.workingLayerRingImpactDecisionUnclear;
  return RITUAL_COPY.workingLayerRingImpactDecisionDefault;
}

export function workingLayerRingImpactForQuestion(optionId: string | null): string {
  const key = String(optionId || "").toLowerCase();
  if (!key) return RITUAL_COPY.workingLayerRingImpactQuestionDefault;
  if (key.includes("people") || key.includes("love")) return RITUAL_COPY.workingLayerRingImpactQuestionLove;
  if (key.includes("step") || key.includes("motion")) return RITUAL_COPY.workingLayerRingImpactQuestionMotion;
  if (key.includes("quiet") || key.includes("boundary")) return RITUAL_COPY.workingLayerRingImpactQuestionQuiet;
  return RITUAL_COPY.workingLayerRingImpactQuestionFallback;
}

/**
 * Оболочка экрана Today в iOS (`TodayView.swift`); веб может переиспользовать при паритете.
 * Только пользовательский смысл — без описания устройства системы.
 */
export const TODAY_SHELL_COPY = {
  meaningRingsSectionTitle: "Опоры недели",
  guidePanelIntroTitle: "Сначала — суть дня",
  guidePanelIntroBody:
    "Ниже главное сообщение дня. Детали про шаги и карту открой, когда захочешь углубиться — без перегруза одним экраном.",
  guideStepTwoDisclosureLabel: "Действия и карта дня",
  guideStepThreeDisclosureLabel: "Ритм, профиль и сферы",
  morningPanelIntroTitle: "Утро — намерение",
  morningPanelIntroBody:
    "Спокойный вход в день. Карту, число и разбор открой ниже, когда тебе будет удобно.",
  morningStepTwoDisclosureLabel: "Карта, число и ядро дня",
  dayPanelIntroTitle: "День — шаг и сигнал",
  dayPanelIntroBody: "Сначала суть и что сделать. Подробности — в раскрытии ниже.",
  dayStepTwoDisclosureLabel: "Дополнительные блоки и вопросы дня",
  eveningPanelIntroTitle: "Вечер — закрытие",
  eveningPanelIntroBody:
    "Коротко зафиксируй день. Дополнительные вопросы — по раскрытию, когда захочешь.",
  eveningStepTwoDisclosureLabel: "Дополнительные вечерние вопросы",
  lifeSpheresSectionTitle: "Сферы жизни сегодня",
  lifeSpheresSubtitle:
    "По четырём темам видно, где сегодня легче продвинуться, где лучше не давить и где стоит просто не мешать себе.",
  nextStepWhyFallback:
    "Мягко перевести день в первый осознанный шаг — без давления и без лишних задач.",
  guideHeroEyebrow: "Суть дня",
  loadingGuideHero: "Собираю разбор дня…",
  loadingMorningNarrative: "Собираю подсказки на день…",
  loadingDayNarrative: "Собираю блок про день…",
  loadingEveningNarrative: "Собираю вечерний итог…",
  narrativeFallbackMorning:
    "Утренний текст подскажет, куда вложить внимание сегодня — не только настроение.",
  narrativeFallbackEvening:
    "Короткий вечерний итог помогает честнее закрыть день и лучше стартовать завтра.",
  guideEnergyLineFallback: "Строка про энергию станет яснее после вечерней отметки.",
  profileTileTitle: "Базовый темп",
  profileTileCaption: "Солнце, Луна и асцендент — ориентир, как ты обычно реагируешь и восстанавливаешься.",
  weekRhythmCalendarSubtitle:
    "Календарь показывает день внутри недели и где уже стоят отметки утра, дня и вечера.",
  weekRhythmSummaryTail: "Чем стабильнее отметки, тем полезнее ориентиры на ближайшие дни.",

  // --- iOS `TodayView` (герой, панели, таро, fusion) — паритет `TodayShellCopy` ---
  shellToolbarOpenProfileSummary: "Открыть Profile Summary",
  shellToolbarRefresh: "Обновить",
  shellNativeStepGuideTitle: "Today",
  shellNativeStepMorningTitle: "Фокус",
  shellNativeStepDayTitle: "Состояние",
  shellNativeStepEveningTitle: "Рефлексия",
  shellNativeStepGuideSubtitle: "Вход в день",
  shellNativeStepMorningSubtitle: "Намерение",
  shellNativeStepDaySubtitle: "Сигналы",
  shellNativeStepEveningSubtitle: "Закрытие",
  shellHeroDoNotEnterTitle: "Не входить",
  shellHeroFirstMoveFallback: "Собери день вокруг одного устойчивого движения",
  shellHeroAvoidFallback: "Не усиливай лишний шум и второстепенные темы",
  shellHeroSignalDayTitle: "Сигнал дня",
  shellHeroOverviewCollapse: "Свернуть обзор",
  shellHeroOverviewExpand: "Обзор дня: уровень, метрики и опоры",
  shellHeroOverviewA11yCollapse: "Свернуть обзор дня",
  shellHeroOverviewA11yExpand: "Показать полный обзор дня с уровнем и метриками",
  shellHeroChipSun: "Солнце",
  shellHeroChipMoon: "Луна",
  shellHeroChipAscendant: "Асцендент",
  shellHeroHeadlineFallback: "Сначала собери себя, потом собери день",
  shellHeroSubheadlineFallback:
    "Главный экран должен не перегружать, а быстро вводить тебя в правильный ритм дня.",
  shellYourLevelLabel: "Твой уровень",
  shellTarotCardPreparing: "Карта дня готовится",
  shellGuideDayAxisTitle: "Ось дня",
  shellGuideDayAxisFallback: "Собирай день вокруг одной оси, а не вокруг случайных импульсов.",
  shellGuideSupportsTitle: "Поддержит",
  shellGuideSupportsFallback: "Выбирать одно движение, которое действительно держит тебя.",
  shellNumerologyGathering: "Число дня ещё собирается",
  shellNextStepSectionTitle: "Следующий шаг",
  shellNextStepDoTitle: "Что сделать сейчас",
  shellNextStepWhyTitle: "Почему это важно",
  shellNextStepActionFallback: "Открой утро и зафиксируй одно намерение.",
  shellFitSectionTitle: "Как этот день ложится на тебя",
  shellFitStrongerAxisLabel: "Сильнее",
  shellFitBestModeTitle: "Лучший режим",
  shellFitBestModeFallback: "День лучше раскрывать из ровного темпа, а не из рывка.",
  shellFitFragileAxisTitle: "Хрупкая ось",
  shellFitLeadFallback:
    "Слой guide должен объяснять день через твой собственный ритм, а не как универсальный прогноз.",
  shellFitWeakAxisRiskFallback: "Пока данных мало. Отметь утро и один шаг днём, чтобы риск уточнился.",
  shellNarrativeHeroEnergyTitle: "Энергия",
  shellNarrativeHeroRiskTitle: "Риск",
  shellNarrativeHeroRiskFallback: "Главный риск дня станет яснее после первых сигналов.",
  shellNarrativeHeadlineFallback: "Собери день вокруг одной правильной оси",
  shellNarrativeSublineFallback: "Сначала вход в день, потом глубина. Не наоборот.",
  shellExecutionFocusHeading: "На чем держать фокус сегодня",
  shellExecutionAvoidHeading: "Чего избегать сегодня",
  shellExecutionDoFallback1: "Доведи до конца то, что уже в работе.",
  shellExecutionDoFallback2: "Упрости коммуникацию: коротко и по делу.",
  shellExecutionDoFallback3: "Сдвинь вперёд одно важное дело.",
  shellExecutionAvoidFallback1: "Не разжигай конфликты.",
  shellExecutionAvoidFallback2: "Не перегружай себя обязательствами.",
  shellTarotResonanceTitle: "Отклик",
  shellTarotResonancePartial: "Частично",
  shellTarotResonanceSaved: "Сохранено",
  shellListDoTitle: "Что сделать",
  shellListAvoidTitle: "Чего избегать",
  shellListDoFallback: "Собери день вокруг одного полезного действия.",
  shellListAvoidFallback: "Не усиливай вторичный шум и лишнее напряжение.",
  shellDayProgressHeading: "Прогресс дня",
  shellDayProgressStepDone: "Готово",
  shellDayProgressStepNext: "Следующий шаг",
  shellProgressPhaseTodayComplete: "Today",
  shellSphereForecastCollapse: "Свернуть прогноз сферы",
  shellSphereForecastExpand: "Открыть прогноз сферы",
  shellSphereLoveTitle: "Любовь",
  shellSphereLoveFallback: "Здесь появится короткий прогноз по отношениям на сегодня.",
  shellSphereMoneyTitle: "Деньги",
  shellSphereMoneyFallback: "Сюда подтягивается практическая линия решений и ресурса.",
  shellSphereWorkTitle: "Работа",
  shellSphereWorkFallback: "Сюда должен прийти рабочий фокус дня.",
  shellSphereFamilyTitle: "Семья",
  shellSphereFamilyFallback: "Этот блок показывает, как сегодня может чувствоваться общение дома.",
  shellMorningDayModeTitle: "Режим дня",
  shellMorningDayModeFallback: "Ровный собранный ритм",
  shellMorningDayModeCaption: "Тон, в котором день лучше раскрывается",
  shellMorningNarrativeHeadlineFallback: "Подсказки на день",
  shellProfileBuilding: "Профиль ещё собирается",
  shellEveningClosingToneTitle: "Тон закрытия",
  shellEveningNarrativeHeadlineFallback: "Вечер",
  shellEveningMorningLinkTitle: "Связь с утром",
  shellMorningCoreTitle: "Ядро дня",
  shellTarotCardDayTitle: "Карта дня",
  shellCoreGathering: "Собирается",
  shellTarotCardCaption: "Символ дня",
  shellNumerologyDayTitle: "Число дня",
  shellNumerologyCaption: "Числовой акцент дня",
  shellForecastShortTitle: "Коротко про день",
  shellWhatSupportsDayTitle: "Что поддержит день",
  shellWhatSupportsFallback: "Один ясный первый шаг.",
  shellWhatNotAmplifyTitle: "Что не усиливать",
  shellWhatNotAmplifyFallback: "Не расширяй шум и вторичные задачи.",
  shellTarotDaySectionTitle: "Таро дня",
  shellTarotAgainCta: "Ещё раз",
  shellTarotA11yClosedCard: "Закрытая карта",
  shellTarotPickCardHint: "Выбери карту",
  shellEnergyStateSectionTitle: "Энергия и состояние",
  shellEnergySignatureEmpty:
    "Покажем красивую карту энергии, как только появится первый живой сигнал дня.",
  shellFusionOrbEnergy: "Энергия",
  shellFusionOrbBalance: "Баланс",
  shellFusionOrbFocus: "Фокус",
  shellWeekRhythmTitle: "Ритм недели",
  shellWeekCalendarFootnoteActive:
    "Точки под датой показывают, какие части дня уже прожиты и зафиксированы.",
  shellWeekCalendarFootnoteInactive:
    "Когда ты начнешь отмечать утро, день и вечер, картина недели станет заметно яснее.",
  shellTrendInsightTitle: "Что уже видно по твоим отметкам",
  shellTrendLineTrend: "Тренд",
  shellTrendLineRisk: "Риск",
  shellTrendLineCorrelation: "Корреляция",
  shellWorkingLayerDayStepTitle: "Шаг дня",
  shellWorkingLayerOpeningFallback: "Выбери один рабочий фокус и одно ограничение на день.",
  shellNextActionCardTitle: "Следующий шаг",
  shellNextActionFallback: "Зафиксируй состояние и одно следующее действие.",
  shellCriticalLimitTitle: "Критический лимит",
  shellCriticalLimitFallback: "Не пытайся раскрыть весь день за один раз.",
  shellActionPlanTitle: "План дня",
  shellDayDetailsHeading: "Вопросы и рабочие блоки",
  shellQuestionOfDayCardTitle: "Вопрос дня",
  shellPersonalInsightTitleFallback: "Личный инсайт",
  shellWeeklyFocusTitle: "Недельный фокус",
  shellDisciplineTitle: "Дисциплина",
  shellNudgeHintTitle: "Подсказка",
  shellEveningDetailsHeading: "Вечерние вопросы",
  shellEveningMainQuestionTitle: "Основной вопрос",
  shellEveningBeforeCloseTitle: "Перед закрытием",
  shellEveningWhatWeCaptureTitle: "Что фиксируем",
  shellDayEnergyRibbonTitle: "Энергия дня",
  shellDayEnergyRibbonSubtitle: "Три шкалы: энергия, баланс и фокус.",
  shellRecentJournalTitle: "Последние записи",
  shellYourFocusTitle: "Твой фокус",
  shellMarkProgressCta: "Отметить прогресс",
  shellAddGoalHint: "Добавь цель, чтобы отметить по ней шаг сегодня.",
  shellGoalHintStrongDay: "Сегодня удачный день, чтобы сдвинуться вперёд.",
  shellGoalHintCarefulDay: "Не лучший день для рискованных шагов. Держи шаг маленьким и ясным.",
  shellLoadStateIdle: "Ожидание",
  shellLoadStateLoading: "Собираем день",
  shellLoadStateDone: "Готово",
  shellFallbackPanelTitle: "Экран дня загружается",
  shellFallbackPanelLoadingBody: "Загружаю день и собираю все блоки.",
  shellFallbackPanelStaleHint: "Данные еще загружаются. Нажми «Обновить экран дня».",
  shellFallbackRefreshScreenCta: "Обновить экран дня",
} as const;

/** Развёрнутый заголовок уровня в орбе жизни (`TodayLifeLevelOrb`, iOS). */
export function formatShellYourLevelDetail(tierTitle: string): string {
  return `${TODAY_SHELL_COPY.shellYourLevelLabel}: ${tierTitle}`;
}

/** Компактная строка прогресса дня с буллетом (`TodayGuideProgressSection`, iOS). */
export function formatShellDayProgressBullets(percent: number, completed: number, total: number): string {
  return `${percent}% • ${completed} ${RITUAL_COPY.guideDayProgressOutOf} ${total} шагов`;
}

/** Строка «Число N» для числа дня. */
export function formatShellNumerologyValue(value: string | number): string {
  return `Число ${value}`;
}

/** Карточка «связь с утром» с кавычками-ёлочками. */
export function formatShellMorningIntentionRecall(intention: string): string {
  return `Утром ты задал: “${intention}”`;
}

/** Склейка хрупкой оси и базового текста риска. */
export function formatShellWeakAxisLine(weakestAxisTitle: string, base: string): string {
  return `${weakestAxisTitle} сейчас требует бережности. ${base}`;
}

/** Подпись открытой карты под колодой. */
export function formatShellTarotDayLine(cardName: string): string {
  return `${TODAY_SHELL_COPY.shellTarotCardDayTitle}: ${cardName}`;
}

/** VoiceOver: открытая карта с именем. */
export function formatShellTarotA11yOpenCard(cardName: string): string {
  return `Открытая карта ${cardName}`;
}

/** Честный шаг — чипы под картой дня (сигнал для персонализации). */
export const RITUAL_CARD_HONEST_STEP_CHIPS: { id: string; label: string }[] = [
  { id: "talk", label: "разговор" },
  { id: "work", label: "работа" },
  { id: "money", label: "деньги" },
  { id: "relations", label: "отношения" },
  { id: "body", label: "тело / энергия" },
  { id: "unknown", label: "пока не знаю" },
];

/** Число дня — какой ритм нужен (сигнал для персонализации). */
export const RITUAL_NUMBER_RHYTHM_CHIPS: { id: string; label: string }[] = [
  { id: "gather", label: "собраться" },
  { id: "decide", label: "решиться" },
  { id: "rest", label: "отдохнуть" },
  { id: "talk", label: "поговорить" },
  { id: "steady", label: "не сорваться" },
];

/** Домен главного шага (навигация в Flow / событие). */
export const RITUAL_MAIN_STEP_DOMAIN_CHIPS: { id: string; label: string }[] = [
  { id: "work", label: "работа" },
  { id: "money", label: "деньги" },
  { id: "relations", label: "отношения" },
  { id: "body", label: "тело" },
  { id: "other", label: "другое" },
];

/** Порядок и подписи для `activity_context.guide_meaning_completions_today` (DE-7, сервер). */
export const GUIDE_MEANING_COMPLETION_DISPLAY: { key: string; shortLabel: string }[] = [
  { key: "habit_completed", shortLabel: "привычка" },
  { key: "practice_completed", shortLabel: "практика" },
  { key: "focus_completed", shortLabel: "фокус" },
  { key: "affirmation_done", shortLabel: "аффирмация" },
  { key: "ascetic_step_done", shortLabel: "аскеза" },
];

export function formatGuideMeaningCompletionsLine(raw: Record<string, unknown> | null | undefined): string | null {
  if (!raw || typeof raw !== "object") return null;
  const parts: string[] = [];
  for (const { key, shortLabel } of GUIDE_MEANING_COMPLETION_DISPLAY) {
    const n = Number(raw[key]);
    if (Number.isFinite(n) && n > 0) {
      parts.push(n === 1 ? shortLabel : `${shortLabel} ×${n}`);
    }
  }
  return parts.length ? parts.join(" · ") : null;
}

/** Есть объект `guide_meaning_completions_today` в ответе fusion (в т.ч. все нули). */
export function hasGuideMeaningCompletionsPayload(raw: Record<string, unknown> | null | undefined): boolean {
  return raw != null && typeof raw === "object";
}

export type GuideMeaningCompletionChip = { key: string; label: string; count: number };

/** Чипы для UI: только ненулевые счётчики, канонический порядок. */
function clampFusionAxisScore(n: number): number {
  if (!Number.isFinite(n)) return 50;
  return Math.max(0, Math.min(100, Math.round(n)));
}

function fusionScoreDeltaTrustworthy(h: Record<string, unknown>): boolean {
  if (h.fusion_score_delta_trustworthy === false) return false;
  return true;
}

function trailing7dSummaryTrustworthy(h: Record<string, unknown>): boolean {
  if (h.trailing_7d_summary_trustworthy === false) return false;
  return true;
}

/** O7: `false` — не показывать нижнюю подсказку полоски (основной текст уже самодостаточен). */
export function isFusionDayHistoryDeltaUntrustworthy(raw: unknown): boolean {
  if (!raw || typeof raw !== "object") return false;
  return (raw as Record<string, unknown>).fusion_score_delta_trustworthy === false;
}

/** DE-9: одна строка из `GET /tracking/fusion` → `day_history` (`day_history_v0`). */
export function formatFusionDayHistoryRu(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const fs = (y as Record<string, unknown>).fusion_scores;
  if (!fs || typeof fs !== "object") return null;
  const scores = fs as Record<string, unknown>;
  const ye = clampFusionAxisScore(Number(scores.energy));
  const ybal = clampFusionAxisScore(Number(scores.emotional_balance));
  const yf = clampFusionAxisScore(Number(scores.focus));
  const deltaRaw = h.fusion_score_delta_vs_yesterday;
  if (!deltaRaw || typeof deltaRaw !== "object") return null;
  const d = deltaRaw as Record<string, unknown>;
  const dE = Math.round(Number(d.energy));
  const dBal = Math.round(Number(d.emotional_balance));
  const dF = Math.round(Number(d.focus));
  const fmt = (v: number) => (v > 0 ? `+${v}` : `${v}`);
  const head = `Вчера: энергия ${ye}, баланс ${ybal}, фокус ${yf}`;
  if (!fusionScoreDeltaTrustworthy(h)) {
    return RITUAL_COPY.dayHistoryDeltaUntrustworthyTail;
  }
  const allZero = dE === 0 && dBal === 0 && dF === 0;
  if (allZero) {
    return `${head}. ${RITUAL_COPY.dayHistoryDeltaAllZeroTail}`;
  }
  return `${head} · к сегодня: энергия ${fmt(dE)}, баланс ${fmt(dBal)}, фокус ${fmt(dF)}`;
}

/** EN line for `day_history` strip when UI locale is English (DE-9 v1.3). */
export function formatFusionDayHistoryEn(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const fs = (y as Record<string, unknown>).fusion_scores;
  if (!fs || typeof fs !== "object") return null;
  const scores = fs as Record<string, unknown>;
  const ye = clampFusionAxisScore(Number(scores.energy));
  const ybal = clampFusionAxisScore(Number(scores.emotional_balance));
  const yf = clampFusionAxisScore(Number(scores.focus));
  const deltaRaw = h.fusion_score_delta_vs_yesterday;
  if (!deltaRaw || typeof deltaRaw !== "object") return null;
  const d = deltaRaw as Record<string, unknown>;
  const dE = Math.round(Number(d.energy));
  const dBal = Math.round(Number(d.emotional_balance));
  const dF = Math.round(Number(d.focus));
  const fmt = (v: number) => (v > 0 ? `+${v}` : `${v}`);
  const head = `Yesterday: energy ${ye}, balance ${ybal}, focus ${yf}`;
  if (!fusionScoreDeltaTrustworthy(h)) {
    return RITUAL_COPY.dayHistoryDeltaUntrustworthyTailEn;
  }
  const allZero = dE === 0 && dBal === 0 && dF === 0;
  if (allZero) {
    return `${head}. ${RITUAL_COPY.dayHistoryDeltaAllZeroTailEn}`;
  }
  return `${head} · toward today: energy ${fmt(dE)}, balance ${fmt(dBal)}, focus ${fmt(dF)}`;
}

/** DE-9 v1.2: одна строка из `trailing_7d_summary` в `day_history_v0`. */
export function formatFusionDayHistoryWeekSummaryRu(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  if (!trailing7dSummaryTrustworthy(h)) return null;
  const sum = h.trailing_7d_summary;
  if (!sum || typeof sum !== "object") return null;
  const s = sum as Record<string, unknown>;
  const axis = (key: string): string | null => {
    const block = s[key];
    if (!block || typeof block !== "object") return null;
    const b = block as Record<string, unknown>;
    const avg = Number(b.avg);
    const mn = Math.round(Number(b.min));
    const mx = Math.round(Number(b.max));
    if (!Number.isFinite(avg) || !Number.isFinite(mn) || !Number.isFinite(mx)) return null;
    return `ср. ${Math.round(avg)} (${mn}–${mx})`;
  };
  const e = axis("energy");
  const bal = axis("emotional_balance");
  const f = axis("focus");
  if (!e || !bal || !f) return null;
  return `7 дней до вчера: энергия ${e}, баланс ${bal}, фокус ${f}`;
}

function pluralStepsRu(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return `${n} шаг`;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return `${n} шага`;
  return `${n} шагов`;
}

/** DE-9 v1.4: строка про смысловые шаги вчера из `meaning_day_signals` / `day_flow`. */
export function formatFusionDayHistoryMeaningLineRu(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const yRec = y as Record<string, unknown>;
  if (yRec.meaning_active !== true) return null;
  const completions = Number(yRec.meaning_completions_total) || 0;
  const dayFlow = yRec.day_flow;
  const flowRec = dayFlow && typeof dayFlow === "object" ? (dayFlow as Record<string, unknown>) : null;
  const signals = yRec.meaning_day_signals;
  const sigRec = signals && typeof signals === "object" ? (signals as Record<string, unknown>) : null;
  const evening =
    Boolean(flowRec?.evening_completed) || Number(sigRec?.evening_reflection_submitted || 0) > 0;
  const spheres = Number(sigRec?.sphere_opened || 0);
  const parts: string[] = [];
  if (completions > 0) parts.push(`${pluralStepsRu(completions)} в Flow`);
  if (evening) parts.push("вечер закрыт");
  if (spheres > 0) {
    const sphereWord = spheres === 1 ? "сфера" : spheres < 5 ? "сферы" : "сфер";
    parts.push(`открыт${spheres === 1 ? "а" : "ы"} ${spheres} ${sphereWord}`);
  }
  if (parts.length === 0 && Boolean(flowRec?.day_completed)) parts.push("день отмечен");
  if (parts.length === 0) return null;
  return `Вчера: ${parts.join(", ")}.`;
}

/** EN counterpart for DE-9 v1.4 meaning line. */
export function formatFusionDayHistoryMeaningLineEn(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const yRec = y as Record<string, unknown>;
  if (yRec.meaning_active !== true) return null;
  const completions = Number(yRec.meaning_completions_total) || 0;
  const dayFlow = yRec.day_flow;
  const flowRec = dayFlow && typeof dayFlow === "object" ? (dayFlow as Record<string, unknown>) : null;
  const signals = yRec.meaning_day_signals;
  const sigRec = signals && typeof signals === "object" ? (signals as Record<string, unknown>) : null;
  const evening =
    Boolean(flowRec?.evening_completed) || Number(sigRec?.evening_reflection_submitted || 0) > 0;
  const spheres = Number(sigRec?.sphere_opened || 0);
  const parts: string[] = [];
  if (completions > 0) {
    parts.push(`${completions} Flow step${completions === 1 ? "" : "s"}`);
  }
  if (evening) parts.push("evening closed");
  if (spheres > 0) parts.push(`${spheres} sphere${spheres === 1 ? "" : "s"} opened`);
  if (parts.length === 0 && Boolean(flowRec?.day_completed)) parts.push("day marked complete");
  if (parts.length === 0) return null;
  return `Yesterday: ${parts.join(", ")}.`;
}

/** DE-9 v1.5: одна строка из `reflection_excerpt` (вечер / дневник). */
export function formatFusionDayHistoryReflectionLineRu(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const ex = (y as Record<string, unknown>).reflection_excerpt;
  if (!ex || typeof ex !== "object") return null;
  const rec = ex as Record<string, unknown>;
  const er = typeof rec.evening_reflection === "string" ? rec.evening_reflection.trim() : "";
  if (er.length >= 8) return `Вчера вечером: «${er}»`;
  const obs = rec.evening_observations;
  if (obs && typeof obs === "object") {
    const noticed = String((obs as Record<string, unknown>).noticed || "").trim();
    if (noticed.length >= 8) return `Вчера заметил(а): «${noticed}»`;
  }
  const mi = typeof rec.morning_intention === "string" ? rec.morning_intention.trim() : "";
  if (mi.length >= 8) return `Вчера утром: «${mi}»`;
  return null;
}

export function formatFusionDayHistoryReflectionLineEn(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  const h = raw as Record<string, unknown>;
  if (h.contract_version !== "day_history_v0") return null;
  const y = h.yesterday;
  if (!y || typeof y !== "object") return null;
  const ex = (y as Record<string, unknown>).reflection_excerpt;
  if (!ex || typeof ex !== "object") return null;
  const rec = ex as Record<string, unknown>;
  const er = typeof rec.evening_reflection === "string" ? rec.evening_reflection.trim() : "";
  if (er.length >= 8) return `Yesterday evening: "${er}"`;
  const obs = rec.evening_observations;
  if (obs && typeof obs === "object") {
    const noticed = String((obs as Record<string, unknown>).noticed || "").trim();
    if (noticed.length >= 8) return `Yesterday you noticed: "${noticed}"`;
  }
  const mi = typeof rec.morning_intention === "string" ? rec.morning_intention.trim() : "";
  if (mi.length >= 8) return `Yesterday morning: "${mi}"`;
  return null;
}

export function guideMeaningCompletionChipItems(
  raw: Record<string, unknown> | null | undefined,
): GuideMeaningCompletionChip[] {
  if (!raw || typeof raw !== "object") return [];
  const out: GuideMeaningCompletionChip[] = [];
  for (const { key, shortLabel } of GUIDE_MEANING_COMPLETION_DISPLAY) {
    const n = Number(raw[key]);
    if (Number.isFinite(n) && n > 0) {
      const label = shortLabel.length > 0 ? shortLabel.charAt(0).toUpperCase() + shortLabel.slice(1) : shortLabel;
      out.push({ key, label, count: Math.max(0, Math.round(n)) });
    }
  }
  return out;
}

/** Упрощённый трекинг дня (паритет с продуктовой спецификацией v5). */
export const RITUAL_ESSENTIALS = [
  {
    id: "water",
    label: "Вода",
    explanation: "Базовая норма за день — меньше путаешь жажду с раздражением.",
  },
  {
    id: "movement",
    label: "Движение",
    explanation: "5–10 минут пройтись или размять спину.",
  },
  {
    id: "pause",
    label: "Пауза",
    explanation: "Одна остановка без экрана — чтобы день не уехал на автопилоте.",
  },
  {
    id: "focus20",
    label: "Фокус 20 минут",
    explanation: "Один слот без переключений на главное дело.",
  },
] as const;

/** Быстрые чипы блока «Собрать день» — паритет iOS `TodayRitualBuildDayQuickChips` / `buildDayQuickChips` в `TodayRitualFlowView`. */
export const RITUAL_BUILD_DAY_QUICK_CHIPS: ReadonlyArray<{
  id: string;
  label: string;
  entityKind: TrackerEntityKind;
}> = [
  { id: "chip_habit_discipline", label: "дисциплина", entityKind: "habit" },
  { id: "chip_goal_money", label: "деньги", entityKind: "goal" },
  { id: "chip_goal_closeness", label: "близость", entityKind: "goal" },
  { id: "chip_ascetic_emotions", label: "эмоции", entityKind: "ascetic" },
];

export type RitualEssentialItem = { id: string; label: string; explanation: string };

/** Какой чеклист «базы дня» показать в зависимости от настроения. */
/** Три тега под «твоё число дня» — визуальный паритет с макетом, если в API нет отдельных ключевых слов. */
/** Три коротких тега под картой — из lead RU (как iOS `anchorTarotTags`). */
export function anchorTarotTagsFromLead(leadRu: string): string[] {
  return leadRu
    .split(/[,;.]/)
    .map((s) => s.trim())
    .filter((s) => s.length > 2 && s.length < 38)
    .slice(0, 3);
}

export function numberDayTagTriad(numerologyValue: string): string[] {
  const d = String(numerologyValue).replace(/\D/g, "").slice(-1) || "1";
  const pool: Record<string, [string, string, string]> = {
    "1": ["Старт", "Ясность", "Инициатива"],
    "2": ["Партнёрство", "Такт", "Баланс"],
    "3": ["Общение", "Идеи", "Лёгкость"],
    "4": ["Опора", "Порядок", "Шаг"],
    "5": ["Смена", "Импульс", "Гибкость"],
    "6": ["Забота", "Близость", "Гармония"],
    "7": ["Тишина", "Анализ", "Глубина"],
    "8": ["Ресурс", "Результат", "Границы"],
    "9": ["Завершение", "Смысл", "Отпускание"],
  };
  return [...(pool[d] ?? pool["1"]!)];
}

export function essentialsForMood(_mood: string | null): readonly RitualEssentialItem[] {
  return RITUAL_ESSENTIALS;
}

/** O6: настроения ритуала с низким ресурсом (паритет бэкенда `_LOW_ENERGY_RITUAL_MOODS`). */
const RITUAL_LOW_ENERGY_MOOD_IDS = new Set<string>(["tired", "heavy", "quiet_wish"]);

export function isLowEnergyRitualMood(mood: string | null | undefined): boolean {
  if (!mood) return false;
  return RITUAL_LOW_ENERGY_MOOD_IDS.has(String(mood).trim().toLowerCase());
}

/** Подписи к kind из API `why_astrological_layers` */
export const WHY_ASTRO_KIND_LABELS: Record<string, string> = {
  natal_angle: "Угол карты",
  natal_luminary: "Светила",
  natal_personal: "Личные планеты",
  natal_aspect: "Аспект",
  natal_sun_sign: "Солнечный знак",
  daily_spine: "Стержень дня",
  lunar_context: "Луна и фаза",
  profile_prism: "Профиль",
  rhythm_placeholder: "Ритм",
  ritual_tarot: "Карта ритуала",
  ritual_number: "Число ритуала",
  ritual_mood: "Состояние",
  ritual_day_events: "События дня",
};

export type GuidanceLead = "love" | "work" | "neutral";

export function inferGuidanceLead(summaryTitle: string, possible: string[], avoid: string[], support: string[]): GuidanceLead {
  const blob = [summaryTitle, ...possible, ...avoid, ...support].join(" ").toLowerCase();
  if (/люб|отношен|близ|партн|сердеч|интим|романт/.test(blob)) return "love";
  if (/работ|деньг|карьер|проект|офис|клиент|сделк/.test(blob)) return "work";
  return "neutral";
}

export function guidanceBodyForLead(lead: GuidanceLead): string {
  switch (lead) {
    case "love":
      return "Сегодня тема близости звучит громче. Зайди в Проводник со своим вопросом — так проще получить ясный шаг, а не общие слова.";
    case "work":
      return RITUAL_COPY.guidanceWorkFollowup;
    default:
      return RITUAL_COPY.guidanceNeutralFollowup;
  }
}

export function suggestedQuestionForLead(lead: GuidanceLead): string {
  switch (lead) {
    case "love":
      return RITUAL_COPY.suggestedQuestionLove;
    case "work":
      return RITUAL_COPY.suggestedQuestionWork;
    default:
      return RITUAL_COPY.suggestedQuestionNeutral;
  }
}

export function ritualGoalSuggestions(lead: GuidanceLead): readonly { title: string; reason: string }[] {
  switch (lead) {
    case "love":
      return [
        {
          title: "Один честный разговор",
          reason: "Если день про отношения — не распахивать всё сразу, а прояснить одну вещь, которая болит.",
        },
        {
          title: "Пауза перед ответом",
          reason: "Так проще не ответить из обиды или тревоги — и услышать себя.",
        },
      ];
    case "work":
      return [
        {
          title: "Один спокойный рабочий блок",
          reason:
            "Внимание не расползается между задачами — к вечеру легче заметить, что главное для тебя сдвинулось.",
        },
        {
          title: "Пауза перед импульсной тратой",
          reason: "Если фон про деньги, это часто даёт опору быстрее, чем новые списки планов.",
        },
      ];
    default:
      return [
        {
          title: "Утренний ритм",
          reason: "Вода, чуть движения и один понятный старт — без давления «успеть всё».",
        },
        {
          title: "Один завершённый шаг",
          reason: "Конкретика вместо туманного «надо» — так проще почувствовать опору: я справляюсь.",
        },
      ];
  }
}

/** Темы для микро-вопроса после check-in (обучение персонализации). */
export const RITUAL_HEAD_TOPIC_CHIPS: { id: string; label: string }[] = [
  { id: "work", label: "работа" },
  { id: "money", label: "деньги" },
  { id: "relations", label: "отношения" },
  { id: "body", label: "тело / энергия" },
  { id: "family", label: "семья" },
  { id: "decision", label: "решение, которое надо принять" },
  { id: "none", label: "ничего конкретного" },
];

/** Шесть состояний как на макете Today (2×3). */
export const RITUAL_MOOD_GRID: { id: string; label: string; icon: string }[] = [
  { id: "calm", label: "Спокойно", icon: "♥" },
  { id: "anxious", label: "Тревожно", icon: "☁" },
  { id: "tired", label: "Устало", icon: "🔋" },
  { id: "driven", label: "В драйве", icon: "🔥" },
  { id: "irritated", label: "Раздражённо", icon: "⚡" },
  { id: "other", label: "Другое", icon: "⋯" },
];

/** Все id настроения (сетка + старые сохранённые значения). */
export const RITUAL_MOOD_LABELS: { id: string; label: string }[] = [
  { id: "calm", label: "спокойно" },
  { id: "anxious", label: "тревожно" },
  { id: "tired", label: "устало" },
  { id: "driven", label: "в драйве" },
  { id: "irritated", label: "раздражённо" },
  { id: "other", label: "другое" },
  { id: "motivated", label: "в драйве" },
  { id: "confused", label: "неясно" },
  { id: "quiet_wish", label: "хочется тишины" },
  { id: "move_wish", label: "хочется движения" },
  { id: "heavy", label: "тяжело" },
  { id: "hopeful", label: "с надеждой" },
  { id: "distant", label: "на дистанции" },
];

/** Темп дня по шкале энергии ритуала (не предсказание, ориентир для карточки «Коротко о дне»). */
export function tempoLabelForEnergyScore(score: number): string {
  const s = Math.max(0, Math.min(100, Math.round(Number.isFinite(score) ? score : 0)));
  if (s < 38) return "тихий";
  if (s < 58) return "спокойный";
  if (s < 78) return "ровный";
  return "подвижный";
}

/** Словесный уровень «опоры в ритме» по шкале 0–100 (те же пороги, что в ритуале и на карточках сфер). */
export function rhythmTierLabelForScore(score: number): string {
  const s = Math.max(0, Math.min(100, Math.round(Number.isFinite(score) ? score : 0)));
  if (s < 38) return "Мало недавних шагов в Flow — это нормально; одна отметка уже меняет картину.";
  if (s < 58) return "Спокойный уровень: немного опорных шагов за последние дни.";
  if (s < 78) return "Хорошая опора — твои шаги заметны.";
  return "Очень крепкая опора";
}

function narrativeLookup(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = (payload as Record<string, unknown>)[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function clipWhy(s: string, max: number): string {
  const t = s.trim();
  if (t.length <= max) return t;
  return `${t.slice(0, max - 1)}…`;
}

/** Убираем префикс «Фаза:» — подпись уже есть в UI («Луна и фон дня»). */
export function normalizeLunarPhaseLabel(whyMoon: string | null | undefined): string | null {
  const raw = whyMoon?.trim();
  if (!raw) return null;
  const stripped = raw.replace(/^фаза\s*:\s*/i, "").trim();
  return stripped || raw;
}

function digitalRootPositive(n: number): number {
  let x = Math.abs(Math.round(n));
  if (!Number.isFinite(x) || x === 0) return 1;
  while (x > 9) {
    x = String(x)
      .split("")
      .reduce((acc, ch) => acc + (parseInt(ch, 10) || 0), 0);
  }
  return x;
}

/**
 * Ключ для копирайта ритма числа дня: 1–9 по корню, либо мастер 11/22/33 если так в значении дня.
 * Паритет с iOS `TodayRitualCopy.resolvePersonalDayRhythmKey`.
 */
export function resolvePersonalDayRhythmKey(
  reduced: number | null | undefined,
  displayValue: string,
): number {
  const digits = String(displayValue).replace(/\D/g, "");
  const raw = digits ? parseInt(digits, 10) : NaN;
  if (raw === 11 || raw === 22 || raw === 33) return raw;
  if (typeof reduced === "number" && Number.isFinite(reduced)) {
    const r = Math.round(reduced);
    if (r >= 1 && r <= 9) return r;
  }
  if (Number.isFinite(raw) && raw > 0) return digitalRootPositive(raw);
  return 1;
}

const PERSONAL_DAY_RHYTHM_FULL: Record<number, string> = {
  1: "Число дня с корнем 1 — ритм старта: один ясный первый шаг и инициатива, а не ожидание внешнего «разрешения начать».",
  2: "Корень 2 — ритм согласования: выдержанный темп, пауза перед ответом и опора на пару/договорённости, а не резкий рывок.",
  3: "Корень 3 — ритм лёгкости и коротких циклов: формулировать вслух, прояснять, не закапываться в перфекционизм.",
  4: "Корень 4 — ритм шага и опоры: измеримый прогресс, режим и дисциплина малыми порциями.",
  5: "Корень 5 — ритм смены и гибкости: адаптироваться к факту, не цепляясь за первый план любой ценой.",
  6: "Корень 6 — ритм заботы и баланса обязательств: держать одну зону ответственности честно, без перегруза «за всех».",
  7: "Корень 7 — ритм глубины: время на анализ и тишину, чтобы не путать шум с ясностью.",
  8: "Корень 8 — ритм результата и границ: ресурсы, договорённости и ответственность за итог, без лишней суеты.",
  9: "Корень 9 — ритм завершения: подводить смысл, отпускать лишнее, не цепляться за отжившее.",
  11: "Число 11 — ритм тонкого считывания: доверять интуиции, но закреплять инсайт одним простым действием.",
  22: "Число 22 — ритм структуры под масштаб: большой замысел через конкретные кирпичики, без перегруза всем сразу.",
  33: "Число 33 — ритм поддержки и ясности для других: забота, которая не обнуляет твои границы.",
};

const PERSONAL_DAY_RHYTHM_BRIDGE: Record<number, string> = {
  1: "число с корнем 1 просит старта и первого шага без откладывания",
  2: "корень 2 просит ровного темпа и согласования, а не форсированной скорости",
  3: "корень 3 просит лёгких циклов и прояснений вслух",
  4: "корень 4 просит шагов и опоры, а не размытого многозадачия",
  5: "корень 5 просит гибкости и смены плана по факту",
  6: "корень 6 просит честного баланса заботы и границ",
  7: "корень 7 просит паузы на ясность, а не спешных выводов",
  8: "корень 8 просит фокуса на результате и договорённостях",
  9: "корень 9 просит завершать и отпускать лишнее",
  11: "число 11 просит связать интуицию с одним простым действием",
  22: "число 22 просит строить масштаб короткими опорами",
  33: "число 33 просит заботу без самопожертвования",
};

/** Полная строка для блока «Почему так?» (или fallback, если нет объяснения от API). */
export function personalDayRhythmLine(reduced: number | null | undefined, displayValue: string): string {
  const key = resolvePersonalDayRhythmKey(reduced, displayValue);
  return PERSONAL_DAY_RHYTHM_FULL[key] ?? PERSONAL_DAY_RHYTHM_FULL[1]!;
}

/** Короткий хвост для моста «карта + число». */
export function personalDayRhythmBridgeSuffix(reduced: number | null | undefined, displayValue: string): string {
  const key = resolvePersonalDayRhythmKey(reduced, displayValue);
  return PERSONAL_DAY_RHYTHM_BRIDGE[key] ?? PERSONAL_DAY_RHYTHM_BRIDGE[1]!;
}

/** Одна строка луны для сводки: темы · фаза; без второй строки «Фаза луны» с тем же текстом. */
export function formatLunarRitualSummaryLine(
  whyMoon: string | null,
  whyLunar: string | null,
  guidePayload: Record<string, unknown> | null,
  maxLen: number,
): string {
  const phase = normalizeLunarPhaseLabel(whyMoon);
  const themes = whyLunar?.trim() || "";
  let primary = "";
  if (themes && phase) primary = `${themes} · ${phase}`;
  else primary = themes || phase || "";
  if (primary) return clipWhy(primary, maxLen);
  const li = narrativeLookup(guidePayload, "lunar_influence");
  if (li) return clipWhy(li, maxLen);
  const tr = narrativeLookup(guidePayload, "transit_influence");
  if (tr) return clipWhy(tr, maxLen);
  return "—";
}

function normalizeLoose(s: string): string {
  return s
    .toLowerCase()
    .replace(/[·,.:;!?—–-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const WHY_LINE_PREFIXES: RegExp[] = [
  /^напряжение дня сейчас в одном месте:\s*/i,
  /^лучше всего день раскрывается через такой режим:\s*/i,
  /^утренний фокус для дня:\s*/i,
];

/** Варианты строки для сравнения (тело без служебного префикса «Почему так?»). */
export function expansionVariantsForWhyDedup(line: string): string[] {
  const t = line.trim();
  if (!t) return [];
  const out = new Set<string>([t]);
  for (const re of WHY_LINE_PREFIXES) {
    const rest = t.replace(re, "").trim();
    if (rest.length >= 4) out.add(rest);
  }
  return Array.from(out);
}

/**
 * Похожие ли две строки по смыслу (пересечение значимых токенов / вложенность).
 * Используем для среза дублей между сводкой, spine и narrative.
 */
export function textsSemanticallyRedundant(a: string, b: string, minTokenOverlap = 0.56): boolean {
  const na = normalizeLoose(a);
  const nb = normalizeLoose(b);
  if (!na || !nb) return false;
  if (na === nb) return true;
  const minL = Math.min(na.length, nb.length);
  const maxL = Math.max(na.length, nb.length);
  if (minL >= 22 && maxL >= minL) {
    if (na.includes(nb) || nb.includes(na)) return true;
  }
  const ta = na.split(" ").filter((w) => w.length > 2);
  const tb = nb.split(" ").filter((w) => w.length > 2);
  if (ta.length < 3 || tb.length < 3) {
    return minL >= 10 && (na.includes(nb) || nb.includes(na));
  }
  const setB = new Set(tb);
  let inter = 0;
  const setA = new Set(ta);
  setA.forEach((w) => {
    if (setB.has(w)) inter += 1;
  });
  const denom = Math.min(setA.size, setB.size);
  return denom > 0 && inter / denom >= minTokenOverlap;
}

export function lineRedundantWithAny(line: string, pool: string[]): boolean {
  const variants = expansionVariantsForWhyDedup(line);
  for (const p of pool) {
    const pt = p?.trim();
    if (!pt) continue;
    const pvars = expansionVariantsForWhyDedup(pt);
    for (const v of variants) {
      for (const x of pvars) {
        if (textsSemanticallyRedundant(v, x)) return true;
      }
    }
  }
  return false;
}

/** Служебные значения key_focus / morning_focus из бэка — не показывать как «фокус». */
export function isDiscardableMorningFocus(focus: string | null | undefined): boolean {
  const t = (focus ?? "").trim().toLowerCase();
  if (t.length < 2) return true;
  const junk = new Set([
    "general",
    "overall",
    "mixed",
    "none",
    "other",
    "default",
    "общее",
    "прочее",
    "другое",
    "без фокуса",
  ]);
  if (junk.has(t)) return true;
  if (/^[a-z_]{1,20}$/.test(t)) return true;
  return false;
}

export function pickFirstDistinctLine(candidates: string[], avoid: string[]): string {
  for (const c of candidates) {
    const t = c.trim();
    if (!t || t === "—") continue;
    if (!lineRedundantWithAny(t, avoid)) return t;
  }
  const fb = candidates.map((c) => c.trim()).find((x) => x.length > 0);
  return fb ?? "—";
}

/** Сгенерированный `lunar_influence` часто дословно повторяет фазу и темы из астрономии — не дублируем. */
function lunarInfluenceRedundantWithAstronomy(influence: string, moonBlock: string): boolean {
  const a = normalizeLoose(influence);
  const b = normalizeLoose(moonBlock);
  if (a.length < 14 || b.length < 8) return false;
  if (a.includes(b) || b.includes(a)) return true;
  const wordsB = b.split(" ").filter((w) => w.length > 3);
  if (wordsB.length === 0) return false;
  let hit = 0;
  for (const w of wordsB) {
    if (a.includes(w)) hit++;
  }
  return hit / wordsB.length >= 0.72;
}

/** Паритет с iOS `TodayRitualWhyReasonLines` — текст для раскрытия «Почему так?». */
export function buildRitualWhyLinesWeb(input: {
  summaryTitle: string;
  possible: string[];
  guidePayload: Record<string, unknown> | null;
  spine: { main_risk?: string; best_mode?: string } | null | undefined;
  /** Число дня как на бейдже (например 19). */
  numerologyValue: string;
  reducedValue: number | null | undefined;
  /** Если платный слой уже дал развёрнутое объяснение — показываем его вместо шаблона. */
  numerologyDetailLine: string | null | undefined;
  morningFocus: string | null | undefined;
  whyMoon: string | null;
  whyLunar: string | null;
  /** Уже показано выше на карточке — не повторять в «Почему так?». */
  avoidLines: string[];
}): { headline: string | null; lines: string[] } {
  const p = input.guidePayload;
  const rawHeadline = narrativeLookup(p, "headline") ?? narrativeLookup(p, "focus_line");
  const headline =
    rawHeadline && !lineRedundantWithAny(rawHeadline, input.avoidLines) ? rawHeadline : null;
  const lines: string[] = [];
  const phaseLabel = normalizeLunarPhaseLabel(input.whyMoon);
  const themes = input.whyLunar?.trim() || "";
  let moonBlock = "";
  if (themes && phaseLabel) moonBlock = `${themes} · ${phaseLabel}`;
  else moonBlock = themes || phaseLabel || "";

  const lunarInf = narrativeLookup(p, "lunar_influence");
  if (lunarInf && moonBlock && lunarInfluenceRedundantWithAstronomy(lunarInf, moonBlock)) {
    lines.push(clipWhy(moonBlock, 420));
  } else if (lunarInf && moonBlock) {
    lines.push(clipWhy(moonBlock, 420));
    if (!lunarInfluenceRedundantWithAstronomy(lunarInf, moonBlock)) {
      lines.push(clipWhy(lunarInf, 420));
    }
  } else if (lunarInf) {
    lines.push(clipWhy(lunarInf, 420));
  } else if (moonBlock) {
    lines.push(clipWhy(moonBlock, 420));
  }
  const risk = input.spine?.main_risk?.trim();
  if (risk) lines.push(`Напряжение дня сейчас в одном месте: ${risk}`);
  const best = input.spine?.best_mode?.trim();
  if (best) lines.push(`Лучше всего день раскрывается через такой режим: ${best}`);
  const transit = narrativeLookup(p, "transit_influence");
  if (transit) lines.push(clipWhy(transit, 420));
  const detail = input.numerologyDetailLine?.trim();
  if (detail && detail.length >= 36) {
    lines.push(clipWhy(detail, 420));
  } else {
    lines.push(personalDayRhythmLine(input.reducedValue, input.numerologyValue));
  }
  const nextAction = narrativeLookup(p, "next_action");
  if (nextAction) lines.push(nextAction);
  const focus = input.morningFocus?.trim();
  if (focus && !isDiscardableMorningFocus(focus)) lines.push(`Утренний фокус для дня: ${focus}`);
  const nudge = narrativeLookup(p, "nudge_message");
  if (nudge) lines.push(nudge);

  const seen = new Set<string>();
  const out: string[] = [];
  const avoidPool = input.avoidLines.map((x) => x.trim()).filter(Boolean);
  for (const line of lines) {
    const t = line.trim();
    if (!t) continue;
    const norm = t.toLowerCase().replace(/\s+/g, " ");
    if (seen.has(norm)) continue;
    seen.add(norm);
    if (lineRedundantWithAny(t, [...avoidPool, ...out])) continue;
    const sum = input.summaryTitle.trim().toLowerCase().replace(/\s+/g, " ");
    if (sum.length > 10 && (norm === sum || norm.includes(sum.slice(0, 52)))) continue;
    let dupPossible = false;
    for (const pv of input.possible) {
      const pn = pv.trim().toLowerCase().replace(/\s+/g, " ");
      if (pn.length > 12 && (norm === pn || norm.includes(pn) || pn.includes(norm))) {
        dupPossible = true;
        break;
      }
    }
    if (dupPossible) continue;
    out.push(t);
    if (out.length >= 5) break;
  }
  let outHeadline = headline;
  if (outHeadline && lineRedundantWithAny(outHeadline, out)) outHeadline = null;
  return { headline: outHeadline, lines: out };
}

// --- Experience layout chrome (`TodayExperienceLayout` iOS) — RU/EN; зеркало: `TodayExperienceChromeCopy` ---

export type TodayExperienceLocale = "ru" | "en";

/** Демо-окна числа дня (время · цвет · камень · стихия). */
export type TodayExperienceLuckyPreset = readonly [string, string, string, string];

export const TODAY_EXPERIENCE_CHROME_RU = {
  todayEyebrow: "СЕГОДНЯ",
  of100: "из 100",
  rhythmSummary: "сводный ритм дня",
  a11yRhythm: "Сводный ритм дня",
  whyDayFeels: "Почему день ощущается так",
  a11yWhyHint: "Краткий разбор и контекст дня",
  energy: "Энергия",
  balance: "Баланс",
  focus: "Фокус",
  heroFallback: "Собери день вокруг одного спокойного вектора — меньше распыления, больше ясности.",
  dayHeadlineFallback: "День внимательного выбора",
  meaningToday: "Смысл сегодня",
  lookDeeper: "Смотреть глубже",
  lessonSubtitleFallback:
    "Сейчас важно не сделать больше, а сделать осознаннее. Один вектор лучше трёх планов.",
  todayPrefix: "Сегодня: ",
  cardOfDay: "Карта дня",
  tarotA11yFaceUp: "Раскрыта карта дня",
  tarotA11yBack: "Рубашка карты дня",
  tarotA11yFlip: "Дважды нажмите или коснитесь, чтобы перевернуть",
  deeper: "Глубже",
  firstMovePrefix: "Опорный ход: ",
  cautionPrefix: "Осторожность: ",
  todayDoPrefix: "Сегодня: ",
  firstMoveFallback: "один честный шаг, без суеты",
  cautionFallback: "не наращивай шум и спешку",
  todayDoFallback: "зафиксируй смысл до обеда",
  fullGuidanceCta: "Полный расклад в Центре разборов",
  numberOfDay: "Число дня",
  luckyWindowPrefix: "Удачное окно · ",
  colorDotPrefix: "Цвет · ",
  stoneDotPrefix: "Камень · ",
  elementDotPrefix: "Стихия · ",
  ringsTitle: "Кольца выравнивания",
  ringsSubtitle: "Удерживай ясность — смотри, что просаживает кольцо, и куда вести день",
  practicesTitle: "Рекомендовано на сегодня",
  ringHintWater: "→ сильнее кольцо: эмоции +4",
  ringHintBody: "→ сильнее: собранность +4",
  ringHintMoney: "→ сильнее: ресурс +4",
  ringHintDefault: "→ сильнее: смысл +2",
  ritualAffirmation: "Аффирмация",
  ritualAscetic: "Аскеза дня",
  ritualPractice: "Практика",
  ritualJournal: "Записать",
  ritualRite: "Ритуал",
  ritualAsceticBody: "Без импульсивных трат",
  ritualPracticeBody: "Дыхание по Луне, 2 мин",
  ritualJournalBody: "Что ты боишься сказать вслух?",
  ritualRiteBody: "Серебро в контакте с кожей сегодня",
  microTitle: "Короткий вопрос дня",
  microPrompt: "Что больше всего забирает силы?",
  microReward: "Кольцо близости +3% — профиль глубже учитывает твой день",
  microOptions: [
    "Отношения",
    "Неопределённость",
    "Работа",
    "Деньги",
    "Перетаранивание в голове",
  ] as const,
  ritualAffirmationFallback: "Я выбираю ясность важнее удобства",
  habitsTitle: "Сегодня: база",
  habitWater: "Вода",
  habitMove: "Движение",
  habitReflect: "Пауза",
  habitWork: "Глубокая работа",
  habitSpend: "Без эмоциональных трат",
  compatTitle: "Совместимость сегодня",
  compatBody:
    "Линия отношений может пульсировать сильнее — сравнить пары важно, пока внимание в теме",
  compatCta: "Совместимость",
  guidTitle: "Спросить то, что нельзя обсудить в чате",
  guidBody: "Сценарии: «вернётся ли», «уходить ли с работы», «почему снова стопор»",
  guidCta: "Разбор: вопрос",
  diaryTitle: "Пиши чувство, а не план",
  diaryBody:
    "Что ранит? Чем гордишься? Чего боишься признать? Это питает персонализацию.",
  diaryCta: "Отметить в Flow",
  tomorrowTitle: "Завтра: окно ясности",
  tomorrowBody:
    "К после 8:00 откроется сильный слой намерения. Загляни — короткое планирование, без паники.",
  tomorrowCta: "Напомнить (завтра в Today)",
  sheetWhyTitle: "Сегодня: почему так",
  sheetDone: "Готово",
  sheetNatal: "Натал",
  sheetMeaning: "Смысл",
  sheetMoon: "Луна (натал)",
  sheetMoonFallback: "считается с картой",
  sheetFirstMove: "Опорный ход",
  sheetFirstMoveFallback: "один устойчивый вектор",
  sheetRisk: "Риск дня",
  sheetBody: "Тело и сигналы",
  sheetBodyFallback: "собирай сигналы, не обещай лишнего",
  ringSheetTitle: "Разбор",
  ringSheetClose: "Закрыть",
  ringSheetHeadlinePrefix: "Кольцо: ",
  ringSheetNowPrefix: "Сейчас ",
  ringSheetScoreMid: " из 100. ",
  ringSheetTailEmpty: "Сигналы копим ежедневными фиксациями.",
  ringSheetTailFactorsPrefix: "Сильные факторы: ",
  ringAskGuidance: "Спросить в разборе",
  ringLove: "близость",
  ringWealth: "ресурс",
  ringDiscipline: "собранность",
  ringEmotion: "эмоции",
  ringPurpose: "смысл",
  ringSelf: "опора в себе",
  gridLove: "Близость",
  gridWealth: "Ресурс",
  gridDiscipline: "Собранность",
  gridEmotion: "Эмоции",
  gridPurpose: "Смысл",
  gridSelf: "В себе",
  luckyPresets: [
    ["8:00–10:00", "Голубой", "Сапфир", "Воздух"],
    ["14:00–16:00", "Синий глубокий", "Лунный камень", "Вода"],
    ["19:00–21:00", "Индиго", "Аметист", "Свет"],
  ] as const satisfies readonly TodayExperienceLuckyPreset[],
} as const;

export const TODAY_EXPERIENCE_CHROME_EN = {
  todayEyebrow: "TODAY",
  of100: "of 100",
  rhythmSummary: "blended day rhythm",
  a11yRhythm: "Blended day rhythm",
  whyDayFeels: "Why today feels like this",
  a11yWhyHint: "Short read on today’s context",
  energy: "Energy",
  balance: "Balance",
  focus: "Focus",
  heroFallback: "Anchor the day around one calm vector—less scatter, more clarity.",
  dayHeadlineFallback: "A day of careful choices",
  meaningToday: "Today’s meaning",
  lookDeeper: "Go deeper",
  lessonSubtitleFallback:
    "What matters now is not doing more, but doing it with awareness. One vector beats three plans.",
  todayPrefix: "Today: ",
  cardOfDay: "Card of the day",
  tarotA11yFaceUp: "Daily card face up",
  tarotA11yBack: "Daily card back",
  tarotA11yFlip: "Double-tap to flip",
  deeper: "Deeper",
  firstMovePrefix: "Key move: ",
  cautionPrefix: "Caution: ",
  todayDoPrefix: "Today: ",
  firstMoveFallback: "one honest step, no rush",
  cautionFallback: "don’t add noise or hurry",
  todayDoFallback: "lock in the meaning before noon",
  fullGuidanceCta: "Full reading in Guidance",
  numberOfDay: "Number of the day",
  luckyWindowPrefix: "Lucky window · ",
  colorDotPrefix: "Color · ",
  stoneDotPrefix: "Stone · ",
  elementDotPrefix: "Element · ",
  ringsTitle: "Alignment rings",
  ringsSubtitle: "Stay clear—see what drags a ring down and where to steer the day",
  practicesTitle: "Suggested for today",
  ringHintWater: "→ stronger: emotions +4",
  ringHintBody: "→ stronger: discipline +4",
  ringHintMoney: "→ stronger: resources +4",
  ringHintDefault: "→ stronger: meaning +2",
  ritualAffirmation: "Affirmation",
  ritualAscetic: "Daily ascetic",
  ritualPractice: "Practice",
  ritualJournal: "Journal",
  ritualRite: "Ritual",
  ritualAsceticBody: "No impulsive spending",
  ritualPracticeBody: "Moon breath, 2 min",
  ritualJournalBody: "What are you afraid to say out loud?",
  ritualRiteBody: "Silver touching skin today",
  microTitle: "Quick question",
  microPrompt: "What drains you most?",
  microReward: "Closeness ring +3%—your profile learns your day better",
  microOptions: ["Relationships", "Uncertainty", "Work", "Money", "Overthinking"] as const,
  ritualAffirmationFallback: "I choose clarity over comfort",
  habitsTitle: "Today: basics",
  habitWater: "Water",
  habitMove: "Movement",
  habitReflect: "Pause",
  habitWork: "Deep work",
  habitSpend: "No emotional spending",
  compatTitle: "Compatibility today",
  compatBody:
    "Relationship energy may pulse louder—compare pairs while it’s on your mind",
  compatCta: "Compatibility",
  guidTitle: "Ask what’s hard to say in chat",
  guidBody: "Themes: “will they return”, “should I leave this job”, “why I’m stuck again”",
  guidCta: "Guidance: ask",
  diaryTitle: "Write feeling, not plans",
  diaryBody:
    "What hurts? What are you proud of? What’s hard to admit? This feeds personalization.",
  diaryCta: "Log in Flow",
  tomorrowTitle: "Tomorrow: clarity window",
  tomorrowBody:
    "After ~8:00 a stronger intention layer opens—peek in for light planning, no panic.",
  tomorrowCta: "Remind (tomorrow in Today)",
  sheetWhyTitle: "Today: why it feels this way",
  sheetDone: "Done",
  sheetNatal: "Natal",
  sheetMeaning: "Meaning",
  sheetMoon: "Moon (natal)",
  sheetMoonFallback: "from your chart",
  sheetFirstMove: "Key move",
  sheetFirstMoveFallback: "one steady vector",
  sheetRisk: "Day risk",
  sheetBody: "Body and signals",
  sheetBodyFallback: "gather signals, promise less",
  ringSheetTitle: "Read",
  ringSheetClose: "Close",
  ringSheetHeadlinePrefix: "Ring: ",
  ringSheetNowPrefix: "Now ",
  ringSheetScoreMid: " of 100. ",
  ringSheetTailEmpty: "We build signals with daily check-ins.",
  ringSheetTailFactorsPrefix: "Strong factors: ",
  ringAskGuidance: "Ask in Guidance",
  ringLove: "closeness",
  ringWealth: "resources",
  ringDiscipline: "discipline",
  ringEmotion: "emotions",
  ringPurpose: "meaning",
  ringSelf: "self-trust",
  gridLove: "Closeness",
  gridWealth: "Resources",
  gridDiscipline: "Focus",
  gridEmotion: "Emotions",
  gridPurpose: "Meaning",
  gridSelf: "Inner",
  luckyPresets: [
    ["8:00–10:00", "Azure", "Sapphire", "Air"],
    ["14:00–16:00", "Deep blue", "Moonstone", "Water"],
    ["19:00–21:00", "Indigo", "Amethyst", "Light"],
  ] as const satisfies readonly TodayExperienceLuckyPreset[],
} as const;

export function experienceChromeBundle(locale: TodayExperienceLocale) {
  return locale === "ru" ? TODAY_EXPERIENCE_CHROME_RU : TODAY_EXPERIENCE_CHROME_EN;
}

export function formatExperienceFirstMove(v: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).firstMovePrefix}${v}`;
}

export function formatExperienceCaution(v: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).cautionPrefix}${v}`;
}

export function formatExperienceTodayDo(v: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).todayDoPrefix}${v}`;
}

export function formatExperienceLuckyWindow(time: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).luckyWindowPrefix}${time}`;
}

export function formatExperienceColorLine(color: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).colorDotPrefix}${color}`;
}

export function formatExperienceStoneLine(stone: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).stoneDotPrefix}${stone}`;
}

export function formatExperienceElementLine(element: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).elementDotPrefix}${element}`;
}

export function formatExperienceRingSheetHeadline(name: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).ringSheetHeadlinePrefix}${name}`;
}

export function formatExperienceRingSheetBody(
  score: number,
  tail: string,
  locale: TodayExperienceLocale,
): string {
  const b = experienceChromeBundle(locale);
  return `${b.ringSheetNowPrefix}${score}${b.ringSheetScoreMid}${tail}`;
}

export function formatExperienceRingSheetTailFactors(factors: string, locale: TodayExperienceLocale): string {
  return `${experienceChromeBundle(locale).ringSheetTailFactorsPrefix}${factors}`;
}

export function experienceChromeMicroOptions(locale: TodayExperienceLocale): readonly string[] {
  return experienceChromeBundle(locale).microOptions as readonly string[];
}

export function experienceChromeLuckyPresets(locale: TodayExperienceLocale): readonly TodayExperienceLuckyPreset[] {
  return experienceChromeBundle(locale).luckyPresets;
}

/** Flow / Practices / подписи главного TabView — канон в отдельном модуле. */
export * from "./flowPracticesMainTabChrome";
