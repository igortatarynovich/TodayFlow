import Foundation

/// Паритет `frontend/src/components/today/practicesCatalogContent.ts` — цели, направления, ключевые слова.
enum PracticeCatalogGoalId: String, CaseIterable, Identifiable {
    case calm
    case energy
    case focus
    case connection
    case growth
    case relationships

    var id: String { rawValue }
}

enum PracticeCatalogDirectionKey: String, CaseIterable, Hashable {
    case meditation = "Медитация"
    case breath = "Дыхательные практики"
    case somatic = "Телесные практики"
    case movement = "Движение"
    case activation = "Активация"
    case attention = "Внимание"
    case mindfulness = "Осознанность"
    case reflection = "Рефлексия"
    case journal = "Дневник"
    case changeWork = "Практики изменений"
    case cycles = "Циклы"
    case lovingKindness = "Медитация любящей доброты"
    case openness = "Открытость"
}

struct PracticeCatalogGoalOption: Identifiable {
    let id: PracticeCatalogGoalId
    let icon: String
    let title: String
    let description: String
    let directions: [PracticeCatalogDirectionKey]
}

enum PracticeCatalogContent {
    static let directionKeywords: [PracticeCatalogDirectionKey: [String]] = [
        .meditation: ["медитация", "медитировать", "осознанность", "mindfulness"],
        .breath: ["дыхание", "пранаяма", "breathing", "вдох", "выдох"],
        .somatic: ["тело", "движение", "ходьба", "йога", "растяжка"],
        .movement: ["движение", "активность", "энергия", "активация"],
        .activation: ["энергия", "активация", "бодрость", "пробуждение"],
        .attention: ["внимание", "концентрация", "фокус", "осознанность"],
        .mindfulness: ["осознанность", "mindfulness", "настоящий момент", "присутствие"],
        .reflection: ["рефлексия", "размышление", "дневник", "вопросы", "понимание"],
        .journal: ["дневник", "запись", "journaling", "размышление"],
        .changeWork: ["изменение", "рост", "развитие", "паттерн"],
        .cycles: ["цикл", "луна", "неделя", "месяц", "переход"],
        .lovingKindness: ["любовь", "доброта", "сострадание", "метта", "loving-kindness"],
        .openness: ["открытость", "принятие", "отношения", "связь"],
    ]

    static func goals(ru: Bool) -> [PracticeCatalogGoalOption] {
        [
            PracticeCatalogGoalOption(
                id: .calm,
                icon: "🧘",
                title: ru ? "Спокойствие и баланс" : "Calm and balance",
                description: ru
                    ? "Снизить тревожность, найти внутренний покой, восстановить баланс"
                    : "Ease anxiety, find inner calm, restore balance",
                directions: [.meditation, .breath, .somatic]
            ),
            PracticeCatalogGoalOption(
                id: .energy,
                icon: "⚡",
                title: ru ? "Энергия и активность" : "Energy and activity",
                description: ru
                    ? "Поднять энергию, мотивацию и активность"
                    : "Raise energy, motivation, and activity",
                directions: [.breath, .movement, .activation]
            ),
            PracticeCatalogGoalOption(
                id: .focus,
                icon: "🎯",
                title: ru ? "Фокус и концентрация" : "Focus and concentration",
                description: ru
                    ? "Улучшить концентрацию, снизить отвлечения, повысить продуктивность"
                    : "Improve concentration, cut distraction, get more done",
                directions: [.meditation, .attention, .mindfulness]
            ),
            PracticeCatalogGoalOption(
                id: .connection,
                icon: "💫",
                title: ru ? "Связь с собой" : "Connection with yourself",
                description: ru
                    ? "Понять себя, свои потребности и эмоции"
                    : "Understand yourself, your needs, and your emotions",
                directions: [.reflection, .journal, .mindfulness]
            ),
            PracticeCatalogGoalOption(
                id: .growth,
                icon: "🌱",
                title: ru ? "Рост и развитие" : "Growth and development",
                description: ru
                    ? "Развивать навыки, менять паттерны, расти"
                    : "Build skills, shift patterns, grow",
                directions: [.reflection, .changeWork, .cycles]
            ),
            PracticeCatalogGoalOption(
                id: .relationships,
                icon: "💝",
                title: ru ? "Отношения" : "Relationships",
                description: ru
                    ? "Улучшить близость с близкими, открыться любви"
                    : "Improve closeness with loved ones, open to love",
                directions: [.lovingKindness, .reflection, .openness]
            ),
        ]
    }

    static func directionLabel(_ key: PracticeCatalogDirectionKey, ru: Bool) -> String {
        guard !ru else { return key.rawValue }
        switch key {
        case .meditation: return "Meditation"
        case .breath: return "Breathwork"
        case .somatic: return "Somatic practice"
        case .movement: return "Movement"
        case .activation: return "Activation"
        case .attention: return "Attention"
        case .mindfulness: return "Mindfulness"
        case .reflection: return "Reflection"
        case .journal: return "Journaling"
        case .changeWork: return "Change work"
        case .cycles: return "Cycles"
        case .lovingKindness: return "Loving-kindness"
        case .openness: return "Openness"
        }
    }

    static func matchesDirection(_ practice: PracticeSummaryDTO, direction: PracticeCatalogDirectionKey) -> Bool {
        let keywords = directionKeywords[direction] ?? []
        let haystack = [
            practice.title,
            practice.description ?? "",
            practice.category,
            practice.tags.joined(separator: " "),
        ]
            .joined(separator: " ")
            .lowercased()
        return keywords.contains { haystack.contains($0) }
    }

    enum CatalogTabId: String, CaseIterable, Identifiable {
        case all
        case breath
        case meditation
        case affirmation
        case ascetic

        var id: String { rawValue }

        func label(ru: Bool) -> String {
            switch self {
            case .all: return ru ? "Все" : "All"
            case .breath: return ru ? "Дыхание" : "Breath"
            case .meditation: return ru ? "Медитации" : "Meditations"
            case .affirmation: return ru ? "Аффirmации" : "Affirmations"
            case .ascetic: return ru ? "Аскезы" : "Ascetics"
            }
        }
    }

    static func matchesCatalogTab(_ practice: PracticeSummaryDTO, tab: CatalogTabId) -> Bool {
        if tab == .all { return true }
        let haystack = "\(practice.category) \(practice.tags.joined(separator: " "))".lowercased()
        switch tab {
        case .breath: return haystack.contains("дых") || haystack.contains("breath")
        case .meditation: return haystack.contains("медит")
        case .affirmation: return haystack.contains("афф") || haystack.contains("affirm")
        case .ascetic: return haystack.contains("аск") || haystack.contains("ascet")
        case .all: return true
        }
    }

    static func categoryLabel(for practice: PracticeSummaryDTO, ru: Bool) -> String {
        let category = practice.category.lowercased()
        if category.contains("дых") || category.contains("breath") { return ru ? "Дыхание" : "Breath" }
        if category.contains("медит") { return ru ? "Медитация" : "Meditation" }
        if category.contains("афф") || category.contains("affirm") { return ru ? "Аффirmация" : "Affirmation" }
        if category.contains("аск") || category.contains("ascet") { return ru ? "Аскеза" : "Ascetic" }
        if category.contains("пис") || category.contains("journal") { return ru ? "Письмо" : "Writing" }
        return practice.category
    }
}
