import Foundation

enum GoalScope: String, CaseIterable, Identifiable {
    case week
    case month

    var id: String { rawValue }

    var title: String {
        IOSAppLocale.prefersRussian
            ? (self == .week ? "Неделя" : "Месяц")
            : (self == .week ? "Week" : "Month")
    }
}

/// Паритет с `TrackerEntityKind` на вебе (`EntityCreateWizard`): быстрый вход из блока «Собрать день».
enum TrackerQuickCreateKind: String, Equatable {
    case habit
    case goal
    case ascetic
}

struct TrackerActivitySummary: Identifiable, Hashable {
    let id: String
    let title: String
    let detail: String
    let isComplete: Bool
}

struct TrackerDaySummary: Identifiable, Hashable {
    let id: String
    let dateISO: String
    let dayNumber: String
    let weekdayTitle: String
    let isToday: Bool
    let isInDisplayedMonth: Bool
    let completionCount: Int
    let activities: [TrackerActivitySummary]
    let moodScore: Int?

    var hasActivity: Bool {
        completionCount > 0 || !activities.isEmpty
    }
}

/// Элемент каталога `GET /practices/affirmations`.
struct AffirmationCatalogItem: Identifiable, Hashable {
    let id: String
    let title: String
    let text: String

    var displayLine: String {
        let t = title.trimmingCharacters(in: .whitespacesAndNewlines)
        if !t.isEmpty { return t }
        let b = text.trimmingCharacters(in: .whitespacesAndNewlines)
        return b.isEmpty ? id : b
    }
}

struct AsceticTrackEntry: Hashable {
    let dateISO: String
    let completed: Bool
}

/// Аскеза из ответа `/tracking/calendar` (`ascetic_tracks`).
struct AsceticTrack: Identifiable, Hashable {
    let asceticismId: String
    let title: String?
    let contractStatus: String?
    let entries: [AsceticTrackEntry]

    var id: String { asceticismId }

    var displayTitle: String {
        if let t = title?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty {
            return t
        }
        return asceticismId
    }

    /// Отметки имеют смысл для активных контрактов; без статуса показываем как раньше.
    var allowsLogging: Bool {
        guard let raw = contractStatus?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased(), !raw.isEmpty else {
            return true
        }
        return raw == "active"
    }

    func isDone(on dateISO: String) -> Bool {
        entries.first { $0.dateISO == dateISO }?.completed ?? false
    }
}

struct HabitTrack: Identifiable, Hashable {
    let id: Int
    var name: String
    var isActive: Bool
    var completedDates: Set<String>

    func isDone(on dateISO: String) -> Bool {
        completedDates.contains(dateISO)
    }
}

struct GoalTrack: Identifiable, Hashable {
    let id: Int
    var title: String
    var scope: GoalScope
    var completed: Bool
    var weekStart: String
    var stepDates: Set<String>

    func isStepped(on dateISO: String) -> Bool {
        stepDates.contains(dateISO)
    }

    func allowsStep(on dateISO: String) -> Bool {
        let trimmed = dateISO.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return false }
        switch scope {
        case .week:
            return weekSliceDayISOs().contains(trimmed)
        case .month:
            return true
        }
    }

    /// Progress ring fill: weekly goals use steps in the goal’s week window; monthly uses total steps vs a soft cap.
    var displayProgress: Double {
        switch scope {
        case .week:
            let window = Self.isoDays(from: weekStart, count: 7)
            let done = window.filter { stepDates.contains($0) }.count
            return min(1, Double(done) / 7)
        case .month:
            return min(1, Double(stepDates.count) / 30)
        }
    }

    func weekSliceDayISOs(count: Int = 7) -> [String] {
        Self.isoDays(from: weekStart, count: count)
    }

    private static let isoDayFormatter: DateFormatter = {
        let f = DateFormatter()
        f.calendar = Calendar(identifier: .gregorian)
        f.locale = Locale(identifier: "en_US_POSIX")
        f.timeZone = TimeZone.current
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    private static func isoDays(from weekStartISO: String, count: Int) -> [String] {
        guard let start = isoDayFormatter.date(from: weekStartISO) else { return [] }
        let cal = Calendar.current
        return (0..<count).compactMap { offset in
            cal.date(byAdding: .day, value: offset, to: start).map { isoDayFormatter.string(from: $0) }
        }
    }
}

struct CalendarSnapshot: Hashable {
    var monthTitle: String
    var fromDateISO: String
    var toDateISO: String
    var days: [TrackerDaySummary]
    var streaks: [String: Int]
    var monthSummary: [String: Int]
    var goalTracks: [GoalTrack]
    var habitTracks: [HabitTrack]
    var asceticTracks: [AsceticTrack]

    static let empty = CalendarSnapshot(
        monthTitle: "Month",
        fromDateISO: "2026-03-01",
        toDateISO: "2026-03-31",
        days: [],
        streaks: [:],
        monthSummary: [:],
        goalTracks: [],
        habitTracks: [],
        asceticTracks: []
    )
}

struct ObservationDiaryEntry: Identifiable, Hashable {
    let id: Int
    let dateISO: String
    let noticed: String
    let hardest: String
    let easierThanExpected: String
    let createdAt: String?
    let updatedAt: String?

    var hasContent: Bool {
        !noticed.isEmpty || !hardest.isEmpty || !easierThanExpected.isEmpty
    }
}

enum InsightConfidence: String, Hashable {
    case low
    case medium
    case high

    var title: String {
        switch self {
        case .low: return "Низкая уверенность"
        case .medium: return "Средняя уверенность"
        case .high: return "Высокая уверенность"
        }
    }
}

struct AutoInsightItem: Identifiable, Hashable {
    let id: String
    let dateISO: String
    let type: String
    let text: String
    let confidence: InsightConfidence
    let dataPoints: [String: String]
    let createdAt: String?

    var typeTitle: String {
        switch type {
        case "streak": return "Стрик"
        case "pattern": return "Паттерн"
        case "shift": return "Сдвиг"
        case "correlation": return "Корреляция"
        case "weekend_pattern": return "Ритм выходных"
        case "signal_closure": return "Собранность дня"
        case "signal_clarity": return "Ясность решения"
        case "signal_focus": return "Повторяющийся фокус"
        default: return type.replacingOccurrences(of: "_", with: " ").capitalized
        }
    }
}
