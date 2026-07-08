import Foundation

// MARK: - Страница результата расклада (веб `/tarot/result`)
// Зеркало `frontend/src/components/tarot/tarotSpreadResultChrome.ts`

enum TarotSpreadResultChromeCopy {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var tarotSpreadResultErrorLoadFailed: String {
        ru ? "Не удалось загрузить результат расклада" : "Couldn’t load the spread result"
    }
    static var tarotSpreadResultErrorNotFound: String { ru ? "Результат не найден" : "Result not found" }
    static var tarotSpreadResultBackToTarot: String { ru ? "К таро" : "Back to Tarot" }
    static var tarotSpreadResultShareTitle: String { ru ? "Таро" : "Tarot" }
    static var tarotSpreadResultShareText: String { ru ? "Результат расклада" : "Spread result" }
    static var tarotSpreadResultToastLinkCopied: String { ru ? "Ссылка скопирована" : "Link copied" }
    static var tarotSpreadResultToastFavoriteAdded: String { ru ? "В избранном" : "Saved to favorites" }
    static var tarotSpreadResultToastFavoriteRemoved: String { ru ? "Убрано из избранного" : "Removed from favorites" }
    static var tarotSpreadResultToastFavoriteFailed: String {
        ru ? "Не удалось обновить избранное" : "Couldn’t update favorites"
    }
    static var tarotSpreadResultFavoriteSaving: String { ru ? "Сохранение…" : "Saving…" }
    static var tarotSpreadResultFavoriteAdd: String { ru ? "В избранное" : "Add to favorites" }
    static var tarotSpreadResultFavoriteRemove: String { ru ? "Убрать из избранного" : "Remove from favorites" }
    static var tarotSpreadResultDefaultSpreadTitle: String { ru ? "Расклад" : "Spread" }
    static var tarotSpreadResultQuestionPrefix: String { ru ? "Вопрос:" : "Question:" }
    static var tarotSpreadResultProfileFallbackFocus: String {
        ru
            ? "Фокус на ближайший шаг, не на «ответ навсегда»."
            : "Focus on the next small step, not a “forever answer.”"
    }
    static var tarotSpreadResultKeyMeaningFallback: String {
        ru ? "Главный смысл — в формулировках ниже." : "The main meaning is in the sections below."
    }
    static var tarotSpreadResultManifestationOneCard: String {
        ru
            ? "Один шаг, разговор или решение — без бесконечных откладываний."
            : "One step, one conversation, or one decision—without endless postponing."
    }
    static var tarotSpreadResultManifestationThreeCards: String {
        ru ? "Линия: прошлое · сейчас · как действуешь дальше." : "A line: past · now · how you move next."
    }
    static var tarotSpreadResultCautionDefault: String {
        ru ? "Не превращать расклад в приговор — ищи один точный шаг." : "Don’t turn the spread into a verdict—look for one precise step."
    }
    static var tarotSpreadResultNextStepOneCard: String {
        ru ? "Сверься с картой дня по тону." : "Check the card of the day for the tone."
    }
    static var tarotSpreadResultNextStepThreeCards: String {
        ru ? "Проверь в Today, как линия ложится на день." : "See in Today how the line fits your day."
    }
    static var tarotSpreadResultNextStepLabelCardOfDay: String { ru ? "Карта дня" : "Card of the day" }
    static var tarotSpreadResultNextStepLabelToday: String { ru ? "Я сегодня" : "My Today" }
    static var tarotSpreadResultReturnSpreadOneCard: String { ru ? "Ещё одна карта" : "Another single card" }
    static var tarotSpreadResultReturnSpreadThreeCards: String { ru ? "Три карты снова" : "Three cards again" }
    static var tarotSpreadResultSectionProfile: String { ru ? "Профиль" : "Profile" }
    static var tarotSpreadResultSectionNext: String { ru ? "Дальше" : "Next" }
    static var tarotSpreadResultJournal: String { ru ? "Журнал" : "Journal" }
    static var tarotSpreadResultThreeCardsCta: String { ru ? "Три карты" : "Three cards" }
    static var tarotSpreadResultShare: String { ru ? "Поделиться" : "Share" }
    static var tarotSpreadResultPositionDetailsSummary: String { ru ? "Ещё по позициям" : "More by positions" }
    static var tarotSpreadResultPositionSingleCard: String { ru ? "Карта" : "Card" }
    static var tarotSpreadResultModeLabel: String { ru ? "Таро" : "Tarot" }
    static var tarotSpreadResultProfileHintWithProfile: String { ru ? "С учётом профиля" : "With profile in mind" }
    static var tarotSpreadResultOrientationSubtitleUpright: String { ru ? "Прямое положение" : "Upright" }
    static var tarotSpreadResultOrientationSubtitleReversed: String { ru ? "Перевёрнутое положение" : "Reversed" }

    /// Паритет `tarotSpreadResultResolvePositionLabel` (известные id → i18n; иначе заголовок с API или id).
    static func tarotSpreadResultPositionLabel(id: String, apiTitle: String?) -> String {
        let mapped: String? = switch id {
        case "past": ru ? "Прошлое" : "Past"
        case "present": ru ? "Настоящее" : "Present"
        case "future": ru ? "Будущее" : "Future"
        case "answer": ru ? "Ответ" : "Answer"
        case "situation": ru ? "Ситуация" : "Situation"
        case "action": ru ? "Действие" : "Action"
        case "outcome": ru ? "Результат" : "Outcome"
        default: nil
        }
        if let mapped { return mapped }
        if let t = apiTitle?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty { return t }
        return id
    }
}
