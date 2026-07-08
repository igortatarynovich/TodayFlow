import Foundation
import SwiftUI

enum MapsLocale {
    case ru
    case en
}

struct MapHeatmapCellModel: Identifiable {
    var id: String { dateISO }
    let dateISO: String
    let color: Color
    let hasMark: Bool
    let isFuture: Bool
    let title: String
}

struct MoodMapDayRecord {
    let dateISO: String
    let moodId: String
    let moodLabel: String
    let focusLabel: String?
    let dayGoal: String?
}

enum MoodMapModel {
    static let windowDays = 35
    static let emptyColor = Color(red: 180 / 255, green: 170 / 255, blue: 158 / 255, opacity: 0.35)

    private static let moodColors: [String: Color] = [
        "calm": Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.88),
        "driven": Color(red: 155 / 255, green: 118 / 255, blue: 70 / 255, opacity: 0.92),
        "inspired": Color(red: 201 / 255, green: 168 / 255, blue: 115 / 255, opacity: 0.9),
        "tired": Color(red: 154 / 255, green: 132 / 255, blue: 104 / 255, opacity: 0.72),
        "anxious": Color(red: 180 / 255, green: 120 / 255, blue: 100 / 255, opacity: 0.78),
        "overloaded": Color(red: 140 / 255, green: 90 / 255, blue: 80 / 255, opacity: 0.85),
        "irritated": Color(red: 180 / 255, green: 120 / 255, blue: 100 / 255, opacity: 0.78),
        "heavy": Color(red: 154 / 255, green: 132 / 255, blue: 104 / 255, opacity: 0.72),
        "quiet_wish": Color(red: 154 / 255, green: 132 / 255, blue: 104 / 255, opacity: 0.72),
        "motivated": Color(red: 155 / 255, green: 118 / 255, blue: 70 / 255, opacity: 0.92),
        "move_wish": Color(red: 155 / 255, green: 118 / 255, blue: 70 / 255, opacity: 0.92),
    ]

    private static let moodLabels: [String: String] = {
        var map = Dictionary(uniqueKeysWithValues: TodayRitualCopy.moodGridMockup.map { ($0.id, $0.label) })
        map["inspired"] = "Вдохновён"
        map["overloaded"] = "Перегружен"
        return map
    }()

    static func moodLabel(for id: String) -> String {
        moodLabels[id] ?? id
    }

    static func scanRecords(ritualEmail: String? = nil) -> [MoodMapDayRecord] {
        if let ritualEmail, let today = todayISO() {
            TodayDayEngagementSync.backfillFromRitualExtras(email: ritualEmail, dateISO: today)
        }
        let focusLabels: [String: String] = [
            "work": "Работа", "money": "Деньги", "relations": "Отношения", "family": "Семья",
            "health": "Здоровье", "growth": "Саморазвитие", "decision": "Решение", "other": "Другое",
        ]
        return TodayDayEngagementStore.allDateKeys().compactMap { dateISO in
            let e = TodayDayEngagementStore.load(dateISO: dateISO)
            guard let moodId = e.morningMoodId else { return nil }
            return MoodMapDayRecord(
                dateISO: dateISO,
                moodId: moodId,
                moodLabel: moodLabel(for: moodId),
                focusLabel: e.focusTopicId.flatMap { focusLabels[$0] ?? $0 },
                dayGoal: e.dayGoal
            )
        }
        .sorted { $0.dateISO > $1.dateISO }
    }

    static func buildCells(todayISO: String, records: [MoodMapDayRecord]) -> [MapHeatmapCellModel] {
        let byDate = Dictionary(uniqueKeysWithValues: records.map { ($0.dateISO, $0) })
        return mapWindow(todayISO: todayISO).map { dateISO in
            let record = byDate[dateISO]
            let isFuture = dateISO > todayISO
            let color = record.map { moodColors[$0.moodId] ?? Color(red: 191 / 255, green: 151 / 255, blue: 95 / 255, opacity: 0.62) } ?? emptyColor
            return MapHeatmapCellModel(
                dateISO: dateISO,
                color: color,
                hasMark: record != nil,
                isFuture: isFuture,
                title: record.map { "\(dateISO) — \($0.moodLabel)" } ?? dateISO
            )
        }
    }

    static func dayStory(_ record: MoodMapDayRecord, locale: MapsLocale) -> String {
        let continuity = TodayDayContinuityStore.load(dateISO: record.dateISO)
        var parts: [String] = []
        if locale == .ru {
            parts.append("\(formatDate(record.dateISO, locale: locale)) — \(record.moodLabel).")
            if let focus = record.focusLabel { parts.append("Фокус был на «\(focus)».") }
            if let goal = record.dayGoal { parts.append("Обещание дня: «\(goal)».") }
            if let outcome = continuity?.outcome { parts.append(outcomeCopyRu(outcome)) }
        } else {
            parts.append("\(formatDate(record.dateISO, locale: locale)) — \(record.moodLabel).")
            if let focus = record.focusLabel { parts.append("Focus was on \(focus.lowercased()).") }
            if let goal = record.dayGoal { parts.append("Promise of the day: “\(goal)”.") }
            if let outcome = continuity?.outcome { parts.append(outcomeCopyEn(outcome)) }
        }
        return parts.joined(separator: " ")
    }

    static func observation(records: [MoodMapDayRecord], locale: MapsLocale) -> String? {
        guard records.count >= 3 else { return nil }
        var counts: [String: Int] = [:]
        records.forEach { counts[$0.moodId, default: 0] += 1 }
        guard let top = counts.max(by: { $0.value < $1.value }) else { return nil }
        let label = moodLabel(for: top.key)
        if locale == .ru {
            return "За последние отметки чаще всего было «\(label)» — \(top.value) дн. Так складывается тон твоих дней."
        }
        return "Lately “\(label)” shows up most often—\(top.value) days."
    }

    private static func outcomeCopyRu(_ outcome: DayFocusOutcome) -> String {
        switch outcome {
        case .done: return "Вечером день закрыт — главное сделано."
        case .partial: return "Вечером день закрыт частично."
        case .notDone: return "Вечером обещание дня не удалось выполнить."
        }
    }

    private static func outcomeCopyEn(_ outcome: DayFocusOutcome) -> String {
        switch outcome {
        case .done: return "You closed the day—main focus done."
        case .partial: return "You closed the day partly."
        case .notDone: return "The promise of the day didn’t land by evening."
        }
    }
}

enum EnergyMapModel {
    static let windowDays = 35

    static func scanRecordsWithMoodFallback() -> [EnergyMapDayRecord] {
        var byDate = Dictionary(uniqueKeysWithValues: EnergyMapStore.allRecords().map { ($0.dateISO, $0) })
        let infer: [String: Int] = ["tired": 32, "overloaded": 28, "anxious": 36, "calm": 56, "driven": 78, "inspired": 82]
        for dateISO in TodayDayEngagementStore.allDateKeys() where byDate[dateISO] == nil {
            let mood = TodayDayEngagementStore.load(dateISO: dateISO).morningMoodId
            guard let mood, let score = infer[mood] else { continue }
            byDate[dateISO] = EnergyMapDayRecord(
                dateISO: dateISO, energyScore: score, focusScore: nil, balanceScore: nil,
                capturedAt: ISO8601DateFormatter().string(from: Date()), source: "mood_infer"
            )
        }
        return byDate.values.sorted { $0.dateISO > $1.dateISO }
    }

    static func cellColor(score: Int) -> Color {
        let s = max(0, min(100, score))
        if s < 38 { return Color(red: 154 / 255, green: 132 / 255, blue: 104 / 255, opacity: 0.72) }
        if s < 58 { return Color(red: 191 / 255, green: 168 / 255, blue: 120 / 255, opacity: 0.78) }
        if s < 78 { return Color(red: 175 / 255, green: 138 / 255, blue: 82 / 255, opacity: 0.88) }
        return Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.92)
    }

    static func buildCells(todayISO: String, records: [EnergyMapDayRecord]) -> [MapHeatmapCellModel] {
        let byDate = Dictionary(uniqueKeysWithValues: records.map { ($0.dateISO, $0) })
        return mapWindow(todayISO: todayISO).map { dateISO in
            let record = byDate[dateISO]
            let isFuture = dateISO > todayISO
            return MapHeatmapCellModel(
                dateISO: dateISO,
                color: record.map { cellColor(score: $0.energyScore) } ?? MoodMapModel.emptyColor,
                hasMark: record != nil,
                isFuture: isFuture,
                title: record.map { "\(dateISO) — \(tempoLabel($0.energyScore))" } ?? dateISO
            )
        }
    }

    static func tempoLabel(_ score: Int) -> String {
        let s = max(0, min(100, score))
        if s < 38 { return "тихий" }
        if s < 58 { return "спокойный" }
        if s < 78 { return "ровный" }
        return "подвижный"
    }

    static func dayStory(_ record: EnergyMapDayRecord, locale: MapsLocale) -> String {
        let engagement = TodayDayEngagementStore.load(dateISO: record.dateISO)
        let continuity = TodayDayContinuityStore.load(dateISO: record.dateISO)
        let tempo = tempoLabel(record.energyScore)
        if locale == .ru {
            var parts = ["\(formatDate(record.dateISO, locale: locale)) — \(tempo) темп дня."]
            if let mood = engagement.morningMoodId {
                parts.append("Утром отмечено: «\(MoodMapModel.moodLabel(for: mood))».")
            }
            if continuity?.outcome == .done { parts.append("Вечером главное удалось закрыть.") }
            if continuity?.outcome == .notDone { parts.append("К вечеру обещание дня осталось открытым.") }
            return parts.joined(separator: " ")
        }
        var parts = ["\(formatDate(record.dateISO, locale: locale)) — a \(tempo) day tempo."]
        if let mood = engagement.morningMoodId {
            parts.append("Morning mark: “\(MoodMapModel.moodLabel(for: mood))”.")
        }
        if continuity?.outcome == .done { parts.append("By evening, the main focus landed.") }
        if continuity?.outcome == .notDone { parts.append("By evening, the day’s promise stayed open.") }
        return parts.joined(separator: " ")
    }

    static func observation(records: [EnergyMapDayRecord], locale: MapsLocale) -> String? {
        guard records.count >= 3 else { return nil }
        let strong = records.filter { $0.energyScore >= 78 }.count
        if locale == .ru {
            if strong >= 2 { return "В последние отметки чаще выпадали подвижные и ровные дни — темп держится." }
            return "Темп дней постепенно складывается в узор — продолжай отмечать Today."
        }
        if strong >= 2 { return "Lately steady and active days show up more often." }
        return "Your day tempo is forming a pattern."
    }
}

enum PromiseMapOutcomeKind: String {
    case done, partial, notDone = "not_done", open
}

struct PromiseMapDayRecord {
    let dateISO: String
    let promiseText: String
    let outcome: PromiseMapOutcomeKind
}

enum PromiseMapModel {
    static func scanRecords() -> [PromiseMapDayRecord] {
        var byDate: [String: PromiseMapDayRecord] = [:]
        for record in TodayDayContinuityStore.allRecords() {
            let closed = TodayDayContinuityStore.isClosed(record)
            let outcome: PromiseMapOutcomeKind
            if closed, let o = record.outcome {
                outcome = o == .done ? .done : (o == .partial ? .partial : .notDone)
            } else {
                outcome = .open
            }
            byDate[record.dateISO] = PromiseMapDayRecord(dateISO: record.dateISO, promiseText: record.mainFocus, outcome: outcome)
        }
        for dateISO in TodayDayEngagementStore.allDateKeys() where byDate[dateISO] == nil {
            let goal = TodayDayEngagementStore.load(dateISO: dateISO).dayGoal?.trimmingCharacters(in: .whitespacesAndNewlines)
            guard let goal, !goal.isEmpty else { continue }
            byDate[dateISO] = PromiseMapDayRecord(dateISO: dateISO, promiseText: goal, outcome: .open)
        }
        return byDate.values.sorted { $0.dateISO > $1.dateISO }
    }

    static func cellColor(_ outcome: PromiseMapOutcomeKind) -> Color {
        switch outcome {
        case .done: return Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.92)
        case .partial: return Color(red: 191 / 255, green: 151 / 255, blue: 95 / 255, opacity: 0.9)
        case .notDone: return Color(red: 180 / 255, green: 120 / 255, blue: 100 / 255, opacity: 0.78)
        case .open: return Color(red: 214 / 255, green: 179 / 255, blue: 122 / 255, opacity: 0.62)
        }
    }

    static func buildCells(todayISO: String, records: [PromiseMapDayRecord]) -> [MapHeatmapCellModel] {
        let byDate = Dictionary(uniqueKeysWithValues: records.map { ($0.dateISO, $0) })
        return mapWindow(todayISO: todayISO).map { dateISO in
            let record = byDate[dateISO]
            return MapHeatmapCellModel(
                dateISO: dateISO,
                color: record.map { cellColor($0.outcome) } ?? MoodMapModel.emptyColor,
                hasMark: record != nil,
                isFuture: dateISO > todayISO,
                title: record.map { "\(dateISO) — \($0.promiseText)" } ?? dateISO
            )
        }
    }

    static func dayStory(_ record: PromiseMapDayRecord, locale: MapsLocale) -> String {
        if locale == .ru {
            var parts = ["\(formatDate(record.dateISO, locale: locale)) — обещание: «\(record.promiseText)»."]
            switch record.outcome {
            case .open: parts.append("Вечер ещё не закрыт — исход дня пока открыт.")
            case .done: parts.append("К вечеру главное удалось закрыть.")
            case .partial: parts.append("К вечеру получилось частично.")
            case .notDone: parts.append("К вечеру обещание осталось открытым.")
            }
            return parts.joined(separator: " ")
        }
        var parts = ["\(formatDate(record.dateISO, locale: locale)) — promise: “\(record.promiseText)”."]
        switch record.outcome {
        case .open: parts.append("Evening isn’t closed yet.")
        case .done: parts.append("By evening, the main focus landed.")
        case .partial: parts.append("By evening it landed partly.")
        case .notDone: parts.append("By evening the promise stayed open.")
        }
        return parts.joined(separator: " ")
    }

    static func observation(records: [PromiseMapDayRecord], locale: MapsLocale) -> String? {
        let closed = records.filter { $0.outcome != .open }
        guard closed.count >= 3 else { return nil }
        let done = closed.filter { $0.outcome == .done }.count
        if locale == .ru {
            if done >= 2 { return "В последние закрытые дни обещания чаще удавалось закрыть — ритм держится." }
            return "История обещаний складывается — каждый вечер добавляет новую точку."
        }
        if done >= 2 { return "Lately you’ve closed more promises than you left open." }
        return "Your promise story is forming."
    }
}

// MARK: - Shared helpers

func todayISO() -> String? {
    let f = DateFormatter()
    f.locale = Locale(identifier: "en_US_POSIX")
    f.dateFormat = "yyyy-MM-dd"
    return f.string(from: Date())
}

func mapWindow(todayISO: String, days: Int = 35) -> [String] {
    let f = DateFormatter()
    f.locale = Locale(identifier: "en_US_POSIX")
    f.dateFormat = "yyyy-MM-dd"
    guard let end = f.date(from: todayISO) else { return [] }
    return (0 ..< days).reversed().compactMap { offset in
        guard let d = Calendar.current.date(byAdding: .day, value: -offset, to: end) else { return nil }
        return f.string(from: d)
    }
}

func formatDate(_ dateISO: String, locale: MapsLocale) -> String {
    let parts = dateISO.split(separator: "-").compactMap { Int($0) }
    guard parts.count == 3,
          let date = Calendar.current.date(from: DateComponents(year: parts[0], month: parts[1], day: parts[2], hour: 12))
    else { return dateISO }
    let f = DateFormatter()
    f.locale = locale == .ru ? Locale(identifier: "ru_RU") : Locale(identifier: "en_US")
    f.dateFormat = "d MMMM"
    return f.string(from: date)
}

enum MapNavigationDestination: Hashable {
    case hub
    case mood
    case energy
    case promise
    case habits
    case ascetic
    case wish
    case relationship
    case tarot
}

struct ProfileMapExploreCardModel: Identifiable {
    let id: String
    let title: String
    let desc: String
    let destination: MapNavigationDestination?
    let opensRhythm: Bool
    let primary: Bool
}

struct CycleMapEntryIn {
    let date: String
    let periodIntensity: String?
    let ovulation: Bool
    let fertileWindow: Bool
}

enum CycleMapModel {
    private static let activeMoods: Set<String> = ["driven", "inspired", "motivated"]
    private static let quietMoods: Set<String> = ["tired", "calm", "heavy", "overloaded", "anxious"]

    static func hasPeriodIntensity(_ intensity: String?) -> Bool {
        let key = (intensity ?? "").lowercased()
        return key == "light" || key == "medium" || key == "heavy"
    }

    static func countMenstrualCycleStarts(_ entries: [CycleMapEntryIn]) -> Int {
        let sorted = entries.sorted { $0.date < $1.date }
        var starts = 0
        var inPeriod = false
        var lastDate: String?
        for entry in sorted {
            if let lastDate, daysBetweenISO(lastDate, entry.date) > 1 {
                inPeriod = false
            }
            let onPeriod = hasPeriodIntensity(entry.periodIntensity)
            if onPeriod && !inPeriod { starts += 1 }
            inPeriod = onPeriod
            lastDate = entry.date
        }
        return starts
    }

    static func observation(
        entries: [CycleMapEntryIn],
        moodRecords: [MoodMapDayRecord],
        locale: MapsLocale = .ru
    ) -> String? {
        let cycleStarts = countMenstrualCycleStarts(entries)
        if cycleStarts < 4 && entries.count < 28 { return nil }

        let moodByDate = Dictionary(uniqueKeysWithValues: moodRecords.map { ($0.dateISO, $0) })
        var fertileMarks = 0
        var fertileActive = 0
        var periodMarks = 0
        var periodQuiet = 0

        for entry in entries {
            guard let mood = moodByDate[entry.date] else { continue }
            if entry.fertileWindow {
                fertileMarks += 1
                if activeMoods.contains(mood.moodId) { fertileActive += 1 }
            }
            if hasPeriodIntensity(entry.periodIntensity) {
                periodMarks += 1
                if quietMoods.contains(mood.moodId) { periodQuiet += 1 }
            }
        }

        if locale == .ru {
            if fertileMarks >= 4 && fertileActive >= 2 {
                return "В фертильные фазы на карте настроения чаще подвижные отметки — узор из нескольких циклов."
            }
            if periodMarks >= 4 && periodQuiet >= 3 {
                return "В дни с отметкой интенсивности цикла карта настроения чаще спокойнее — это уже повторяется."
            }
            if cycleStarts >= 4 {
                return "Несколько циклов на карте — ритм месяца начинает влиять на узор дней. Контекст, не цифра дня."
            }
            return nil
        }

        if fertileMarks >= 4 && fertileActive >= 2 {
            return "During fertile phases your mood map shows more active marks—a pattern across several cycles."
        }
        if periodMarks >= 4 && periodQuiet >= 3 {
            return "On high-intensity cycle days your mood map is often quieter—that pattern is repeating."
        }
        if cycleStarts >= 4 {
            return "Several cycles on the map—monthly rhythm is shaping the pattern. Context, not a day number."
        }
        return nil
    }
}

enum ProfileLivingMapsModel {
    static let exploreCards: [ProfileMapExploreCardModel] = [
        ProfileMapExploreCardModel(id: "hub", title: "Все карты", desc: "Хаб карт и ритма", destination: .hub, opensRhythm: false, primary: true),
        ProfileMapExploreCardModel(id: "mood", title: "Настроение", desc: "Утренние отметки", destination: .mood, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "energy", title: "Энергия", desc: "Темп дня", destination: .energy, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "promise", title: "Обещания", desc: "Вечернее закрытие", destination: .promise, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "habits", title: "Привычки", desc: "Цветовая карта", destination: .habits, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "ascetic", title: "Аскезы", desc: "Тропа пути", destination: .ascetic, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "wish", title: "Желания", desc: "Созвездие якорей", destination: .wish, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "relationship", title: "Связи", desc: "Круги внимания", destination: .relationship, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "tarot", title: "Таро", desc: "Архетипическая линия", destination: .tarot, opensRhythm: false, primary: false),
        ProfileMapExploreCardModel(id: "rhythm", title: "Ритм", desc: "Месяц и Flow", destination: nil, opensRhythm: true, primary: false),
    ]

    static func localObservation() -> String? {
        let closed = TodayDayContinuityStore.scanClosedRecords()
        if closed.count >= 3 {
            let done = closed.filter { $0.outcome == .done }.count
            if done >= 2 {
                return "Вечером дни чаще закрываются с главным сделанным — на картах это уже заметно."
            }
            if closed.count >= 5 {
                return "\(closed.count) закрытых дней на карте — история складывается без ручной статистики."
            }
        }
        if let mood = MoodMapModel.observation(records: MoodMapModel.scanRecords(), locale: .ru) {
            return mood
        }
        if let promise = PromiseMapModel.observation(records: PromiseMapModel.scanRecords(), locale: .ru) {
            return promise
        }
        if closed.count == 1 {
            return "Первая точка на карте — продолжай отмечать Today, узор проявится сам."
        }
        return nil
    }
}

func dateFromISO(_ dateISO: String) -> Date? {
    let f = DateFormatter()
    f.locale = Locale(identifier: "en_US_POSIX")
    f.dateFormat = "yyyy-MM-dd"
    f.timeZone = TimeZone(secondsFromGMT: 0)
    return f.date(from: dateISO)
}

func daysBetweenISO(_ isoA: String, _ isoB: String) -> Int {
    guard let a = dateFromISO(isoA), let b = dateFromISO(isoB) else { return 0 }
    return Calendar(identifier: .gregorian).dateComponents([.day], from: a, to: b).day ?? 0
}
