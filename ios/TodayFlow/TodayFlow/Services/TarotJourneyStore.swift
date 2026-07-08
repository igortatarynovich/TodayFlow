import Foundation

/// Local journey log — паритет `frontend/src/lib/tarotJourneyStore.ts`.
struct TarotJourneyEntry: Codable, Equatable, Identifiable {
    let id: String
    let completedAt: String
    let question: String
    let concernDomain: String?
    let spreadId: String
    let spreadTitle: String
    let cardIds: [Int]
    let cardNames: [String]
    let resonance: String?
}

enum TarotJourneyStore {
    static let minSessionsToShow = 5
    private static let storageKey = "todayflow:tarot-journey:v1"
    private static let maxEntries = 80

    static func readEntries() -> [TarotJourneyEntry] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([TarotJourneyEntry].self, from: data)
        else { return [] }
        return decoded
    }

    static func writeEntries(_ entries: [TarotJourneyEntry]) {
        let trimmed = Array(entries.prefix(maxEntries))
        guard let data = try? JSONEncoder().encode(trimmed) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }

    @discardableResult
    static func append(
        question: String,
        concernDomain: String?,
        spreadId: String,
        spreadTitle: String,
        cardIds: [Int],
        cardNames: [String],
        resonance: String? = nil
    ) -> TarotJourneyEntry {
        let entry = TarotJourneyEntry(
            id: UUID().uuidString.lowercased(),
            completedAt: ISO8601DateFormatter().string(from: Date()),
            question: question,
            concernDomain: concernDomain,
            spreadId: spreadId,
            spreadTitle: spreadTitle,
            cardIds: cardIds,
            cardNames: cardNames,
            resonance: resonance
        )
        writeEntries([entry] + readEntries())
        return entry
    }

    static func updateResonance(entryId: String, resonance: String) {
        let next = readEntries().map { entry in
            guard entry.id == entryId else { return entry }
            return TarotJourneyEntry(
                id: entry.id,
                completedAt: entry.completedAt,
                question: entry.question,
                concernDomain: entry.concernDomain,
                spreadId: entry.spreadId,
                spreadTitle: entry.spreadTitle,
                cardIds: entry.cardIds,
                cardNames: entry.cardNames,
                resonance: resonance
            )
        }
        writeEntries(next)
    }

    static func sessionCount() -> Int { readEntries().count }

    static func shouldShowPanel() -> Bool { sessionCount() >= minSessionsToShow }
}

struct TarotJourneyThemeChip: Equatable {
    let emoji: String
    let label: String
    let count: Int
}

struct TarotJourneySummary: Equatable {
    static func == (lhs: TarotJourneySummary, rhs: TarotJourneySummary) -> Bool {
        lhs.totalSessions == rhs.totalSessions &&
        lhs.periodLabel == rhs.periodLabel &&
        lhs.themes == rhs.themes &&
        lhs.frequentCards.count == rhs.frequentCards.count &&
        zip(lhs.frequentCards, rhs.frequentCards).allSatisfy { lhsCard, rhsCard in
            lhsCard.name == rhsCard.name && lhsCard.count == rhsCard.count
        } &&
        lhs.recentQuestions == rhs.recentQuestions
    }

    let totalSessions: Int
    let periodLabel: String
    let themes: [TarotJourneyThemeChip]
    let frequentCards: [(name: String, count: Int)]
    let recentQuestions: [String]
}

enum TarotJourneySummaryBuilder {
    private static let domainThemes: [String: (String, String)] = [
        "relationships": ("❤️", "отношения"),
        "work": ("💼", "работа"),
        "money": ("💰", "деньги"),
        "family": ("🏡", "семья"),
        "growth": ("🌱", "саморазвитие"),
        "decision": ("🧭", "выбор"),
        "conflict": ("⚡", "освобождение"),
        "inner_state": ("🕊", "терпение"),
        "other": ("✨", "личный поиск"),
    ]

    static func build(entries: [TarotJourneyEntry], windowDays: Int = 30) -> TarotJourneySummary {
        let cutoff = Date().addingTimeInterval(-Double(windowDays) * 24 * 3600)
        let iso = ISO8601DateFormatter()
        let recent = entries.filter { entry in
            guard let date = iso.date(from: entry.completedAt) else { return false }
            return date >= cutoff
        }
        let pool = recent.isEmpty ? Array(entries.prefix(12)) : recent

        var themeCounts: [String: TarotJourneyThemeChip] = [:]
        func bumpTheme(_ emoji: String, _ label: String) {
            let key = label.lowercased()
            let prev = themeCounts[key]
            themeCounts[key] = TarotJourneyThemeChip(
                emoji: emoji,
                label: label,
                count: (prev?.count ?? 0) + 1
            )
        }

        for entry in pool {
            let domain = (entry.concernDomain ?? "").lowercased()
            if let theme = domainThemes[domain] {
                bumpTheme(theme.0, theme.1)
            }
            if entry.question.localizedCaseInsensitiveContains("выбор") || entry.question.localizedCaseInsensitiveContains("решен") {
                bumpTheme("🧭", "выбор")
            }
            if entry.question.localizedCaseInsensitiveContains("отношен") || entry.question.localizedCaseInsensitiveContains("партн") {
                bumpTheme("❤️", "отношения")
            }
        }

        var cardCounts: [Int: (name: String, count: Int)] = [:]
        for entry in pool {
            for (idx, id) in entry.cardIds.enumerated() {
                let name = entry.cardNames.indices.contains(idx) ? entry.cardNames[idx] : "Card \(id)"
                let ru = TodayTarotTodayRuCatalog.card(id)?.nameRu
                let display = ru ?? name
                let prev = cardCounts[id]
                cardCounts[id] = (display, (prev?.count ?? 0) + 1)
            }
        }

        let themes = themeCounts.values.sorted { $0.count > $1.count }.prefix(4).map { $0 }
        let frequentCards = cardCounts.values.sorted { $0.count > $1.count }.prefix(5).map { ($0.name, $0.count) }
        let recentQuestions = pool.map(\.question).filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }.prefix(5).map { $0 }

        let periodLabel = recent.isEmpty ? "за всё время" : "за последние \(windowDays) дней"
        return TarotJourneySummary(
            totalSessions: entries.count,
            periodLabel: periodLabel,
            themes: Array(themes),
            frequentCards: Array(frequentCards),
            recentQuestions: Array(recentQuestions)
        )
    }
}
