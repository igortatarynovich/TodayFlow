import Foundation

enum JSONValue: Codable, Hashable {
    case string(String)
    case number(Double)
    case bool(Bool)
    case array([JSONValue])
    case object([String: JSONValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode(Double.self) {
            self = .number(value)
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode([String: JSONValue].self) {
            self = .object(value)
        } else if let value = try? container.decode([JSONValue].self) {
            self = .array(value)
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported JSON value")
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case let .string(value):
            try container.encode(value)
        case let .number(value):
            try container.encode(value)
        case let .bool(value):
            try container.encode(value)
        case let .array(value):
            try container.encode(value)
        case let .object(value):
            try container.encode(value)
        case .null:
            try container.encodeNil()
        }
    }

    var stringValue: String? {
        if case let .string(value) = self {
            return value.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        return nil
    }

    var stringArrayValue: [String] {
        guard case let .array(values) = self else { return [] }
        return values.compactMap(\.stringValue).filter { !$0.isEmpty }
    }
}

struct TodayContractV1: Codable, Equatable {
    let contractVersion: String
    let globalContext: TodayContractGlobalContext
    let personalGrowth: TodayContractPersonalGrowth
    let domains: TodayContractDomains
    let primaryAction: String
    let progress: [String: JSONValue]?
    let generationId: String
    let dayStory: TodayContractDayStoryV1?

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case globalContext = "global_context"
        case personalGrowth = "personal_growth"
        case domains
        case primaryAction = "primary_action"
        case progress
        case generationId = "generation_id"
        case dayStory = "day_story"
    }
}

struct TodayContractGlobalContext: Codable, Equatable {
    let period: String
}

struct TodayContractPersonalGrowth: Codable, Equatable {
    let developmentPoint: String

    enum CodingKeys: String, CodingKey {
        case developmentPoint = "development_point"
    }
}

struct TodayContractDomainLens: Codable, Equatable {
    let status: String
    let opportunity: String
    let risk: String
    let action: String
}

struct TodayContractDomains: Codable, Equatable {
    let relationships: TodayContractDomainLens
    let moneyWork: TodayContractDomainLens
    let family: TodayContractDomainLens

    enum CodingKeys: String, CodingKey {
        case relationships
        case moneyWork = "money_work"
        case family
    }
}

struct TodayContractDayStoryV1: Codable, Equatable {
    let contractVersion: String
    let theme: String?
    let direction: String?
    let story: String?
    let `do`: [String]?
    let avoid: [String]?
    let advantage: String?
    let abstain: String?
    let todayMove: String?
    let talisman: [String: String]?
    let practiceRecommendation: [String: String]?
    let symbolicNote: String?

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case theme
        case direction
        case story
        case `do`
        case avoid
        case advantage
        case abstain
        case todayMove = "today_move"
        case talisman
        case practiceRecommendation = "practice_recommendation"
        case symbolicNote = "symbolic_note"
    }

    var headline: String {
        let themeText = (theme ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !themeText.isEmpty { return themeText }
        return (story ?? "").components(separatedBy: ".").first ?? ""
    }
}

enum TodayContractMapper {
    static func themeHeadline(from contract: TodayContractV1?) -> String? {
        guard let contract else { return nil }
        if let story = contract.dayStory?.headline, !story.isEmpty { return story }
        let period = contract.globalContext.period.trimmingCharacters(in: .whitespacesAndNewlines)
        return period.isEmpty ? nil : period
    }

    static func primaryAction(from contract: TodayContractV1?) -> String? {
        guard let contract else { return nil }
        let move = contract.dayStory?.todayMove?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !move.isEmpty { return move }
        let action = contract.primaryAction.trimmingCharacters(in: .whitespacesAndNewlines)
        return action.isEmpty ? nil : action
    }
}

struct ProfileContractV1: Codable, Equatable {
    let contractVersion: String
    let identityCore: String
    let strengths: [String]
    let growthZones: [String]
    let relationshipStyle: String
    let moneyStyle: String
    let decisionStyle: String
    let recurringPatterns: [String]
    let livingChanges: String?
    let profileSnapshotVersion: String?

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case identityCore = "identity_core"
        case strengths
        case growthZones = "growth_zones"
        case relationshipStyle = "relationship_style"
        case moneyStyle = "money_style"
        case decisionStyle = "decision_style"
        case recurringPatterns = "recurring_patterns"
        case livingChanges = "living_changes"
        case profileSnapshotVersion = "profile_snapshot_version"
    }
}

enum TodayNarrativeSurface: String, Codable {
    case guide
    case dayLayer = "day_layer"
    case spheres
    case evening
}

struct TodayNarrativeResponse: Codable {
    let generationID: Int
    /// Совпадает с `generation_id`; для `POST /learning/feedback` (`generation_log_id`).
    let generationLogID: Int
    let surface: String
    let usedFallback: Bool
    let payload: [String: JSONValue]
    /// Урезанный срез селектора с бэка; для эха в `metadata` learning/feedback.
    let profileSelector: [String: JSONValue]?

    enum CodingKeys: String, CodingKey {
        case generationID = "generation_id"
        case generationLogID = "generation_log_id"
        case surface
        case usedFallback = "used_fallback"
        case payload
        case profileSelector = "profile_selector"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        generationID = try c.decode(Int.self, forKey: .generationID)
        generationLogID = try c.decodeIfPresent(Int.self, forKey: .generationLogID) ?? generationID
        surface = try c.decode(String.self, forKey: .surface)
        usedFallback = try c.decode(Bool.self, forKey: .usedFallback)
        payload = try c.decode([String: JSONValue].self, forKey: .payload)
        profileSelector = try c.decodeIfPresent([String: JSONValue].self, forKey: .profileSelector)
    }
}

struct CoreProfileResponse: Codable {
    let profileVersion: String
    let generatedAt: String
    let isReady: Bool
    let missingFields: [String]
    let profileHash: String
    let person: CoreProfilePerson
    let astro: CoreProfileAstro
    let numerology: CoreProfileNumerology
    let baseline: CoreProfileBaseline
    let profiles: CoreProfileProfiles?
    let interpretation: CoreProfileInterpretation?
    let dailyInterpretation: CoreProfileDailyInterpretation?
    let profileContractV1: ProfileContractV1?
    let living: CoreProfileLiving?
    let natalSummary: CoreProfileNatalSummary?

    enum CodingKeys: String, CodingKey {
        case profileVersion = "profile_version"
        case generatedAt = "generated_at"
        case isReady = "is_ready"
        case missingFields = "missing_fields"
        case profileHash = "profile_hash"
        case person
        case astro
        case numerology
        case baseline
        case profiles
        case interpretation
        case dailyInterpretation = "daily_interpretation"
        case profileContractV1 = "profile_contract_v1"
        case living
        case natalSummary = "natal_summary"
    }
}

struct ProfileSummaryResponse: Codable {
    let generatedAt: String
    let profileHash: String
    let isReady: Bool
    let missingFields: [String]
    let displayName: String?
    let coreTrio: ProfileSummaryCoreTrio
    let baseline: CoreProfileBaseline
    let ringsPreview: [String: Int]
    let livingSummary: String?

    enum CodingKeys: String, CodingKey {
        case generatedAt = "generated_at"
        case profileHash = "profile_hash"
        case isReady = "is_ready"
        case missingFields = "missing_fields"
        case displayName = "display_name"
        case coreTrio = "core_trio"
        case baseline
        case ringsPreview = "rings_preview"
        case livingSummary = "living_summary"
    }
}

struct ProfileSummaryCoreTrio: Codable {
    let sunSign: String?
    let birthTimeKnown: Bool?
    let lifePath: Int?

    enum CodingKeys: String, CodingKey {
        case sunSign = "sun_sign"
        case birthTimeKnown = "birth_time_known"
        case lifePath = "life_path"
    }
}

struct ProfileBuildStatusResponse: Codable {
    let status: String
    let isReady: Bool
    let profileHash: String
    let generatedAt: String
    let missingFields: [String]
    let hasSnapshot: Bool

    enum CodingKeys: String, CodingKey {
        case status
        case isReady = "is_ready"
        case profileHash = "profile_hash"
        case generatedAt = "generated_at"
        case missingFields = "missing_fields"
        case hasSnapshot = "has_snapshot"
    }
}

// MARK: - Compact User Model (UMTS-2 v0)

struct CompactUserModelKnowledgeAtom: Codable, Identifiable {
    var id: String { knowledgeID ?? UUID().uuidString }
    let knowledgeID: String?
    let contractVersion: String?
    let knowledgeType: String?
    let dataClass: String?
    let claim: String?
    let claimSummary: String?
    let confidence: Double?
    let evidenceCount: Int?
    let lastConfirmedAt: String?
    let confirmationRequired: Bool?

    enum CodingKeys: String, CodingKey {
        case knowledgeID = "knowledge_id"
        case contractVersion = "contract_version"
        case knowledgeType = "knowledge_type"
        case dataClass = "data_class"
        case claim
        case claimSummary = "claim_summary"
        case confidence
        case evidenceCount = "evidence_count"
        case lastConfirmedAt = "last_confirmed_at"
        case confirmationRequired = "confirmation_required"
    }
}

struct CompactUserModelConfidence: Codable {
    let overall: Double?
    let byDomain: CompactUserModelConfidenceByDomain?
    let uncertaintyFlags: [String]?
    let delta30d: Double?
    let meaningEvents28d: Int?

    enum CodingKeys: String, CodingKey {
        case overall
        case byDomain = "by_domain"
        case uncertaintyFlags = "uncertainty_flags"
        case delta30d = "delta_30d"
        case meaningEvents28d = "meaning_events_28d"
    }
}

struct CompactUserModelConfidenceByDomain: Codable {
    let identity: Double?
    let themes: Double?
    let timing: Double?
    let recommendations: Double?
}

struct CompactUserModelRecommendationItem: Codable, Identifiable {
    var id: String { recID }
    let recID: String
    let text: String
    let timingHint: String?
    let measurable: String?
    let source: String?
    let knowledgeTypeGate: String?

    enum CodingKeys: String, CodingKey {
        case recID = "id"
        case text
        case timingHint = "timing_hint"
        case measurable
        case source
        case knowledgeTypeGate = "knowledge_type_gate"
    }
}

struct CompactUserModelRecommendations: Codable {
    let primary: CompactUserModelRecommendationItem
    let alternates: [CompactUserModelRecommendationItem]?
}

struct CompactUserModelConfidenceHistoryPoint: Codable, Identifiable {
    var id: String { snapshotDate }
    let snapshotDate: String
    let overall: Double
    let byDomain: CompactUserModelConfidenceByDomain?
    let meaningEvents28d: Int?

    enum CodingKeys: String, CodingKey {
        case snapshotDate = "snapshot_date"
        case overall
        case byDomain = "by_domain"
        case meaningEvents28d = "meaning_events_28d"
    }
}

struct CompactUserModelConfidenceHistorySummary: Codable {
    let pointCount: Int
    let overallMin: Double?
    let overallMax: Double?
    let deltaWindow: Double?

    enum CodingKeys: String, CodingKey {
        case pointCount = "point_count"
        case overallMin = "overall_min"
        case overallMax = "overall_max"
        case deltaWindow = "delta_window"
    }
}

struct CompactUserModelConfidenceHistoryResponse: Codable {
    let contractVersion: String
    let asOf: String
    let windowDays: Int
    let startDate: String
    let endDate: String
    let points: [CompactUserModelConfidenceHistoryPoint]
    let summary: CompactUserModelConfidenceHistorySummary

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case asOf = "as_of"
        case windowDays = "window_days"
        case startDate = "start_date"
        case endDate = "end_date"
        case points
        case summary
    }
}

struct CompactUserModelResponse: Codable {
    let contractVersion: String
    let asOf: String
    let generatedAt: String
    let identity: CompactUserModelIdentity
    let currentState: CompactUserModelCurrentState
    let activeThemes: [CompactUserModelTheme]
    let behavioralPatterns: CompactUserModelBehavioralPatterns
    let recommendations: CompactUserModelRecommendations?
    let knowledgeAtomsTopK: [CompactUserModelKnowledgeAtom]
    let interpretationInstancesTopK: [CompactUserModelInterpretationInstance]?
    let relationshipInsightsTopK: [CompactUserModelRelationshipInsight]?
    let confidence: CompactUserModelConfidence

    enum CodingKeys: String, CodingKey {
        case contractVersion = "contract_version"
        case asOf = "as_of"
        case generatedAt = "generated_at"
        case identity
        case currentState = "current_state"
        case activeThemes = "active_themes"
        case behavioralPatterns = "behavioral_patterns"
        case recommendations
        case knowledgeAtomsTopK = "knowledge_atoms_top_k"
        case interpretationInstancesTopK = "interpretation_instances_top_k"
        case relationshipInsightsTopK = "relationship_insights_top_k"
        case confidence
    }
}

struct CompactUserModelIdentity: Codable {
    let displayName: String?
    let sunSign: String?
    let moonSign: String?
    let risingSign: String?
    let lifePath: Int?
    let archetype: String?
    let summary: String?
    let strengths: [String]?
    let constraints: [String]?

    enum CodingKeys: String, CodingKey {
        case displayName = "display_name"
        case sunSign = "sun_sign"
        case moonSign = "moon_sign"
        case risingSign = "rising_sign"
        case lifePath = "life_path"
        case archetype
        case summary
        case strengths
        case constraints
    }
}

struct CompactUserModelCurrentState: Codable {
    let localDate: String?
    let moodID: String?
    let moodCapturedAt: String?
    let focusTopicID: String?
    let focusCapturedAt: String?

    enum CodingKeys: String, CodingKey {
        case localDate = "local_date"
        case moodID = "mood_id"
        case moodCapturedAt = "mood_captured_at"
        case focusTopicID = "focus_topic_id"
        case focusCapturedAt = "focus_captured_at"
    }
}

struct CompactUserModelTheme: Codable, Identifiable {
    var id: String { themeID }
    let themeID: String
    let weight: Double?
    let stability: String?
    let source: String?

    enum CodingKeys: String, CodingKey {
        case themeID = "id"
        case weight
        case stability
        case source
    }
}

struct CompactUserModelBehavioralPatterns: Codable {
    let works: [String]?
    let doesNotWork: [String]?
    let hints: [String]?
    let windowDays: Int?
    let totalEvents: Int?

    enum CodingKeys: String, CodingKey {
        case works
        case doesNotWork = "does_not_work"
        case hints
        case windowDays = "window_days"
        case totalEvents = "total_events"
    }
}

struct CompactUserModelInterpretationInstance: Codable, Identifiable {
    var id: String { instanceID ?? UUID().uuidString }
    let instanceID: String?
    let interpretationRefID: String?
    let level: String?
    let summary: String?
    let dominantMeaning: String?
    let confirmationRequired: Bool?
    let evidenceCount: Int?
    let userVerdict: String?

    enum CodingKeys: String, CodingKey {
        case instanceID = "instance_id"
        case interpretationRefID = "interpretation_ref_id"
        case level
        case summary
        case dominantMeaning = "dominant_meaning"
        case confirmationRequired = "confirmation_required"
        case evidenceCount = "evidence_count"
        case userVerdict = "user_verdict"
    }
}

struct CompactUserModelRelationshipInsight: Codable, Hashable, Identifiable {
    var id: String { knowledgeID ?? label }
    let knowledgeID: String?
    let kind: String?
    let label: String
    let summary: String?
    let domain: String?
    let confirmedAt: String?

    enum CodingKeys: String, CodingKey {
        case knowledgeID = "knowledge_id"
        case kind
        case label
        case summary
        case domain
        case confirmedAt = "confirmed_at"
    }
}

struct MeaningEventInput: Codable {
    let eventID: String?
    let eventType: String
    let eventSource: String
    let eventTime: String?
    let localDate: String?
    let qualityScore: Double?
    let payload: [String: JSONValue]?
    let idempotencyKey: String

    enum CodingKeys: String, CodingKey {
        case eventID = "event_id"
        case eventType = "event_type"
        case eventSource = "event_source"
        case eventTime = "event_time"
        case localDate = "local_date"
        case qualityScore = "quality_score"
        case payload
        case idempotencyKey = "idempotency_key"
    }
}

struct MeaningEventsRequest: Codable {
    let events: [MeaningEventInput]
}

struct MeaningEventsResponse: Codable {
    let accepted: Int
    let deduplicated: Int
    let total: Int
}

struct MeaningRingItem: Codable, Identifiable, Hashable {
    var id: String { ring }
    let ring: String
    let score: Int
    let trend7d: Int
    let confidence: String
    let topContributors: [String]

    enum CodingKeys: String, CodingKey {
        case ring
        case score
        case trend7d = "trend_7d"
        case confidence
        case topContributors = "top_contributors"
    }
}

struct MeaningRingsResponse: Codable {
    let windowDays: Int
    let generatedAt: String
    let rings: [MeaningRingItem]

    enum CodingKeys: String, CodingKey {
        case windowDays = "window_days"
        case generatedAt = "generated_at"
        case rings
    }
}

struct CoreProfilePerson: Codable {
    let firstName: String?
    let displayName: String?
    let locale: String?
    let gender: String?

    enum CodingKeys: String, CodingKey {
        case firstName = "first_name"
        case displayName = "display_name"
        case locale
        case gender
    }
}

struct CoreProfileAstro: Codable {
    let profileID: Int?
    let label: String?
    let relation: String?
    let birthDate: String?
    let birthTime: String?
    let timeUnknown: Bool?
    let locationName: String?
    let sunSign: String?
    let sunElement: String?
    let sunModality: String?

    enum CodingKeys: String, CodingKey {
        case profileID = "profile_id"
        case label
        case relation
        case birthDate = "birth_date"
        case birthTime = "birth_time"
        case timeUnknown = "time_unknown"
        case locationName = "location_name"
        case sunSign = "sun_sign"
        case sunElement = "sun_element"
        case sunModality = "sun_modality"
    }
}

struct CoreProfileNumerology: Codable {
    let fullName: String?
    let birthDate: String?
    let lifePath: Int?
    let expression: Int?
    let soulUrge: Int?
    let personality: Int?
    let isMasterLifePath: Bool?

    enum CodingKeys: String, CodingKey {
        case fullName = "full_name"
        case birthDate = "birth_date"
        case lifePath = "life_path"
        case expression
        case soulUrge = "soul_urge"
        case personality
        case isMasterLifePath = "is_master_life_path"
    }
}

struct CoreProfileBaseline: Codable {
    let archetypeSeed: String?
    let elementFocus: String?
    let rhythmStyle: String?

    enum CodingKeys: String, CodingKey {
        case archetypeSeed = "archetype_seed"
        case elementFocus = "element_focus"
        case rhythmStyle = "rhythm_style"
    }
}

struct CoreProfileProfiles: Codable {
    let selectedProfileID: Int?
    let primaryProfileID: Int?
    let hasMultipleProfiles: Bool?
    let items: [CoreProfileCircleItem]?

    enum CodingKeys: String, CodingKey {
        case selectedProfileID = "selected_profile_id"
        case primaryProfileID = "primary_profile_id"
        case hasMultipleProfiles = "has_multiple_profiles"
        case items
    }
}

struct CoreProfileCircleItem: Codable, Identifiable {
    let id: Int
    let label: String
    let relation: String?
    let isPrimary: Bool
    let isSelected: Bool
    let birthDate: String?
    let birthTime: String?
    let timeUnknown: Bool?
    let locationName: String?
    let sunSign: String?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case relation
        case isPrimary = "is_primary"
        case isSelected = "is_selected"
        case birthDate = "birth_date"
        case birthTime = "birth_time"
        case timeUnknown = "time_unknown"
        case locationName = "location_name"
        case sunSign = "sun_sign"
    }
}

struct CoreProfileInterpretation: Codable {
    let identity: String?
    let strengths: [String]?
    let watchouts: [String]?
    let lifeAreas: CoreProfileLifeAreas?

    enum CodingKeys: String, CodingKey {
        case identity
        case strengths
        case watchouts
        case lifeAreas = "life_areas"
    }
}

struct CoreProfileLifeAreas: Codable {
    let love: String?
    let career: String?
    let money: String?
    let family: String?
    let sex: String?
    let kids: String?
    let body: String?
    let friends: String?
    let decisions: String?
}

struct CoreProfileDailyInterpretation: Codable {
    let dailyLenses: CoreProfileDailyLenses?

    enum CodingKeys: String, CodingKey {
        case dailyLenses = "daily_lenses"
    }
}

struct CoreProfileDailyLenses: Codable {
    let general: String?
    let love: String?
    let career: String?
    let money: String?
    let family: String?
}

struct CoreProfileLiving: Codable {
    let summary: String?
    let signalProfile: CoreProfileSignalProfile?
    let weeklyState: CoreProfileWeeklyState?
    let recentInsights: [CoreProfileInsight]?
    let learningContext: CoreProfileLearningContext?

    enum CodingKeys: String, CodingKey {
        case summary
        case signalProfile = "signal_profile"
        case weeklyState = "weekly_state"
        case recentInsights = "recent_insights"
        case learningContext = "learning_context"
    }
}

struct CoreProfileSignalProfile: Codable {
    let signalsDays: Int?
    let closureState: String?
    let clarityState: String?
    let dominantFocus: String?

    enum CodingKeys: String, CodingKey {
        case signalsDays = "signals_days"
        case closureState = "closure_state"
        case clarityState = "clarity_state"
        case dominantFocus = "dominant_focus"
    }
}

struct CoreProfileWeeklyState: Codable {
    let integrationText: String?

    enum CodingKeys: String, CodingKey {
        case integrationText = "integration_text"
    }
}

struct CoreProfileInsight: Codable, Identifiable {
    let id: String
    let date: String?
    let type: String?
    let text: String
}

struct CoreProfileLearningContext: Codable {
    let summary: String?
    let responseStyle: String?
    let supportStyle: String?
    let dominantLanes: [String]?
    let dominantDiaryTopics: [String]?

    enum CodingKeys: String, CodingKey {
        case summary
        case responseStyle = "response_style"
        case supportStyle = "support_style"
        case dominantLanes = "dominant_lanes"
        case dominantDiaryTopics = "dominant_diary_topics"
    }
}

struct CoreProfileNatalSummary: Codable {
    let overview: String?
    let chartTone: String?
    let signature: [String]?
    let patterns: [String]?

    enum CodingKeys: String, CodingKey {
        case overview
        case chartTone = "chart_tone"
        case signature
        case patterns
    }
}

struct AccountSettings: Codable {
    let email: String
    let greeting: String?
    let firstName: String?
    let lastName: String?
    let country: String?
    let language: String?
    let locale: String?
    let stayLoggedIn: Bool?
    let newsletterOptIn: Bool?
    let pushOptIn: Bool?
    let subscriptions: [String]
    let astrologyLevel: String?
    let textPreference: String?
    /// DE-8: quick | normal | deep — объём текста за один вызов narrative (серверный дефолт `normal`).
    let todayNarrativeDepthLevel: String?
    let gender: String?

    enum CodingKeys: String, CodingKey {
        case email
        case greeting
        case firstName = "first_name"
        case lastName = "last_name"
        case country
        case language
        case locale
        case stayLoggedIn = "stay_logged_in"
        case newsletterOptIn = "newsletter_opt_in"
        case pushOptIn = "push_opt_in"
        case subscriptions
        case astrologyLevel = "astrology_level"
        case textPreference = "text_preference"
        case todayNarrativeDepthLevel = "today_narrative_depth_level"
        case gender
    }
}

struct AccountSettingsUpdate: Encodable {
    let email: String
    let greeting: String?
    let firstName: String?
    let lastName: String?
    let country: String?
    let language: String?
    let locale: String?
    let stayLoggedIn: Bool
    let newsletterOptIn: Bool
    let pushOptIn: Bool
    let astrologyLevel: String
    let textPreference: String
    let todayNarrativeDepthLevel: String
    let gender: String

    enum CodingKeys: String, CodingKey {
        case email
        case greeting
        case firstName = "first_name"
        case lastName = "last_name"
        case country
        case language
        case locale
        case stayLoggedIn = "stay_logged_in"
        case newsletterOptIn = "newsletter_opt_in"
        case pushOptIn = "push_opt_in"
        case astrologyLevel = "astrology_level"
        case textPreference = "text_preference"
        case todayNarrativeDepthLevel = "today_narrative_depth_level"
        case gender
    }
}

struct NatalChartPreview: Codable {
    let astroProfileID: Int?
    let positions: [String: NatalChartPosition]
    let houses: [NatalHouse]
    let ascendant: NatalAscendant?
    let interpretations: NatalInterpretations?
    let aspects: NatalAspects?
    let cached: Bool?

    enum CodingKeys: String, CodingKey {
        case astroProfileID = "astro_profile_id"
        case positions
        case houses
        case ascendant
        case interpretations
        case aspects
        case cached
    }
}

struct NatalChartPosition: Codable, Hashable {
    let longitude: Double?
    let sign: String?
    let house: Int?
    let degree: Double?
}

struct NatalHouse: Codable, Hashable, Identifiable {
    let house: Int
    let cuspLongitude: Double?
    let sign: String?
    let degree: Double?

    var id: Int { house }

    enum CodingKeys: String, CodingKey {
        case house
        case cuspLongitude = "cusp_longitude"
        case sign
        case degree
    }
}

struct NatalAscendant: Codable, Hashable {
    let longitude: Double?
    let degree: Double?
    /// Совпадает с веб: `ascendant.sign` в ответе `GET /natal-chart/`.
    let sign: String?
}

struct NatalInterpretations: Codable, Hashable {
    let houses: [String: NatalHouseInterpretation]?
}

struct NatalHouseInterpretation: Codable, Hashable {
    let name: String?
    let theme: String?
    let description: String?
}

struct NatalAspects: Codable, Hashable {
    let callouts: [NatalAspectCallout]?
}

struct NatalAspectCallout: Codable, Hashable, Identifiable {
    let aspectID: String?
    let label: String?
    /// API returns a single display string (e.g. "Sun · Moon"), not an array.
    let bodies: String?
    let keywords: [String]?
    let description: String?
    let tensionLevel: String?
    let polarity: String?
    let degreesApart: Double?
    let orbDelta: Double?
    let strength: String?
    let integration: String?

    var id: String {
        aspectID ?? label ?? UUID().uuidString
    }

    enum CodingKeys: String, CodingKey {
        case aspectID = "aspect_id"
        case label
        case bodies
        case keywords
        case description
        case tensionLevel = "tension_level"
        case polarity
        case degreesApart = "degrees_apart"
        case orbDelta = "orb_delta"
        case strength
        case integration
    }
}

struct StoredAstroProfile: Codable, Identifiable, Hashable {
    let id: Int
    let label: String
    let relation: String?
    let birthDate: String
    let birthTime: String?
    let timeUnknown: Bool?
    let locationName: String?
    let latitude: Double?
    let longitude: Double?
    let isPrimary: Bool?
    let birthFactsCorrectionsUsed: Int?
    let birthFactsCorrectionsMax: Int?
    let birthFactsCorrectionsRemaining: Int?
    let birthFactsCooldownRemainingSeconds: Int?

    enum CodingKeys: String, CodingKey {
        case id
        case label
        case relation
        case birthDate = "birth_date"
        case birthTime = "birth_time"
        case timeUnknown = "time_unknown"
        case locationName = "location_name"
        case latitude
        case longitude
        case isPrimary = "is_primary"
        case birthFactsCorrectionsUsed = "birth_facts_corrections_used"
        case birthFactsCorrectionsMax = "birth_facts_corrections_max"
        case birthFactsCorrectionsRemaining = "birth_facts_corrections_remaining"
        case birthFactsCooldownRemainingSeconds = "birth_facts_cooldown_remaining_seconds"
    }

    init(
        id: Int,
        label: String,
        relation: String?,
        birthDate: String,
        birthTime: String?,
        timeUnknown: Bool?,
        locationName: String?,
        latitude: Double?,
        longitude: Double?,
        isPrimary: Bool?,
        birthFactsCorrectionsUsed: Int? = nil,
        birthFactsCorrectionsMax: Int? = nil,
        birthFactsCorrectionsRemaining: Int? = nil,
        birthFactsCooldownRemainingSeconds: Int? = nil
    ) {
        self.id = id
        self.label = label
        self.relation = relation
        self.birthDate = birthDate
        self.birthTime = birthTime
        self.timeUnknown = timeUnknown
        self.locationName = locationName
        self.latitude = latitude
        self.longitude = longitude
        self.isPrimary = isPrimary
        self.birthFactsCorrectionsUsed = birthFactsCorrectionsUsed
        self.birthFactsCorrectionsMax = birthFactsCorrectionsMax
        self.birthFactsCorrectionsRemaining = birthFactsCorrectionsRemaining
        self.birthFactsCooldownRemainingSeconds = birthFactsCooldownRemainingSeconds
    }
}

/// Ответ POST/PUT `account/astro-data`, POST `account/astro-data/:id/primary`: строка профиля и обновлённое ядро персонализации.
struct AstroProfileMutationAPIResponse: Codable {
    let id: Int
    let label: String
    let relation: String?
    let birthDate: String
    let birthTime: String?
    let timeUnknown: Bool
    let timezoneOffsetMinutes: Int?
    let timezoneName: String?
    let locationName: String?
    let latitude: Double?
    let longitude: Double?
    let notes: String?
    let isPrimary: Bool
    let createdAt: String?
    let birthFactsCorrectionsUsed: Int?
    let birthFactsCorrectionsMax: Int?
    let birthFactsCorrectionsRemaining: Int?
    let birthFactsCooldownRemainingSeconds: Int?
    let coreProfile: CoreProfileResponse?

    enum CodingKeys: String, CodingKey {
        case id, label, relation, latitude, longitude, notes
        case birthDate = "birth_date"
        case birthTime = "birth_time"
        case timeUnknown = "time_unknown"
        case timezoneOffsetMinutes = "timezone_offset_minutes"
        case timezoneName = "timezone_name"
        case locationName = "location_name"
        case isPrimary = "is_primary"
        case createdAt = "created_at"
        case birthFactsCorrectionsUsed = "birth_facts_corrections_used"
        case birthFactsCorrectionsMax = "birth_facts_corrections_max"
        case birthFactsCorrectionsRemaining = "birth_facts_corrections_remaining"
        case birthFactsCooldownRemainingSeconds = "birth_facts_cooldown_remaining_seconds"
        case coreProfile = "core_profile"
    }

    var storedSnapshot: StoredAstroProfile {
        StoredAstroProfile(
            id: id,
            label: label,
            relation: relation,
            birthDate: birthDate,
            birthTime: birthTime,
            timeUnknown: timeUnknown,
            locationName: locationName,
            latitude: latitude,
            longitude: longitude,
            isPrimary: isPrimary,
            birthFactsCorrectionsUsed: birthFactsCorrectionsUsed,
            birthFactsCorrectionsMax: birthFactsCorrectionsMax,
            birthFactsCorrectionsRemaining: birthFactsCorrectionsRemaining,
            birthFactsCooldownRemainingSeconds: birthFactsCooldownRemainingSeconds
        )
    }
}

struct AstroProfileInput {
    let label: String
    let relation: String
    let birthDate: String
    let birthTime: String?
    let timeUnknown: Bool
    let locationName: String
    let latitude: Double?
    let longitude: Double?
    let isPrimary: Bool
}

struct AstroProfileUpdatePayload: Encodable {
    let label: String
    let relation: String
    let birth_date: String
    let birth_time: String?
    let time_unknown: Bool
    let location_name: String
    let latitude: Double?
    let longitude: Double?
}

struct AstroProfilesResponse: Codable {
    let profiles: [StoredAstroProfile]
}

struct QuestionAnswerResult: Codable {
    let generationLogID: Int?
    let question: String
    let lane: String
    let laneTitle: String
    let profileReady: Bool
    let answer: QuestionAnswerBlock
    let suggestedRoute: SuggestedRoute

    enum CodingKeys: String, CodingKey {
        case generationLogID = "generation_log_id"
        case question
        case lane
        case laneTitle = "lane_title"
        case profileReady = "profile_ready"
        case answer
        case suggestedRoute = "suggested_route"
    }
}

/// Оценка вопроса для Guidance (`question_assessment`).
struct GuidanceQuestionAssessmentDTO: Codable {
    let flags: GuidanceQuestionAssessmentFlags
    let suggestion: String?
    let weakReadingWarning: String?

    enum CodingKeys: String, CodingKey {
        case flags
        case suggestion
        case weakReadingWarning = "weak_reading_warning"
    }
}

struct GuidanceQuestionAssessmentFlags: Codable {
    let tooGeneral: Bool
    let fortuneTellingTone: Bool
    let lowActionability: Bool
    let possibleRepeat: Bool

    enum CodingKeys: String, CodingKey {
        case tooGeneral = "too_general"
        case fortuneTellingTone = "fortune_telling_tone"
        case lowActionability = "low_actionability"
        case possibleRepeat = "possible_repeat"
    }
}

/// Структурированный контракт разбора (`interpretation`).
struct GuidanceInterpretationContractDTO: Codable {
    let summary: String
    let coreInsight: String
    let profileBridge: String
    let action: String
    let avoid: String
    let continueHint: String
    let whyOutline: String
    let positionWeightsNote: String

    enum CodingKeys: String, CodingKey {
        case summary
        case coreInsight = "core_insight"
        case profileBridge = "profile_bridge"
        case action
        case avoid
        case continueHint = "continue_hint"
        case whyOutline = "why_outline"
        case positionWeightsNote = "position_weights_note"
    }
}

/// Явный мост в дневной Flow / OS (`flow_bridge` в API).
struct GuidanceFlowBridge: Codable {
    let href: String
    let label: String
    let reason: String
    let kind: String
}

/// Ответ `POST /questions/reading` (Guidance с картами).
struct GuidanceReadingResult: Codable {
    let generationLogId: Int?
    let question: String
    let spreadId: String
    let lane: String
    let laneTitle: String
    let profileReady: Bool
    let answer: QuestionAnswerBlock
    let suggestedRoute: SuggestedRoute
    let flowBridge: GuidanceFlowBridge?
    let editorial: GuidanceEditorial?
    let tarotCards: [GuidanceTarotCardPreview]
    let questionAssessment: GuidanceQuestionAssessmentDTO?
    let interpretation: GuidanceInterpretationContractDTO?
    let isClarification: Bool?
    let clarificationParentLogId: Int?
    let clarificationGoal: String?

    enum CodingKeys: String, CodingKey {
        case generationLogId = "generation_log_id"
        case question
        case spreadId = "spread_id"
        case lane
        case laneTitle = "lane_title"
        case profileReady = "profile_ready"
        case answer
        case suggestedRoute = "suggested_route"
        case flowBridge = "flow_bridge"
        case editorial
        case tarotCards = "tarot_cards"
        case questionAssessment = "question_assessment"
        case interpretation
        case isClarification = "is_clarification"
        case clarificationParentLogId = "clarification_parent_log_id"
        case clarificationGoal = "clarification_goal"
    }
}

struct GuidanceEditorial: Codable {
    let currentFocus: String?
    let carriedContext: String?
    let nextStep: String?
}

struct GuidanceTarotCardPreview: Codable {
    let name: String
    let orientation: String
    let position: String
    let positionId: String?
    /// Подсказка к позиции расклада (как в `GET /tarot/spread`).
    let positionPrompt: String?
    let meaning: String
    /// Индекс лица в `images/cards/tarot` (0…77); `nil` в старых ответах API.
    let cardId: Int?
    let keywords: [String]?
}

// MARK: - Questions / Guidance history (`GET /questions/history`)

struct QuestionsHistoryResponseDTO: Codable {
    let history: [QuestionsHistoryItemDTO]
}

struct QuestionsHistoryItemDTO: Codable, Identifiable {
    let generationLogId: Int
    let createdAt: String
    let mode: String
    let lane: String?
    let question: String
    let focus: String?
    let nextStep: String?
    let routeLabel: String?
    let surface: String?
    let spreadId: String?
    let topic: String?
    let leadCardName: String?
    let leadCardOrientation: String?

    var id: Int { generationLogId }
}

/// Сводка для экрана истории Guidance (вопросы + таро).
struct GuidanceHistoryBundle {
    let questions: [QuestionsHistoryItemDTO]
    let tarotDaily: [TarotDailyDrawDTO]
    let spreads: [TarotSpreadRecordDTO]
}

struct QuestionAnswerBlock: Codable {
    let clarity: String
    let explanation: String
    let forecast: String
    let decision: String
    let today: String
}

struct SuggestedRoute: Codable {
    let href: String
    let label: String
    let reason: String
}

struct CompatibilityScenarioContext: Codable, Hashable {
    let formatId: String
    let displayScore: Int
    let subscores: [String: Int]
    let toneMode: String?
    let deepBlockOrder: [String]?
    let attachmentReference: CompatibilityAttachmentReference?

    enum CodingKeys: String, CodingKey {
        case formatId = "format_id"
        case displayScore = "display_score"
        case subscores
        case toneMode = "tone_mode"
        case deepBlockOrder = "deep_block_order"
        case attachmentReference = "attachment_reference"
    }
}

struct CompatibilityComparisonResponse: Codable {
    let profile1: CompatibilityProfileSummary?
    let profile2: CompatibilityProfileSummary?
    let compatibility: CompatibilityResult
    let funnelArtifact: CompatibilityFunnelArtifact?
    let scenarioContext: CompatibilityScenarioContext?

    /// POST `/compatibility/compare` — вложенный `compatibility`. POST `/compatibility/synastry` — плоский `EnrichedCompatibilityResponse` (как на вебе).
    enum CodingKeys: String, CodingKey {
        case profile1 = "profile_1"
        case profile2 = "profile_2"
        case compatibility
        case funnelArtifact = "funnel_artifact"
        case scenarioContext = "scenario_context"
        case overallScore = "overall_score"
        case aspects
        case summary
        case relationshipType = "relationship_type"
        case recommendations
        case deepDive = "deep_dive"
        case editorial
    }

    init(
        profile1: CompatibilityProfileSummary?,
        profile2: CompatibilityProfileSummary?,
        compatibility: CompatibilityResult,
        funnelArtifact: CompatibilityFunnelArtifact?,
        scenarioContext: CompatibilityScenarioContext? = nil
    ) {
        self.profile1 = profile1
        self.profile2 = profile2
        self.compatibility = compatibility
        self.funnelArtifact = funnelArtifact
        self.scenarioContext = scenarioContext
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        profile1 = try c.decodeIfPresent(CompatibilityProfileSummary.self, forKey: .profile1)
        profile2 = try c.decodeIfPresent(CompatibilityProfileSummary.self, forKey: .profile2)
        funnelArtifact = try c.decodeIfPresent(CompatibilityFunnelArtifact.self, forKey: .funnelArtifact)
        scenarioContext = try c.decodeIfPresent(CompatibilityScenarioContext.self, forKey: .scenarioContext)

        if let nested = try c.decodeIfPresent(CompatibilityResult.self, forKey: .compatibility) {
            compatibility = nested
        } else {
            let overall = try c.decode(Int.self, forKey: .overallScore)
            let aspects = try c.decodeIfPresent([CompatibilityAspect].self, forKey: .aspects) ?? []
            let summary = try c.decodeIfPresent(String.self, forKey: .summary)
            let relationshipType = try c.decodeIfPresent(String.self, forKey: .relationshipType)
            let recommendations = try c.decodeIfPresent([String].self, forKey: .recommendations) ?? []
            let deepDive = try c.decodeIfPresent(CompatibilityDeepDive.self, forKey: .deepDive)
            let editorial = try c.decodeIfPresent(CompatibilityEditorialPayload.self, forKey: .editorial)
            compatibility = CompatibilityResult(
                overallScore: overall,
                aspects: aspects,
                summary: summary,
                relationshipType: relationshipType,
                recommendations: recommendations,
                deepDive: deepDive,
                editorial: editorial
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encodeIfPresent(profile1, forKey: .profile1)
        try c.encodeIfPresent(profile2, forKey: .profile2)
        try c.encodeIfPresent(funnelArtifact, forKey: .funnelArtifact)
        try c.encodeIfPresent(scenarioContext, forKey: .scenarioContext)
        try c.encode(compatibility, forKey: .compatibility)
    }
}

struct CompatibilityProfileSummary: Codable {
    let id: Int?
    let label: String?
}

/// Редакторский слой совместимости (`editorial` в ответе compare / synastry).
struct CompatibilityEditorialPayload: Codable, Hashable {
    let modeFocus: String?
    let pairThesis: String
    let strengths: [String]
    let tensions: [String]
    let nextStep: String

    enum CodingKeys: String, CodingKey {
        case modeFocus = "mode_focus"
        case pairThesis = "pair_thesis"
        case strengths
        case tensions
        case nextStep = "next_step"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        modeFocus = try c.decodeIfPresent(String.self, forKey: .modeFocus)
        pairThesis = try c.decodeIfPresent(String.self, forKey: .pairThesis) ?? ""
        strengths = try c.decodeIfPresent([String].self, forKey: .strengths) ?? []
        tensions = try c.decodeIfPresent([String].self, forKey: .tensions) ?? []
        nextStep = try c.decodeIfPresent(String.self, forKey: .nextStep) ?? ""
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encodeIfPresent(modeFocus, forKey: .modeFocus)
        try c.encode(pairThesis, forKey: .pairThesis)
        try c.encode(strengths, forKey: .strengths)
        try c.encode(tensions, forKey: .tensions)
        try c.encode(nextStep, forKey: .nextStep)
    }
}

struct CompatibilityResult: Codable {
    let overallScore: Int
    let aspects: [CompatibilityAspect]
    let summary: String?
    let relationshipType: String?
    let recommendations: [String]
    let deepDive: CompatibilityDeepDive?
    let editorial: CompatibilityEditorialPayload?

    enum CodingKeys: String, CodingKey {
        case overallScore = "overall_score"
        case aspects
        case summary
        case relationshipType = "relationship_type"
        case recommendations
        case deepDive = "deep_dive"
        case editorial
    }
}

struct CompatibilityAspect: Codable, Identifiable {
    let type: String
    let description: String
    let score: Int

    var id: String { "\(type)-\(description)" }
}

struct CompatibilityDeepDive: Codable {
    let relationshipArchetype: String?
    let strongestAxis: String?
    let tensionAxis: String?
    let dimensions: [CompatibilityDimension]
    let strengths: [String]
    let challenges: [String]
    let guidance: [String]
    let knowledge: CompatibilityKnowledge?

    enum CodingKeys: String, CodingKey {
        case relationshipArchetype = "relationship_archetype"
        case strongestAxis = "strongest_axis"
        case tensionAxis = "tension_axis"
        case dimensions
        case strengths
        case challenges
        case guidance
        case knowledge
    }
}

struct CompatibilityDimension: Codable, Identifiable {
    let key: String
    let label: String
    let score: Int
    let summary: String
    let indicators: [String]?

    var id: String { key }
}

struct CompatibilityKnowledge: Codable {
    let relationshipMode: String?
    let modeTitle: String?
    let modeSummary: String?
    let signPairSummary: String?
    let elementalDynamic: String?
    let modalityDynamic: String?
    let rulers: [String]
    let themes: [String]
    let stones: [String]
    let lifePathPair: String?

    enum CodingKeys: String, CodingKey {
        case relationshipMode = "relationship_mode"
        case modeTitle = "mode_title"
        case modeSummary = "mode_summary"
        case signPairSummary = "sign_pair_summary"
        case elementalDynamic = "elemental_dynamic"
        case modalityDynamic = "modality_dynamic"
        case rulers
        case themes
        case stones
        case lifePathPair = "life_path_pair"
    }
}

struct GuideWhyAstroLayer: Identifiable, Hashable {
    let id: String
    let kind: String
    let anchor: String
    let detail: String
}

extension Dictionary where Key == String, Value == JSONValue {
    func narrativeString(_ key: String) -> String? {
        self[key]?.stringValue
    }

    func narrativeStringArray(_ key: String) -> [String] {
        self[key]?.stringArrayValue ?? []
    }

    func narrativeWhyAstroLayers(_ key: String = "why_astrological_layers") -> [GuideWhyAstroLayer] {
        guard case let .array(items) = self[key] ?? .null else { return [] }
        var out: [GuideWhyAstroLayer] = []
        for (idx, item) in items.enumerated() {
            guard case let .object(o) = item else { continue }
            let kind = o["kind"]?.stringValue ?? "layer"
            let anchor = o["anchor"]?.stringValue ?? ""
            let detail = o["detail"]?.stringValue ?? ""
            if anchor.count < 2 || detail.count < 8 { continue }
            let layerId = "\(idx)-\(kind)-\(anchor.prefix(24))"
            out.append(GuideWhyAstroLayer(id: layerId, kind: kind, anchor: anchor, detail: detail))
            if out.count >= 8 { break }
        }
        return out
    }
}

// MARK: - Sign compatibility (GET /compatibility/signs)

struct CompatibilityFunnelDomainScore: Codable, Hashable {
    let domainId: String
    let label: String
    let scorePct: Int
    let confidence: Double
    let applicable: Bool
    let basis: String
    let raises: [String]
    let lowers: [String]
    let improve: [String]
}

struct CompatibilityFunnelTimelinePhase: Codable, Hashable {
    let phaseId: String
    let headline: String
    let body: String
}

struct CompatibilityFunnelDynamicCore: Codable, Hashable {
    let youLine: String
    let partnerLine: String
    let controlPattern: String
    let clarityNote: String
}

struct CompatibilityFunnelRiskBand: Codable, Hashable {
    let level: String
    let headline: String
    let whenOk: String
    let whenShifts: String
    let whenBreaks: String
}

/// Согласование воронки с дневным слоем (Today).
struct CompatibilityFunnelTodayAlignment: Codable, Hashable {
    let source: String
    let focusLabel: String
    let doEcho: String
    let avoidEcho: String
    let syncNote: String
}

/// Первый шаг LLM-цепочки: структурный слой (`llm_base_model` в API).
struct CompatibilityLLMBaseModelFields: Codable, Hashable {
    let pullVsTension: String
    let attractionOrDependency: String
    let conflictCycle: String
    let sexualDynamic: String
    let alignedActionsHint: String
}

/// Воронка точности и доменные скоры (`funnel_artifact` в ответе API).
struct CompatibilityFunnelArtifact: Codable, Hashable {
    let pipelineVersion: String
    let accuracyTier: String
    let accuracyLabel: String
    let relationshipContext: String
    let scoreSemantics: String
    let confidenceNote: String
    let overallScore: Int
    let domainScores: [CompatibilityFunnelDomainScore]
    let childrenRelevant: Bool
    let timeline: [CompatibilityFunnelTimelinePhase]
    let dynamicCore: CompatibilityFunnelDynamicCore
    let riskBands: [CompatibilityFunnelRiskBand]
    let todayAlignment: CompatibilityFunnelTodayAlignment?
    let llmBaseModel: CompatibilityLLMBaseModelFields?
}

struct SignCompatibilityQuickReading: Codable, Hashable {
    let headline: String?
    let strongest: String?
    let friction: String?
    let nextStep: String?
    let strengths: [String]?
    let cautions: [String]?
}

struct SignCompatibilitySubscores: Codable, Hashable {
    let attraction: Int
    let stability: Int
    let conflicts: Int
    let sexuality: Int
}

struct SignCompatibilityAnalysisBlock: Codable, Hashable {
    let key: String
    let title: String
    let subtitle: String
    let takeaway: String
    let detail: String
    let risk: String
    let action: String
    let tips: [String]?

    var resolvedTips: [String] { tips ?? [] }
}

struct SignCompatibilityRoles: Codable, Hashable {
    let youBullets: [String]
    let partnerBullets: [String]
}

struct SignCompatibilityScenarioGroup: Codable, Hashable {
    let id: String
    let title: String
    let bullets: [String]
}

struct SignCompatibilityProductSurface: Codable, Hashable {
    let scoreTagline: String
    let subscores: SignCompatibilitySubscores
    let overviewParagraphs: [String]
    let blocks: [SignCompatibilityAnalysisBlock]
    let roles: SignCompatibilityRoles
    let scenarios: [SignCompatibilityScenarioGroup]
}

struct SignCompatibilityAPIResponse: Codable, Hashable {
    let fromSign: String
    let toSign: String
    let fromSignName: String
    let toSignName: String
    let score: Int
    let summary: String
    let quickReading: SignCompatibilityQuickReading?
    let freeParagraphs: [String]
    let fullParagraphs: [String]
    let isPaid: Bool
    let contentId: String
    let personalized: JSONValue?
    let relationshipContext: String?
    let productSurface: SignCompatibilityProductSurface?
    /// Mirrors backend `content_locale` (en | ru).
    let contentLocale: String?
    let generationSource: String?
    let pairDynamics: JSONValue?
    let funnelArtifact: CompatibilityFunnelArtifact?
    let attachmentReference: CompatibilityAttachmentReference?

    enum CodingKeys: String, CodingKey {
        case fromSign = "from_sign"
        case toSign = "to_sign"
        case fromSignName = "from_sign_name"
        case toSignName = "to_sign_name"
        case score
        case summary
        case quickReading = "quick_reading"
        case freeParagraphs = "free_paragraphs"
        case fullParagraphs = "full_paragraphs"
        case isPaid = "is_paid"
        case contentId = "content_id"
        case personalized
        case relationshipContext = "relationship_context"
        case productSurface = "product_surface"
        case contentLocale = "content_locale"
        case generationSource = "generation_source"
        case pairDynamics = "pair_dynamics"
        case funnelArtifact = "funnel_artifact"
        case attachmentReference = "attachment_reference"
    }
}

// MARK: - Compatibility encyclopedia (GET /compatibility/encyclopedia)

struct CompatibilityEncyclopediaHero: Codable, Hashable {
    let eyebrow: String
    let title: String
    let lead: String
}

struct CompatibilityEncyclopediaAnalyzeParams: Codable, Hashable {
    let topic: String?
    let reading: String?
    let series: String?
}

struct CompatibilityEncyclopediaIntroBlock: Codable, Hashable {
    let kind: String
    let text: String?
    let items: [String]?
}

struct CompatibilityEncyclopediaCategory: Codable, Hashable, Identifiable {
    let id: String
    let emoji: String
    let title: String
    let subtitle: String
    let analyzeParams: CompatibilityEncyclopediaAnalyzeParams
    let introBlocks: [CompatibilityEncyclopediaIntroBlock]?
}

struct CompatibilityEncyclopediaReading: Codable, Hashable, Identifiable {
    let id: String
    let title: String
    let analyzeParams: CompatibilityEncyclopediaAnalyzeParams
    let introBlocks: [CompatibilityEncyclopediaIntroBlock]?
}

struct CompatibilityEncyclopediaSeries: Codable, Hashable, Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let analyzeParams: CompatibilityEncyclopediaAnalyzeParams
    let introBlocks: [CompatibilityEncyclopediaIntroBlock]?
    let scenarioBullets: [String]?
}

/// Selection passed from encyclopedia hub into native analyze flow.
struct CompatibilityEncyclopediaAnalyzeSelection: Hashable {
    let label: String
    let selectionKind: String
    let selectionId: String
    let topicId: String?
    let readingId: String?
    let seriesId: String?
    let introBlocks: [CompatibilityEncyclopediaIntroBlock]
    let scenarioBullets: [String]
}

struct CompatibilityEncyclopediaResponse: Codable, Hashable {
    let contentLocale: String
    let version: String
    let hero: CompatibilityEncyclopediaHero
    let categories: [CompatibilityEncyclopediaCategory]
    let popularReadings: [CompatibilityEncyclopediaReading]
    let series: [CompatibilityEncyclopediaSeries]
}

// MARK: - Zodiac display (EN API → RU, как на вебе)

enum ZodiacSignRU {
    private static let englishByLongitude: [String] = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    /// Показ в UI: кириллицу оставляем, латиницу с API переводим в русское название.
    static func title(_ raw: String?) -> String {
        guard let raw, !raw.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return "—"
        }
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if t.range(of: "[А-Яа-яЁё]", options: .regularExpression) != nil { return t }

        switch t.lowercased() {
        case "aries", "овен": return "Овен"
        case "taurus", "телец": return "Телец"
        case "gemini", "близнецы": return "Близнецы"
        case "cancer", "рак": return "Рак"
        case "leo", "лев": return "Лев"
        case "virgo", "дева": return "Дева"
        case "libra", "весы": return "Весы"
        case "scorpio", "скорпион": return "Скорпион"
        case "sagittarius", "стрелец": return "Стрелец"
        case "capricorn", "козерог": return "Козерог"
        case "aquarius", "водолей": return "Водолей"
        case "pisces", "рыбы": return "Рыбы"
        default: return t
        }
    }

    static func englishSignFromLongitude(_ longitude: Double) -> String {
        let normalized = longitude.truncatingRemainder(dividingBy: 360)
        let positive = normalized >= 0 ? normalized : normalized + 360
        let index = Int(positive / 30) % englishByLongitude.count
        return englishByLongitude[index]
    }

    static func planetLine(_ chart: NatalChartPreview, body: String) -> String? {
        let lower = body.lowercased()
        var position: NatalChartPosition?
        if let p = chart.positions[lower] ?? chart.positions[body] {
            position = p
        } else {
            position = chart.positions.first { $0.key.lowercased() == lower }?.value
        }
        guard let p = position else { return nil }
        if let s = p.sign, !s.isEmpty { return title(s) }
        if let lon = p.longitude ?? p.degree { return title(englishSignFromLongitude(lon)) }
        return nil
    }

    static func ascendantLine(_ chart: NatalChartPreview) -> String? {
        if let s = chart.ascendant?.sign, !s.isEmpty { return title(s) }
        if let lon = chart.ascendant?.longitude ?? chart.ascendant?.degree {
            return title(englishSignFromLongitude(lon))
        }
        if let s = chart.houses.first(where: { $0.house == 1 })?.sign, !s.isEmpty {
            return title(s)
        }
        if let s = chart.houses.first?.sign, !s.isEmpty {
            return title(s)
        }
        return nil
    }
}
