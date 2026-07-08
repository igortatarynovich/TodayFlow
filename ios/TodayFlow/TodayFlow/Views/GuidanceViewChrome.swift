import Foundation

/// RU/EN chrome for Guidance (`QuestionsView` + history sheet). Mirrors `IOSAppLocale` rules.
enum GuidanceViewChrome {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    // MARK: Primary + nav

    /// Паритет `nav.guidance.hub` / шапки Guidance на вебе при `locale=ru`.
    static var navTitle: String { ru ? "Центр разборов" : "Guidance" }
    static var modePicker: String { ru ? "Режим" : "Mode" }
    static var primaryTarot: String { ru ? "Расклад с картами" : "Card reading" }
    static var primaryQuick: String { ru ? "Быстрый ответ" : "Quick answer" }
    static var startOver: String { ru ? "С начала" : "Start over" }
    static var historyA11y: String { ru ? "История" : "History" }

    // MARK: Spread sections (picker groups)

    static var spreadSectionQuick: String { GuidanceHubChromeCopy.guidanceHubCatalogSectionQuick }
    static var spreadSectionMedium: String { GuidanceHubChromeCopy.guidanceHubCatalogSectionMedium }
    static var spreadSectionDeep: String { GuidanceHubChromeCopy.guidanceHubCatalogSectionDeep }

    // MARK: Hero

    static var heroTitle: String { ru ? "Один вопрос — разбор ситуации" : "One question—a grounded read" }
    static var heroBody: String {
        ru
            ? "Расклад, вопрос, контекст и карты — на одном экране, сверху вниз. Разбор можно запросить, когда открыты все позиции и вопрос готов."
            : "Spread, question, context, and cards—one screen, top to bottom. Request the read once every position is open and your question is ready."
    }

    // MARK: Jump bar

    static var jumpBarLabel: String { ru ? "К секции" : "Jump to" }
    static var jumpSpread: String { ru ? "Расклад" : "Spread" }
    static var jumpQuestion: String { ru ? "Вопрос" : "Question" }
    static var jumpContext: String { ru ? "Контекст" : "Context" }
    static var jumpCards: String { ru ? "Карты" : "Cards" }
    static var jumpReading: String { ru ? "Разбор" : "Reading" }
    static var jumpBarA11y: String { ru ? "Быстрый переход по секциям разбора" : "Quick jump between Guidance sections" }
    static var jumpReadingHint: String { ru ? "Появится после получения разбора" : "Available after the reading loads" }

    // MARK: Tarot sections

    static var secSpreadTitle: String { ru ? "Расклад" : "Spread" }
    static var secSpreadLead: String {
        ru
            ? "Один список по группам. Позже можно пересдать карты под другой формат."
            : "One grouped list. You can reshuffle for another format later."
    }
    static var spreadPicker: String { ru ? "Расклад" : "Spread" }

    static var secClarifyTitle: String { ru ? "Фокус уточнения" : "Clarification focus" }
    static var secClarifyLead: String {
        ru
            ? "Одна карта к последнему разбору. Выбери, что хочешь прояснить — затем раздай одну карту."
            : "One card for your last reading. Pick what to clarify—then draw one card."
    }

    static var secQuestionTitle: String { ru ? "Вопрос" : "Question" }
    static var secQuestionLeadClarify: String {
        ru
            ? "Тот же вопрос, что в основном разборе — его нельзя менять на шаге уточнения."
            : "Same question as the main reading—you can’t change it during clarification."
    }
    static var secQuestionLeadNormal: String {
        ru
            ? "Сформулируй для ясности, не для гарантий — минимум три символа."
            : "Ask for clarity, not guarantees—at least three characters."
    }
    static var questionPlaceholder: String {
        ru
            ? "Сформулируй вопрос для ясности, не для гарантий"
            : "Phrase your question for clarity, not guarantees"
    }

    static var secContextTitle: String { ru ? "Контекст" : "Context" }
    static var secContextLeadClarify: String {
        ru ? "Контекст уже учтён в основном разборе — здесь только просмотр." : "Context is already in the main reading—view only here."
    }
    static var secContextLeadNormal: String {
        ru
            ? "По желанию — так разбор точнее. Можно пропустить и сразу перейти к картам."
            : "Optional—helps accuracy. Skip and go straight to cards if you want."
    }
    static var chipTopic: String { ru ? "Тема" : "Topic" }
    static var chipOutcome: String { ru ? "Что хочу получить" : "What I want from this" }
    static var chipWho: String { ru ? "Кто этот человек" : "Who they are to you" }
    static var chipIntimacy: String { ru ? "Что волнует" : "What’s on your mind" }

    static var secCardsTitle: String { ru ? "Карты" : "Cards" }
    static var secCardsLeadClarify: String {
        ru ? "Расклад фиксирован: одна карта. Открой её и запроси уточнение." : "Fixed spread: one card. Reveal it and request clarification."
    }
    static var secCardsLeadNormal: String {
        ru
            ? "Раздай колоду, затем открывай позиции по одной. Когда всё открыто и вопрос готов — запроси разбор."
            : "Shuffle, then reveal positions one by one. When all are open and your question is ready—request the reading."
    }
    static var dealHint: String {
        ru
            ? "Нажми «Раздать карты», когда будешь готов сфокусироваться на вопросе."
            : "Tap “Deal cards” when you’re ready to focus on your question."
    }
    static var dealCards: String { ru ? "Раздать карты" : "Deal cards" }
    static var reshuffle: String { ru ? "Пересдать" : "Reshuffle" }
    static var revealAllHint: String {
        ru
            ? "Открой каждую позицию — затем появится кнопка «Получить разбор»."
            : "Reveal every position—then the “Get reading” button appears."
    }
    static var getClarification: String { ru ? "Получить уточнение" : "Get clarification" }
    static var getReading: String { ru ? "Получить разбор" : "Get reading" }
    static var needQuestionClarify: String {
        ru ? "Вопрос основного разбора должен остаться заполненным." : "Keep the main reading’s question filled in."
    }
    static var needQuestionNormal: String {
        ru ? "Сначала уточни вопрос выше (минимум три символа)." : "Clarify your question above (at least three characters)."
    }

    static var loadingClarify: String { ru ? "Собираем уточнение…" : "Gathering clarification…" }
    static var loadingReading: String { ru ? "Собираем разбор…" : "Gathering reading…" }
    static var loadingClarifySub: String {
        ru
            ? "Одна карта к твоему последнему разбору — тот же контекст, другой фокус вопроса."
            : "One card on your last reading—same context, a different focus."
    }
    static var loadingReadingSub: String {
        ru
            ? "Учитываем вопрос, позиции и профиль — это связный текст под ситуацию, не справочник значений."
            : "We use your question, positions, and profile—coherent guidance, not a keyword list."
    }

    static var cardReversed: String { ru ? "перевёрнутая" : "reversed" }
    static var cardUpright: String { ru ? "прямая" : "upright" }
    static func orientationLabel(_ orientation: String?) -> String {
        guard let orientation else { return cardUpright }
        return orientation.lowercased() == "reversed" ? cardReversed : cardUpright
    }

    static var openCard: String { ru ? "Открыть карту" : "Reveal card" }

    // MARK: Quick flow

    static var quickStage1: String { ru ? "1. Фокус" : "1. Focus" }
    static var quickStage2: String { ru ? "2. Разбор" : "2. Read" }
    static var quickStage3: String { ru ? "3. След. шаг" : "3. Next" }
    static var lanePicker: String { ru ? "Режим вопроса" : "Question mode" }
    static var yourQuestion: String { ru ? "Твой вопрос" : "Your question" }
    static var quickLoadingCta: String { ru ? "Собираю разбор..." : "Gathering read..." }
    static var quickOpenReading: String { ru ? "Открыть разбор" : "Open reading" }

    // MARK: Answer cards (quick + guidance)

    static var badgeWithProfile: String { ru ? "С учётом профиля" : "With profile" }
    static var badgeNoProfile: String { ru ? "Без профиля" : "No profile" }
    static var badgeProfileShort: String { ru ? "Профиль" : "Profile" }

    static var ansClarity: String { ru ? "Ясность" : "Clarity" }
    static var ansExplanation: String { ru ? "Объяснение" : "Explanation" }
    static var ansToday: String { ru ? "Сегодня" : "Today" }
    static var ansDecision: String { ru ? "Решение" : "Decision" }
    static var ansForecast: String { ru ? "Прогноз" : "Outlook" }
    static var nextRoute: String { ru ? "Следующий маршрут" : "Next route" }
    static var openNextStep: String { ru ? "Открыть следующий шаг" : "Open next step" }

    static var clarifyingCard: String { ru ? "Уточняющая карта" : "Clarifying card" }
    static func spreadColon(_ name: String) -> String { ru ? "Расклад: \(name)" : "Spread: \(name)" }
    static func focusColon(_ label: String) -> String { ru ? "Фокус: \(label)" : "Focus: \(label)" }
    static var questionStrength: String { ru ? "Вопрос и сила расклада" : "Question and spread strength" }
    static var ansShort: String { ru ? "Коротко" : "Brief" }
    static var ansWhatsHappening: String { ru ? "Что здесь происходит" : "What’s going on" }
    static var ansCardByCard: String { ru ? "Карта за картой" : "Card by card" }
    static var ansForYou: String { ru ? "Что это значит для тебя" : "What this means for you" }
    static var ansCore: String { ru ? "Главный узел" : "Core knot" }
    static var ansWhy: String { ru ? "Почему такой вывод" : "Why this read" }
    static var ansContinue: String { ru ? "Если хочешь продолжить" : "If you want to go further" }
    static var ansAvoid: String { ru ? "Чего не делать" : "What to avoid" }
    static var ansDo: String { ru ? "Что лучше сделать" : "What works better" }
    static var ansNextStep: String { ru ? "Следующий шаг" : "Next step" }
    static var route: String { ru ? "Маршрут" : "Route" }
    static var pullClarifier: String { ru ? "Вытянуть уточняющую карту" : "Draw a clarifier" }
    static var newSpread: String { ru ? "Новый расклад" : "New spread" }

    // MARK: Errors + feedback

    static var clarifyOneCardOnly: String { ru ? "Уточнение доступно только для одной карты." : "Clarification is only available for a one-card spread." }
    static var clarifyAlreadyUsed: String { ru ? "Уточнение для этого разбора уже было запрошено." : "Clarification was already requested for this reading." }

    static var feedbackHow: String { ru ? "Как откликнулось?" : "How did it land?" }
    static var resonanceHigh: String { ru ? "Сильно" : "Strong" }
    static var resonancePartial: String { ru ? "Частично" : "Partial" }
    static var resonanceLow: String { ru ? "Мало" : "Little" }
    static var feedbackComment: String { ru ? "Комментарий (по желанию)" : "Comment (optional)" }
    static var saved: String { ru ? "Сохранено" : "Saved" }
    static var sendFeedback: String { ru ? "Отправить отклик" : "Send feedback" }
    static var shortMark: String { ru ? "Короткая отметка" : "Quick mark" }
    static var helpfulDone: String { ru ? "Помогло ✓" : "Helpful ✓" }
    static var helpful: String { ru ? "Дало ясность" : "Felt clear" }
    static var unclearDone: String { ru ? "Отмечено ✓" : "Noted ✓" }
    static var unclear: String { ru ? "Нужно яснее" : "Need clarity" }
    static var quickFeedbackTitle: String { ru ? "Отклик на разбор" : "Reading feedback" }
    static var pickResonance: String { ru ? "Выбери, насколько откликнулось" : "Pick how much it resonated" }
    static var thanksFeedback: String { ru ? "Спасибо, это поможет следующим разборам" : "Thanks—this helps future reads" }
    static var signalSaved: String { ru ? "Сигнал сохранён" : "Signal saved" }
    static var notedNeedClarity: String { ru ? "Отметили, что нужно больше ясности" : "Noted: needs more clarity" }

    // MARK: History sheet

    static var historyTitle: String { ru ? "История" : "History" }
    static var close: String { ru ? "Закрыть" : "Close" }
    static var loading: String { ru ? "Загрузка…" : "Loading…" }
    static var emptyHistory: String { ru ? "Пока ничего нет" : "Nothing yet" }
    static var filterAll: String { ru ? "Все" : "All" }
    static var filterGuidance: String { ru ? "Разбор" : "Guidance" }
    static var filterQuestions: String { ru ? "Вопросы" : "Questions" }
    static var filterDecisions: String { ru ? "Решения" : "Decisions" }
    static var filterTarot: String { ru ? "Таро" : "Tarot" }
    static func topicLine(_ topic: String) -> String { ru ? "Тема: \(topic)" : "Topic: \(topic)" }
    static var openGuidance: String { ru ? "Открыть разбор" : "Open Guidance" }
    static var openDecisions: String { ru ? "Экран решений" : "Decisions" }
    static var openQuestions: String { ru ? "Вопросы" : "Questions" }
    static var dailyCard: String { ru ? "Карта дня" : "Daily card" }
    static var openTarot: String { ru ? "Открыть Таро" : "Open Tarot" }
    static var spreadHeader: String { ru ? "Расклад" : "Spread" }

    static func modeTitle(_ mode: String) -> String {
        switch mode {
        case "guidance": return ru ? "Разбор" : "Guidance"
        case "guidance_clarify": return ru ? "Уточнение к разбору" : "Guidance · clarify"
        case "decision": return ru ? "Решение" : "Decision"
        case "question": return ru ? "Вопрос" : "Question"
        default: return mode
        }
    }

    // MARK: Choice rows (ids stable for API)

    static var topicChoices: [(id: String, label: String)] {
        ru
            ? [
                ("relationships", "отношения"),
                ("work", "работа"),
                ("money", "деньги"),
                ("family", "семья"),
                ("choice", "выбор"),
                ("inner_state", "состояние"),
                ("intimacy", "близость"),
                ("other", "другое"),
            ]
            : [
                ("relationships", "relationships"),
                ("work", "work"),
                ("money", "money"),
                ("family", "family"),
                ("choice", "choice"),
                ("inner_state", "state"),
                ("intimacy", "intimacy"),
                ("other", "other"),
            ]
    }

    static var outcomeChoices: [(id: String, label: String)] {
        ru
            ? [
                ("clarity", "ясность"),
                ("decision", "решение"),
                ("confirmation", "подтверждение"),
                ("warning", "предупреждение"),
                ("next_step", "шаг"),
                ("understand_other", "другой человек"),
                ("understand_self", "себя"),
            ]
            : [
                ("clarity", "clarity"),
                ("decision", "decision"),
                ("confirmation", "confirmation"),
                ("warning", "warning"),
                ("next_step", "next step"),
                ("understand_other", "the other person"),
                ("understand_self", "myself"),
            ]
    }

    static var relationshipRoles: [(id: String, label: String)] {
        ru
            ? [
                ("partner", "партнёр"),
                ("ex", "бывший"),
                ("crush", "симпатия"),
                ("unclear", "неясно"),
                ("sexual_pull", "притяжение"),
                ("other_rel", "другое"),
            ]
            : [
                ("partner", "partner"),
                ("ex", "ex"),
                ("crush", "crush"),
                ("unclear", "unclear"),
                ("sexual_pull", "pull"),
                ("other_rel", "other"),
            ]
    }

    static var intimacyChoices: [(id: String, label: String)] {
        ru
            ? [
                ("desire", "желание"),
                ("distance", "дистанция"),
                ("tension", "напряжение"),
                ("attachment", "зависимость"),
                ("lack_closeness", "мало близости"),
                ("boundaries", "границы"),
                ("other_in", "другое"),
            ]
            : [
                ("desire", "desire"),
                ("distance", "distance"),
                ("tension", "tension"),
                ("attachment", "attachment"),
                ("lack_closeness", "not enough closeness"),
                ("boundaries", "boundaries"),
                ("other_in", "other"),
            ]
    }

    static var clarificationGoals: [(id: String, label: String)] {
        ru
            ? [
                ("blind_spot", "что я не вижу"),
                ("next_step", "следующий шаг"),
                ("risk", "где риск"),
                ("boundary", "здоровая граница"),
            ]
            : [
                ("blind_spot", "blind spot"),
                ("next_step", "next step"),
                ("risk", "risk"),
                ("boundary", "healthy boundary"),
            ]
    }

    /// `(id, icon, title, hint, prompt)` for quick-answer shortcuts.
    static var quickEntryRows: [(String, String, String, String, String)] {
        ru
            ? [
                ("love", "💞", "Отношения", "Когда неясно, что происходит между вами", "Что сейчас происходит в этой связи и как мне лучше действовать?"),
                ("money", "💸", "Деньги", "Когда тревожно за доход и решения", "Что сейчас мешает деньгам и какой шаг даст сдвиг?"),
                ("decision", "🧭", "Решение", "Когда застрял между двумя вариантами", "Какой выбор сейчас будет для меня точнее и спокойнее?"),
            ]
            : [
                ("love", "💞", "Relationships", "When it’s unclear what’s happening between you", "What’s happening in this connection and how should I act?"),
                ("money", "💸", "Money", "When income and choices feel tense", "What’s blocking money right now and what move would shift it?"),
                ("decision", "🧭", "Decision", "When you’re stuck between two paths", "Which choice is truer and calmer for me right now?"),
            ]
    }

    // MARK: Lane copy (`Lane.rawValue`: daily | decision | pattern)

    static func laneTitle(raw: String) -> String {
        switch raw {
        case "daily": return ru ? "Сегодня" : "Today"
        case "decision": return ru ? "Решение" : "Decision"
        case "pattern": return ru ? "Паттерн" : "Pattern"
        default: return raw
        }
    }

    static func lanePrompt(raw: String) -> String {
        switch raw {
        case "daily":
            return ru ? "Что мне важно понять про сегодняшний день?" : "What do I need to understand about today?"
        case "decision":
            return ru ? "Что мне важно увидеть перед решением?" : "What do I need to see before I decide?"
        case "pattern":
            return ru ? "Какой повторяющийся паттерн я хочу разобрать?" : "Which repeating pattern do I want to unpack?"
        default: return ""
        }
    }

    static func laneQuickPrompts(raw: String) -> [String] {
        switch raw {
        case "daily":
            return ru
                ? [
                    "На чем мне держать день сегодня?",
                    "Где сегодня не распылиться?",
                    "Какой шаг лучше сделать первым?",
                ]
                : [
                    "What should I anchor my day on today?",
                    "Where should I avoid scattering my energy today?",
                    "Which step should I take first?",
                ]
        case "decision":
            return ru
                ? [
                    "Стоит ли двигать это сейчас?",
                    "Чего я не вижу в своём решении?",
                    "Что здесь важнее скорости?",
                ]
                : [
                    "Should I move on this now?",
                    "What am I missing in my decision?",
                    "What matters more than speed here?",
                ]
        case "pattern":
            return ru
                ? [
                    "Почему я снова устаю в одном и том же месте?",
                    "Какой сценарий повторяется у меня в отношениях?",
                    "Где я сама усиливаю напряжение?",
                ]
                : [
                    "Why do I keep burning out in the same place?",
                    "What scenario repeats for me in relationships?",
                    "Where am I adding tension myself?",
                ]
        default: return []
        }
    }

    static func topicHistoryLabel(_ topic: String?) -> String? {
        guard let topic else { return nil }
        let map: [String: String] =
            ru
                ? [
                    "relationships": "отношения",
                    "work": "работа",
                    "money": "деньги",
                    "family": "семья",
                    "choice": "выбор",
                    "inner_state": "состояние",
                    "intimacy": "близость",
                    "other": "другое",
                ]
                : [
                    "relationships": "relationships",
                    "work": "work",
                    "money": "money",
                    "family": "family",
                    "choice": "choice",
                    "inner_state": "state",
                    "intimacy": "intimacy",
                    "other": "other",
                ]
        return map[topic]
    }
}
