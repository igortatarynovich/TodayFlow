import Foundation

struct RingMetric: Identifiable, Hashable {
    let id: String
    let title: String
    let value: Int
    let subtitle: String

    var progress: Double {
        min(max(Double(value) / 100.0, 0.0), 1.0)
    }
}

enum LifeLevelTier: String, CaseIterable, Hashable {
    case bronze
    case silver
    case gold
    case platinum

    var title: String {
        switch self {
        case .bronze: return "Бронза"
        case .silver: return "Серебро"
        case .gold: return "Золото"
        case .platinum: return "Платина"
        }
    }

    var meaning: String {
        switch self {
        case .bronze:
            return "Ты всё ещё настраиваешь базовую управляемость дня."
        case .silver:
            return "Базовый ритм есть, но он пока не устойчив."
        case .gold:
            return "Ты держишься за решения и не распадаешься по мелочам."
        case .platinum:
            return "Твой дневной ритм выстроен как система."
        }
    }

    var shortMeaning: String {
        switch self {
        case .bronze: return "Базовая опора дня ещё формируется"
        case .silver: return "Стабильность постепенно обретает форму"
        case .gold: return "Контроль и ясность держатся"
        case .platinum: return "Ритм глубоко систематизирован"
        }
    }

    var next: LifeLevelTier? {
        switch self {
        case .bronze: return .silver
        case .silver: return .gold
        case .gold: return .platinum
        case .platinum: return nil
        }
    }
}

struct LifeLevelContour: Hashable {
    let tier: LifeLevelTier
    let score: Int
    let execution: Int
    let alignment: Int
    let consistency: Int
    let trackedDays: Int
    let progressToNext: Double
    let statusLine: String
    let guidanceLine: String
    let alertLine: String?
}

struct TodayScenario: Identifiable, Hashable {
    let id: String
    let title: String
    /// Короткая строка дня (если есть в API отдельно от summary).
    let focus: String?
    let summary: String
    let accentHex: String
    let deepLinkPath: String
}

struct TodayDashboard: Hashable {
    var dateISO: String
    var dateTitle: String
    /// Баллы из того же ответа, что `GET /today/state-map` / fusion — для ритуала, пока `store.fusionIndex` не обновлён отдельным запросом.
    var fusionScores: FusionScores?
    var headline: String
    var profilePrism: String
    var tarotTitle: String
    var numerologyTitle: String
    var energyTitle: String
    var guidanceSummary: String
    var actionItems: [String]
    var focusItems: [String]
    var riskNote: String
    var morningIntention: String
    var checkinTitle: String
    var checkinSubtitle: String
    var checkinHint: String
    var ritualFeedback: String?
    var quickDecisionAnswer: String?
    var questionOfDayAnswer: String
    var completedExecutionActions: [String]
    var respectedAvoidActions: [String]
    var metrics: [RingMetric]
    var contour: LifeLevelContour
    var scenarios: [TodayScenario]
    var streakCount: Int
    var completionProgress: Double
}

extension TodayDashboard {
    static let placeholder = TodayDashboard(
        dateISO: "2026-03-30",
        dateTitle: "Сегодня",
        fusionScores: FusionScores(energy: 58, emotionalBalance: 62, focus: 55),
        headline: "День раскрывается лучше, когда выбираешь одну линию и не распыляешь импульс.",
        profilePrism: "Спокойнее темп — решения становятся чётче.",
        tarotTitle: "Карта дня",
        numerologyTitle: "Число дня",
        energyTitle: "Тихая тяга",
        guidanceSummary: "Открой день одним действием, которое убирает шум.",
        actionItems: [
            "Зафиксируй одно ясное намерение.",
            "Защити один непрерывный блок.",
            "Закрой день одной фразой."
        ],
        focusItems: ["приоритет", "ясность", "темп"],
        riskNote: "Слишком много параллельных нитей сгладит день.",
        morningIntention: "",
        checkinTitle: "Одна строка на сегодня",
        checkinSubtitle: "Задай тон, пока шум не перехватил день.",
        checkinHint: "Что сегодня важнее всего?",
        ritualFeedback: nil,
        quickDecisionAnswer: nil,
        questionOfDayAnswer: "",
        completedExecutionActions: [],
        respectedAvoidActions: [],
        metrics: [
            RingMetric(id: "execution", title: "Закрытие дня", value: 62, subtitle: "Закрывай день маленькими конкретными шагами"),
            RingMetric(id: "awareness", title: "Ясность", value: 68, subtitle: "Замечай, что реально ведёт день"),
            RingMetric(id: "alignment", title: "Согласованность", value: 57, subtitle: "Держи решения ровными и чистыми")
        ],
        contour: LifeLevelContour(
            tier: .silver,
            score: 61,
            execution: 62,
            alignment: 59,
            consistency: 63,
            trackedDays: 5,
            progressToNext: 0.8,
            statusLine: "Базовый ритм есть, но ему ещё нужна устойчивость.",
            guidanceLine: "Чтобы выйти на «Золото»: сохраняй ритм ещё 3 дня и избегай импульсивных решений.",
            alertLine: "Почти уровень «Золото»"
        ),
        scenarios: [
            TodayScenario(
                id: "career",
                title: "Карьера",
                focus: "Один шаг по делу",
                summary: "Используй день для одного конкретного движения, а не широкой перестройки.",
                accentHex: "#E37A3F",
                deepLinkPath: "/questions/money-career"
            ),
            TodayScenario(
                id: "love",
                title: "Отношения",
                focus: "Честный контакт",
                summary: "Короткая ясность заходит лучше, чем эмоциональные простыни.",
                accentHex: "#D26A8C",
                deepLinkPath: "/questions/love"
            )
        ],
        streakCount: 3,
        completionProgress: 0.42
    )
}
