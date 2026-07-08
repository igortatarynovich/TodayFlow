import Foundation

// MARK: - Категории (`GET /practices/categories/list`)

struct PracticeCategoryDTO: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let icon: String
}

struct PracticeCategoriesListDTO: Codable {
    let categories: [PracticeCategoryDTO]
}

// MARK: - Interpretation bundle (`GET /practices/interpretation-bundle`)

struct InterpretationBundleDTO: Codable {
    let bundleId: String?
    let patternAxis: String?
    let day: Int?
    let pattern: InterpretationBundlePatternDTO?
    let practice: InterpretationBundlePracticeSnippetDTO?
    let interpretation: InterpretationBundleInterpretationTextDTO?
    let cta: InterpretationBundleCTADTO?
}

struct InterpretationBundlePatternDTO: Codable {
    let axisId: String?
    let name: String?
    let value: Double?
    let isPositive: Bool?
}

struct InterpretationBundlePracticeSnippetDTO: Codable {
    let id: String?
    let title: String?
    let description: String?
    let category: String?
    let durationMinutes: Int?
    let difficulty: String?
    let isFree: Bool?
    let accessLevel: String?
    let tags: [String]?
    let personalizedReason: String?
}

struct InterpretationBundleInterpretationTextDTO: Codable {
    let facet: String?
    let text: String?
    let maxSentences: Int?
}

struct InterpretationBundleCTADTO: Codable {
    let afterCompletion: String?
    let target: String?
}

// MARK: - Список и карточка (`GET /practices/`, `GET /practices/current`)

struct PracticeSummaryDTO: Codable, Identifiable {
    let id: String
    let title: String
    let description: String
    let category: String
    let practiceType: String?
    let cycleType: String?
    let durationMinutes: Int?
    let difficulty: String
    let isFree: Bool
    let isPersonalized: Bool
    let personalizedReason: String?
    let accessLevel: String
    let tags: [String]
    let targetAxis: String?
    let format: String?
    /// Для `GET /practices/sequences` и серий в каталоге.
    let sequenceId: String?
    let stepNumber: Int?
    let totalSteps: Int?
}

// MARK: - Деталь (`GET /practices/{id}`)

struct PracticeStepDTO: Codable, Identifiable {
    var id: Int { stepNumber }
    let stepNumber: Int
    let title: String
    let description: String
    let durationMinutes: Int?
    let instructions: [String]?
    let questions: [String]?
}

struct PracticeDetailDTO: Codable {
    let id: String
    let title: String
    let description: String
    let category: String
    let practiceType: String?
    let cycleType: String?
    let durationMinutes: Int?
    let difficulty: String
    let isFree: Bool
    let isPersonalized: Bool
    let personalizedReason: String?
    let accessLevel: String
    let tags: [String]
    let targetAxis: String?
    let format: String?
    let instructions: [String]?
    let prompt: String?
    let questions: [String]?
    let steps: [PracticeStepDTO]?
    let sequenceId: String?
    let stepNumber: Int?
    let totalSteps: Int?
    let audioUrl: String?
    let relatedPractices: [String]?
}

// MARK: - Завершение (`POST /practices/{id}/complete`)

struct PracticeUsageDTO: Codable {
    let practiceId: String
    let completedAt: Date
}

// MARK: - История (`GET /practices/history`)

struct PracticeHistoryItemDTO: Codable, Identifiable {
    let id: Int
    let practiceId: String
    let practiceTitle: String?
    let category: String?
    let completedAt: Date
    let isPersonalized: Bool
    let sequenceId: String?
    let stepNumber: Int?
}

struct PracticeHistoryResponseDTO: Codable {
    let history: [PracticeHistoryItemDTO]
    let total: Int
}

// MARK: - Прогресс (`GET /practices/progress`)

struct CategoryProgressDTO: Codable, Identifiable {
    var id: String { category }
    let category: String
    let totalCompleted: Int
    let personalizedCompleted: Int
}

struct PracticeProgressResponseDTO: Codable {
    let totalCompleted: Int
    let personalizedCompleted: Int
    let generalCompleted: Int
    let byCategory: [CategoryProgressDTO]
    let currentStreakDays: Int
    let longestStreakDays: Int
    let weeksActive: Int
}

// MARK: - Лимиты (`GET /practices/limits`)

struct PracticeLimitsDTO: Codable {
    let subscriptionLevel: String
    let personalizedLimit: Int
    let usedThisWeek: Int
    let remainingThisWeek: Int
    /// Дата начала недели `YYYY-MM-DD`.
    let weekStart: String
}

// MARK: - Прогресс серии (`GET /practices/sequences/{id}/progress`)

struct SequenceProgressDTO: Codable {
    let sequenceId: String
    let sequenceTitle: String
    let totalSteps: Int
    let completedSteps: Int
    let currentStep: Int?
    let startedAt: Date?
    let lastCompletedAt: Date?
    let isCompleted: Bool
}

// MARK: - День пользователя (как `frontend/src/hooks/useUserDay.ts`)

/// Элемент `GET /practices/asceticisms`
struct PracticeAsceticismDTO: Codable {
    let id: String?
    let title: String?
    let description: String?
}

/// Элемент `GET /practices/affirmations`
struct PracticeAffirmationListItemDTO: Codable {
    let id: String?
    let title: String?
    let text: String?
    let goal: String?
    let direction: String?
    let tags: [String]?
}

enum PracticeUserDay {
    /// Ключ и логика совпадают с вебом: `todayflow_first_visit_${userId}`, день 1 — первый визит, далее по календарю, максимум 7.
    static func dayNumber(userId: Int) -> Int {
        let key = "todayflow_first_visit_\(userId)"
        let calendar = Calendar.current
        let todayStart = calendar.startOfDay(for: Date())

        if let raw = UserDefaults.standard.string(forKey: key), !raw.isEmpty {
            guard let firstDate = parseFirstVisitDate(raw) else { return 1 }
            let firstStart = calendar.startOfDay(for: firstDate)
            let diff = calendar.dateComponents([.day], from: firstStart, to: todayStart).day ?? 0
            let day = diff + 1
            return min(max(day, 1), 7)
        }

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        UserDefaults.standard.set(formatter.string(from: Date()), forKey: key)
        return 1
    }

    private static func parseFirstVisitDate(_ raw: String) -> Date? {
        let f1 = ISO8601DateFormatter()
        f1.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let d = f1.date(from: raw) { return d }
        let f2 = ISO8601DateFormatter()
        f2.formatOptions = [.withInternetDateTime]
        return f2.date(from: raw)
    }
}
