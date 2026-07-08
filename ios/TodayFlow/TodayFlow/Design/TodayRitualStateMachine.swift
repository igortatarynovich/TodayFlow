import Foundation

// MARK: - Snapshot (единственный источник правды для фазы — те же флаги, что persistence + UI)

/// Срез главного хребта ритуала Today: карта → число → настроение → «Готово» → «Твой день».
/// Должен собираться из `@State` / persistence без «догадок» UI.
struct TodayRitualSpineSnapshot: Equatable {
    var dayOpened: Bool
    var tarotContinueAck: Bool
    var numberRevealed: Bool
    var tarotMainId: Int?
    /// Есть запись в каталоге для `tarotMainId` (как `drawnTarotMain != nil` во `TodayRitualFlowView`).
    var tarotMainResolved: Bool
    var selectedMoodId: String?
    var checkInSubmitted: Bool
    /// Пока грузится персональный нарратив после чек-ина (передаётся с родителя).
    var guideNarrativeLoading: Bool

    /// Паритет с `ritualSpineComplete` / `isRitualSpineComplete` (веб `todayRitualPersisted.ts`) — явный `tarotContinueAck`.
    var isSpineComplete: Bool {
        tarotMainResolved && tarotContinueAck && numberRevealed && selectedMoodId != nil && checkInSubmitted
    }
}

// MARK: - Phases

/// Формальные фазы главного хребта (без под-шагов «глубины» карты — их закрывает `RitualTarotPickMiniFlow`).
enum TodayRitualSpinePhase: Equatable {
    case notStarted
    case tarotInteractive
    case numberSelecting
    case checkIn
    /// `isNarrativeRefreshing` — момент после «Готово», пока бэкенд собирает текст (внимание / лоадер — на усмотрение UI).
    case dayReady(isNarrativeRefreshing: Bool)

    var analyticsStepLabel: String {
        switch self {
        case .notStarted: return "not_started"
        case .tarotInteractive: return "tarot_interactive"
        case .numberSelecting: return "number_selecting"
        case .checkIn: return "check_in"
        case .dayReady(let loading): return loading ? "day_ready_refreshing" : "day_ready"
        }
    }
}

// MARK: - User events (то, что пользователь *сделал* — один шаг контракта)

enum TodayRitualSpineUserEvent: Equatable {
    /// Тап «Открыть день» / восстановление opened-day из persistence.
    case openedDay
    /// Зафиксировал карту и нажал «Продолжить» к числу.
    case continuedPastTarot
    /// Выбрал число дня (цветок / орбита).
    case revealedNumber
    /// Выбрал настроение (ещё не «Готово»).
    case selectedMood(String)
    /// Чек-ин отправлен, стартует запрос нарратива.
    case submittedCheckIn
}

// MARK: - Machine

enum TodayRitualSpinePhaseResolver {
    static func phase(for snapshot: TodayRitualSpineSnapshot) -> TodayRitualSpinePhase {
        guard snapshot.dayOpened else { return .notStarted }
        guard !snapshot.isSpineComplete else {
            return .dayReady(isNarrativeRefreshing: snapshot.guideNarrativeLoading)
        }
        if !snapshot.tarotContinueAck { return .tarotInteractive }
        if !snapshot.numberRevealed { return .numberSelecting }
        return .checkIn
    }

    /// Невозможные комбинации флагов (баг, гонка, битый кэш). UI может скрывать блоки, но это сигнал в лог.
    static func consistencyIssues(_ s: TodayRitualSpineSnapshot) -> [String] {
        var issues: [String] = []
        if s.tarotContinueAck && !s.dayOpened {
            issues.append("tarot_continue_without_opened_day")
        }
        if s.numberRevealed && !s.dayOpened {
            issues.append("number_without_opened_day")
        }
        if s.checkInSubmitted && !s.numberRevealed {
            issues.append("checkin_without_number")
        }
        if s.checkInSubmitted, s.selectedMoodId == nil {
            issues.append("checkin_without_mood")
        }
        if s.isSpineComplete, !s.tarotMainResolved {
            issues.append("spine_complete_without_resolved_tarot")
        }
        return issues
    }
}

// MARK: - Transitions (запрет «перепрыгивания»)

enum TodayRitualSpineTransition {
    /// Можно ли применить событие **в текущем** снимке (до мутации состояния).
    static func allows(_ event: TodayRitualSpineUserEvent, snapshot before: TodayRitualSpineSnapshot) -> Bool {
        let phase = TodayRitualSpinePhaseResolver.phase(for: before)
        switch event {
        case .openedDay:
            return phase == .notStarted && !before.dayOpened
        case .continuedPastTarot:
            return phase == .tarotInteractive && before.dayOpened && !before.tarotContinueAck
        case .revealedNumber:
            return phase == .numberSelecting && before.tarotContinueAck && !before.numberRevealed
        case .selectedMood:
            return before.numberRevealed && !before.checkInSubmitted
        case .submittedCheckIn:
            guard before.numberRevealed, !before.checkInSubmitted, before.selectedMoodId != nil else { return false }
            return before.tarotMainResolved
        }
    }

    #if DEBUG
    static func assertAllows(_ event: TodayRitualSpineUserEvent, snapshot before: TodayRitualSpineSnapshot, file: StaticString = #fileID, line: UInt = #line) {
        assert(allows(event, snapshot: before), "Illegal ritual transition \(event) in phase \(TodayRitualSpinePhaseResolver.phase(for: before))", file: file, line: line)
    }
    #endif
}

// MARK: - Effects (побочные действия после допустимого перехода)

/// Подсказка для `trackTodaySurfaceEvent` — детали (например число дня) подставляет UI.
enum TodayRitualSpineAnalyticsHint: Equatable {
    case none
    case numberRevealed
    case moodSelected(moodId: String)
}

/// Что должен сделать слой UI / persistence после успешного `TodayRitualSpineReducer.apply`.
struct TodayRitualSpineEffects: Equatable {
    var saveOpenedDay: Bool = false
    var saveNumberRevealed: Bool = false
    var persistRitualExtras: Bool = false
    /// Сброс «доп. шагов» числа при первом раскрытии (паритет с текущим `TodayRitualFlowView`).
    var resetNumberExtraSteps: Bool = false
    /// Немедленный скролл (после короткой задержки на главном потоке — задаёт вызывающий).
    var scrollToAnchorId: String?
    /// Скролл только после завершения `refreshTodayNarrativeAfterRitual` (чек-ин).
    var scrollAfterNarrativeRefresh: String?
    var analyticsHint: TodayRitualSpineAnalyticsHint = .none
}

// MARK: - Reducer (снимок + событие → новый снимок + эффекты)

enum TodayRitualSpineReducer {
    /// Чистый переход: при недопустимом событии возвращает `nil` (UI не меняет хребет).
    static func apply(event: TodayRitualSpineUserEvent, to before: TodayRitualSpineSnapshot) -> (after: TodayRitualSpineSnapshot, effects: TodayRitualSpineEffects)? {
        guard TodayRitualSpineTransition.allows(event, snapshot: before) else { return nil }
        var after = before
        var effects = TodayRitualSpineEffects()
        switch event {
        case .openedDay:
            after.dayOpened = true
            effects.saveOpenedDay = true
            effects.scrollToAnchorId = "ritualDeck"
        case .continuedPastTarot:
            after.tarotContinueAck = true
            effects.persistRitualExtras = true
            effects.scrollToAnchorId = "ritualNumber"
        case .revealedNumber:
            after.numberRevealed = true
            effects.saveNumberRevealed = true
            effects.resetNumberExtraSteps = true
            effects.scrollToAnchorId = "ritualCheckin"
            effects.analyticsHint = .numberRevealed
        case .selectedMood(let id):
            after.selectedMoodId = id
            effects.persistRitualExtras = true
            effects.analyticsHint = .moodSelected(moodId: id)
        case .submittedCheckIn:
            after.checkInSubmitted = true
            effects.persistRitualExtras = true
            effects.scrollAfterNarrativeRefresh = "ritualYourDay"
        }
        return (after, effects)
    }
}

// MARK: - Interaction contract (что дальше видит пользователь и что фиксируется)

/// Одна строка UX-контракта: действие → сигнал → следующий экранный фокус.
struct TodayRitualSpineContractRow: Equatable {
    /// Событие пользователя (или системы после действия).
    let userEvent: TodayRitualSpineUserEvent
    /// Что пишем в persistence / какие поля `RitualDayExtras` / opened-day / number-revealed.
    let persistenceSummary: String
    /// Основной `ScrollViewReader` id для следующего фокуса внимания.
    let nextScrollAnchorId: String?
    /// Имя или семейство события аналитики (как в `trackTodaySurfaceEvent`).
    let analyticsKind: String?
}

enum TodayRitualSpineInteractionContract {
    /// Контракт для **текущей** фазы: что пользователь должен сделать дальше и что произойдёт.
    static func primaryPath(for phase: TodayRitualSpinePhase) -> [TodayRitualSpineContractRow] {
        switch phase {
        case .notStarted:
            return [
                TodayRitualSpineContractRow(
                    userEvent: .openedDay,
                    persistenceSummary: "opened_day_key",
                    nextScrollAnchorId: "ritualDeck",
                    analyticsKind: nil
                ),
            ]
        case .tarotInteractive:
            return [
                TodayRitualSpineContractRow(
                    userEvent: .continuedPastTarot,
                    persistenceSummary: "ritual_extras.tarotContinueAck",
                    nextScrollAnchorId: "ritualNumber",
                    analyticsKind: "tarot_selected"
                ),
            ]
        case .numberSelecting:
            return [
                TodayRitualSpineContractRow(
                    userEvent: .revealedNumber,
                    persistenceSummary: "number_revealed_key",
                    nextScrollAnchorId: "ritualCheckin",
                    analyticsKind: "number_selected"
                ),
            ]
        case .checkIn:
            return [
                TodayRitualSpineContractRow(
                    userEvent: .selectedMood("…"),
                    persistenceSummary: "ritual_extras.mood",
                    nextScrollAnchorId: nil,
                    analyticsKind: "mood_selected"
                ),
                TodayRitualSpineContractRow(
                    userEvent: .submittedCheckIn,
                    persistenceSummary: "ritual_extras.checkInSubmitted + POST today/narrative",
                    nextScrollAnchorId: "ritualYourDay",
                    analyticsKind: "checkin_complete"
                ),
            ]
        case .dayReady(let refreshing):
            if refreshing {
                return [
                    TodayRitualSpineContractRow(
                        userEvent: .submittedCheckIn,
                        persistenceSummary: "narrative_inflight",
                        nextScrollAnchorId: "ritualYourDay",
                        analyticsKind: nil
                    ),
                ]
            }
            return [
                TodayRitualSpineContractRow(
                    userEvent: .submittedCheckIn,
                    persistenceSummary: "none",
                    nextScrollAnchorId: "ritualYourDay",
                    analyticsKind: nil
                ),
            ]
        }
    }
}
