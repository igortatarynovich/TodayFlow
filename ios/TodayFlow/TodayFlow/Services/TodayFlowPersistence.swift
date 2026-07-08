import Foundation

struct TodayFlowPersistence {
    static let shared = TodayFlowPersistence()

    private let defaults = UserDefaults.standard
    private let sessionKey = "todayflow.session"
    private let snapshotKey = "todayflow.snapshot"
    private let draftKey = "todayflow.draft"
    private let meaningOutboxKey = "todayflow.meaning.outbox.v1"
    private let meaningRingsCacheKey = "todayflow.meaning.rings.cache.v1"
    private let coreSetupSyncedPrefix = "todayflow.coreSetupSynced."
    private let profileSummarySeenPrefix = "todayflow.profileSummarySeen."
    private let authValidatedAtPrefix = "todayflow.authValidatedAt."
    private let snapshotSavedAtPrefix = "todayflow.snapshotSavedAt."
    private let openedDayPrefix = "todayflow.openedDay."
    private let cardRevealedPrefix = "todayflow.cardRevealed."
    private let numberRevealedPrefix = "todayflow.numberRevealed."
    private let ritualExtrasPrefix = "todayflow.ritualExtras.v1."

    func loadSession() -> AuthSession? {
        decode(AuthSession.self, forKey: sessionKey)
    }

    func loadSnapshot() -> TodayFlowPersistedState? {
        decode(TodayFlowPersistedState.self, forKey: snapshotKey)
    }

    func loadDraft() -> BirthProfileDraft? {
        decode(BirthProfileDraft.self, forKey: draftKey)
    }

    func loadMeaningOutbox() -> [MeaningEventInput] {
        decode([MeaningEventInput].self, forKey: meaningOutboxKey) ?? []
    }

    func saveMeaningOutbox(_ events: [MeaningEventInput]) {
        encode(events, forKey: meaningOutboxKey)
    }

    func loadMeaningRingsCache() -> MeaningRingsResponse? {
        decode(MeaningRingsResponse.self, forKey: meaningRingsCacheKey)
    }

    func saveMeaningRingsCache(_ cache: MeaningRingsResponse?) {
        if let cache {
            encode(cache, forKey: meaningRingsCacheKey)
        } else {
            defaults.removeObject(forKey: meaningRingsCacheKey)
        }
    }

    func saveSession(_ session: AuthSession?) {
        if let session {
            encode(session, forKey: sessionKey)
        } else {
            defaults.removeObject(forKey: sessionKey)
        }
    }

    func save(snapshot: TodayFlowPersistedState, draft: BirthProfileDraft?) {
        encode(snapshot, forKey: snapshotKey)
        if let draft {
            encode(draft, forKey: draftKey)
        } else {
            defaults.removeObject(forKey: draftKey)
        }
    }

    func clear() {
        defaults.removeObject(forKey: sessionKey)
        defaults.removeObject(forKey: snapshotKey)
        defaults.removeObject(forKey: draftKey)
        defaults.removeObject(forKey: meaningOutboxKey)
        defaults.removeObject(forKey: meaningRingsCacheKey)
    }

    func clearSnapshot() {
        defaults.removeObject(forKey: snapshotKey)
        defaults.removeObject(forKey: draftKey)
    }

    func hasCoreSetupSyncMarker(for email: String?) -> Bool {
        guard let key = coreSetupSyncKey(for: email) else { return false }
        return defaults.bool(forKey: key)
    }

    func saveCoreSetupSyncMarker(for email: String?) {
        guard let key = coreSetupSyncKey(for: email) else { return }
        defaults.set(true, forKey: key)
    }

    func clearCoreSetupSyncMarker(for email: String?) {
        guard let key = coreSetupSyncKey(for: email) else { return }
        defaults.removeObject(forKey: key)
    }

    func hasProfileSummarySeen(for email: String?) -> Bool {
        guard let key = profileSummarySeenKey(for: email) else { return false }
        return defaults.bool(forKey: key)
    }

    func saveProfileSummarySeen(for email: String?) {
        guard let key = profileSummarySeenKey(for: email) else { return }
        defaults.set(true, forKey: key)
    }

    func clearProfileSummarySeen(for email: String?) {
        guard let key = profileSummarySeenKey(for: email) else { return }
        defaults.removeObject(forKey: key)
    }

    func loadLastAuthValidatedAt(for email: String?) -> Date? {
        guard let key = authValidatedAtKey(for: email) else { return nil }
        let ts = defaults.double(forKey: key)
        guard ts > 0 else { return nil }
        return Date(timeIntervalSince1970: ts)
    }

    func saveLastAuthValidatedAt(for email: String?, date: Date = Date()) {
        guard let key = authValidatedAtKey(for: email) else { return }
        defaults.set(date.timeIntervalSince1970, forKey: key)
    }

    func clearLastAuthValidatedAt(for email: String?) {
        guard let key = authValidatedAtKey(for: email) else { return }
        defaults.removeObject(forKey: key)
    }

    func loadLastSnapshotSavedAt(for email: String?) -> Date? {
        guard let key = snapshotSavedAtKey(for: email) else { return nil }
        let ts = defaults.double(forKey: key)
        guard ts > 0 else { return nil }
        return Date(timeIntervalSince1970: ts)
    }

    func saveLastSnapshotSavedAt(for email: String?, date: Date = Date()) {
        guard let key = snapshotSavedAtKey(for: email) else { return }
        defaults.set(date.timeIntervalSince1970, forKey: key)
    }

    func clearLastSnapshotSavedAt(for email: String?) {
        guard let key = snapshotSavedAtKey(for: email) else { return }
        defaults.removeObject(forKey: key)
    }

    func hasOpenedDay(for email: String?, dateISO: String) -> Bool {
        guard let key = openedDayKey(for: email, dateISO: dateISO) else { return false }
        return defaults.bool(forKey: key)
    }

    func saveOpenedDay(for email: String?, dateISO: String) {
        guard let key = openedDayKey(for: email, dateISO: dateISO) else { return }
        defaults.set(true, forKey: key)
    }

    func clearOpenedDay(for email: String?, dateISO: String) {
        guard let key = openedDayKey(for: email, dateISO: dateISO) else { return }
        defaults.removeObject(forKey: key)
    }

    func hasCardRevealed(for email: String?, dateISO: String) -> Bool {
        guard let key = userScopedDayKey(prefix: cardRevealedPrefix, email: email, dateISO: dateISO) else { return false }
        return defaults.bool(forKey: key)
    }

    func saveCardRevealed(for email: String?, dateISO: String) {
        guard let key = userScopedDayKey(prefix: cardRevealedPrefix, email: email, dateISO: dateISO) else { return }
        defaults.set(true, forKey: key)
    }

    func hasNumberRevealed(for email: String?, dateISO: String) -> Bool {
        guard let key = userScopedDayKey(prefix: numberRevealedPrefix, email: email, dateISO: dateISO) else { return false }
        return defaults.bool(forKey: key)
    }

    func saveNumberRevealed(for email: String?, dateISO: String) {
        guard let key = userScopedDayKey(prefix: numberRevealedPrefix, email: email, dateISO: dateISO) else { return }
        defaults.set(true, forKey: key)
    }

    func clearNumberRevealed(for email: String?, dateISO: String) {
        guard let key = userScopedDayKey(prefix: numberRevealedPrefix, email: email, dateISO: dateISO) else { return }
        defaults.removeObject(forKey: key)
    }

    func loadRitualDayExtras(for email: String?, dateISO: String) -> RitualDayExtras? {
        guard let key = userScopedDayKey(prefix: ritualExtrasPrefix, email: email, dateISO: dateISO) else { return nil }
        return decode(RitualDayExtras.self, forKey: key)
    }

    func saveRitualDayExtras(for email: String?, dateISO: String, extras: RitualDayExtras) {
        guard let key = userScopedDayKey(prefix: ritualExtrasPrefix, email: email, dateISO: dateISO) else { return }
        encode(extras, forKey: key)
    }

    func clearRitualDayExtras(for email: String?, dateISO: String) {
        guard let key = userScopedDayKey(prefix: ritualExtrasPrefix, email: email, dateISO: dateISO) else { return }
        defaults.removeObject(forKey: key)
    }

    private func decode<T: Decodable>(_ type: T.Type, forKey key: String) -> T? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(type, from: data)
    }

    private func encode<T: Encodable>(_ value: T, forKey key: String) {
        guard let data = try? JSONEncoder().encode(value) else { return }
        defaults.set(data, forKey: key)
    }

    private func coreSetupSyncKey(for email: String?) -> String? {
        guard let email else { return nil }
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return nil }
        return coreSetupSyncedPrefix + normalized
    }

    private func profileSummarySeenKey(for email: String?) -> String? {
        guard let email else { return nil }
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return nil }
        return profileSummarySeenPrefix + normalized
    }

    private func authValidatedAtKey(for email: String?) -> String? {
        guard let email else { return nil }
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return nil }
        return authValidatedAtPrefix + normalized
    }

    private func snapshotSavedAtKey(for email: String?) -> String? {
        guard let email else { return nil }
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !normalized.isEmpty else { return nil }
        return snapshotSavedAtPrefix + normalized
    }

    private func userScopedDayKey(prefix: String, email: String?, dateISO: String) -> String? {
        guard let email else { return nil }
        let normalizedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let normalizedDate = dateISO.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalizedEmail.isEmpty, !normalizedDate.isEmpty else { return nil }
        return prefix + normalizedEmail + "." + normalizedDate
    }

    private func openedDayKey(for email: String?, dateISO: String) -> String? {
        userScopedDayKey(prefix: openedDayPrefix, email: email, dateISO: dateISO)
    }
}

/// Микро-ответы ритуала на день — паритет с веб `todayflow.ritual.v1` (настроение, голова, карта, число, база).
struct RitualDayExtras: Codable, Equatable {
    var mood: String?
    var headTopic: String?
    var honestStep: String?
    var numberRhythm: String?
    var essentials: [String]
    /// Интерактивная карта дня (пользователь вытягивает сам), паритет с веб `todayflow.ritual.v1`.
    var tarotMainId: Int?
    var tarotClarifierId: Int?
    var tarotApplied: Bool?
    /// Карта зафиксирована и пользователь нажал «Продолжить» к числу (паритет с веб `tarotContinueAck`).
    var tarotContinueAck: Bool?
    /// После «Готово» в блоке настроения — как на макете, чек-ин скрыт, дальше сводка «Твой день».
    var checkInSubmitted: Bool?
}

struct TodayFlowPersistedState: Codable {
    let ownerEmail: String
    let profile: BirthProfile
    let todayCycle: TodayCycle?
    let fusionIndex: FusionIndex?
    let fusionHistory: [FusionIndex]
    let dailyFocus: DailyFocus
    let rituals: [Ritual]
    let user: UserProfile
}
