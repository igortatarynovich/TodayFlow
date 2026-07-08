import Foundation

struct TodayCycle: Codable {
    let date: String
    let morning: TodayMorning?
    let morningCompleted: Bool
    let dayConnection: TodayDayConnection?
    let dayTrackers: [TodayTracker]
    let dayJournalEntries: [TodayJournalEntry]
    let dayCompleted: Bool
    let evening: TodayEvening?
    let eveningCompleted: Bool
    let morningAvailable: Bool
    let dayAvailable: Bool
    let eveningAvailable: Bool
    let coreProfile: TodayCoreProfile?
    let consistency: TodayConsistency?
    let rewards: TodayRewardsSnapshot?
    let rewardMilestones: [TodayRewardMilestone]?

    enum CodingKeys: String, CodingKey {
        case date
        case morning
        case morningCompleted = "morning_completed"
        case dayConnection = "day_connection"
        case dayTrackers = "day_trackers"
        case dayJournalEntries = "day_journal_entries"
        case dayCompleted = "day_completed"
        case evening
        case eveningCompleted = "evening_completed"
        case morningAvailable = "morning_available"
        case dayAvailable = "day_available"
        case eveningAvailable = "evening_available"
        case coreProfile = "core_profile"
        case consistency
        case rewards
        case rewardMilestones = "reward_milestones"
    }

    /// Короткие строки для `ritual_context.day_events` в POST /today/narrative (guide).
    func dayEventsForNarrative() -> [String] {
        var out: [String] = []
        if let f = dayConnection?.morningFocus?.trimmingCharacters(in: .whitespacesAndNewlines), !f.isEmpty,
           !TodayCycle.isDiscardableMorningFocus(f)
        {
            out.append("Фокус утра: \(String(f.prefix(160)))")
        }
        if let i = dayConnection?.morningIntention?.trimmingCharacters(in: .whitespacesAndNewlines), !i.isEmpty {
            out.append("Намерение: \(String(i.prefix(160)))")
        }
        for t in dayTrackers.prefix(14) {
            let bits = [t.type, t.note]
                .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
            let line = bits.joined(separator: " · ")
            if !line.isEmpty {
                out.append("Шаг дня: \(String(line.prefix(200)))")
            }
        }
        if !dayJournalEntries.isEmpty {
            out.append("Дневник: записей сегодня — \(dayJournalEntries.count)")
        }
        if dayConnection?.dayCompleted == true {
            out.append("Дневной цикл отмечен как завершённый")
        }
        return Array(out.prefix(24))
    }

    /// Паритет с веб `isDiscardableMorningFocus`: не слать сырой slug в LLM как «фокус».
    private static func isDiscardableMorningFocus(_ focus: String) -> Bool {
        let t = focus.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if t.count < 2 { return true }
        let junk: Set<String> = [
            "general", "overall", "mixed", "none", "other", "default",
            "общее", "прочее", "другое", "без фокуса",
        ]
        if junk.contains(t) { return true }
        if t.range(of: "^[a-z_]{1,20}$", options: .regularExpression) != nil {
            return true
        }
        return false
    }
}

struct TodayRewardsSnapshot: Codable {
    let archetypeSeed: String?
    let archetypeLevel: String
    let archetypeProgress: TodayArchetypeProgress?
    let streaks: TodayRewardStreaks
    let scores: TodayRewardScores
    let evolutionIndex: Int
    let rewardEvolutionIndexPeak: Int?
    let rewardRingsEarned: [String]?
    let seals: [TodayRewardSeal]
    let message: String

    enum CodingKeys: String, CodingKey {
        case archetypeSeed = "archetype_seed"
        case archetypeLevel = "archetype_level"
        case archetypeProgress = "archetype_progress"
        case streaks
        case scores
        case evolutionIndex = "evolution_index"
        case rewardEvolutionIndexPeak = "reward_evolution_index_peak"
        case rewardRingsEarned = "reward_rings_earned"
        case seals
        case message
    }
}

struct TodayArchetypeProgress: Codable {
    let current: String?
    let next: String?
    let progressPct: Int?

    enum CodingKeys: String, CodingKey {
        case current
        case next
        case progressPct = "progress_pct"
    }
}

struct TodayRewardStreaks: Codable {
    let dailyCurrent: Int
    let weeklyCurrent: Int
    let habitBest: Int
    let asceticBest: Int
    let tarotCurrent: Int

    enum CodingKeys: String, CodingKey {
        case dailyCurrent = "daily_current"
        case weeklyCurrent = "weekly_current"
        case habitBest = "habit_best"
        case asceticBest = "ascetic_best"
        case tarotCurrent = "tarot_current"
    }
}

struct TodayRewardScores: Codable {
    let mind: Int
    let energy: Int
    let discipline: Int
    let reflection: Int
}

struct TodayRewardSeal: Codable, Identifiable {
    let code: String
    let title: String
    let strength: Int

    var id: String { code }
}

struct TodayRewardMilestone: Codable, Identifiable {
    let name: String
    let targetDays: Int
    let status: String
    let daysLeft: Int

    var id: String { name }

    enum CodingKeys: String, CodingKey {
        case name
        case targetDays = "target_days"
        case status
        case daysLeft = "days_left"
    }
}

struct TodayNumerologyExplanation: Codable {
    let meaning: String?
    let summary: String?
    let whyThisNumber: String?
    let howDayLooks: String?

    enum CodingKeys: String, CodingKey {
        case meaning
        case summary
        case whyThisNumber = "why_this_number"
        case howDayLooks = "how_day_looks"
    }
}

struct TodayMorning: Codable {
    let tarotCard: TodayTarotCard?
    let numerologyNumber: TodayNumerologyNumber?
    let numerologyExplanation: TodayNumerologyExplanation?
    let dailyForecastSummary: TodayDailyForecastSummary?
    let dailyHoroscope: TodayDailyHoroscope?
    let dailyRecommendations: TodayDailyRecommendations?
    /// Паритет с веб `morning.decision_engine` — оценка энергии для того же fallback, что `guideHeadline`.
    let decisionEngine: TodayMorningDecisionEngine?
    /// Паритет с веб `morningRitualData.celestial_events` — для блока «Почему так?» (луна).
    let celestialEvents: TodayCelestialEvents?

    enum CodingKeys: String, CodingKey {
        case tarotCard = "tarot_card"
        case numerologyNumber = "numerology_number"
        case numerologyExplanation = "numerology_explanation"
        case dailyForecastSummary = "daily_forecast_summary"
        case dailyHoroscope = "daily_horoscope"
        case dailyRecommendations = "daily_recommendations"
        case decisionEngine = "decision_engine"
        case celestialEvents = "celestial_events"
    }
}

struct TodayMorningDecisionEngine: Codable {
    let hero: TodayMorningDecisionHero?
}

struct TodayMorningDecisionHero: Codable {
    let energyScore: Int?

    enum CodingKeys: String, CodingKey {
        case energyScore = "energy_score"
    }
}

struct TodayCelestialEvents: Codable {
    let lunarPhase: TodayLunarPhaseBrief?
    let retrogrades: [TodayRetrogradeEvent]?
    let skyAspects: [TodaySkyAspectEvent]?
    let personalTransits: [TodayPersonalTransitEvent]?
    let ingresses: [TodayIngressEvent]?
    let dailySymbols: TodayDailySymbols?

    enum CodingKeys: String, CodingKey {
        case lunarPhase = "lunar_phase"
        case retrogrades
        case skyAspects = "sky_aspects"
        case personalTransits = "personal_transits"
        case ingresses
        case dailySymbols = "daily_symbols"
    }
}

struct TodayRetrogradeEvent: Codable, Identifiable {
    let planet: String?
    let planetRu: String?
    let storyRu: String?

    var id: String { planet ?? planetRu ?? UUID().uuidString }

    enum CodingKeys: String, CodingKey {
        case planet
        case planetRu = "planet_ru"
        case storyRu = "story_ru"
    }
}

struct TodaySkyAspectEvent: Codable, Identifiable {
    let eventId: String?
    let title: String?
    let storyRu: String?

    var id: String { eventId ?? title ?? UUID().uuidString }

    enum CodingKeys: String, CodingKey {
        case eventId = "id"
        case title
        case storyRu = "story_ru"
    }
}

struct TodayPersonalTransitEvent: Codable, Identifiable {
    let eventId: String?
    let title: String?
    let storyRu: String?

    var id: String { eventId ?? title ?? UUID().uuidString }

    enum CodingKeys: String, CodingKey {
        case eventId = "id"
        case title
        case storyRu = "story_ru"
    }
}

struct TodayIngressEvent: Codable, Identifiable {
    let planetRu: String?
    let signRu: String?
    let storyRu: String?

    var id: String { "\(planetRu ?? "")-\(signRu ?? "")" }

    enum CodingKeys: String, CodingKey {
        case planetRu = "planet_ru"
        case signRu = "sign_ru"
        case storyRu = "story_ru"
    }
}

struct TodayDailySymbols: Codable {
    let color: TodayDailySymbolItem?
    let stone: TodayDailySymbolItem?
    let totem: TodayDailyTotem?
}

struct TodayDailySymbolItem: Codable {
    let name: String?
    let storyRu: String?

    enum CodingKeys: String, CodingKey {
        case name
        case storyRu = "story_ru"
    }
}

struct TodayDailyTotem: Codable, Identifiable {
    let totemId: String?
    let name: String?
    let emoji: String?
    let storyRu: String?

    var id: String { totemId ?? name ?? UUID().uuidString }

    enum CodingKeys: String, CodingKey {
        case totemId = "id"
        case name
        case emoji
        case storyRu = "story_ru"
    }
}

struct TodayLunarPhaseBrief: Codable {
    let name: String?
    /// Строка тем (как в API morning ritual).
    let themes: String?
}

struct TodayTarotCard: Codable {
    let name: String?
}

struct TodayNumerologyNumber: Codable {
    let value: Int?
    let reducedValue: Int?
    let title: String?

    enum CodingKeys: String, CodingKey {
        case value
        case reducedValue = "reduced_value"
        case title
    }
}

struct TodayDailyForecastSummary: Codable {
    let summary: String?
}

struct TodayDailyHoroscope: Codable {
    let headline: String?
    let profilePrism: String?
    let spine: TodayDailySpine?

    enum CodingKeys: String, CodingKey {
        case headline
        case profilePrism = "profile_prism"
        case spine
    }
}

struct TodayDailySpine: Codable {
    let dayAxis: String?
    let mainRisk: String?
    let bestMode: String?
    let firstMove: String?
    let doNotEnter: String?

    enum CodingKeys: String, CodingKey {
        case dayAxis = "day_axis"
        case mainRisk = "main_risk"
        case bestMode = "best_mode"
        case firstMove = "first_move"
        case doNotEnter = "do_not_enter"
    }
}

struct TodayDailyRecommendations: Codable {
    let whatToDo: String?
    let whatToAvoid: String?
    let priorities: [String]?

    enum CodingKeys: String, CodingKey {
        case whatToDo = "what_to_do"
        case whatToAvoid = "what_to_avoid"
        case priorities
    }
}

struct TodayDayConnection: Codable {
    let morningIntention: String?
    /// Паритет с веб `todayData.day_connection.morning_focus` для «Почему так?».
    let morningFocus: String?
    let eveningReflection: String?
    let eveningObservations: TodayEveningObservations?
    let connectionThread: String?
    let morningCompleted: Bool
    let dayCompleted: Bool
    let eveningCompleted: Bool

    enum CodingKeys: String, CodingKey {
        case morningIntention = "morning_intention"
        case morningFocus = "morning_focus"
        case eveningReflection = "evening_reflection"
        case eveningObservations = "evening_observations"
        case connectionThread = "connection_thread"
        case morningCompleted = "morning_completed"
        case dayCompleted = "day_completed"
        case eveningCompleted = "evening_completed"
    }
}

struct TodayEveningObservations: Codable {
    let noticed: String?
    let hardest: String?
    let easierThanExpected: String?

    enum CodingKeys: String, CodingKey {
        case noticed
        case hardest
        case easierThanExpected = "easier_than_expected"
    }
}

struct TodayTracker: Codable, Identifiable {
    let id: Int
    let date: String?
    let type: String?
    let completed: Bool?
    let state: String?
    let stateScale: Int?
    let note: String?

    enum CodingKeys: String, CodingKey {
        case id
        case date
        case type
        case completed
        case state
        case stateScale = "state_scale"
        case note
    }
}

struct TodayJournalEntry: Codable, Identifiable {
    let id: Int
    let type: String?
    let content: String
}

struct TodayEvening: Codable {
    let completed: Bool?
    let closingPhraseText: String?

    enum CodingKeys: String, CodingKey {
        case completed
        case closingPhraseText = "closing_phrase_text"
    }
}

struct TodayCoreProfile: Codable {
    let firstName: String?
    let sunSign: String?
    let lifePath: String?
    let archetype: String?

    enum CodingKeys: String, CodingKey {
        case firstName = "first_name"
        case sunSign = "sun_sign"
        case lifePath = "life_path"
        case archetype
    }
}

struct TodayConsistency: Codable {
    let summary: String?
    let doFocus: String?
    let avoidFocus: String?

    enum CodingKeys: String, CodingKey {
        case summary
        case doFocus = "do_focus"
        case avoidFocus = "avoid_focus"
    }
}

extension TodayCycle {
    var formattedDateTitle: String {
        guard let parsedDate = Self.apiDateFormatter.date(from: date) else {
            return date
        }
        return parsedDate.dayHeaderTitle
    }

    private static let apiDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
}
