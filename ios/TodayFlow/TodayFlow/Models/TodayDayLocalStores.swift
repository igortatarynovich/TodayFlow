import Foundation

// MARK: - Day engagement (web: todayflow.day_engagement.v1.{dateISO})

struct DayEngagementState: Codable, Equatable {
    var dayGoal: String?
    var morningMoodId: String?
    var morningMoodCapturedAtMs: Double?
    var focusTopicId: String?
    var focusTopicCapturedAtMs: Double?
    var eveningHighlightId: String?
}

enum TodayDayEngagementStore {
    private static let prefix = "todayflow.day_engagement.v1."

    static func storageKey(dateISO: String) -> String { prefix + dateISO }

    static func load(dateISO: String) -> DayEngagementState {
        guard let data = UserDefaults.standard.data(forKey: storageKey(dateISO: dateISO)),
              let decoded = try? JSONDecoder().decode(DayEngagementState.self, from: data)
        else {
            return DayEngagementState()
        }
        return decoded
    }

    static func save(dateISO: String, patch: DayEngagementState) {
        var next = load(dateISO: dateISO)
        if patch.dayGoal != nil { next.dayGoal = patch.dayGoal }
        if patch.morningMoodId != nil { next.morningMoodId = patch.morningMoodId }
        if patch.morningMoodCapturedAtMs != nil { next.morningMoodCapturedAtMs = patch.morningMoodCapturedAtMs }
        if patch.focusTopicId != nil { next.focusTopicId = patch.focusTopicId }
        if patch.focusTopicCapturedAtMs != nil { next.focusTopicCapturedAtMs = patch.focusTopicCapturedAtMs }
        if patch.eveningHighlightId != nil { next.eveningHighlightId = patch.eveningHighlightId }
        guard let data = try? JSONEncoder().encode(next) else { return }
        UserDefaults.standard.set(data, forKey: storageKey(dateISO: dateISO))
    }

    static func saveMorningMood(dateISO: String, moodId: String) {
        var state = load(dateISO: dateISO)
        state.morningMoodId = moodId
        state.morningMoodCapturedAtMs = Date().timeIntervalSince1970 * 1000
        guard let data = try? JSONEncoder().encode(state) else { return }
        UserDefaults.standard.set(data, forKey: storageKey(dateISO: dateISO))
    }

    static func allDateKeys() -> [String] {
        let p = prefix
        return UserDefaults.standard.dictionaryRepresentation().keys
            .filter { $0.hasPrefix(p) }
            .map { String($0.dropFirst(p.count)) }
    }
}

// MARK: - Day continuity (web: todayflow.day_continuity.v1.{dateISO})

enum DayFocusOutcome: String, Codable {
    case done
    case partial
    case notDone = "not_done"
}

struct DayContinuityRecord: Codable, Equatable {
    var dateISO: String
    var mainFocus: String
    var outcome: DayFocusOutcome?
    var outcomeNote: String?
    var closedAt: String?
}

enum TodayDayContinuityStore {
    private static let prefix = "todayflow.day_continuity.v1."

    static func storageKey(dateISO: String) -> String { prefix + dateISO }

    static func load(dateISO: String) -> DayContinuityRecord? {
        guard let data = UserDefaults.standard.data(forKey: storageKey(dateISO: dateISO)),
              let record = try? JSONDecoder().decode(DayContinuityRecord.self, from: data),
              !record.mainFocus.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
        else { return nil }
        return record
    }

    static func save(_ record: DayContinuityRecord) {
        guard let data = try? JSONEncoder().encode(record) else { return }
        UserDefaults.standard.set(data, forKey: storageKey(dateISO: record.dateISO))
    }

    static func isClosed(_ record: DayContinuityRecord?) -> Bool {
        guard let record, record.closedAt != nil, record.outcome != nil else { return false }
        return true
    }

    static func previousDateISO(_ dateISO: String) -> String {
        let parts = dateISO.split(separator: "-").compactMap { Int($0) }
        guard parts.count == 3 else { return dateISO }
        var comp = DateComponents(year: parts[0], month: parts[1], day: parts[2])
        comp.hour = 12
        guard let date = Calendar.current.date(from: comp),
              let prev = Calendar.current.date(byAdding: .day, value: -1, to: date)
        else { return dateISO }
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd"
        return f.string(from: prev)
    }

    static func scanClosedRecords() -> [DayContinuityRecord] {
        allRecords().filter { isClosed($0) }
            .sorted { ($0.closedAt ?? $0.dateISO) > ($1.closedAt ?? $1.dateISO) }
    }

    static func allRecords() -> [DayContinuityRecord] {
        let p = prefix
        return UserDefaults.standard.dictionaryRepresentation().keys
            .filter { $0.hasPrefix(p) }
            .compactMap { key -> DayContinuityRecord? in
                let dateISO = String(key.dropFirst(p.count))
                return load(dateISO: dateISO)
            }
    }
}

// MARK: - Energy map cache (web: todayflow.energy_map.v1.{dateISO})

struct EnergyMapDayRecord: Codable, Equatable {
    var dateISO: String
    var energyScore: Int
    var focusScore: Int?
    var balanceScore: Int?
    var capturedAt: String
    var source: String
}

enum EnergyMapStore {
    private static let prefix = "todayflow.energy_map.v1."

    static func storageKey(dateISO: String) -> String { prefix + dateISO }

    static func save(dateISO: String, energyScore: Int, focusScore: Int?, balanceScore: Int?, source: String) {
        let clamped = max(0, min(100, energyScore))
        let record = EnergyMapDayRecord(
            dateISO: dateISO,
            energyScore: clamped,
            focusScore: focusScore,
            balanceScore: balanceScore,
            capturedAt: ISO8601DateFormatter().string(from: Date()),
            source: source
        )
        guard let data = try? JSONEncoder().encode(record) else { return }
        UserDefaults.standard.set(data, forKey: storageKey(dateISO: dateISO))
    }

    static func load(dateISO: String) -> EnergyMapDayRecord? {
        guard let data = UserDefaults.standard.data(forKey: storageKey(dateISO: dateISO)),
              let record = try? JSONDecoder().decode(EnergyMapDayRecord.self, from: data)
        else { return nil }
        return record
    }

    static func allRecords() -> [EnergyMapDayRecord] {
        let p = prefix
        return UserDefaults.standard.dictionaryRepresentation().keys
            .filter { $0.hasPrefix(p) }
            .compactMap { key -> EnergyMapDayRecord? in
                let dateISO = String(key.dropFirst(p.count))
                return load(dateISO: dateISO)
            }
            .sorted { $0.dateISO > $1.dateISO }
    }
}

/// Dual-write mood into engagement store; backfill from ritual extras when scanning.
enum TodayDayEngagementSync {
    static func syncMorningMood(dateISO: String, moodId: String) {
        TodayDayEngagementStore.saveMorningMood(dateISO: dateISO, moodId: moodId)
    }

    static func syncDayGoal(dateISO: String, goal: String) {
        let trimmed = goal.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        TodayDayEngagementStore.save(dateISO: dateISO, patch: DayEngagementState(dayGoal: trimmed))
    }

    static func backfillFromRitualExtras(email: String?, dateISO: String) {
        guard let email else { return }
        let engagement = TodayDayEngagementStore.load(dateISO: dateISO)
        guard engagement.morningMoodId == nil,
              let extras = TodayFlowPersistence.shared.loadRitualDayExtras(for: email, dateISO: dateISO),
              let mood = extras.mood
        else { return }
        TodayDayEngagementStore.saveMorningMood(dateISO: dateISO, moodId: mood)
    }
}

// MARK: - Day continuity sync (web: todayDayContinuity + evening close)

enum TodayDayContinuitySync {
    private static let fallbackFocus = "Главная тема дня"

    static func resolveMainFocus(dateISO: String, cycle: TodayCycle?) -> String? {
        let engagementGoal = TodayDayEngagementStore.load(dateISO: dateISO).dayGoal?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if let engagementGoal, !engagementGoal.isEmpty { return engagementGoal }

        guard cycle?.date == dateISO else { return nil }
        let connection = cycle?.dayConnection
        if let intention = connection?.morningIntention?.trimmingCharacters(in: .whitespacesAndNewlines),
           !intention.isEmpty
        {
            return intention
        }
        if let focus = connection?.morningFocus?.trimmingCharacters(in: .whitespacesAndNewlines),
           !focus.isEmpty
        {
            return focus
        }
        return nil
    }

    static func saveDraft(dateISO: String, mainFocus: String) {
        let trimmed = mainFocus.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let existing = TodayDayContinuityStore.load(dateISO: dateISO)
        if TodayDayContinuityStore.isClosed(existing) { return }
        TodayDayContinuityStore.save(
            DayContinuityRecord(
                dateISO: dateISO,
                mainFocus: trimmed,
                outcome: existing?.outcome,
                outcomeNote: existing?.outcomeNote,
                closedAt: existing?.closedAt
            )
        )
    }

    static func backfillFromCycle(_ cycle: TodayCycle?) {
        guard let cycle else { return }
        let dateISO = cycle.date
        guard let focus = resolveMainFocus(dateISO: dateISO, cycle: cycle) else { return }

        if TodayDayEngagementStore.load(dateISO: dateISO).dayGoal == nil {
            TodayDayEngagementSync.syncDayGoal(dateISO: dateISO, goal: focus)
        }

        let existing = TodayDayContinuityStore.load(dateISO: dateISO)
        if TodayDayContinuityStore.isClosed(existing) { return }

        if cycle.dayConnection?.eveningCompleted == true {
            let note = cycle.dayConnection?.eveningReflection?
                .trimmingCharacters(in: .whitespacesAndNewlines)
            TodayDayContinuityStore.save(
                DayContinuityRecord(
                    dateISO: dateISO,
                    mainFocus: existing?.mainFocus ?? focus,
                    outcome: existing?.outcome ?? .done,
                    outcomeNote: existing?.outcomeNote ?? (note?.isEmpty == false ? note : nil),
                    closedAt: existing?.closedAt ?? ISO8601DateFormatter().string(from: Date())
                )
            )
            return
        }

        if existing == nil {
            saveDraft(dateISO: dateISO, mainFocus: focus)
        }
    }

    static func recordEveningSave(
        dateISO: String,
        cycle: TodayCycle?,
        markComplete: Bool,
        reflection: String,
        noticed: String,
        hardest: String,
        easierThanExpected: String
    ) {
        let focus = resolveMainFocus(dateISO: dateISO, cycle: cycle) ?? fallbackFocus
        let noteParts = [reflection, noticed, hardest, easierThanExpected]
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        let note = noteParts.isEmpty ? nil : noteParts.joined(separator: " · ")

        guard markComplete else {
            let existing = TodayDayContinuityStore.load(dateISO: dateISO)
            TodayDayContinuityStore.save(
                DayContinuityRecord(
                    dateISO: dateISO,
                    mainFocus: existing?.mainFocus ?? focus,
                    outcome: existing?.outcome,
                    outcomeNote: note ?? existing?.outcomeNote,
                    closedAt: existing?.closedAt
                )
            )
            return
        }

        TodayDayContinuityStore.save(
            DayContinuityRecord(
                dateISO: dateISO,
                mainFocus: focus,
                outcome: .done,
                outcomeNote: note,
                closedAt: ISO8601DateFormatter().string(from: Date())
            )
        )
    }
}

// MARK: - Wish map (web: todayflow.wish_map.v1.*)

struct WishAnchorRecord: Codable, Equatable, Identifiable {
    let id: String
    var title: String
    var source: String
    var createdAt: String
    var lastStepDate: String?
    var stepCount: Int
}

enum WishMapStore {
    private static let prefix = "todayflow.wish_map.v1."

    static func readLocalAnchors() -> [WishAnchorRecord] {
        let keys = UserDefaults.standard.dictionaryRepresentation().keys.filter { $0.hasPrefix(prefix) }
        return keys.compactMap { key -> WishAnchorRecord? in
            guard let data = UserDefaults.standard.data(forKey: key),
                  let record = try? JSONDecoder().decode(WishAnchorRecord.self, from: data)
            else { return nil }
            return record.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : record
        }
        .sorted { ($0.lastStepDate ?? $0.createdAt) > ($1.lastStepDate ?? $1.createdAt) }
    }

    static func saveLocalAnchor(title: String) -> WishAnchorRecord {
        let id = "local-\(Int(Date().timeIntervalSince1970 * 1000))"
        let record = WishAnchorRecord(
            id: id,
            title: title.trimmingCharacters(in: .whitespacesAndNewlines),
            source: "local",
            createdAt: ISO8601DateFormatter().string(from: Date()),
            lastStepDate: nil,
            stepCount: 0
        )
        if let data = try? JSONEncoder().encode(record) {
            UserDefaults.standard.set(data, forKey: prefix + id)
        }
        return record
    }

    static func mergeFromGoals(_ goals: [GoalTrack]) -> [WishAnchorRecord] {
        let fromGoals = goals
            .filter { $0.scope == .month && !$0.completed }
            .map { goal in
                let sorted = goal.stepDates.sorted()
                return WishAnchorRecord(
                    id: "goal-\(goal.id)",
                    title: goal.title,
                    source: "goal",
                    createdAt: sorted.first.map { "\($0)T12:00:00.000Z" } ?? ISO8601DateFormatter().string(from: Date()),
                    lastStepDate: sorted.last,
                    stepCount: sorted.count
                )
            }
        var byTitle: [String: WishAnchorRecord] = [:]
        for item in fromGoals + readLocalAnchors() {
            let key = item.title.lowercased()
            if let prev = byTitle[key], prev.stepCount >= item.stepCount { continue }
            byTitle[key] = item
        }
        return byTitle.values.sorted { ($0.lastStepDate ?? $0.createdAt) > ($1.lastStepDate ?? $1.createdAt) }
    }
}

// MARK: - Relationship map (web: todayflow.relationship_map.v1)

struct RelationshipCircleRecord: Codable, Equatable, Identifiable {
    let id: String
    var label: String
    var scenarioId: String
    var pairLine: String?
    var theme: String?
    var lastSeenAt: String
    var visitCount: Int
}

enum RelationshipMapStore {
    private static let storageKey = "todayflow.relationship_map.v1"
    private static let maxCircles = 24

    static func readCircles() -> [RelationshipCircleRecord] {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let decoded = try? JSONDecoder().decode([RelationshipCircleRecord].self, from: data)
        else { return [] }
        return decoded
    }

    static func recordVisit(label: String, scenarioId: String, pairLine: String?, theme: String?) {
        let trimmedLabel = label.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedScenario = scenarioId.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedLabel.isEmpty, !trimmedScenario.isEmpty else { return }
        let key = "\(trimmedLabel.lowercased())|\(trimmedScenario.lowercased())"
        let now = ISO8601DateFormatter().string(from: Date())
        var existing = readCircles()
        if let idx = existing.firstIndex(where: { "\($0.label.lowercased())|\($0.scenarioId.lowercased())" == key }) {
            var record = existing[idx]
            record.pairLine = pairLine ?? record.pairLine
            record.theme = theme ?? record.theme
            record.lastSeenAt = now
            record.visitCount += 1
            existing.remove(at: idx)
            existing.insert(record, at: 0)
        } else {
            existing.insert(
                RelationshipCircleRecord(
                    id: UUID().uuidString,
                    label: trimmedLabel,
                    scenarioId: trimmedScenario,
                    pairLine: pairLine,
                    theme: theme,
                    lastSeenAt: now,
                    visitCount: 1
                ),
                at: 0
            )
        }
        if let data = try? JSONEncoder().encode(Array(existing.prefix(maxCircles))) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
}
