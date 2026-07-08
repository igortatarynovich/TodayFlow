import Foundation

// MARK: - Результат разбора (веб `GuidanceStructuredResult`, полоса карт, карточка результата)
// Зеркало `frontend/src/components/guidance/guidanceResultChrome.ts`

enum GuidanceResultChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var guidanceResultReflectionFallback: String {
        ru
            ? "Что для тебя сейчас важнее: быстро снять напряжение или получить ясность, которую можно проверить действием?"
            : "What matters more for you right now: easing the tension quickly, or getting clarity you can test with one action?"
    }
    static var guidanceResultToastPickResonance: String {
        ru ? "Выбери, насколько откликнулось" : "Pick how much this resonated"
    }
    static var guidanceResultToastFeedbackThanks: String {
        ru ? "Спасибо, это поможет следующим разборам" : "Thanks—that helps us improve future readings"
    }
    static var guidanceResultToastFeedbackSaveFailed: String {
        ru ? "Не удалось сохранить ответ" : "Couldn’t save your response"
    }
    static var guidanceResultAssessmentEyebrow: String { ru ? "Вопрос и сила расклада" : "Your question and the spread’s strength" }
    static var guidanceResultSafetyBanner: String {
        ru
            ? "Этот расклад может помочь увидеть эмоции и внутренний конфликт, но не должен заменять профессиональную помощь или фактическую проверку ситуации. Если речь о безопасности, деньгах, здоровье или документах — опирайся на реальные данные и специалистов."
            : "This reading can help you see emotions and inner conflict, but it isn’t a substitute for professional support or checking facts on the ground. If safety, money, health, or paperwork is involved—rely on real information and qualified help."
    }
    static var guidanceResultShortEyebrowClarify: String { ru ? "Уточняющая карта" : "Clarifying card" }
    static var guidanceResultShortEyebrowMain: String { ru ? "Коротко" : "In short" }
    static var guidanceResultHappeningEyebrow: String { ru ? "Что здесь происходит" : "What’s going on here" }
    static var guidanceResultCardsEyebrow: String { ru ? "Карта за картой" : "Card by card" }
    private static var guidanceResultPositionLineTemplate: String { ru ? "Позиция: {position}" : "Position: {position}" }
    static func guidanceResultPositionLine(position: String) -> String {
        guidanceResultPositionLineTemplate.replacingOccurrences(of: "{position}", with: position)
    }
    static var guidanceResultOrientationReversed: String { ru ? "перевёрнутая" : "reversed" }
    static var guidanceResultOrientationUpright: String { ru ? "прямая" : "upright" }
    private static var guidanceResultMeaningLineTemplate: String {
        ru
            ? "Справочное значение в этой позиции: {meaning}"
            : "Reference meaning in this position: {meaning}"
    }
    static func guidanceResultMeaningLine(meaning: String) -> String {
        guidanceResultMeaningLineTemplate.replacingOccurrences(of: "{meaning}", with: meaning)
    }
    static var guidanceResultProfileBridgeEyebrow: String { ru ? "Что это значит для тебя" : "What this means for you" }
    static var guidanceResultCoreEyebrow: String { ru ? "Главный узел ситуации" : "The main knot in the situation" }
    static var guidanceResultWhyToggleOpenPrefix: String { "▼" }
    static var guidanceResultWhyToggleClosedPrefix: String { "▶" }
    static var guidanceResultWhyToggleLabel: String { ru ? "Почему такой вывод?" : "Why this interpretation?" }
    static var guidanceResultContinueEyebrow: String { ru ? "Если хочешь продолжить" : "If you want to go further" }
    static var guidanceResultAvoidEyebrow: String { ru ? "Чего лучше не делать" : "What to avoid" }
    static var guidanceResultDoEyebrow: String { ru ? "Что лучше сделать" : "What to do instead" }
    static var guidanceResultReflectionEyebrow: String { ru ? "Вопрос к себе" : "A question for yourself" }
    static var guidanceResultNextStepEyebrow: String { ru ? "Следующий шаг" : "Next step" }
    static var guidanceResultCompatTitle: String { ru ? "Разобрать вашу совместимость" : "Explore your compatibility" }
    static var guidanceResultCompatLead: String {
        ru
            ? "Если есть конкретный человек, можно посмотреть динамику глубже: эмоции, конфликты, близость и перспективу."
            : "If there’s a specific person, you can go deeper on the dynamic—emotions, conflict, closeness, and perspective."
    }
    static var guidanceResultCompatCta: String { ru ? "Перейти в Совместимость" : "Open Compatibility" }
    static var guidanceResultPatternTitle: String { ru ? "Понять свой паттерн" : "Understand your pattern" }
    static var guidanceResultPatternLead: String {
        ru
            ? "Если такие ситуации повторяются, полезно посмотреть на свой сценарий в портрете."
            : "If this keeps showing up, your portrait is a good place to see the script."
    }
    static var guidanceResultPatternCta: String { ru ? "Открыть профиль" : "Open profile" }
    static var guidanceResultClarifyTitle: String { ru ? "Уточняющий расклад" : "Clarifying spread" }
    static var guidanceResultClarifyLead: String {
        ru
            ? "Одна карта с конкретной целью. На сервере — не больше одного уточнения на основной разбор."
            : "One card with a specific aim. The server allows at most one clarification per main reading."
    }
    static var guidanceResultClarifyCta: String { ru ? "Вытянуть уточняющую карту" : "Draw a clarifying card" }
    static var guidanceResultFeedbackEyebrow: String { ru ? "Это откликнулось?" : "Did this land?" }
    static var guidanceResultResonanceHigh: String { ru ? "да, очень точно" : "yes, very accurate" }
    static var guidanceResultResonancePartial: String { ru ? "частично" : "partly" }
    static var guidanceResultResonanceNone: String { ru ? "нет, не про меня" : "no, not about me" }
    static var guidanceResultMatchChipsPrompt: String { ru ? "Что именно совпало?" : "What matched?" }
    static var guidanceResultMatchChipEmotions: String { ru ? "эмоции" : "emotions" }
    static var guidanceResultMatchChipPerson: String { ru ? "человек" : "the person" }
    static var guidanceResultMatchChipSexualTension: String { ru ? "сексуальное напряжение" : "sexual tension" }
    static var guidanceResultMatchChipFear: String { ru ? "страх" : "fear" }
    static var guidanceResultMatchChipAdvice: String { ru ? "совет" : "the advice" }
    static var guidanceResultMatchChipNothing: String { ru ? "ничего" : "none of these" }
    static var guidanceResultMatchChipIds: [String] {
        [
            guidanceResultMatchChipEmotions,
            guidanceResultMatchChipPerson,
            guidanceResultMatchChipSexualTension,
            guidanceResultMatchChipFear,
            guidanceResultMatchChipAdvice,
            guidanceResultMatchChipNothing,
        ]
    }
    static var guidanceResultCommentLabel: String {
        ru
            ? "Что важно запомнить для следующих разборов?"
            : "What should we remember for your next readings?"
    }
    static var guidanceResultCommentPlaceholder: String { ru ? "Коротко своими словами…" : "In your own words, briefly…" }
    static var guidanceResultSubmitFeedback: String { ru ? "Отправить отзыв" : "Send feedback" }
    static var guidanceResultFeedbackSaved: String { ru ? "Сохранено" : "Saved" }
    static var guidanceResultLegacyQuickLabel: String { ru ? "Быстрая отметка" : "Quick mark" }
    static var guidanceResultLegacyHelpfulActive: String { ru ? "Помогло" : "Helpful" }
    static var guidanceResultLegacyHelpfulInactive: String { ru ? "Дало ясность" : "It clarified things" }
    static var guidanceResultLegacyUnclearActive: String { ru ? "Отмечено" : "Noted" }
    static var guidanceResultLegacyUnclearInactive: String { ru ? "Мало ясности" : "Still unclear" }
    static var guidanceResultProfileIncompleteHint: String {
        ru
            ? "Ответ собран без полного профиля — заполни портрет, чтобы разборы стали точнее."
            : "This answer was assembled without a full profile—fill in your portrait for more precise readings."
    }
    static var guidanceStripRevealHint: String { ru ? "Нажми, чтобы открыть" : "Tap to reveal" }
    static var guidanceStripPositionFallback: String { ru ? "Карта" : "Card" }
    static var guidanceResultCardBlockCurrent: String { ru ? "Суть сейчас" : "The heart of it now" }
    static var guidanceResultCardBlockManifestation: String { ru ? "Проявление" : "How it shows up" }
    static var guidanceResultCardBlockCaution: String { ru ? "Риск" : "Risk" }
    static var guidanceResultCardBlockNextStep: String { ru ? "Следующий шаг" : "Next step" }

    static func stripTarotAppendFromExplanation(_ explanation: String) -> String {
        let needles = ["\nРасклад (", " Расклад (", "\nSpread (", " Spread ("]
        var bestOffset = -1
        for n in needles {
            if let r = explanation.range(of: n, options: .backwards) {
                let o = explanation.distance(from: explanation.startIndex, to: r.lowerBound)
                if o > bestOffset { bestOffset = o }
            }
        }
        if bestOffset < 0 { return explanation }
        let endIdx = explanation.index(explanation.startIndex, offsetBy: bestOffset)
        return String(explanation[..<endIdx]).trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Паритет `guidanceResultLoveQuestionHeuristic` (веб).
    static func guidanceResultLoveQuestionHeuristic(question: String) -> Bool {
        let pattern = ru
            ? "любов|партн|близост|чувств|он |она "
            : "love|partner|relationship|feel|closeness|crush|dating|them |him |her |they "
        return question.range(of: pattern, options: [.regularExpression, .caseInsensitive]) != nil
    }

    /// Паритет `guidanceResultShowCompatHint` (веб).
    static func guidanceResultShowCompatHint(topicId: String?, lane: String, question: String) -> Bool {
        guard topicId == "relationships" else { return false }
        if lane == "love" { return true }
        return guidanceResultLoveQuestionHeuristic(question: question)
    }
}
