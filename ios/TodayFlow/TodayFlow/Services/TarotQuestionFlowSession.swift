import Foundation

struct TarotQuestionSession: Codable, Equatable {
    var sessionId: String
    var step: TarotFlowStep
    var concernDomain: TarotConcernDomain?
    var refinementId: String?
    var customQuestion: String
    var spreadId: String?
    var startedAt: String
}

enum TarotQuestionFlowSessionStore {
    private static let storageKey = "todayflow:tarot-question-flow:v1"

    static func read() -> TarotQuestionSession? {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else { return nil }
        return try? JSONDecoder().decode(TarotQuestionSession.self, from: data)
    }

    static func write(_ session: TarotQuestionSession) {
        guard let data = try? JSONEncoder().encode(session) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }

    static func create() -> TarotQuestionSession {
        TarotQuestionSession(
            sessionId: UUID().uuidString.lowercased(),
            step: .hero,
            concernDomain: nil,
            refinementId: nil,
            customQuestion: "",
            spreadId: nil,
            startedAt: ISO8601DateFormatter().string(from: Date())
        )
    }

    static func patch(_ patch: (inout TarotQuestionSession) -> Void) -> TarotQuestionSession {
        var session = read() ?? create()
        patch(&session)
        write(session)
        return session
    }
}
