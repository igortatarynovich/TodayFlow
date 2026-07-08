import Foundation

// MARK: - API DTOs (aligned with backend `todayflow_backend.core.models`)

struct TarotCardDTO: Codable, Hashable, Identifiable {
    let id: Int
    let name: String
    let keywords: [String]?
    let upright: String?
    let reversed: String?

    var keywordList: [String] { keywords ?? [] }

    func meaning(for orientation: String) -> String {
        orientation == "reversed" ? (reversed ?? "") : (upright ?? "")
    }
}

struct TarotMantraDTO: Codable, Hashable {
    let title: String?
    let mantra: String?
    let intention: String?
    let guidance: String?
    let humanText: String?
}

struct TarotDailyDrawDTO: Codable, Hashable {
    let date: String
    let card: TarotCardDTO
    let orientation: String
    let mantra: TarotMantraDTO?
}

/// Ответ `GET /tarot/history`.
struct TarotHistoryResponseDTO: Codable, Hashable {
    let today: TarotDailyDrawDTO
    let history: [TarotDailyDrawDTO]
    let streakDays: Int
}

struct TarotSpreadPositionDTO: Codable, Hashable {
    let id: String
    let title: String
    let prompt: String?
}

struct TarotSpreadCardDTO: Codable, Hashable {
    let position: TarotSpreadPositionDTO
    let card: TarotCardDTO
    let orientation: String
    let meaning: String
}

struct TarotSpreadResultDTO: Codable, Hashable {
    let spreadId: String
    let title: String?
    let description: String?
    let cards: [TarotSpreadCardDTO]
}

struct TarotFollowUpChipDTO: Codable, Hashable, Identifiable {
    let id: String
    let label: String
}

struct TarotCardInsightDTO: Codable, Hashable, Identifiable {
    let positionLabel: String
    let cardNameRu: String
    let cardId: Int
    let orientation: String
    let line: String

    var id: String { "\(cardId)-\(positionLabel)-\(orientation)" }
}

struct TarotSpreadReadingDTO: Codable, Hashable {
    let meaning: String?
    let manifestation: String?
    let caution: String?
    let nextStep: String?
    let synthesisWhy: String?
    let actionsToday: [String]?
    let selfQuestion: String?
    let profileLens: String?
    let profileLensApplied: Bool?
    let insightHolding: String?
    let insightShifting: String?
    let insightAttention: String?
    let todaySuggestion: String?
    let followUpPrompt: String?
    let followUpChips: [TarotFollowUpChipDTO]?
    let cardInsights: [TarotCardInsightDTO]?
}

struct TarotSpreadContextDTO: Codable, Hashable {
    let spread: TarotSpreadResultDTO
    let reading: TarotSpreadReadingDTO?
    let generationLogId: Int?
}

// MARK: - Requests

struct TarotSpreadContextRequest: Encodable {
    let spreadId: String
    let question: String?
    let concernDomain: String?
    let selectedCards: [TarotSelectedCardRequest]
}

struct TarotSelectedCardRequest: Encodable {
    let cardId: Int
    let orientation: String
}

struct TarotDeckDrawRequest: Encodable {
    let count: Int
}

/// Тело `POST /tarot/spread` — раздача расклада до интерпретации.
struct TarotSpreadDrawRequest: Encodable {
    let spread_id: String
}

/// Параметры question-first ритуала (web `/tarot/spread/[spreadId]`).
struct TarotSpreadRitualConfig: Hashable, Codable {
    let spreadId: String
    let title: String
    let question: String
    let concernDomain: String?
    let refinementId: String?
    let cardCount: Int
    let positionLabels: [String]
    let anchorCardId: Int?
    let anchorOrientation: String?

    var requiredFromDeck: Int {
        anchorCardId != nil ? max(0, cardCount - 1) : cardCount
    }

    var deckCount: Int {
        max(requiredFromDeck + 5, 8)
    }

    var deckSelectionLabels: [String] {
        anchorCardId != nil ? Array(positionLabels.dropFirst()) : positionLabels
    }
}

// MARK: - Favorites & spread history

struct TarotFavoritesResponse: Decodable, Hashable {
    let favorites: [Int]
}

struct TarotFavoriteToggleRequest: Encodable {
    let cardId: Int
    /// Backend toggles by `card_id`; поле требуется контрактом Pydantic.
    let favorite: Bool
}

struct TarotSpreadRecordDTO: Codable, Hashable, Identifiable {
    let drawDate: String
    let createdAt: String?
    let spread: TarotSpreadResultDTO

    /// Стабильный ключ для списков (API не отдаёт отдельный id записи).
    var id: String {
        let cardsKey = spread.cards.map { "\($0.card.id):\($0.orientation)" }.joined(separator: ",")
        return "\(drawDate)|\(createdAt ?? "")|\(spread.spreadId)|\(cardsKey)"
    }
}

struct TarotSpreadHistoryDTO: Decodable, Hashable {
    let history: [TarotSpreadRecordDTO]
}
