import Foundation

/// Канон строк — `frontend/src/components/today/todayRitualCopy.ts`. Любое изменение пользовательского текста: сначала TS, затем дословно здесь.
///
/// Голос: «ты»; сценарий говорит «я», не «мы». Род по умолчанию нейтрален; при известном поле профиля для заголовка «чего не дожимать» — `RuUserDeclension.ritualAvoidHeading`.
enum TodayRitualCopy {
    static let checkInTitle = "Как ты сейчас?"
    static let checkInEyebrow = "Сейчас"
    static let checkInHint =
        "Отметь состояние — так разбор дня лучше совпадёт с тем, что ты реально чувствуешь. Без оценок и «нормы»."
    static let moodAck =
        "Принято. Сегодня лучше не перегружать тебя задачами — выбери один ясный шаг."
    static let moodAckDrive =
        "Принято. У тебя есть энергия, но важно не разнести её на десять направлений."
    static let checkInMicroEyebrow = "Уточнение"
    static let checkInMicroHint = "Что сегодня сильнее всего занимает голову?"

    static let summaryEyebrow = "Подсказки на день"
    /// Заголовок блока со списками possible / avoid / support — паритет с веб `summarySituationEyebrow`.
    static let summarySituationEyebrow = "Ориентиры дня"
    static let summaryIntro =
        "Это не инструкция и не приговор — просто дружеские ориентиры. Возьми то, что откликается; остальное смело отпусти."
    static let possibleHeading = "Что может зайти полегче"
    static let avoidHeading = "Чего сегодня лучше не дожимать"
    static let supportHeading = "На что можно опереться"
    static let whyCTA = "Откуда это всё — простыми словами"
    static let whySheetTitle = "Почему сегодня так написано"
    static let whyAstroEyebrow = "Твоя карта и небо сегодня"
    static let whyAstroIntro =
        "Коротко: что из твоей карты и неба на сегодня поддерживает этот день — не развлечение и не общие фразы."
    static let whyPatternEyebrow = "Как складывается день"
    static let whyLifeContextEyebrow = "Твой контекст"
    static let whyFallback =
        "Это не готовый текст из журнала: он опирается на твои ответы о себе и о дне."

    static func whyAstroKindTitle(_ kind: String) -> String {
        switch kind {
        case "natal_angle": return "Угол карты"
        case "natal_luminary": return "Светила"
        case "natal_personal": return "Личные планеты"
        case "natal_aspect": return "Аспект"
        case "natal_sun_sign": return "Солнечный знак"
        case "daily_spine": return "Стержень дня"
        case "lunar_context": return "Луна и фаза"
        case "profile_prism": return "Профиль"
        case "rhythm_placeholder": return "Ритм"
        case "ritual_tarot": return "Карта ритуала"
        case "ritual_number": return "Число ритуала"
        case "ritual_mood": return "Состояние"
        case "ritual_day_events": return "События дня"
        default: return "Слой карты"
        }
    }

    static let areasEyebrow = "Сферы"
    static let areasTitle = "Куда смотреть сегодня"
    static let areasIntroToday =
        "Три линии: где движение уместно, где лучше не давить, где держать нейтралитет. Нажми строку — коротко по теме и по твоему ритму."
    /// O11: паритет `RITUAL_COPY.areasScoresProvisionalHint` на вебе.
    static let areasScoresProvisionalHint =
        "Проценты у сфер сейчас приблизительные: по кольцам Meaning мало данных, а в Flow пока немного опор. Пара честных отметок сделает картину точнее."
    static let areasBeforeMoodHint =
        "Если отметишь настроение выше, строка «опора в ритме» у сферы станет ближе к тому, как ты реально живёшь тему."
    static let areaTodayEyebrow = "Сегодня по теме"
    static let areaRhythmEyebrow = "Опора в ритме"
    static let areaRhythmExpanded =
        "Число у сферы — про твои недавние шаги в Flow по этой теме, а не про «оценку звёзд»."
    static let areasScenarioMissing =
        "Отдельной подсказки по этой сфере в тексте дня нет — загляни в блок «Ориентиры дня» выше."
    static let areaSignal = "Что может усилить тему"
    static let areaNuance = "На что не рассчитывать"
    static let heroRhythmCaption = "Твой ритм по отметкам"
    /// Паритет с `RITUAL_COPY.heroRhythmScorePending` на вебе.
    static let heroRhythmScorePending = "появится, когда накопится несколько твоих отметок в Flow"
    /// Паритет с веб `RITUAL_COPY.heroShortDayTitle` … `heroWindowLabel`.
    static let heroShortDayTitle = "Коротко о дне"
    static let heroWhyPrompt = "Почему так?"
    static let heroFocusLabel = "Фокус"
    static let heroTempoLabel = "Темп"
    static let heroRiskLabel = "Риск"
    static let heroBestMoveLabel = "Лучший ход"
    static let heroWindowLabel = "Лучшее окно"
    static let heroRhythmHint =
        "Не про судьбу: насколько в последние дни ты опираешься на свои отметки и шаги в Flow. Строка ниже — про настроение сегодня."
    static func heroScoreFootnote(score: Int) -> String {
        "По желанию: насколько день ощущается цельным — \(score) из 100."
    }

    /// Паритет с `tempoLabelForEnergyScore` на вебе (`todayRitualCopy.ts`).
    static func tempoLabelForEnergyScore(score: Int) -> String {
        let s = min(100, max(0, score))
        switch s {
        case ..<38:
            return "тихий"
        case ..<58:
            return "спокойный"
        case ..<78:
            return "ровный"
        default:
            return "подвижный"
        }
    }

    /// Тот же смысл, что `rhythmTierLabelForScore` на вебе (пороги 38 / 58 / 78).
    static func rhythmTierLabel(score: Int) -> String {
        let s = min(100, max(0, score))
        switch s {
        case ..<38:
            return "Мало недавних шагов в Flow — это нормально; одна отметка уже меняет картину."
        case ..<58:
            return "Спокойный уровень: немного опорных шагов за последние дни."
        case ..<78:
            return "Хорошая опора — твои шаги заметны."
        default:
            return "Очень крепкая опора"
        }
    }

    /// `RITUAL_COPY.areasFallback` на вебе.
    static let areasFallback =
        "Пока мало твоих отметок по сферам — ниже общий ориентир. Одна честная запись в течение дня уже сделает следующий разбор точнее."

    static let focusEyebrow = "Что сделать"
    /// Паритет `RITUAL_COPY.focusTitle` / TODAY_WEB §4 — секция «Главный шаг».
    static let focusTitle = "Главный шаг на сегодня"
    static let focusChooseOneHint =
        "Выбери один вариант — потом можно зафиксировать в Flow или взять 20 минут."
    /// DE-7: заголовок блока над чипами (паритет веб `RITUAL_COPY.guideMeaningCompletionsEyebrow`).
    static let guideMeaningCompletionsEyebrow = "Сегодня в Flow"
    /// Когда fusion отдал счётчики, но за день всё ещё нули.
    static let guideMeaningCompletionsEmpty =
        "Пока нет завершённых шагов — выбери вариант ниже или открой календарь Flow."
    /// DE-7: префикс одной строки (устарело по отношению к чипам; оставлено для совместимости).
    static let mainStepMeaningProgressIntro = "Сегодня в Flow уже отмечено:"

    private static let guideMeaningCompletionOrder: [(key: String, label: String)] = [
        ("habit_completed", "привычка"),
        ("practice_completed", "практика"),
        ("focus_completed", "фокус"),
        ("affirmation_done", "аффирмация"),
        ("ascetic_step_done", "аскеза"),
    ]

    /// Чипы для блока «Сегодня в Flow»: только ненулевые, канонический порядок (паритет веб `guideMeaningCompletionChipItems`).
    static func guideMeaningCompletionChipItems(_ raw: [String: Int]) -> [(key: String, label: String, count: Int)] {
        var out: [(String, String, Int)] = []
        for item in guideMeaningCompletionOrder {
            let n = raw[item.key] ?? 0
            if n > 0 {
                out.append((item.key, item.label.capitalized, n))
            }
        }
        return out
    }

    /// Паритет `formatGuideMeaningCompletionsLine` в `todayRitualCopy.ts` и `guide_flow_signals.py`.
    static func formatGuideMeaningCompletionsLine(_ raw: [String: Int]?) -> String? {
        guard let raw, !raw.isEmpty else { return nil }
        var parts: [String] = []
        for item in guideMeaningCompletionOrder {
            let n = raw[item.key] ?? 0
            if n == 1 {
                parts.append(item.label)
            } else if n > 1 {
                parts.append("\(item.label) ×\(n)")
            }
        }
        return parts.isEmpty ? nil : parts.joined(separator: " · ")
    }
    static let heroCoreEyebrow = "Сегодня"
    static let ritualDayReadyFootnote =
        "Карта и число остаются в сводке и в «Почему так?» — я не дублирую их большими блоками, чтобы экран не перегружать."
    static let supportEyebrow = "Поддержка"
    /// Паритет `RITUAL_COPY.supportSectionTitle` на вебе.
    static let supportSectionTitle = "Поддержка на сегодня"
    /// Паритет `RITUAL_COPY.supportIntroNoStructure` — когда в Flow ещё нет целей.
    static let supportIntroNoStructure =
        "Так Today сможет подстраивать рекомендации под реальные действия, а не только под настроение. Добавь цель, привычку, короткую практику или аскезу в Flow."

    static let essentialsEyebrow = "Базовые опоры"
    static let essentialsTitle = "Чтобы не слететь"
    static let essentialsSub = "Четыре опоры — отметь по факту, без отчёта."
    static let essentialsPurposeHint =
        "Не чеклист «успешного человека». Галочка — знак, что это сделано для себя, без отчёта никому."
    static let essentialsProgressExplain =
        "Полоска — только для тебя, без оценки «молодец / не молодец»."
    static let essentialsMoodAdaptHint =
        "Четыре опоры на каждый день — отметь то, что для тебя честно: уже сделано, в процессе или точно запланировано на сегодня."

    static func essentialsProgressLabel(done: Int, total: Int) -> String {
        "Отмечено: \(done) из \(total)"
    }

    static let buildDayEyebrow = "Собрать день"
    static let buildDayTitle = "С чего начать"
    static let buildDayBody =
        "Добавь в Flow цель, привычку или короткую практику — разбор дня сможет опираться на твой реальный план, а не только на символы."
    static let buildDayIdeasTitle = "Идеи на сегодня"
    static let buildDayIdeasIntro =
        "Без обязаловки — коротко, зачем это может помочь именно сегодня."
    static let buildDayCalendarHint =
        "Если занесёшь в календарь Flow привычку, цель или аскезу, проще держать один якорь и не расползаться по задачам."

    /// Паритет `RITUAL_BUILD_DAY_QUICK_CHIPS` в `todayRitualCopy.ts` — порядок и подписи дословно.
    enum BuildDayQuickChips {
        static let rows: [(id: String, title: String, kind: TrackerQuickCreateKind)] = [
            ("chip_habit_discipline", "дисциплина", .habit),
            ("chip_goal_money", "деньги", .goal),
            ("chip_goal_closeness", "близость", .goal),
            ("chip_ascetic_emotions", "эмоции", .ascetic),
        ]
    }

    /// Оболочка `/today`: загрузка, ошибки, фон (паритет веб `RITUAL_COPY`, §5.3).
    enum TodayPageShell {
        static let loadingSession = "Сессия…"
        static let loadingDay = "Собираю твой день…"
        static let refreshingDay = "Обновляю твой день…"
        static let authRequired = "Войдите, чтобы использовать цикл дня"
        static let dataMissing = "Данные не найдены"
        static let retryCta = "Попробовать снова"
        static let loadError = "Ошибка при загрузке дня"
        static let supplementaryLoadingHint = "Календарь и ритм подгружаются в фоне"
        static let dailyStepMeaning = "Смысл дня"
        static let dailyStepFocus = "Опора и действие"
        static let dailyStepClosing = "Итог дня"
    }

    /// DE-8: паритет веб `TodayNarrativeDepthControl`.
    enum NarrativeDepthControl {
        static let eyebrow = "Глубина текстов дня"
        static let saving = "Сохраняю и обновляю…"
        static let hint = "Влияет на следующую генерацию guide и связанных блоков."
        static let hintSettingsTail = "Полный список — Профиль → Настройки."
        static let allSettingsCta = "Все настройки"
        /// Паритет `RITUAL_COPY.narrativeDepthOption*` / `todayNarrativeDepthUi.ts`.
        static let optionQuick = "Короче"
        static let optionNormal = "Обычно"
        static let optionDeep = "Глубже"
    }

    /// Нижняя панель «20 минут» (паритет веб `page.tsx` / `TodayFocusTwentyBar`).
    enum FocusTimerChrome {
        static func chromeLine(timeLabel: String) -> String { "Фокус \(timeLabel)" }
        static let pause = "Пауза"
        static let stop = "Стоп"
        static let toastInfo = "20 минут на выбранный шаг — один слот без переключений."
    }

    /// Тосты и фолбэки ошибок `/today` (паритет веб `RITUAL_COPY`).
    enum TodayPageToasts {
        static let guidanceFollowup =
            "После разбора: закрепи один конкретный шаг в дневном ритме ниже."
        static let saveDayConnectionError = "Не удалось сохранить ответ дня"
        static let completePracticeError = "Не удалось отметить практику"
        static let saveEveningCloseError = "Не удалось сохранить закрытие дня"
    }

    /// Сообщения при смене глубины narrative (веб показывает тосты; iOS — запас под паритет).
    enum NarrativeDepthToasts {
        static let deepSubscriptionRequired = "Режим «Глубже» доступен с подпиской Plus или Pro."
        static let saveSuccess = "Глубина сохранена — обновляю тексты дня."
        static let saveError = "Не удалось сохранить глубину"
    }

    /// Пресеты окна / цвета / камня для числа (паритет веб `NUMEROLOGY_LUCKY_DAY_PRESETS`).
    enum NumerologyLuckyDayPresets {
        static let rows: [(time: String, color: String, stone: String)] = [
            ("8:00–10:00", "Лазурь", "Сапфир"),
            ("14:00–16:00", "Глубокий синий", "Лунный камень"),
            ("19:00–21:00", "Индиго", "Аметист"),
        ]
    }

    /// Паритет веб `ritualGuideDayLabelFallback`.
    static let ritualGuideDayLabelFallback = "День выбора"
    /// Паритет веб `numerologyMeaningFallbackShort`.
    static let numerologyMeaningFallbackShort = "Пауза. Правда. Сбор внимания."
    /// Теги колец плана дня (цикл из трёх) — паритет веб `todayActionPlanRing*`.
    static let todayActionPlanRingCloseness = "близость"
    static let todayActionPlanRingFocus = "фокус"
    static let todayActionPlanRingMoney = "деньги"
    static let todayActionPlanRingTarot = "таро"

    static let ritualDeckEyebrow = "Листай: число · карта · подсказки дня"
    static let todaySummaryEyebrow = "Сводка дня"
    static let numberDayCaptionSystem = "Число дня уже рассчитано"
    static let tarotDayCaptionInteractive = "Вытяни карту дня"
    static let tarotCardSubhead = "Вытяни карту — она задаст акцент твоего дня"
    static let tarotClosedLead =
        "Иногда день становится понятнее, когда есть один символ, через который можно на него посмотреть."
    static let tarotClosedBody =
        "Вытяни карту — станет яснее, какую тему она подсвечивает сегодня: в действиях, отношениях, деньгах, энергии и решениях."
    static let tarotDrawIntro =
        "Вытяни одну карту Таро для сегодняшнего дня. Это не «готовый ответ», а символ, через который можно посмотреть на день: где действовать, где быть осторожнее, что не игнорировать и какой вопрос себе задать."
    static let tarotDrawCta = "Вытянуть карту"
    static let tarotApplyToTodayCta = "Применить к Today"
    static let tarotDrawAnotherCta = "Вытянуть другую"
    static let tarotDrawAnotherHint =
        "Можно добавить одну уточняющую карту за день — второй раз уже без нового перетягивания."
    static let tarotYourCardPrefix = "Твоя карта дня — "
    static let tarotAppliedAck =
        "Карта учтена: сферы и шаг подстроены под её смысл. Вечером можно честно отметить, что сработало."
    static let tarotQuestionEyebrow = "Главный вопрос карты"
    static let tarotClarifierEyebrow = "Уточняющая карта"

    static let eveningHookTitle = "Вечерняя фиксация"
    static let eveningHookBody =
        "Вечером можно отметить, что совпало, что не сработало и что стало понятнее. Удобно после 19:00."
    /// Паритет веб `RITUAL_COPY.eveningHookBodyCompact` (до 19:00 на `/today`).
    static let eveningHookBodyCompact =
        "Вечером вернёмся к этому: что совпало, что не сработало, что стало понятнее."
    static let eveningDetails = "Открыть форму"

    static let cardEyebrow = "Карта дня"
    static let cardClosedHint =
        "Иногда день становится понятнее, когда есть один символ, через который можно на него посмотреть."
    static let cardRevealedHint =
        "Карта работает как личный символ дня: через неё проще заметить тему, риск и один честный шаг."
    static let revealCardCta = "Вытянуть карту"
    static let continueToNumber = "Продолжить"
    /// Паритет с `RITUAL_COPY` на вебе (пошаговый макет).
    static let ritualEntryTitle = "Твой день"
    static let ritualEntryBody =
        "Ответы уже внутри тебя. Я помогу их увидеть и подсветить ясный шаг."
    static let ritualEntryCta = "Начать"
    static let ritualEntryTiming = "Это займёт 1–2 минуты"
    static let ritualProgressHint = "Карта → число → настроение — шаги ниже."
    /// Паритет веб `RITUAL_COPY.ritualProgressCardLabel` — фраза «Карта: …» в подсказке героя.
    static let ritualProgressCardLabel = "Карта"
    /// Паритет веб `RITUAL_COPY.ritualProgressNumberLabel`.
    static let ritualProgressNumberLabel = "Число"
    /// Паритет с `RITUAL_COPY.ritualProgressNumberPending` на вебе.
    static let ritualProgressNumberPending = "Число дня откроешь на следующем шаге."
    static let ritualStepCardShort = "Карта"
    static let ritualStepNumberShort = "Число"
    static let ritualStepMoodShort = "Настроение"
    static let tarotExtraDetailToggle = "Дополнительно: вопрос карты, применить к дню…"
    static let numberExtraDetailToggle = "Дополнительно: ритм и связка с картой"
    static let sphereDeckSwipeHint = "Три направления: где лучше движение, где аккуратность, где нейтральный фон."
    static let sphereDeckOpenDetailCta = "Подробнее по сфере"
    /// Как `RITUAL_COPY.areaSignal` на вебе.
    static let sphereSheetWhyTitle = "Что может усилить тему"
    static let sphereSheetWebParityNote =
        "Здесь тот же текст по сфере, что и на большом экране — можно дочитать без потери смысла."
    static let sphereSheetNavTitle = "Сфера дня"
    static let reloadDayPaidHeadline = "Перезагрузить день (скоро)"
    static let reloadDayPaidBody =
        "Платная опция за внутренние токены или оплату: новый проход ритуала и пересбор текстов. Сейчас доступно только «Обновить день» — бесплатно сбросить шаги этого прохода."
    static let refreshDayCta = "Обновить день"
    static let tarotRevealScreenTitle = "Твоя карта дня"
    static let numberRevealScreenTitle = "Твоё число дня"
    static let ritualContinueCta = "Продолжить"
    static let ritualMoodDoneCta = "Готово"
    static let numberRevealDoneCta = "Готово"
    static let ritualDayReadyTitle = "Твой день"
    static let daySummaryMarkersEyebrow = "Маркеры дня"
    static let daySummaryShortEyebrow = "Короткая сводка"
    /// Паритет `RITUAL_COPY.guideAdditionalDisclosureTitle` / веб `TodayGuideSection` summary.
    static let guideAdditionalDisclosureTitle = "Дополнительно"
    /// Подзаголовок раскрываемой зоны в ритуальной карточке «Твой день» (содержимое — сводка, делать/не делать, ориентиры).
    static let guideAdditionalDisclosureSubtitleRitualCard =
        "Короткая сводка, ориентиры «делать / не делать» и практические подсказки"
    /// DE-9: полоска из `fusion.day_history` (паритет веб `RITUAL_COPY.dayHistoryEyebrow`).
    static let dayHistoryEyebrow = "Ритм и вчера"
    static let dayHistoryHint = "По отметкам в Flow: вчерашние баллы и сдвиг к сегодняшнему дню."
    /// DE-9 v1.3: при нулевой дельте не показываем «к сегодня: … 0» (паритет веб `RITUAL_COPY`).
    static let dayHistoryDeltaAllZeroTailRu =
        "Сдвига к сегодняшнему дню по отметкам пока нет — когда появятся сегодняшние баллы в Flow, строка станет точнее."
    static let dayHistoryDeltaAllZeroTailEn =
        "No shift toward today in Flow yet—once today's scores are logged, this line will read clearer."
    /// O7: одна строка без ложных «вчера 50/50/50» — паритет `RITUAL_COPY.dayHistoryDeltaUntrustworthyTail`.
    static let dayHistoryDeltaUntrustworthyTailRu =
        "Вчера в Flow не было отметок для сравнения с сегодня. Когда появятся вчерашний ритм — настроение, дневник или практики — здесь будут баллы и сдвиг «к сегодня»."
    static let dayHistoryDeltaUntrustworthyTailEn =
        "No Flow markers yesterday to compare with today. Once you log mood, diary, or practice for that day, scores and the toward-today line will show here."

    /// Паритет `formatFusionDayHistoryRu` / `formatFusionDayHistoryEn` в `todayRitualCopy.ts`.
    static func formatFusionDayHistoryLine(_ raw: FusionDayHistoryV0?) -> String? {
        guard let h = raw, h.contractVersion == "day_history_v0" else { return nil }
        let fs = h.yesterday.fusionScores
        let d = h.fusionScoreDeltaVsYesterday
        func fmt(_ v: Int) -> String { v > 0 ? "+\(v)" : "\(v)" }
        let ru = IOSAppLocale.prefersRussian
        let trustworthy = h.fusionScoreDeltaTrustworthy ?? true
        let headRu = "Вчера: энергия \(fs.energy), баланс \(fs.emotionalBalance), фокус \(fs.focus)"
        let headEn = "Yesterday: energy \(fs.energy), balance \(fs.emotionalBalance), focus \(fs.focus)"
        if !trustworthy {
            if ru {
                return dayHistoryDeltaUntrustworthyTailRu
            }
            return dayHistoryDeltaUntrustworthyTailEn
        }
        let allZero = d.energy == 0 && d.emotionalBalance == 0 && d.focus == 0
        if allZero {
            if ru {
                return "\(headRu). \(dayHistoryDeltaAllZeroTailRu)"
            }
            return "\(headEn). \(dayHistoryDeltaAllZeroTailEn)"
        }
        if ru {
            return "\(headRu) · к сегодня: энергия \(fmt(d.energy)), баланс \(fmt(d.emotionalBalance)), фокус \(fmt(d.focus))"
        }
        return "\(headEn) · toward today: energy \(fmt(d.energy)), balance \(fmt(d.emotionalBalance)), focus \(fmt(d.focus))"
    }

    /// Паритет `formatFusionDayHistoryWeekSummaryRu` в `todayRitualCopy.ts` (тире U+2013 между min и max).
    static func formatFusionDayHistoryWeekLine(_ raw: FusionDayHistoryV0?) -> String? {
        if raw?.trailing7dSummaryTrustworthy == false { return nil }
        guard let s = raw?.trailing7dSummary else { return nil }
        func fmt(_ a: FusionDayHistoryV0.Trailing7dAxisAgg) -> String {
            let av = Int(a.avg.rounded())
            return "ср. \(av) (\(a.min)\u{2013}\(a.max))"
        }
        return "7 дней до вчера: энергия \(fmt(s.energy)), баланс \(fmt(s.emotionalBalance)), фокус \(fmt(s.focus))"
    }

    /// DE-9 v1.4: паритет `formatFusionDayHistoryMeaningLineRu` в `todayRitualCopy.ts`.
    static func formatFusionDayHistoryMeaningLine(_ raw: FusionDayHistoryV0?) -> String? {
        guard let y = raw?.yesterday, y.meaningActive == true else { return nil }
        let completions = y.meaningCompletionsTotal ?? 0
        let evening = (y.dayFlow?.eveningCompleted == true)
            || (y.meaningDaySignals?["evening_reflection_submitted"] ?? 0) > 0
        let spheres = y.meaningDaySignals?["sphere_opened"] ?? 0
        var parts: [String] = []
        if completions > 0 {
            parts.append(pluralStepsRu(completions) + " в Flow")
        }
        if evening { parts.append("вечер закрыт") }
        if spheres > 0 {
            let word = spheres == 1 ? "сфера" : (spheres < 5 ? "сферы" : "сфер")
            let opened = spheres == 1 ? "открыта" : "открыты"
            parts.append("\(opened) \(spheres) \(word)")
        }
        if parts.isEmpty, y.dayFlow?.dayCompleted == true {
            parts.append("день отмечен")
        }
        if parts.isEmpty { return nil }
        return "Вчера: \(parts.joined(separator: ", "))."
    }

    /// DE-9 v1.5: паритет `formatFusionDayHistoryReflectionLineRu`.
    static func formatFusionDayHistoryReflectionLine(_ raw: FusionDayHistoryV0?) -> String? {
        guard let ex = raw?.yesterday.reflectionExcerpt else { return nil }
        if let er = ex.eveningReflection?.trimmingCharacters(in: .whitespacesAndNewlines), er.count >= 8 {
            return "Вчера вечером: «\(er)»"
        }
        if let noticed = ex.eveningObservations?["noticed"]?.trimmingCharacters(in: .whitespacesAndNewlines),
           noticed.count >= 8 {
            return "Вчера заметил(а): «\(noticed)»"
        }
        if let mi = ex.morningIntention?.trimmingCharacters(in: .whitespacesAndNewlines), mi.count >= 8 {
            return "Вчера утром: «\(mi)»"
        }
        return nil
    }

    private static func pluralStepsRu(_ n: Int) -> String {
        let mod10 = n % 10
        let mod100 = n % 100
        if mod10 == 1 && mod100 != 11 { return "\(n) шаг" }
        if (2...4).contains(mod10) && !(12...14).contains(mod100) { return "\(n) шага" }
        return "\(n) шагов"
    }

    /// Паритет веб `formatRitualCardNumberBridgePageFallback`.
    static func formatRitualCardNumberBridgePageFallback(cardName: String, numerologyDigit: String) -> String {
        "«\(cardName)» и число \(numerologyDigit) просят одного: внутренняя честность — раньше внешнего «надо»."
    }

    /// Паритет веб `formatRitualCardNumberBridgeWithTarotPicked`.
    static func formatRitualCardNumberBridgeWithTarotPicked(
        cardNameRu: String,
        numerologyDigit: String,
        rhythmSuffix: String,
        clarifierNameRu: String?
    ) -> String {
        let trimmed = clarifierNameRu?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let extra: String
        if trimmed.isEmpty {
            extra = ""
        } else {
            extra = " Уточнение — «\(trimmed)»: второй акцент к символу дня."
        }
        return "«\(cardNameRu)» и число \(numerologyDigit): картой задаёшь акцент дня; \(rhythmSuffix).\(extra)"
    }

    /// Паритет веб `formatRitualCardNumberDetailEyebrow`.
    static func formatRitualCardNumberDetailEyebrow(numerologyValue: String) -> String {
        "\(ritualProgressNumberLabel) \(numerologyValue)"
    }

    /// Паритет с `RITUAL_COPY.dayEngineBriefEyebrow` на вебе — ключ `day_engine_brief` в payload guide.
    static let dayEngineBriefEyebrow = "Опора дня"
    /// Паритет с `RITUAL_COPY.dayModelBriefEyebrow` — блок `day_model` (`day_model_v0`).
    static let dayModelBriefEyebrow = "Одна ось дня"
    static let dayModelOneFocusLabel = "Фокус"
    static let daySummaryDoTitle = "Что делать"
    /// Короткий нейтральный вариант; в `TodayRitualFlowView` над текстом «не дожимать» показывают `RuUserDeclension.ritualAvoidHeading`.
    static let daySummaryDontTitle = "Чего не делать"
    static let daySummaryPracticalEyebrow = "Практичные ориентиры"
    static let daySummaryWhyCta = "Почему так?"
    static let daySummaryWhyCollapse = "Свернуть объяснение"
    static let dayMarkerCard = "Карта"
    static let dayMarkerNumber = "Число"
    static let dayMarkerMoon = "Луна и фон дня"
    static let dayMarkerPhase = "Фаза Луны"
    static let dayMarkerMood = "Состояние"
    static let spheresTodayTitle = "Сферы сегодня"
    static let spheresSeeAll = "Подробнее по сферам"
    /// Паритет веб `RITUAL_COPY.areasTriadModalDetailHint` — строка под карточкой сферы в треугольнике.
    static let areasTriadModalDetailHint = "Подробнее в окне"
    static let relationshipSphereLabel = "Отношения"

    // MARK: - Четыре сферы (`todayFourAreas.ts` ⇄ RitualFourAreaBuilder)

    static let fourAreaLabelLove = "Любовь"
    static let fourAreaLabelWork = "Работа"
    static let fourAreaLabelMoney = "Деньги"
    static let fourAreaLabelEnergy = "Энергия"
    static let fourAreaEnergyHeadlineFallback = "Темп и ресурс"
    static let fourAreaEnergyRiskChunkPrefix = "Напряжение редко уходит само, пока на фоне: "
    static let fourAreaMoodSuffixCautious = " Сейчас особенно важно не форсировать."
    static let fourAreaMoodSuffixFuel = " Это можно использовать как топливо, если держать темп."
    static let fourAreaLoveInsightFallback = "В близости честный контакт полезнее красивой картинки."
    static let fourAreaLoveWatch = "Не пытайся угадать другого человека — лучше сказать прямо."
    static let fourAreaLoveReasonBase =
        "Подсказка опирается на твой гороскоп дня и настроение: чем честнее ты с собой в чек-ине, тем меньше «угадайку» в тексте."
    static let fourAreaWorkInsightFallback = "Один понятный вектор обычно спокойнее, чем десять задач «на потом»."
    static let fourAreaWorkWatch = "Сложное лучше расписать или взять в один спокойный слот."
    static let fourAreaWorkReasonNoFirstMoveFallback =
        "Если в Flow есть цели и привычки — опираюсь на них; иначе на ось дня из гороскопа, без выдуманных задач."
    static let fourAreaMoneyInsightFallback = "Полезно отличить спешку от того, что правда нужно — и не кормить шум."
    static let fourAreaMoneyWatch = "Импульсивная трата? Попробуй паузу до вечера."
    static let fourAreaMoneyReasonNoAvoidFallback =
        "Фокус на цифрах и границах: что уже есть в твоём дне и что гороскоп помечает как риск импульса."
    static let fourAreaEnergyInsightSoftDay = "Собери день мягко, без скачков «на рывок»."
    static let fourAreaEnergyInsightNoBestModeFallback =
        "Энергия дня не про рывок, а про ровный ритм — чтобы потом не разбирать последствия."
    static let fourAreaEnergyWatch = "Сон, еда и вода — раньше новых обещаний кому-то."
    static let fourAreaEnergyReasonFallback =
        "Энергия — про сон, нагрузку и эмоциональный фон; собираю это из твоего контекста."

    static func fourAreaMoodSuffix(mood: String?) -> String {
        guard let mood else { return "" }
        switch mood {
        case "anxious", "heavy", "confused":
            return fourAreaMoodSuffixCautious
        case "motivated", "hopeful", "driven":
            return fourAreaMoodSuffixFuel
        default:
            return ""
        }
    }

    static func formatFourAreaEnergyRiskChunk(risk: String) -> String {
        fourAreaEnergyRiskChunkPrefix + risk
    }

    // MARK: - Ритуальный поток iOS (`TodayRitualFlowView`)

    static let ritualFlowHeroMetricsDisclaimerRu = "Это метрики в приложении, не предсказание судьбы."
    static let ritualFlowHeroMetricsDisclaimerEn = "These are in-app metrics—not a prediction of fate."
    static let ritualFlowProtectionSaving = "Сохраняю..."
    static let ritualFlowProtectionSaveCta = "Защитить это сегодня"
    static let ritualFlowEveningNarrativeLoading = "Собираю вечерний смысл…"
    static let ritualFlowEveningHeadlineFallback = "Короткий вечерний вектор"
    static let ritualFlowHeroSubtitleFallback = "Сегодня важен не контроль, а ясность."
    static let ritualFlowNumerologyLinePrefix = "Число: "
    static let ritualFlowNumerologyEmpty = "Число: —"
    static let ritualFlowTriadStrongNoTail = " — сейчас лучшее место для движения."
    static let ritualFlowTriadStrongWithTail = " — сейчас лучшее место для движения: "
    static let ritualFlowTriadWeakNoTail = " — аккуратно, не дави — лучше сказать прямо, чем угадывать."
    static let ritualFlowTriadWeakWithTail = " — аккуратно, не дави: "
    static let ritualFlowTriadNeutralNoTail = " — нейтрально, без лишнего импульса."
    static let ritualFlowTriadNeutralWithTail = " — нейтрально: "
    static let ritualFlowNatalMoonPrefix = "Луна в натале: "
    static let ritualFlowProtectionSavedPrefix = "Сохранили. Теперь день собран вокруг: "
    static let ritualFlowProtectionSavedSuffix = "."
    static let ritualFlowProtectionSaveError = "Не удалось сохранить цель дня. Попробуй ещё раз."
    static let ritualFlowProtectionDisciplineTitle = "Дисциплину"
    static let ritualFlowProtectionDisciplineReason =
        "Если день рассыпается, мягкая дисциплина возвращает тебе управление без жёсткости."
    static let ritualFlowProtectionDisciplinePrompt =
        "Сегодня я защищаю дисциплину: один ясный шаг важнее трёх незавершённых."
    static let ritualFlowProtectionMoneyReason =
        "Подходит, когда фон дня про ресурс, траты или решения под давлением."
    static let ritualFlowProtectionMoneyPrompt =
        "Сегодня я защищаю деньги: не трачу на эмоции и сначала даю себе паузу."
    static let ritualFlowProtectionLoveReason =
        "Если день про отношения, лучше беречь честность и темп разговора, а не форсировать ответ."
    static let ritualFlowProtectionLovePrompt =
        "Сегодня я защищаю любовь: выбираю честный контакт вместо догадок и напряжения."
    static let ritualFlowProtectionBalanceTitle = "Баланс"
    static let ritualFlowProtectionBalanceReason =
        "Когда внутри тяжело или тревожно, лучше строить день вокруг эмоциональной устойчивости."
    static let ritualFlowProtectionBalancePrompt =
        "Сегодня я защищаю баланс: не перегружаю себя и возвращаюсь к телу, если начинает качать."
    static let ritualFlowGoalLoveHonestTalkTitle = "Один честный разговор"
    static let ritualFlowGoalLoveHonestTalkReason =
        "Если день про отношения — не распахивать всё сразу, а прояснить одну вещь, которая болит."
    static let ritualFlowGoalLovePauseReplyTitle = "Пауза перед ответом"
    static let ritualFlowGoalLovePauseReplyReason =
        "Так проще не ответить из обиды или тревоги — и услышать себя."
    static let ritualFlowGoalWorkCalmBlockTitle = "Один спокойный рабочий блок"
    static let ritualFlowGoalWorkCalmBlockReason =
        "Внимание не расползается между задачами — к вечеру легче заметить, что главное для тебя сдвинулось."
    static let ritualFlowGoalWorkPauseSpendTitle = "Пауза перед импульсной тратой"
    static let ritualFlowGoalWorkPauseSpendReason =
        "Если фон про деньги, это часто даёт опору быстрее, чем новые списки планов."
    static let ritualFlowGoalNeutralMorningTitle = "Утренний ритм"
    static let ritualFlowGoalNeutralMorningReason =
        "Вода, чуть движения и один понятный старт — без давления «успеть всё»."
    static let ritualFlowGoalNeutralOneStepTitle = "Один завершённый шаг"
    static let ritualFlowGoalNeutralOneStepReason =
        "Конкретика вместо туманного «надо» — так проще почувствовать опору: я справляюсь."

    static func formatRitualFlowSphereRhythmA11y(title: String, pct: Int) -> String {
        "Опора в ритме по теме «\(title)»: \(pct) из 100"
    }

    static func formatRitualFlowTriadLine(head: String, tail: String, stance: String) -> String {
        let t = tail.trimmingCharacters(in: .whitespacesAndNewlines)
        switch stance {
        case "up":
            return t.isEmpty ? head + ritualFlowTriadStrongNoTail : head + ritualFlowTriadStrongWithTail + t
        case "down":
            return t.isEmpty ? head + ritualFlowTriadWeakNoTail : head + ritualFlowTriadWeakWithTail + t
        default:
            return t.isEmpty ? head + ritualFlowTriadNeutralNoTail : head + ritualFlowTriadNeutralWithTail + t
        }
    }

    static func formatRitualFlowProtectionSaved(titleLowercased: String) -> String {
        ritualFlowProtectionSavedPrefix + titleLowercased + ritualFlowProtectionSavedSuffix
    }

    static func formatRitualFlowNumerologyLine(value: Int?) -> String {
        guard let value else { return ritualFlowNumerologyEmpty }
        return ritualFlowNumerologyLinePrefix + "\(value)"
    }

    static func formatRitualFlowNatalMoon(sign: String) -> String {
        ritualFlowNatalMoonPrefix + sign
    }

    static let numberDayEyebrow = "Число дня"
    static let numberClosedHint =
        "Число задаёт ритм дня рядом с картой. Открой блок — увидишь цифру и короткий смысл."
    static let numberRevealCta = "Открыть число дня"

    static let numerologyBestTimeLabel = "Удачное окно сегодня"
    static let numerologyColorLabel = "Цвет дня"
    static let numerologyStoneLabel = "Камень на поддержку"

    static let dayLayerEyebrow = "Твой ритм в Flow"
    static let dayLayerIntro =
        "Короткие строки из твоих отметок и контекста — рядом с картой дня, чтобы не искать это в другом месте."
    static let dayLayerNudgeLabel = "Ориентир"
    static let dayLayerWeeklyLabel = "Неделя"
    static let dayLayerDisciplineLabel = "Дисциплина дня"
    static let dayLayerQuestionLabel = "Мягкий вопрос"
    static let dayLayerContextLabel = "К решениям дня"

    static let deeperRoutesEyebrow = "Если нужна глубина"
    static let deeperRoutesSub =
        "Today показывает направление. Если есть конкретный вопрос — разбери его отдельно."
    static let deeperGuidanceTitle = "Проводник"
    static let deeperGuidanceBody =
        "Когда нужно выбрать, решить или понять, что делать дальше: открытые вопросы, работа, деньги, внутренний конфликт."
    static let deeperGuidanceCta = "Разобрать вопрос"
    static let deeperCompatibilityTitle = "Совместимость"
    static let deeperCompatibilityBody =
        "Когда вопрос связан с человеком, отношениями, притяжением или сексуальной динамикой."
    static let deeperCompatibilityCta = "Разобрать отношения"
    static let deeperPortraitTitle = "Портрет"
    static let deeperPortraitBody =
        "Обнови факты о себе — подсказки про любовь, деньги и сильные стороны будут ближе к жизни, а не к шаблону."
    static let deeperPortraitCta = "Обновить портрет"

    static let guidanceTitle = "Если хочется разобраться глубже"
    static let guidanceCta = "Открыть проводник"
    static let guidanceExamplePrefix = "Можно спросить так:"
    static let guidanceCompatEyebrow = "Если дальше про пару"
    static let guidanceLoveFollowup = "Если тема про любовь или отношения — после разбора можно зайти в совместимость и посмотреть вас как пару."
    static let guidanceWorkFollowup =
        "Если день про работу или деньги — задай вопрос в Проводнике своими словами: так проще получить следующий шаг, а не общую фразу."
    static let guidanceNeutralFollowup =
        "Сформулируй вопрос как тебе удобно — так Проводник даст шаг по живой теме, а не воду."
    static let compatibilityCta = "Совместимость"

    static let cardHonestStepQuestion = "Что сегодня больше всего похоже на твой честный шаг?"
    static let cardWhatMeansButton = "Что значит эта карта?"
    static let cardMeaningPopoverTitle = "Что значит эта карта?"
    static let cardMeaningAckCta = "Поняла"
    static let sheetCloseCta = "Закрыть"
    static let ritualCardNumberDetailTitle = "Карта и число"
    static let cardMeaningPopoverBody =
        "Карта задаёт тему дня: на что смотреть внимательнее, что не игнорировать и какой один шаг ближе всего к правде — без буквального «предсказания»."
    static let cardSaveFocus = "Сохранить как фокус дня"
    static let cardSaveFocusDone =
        "Сохранено. Фокус дня можно держать в голове или перенести в Flow как одну задачу."
    static let numberRhythmQuestion = "Сегодня тебе больше нужно:"
    static func spherePercentPrompt(score: Int, provisional: Bool = false) -> String {
        let n = min(100, max(0, score))
        let prefix = provisional ? "≈" : ""
        return "Что значит \(prefix)\(n)%?"
    }

    static let spherePercentExplainerTitle = "Про процент у сферы"
    static let spherePercentExplainerBody =
        "Это не предсказание и не «шанс события». Процент показывает, насколько сегодня комфортно действовать в теме с учётом твоего числа, отметок и карты, если она уже включена в разбор. Низкий процент — повод не спешить или выбрать вариант полегче, а не «нельзя»."
    static let focusPickStep = "Выбрать мой шаг"
    static let focusStart20 = "Начать 20 минут"
    static let focusStart20Hint =
        "Намерение записано: 20 минут на один понятный кусок. Таймер — как тебе удобно; главное — один слот без переключений."
    static let focusPickHint = "Что выберешь?"
    static let focusFallbackLine =
        "Закрой одну вещь, которая давно висит: письмо, решение, оплата, короткий разговор. Цель — не гнаться за образом «идеального дня», а убрать один висящий кусок с поля внимания."

    static let ritualOpenDay = "Открыть день"
    static let ritualDayAlreadyOpen = "День уже открыт"

    /// Паритет с `RITUAL_MOOD_LABELS` на вебе.
    static let moodLabels: [(id: String, label: String)] = [
        ("calm", "спокойно"),
        ("anxious", "тревожно"),
        ("tired", "устало"),
        ("driven", "в драйве"),
        ("motivated", "в драйве"),
        ("irritated", "раздражённо"),
        ("other", "другое"),
        ("confused", "неясно"),
        ("quiet_wish", "хочется тишины"),
        ("move_wish", "хочется движения"),
        ("heavy", "тяжело"),
        ("hopeful", "с надеждой"),
        ("distant", "на дистанции"),
    ]

    /// Паритет с `RITUAL_HEAD_TOPIC_CHIPS`.
    static let headTopicChips: [(id: String, label: String)] = [
        ("work", "работа"),
        ("money", "деньги"),
        ("relations", "отношения"),
        ("body", "тело / энергия"),
        ("family", "семья"),
        ("decision", "решение, которое надо принять"),
        ("none", "ничего конкретного"),
    ]

    static let cardHonestStepChips: [(id: String, label: String)] = [
        ("talk", "разговор"),
        ("work", "работа"),
        ("money", "деньги"),
        ("relations", "отношения"),
        ("body", "тело / энергия"),
        ("unknown", "пока не знаю"),
    ]

    static let numberRhythmChips: [(id: String, label: String)] = [
        ("gather", "собраться"),
        ("decide", "решиться"),
        ("rest", "отдохнуть"),
        ("talk", "поговорить"),
        ("steady", "не сорваться"),
    ]

    static let mainStepDomainChips: [(id: String, label: String)] = [
        ("work", "работа"),
        ("money", "деньги"),
        ("relations", "отношения"),
        ("body", "тело"),
        ("other", "другое"),
    ]

    struct EssentialDef: Identifiable, Hashable {
        let id: String
        let title: String
        let explanation: String
    }

    /// O6: паритет `isLowEnergyRitualMood` / `_LOW_ENERGY_RITUAL_MOODS` в `today_narrative.py`.
    static func isLowEnergyRitualMood(_ mood: String?) -> Bool {
        let m = (mood ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return m == "tired" || m == "heavy" || m == "quiet_wish"
    }

    /// Как `RITUAL_ESSENTIALS` + `essentialsForMood` на вебе (один список для любого настроения).
    static let essentialsDefault: [EssentialDef] = [
        .init(id: "water", title: "Вода", explanation: "Базовая норма за день — меньше путаешь жажду с раздражением."),
        .init(id: "movement", title: "Движение", explanation: "5–10 минут пройтись или размять спину."),
        .init(id: "pause", title: "Пауза", explanation: "Одна остановка без экрана — чтобы день не уехал на автопилоте."),
        .init(id: "focus20", title: "Фокус 20 минут", explanation: "Один слот без переключений на главное дело."),
    ]

    static func essentialsForMood(_ mood: String?) -> [EssentialDef] {
        _ = mood
        return essentialsDefault
    }

    static let tarotIdleHint = "Нажми, чтобы вытянуть карту"
    static let tarotGridLead = "Сконцентрируйся"
    static let tarotGridSub = "и выбери одну карту"
    static let tarotGridPickHint = "Выбирай ту, что откликается больше всего."
    static let tarotGridPickHintPrimary = "Выбирай ту, что откликается"
    static let tarotGridPickHintSecondary = "Правильного выбора не бывает."
    static let tarotGridPickFooter = "Прислушайся к первому импульсу."
    static let tarotRevealContinueCta = "Продолжить"
    static let tarotSkipAnimationCta = "Показать карту сразу"
    static let tarotBridgeToNumber = "Карта зафиксирована. Дальше — число дня."
    static let tarotAnimationTroubleHint = "Проблемы с анимацией?"
    static let tarotCommitWithoutRitualCta = "Зафиксировать карту без ритуала"
    static let checkInMoodMarkedTail = "— отмечено"
    static let numberDaySubPick = "Выбери число от 1 до 6"
    static let numberDayEnergyInfo = "Число — это энергия дня. Оно подскажет твой ритм и фокус."
    static let numberCircleHint = "Интуитивно выбери своё число"
    static let moodCheckSub = "Это поможет сделать разбор точнее."

    /// Сетка 2×3 как на макете (id совпадают с веб `RITUAL_MOOD_GRID`).
    static let moodGridMockup: [(id: String, label: String, systemImage: String)] = [
        ("calm", "Спокойно", "heart"),
        ("anxious", "Тревожно", "cloud"),
        ("tired", "Устало", "battery.100"),
        ("driven", "В драйве", "flame"),
        ("irritated", "Раздражённо", "bolt.fill"),
        ("other", "Другое", "ellipsis"),
    ]

    static func anchorTarotTags(from leadRu: String) -> [String] {
        leadRu.split { ",;.".contains($0) }
            .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { $0.count > 2 && $0.count < 38 }
            .prefix(3)
            .map { String($0) }
    }

    /// Паритет с веб `numberDayTagTriad`.
    static func numberDayTagTriad(numerologyValue: String) -> [String] {
        let d = String(numerologyValue.filter(\.isNumber).suffix(1))
        let digit = d.isEmpty ? "1" : d
        let pool: [String: [String]] = [
            "1": ["Старт", "Ясность", "Инициатива"],
            "2": ["Партнёрство", "Такт", "Баланс"],
            "3": ["Общение", "Идеи", "Лёгкость"],
            "4": ["Опора", "Порядок", "Шаг"],
            "5": ["Смена", "Импульс", "Гибкость"],
            "6": ["Забота", "Близость", "Гармония"],
            "7": ["Тишина", "Анализ", "Глубина"],
            "8": ["Ресурс", "Результат", "Границы"],
            "9": ["Завершение", "Смысл", "Отпускание"],
        ]
        return pool[digit] ?? pool["1"]!
    }

    /// Строка над «Твой день»: дата · Утро|День|Вечер (локальное время устройства).
    static func ritualEntryEyebrow(displayDate: String, now: Date = Date()) -> String {
        let slot = TodayRitualEntryIllustration.timeSlot(for: now)
        let word: String
        switch slot {
        case "morning": word = "Утро"
        case "day": word = "День"
        default: word = "Вечер"
        }
        return "\(displayDate) · \(word)"
    }
}

/// Паритет `frontend/src/lib/ruUserGender.ts` — согласование «ты» по полу из профиля (когда появится в API).
enum RuUserDeclension {
    case feminine
    case masculine
    case unspecified

    static func parse(_ raw: String?) -> RuUserDeclension {
        guard let t = raw?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased(), !t.isEmpty else {
            return .unspecified
        }
        if ["f", "female", "feminine", "woman", "ж", "женский", "женщина"].contains(t) || t.hasPrefix("жен") {
            return .feminine
        }
        if ["m", "male", "masculine", "man", "м", "мужской", "мужчина"].contains(t) || t.hasPrefix("муж") {
            return .masculine
        }
        return .unspecified
    }

    /// Заголовок блока «чего не дожимать» — при известном поле профиля подставляй вместо `TodayRitualCopy.avoidHeading`.
    static func ritualAvoidHeading(_ d: RuUserDeclension) -> String {
        switch d {
        case .feminine:
            return "Чего бы сегодня не дожимала"
        case .masculine:
            return "Чего бы сегодня не дожимал"
        case .unspecified:
            return TodayRitualCopy.avoidHeading
        }
    }
}

/// Паритет `frontend/src/components/today/todayRitualCopy.ts` → `TODAY_SHELL_COPY` (оболочка `TodayView`).
enum TodayShellCopy {
    static let meaningRingsSectionTitle = "Опоры недели"
    static let guidePanelIntroTitle = "Сначала — суть дня"
    static let guidePanelIntroBody =
        "Ниже главное сообщение дня. Детали про шаги и карту открой, когда захочешь углубиться — без перегруза одним экраном."
    static let guideStepTwoDisclosureLabel = "Действия и карта дня"
    static let guideStepThreeDisclosureLabel = "Ритм, профиль и сферы"
    static let morningPanelIntroTitle = "Утро — намерение"
    static let morningPanelIntroBody =
        "Спокойный вход в день. Карту, число и разбор открой ниже, когда тебе будет удобно."
    static let morningStepTwoDisclosureLabel = "Карта, число и ядро дня"
    static let dayPanelIntroTitle = "День — шаг и сигнал"
    static let dayPanelIntroBody = "Сначала суть и что сделать. Подробности — в раскрытии ниже."
    static let dayStepTwoDisclosureLabel = "Дополнительные блоки и вопросы дня"
    static let eveningPanelIntroTitle = "Вечер — закрытие"
    static let eveningPanelIntroBody =
        "Коротко зафиксируй день. Дополнительные вопросы — по раскрытию, когда захочешь."
    static let eveningStepTwoDisclosureLabel = "Дополнительные вечерние вопросы"
    static let lifeSpheresSectionTitle = "Сферы жизни сегодня"
    static let lifeSpheresSubtitle =
        "По четырём темам видно, где сегодня легче продвинуться, где лучше не давить и где стоит просто не мешать себе."
    static let nextStepWhyFallback =
        "Мягко перевести день в первый осознанный шаг — без давления и без лишних задач."
    static let guideHeroEyebrow = "Суть дня"
    static let loadingGuideHero = "Собираю разбор дня…"
    static let loadingMorningNarrative = "Собираю подсказки на день…"
    static let loadingDayNarrative = "Собираю блок про день…"
    static let loadingEveningNarrative = "Собираю вечерний итог…"
    static let narrativeFallbackMorning =
        "Утренний текст подскажет, куда вложить внимание сегодня — не только настроение."
    static let narrativeFallbackEvening =
        "Короткий вечерний итог помогает честнее закрыть день и лучше стартовать завтра."
    static let guideEnergyLineFallback = "Строка про энергию станет яснее после вечерней отметки."
    static let profileTileTitle = "Базовый темп"
    static let profileTileCaption =
        "Солнце, Луна и асцендент — ориентир, как ты обычно реагируешь и восстанавливаешься."
    static let weekRhythmCalendarSubtitle =
        "Календарь показывает день внутри недели и где уже стоят отметки утра, дня и вечера."
    static let weekRhythmSummaryTail = "Чем стабильнее отметки, тем полезнее ориентиры на ближайшие дни."

    // iOS `TodayView` — паритет `TODAY_SHELL_COPY.shell*` в `todayRitualCopy.ts`
    static let shellToolbarOpenProfileSummary = "Открыть Profile Summary"
    static let shellToolbarRefresh = "Обновить"
    static let shellNativeStepGuideTitle = "Today"
    static let shellNativeStepMorningTitle = "Фокус"
    static let shellNativeStepDayTitle = "Состояние"
    static let shellNativeStepEveningTitle = "Рефлексия"
    static let shellNativeStepGuideSubtitle = "Вход в день"
    static let shellNativeStepMorningSubtitle = "Намерение"
    static let shellNativeStepDaySubtitle = "Сигналы"
    static let shellNativeStepEveningSubtitle = "Закрытие"
    static let shellHeroDoNotEnterTitle = "Не входить"
    static let shellHeroFirstMoveFallback = "Собери день вокруг одного устойчивого движения"
    static let shellHeroAvoidFallback = "Не усиливай лишний шум и второстепенные темы"
    static let shellHeroSignalDayTitle = "Сигнал дня"
    static let shellHeroOverviewCollapse = "Свернуть обзор"
    static let shellHeroOverviewExpand = "Обзор дня: уровень, метрики и опоры"
    static let shellHeroOverviewA11yCollapse = "Свернуть обзор дня"
    static let shellHeroOverviewA11yExpand = "Показать полный обзор дня с уровнем и метриками"
    static let shellHeroChipSun = "Солнце"
    static let shellHeroChipMoon = "Луна"
    static let shellHeroChipAscendant = "Асцендент"
    static let shellHeroHeadlineFallback = "Сначала собери себя, потом собери день"
    static let shellHeroSubheadlineFallback =
        "Главный экран должен не перегружать, а быстро вводить тебя в правильный ритм дня."
    static let shellYourLevelLabel = "Твой уровень"
    static let shellTarotCardPreparing = "Карта дня готовится"
    static let shellGuideDayAxisTitle = "Ось дня"
    static let shellGuideDayAxisFallback = "Собирай день вокруг одной оси, а не вокруг случайных импульсов."
    static let shellGuideSupportsTitle = "Поддержит"
    static let shellGuideSupportsFallback = "Выбирать одно движение, которое действительно держит тебя."
    static let shellNumerologyGathering = "Число дня ещё собирается"
    static let shellNextStepSectionTitle = "Следующий шаг"
    static let shellNextStepDoTitle = "Что сделать сейчас"
    static let shellNextStepWhyTitle = "Почему это важно"
    static let shellNextStepActionFallback = "Открой утро и зафиксируй одно намерение."
    static let shellFitSectionTitle = "Как этот день ложится на тебя"
    static let shellFitStrongerAxisLabel = "Сильнее"
    static let shellFitBestModeTitle = "Лучший режим"
    static let shellFitBestModeFallback = "День лучше раскрывать из ровного темпа, а не из рывка."
    static let shellFitFragileAxisTitle = "Хрупкая ось"
    static let shellFitLeadFallback =
        "Слой guide должен объяснять день через твой собственный ритм, а не как универсальный прогноз."
    static let shellFitWeakAxisRiskFallback = "Пока данных мало. Отметь утро и один шаг днём, чтобы риск уточнился."
    static let shellNarrativeHeroEnergyTitle = "Энергия"
    static let shellNarrativeHeroRiskTitle = "Риск"
    static let shellNarrativeHeroRiskFallback = "Главный риск дня станет яснее после первых сигналов."
    static let shellNarrativeHeadlineFallback = "Собери день вокруг одной правильной оси"
    static let shellNarrativeSublineFallback = "Сначала вход в день, потом глубина. Не наоборот."
    static let shellExecutionFocusHeading = "На чем держать фокус сегодня"
    static let shellExecutionAvoidHeading = "Чего избегать сегодня"
    static let shellExecutionDoFallback1 = "Доведи до конца то, что уже в работе."
    static let shellExecutionDoFallback2 = "Упрости коммуникацию: коротко и по делу."
    static let shellExecutionDoFallback3 = "Сдвинь вперёд одно важное дело."
    static let shellExecutionAvoidFallback1 = "Не разжигай конфликты."
    static let shellExecutionAvoidFallback2 = "Не перегружай себя обязательствами."
    static let shellTarotResonanceTitle = "Отклик"
    static let shellTarotResonancePartial = "Частично"
    static let shellTarotResonanceSaved = "Сохранено"
    static let shellListDoTitle = "Что сделать"
    static let shellListAvoidTitle = "Чего избегать"
    static let shellListDoFallback = "Собери день вокруг одного полезного действия."
    static let shellListAvoidFallback = "Не усиливай вторичный шум и лишнее напряжение."
    static let shellDayProgressHeading = "Прогресс дня"
    static let shellDayProgressStepDone = "Готово"
    static let shellDayProgressStepNext = "Следующий шаг"
    static let shellProgressPhaseTodayComplete = "Today"
    static let shellSphereForecastCollapse = "Свернуть прогноз сферы"
    static let shellSphereForecastExpand = "Открыть прогноз сферы"
    static let shellSphereLoveTitle = "Любовь"
    static let shellSphereLoveFallback = "Здесь появится короткий прогноз по отношениям на сегодня."
    static let shellSphereMoneyTitle = "Деньги"
    static let shellSphereMoneyFallback = "Сюда подтягивается практическая линия решений и ресурса."
    static let shellSphereWorkTitle = "Работа"
    static let shellSphereWorkFallback = "Сюда должен прийти рабочий фокус дня."
    static let shellSphereFamilyTitle = "Семья"
    static let shellSphereFamilyFallback = "Этот блок показывает, как сегодня может чувствоваться общение дома."
    static let shellMorningDayModeTitle = "Режим дня"
    static let shellMorningDayModeFallback = "Ровный собранный ритм"
    static let shellMorningDayModeCaption = "Тон, в котором день лучше раскрывается"
    static let shellMorningNarrativeHeadlineFallback = "Подсказки на день"
    static let shellProfileBuilding = "Профиль ещё собирается"
    static let shellEveningClosingToneTitle = "Тон закрытия"
    static let shellEveningNarrativeHeadlineFallback = "Вечер"
    static let shellEveningMorningLinkTitle = "Связь с утром"
    static let shellMorningCoreTitle = "Ядро дня"
    static let shellTarotCardDayTitle = "Карта дня"
    static let shellCoreGathering = "Собирается"
    static let shellTarotCardCaption = "Символ дня"
    static let shellNumerologyDayTitle = "Число дня"
    static let shellNumerologyCaption = "Числовой акцент дня"
    static let shellForecastShortTitle = "Коротко про день"
    static let shellWhatSupportsDayTitle = "Что поддержит день"
    static let shellWhatSupportsFallback = "Один ясный первый шаг."
    static let shellWhatNotAmplifyTitle = "Что не усиливать"
    static let shellWhatNotAmplifyFallback = "Не расширяй шум и вторичные задачи."
    static let shellTarotDaySectionTitle = "Таро дня"
    static let shellTarotAgainCta = "Ещё раз"
    static let shellTarotA11yClosedCard = "Закрытая карта"
    static let shellTarotPickCardHint = "Выбери карту"
    static let shellEnergyStateSectionTitle = "Энергия и состояние"
    static let shellEnergySignatureEmpty =
        "Покажем красивую карту энергии, как только появится первый живой сигнал дня."
    static let shellFusionOrbEnergy = "Энергия"
    static let shellFusionOrbBalance = "Баланс"
    static let shellFusionOrbFocus = "Фокус"
    static let shellWeekRhythmTitle = "Ритм недели"
    static let shellWeekCalendarFootnoteActive =
        "Точки под датой показывают, какие части дня уже прожиты и зафиксированы."
    static let shellWeekCalendarFootnoteInactive =
        "Когда ты начнешь отмечать утро, день и вечер, картина недели станет заметно яснее."
    static let shellTrendInsightTitle = "Что уже видно по твоим отметкам"
    static let shellTrendLineTrend = "Тренд"
    static let shellTrendLineRisk = "Риск"
    static let shellTrendLineCorrelation = "Корреляция"
    static let shellWorkingLayerDayStepTitle = "Шаг дня"
    static let shellWorkingLayerOpeningFallback = "Выбери один рабочий фокус и одно ограничение на день."
    static let shellNextActionCardTitle = "Следующий шаг"
    static let shellNextActionFallback = "Зафиксируй состояние и одно следующее действие."
    static let shellCriticalLimitTitle = "Критический лимит"
    static let shellCriticalLimitFallback = "Не пытайся раскрыть весь день за один раз."
    static let shellActionPlanTitle = "План дня"
    static let shellDayDetailsHeading = "Вопросы и рабочие блоки"
    static let shellQuestionOfDayCardTitle = "Вопрос дня"
    static let shellPersonalInsightTitleFallback = "Личный инсайт"
    static let shellWeeklyFocusTitle = "Недельный фокус"
    static let shellDisciplineTitle = "Дисциплина"
    static let shellNudgeHintTitle = "Подсказка"
    static let shellEveningDetailsHeading = "Вечерние вопросы"
    static let shellEveningMainQuestionTitle = "Основной вопрос"
    static let shellEveningBeforeCloseTitle = "Перед закрытием"
    static let shellEveningWhatWeCaptureTitle = "Что фиксируем"
    static let shellDayEnergyRibbonTitle = "Энергия дня"
    static let shellDayEnergyRibbonSubtitle = "Три шкалы: энергия, баланс и фокус."
    static let shellRecentJournalTitle = "Последние записи"
    static let shellYourFocusTitle = "Твой фокус"
    static let shellMarkProgressCta = "Отметить прогресс"
    static let shellAddGoalHint = "Добавь цель, чтобы отметить по ней шаг сегодня."
    static let shellGoalHintStrongDay = "Сегодня удачный день, чтобы сдвинуться вперёд."
    static let shellGoalHintCarefulDay = "Не лучший день для рискованных шагов. Держи шаг маленьким и ясным."
    static let shellLoadStateIdle = "Ожидание"
    static let shellLoadStateLoading = "Собираем день"
    static let shellLoadStateDone = "Готово"
    static let shellFallbackPanelTitle = "Экран дня загружается"
    static let shellFallbackPanelLoadingBody = "Загружаю день и собираю все блоки."
    static let shellFallbackPanelStaleHint = "Данные еще загружаются. Нажми «Обновить экран дня»."
    static let shellFallbackRefreshScreenCta = "Обновить экран дня"

    static func formatYourLevelDetail(tierTitle: String) -> String {
        "\(shellYourLevelLabel): \(tierTitle)"
    }

    static func formatDayProgressBullets(percent: Int, completed: Int, total: Int) -> String {
        "\(percent)% • \(completed) \(TodayWebGuideSectionCopy.guideDayProgressOutOf) \(total) шагов"
    }

    static func formatNumerologyValue(_ value: CustomStringConvertible) -> String {
        "Число \(value)"
    }

    static func formatMorningIntentionRecall(intention: String) -> String {
        "Утром ты задал: “\(intention)”"
    }

    static func formatWeakAxisLine(weakestAxisTitle: String, base: String) -> String {
        "\(weakestAxisTitle) сейчас требует бережности. \(base)"
    }

    static func formatTarotDayLine(cardName: String) -> String {
        "\(shellTarotCardDayTitle): \(cardName)"
    }

    static func formatTarotA11yOpenCard(cardName: String) -> String {
        "Открытая карта \(cardName)"
    }
}

// MARK: - RITUAL_COPY: веб Guide / Working layer / Quick actions
// Паритет `frontend/src/components/today/todayRitualCopy.ts` — `TodayGuideSection`, `TodayWorkingLayerSection`, `TodayQuickActions`.

enum TodayWebQuickActionsCopy {
    static let quickStateCheckNeedScaleOrNote = "Выбери хотя бы шкалу или короткую заметку"
    static let quickStateCheckSavedToast = "Состояние сохранено"
    static let quickStateCheckSaveErrorToast = "Не удалось сохранить состояние. Попробуй еще раз."
    static let quickStateCheckLoading = "Загрузка состояния…"
    static let quickStateCheckMoodLabel = "Настроение (1–5)"
    static let quickStateCheckEnergyLabel = "Энергия (1–5)"
    static let quickStateCheckStressLabel = "Стресс (1–5, выше — сильнее)"
    static let quickStateCheckNotePlaceholder = "Одна строка — что чувствуешь сейчас"
    static let quickStateCheckSaveCta = "Сохранить состояние"
    static let quickStateCheckSavingCta = "Сохраняю…"
    static let quickJournalEntryErrorToast = "Ошибка при сохранении записи"
    static let quickJournalOpenCta = "✍️ Записать в дневник"
    static let quickJournalTabObservation = "👁️ Наблюдение"
    static let quickJournalTabGratitude = "🙏 Благодарность"
    static let quickJournalTabInsight = "💡 Вывод"
    static let quickJournalPlaceholderObservation = "Что ты заметил сегодня?"
    static let quickJournalPlaceholderGratitude = "За что ты благодарен?"
    static let quickJournalPlaceholderInsight = "Какой вывод ты сделал?"
    static let formSaveCta = "Сохранить"
    static let formCancelCta = "Отмена"
    static let formSavingShort = "Сохранение..."
    static let quickTrackerEntryErrorToast = "Ошибка при сохранении состояния"
    static let quickTrackerOpenCta = "📍 Отметить состояние"
    static let quickTrackerHowYouFeelPrompt = "Как ты себя чувствуешь?"
    static let quickTrackerNotePlaceholder = "Коротко опиши своё состояние..."
}

enum TodayWebGuideSectionCopy {
    static let guidePanelEyebrowToday = "Сегодня"
    static let guideNarrativeRefiningLine = "Уточняем формулировку дня…"
    static let guideWhyTodayCta = "Почему сегодня?"
    /// O9: главный CTA героя guide → вкладка «День» (паритет `RITUAL_COPY.guidePrimaryNavigateCta` на вебе).
    static let guidePrimaryNavigateCta = "К шагу дня"
    static let guideEmotionalRingsSectionTitle = "Сферы в кольцах"
    static let guideOpenSphereForDetailHint = "Чувствуешь блок? Открой сферу и посмотри подробный разбор."
    static let guideWhatToDoTodayTitle = "Что сделать сегодня"
    static let guidePrimaryDoFallback = "Сделай один короткий шаг по главному фокусу."
    static let guideOpenDayStepCta = "Открыть шаг дня"
    static let guideShortQuestionAboutYouTitle = "Короткий вопрос о тебе"
    static let guideMiniPlanTitle = "Мини-план"
    static let guideMiniFlowWater = "Вода"
    static let guideMiniFlowMovement = "Движение"
    static let guideMiniFlowReflection = "Рефлексия"
    static let guideMiniFlowFocusSession = "Фокус-сессия"
    static let guideOpenFullCalendarCta = "Открыть полный план дня"
    static let guideDayProgressIntro = "Прогресс дня:"
    static let guideDayProgressOutOf = "из"
    static let guideEmotionalTriggersTitle = "Эмоциональные триггеры"
    static let guideTriggerDayCard = "Карта дня"
    static let guideTriggerRelationshipEnergy = "Энергия отношений"
    static let guideTriggerQuickDiary = "Быстрый дневник"
    static let guideShowDayDetailsSummary = "Показать детали дня"
    static let guideDetailEnergyPrefix = "Энергия:"
    static let guideDetailFocusPrefix = "Фокус:"
    static let guideDetailRiskPrefix = "Риск:"
    static let guideDetailMoonPrefix = "Луна:"
    static let guideEmotionalRingLove = "Любовь"
    static let guideEmotionalRingFocus = "Фокус"
    static let guideEmotionalRingMoney = "Деньги"
    static let guideEmotionalRingState = "Состояние"

    static func formatDayProgressLine(percent: Int, completed: Int, total: Int) -> String {
        "\(guideDayProgressIntro) \(percent)% (\(completed) \(guideDayProgressOutOf) \(total))"
    }
}

enum TodayWebWorkingLayerCopy {
    static let workingLayerDayStepLoading = "Готовим шаг дня…"
    static let workingLayerNudgeRecsSummary = "Что поможет"
    static let workingLayerExtraStepTitle = "Добавить ещё один шаг?"
    static let workingLayerExtraStepLead = "Добавляешь ещё один шаг сегодня?"
    static let workingLayerExtraStepCaptionPrefix = "На сегодня:"
    static let workingLayerQuickDecisionYes = "Да, добавляю"
    static let workingLayerQuickDecisionNo = "Нет, оставлю так"
    static let workingLayerQuickDecisionUnclear = "Пока не решил(а)"
    static let workingLayerHintSummary = "Подсказка"
    static let workingLayerDecisionAckYes = "Хорошо. Добавь только шаг по главному фокусу."
    static let workingLayerDecisionAckNo = "Отлично. Так ты сохраняешь энергию для главного."
    static let workingLayerDecisionAckUnclear = "Нормально. Сделай паузу и вернись позже."
    static let workingLayerRingImpactDecisionDefault = "Каждый такой ответ помогает точнее подбирать подсказки."
    static let workingLayerRingImpactDecisionYes = "Отлично. Такой выбор обычно помогает быстрее продвигаться в делах."
    static let workingLayerRingImpactDecisionNo = "Отлично. Так ты бережешь силы и не перегружаешь день."
    static let workingLayerRingImpactDecisionUnclear = "Нормально. Честная фиксация состояния уже полезна."
    static let workingLayerRingImpactQuestionDefault = "Ответы на короткие вопросы помогают лучше подбирать рекомендации."
    static let workingLayerRingImpactQuestionLove = "Принято: для тебя сейчас важнее контакт и поддержка."
    static let workingLayerRingImpactQuestionMotion = "Принято: тебе лучше заходят короткие действия и движение."
    static let workingLayerRingImpactQuestionQuiet = "Принято: тебе нужен более спокойный и бережный режим."
    static let workingLayerRingImpactQuestionFallback = "Принято: учту это в следующих подсказках."
    /// Компактный блок «быстрый ответ» в `TodayView` (паритет `RITUAL_COPY` в `todayRitualCopy.ts`).
    static let workingLayerQuickDecisionSaving = "Сохраняю..."
    static let workingLayerQuickDecisionSaveCta = "Сохранить быстрый ответ"
    static let workingLayerQuickDecisionSavedBannerPrefix = "Последний быстрый ответ: "
    static let workingLayerQuestionOfDaySavedContextPrefix = "Текущий контекст: "
    /// Компактный блок «Быстрый ответ» в `TodayView` (`TodayQuickAnswerSection`).
    static let workingLayerCompactQuickAnswerEyebrow = "Быстрый ответ"
    static let workingLayerCompactQuickAnswerTitle = "Спроси о своей ситуации"
    static let workingLayerCompactQuickAnswerSubtitle =
        "Быстрый ответ нужен не для длинной консультации, а чтобы снять неопределенность и собрать контекст."
    static let workingLayerCompactQuickAnswerToneLabel = "Выбери тон ответа"
    static let workingLayerCompactQuickAnswerYes = "Да"
    static let workingLayerCompactQuickAnswerNo = "Нет"
    static let workingLayerCompactQuickAnswerUnclear = "Неясно"
    static let workingLayerCompactQuickAnswerContextLabel = "Это про отношения или работу?"
    static let workingLayerCompactQuickAnswerContextRelationships = "Отношения"
    static let workingLayerCompactQuickAnswerContextWork = "Работа"
    static let workingLayerCompactQuickAnswerSuccessStatus =
        "Быстрый ответ сохранен. Следующие подсказки станут точнее по твоему контексту."
    static let workingLayerPracticeTitle = "Практика дня"
    static let workingLayerPracticeSubtitle = "Один короткий шаг с таймером."
    static let workingLayerPracticeChip = "практика"
    static let workingLayerPracticeDurationHintPrefix = "Ориентир по времени: ~"
    static let workingLayerPracticeDurationHintSuffix = " мин"
    static let workingLayerTimerPauseWord = "Пауза"
    static let workingLayerTimerStartWord = "Старт"
    static let workingLayerPracticeMarkDone = "Отметить выполнение"
    static let workingLayerPracticeCompleting = "…"
    static let workingLayerPracticeDone = "Готово"
    static let workingLayerTimerReset = "Сбросить таймер"
    static let workingLayerPracticeMissing = "Практика не выбрана. Добавь одну на сегодня."
    static let workingLayerPracticeCatalogCta = "Каталог практик"
    static let workingLayerWeeklyFocusTitle = "Фокус недели"
    static let workingLayerWeeklyFocusSubtitle = "Удержи один приоритет и один шаг."
    static let workingLayerWeeklyFocusChip = "фокус"
    static let workingLayerWeeklyGoalUnset = "Ещё не задан"
    static let workingLayerWeeklyGoalClosed = "Фокус уже закрыт. Можно поставить следующий."
    static let workingLayerWeeklyGoalInProgress = "Фокус уже в работе. Если сегодня шага ещё не было, отметь один."
    static let workingLayerWeeklyGoalHasFocus = "Фокус уже есть. Закрепи его сегодня одним небольшим шагом."
    static let workingLayerWeeklyGoalEmpty = "Зафиксируй один недельный фокус прямо отсюда."
    static let workingLayerQuickAddTitle = "Добавить на месте"
    static let workingLayerEntityGoal = "Цель"
    static let workingLayerEntityHabit = "Привычка"
    static let workingLayerEntityAscetic = "Аскеза"
    static let workingLayerWizardOpensOverlay = "Откроется поверх этого экрана."
    static let workingLayerDailyTrailTitle = "След дня"
    static let workingLayerUnderstandYouTitle = "Понять тебя точнее"
    static let workingLayerUnderstandYouSubtitle = "Пара коротких ответов для более точных рекомендаций."
    static let workingLayerOptionalChip = "по желанию"
    static let workingLayerWeeklyStateMapTitle = "Недельная карта состояния"
    static let workingLayerWeeklyStateMapBody =
        "Сравниваем отметки состояния и дневник, чтобы понять, что улучшает или ухудшает неделю."
    static let workingLayerTrendUp = "тренд вверх"
    static let workingLayerTrendDown = "тренд вниз"
    static let workingLayerTrendFlat = "стабильно"
    static let workingLayerAvgStateLabel = "Среднее состояние"
    static let workingLayerTrackedDaysLabel = "Дней с отметками"
    static let workingLayerJournalDaysLabel = "Дней с дневником"
    static let workingLayerInsufficientData = "недостаточно данных"
    static let workingLayerRecommendationPrefix = "Рекомендация:"

    static func formatPracticeDurationHint(minutes: Int) -> String {
        "\(workingLayerPracticeDurationHintPrefix)\(minutes)\(workingLayerPracticeDurationHintSuffix)"
    }

    static func formatMiniDecisionCaption(_ caption: String) -> String {
        "\(workingLayerExtraStepCaptionPrefix) \(caption)"
    }

    static func formatWeeklyPatternRecommendation(_ recommendation: String) -> String {
        "\(workingLayerRecommendationPrefix) \(recommendation)"
    }

    static func formatTimerButton(mode: TimerButtonMode, formattedTime: String) -> String {
        let word = mode == .pause ? workingLayerTimerPauseWord : workingLayerTimerStartWord
        return "\(word) \(formattedTime)"
    }

    static func ringImpactForDecision(_ answer: String?) -> String {
        switch answer {
        case "yes": return workingLayerRingImpactDecisionYes
        case "no": return workingLayerRingImpactDecisionNo
        case "unclear": return workingLayerRingImpactDecisionUnclear
        default: return workingLayerRingImpactDecisionDefault
        }
    }

    static func ringImpactForQuestion(optionId: String?) -> String {
        let key = (optionId ?? "").lowercased()
        if key.isEmpty { return workingLayerRingImpactQuestionDefault }
        if key.contains("people") || key.contains("love") { return workingLayerRingImpactQuestionLove }
        if key.contains("step") || key.contains("motion") { return workingLayerRingImpactQuestionMotion }
        if key.contains("quiet") || key.contains("boundary") { return workingLayerRingImpactQuestionQuiet }
        return workingLayerRingImpactQuestionFallback
    }

    enum TimerButtonMode {
        case pause
        case start
    }
}

/// Паритет `RITUAL_QUESTION_OF_DAY_*` / `buildRitualQuestionOfDayDefaultCards` в `todayRitualCopy.ts` и `buildQuestionOfDay` в `todayPageUtils.ts`.
enum TodayWebQuestionOfDayCopy {
    struct Card: Equatable {
        let prompt: String
        let options: [Option]

        struct Option: Equatable {
            let id: String
            let label: String
            let response: String
        }
    }

    static let lowEnergyCards: [Card] = [
        Card(
            prompt: "Когда сил мало, что чаще всего помогает тебе удержаться?",
            options: [
                .init(id: "restore_boundary", label: "пауза и границы", response: "Зафиксировали: опора через паузу и бережные границы."),
                .init(
                    id: "tiny_step",
                    label: "один конкретный шаг",
                    response: "Записано: для тебя сейчас лучше срабатывает один полностью завершённый фрагмент дела."
                ),
                .init(id: "people_warmth", label: "теплый контакт", response: "Зафиксировали: ресурс возвращают люди и поддержка."),
                .init(id: "unclear_low", label: "по-разному, зависит от дня", response: "Отметили вариативность. Будем точнее подбирать формат опоры."),
            ]
        ),
        Card(
            prompt: "Что чаще всего ухудшает твое состояние в такие дни?",
            options: [
                .init(id: "noise_overload", label: "шум и перегруз стимулами", response: "Принято. Добавим акцент на тихие окна и паузы."),
                .init(id: "unclear_tasks", label: "непонятные задачи", response: "Принято. Усилим рекомендацию на один ясный шаг."),
                .init(id: "people_pressure", label: "давление от общения", response: "Принято. Учтем границы в социальных сценариях."),
                .init(id: "late_sleep", label: "сбитый сон и режим", response: "Принято. Будем чаще предлагать бережный вечерний ритуал."),
            ]
        ),
    ]

    static func defaultCards(lowFocus: Bool) -> [Card] {
        let third: Card =
            lowFocus
                ? Card(
                    prompt: "Что чаще всего мешает держать фокус?",
                    options: [
                        .init(id: "focus_notifications", label: "уведомления и отвлечения", response: "Учли: добавим рекомендации по защите фокуса."),
                        .init(id: "focus_anxiety", label: "внутреннее напряжение", response: "Учли: добавим бережные антистресс-шаги."),
                        .init(id: "focus_unclear_priority", label: "нет одного приоритета", response: "Учли: усилим блок с одним главным шагом."),
                        .init(id: "focus_fatigue", label: "усталость к середине дня", response: "Учли: чаще предложим восстановление перед задачами."),
                    ]
                )
                : Card(
                    prompt: "Что сегодня важнее всего продвинуть?",
                    options: [
                        .init(id: "priority_money", label: "деньги и работа", response: "Принято. Усилю прикладные шаги по деньгам и задачам."),
                        .init(id: "priority_relationships", label: "отношения и коммуникация", response: "Принято. Усилю рекомендации по общению и границам."),
                        .init(id: "priority_health", label: "состояние и энергия", response: "Принято. Усилю восстановительный контур дня."),
                        .init(id: "priority_self", label: "я и внутренний порядок", response: "Принято. Предложу более спокойный и сфокусированный ритм."),
                    ]
                )

        return [
            Card(
                prompt: "Что сейчас лучше всего помогает тебе восстанавливаться?",
                options: [
                    .init(id: "rhythm_home", label: "ритм, дом, бытовая опора", response: "Зафиксировали: опора в устойчивом ритме и простых действиях."),
                    .init(id: "people_exchange", label: "люди и живой обмен", response: "Зафиксировали: тебе помогает контакт и диалог."),
                    .init(id: "quiet_depth", label: "тишина и глубокий фокус", response: "Зафиксировали: тебе нужен тихий режим и глубина."),
                    .init(id: "motion_change", label: "движение и смена обстановки", response: "Зафиксировали: ресурс приходит через движение и новизну."),
                ]
            ),
            Card(
                prompt: "Какой формат рекомендаций тебе удобнее сегодня?",
                options: [
                    .init(id: "format_short", label: "очень коротко: 1-2 пункта", response: "Принято. Дадим более компактные подсказки."),
                    .init(id: "format_structured", label: "структурно: что/почему/как", response: "Принято. Дадим рекомендации в структурном формате."),
                    .init(id: "format_emotional", label: "через смысл и поддержку", response: "Принято. Усилим эмоциональную часть рекомендаций."),
                    .init(id: "format_action", label: "только действия без лишнего", response: "Принято. Приоритет на прикладные шаги."),
                ]
            ),
            third,
        ]
    }

    /// Детерминированный выбор карточки по дате (как `buildQuestionOfDay` на вебе).
    static func build(lowEnergy: Bool, lowFocus: Bool, dateIso: String?) -> Card {
        let seedSource: String = {
            if let d = dateIso, !d.isEmpty { return d }
            let f = DateFormatter()
            f.calendar = Calendar(identifier: .gregorian)
            f.locale = Locale(identifier: "en_US_POSIX")
            f.timeZone = TimeZone(secondsFromGMT: 0)
            f.dateFormat = "yyyy-MM-dd"
            return f.string(from: Date())
        }()

        let seed = seedSource.split(separator: "-").reduce(0) { acc, part in
            acc + (Int(part) ?? 0)
        }

        let pool: [Card] = lowEnergy ? lowEnergyCards : defaultCards(lowFocus: lowFocus)
        guard !pool.isEmpty else {
            return Card(prompt: "", options: [])
        }
        let idx = abs(seed) % pool.count
        return pool[idx]
    }
}

// MARK: - RITUAL_COPY: сферы жизни на `/today` и хром секций
// Паритет `TodayLifeSpheresSection.tsx`, `TodaySectionPrimitives.tsx`.

enum TodayWebLifeSpheresCopy {
    static let lifeSpheresDeepenFallbackBody = "Текст пока не готов."
    static let lifeSpheresDeepenLoadError = "Не удалось загрузить текст. Попробуй еще раз."
    static let lifeSpheresMorningRefreshHint = "Сферы дня загружаются. Открой «Утро» и нажми «Обновить день»."
    static let lifeSpheresHubTitle = "Сферы дня: что происходит и что делать"
    static let lifeSpheresHubLead = "Выбери 1 сферу с наибольшим напряжением и сделай один шаг."
    static let lifeSpheresScenarioTitleFallback = "Тема"
    static let lifeSpheresFocusLineFallback = "Открыть чтобы посмотреть прогноз сферы"
    static let lifeSpheresDeepenLoading = "Загрузка…"
    static let lifeSpheresDeepenRefreshWhyCta = "Обновить почему"
    static let lifeSpheresDeepenWhyCta = "Почему это важно"
    static let lifeSpheresScenarioActionCta = "Что делать"
    static let lifeSpheresLoveDeepCompatibilityHint = "Для глубокой проверки связи используй экран Совместимость."
}

enum TodayWebSectionChromeCopy {
    static let todayUiCollapseCta = "Свернуть"
    static let todayUiExpandCta = "Развернуть"
    static let todayUiOpenCta = "Открыть"
    static let daySectionHeaderHintWhenDone = "Блок уже заполнен, но его можно дополнять в любой момент."
    static let daySectionHeaderHintNextStep = "Открой этот блок, когда будешь готов(а) к следующему шагу дня."
}

// MARK: - RITUAL_COPY: этапы дня на `/today` (утро / день / вечер / табы)
// Паритет `TodayDaySection`, `TodayMorningSection`, `TodayEveningSection`, `TodayFlowTabs`.
// Кнопка «Открыть число дня» — `TodayRitualCopy.numberRevealCta`; «Как ты сейчас?» — `TodayRitualCopy.checkInTitle`.

enum TodayWebFlowTabsCopy {
    static let todayFlowTabsNavAriaLabel = "Шаги дня"
    static let todayFlowTabGuideLabel = "Главное"
    static let todayFlowTabGuideDesc = "Сейчас и следующий шаг"
    static let todayFlowTabSpheresLabel = "Сферы"
    static let todayFlowTabSpheresDesc = "Где усилить день"
    static let todayFlowTabMorningLabel = "Утро"
    static let todayFlowTabMorningDesc = "Старт и намерение"
    static let todayFlowTabDayLabel = "День"
    static let todayFlowTabDayDesc = "Ритм и действия"
    static let todayFlowTabEveningLabel = "Вечер"
    static let todayFlowTabEveningDesc = "Закрытие и вывод"
}

// MARK: - RITUAL_COPY: прогрев `/today` и персональные маршруты сфер
// Паритет `thinkingMessages`, `getHoroscopeScenarioRoute` в `todayPageUtils.ts`.

enum TodayWebPageShellCopy {
    static let todayPageThinkingInitialTitle = "Открываем день"
    static let todayPageThinkingInitialMessage = "Подожди немного. Загружаю твой сегодняшний экран."
    static let todayPageThinkingInitialStatus = "Загружаем данные дня"
    static let todayPageThinkingRefreshTitle = "Обновляем день"
    static let todayPageThinkingRefreshMessage = "Подожди немного. Обновляю сегодняшние материалы."
    static let todayPageThinkingRefreshStatus = "Обновляем содержимое дня"
    static let todayPageThinkingRevealTitle = "Готовим день"
    static let todayPageThinkingRevealMessage = "Подожди немного. Скоро всё появится."
    static let todayPageThinkingRevealStatus = "Готовим материалы дня"

    static let horoscopeScenarioRouteLove = "Разобрать тему любви для себя"
    static let horoscopeScenarioRouteFamily = "Записать про семью в дневник"
    static let horoscopeScenarioRouteCareer = "Вопросы про карьеру"
    static let horoscopeScenarioRouteMoney = "Вопросы про деньги"
    static let horoscopeScenarioRouteDefault = "Открыть профиль"
}

// MARK: - RITUAL_COPY: данные дня / нарратив (`todayPageUtils.ts`)
// Статические строки + форматтеры — дословный паритет с `todayRitualCopy.ts`.

enum TodayWebTodayPageDataCopy {
    static let dayEventsMorningFocusPrefix = "Фокус утра: "
    static let dayEventsIntentionPrefix = "Намерение: "
    static let dayEventsTrackerPrefix = "Шаг дня: "
    static let dayEventsDayCycleCompleted = "Дневной цикл отмечен как завершённый"
    static let ritualEntrySublineClosing =
        "Дальше — карта дня, число и короткий чек состояния: так Today опирается на твои данные, а не на общие фразы."

    static let rhythmTooltipProgressMark = "• Отметка прогресса"
    static let rhythmTooltipStateMark = "• Состояние зафиксировано"
    static let rhythmTooltipNoteMark = "• Есть заметка"
    static let rhythmTooltipPracticeMark = "• Выполнена практика"
    static let rhythmTooltipJournalMark = "• Есть запись в дневнике"
    static let rhythmTooltipNoActivity = "• Активности не зафиксированы"
    static let rhythmTooltipClickUnmarkDay = "Клик: снять отметку в карте"
    static let rhythmTooltipClickMarkDay = "Клик: отметить день в карте"

    static let dailyRewardBadgePractice = "Практика дня"
    static let dailyRewardBadgeWeeklyStep = "Шаг недельного фокуса"
    static let dailyRewardBadgeDayClosed = "День закрыт"
    static let dailyRewardGoldTitle = "День в опоре"
    static let dailyRewardGoldMessage = "Хороший темп. Продолжай по текущему фокусу и не добавляй лишнего."
    static let dailyRewardGoldFallbackBadge = "Стабильный фокус"
    static let dailyRewardSilverTitle = "Ровный ход"
    static let dailyRewardSilverMessage = "Ровный ход. Закрой один небольшой шаг и двигайся дальше."
    static let dailyRewardSilverFallbackBadge = "Ровный ритм"
    static let dailyRewardBronzeTitle = "Точка старта"
    static let dailyRewardBronzeMessage = "Начни с одного простого шага и доведи его до конца."
    static let dailyRewardBronzeFallbackBadge = "Первый шаг"

    static let rewardsCardTitleGold = "Высокий уровень"
    static let rewardsCardTitleSilver = "Уверенный уровень"
    static let rewardsCardTitleBronze = "Стартовый уровень"

    static let personalInsightLocalNameFallback = "Ты"
    static let personalInsightTitleHigh = "Опора через профиль"
    static let personalInsightTitleMid = "День держится"
    static let personalInsightTitleStart = "Старт дня"
    static let personalInsightChipFallbackLow = "Низкий порог входа"
    static let personalInsightChipFallbackStable = "Стабильный ритм"
    static let personalInsightChipFallbackStep = "Один шаг сейчас"
    static let personalInsightCtaReturnMap = "Вернуться к карте профиля"
    static let personalInsightCtaOpenMap = "Открыть карту профиля"
    static let personalInsightCtaViewMap = "Посмотреть карту профиля"

    static let nextActionChooseFocusLabel = "Выбрать фокус дня"
    static let nextActionChooseFocusMessage = "Назови одной фразой, что для тебя главное сегодня."
    static let nextActionDoPracticeLabel = "Сделать практику"
    static let nextActionChoosePracticeLabel = "Выбрать практику"
    static let nextActionPracticeMessage = "Сделай одно короткое действие."
    static let nextActionWeeklyStepLabel = "Шаг по недельному фокусу"
    static let nextActionWeeklyStepMessage = "Отметь один шаг по недельному фокусу."
    static let nextActionEveningLabel = "Подвести итог дня"
    static let nextActionEveningMessage = "Коротко подведи итог дня."
    static let nextActionStateLabel = "Отметить состояние"
    static let nextActionStateMessage = "Отметь состояние дня."

    static let dailyNudgeHighMessage = "Сбавь темп. Выбери одно короткое действие и отметь состояние."
    static let dailyNudgeHighCta = "Сделать одно действие"
    static let dailyNudgeMediumMessage = "Сделай один шаг и сразу отметь его."
    static let dailyNudgeMediumCta = "Зафиксировать шаг"
    static let dailyNudgeLowMorningMessage = "Для старта выбери одну главную задачу."
    static let dailyNudgeLowMorningCta = "Открыть утро"
    static let dailyNudgeLowDayMessage = "Сделай один точный шаг."
    static let dailyNudgeLowDayCta = "Сделать один шаг"
    static let dailyNudgeLowEveningMessage = "Подведи итог и закрой день."
    static let dailyNudgeLowEveningCta = "Закрыть день"

    static let dayEnergyLabelCareful = "бережный режим"
    static let dayEnergyGuidanceCareful = "Сбавь темп и двигайся короткими шагами."
    static let dayEnergyLabelStable = "стабильный день"
    static let dayEnergyGuidanceStable = "Держи ровный темп и закрывай задачи по одной."
    static let dayEnergyLabelActive = "день действий"
    static let dayEnergyGuidanceActive = "Ресурса больше обычного. Держи фокус на главном."

    static let dayFocusThemeWork = "работа"
    static let dayFocusThemeMoney = "деньги"
    static let dayFocusThemeRelationships = "отношения"
    static let dayFocusThemeRecovery = "восстановление"
    static let dayFocusThemeClosure = "завершение"
    static let dayFocusFallbackPrimary1 = "работа"
    static let dayFocusFallbackPrimary2 = "восстановление"
    static let dayFocusFallbackLabel = "работа, восстановление"

    static let dayRiskFusionEmotionalLabel = "конфликт и перегрев"
    static let dayRiskFusionEmotionalDetail = "Сегодня легче, чем обычно, уйти в резкость и эмоциональные реакции."
    static let dayRiskFusionFocusLabel = "ошибки от расфокуса"
    static let dayRiskFusionFocusDetail = "Главный риск дня не в событиях, а в том, что внимание распадётся на мелочи."
    static let dayRiskFusionEnergyLabel = "усталость"
    static let dayRiskFusionEnergyDetail = "Лучше не перегружать себя и не путать усталость с отсутствием мотивации."
    static let dayRiskFusionDefaultLabel = "импульсивные решения"
    static let dayRiskFusionDefaultDetail = "Сегодня не спеши там, где важна спокойная проверка деталей."

    static let todayCriticalLimitAmplifyPrefix = "не усиливать: "

    static let weeklyPatternMoodUp = "Настроение к концу недели стало выше."
    static let weeklyPatternMoodDown = "Настроение к концу недели снизилось."
    static let weeklyPatternTrackedOften = "Состояние отслеживается регулярно."
    static let weeklyPatternTrackedRare = "Мало отметок состояния — паттерны читаются слабо."
    static let weeklyPatternJournalHelps = "Дневник помогает фиксировать контекст изменений."
    static let weeklyPatternJournalNone = "Нет записей в дневнике — сложнее понять причины скачков."
    static let weeklyPatternRecCareful3d =
        "Сделай ближайшие 3 дня в бережном режиме: 1 приоритет, вечерняя рефлексия и минимум перегруза."
    static let weeklyPatternRecKeepRhythm =
        "Сохрани рабочий ритм: повтори действия, которые давали улучшение, и не добавляй лишние задачи."
    static let weeklyPatternRecNeutral =
        "Паттерн недели нейтральный: чтобы понять триггеры, добавь 1 короткую отметку состояния и 1 запись в дневник в день."

    static let lifeNowWeeklyCompletedBody = "Эта недельная линия уже закрыта. Сегодня можно не возвращаться к ней."
    static let lifeNowWeeklyProgressStaleBody = "Чтобы не потерять недельный фокус, отметь сегодня один реальный шаг."
    static let lifeNowWeeklyProgressFreshBody = "Отметь один короткий шаг по недельному фокусу."
    static let lifeNowDisciplineTitleFallback = "Ритм дисциплины"
    static let lifeNowDisciplineBodyPractice = "Это короткая опора на сегодня. Выполни и зафиксируй."

    static let dailyReturnMorningEarlyTitle = "Начни с фокуса дня"
    static let dailyReturnMorningLateTitle = "Вернись к фокусу дня"
    static let dailyReturnMorningEarlyMessage = "Сначала выбери фокус, потом переходи к действиям."
    static let dailyReturnMorningLateMessage = "Коротко вернись к фокусу."
    static let dailyReturnMorningCta = "Открыть утро"
    static let dailyReturnMorningChip = "Первый заход"
    static let dailyReturnDayTitle = "Коротко отметь шаг за день"
    static let dailyReturnDayMessageEarly = "Когда появятся 3-5 минут, отметь один реальный шаг."
    static let dailyReturnDayMessageDefault = "Отметь один сделанный шаг."
    static let dailyReturnDayCta = "Отметить шаг"
    static let dailyReturnDayChip = "Короткий возврат"
    static let dailyReturnEveningTitleLate = "Позже стоит вернуться за коротким итогом"
    static let dailyReturnEveningTitlePrepare = "На вечер оставь только честный короткий итог"
    static let dailyReturnEveningMessageLate = "Заверши день спокойно: одна фраза и пара наблюдений."
    static let dailyReturnEveningMessageDefault = "Когда завершишь основное, вернись сюда на короткий итог."
    static let dailyReturnEveningCta = "Открыть итог дня"
    static let dailyReturnEveningChip = "Поздний возврат"
    static let dailyReturnAllSetTitle = "На сегодня всё"
    static let dailyReturnAllSetMessage = "На сегодня достаточно. Если вернёшься, проверь фокус и состояние."
    static let dailyReturnAllSetCta = "Открыть утро"
    static let dailyReturnAllSetChip = "День закрыт"

    static func formatDayEventsJournalCount(_ count: Int) -> String {
        "Дневник: записей сегодня — \(count)"
    }

    static func formatRitualEntrySublineFocusSnippet(_ s: String) -> String {
        "В приложении уже есть фокус: «\(s)»"
    }

    static func formatRitualEntrySublineIntentionSnippet(_ s: String) -> String {
        "Намерение на день: «\(s)»"
    }

    static func formatRitualEntrySublineCalendarLine(_ title: String) -> String {
        "В календаре сегодня: \(title)"
    }

    static func formatRitualEntrySublineProfileSunMoon(sun: String, lunarName: String) -> String {
        "По профилю: Солнце в \(sun); луна сейчас — \(lunarName)."
    }

    static func formatRitualEntrySublineProfileSunOnly(_ sun: String) -> String {
        "По профилю: Солнце в \(sun)."
    }

    static func formatRitualEntrySublineLunarOnly(_ lunarName: String) -> String {
        "Лунный фон дня: \(lunarName)."
    }

    static func formatDailyRewardStreakBadge(streakDays: Int) -> String {
        "Серия \(streakDays) дней"
    }

    static func formatRewardsCardStreakBadge(_ n: Int) -> String {
        "Стрик \(n) дн."
    }

    static func formatRewardsCardArchetypeBadge(_ level: String) -> String {
        "Архетип \(level)"
    }

    static func formatRewardsCardDisciplineBadge(_ score: Int) -> String {
        "Дисциплина \(score)"
    }

    static func formatRewardsCardHabitsBadge(_ n: Int) -> String {
        "Привычки \(n)"
    }

    static func formatRewardsCardAsceticBadge(_ n: Int) -> String {
        "Аскеза \(n)"
    }

    static func formatPersonalInsightChipTarot(_ name: String) -> String {
        "Таро: \(name)"
    }

    static func formatPersonalInsightChipNumber(_ value: CustomStringConvertible) -> String {
        "Число дня: \(value)"
    }

    static func formatPersonalInsightChipEnergy(_ tier: String) -> String {
        "Энергия: \(tier)"
    }

    static func formatPersonalInsightChipFocus(_ tier: String) -> String {
        "Фокус: \(tier)"
    }

    static func formatPersonalInsightChipStreak(_ days: Int) -> String {
        "Серия \(days) дн."
    }

    static func formatPersonalInsightMessageHighWithAnchor(localName: String, profileAnchor: String) -> String {
        "\(localName), спокойный темп на сегодня: \(profileAnchor) Выбери одно короткое действие и закрой его."
    }

    static func formatPersonalInsightMessageHighNoAnchor(localName: String) -> String {
        "\(localName), держи спокойный темп. Одно короткое действие и отметка состояния — достаточно."
    }

    static func formatPersonalInsightMessageMidWithAnchor(localName: String, profileAnchor: String) -> String {
        "\(localName), день держится на базе: \(profileAnchor) Доведи один главный приоритет до результата."
    }

    static func formatPersonalInsightMessageMidNoAnchor(localName: String) -> String {
        "\(localName), день держится хорошо. Доведи один главный приоритет до результата."
    }

    static func formatPersonalInsightMessageStartWithAnchor(localName: String, profileAnchor: String) -> String {
        "\(localName), начни с базы: \(profileAnchor) Выбери одно действие на 5-10 минут и сразу отметь результат."
    }

    static func formatPersonalInsightMessageStartNoAnchor(localName: String) -> String {
        "\(localName), начни с одного действия на 5-10 минут и сразу отметь результат."
    }

    static func formatActionPlanWeeklyStep(_ title: String) -> String {
        "закрыть один шаг по недельному фокусу: \(title)"
    }

    static func formatActionPlanQuickPractice(_ title: String) -> String {
        "сделать короткую практику: \(title)"
    }

    static func formatTodayCriticalLimitAmplify(_ riskLabel: String) -> String {
        "\(todayCriticalLimitAmplifyPrefix)\(riskLabel)"
    }

    static func formatLifeNowDisciplineBodyAscetic(days: Int) -> String {
        "Лучшая серия аскезы: \(days) дн. Удержи ритм до вечера."
    }

    static func formatLifeNowDisciplineBodyHabit(days: Int) -> String {
        "Лучшая серия привычки: \(days) дн. Удержи ритм."
    }

    static func formatLifeNowDisciplineStatusMinutes(_ minutes: Int) -> String {
        "\(minutes) мин"
    }

    static func formatLifeNowDisciplineStatusAscetic(_ n: Int) -> String {
        "Аскеза \(n)"
    }

    static func formatLifeNowDisciplineStatusHabit(_ n: Int) -> String {
        "Привычка \(n)"
    }
}

enum TodayWebDaySectionCopy {
    static let daySectionTitle = "Шаг дня"
    static let dayStepLogicEyebrow = "Логика шага дня"
    static let dayStepLogicBody = "1) Отметь текущее состояние 2) Сделай одну короткую фиксацию 3) Закрой день вечером."
    static let dayIntentionEyebrow = "Намерение дня"
    static let dayPhaseCheckInTitle = "Шаг 1: состояние сейчас"
    static let dayPhaseCheckInHint = "Коротко зафиксируй, как ты сейчас в середине дня."
    static let dayPhaseJournalTitle = "Шаг 2: одна короткая отметка"
    static let dayPhaseJournalSubtitle = "Достаточно одного действия."
    static let dayJournalFixedSummary = "Что уже зафиксировано"
    static let dayJournalTypeObservation = "Наблюдение"
    static let dayJournalTypeGratitude = "Благодарность"
    static let dayJournalTypeInsight = "Инсайт"
    static let dayJournalPromptObservation = "Что ты сейчас замечаешь в себе или в дне?"
    static let dayJournalPromptGratitude = "За что сегодня хочется поблагодарить?"
    static let dayJournalPromptInsight = "Какой вывод или поворот появился?"
    static let dayJournalMoreEntriesIntro = "Открыть ещё"
    static let dayEmptyNoMarkers = "Пока нет отметок за день. Добавь состояние или короткую запись."

    static func formatJournalMoreEntriesCta(count: Int) -> String {
        let suffix: String
        if count == 1 { suffix = "ь" } else if count < 5 { suffix = "и" } else { suffix = "ей" }
        return "\(dayJournalMoreEntriesIntro) \(count) запис\(suffix)"
    }
}

/// Композеры на главном экране `TodayView` (утро / чек-ин / дневник / вечер) — паритет `todayRitualCopy.ts` (`todayView*`).
enum TodayWebTodayViewComposerCopy {
    static let todayViewComposerSaving = "Сохраняю..."
    static let todayViewMorningComposerEyebrow = "Утро"
    static let todayViewMorningComposerTitle = "Что сейчас важнее всего?"
    static let todayViewMorningComposerSubtitle =
        "Одна короткая фраза. Не манифест, а реальный ориентир, вокруг которого держится день."
    static let todayViewMorningComposerPlaceholder = "Например: не распыляться и держать ровный темп"
    static let todayViewMorningComposerSaveCta = "Сохранить фокус"
    static let todayViewMorningComposerSuccessStatus =
        "Фокус сохранен. Теперь день привязан к твоей реальной задаче."
    static let todayViewPulseEyebrow = "Чек-ин"
    static let todayViewPulseTitle = "Как ты себя чувствуешь сегодня?"
    static let todayViewPulseSubtitle =
        "Один тап уже помогает понять, стоит ли усилить действие или, наоборот, смягчить день."
    static let todayViewPulseNotePlaceholder = "Что сильнее всего влияет на тебя прямо сейчас?"
    static let todayViewPulseSaveCta = "Отметить состояние"
    static let todayViewPulseLastSignalBannerPrefix = "Последний сигнал: "
    static let todayViewPulseComposedEnergyPrefix = "Энергия: "
    static let todayViewPulseComposedMoodPrefix = "Настроение: "
    static let todayViewPulseComposedStressPrefix = "Стресс: "
    static let todayViewPulseComposedSeparator = " · "
    static let todayViewPulseEnergyLow = "Низкая"
    static let todayViewPulseEnergyMedium = "Средняя"
    static let todayViewPulseEnergyHigh = "Высокая"
    static let todayViewPulseMoodCalm = "Спокойно"
    static let todayViewPulseMoodOpen = "Открыто"
    static let todayViewPulseMoodTense = "Напряжённо"
    static let todayViewPulseStressLow = "Низкий"
    static let todayViewPulseStressMedium = "Средний"
    static let todayViewPulseStressHigh = "Высокий"
    static let todayViewPulseSuccessStatus = "Состояние сохранено. Рекомендации уже могут подстроиться точнее."
    static let todayViewJournalEyebrow = "Дневник"
    static let todayViewJournalTitle = "Одна полезная заметка"
    static let todayViewJournalSubtitle =
        "Короткая запись помогает лучше видеть не только день, но и повторяющиеся ситуации."
    static let todayViewJournalPickerLabel = "Тип записи"
    static let todayViewJournalSaveCta = "Сохранить заметку"
    static let todayViewJournalSuccessStatus = "Запись сохранена. Это поможет давать тебе более точные подсказки."
    static let todayViewEveningComposerEyebrow = "Вечер"
    static let todayViewEveningComposerTitle = "Как прошел день?"
    static let todayViewEveningComposerSubtitle =
        "Вечером нужен короткий итог: что оказалось лучше, где было трудно и какой сигнал стоит запомнить."
    static let todayViewEveningComposerReflectionPlaceholder = "Что в итоге оказался этот день для тебя?"
    static let todayViewEveningComposerNoticedTitle = "Что заметила"
    static let todayViewEveningComposerHardestTitle = "Где было сложнее"
    static let todayViewEveningComposerEasierTitle = "Что оказалось легче"
    static let todayViewEveningComposerMarkClosedToggle = "Отметить день как закрытый"
    static let todayViewEveningComposerSaveCta = "Сохранить рефлексию"
    static let todayViewEveningComposerSuccessStatus =
        "Рефлексия сохранена. Следующие дни станут точнее на основе этого сигнала."

    static func formatMorningComposerSavedBanner(saved: String) -> String {
        "Текущее намерение: “\(saved)”"
    }

    static func formatJournalSavedCountBanner(count: Int) -> String {
        let mod100 = count % 100
        let mod10 = count % 10
        let word: String
        if (11 ... 14).contains(mod100) {
            word = "записей"
        } else if mod10 == 1 {
            word = "запись"
        } else if (2 ... 4).contains(mod10) {
            word = "записи"
        } else {
            word = "записей"
        }
        return "Сегодня уже сохранено \(count) \(word)."
    }
}

enum TodayWebMorningSectionCopy {
    static let morningSectionTitle = "Утро и опора дня"
    static let morningTarotRevealCta = "Открыть карту дня"
    static let morningTarotClosedHint = "Карта пока закрыта. Открой её."
    static let morningTarotEyebrow = "Карта дня"
    static let morningTarotNameFallback = "Карта дня"
    static let morningNumerologyClosedHint = "Число пока скрыто. Открой его."
    static let morningNumerologyEyebrow = "Число дня"
    static let morningDetailsHideCta = "Скрыть детали"
    static let morningDetailsShowCta = "Детали"
    static let morningCombinedSummaryEyebrow = "Коротко на сегодня"
    static let morningCombinedBothOpenLine = "Карта и число уже дают понятную опору на день."
    static let morningCombinedTarotOnlyLine = "Карта дня уже открыта. Держи фокус на главном."
    static let morningCombinedNumberOnlyLine = "Число дня открыто. Держи спокойный темп и не перегружай себя."
    static let morningHoroscopeHintSummary = "Подсказка утра"
    static let morningPhaseCheckInTitle = "Состояние: утро"
    static let morningPhaseCheckInHint = "Коротко отметь настроение, энергию и напряжение."
    static let morningIntentionEyebrow = "Намерение на день"
    static let morningIntentionLead = "Одна фраза для дня"
    static let morningIntentionHint = "Коротко: что важно удержать до вечера."
    static let morningIntentionPlaceholder = "Например: сегодня держу спокойный темп в важных разговорах."
    static let morningEmptyStateLine = "Начни с карты и короткого намерения."
    static let morningRefreshingShort = "Обновляю..."
    static let morningRefreshBlockCta = "Обновить утро"
    static let morningTarotDetailWhyCard = "Почему эта карта"
    static let morningDetailHowDay = "Как может складываться день"
    static let morningDetailPossibleEvents = "Что может проявиться"
    static let morningDetailWhatSupports = "Что поддержит"
    static let morningDetailWhatNotAmplify = "Чего не усиливать"
    static let morningTarotKeywordsLabel = "Ключевые слова"
    static let morningNumerologyDetailWhyNumber = "Почему это число"
    static let morningNumerologyDetailSupplement = "Дополнение"
}

enum TodayWebEveningSectionCopy {
    static let eveningSectionTitle = "Закрыть день"
    static let eveningOutlookLoadError = "Не удалось загрузить итог. Попробуй еще раз."
    static let eveningOutlookLoading = "Загружаем итог дня…"
    static let eveningNarrativePreparing = "Готовим итог дня…"
    static let eveningOutlookSummaryEyebrow = "Сводка"
    static let eveningOutlookMapTitle = "Карта состояния дня"
    static let eveningOutlookPreambleDefault = "Утро, день и вечер — на одной линии. Ниже короткий итог по дню."
    static let eveningOutlookPhaseMorning = "Утро"
    static let eveningOutlookPhaseDay = "День"
    static let eveningOutlookPhaseEvening = "Вечер"
    static let eveningPhaseNoCheckinYet = "ещё нет отметки"
    static let eveningScaleMoodLabel = "Настроение"
    static let eveningScaleEnergyLabel = "Энергия"
    static let eveningScaleStressLabel = "Стресс"
    static let eveningPhaseHasNote = "есть заметка"
    static let eveningChipDayLine = "линия дня"
    static let eveningChipIntentionSaved = "намерение записано"
    static let eveningChipGoalStepsPrefix = "шаги по целям:"
    static let eveningChipHabitsPrefix = "привычки:"
    static let eveningTextSectionEyebrow = "Текстом"
    static let eveningOpenCalendarCta = "Открыть в календаре"
    static let eveningClosureCardTitle = "Завершение дня"
    static let eveningClosingPhrasePlaceholder = "Завершающая фраза дня (по желанию)"
    static let eveningMarkedDoneCheckbox = "День завершён"
    static let eveningMarkedDoneEncouragement = "На сегодня достаточно. Возьми с собой главное."
    static let eveningPhaseCheckInHint = "Коротко отметь состояние перед итогом дня."
    static let eveningOpenStateMapSummary = "Открыть карту состояния дня"
    static let eveningReflectionTitle = "Итог дня"
    static let eveningReflectionPlaceholder = "Что сработало сегодня и что берешь в завтра?"
    static let eveningExtraDetailsSummary = "Если хочешь добавить детали"
    static let eveningObsPlaceholderNoticed = "Что сегодня особенно заметил"
    static let eveningObsPlaceholderHardest = "Где было сложнее всего"
    static let eveningObsPlaceholderEasier = "Что далось легче"
    static let eveningSaveSummaryCta = "Сохранить итог"
    static let eveningRefreshBlockCta = "Обновить блок"
    static let eveningCompletedCheckLine = "✓ День завершён"
    static let eveningDayStartLinkSummary = "Связь с началом дня"
    static let eveningMorningIntentionRecall = "🌅 В начале дня ты хотел:"
    static let eveningObservationsHeading = "👁️ Наблюдения:"
    static let eveningObsStrongNoticed = "Заметил:"
    static let eveningObsStrongHardest = "Сложнее всего:"
    static let eveningObsStrongEasier = "Легче, чем ожидал:"
    static let eveningReflectionBlockHeading = "💭 Рефлексия:"
    static let eveningThreadBlockHeading = "🧵 Главная линия:"
    static let eveningEmptyClosingHint = "Закрой день в любой момент: одна фраза и пара наблюдений."

    static func formatGoalStepsChip(_ n: Int) -> String { "\(eveningChipGoalStepsPrefix) \(n)" }
    static func formatHabitsChip(_ n: Int) -> String { "\(eveningChipHabitsPrefix) \(n)" }
}
