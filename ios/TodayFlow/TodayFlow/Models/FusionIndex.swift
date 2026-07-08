import Foundation

/// DE-9: `day_history_v0` из `GET /tracking/fusion/{date}` (паритет веб `FusionDayHistoryV0`).
struct FusionDayHistoryV0: Codable {
    struct AxisScores: Codable {
        var energy: Int
        var emotionalBalance: Int
        var focus: Int

        enum CodingKeys: String, CodingKey {
            case energy, focus
            case emotionalBalance = "emotional_balance"
        }

        init(from decoder: Decoder) throws {
            let c = try decoder.container(keyedBy: CodingKeys.self)
            energy = Self.clamp0_100(try c.decodeIfPresent(Int.self, forKey: .energy))
            emotionalBalance = Self.clamp0_100(try c.decodeIfPresent(Int.self, forKey: .emotionalBalance))
            focus = Self.clamp0_100(try c.decodeIfPresent(Int.self, forKey: .focus))
        }

        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            try c.encode(energy, forKey: .energy)
            try c.encode(emotionalBalance, forKey: .emotionalBalance)
            try c.encode(focus, forKey: .focus)
        }

        private static func clamp0_100(_ raw: Int?) -> Int {
            let v = raw ?? 50
            return max(0, min(100, v))
        }
    }

    struct AxisDelta: Codable {
        var energy: Int
        var emotionalBalance: Int
        var focus: Int

        enum CodingKeys: String, CodingKey {
            case energy, focus
            case emotionalBalance = "emotional_balance"
        }

        init(from decoder: Decoder) throws {
            let c = try decoder.container(keyedBy: CodingKeys.self)
            energy = try c.decodeIfPresent(Int.self, forKey: .energy) ?? 0
            emotionalBalance = try c.decodeIfPresent(Int.self, forKey: .emotionalBalance) ?? 0
            focus = try c.decodeIfPresent(Int.self, forKey: .focus) ?? 0
        }

        func encode(to encoder: Encoder) throws {
            var c = encoder.container(keyedBy: CodingKeys.self)
            try c.encode(energy, forKey: .energy)
            try c.encode(emotionalBalance, forKey: .emotionalBalance)
            try c.encode(focus, forKey: .focus)
        }
    }

    struct ReflectionExcerpt: Codable {
        let contractVersion: String?
        let eveningReflection: String?
        let eveningObservations: [String: String]?
        let morningIntention: String?
        let hasReflection: Bool?

        enum CodingKeys: String, CodingKey {
            case contractVersion = "contract_version"
            case eveningReflection = "evening_reflection"
            case eveningObservations = "evening_observations"
            case morningIntention = "morning_intention"
            case hasReflection = "has_reflection"
        }
    }

    struct Yesterday: Codable {
        let date: String
        let fusionScores: AxisScores
        let dayFlow: DayFlowFlags?
        let meaningDaySignals: [String: Int]?
        let meaningCompletionsTotal: Int?
        let meaningActive: Bool?
        let reflectionExcerpt: ReflectionExcerpt?

        enum CodingKeys: String, CodingKey {
            case date
            case fusionScores = "fusion_scores"
            case dayFlow = "day_flow"
            case meaningDaySignals = "meaning_day_signals"
            case meaningCompletionsTotal = "meaning_completions_total"
            case meaningActive = "meaning_active"
            case reflectionExcerpt = "reflection_excerpt"
        }
    }

    struct DayFlowFlags: Codable {
        let morningCompleted: Bool?
        let dayCompleted: Bool?
        let eveningCompleted: Bool?

        enum CodingKeys: String, CodingKey {
            case morningCompleted = "morning_completed"
            case dayCompleted = "day_completed"
            case eveningCompleted = "evening_completed"
        }
    }

    /// DE-9 v1.2: `trailing_7d_summary` из `history_layer_v0` (паритет веб `FusionDayHistoryV0`).
    struct Trailing7dAxisAgg: Codable {
        let avg: Double
        let min: Int
        let max: Int
        let days: Int
    }

    struct Trailing7dSummary: Codable {
        let energy: Trailing7dAxisAgg
        let emotionalBalance: Trailing7dAxisAgg
        let focus: Trailing7dAxisAgg

        enum CodingKeys: String, CodingKey {
            case energy
            case emotionalBalance = "emotional_balance"
            case focus
        }
    }

    let contractVersion: String
    let yesterday: Yesterday
    let fusionScoreDeltaVsYesterday: AxisDelta
    let trailing7dSummary: Trailing7dSummary?
    /// O7: `false`, если вчера не было отметок Flow под формулу fusion; `nil` — старые ответы API (считаем true).
    let fusionScoreDeltaTrustworthy: Bool?
    /// O7: `false` — неделя из дефолтных баллов без отметок; не показывать вторую строку.
    let trailing7dSummaryTrustworthy: Bool?
    let trailing7dFlowDays: Int?

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case yesterday
        case fusionScoreDeltaVsYesterday = "fusion_score_delta_vs_yesterday"
        case trailing7dSummary = "trailing_7d_summary"
        case fusionScoreDeltaTrustworthy = "fusion_score_delta_trustworthy"
        case trailing7dSummaryTrustworthy = "trailing_7d_summary_trustworthy"
        case trailing7dFlowDays = "trailing_7d_flow_days"
    }
}

struct FusionIndex: Codable {
    let date: String
    let scores: FusionScores
    let cycleContext: FusionCycleContext
    let activityContext: FusionActivityContext
    /// Сводка ритма для narrative / профиля (цели, привычки, аскезы, дневник).
    let rhythmContext: FusionRhythmContext?
    let recommendations: [String]
    let encouragement: String
    /// DE-9: вчера + дельта к сегодняшним scores.
    let dayHistory: FusionDayHistoryV0?

    enum CodingKeys: String, CodingKey {
        case date
        case scores
        case cycleContext = "cycle_context"
        case activityContext = "activity_context"
        case rhythmContext = "rhythm_context"
        case recommendations
        case encouragement
        case dayHistory = "day_history"
    }
}

struct FusionRhythmContext: Codable {
    struct GoalSnippet: Codable {
        let title: String
        let scope: String
        let completed: Bool
    }

    struct HabitSnippet: Codable {
        let name: String
        let category: String?
        let frequency: String
        let completedToday: Bool

        enum CodingKeys: String, CodingKey {
            case name
            case category
            case frequency
            case completedToday = "completed_today"
        }
    }

    struct AsceticSnippet: Codable {
        let title: String
        let streakDays: Int
        let completedToday: Bool

        enum CodingKeys: String, CodingKey {
            case title
            case streakDays = "streak_days"
            case completedToday = "completed_today"
        }
    }

    struct DiarySnippet: Codable {
        let hasEntryToday: Bool
        let entriesLast7Days: Int

        enum CodingKeys: String, CodingKey {
            case hasEntryToday = "has_entry_today"
            case entriesLast7Days = "entries_last_7_days"
        }
    }

    let goals: [GoalSnippet]
    let habits: [HabitSnippet]
    let ascetics: [AsceticSnippet]
    let diary: DiarySnippet
}

struct FusionScores: Codable, Hashable {
    let energy: Int
    let emotionalBalance: Int
    let focus: Int

    enum CodingKeys: String, CodingKey {
        case energy
        case emotionalBalance = "emotional_balance"
        case focus
    }
}

enum FusionAxis: CaseIterable, Identifiable {
    case energy
    case emotionalBalance
    case focus

    var id: Self { self }

    var title: String {
        switch self {
        case .energy:
            return "Энергия"
        case .emotionalBalance:
            return "Баланс"
        case .focus:
            return "Фокус"
        }
    }
}

struct FusionCycleContext: Codable {
    let tracked: Bool
    let cycleDay: Int?
    let periodIntensity: String?
    let ovulation: Bool
    let fertileWindow: Bool

    enum CodingKeys: String, CodingKey {
        case tracked
        case cycleDay = "cycle_day"
        case periodIntensity = "period_intensity"
        case ovulation
        case fertileWindow = "fertile_window"
    }
}

struct FusionActivityContext: Codable {
    let practiceCount: Int
    let moodAverage: Double?
    let ritualCompleted: Bool
    let diaryDone: Bool
    let asceticCompleted: Bool
    let affirmationCompleted: Bool
    /// DE-7 v2: server-side counts of «done» meaning_events for the day (`habit_completed`, …).
    let guideMeaningCompletionsToday: [String: Int]?

    enum CodingKeys: String, CodingKey {
        case practiceCount = "practice_count"
        case moodAverage = "mood_avg"
        case ritualCompleted = "ritual_completed"
        case diaryDone = "diary_done"
        case asceticCompleted = "ascetic_completed"
        case affirmationCompleted = "affirmation_completed"
        case guideMeaningCompletionsToday = "guide_meaning_completions_today"
    }
}

extension FusionScores {
    var average: Int {
        Int(round(Double(energy + emotionalBalance + focus) / 3.0))
    }

    func value(for axis: FusionAxis) -> Int {
        switch axis {
        case .energy:
            return energy
        case .emotionalBalance:
            return emotionalBalance
        case .focus:
            return focus
        }
    }
}

extension Array where Element == FusionIndex {
    var orderedFusionHistory: [FusionIndex] {
        sorted { $0.date < $1.date }
    }

    var currentFusion: FusionIndex? {
        orderedFusionHistory.last
    }

    func scoreDelta(for axis: FusionAxis) -> Int {
        let history = orderedFusionHistory
        guard let first = history.first, let last = history.last else { return 0 }
        return last.scores.value(for: axis) - first.scores.value(for: axis)
    }

    var overallScoreDelta: Int {
        guard let first = orderedFusionHistory.first, let last = orderedFusionHistory.last else { return 0 }
        return last.scores.average - first.scores.average
    }

    var strongestAxis: FusionAxis? {
        guard let currentFusion else { return nil }
        return FusionAxis.allCases.max { lhs, rhs in
            currentFusion.scores.value(for: lhs) < currentFusion.scores.value(for: rhs)
        }
    }

    var weakestAxis: FusionAxis? {
        guard let currentFusion else { return nil }
        return FusionAxis.allCases.min { lhs, rhs in
            currentFusion.scores.value(for: lhs) < currentFusion.scores.value(for: rhs)
        }
    }

    var overallTrendHeadline: String {
        let delta = overallScoreDelta
        switch delta {
        case 9...:
            return "Состояние собирается вверх"
        case 3...8:
            return "Есть мягкое выравнивание"
        case -2...2:
            return "День держится без резких качелей"
        case -8 ... -3:
            return "Есть просадка, нужен более бережный темп"
        default:
            return "Контур дня заметно просел"
        }
    }

    var repeatedRiskPattern: String {
        let history = orderedFusionHistory.suffix(3)
        guard !history.isEmpty else {
            return "Нужно ещё несколько сигналов, чтобы увидеть устойчивый риск."
        }

        if history.allSatisfy({ $0.scores.energy < 48 }) {
            return "Энергия держится ниже опоры уже несколько дней подряд."
        }

        if history.allSatisfy({ $0.scores.focus < 52 }) {
            return "Фокус распадается повторно, поэтому день лучше собирать вокруг одного хода."
        }

        if history.allSatisfy({ $0.scores.emotionalBalance < 50 }) {
            return "Эмоциональный баланс остаётся хрупким, не стоит перегружать день лишними задачами."
        }

        if let weakestAxis {
            return "\(weakestAxis.title) сейчас слабее остальных осей и требует самого бережного обращения."
        }

        return "Повторяющийся риск пока не оформился, но история уже начинает собираться."
    }

    var correlationInsight: String {
        let history = orderedFusionHistory
        guard history.count >= 3 else {
            return "Чем регулярнее ты отмечаешь состояние и оставляешь записи, тем точнее подсказки подстраиваются под твой ритм."
        }

        let journalDays = history.filter { $0.activityContext.diaryDone }
        let nonJournalDays = history.filter { !$0.activityContext.diaryDone }
        if let journalAverage = journalDays.meanScore(for: .emotionalBalance),
           let nonJournalAverage = nonJournalDays.meanScore(for: .emotionalBalance),
           journalDays.count >= 2,
           nonJournalDays.count >= 1,
           journalAverage - nonJournalAverage >= 6 {
            return "В дни с дневниковой записью эмоциональный баланс у тебя заметно выше."
        }

        let practiceDays = history.filter { $0.activityContext.practiceCount > 0 }
        let passiveDays = history.filter { $0.activityContext.practiceCount == 0 }
        if let practiceAverage = practiceDays.meanScore(for: .focus),
           let passiveAverage = passiveDays.meanScore(for: .focus),
           practiceDays.count >= 2,
           passiveDays.count >= 1,
           practiceAverage - passiveAverage >= 6 {
            return "Когда у тебя есть практика, фокус держится ощутимо лучше."
        }

        if history.suffix(3).allSatisfy({ $0.activityContext.diaryDone || $0.activityContext.practiceCount > 0 }) {
            return "Последние дни ты даёшь системе устойчивый сигнал, поэтому карта состояния становится заметно точнее."
        }

        return "Сейчас сильнее всего на карту влияет регулярность: один pulse-check и одна запись уже меняют качество интерпретации."
    }

    private func meanScore(for axis: FusionAxis) -> Double? {
        guard !isEmpty else { return nil }
        let total = reduce(0) { partialResult, item in
            partialResult + item.scores.value(for: axis)
        }
        return Double(total) / Double(count)
    }
}
