import Foundation

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
        let t = (theme ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !t.isEmpty { return t }
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

/// Loose JSON for progress bag.
enum JSONValue: Codable, Equatable {
    case string(String)
    case number(Double)
    case bool(Bool)
    case object([String: JSONValue])
    case array([JSONValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Double.self) {
            self = .number(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([String: JSONValue].self) {
            self = .object(value)
        } else if let value = try? container.decode([JSONValue].self) {
            self = .array(value)
        } else {
            self = .null
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let value): try container.encode(value)
        case .number(let value): try container.encode(value)
        case .bool(let value): try container.encode(value)
        case .object(let value): try container.encode(value)
        case .array(let value): try container.encode(value)
        case .null: try container.encodeNil()
        }
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
