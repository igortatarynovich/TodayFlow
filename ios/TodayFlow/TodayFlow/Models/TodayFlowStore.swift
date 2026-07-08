import Foundation
import Observation
import SwiftUI

@MainActor
@Observable
final class TodayFlowStore {
    enum LoadState: Equatable {
        case idle
        case loading
        case loaded
        case failed(String)
    }

    enum SessionRefreshState: Equatable {
        case idle
        case refreshing
        case ready
    }

    var authSession: AuthSession?
    var birthProfile: BirthProfile?
    var todayCycle: TodayCycle?
    var fusionIndex: FusionIndex?
    var fusionHistory: [FusionIndex] = []
    var accountSettings: AccountSettings?
    var coreProfile: CoreProfileResponse?
    var profileSummary: ProfileSummaryResponse?
    var profileBuildStatus: ProfileBuildStatusResponse?
    var compactUserModel: CompactUserModelResponse?
    var cumConfidenceHistory: CompactUserModelConfidenceHistoryResponse?
    var meaningRings: [MeaningRingItem] = []
    var natalChart: NatalChartPreview?
    var todayGuideNarrative: TodayNarrativeResponse?
    var todayContract: TodayContractV1?
    var todayDayNarrative: TodayNarrativeResponse?
    var todaySpheresNarrative: TodayNarrativeResponse?
    var todayEveningNarrative: TodayNarrativeResponse?
    /// Последний ritual_context после ритуала — для day_layer / spheres / evening (intent).
    private var lastRitualNarrativeContext: TodayNarrativeRitualContextPayload?
    private var lastRitualNarrativeContextDate: String?
    var dailyFocus = DailyFocus.placeholder
    var rituals = Ritual.placeholder
    var user = UserProfile.placeholder
    var loadState: LoadState = .idle
    var hasSeenProfileSummary = false
    var sessionRefreshState: SessionRefreshState = .idle
    var sessionWarningMessage: String?
    var lastSessionValidatedAt: Date?
    var lastSnapshotSavedAt: Date?
    var isSyncingCoreSetup = false
    private var lastSubmittedDraft: BirthProfileDraft?

    // MARK: - Tracker (/today/*, /tracking/*)

    var today = TodayDashboard.placeholder
    var calendar = CalendarSnapshot.empty
    var goals: [GoalTrack] = []
    var isBootstrapping = false
    var isRefreshingToday = false
    var isRefreshingCalendar = false
    var isRefreshingGoals = false
    var isSaving = false
    var didBootstrap = false
    var lastError: String?
    var selectedCalendarDateISO = TodayFlowStore.isoDate(from: Date())
    /// Навигация из Today («Собрать день»): после переключения на таб Flow обрабатывается в `CalendarView`.
    var pendingTrackerQuickCreate: TrackerQuickCreateKind?
    var affirmationsCatalog: [AffirmationCatalogItem] = []
    var affirmationDoneById: [String: Bool] = [:]
    var diaryEntries: [ObservationDiaryEntry] = []
    var selectedDiaryEntry: ObservationDiaryEntry?
    var autoInsights: [AutoInsightItem] = []
    var isRefreshingDiary = false
    var isRefreshingInsights = false
    var isGeneratingInsight = false
    private let meaningRuntime = MeaningRuntime()

    /// После выбора «Натальная карта» в обзоре — `ProfileView` прокручивает к блоку карты (UUID, чтобы сработал повторный тап).
    var profileNatalScrollToken: UUID?

    /// Deep link → push карты в Profile (`/maps/*`, `/tracking/progress`, `/habits`).
    var pendingMapNavigation: MapNavigationDestination?

    /// Deep link href из API / universal links — обрабатывается в `ContentView`.
    var pendingHrefRoute: String?

    func requestMapNavigation(_ destination: MapNavigationDestination) {
        pendingMapNavigation = destination
    }

    func openHref(_ href: String) {
        pendingHrefRoute = href
    }

    /// Подтягивает fusion за окно 35 дней в локальный кэш Energy Map (паритет web `/maps/energy`).
    func syncEnergyMapFusionBatch(windowDays: Int = 35) async {
        guard let token = authSession?.token, let today = todayISO() else { return }
        let dates = mapWindow(todayISO: today, days: windowDays)
        await withTaskGroup(of: Void.self) { group in
            for dateISO in dates {
                group.addTask {
                    guard let date = dateFromISO(dateISO) else { return }
                    guard let fusion = try? await TodayFlowAPIClient.shared.fetchFusionIndex(
                        token: token,
                        targetDate: date
                    ) else { return }
                    await MainActor.run {
                        EnergyMapStore.save(
                            dateISO: dateISO,
                            energyScore: fusion.scores.energy,
                            focusScore: fusion.scores.focus,
                            balanceScore: fusion.scores.emotionalBalance,
                            source: "fusion_api"
                        )
                    }
                }
            }
        }
    }

    /// Открыть нативный Tarot Hub (`/tarot` deep link).
    var tarotHubPresentToken: UUID?

    /// Today / card-of-day → three-card deepen ritual (паритет `buildTarotDeepenHref.ts`).
    struct TarotDeepenRequest: Equatable {
        let spreadId: String
        let anchorCardId: Int
        let anchorOrientation: String
        let question: String
        let source: String
    }

    var tarotDeepenRouteToken: UUID?
    private(set) var pendingTarotDeepen: TarotDeepenRequest?

    func requestTarotDeepen(
        anchorCardId: Int,
        anchorOrientation: String = "upright",
        question: String,
        source: String = "today",
        spreadId: String = "three_cards"
    ) {
        pendingTarotDeepen = TarotDeepenRequest(
            spreadId: spreadId,
            anchorCardId: anchorCardId,
            anchorOrientation: anchorOrientation,
            question: question,
            source: source
        )
        tarotDeepenRouteToken = UUID()
    }

    func consumePendingTarotDeepen() -> TarotDeepenRequest? {
        let request = pendingTarotDeepen
        pendingTarotDeepen = nil
        tarotDeepenRouteToken = nil
        return request
    }

    func requestTarotHubPresentation() {
        tarotHubPresentToken = UUID()
    }

    func dismissTarotHubPresentation() {
        tarotHubPresentToken = nil
    }

    /// Prefill для нативного Guidance при переходе с экрана совместимости по профилям (паритет с веб `sessionStorage`).
    struct GuidanceHubCompatPrefill: Equatable {
        let suggestedQuestion: String
        let spreadId: String
        let topicId: String
        let relationshipRoleId: String?
        let outcomeId: String?
    }

    var guidanceHubCompatRouteToken: UUID?
    private(set) var guidanceHubCompatPrefillPayload: GuidanceHubCompatPrefill?

    func stageGuidanceHubCompatPrefill(_ payload: GuidanceHubCompatPrefill) {
        guidanceHubCompatPrefillPayload = payload
        guidanceHubCompatRouteToken = UUID()
    }

    func consumeGuidanceHubCompatPrefill() -> GuidanceHubCompatPrefill? {
        defer {
            guidanceHubCompatPrefillPayload = nil
            guidanceHubCompatRouteToken = nil
        }
        return guidanceHubCompatPrefillPayload
    }

    init() {
        restorePersistedState()
    }

    var isAuthenticated: Bool {
        authSession != nil
    }

    var hasCompletedOnboarding: Bool {
        birthProfile != nil
    }

    func signIn(email: String, password: String) async throws {
        let session = try await TodayFlowAPIClient.shared.signIn(email: email, password: password)
        await MainActor.run {
            applyAuthSession(session, resettingProfile: currentSessionEmail != session.email)
        }
        await restoreBirthProfileFromServerIfNeeded()
    }

    func signUp(email: String, password: String) async throws {
        let session = try await TodayFlowAPIClient.shared.signUp(email: email, password: password)
        await MainActor.run {
            applyAuthSession(session, resettingProfile: true)
        }
    }

    func requestPasswordReset(email: String) async throws -> String {
        try await TodayFlowAPIClient.shared.requestPasswordReset(email: email)
    }

    func resetPassword(token: String, newPassword: String) async throws -> String {
        try await TodayFlowAPIClient.shared.resetPassword(token: token, newPassword: newPassword)
    }

    func changePassword(currentPassword: String, newPassword: String) async throws -> String {
        guard let session = authSession else {
            throw APIError.server("You need to sign in first.")
        }
        return try await TodayFlowAPIClient.shared.changePassword(
            token: session.token,
            currentPassword: currentPassword,
            newPassword: newPassword
        )
    }

    func resumeSessionIfNeeded() async {
        guard let session = authSession else { return }
        guard sessionRefreshState != .refreshing else { return }

        sessionRefreshState = .refreshing
        do {
            let refreshedSession = try await TodayFlowAPIClient.shared.fetchCurrentUser(token: session.token)
            applyAuthSession(refreshedSession, resettingProfile: false)
            await restoreBirthProfileFromServerIfNeeded()
            let now = Date()
            lastSessionValidatedAt = now
            TodayFlowPersistence.shared.saveLastAuthValidatedAt(for: refreshedSession.email, date: now)
            sessionWarningMessage = nil
            sessionRefreshState = .ready
            await syncCoreSetupFromBirthProfileIfNeeded()
            await refreshIfNeeded()
            await bootstrapTrackerIfNeeded()
        } catch {
            // Keep session on transient/network errors; force sign-out only for real auth failures.
            if shouldSignOutAfterSessionRefreshFailure(error) {
                signOut()
                sessionWarningMessage = nil
            }
            if authSession != nil {
                sessionWarningMessage = buildSessionWarningMessage(for: error)
            }
            sessionRefreshState = .idle
        }
    }

    /// Если в приложении уже есть онбординг, а на сервере не создан `AstroProfile`, наталка и аспекты отдают 404.
    func syncCoreSetupFromBirthProfileIfNeeded() async {
        guard let session = authSession, let bp = birthProfile else { return }
        if TodayFlowPersistence.shared.hasCoreSetupSyncMarker(for: session.email) { return }
        guard !isSyncingCoreSetup else { return }
        let draft = lastSubmittedDraft ?? bp.asBirthProfileDraft()
        guard draft.isValid else { return }
        isSyncingCoreSetup = true
        defer { isSyncingCoreSetup = false }
        do {
            try await TodayFlowAPIClient.shared.pushCoreSetupToServer(draft: draft, session: session)
            TodayFlowPersistence.shared.saveCoreSetupSyncMarker(for: session.email)
        } catch {
            // Не рвём сессию: пользователь всё ещё видит локальный профиль.
        }
    }

    func completeOnboarding(with draft: BirthProfileDraft) async {
        loadState = .loading
        lastSubmittedDraft = draft
        TodayFlowPersistence.shared.clearCoreSetupSyncMarker(for: currentSessionEmail)
        TodayFlowPersistence.shared.clearProfileSummarySeen(for: currentSessionEmail)
        hasSeenProfileSummary = false

        do {
            let payload = try await TodayFlowAPIClient.shared.bootstrap(from: draft, session: authSession)
            apply(payload)
            loadState = .loaded
        } catch {
            let profile = draft.resolved
            let payload = TodayFlowBootstrapPayload(
                profile: profile,
                dailyFocus: DailyFocus.personalized(for: profile),
                rituals: Ritual.personalized(for: profile),
                todayCycle: nil,
                fusionIndex: nil,
                fusionHistory: []
            )
            apply(payload)
            loadState = .failed("Сервисы временно недоступны. Показываем локальную версию дня.")
        }
    }

    func refreshIfNeeded() async {
        guard let birthProfile else { return }
        guard loadState != .loading else { return }

        let previousDate = todayCycle?.date

        if todayCycle == nil {
            loadState = .loading
        }

        do {
            let refreshed = try await TodayFlowAPIClient.shared.refreshDayFlow(for: birthProfile, session: authSession)
            dailyFocus = refreshed.dailyFocus
            rituals = refreshed.rituals
            todayCycle = refreshed.todayCycle
            fusionIndex = refreshed.fusionIndex
            fusionHistory = refreshed.fusionHistory
            persistFusionForEnergyMap(fusion: refreshed.fusionIndex)
            TodayDayContinuitySync.backfillFromCycle(refreshed.todayCycle)
            if let dateISO = refreshed.todayCycle?.date {
                TodayDayEngagementSync.backfillFromRitualExtras(email: authSession?.email, dateISO: dateISO)
            }
            if previousDate != refreshed.todayCycle?.date {
                todayGuideNarrative = nil
                todayDayNarrative = nil
                todaySpheresNarrative = nil
                todayEveningNarrative = nil
                lastRitualNarrativeContext = nil
                lastRitualNarrativeContextDate = nil
            }
            loadState = .loaded
            if let token = authSession?.token {
                await meaningRuntime.flush(token: token)
                if let rings = await meaningRuntime.refreshRings(token: token)?.rings {
                    meaningRings = rings
                }
            }
            persistSnapshot()
        } catch {
            if todayCycle == nil {
                loadState = .failed("Главный экран дня загружается дольше обычного. Попробуй обновить ещё раз через пару секунд.")
            } else if loadState == .idle {
                loadState = .failed("Live refresh unavailable. Showing saved flow.")
            }
        }
    }

    func saveMorningIntention(_ intention: String) async throws {
        let cleanValue = intention.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !cleanValue.isEmpty else {
            throw APIError.server("Add a short intention first.")
        }

        let context = try requireTodayContext()
        _ = try await TodayFlowAPIClient.shared.saveMorningIntention(
            token: context.token,
            date: context.date,
            intention: cleanValue
        )
        TodayDayEngagementSync.syncDayGoal(dateISO: context.date, goal: cleanValue)
        TodayDayContinuitySync.saveDraft(dateISO: context.date, mainFocus: cleanValue)
        await refreshIfNeeded()
    }

    func savePulseCheck(state: String?, scale: Int?, note: String?) async throws {
        let cleanState = state?.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanNote = note?.trimmingCharacters(in: .whitespacesAndNewlines)

        guard (cleanState?.isEmpty == false) || scale != nil || (cleanNote?.isEmpty == false) else {
            throw APIError.server("Choose at least one state signal.")
        }

        let context = try requireTodayContext()
        _ = try await TodayFlowAPIClient.shared.savePulseCheck(
            token: context.token,
            payload: PulseCheckPayload(
                date: context.date,
                state: cleanState,
                stateScale: scale,
                note: cleanNote
            )
        )
        await refreshIfNeeded()
    }

    func saveJournalEntry(type: String, content: String) async throws {
        let cleanContent = content.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !cleanContent.isEmpty else {
            throw APIError.server("Journal entry cannot be empty.")
        }

        let context = try requireTodayContext()
        _ = try await TodayFlowAPIClient.shared.saveJournalEntry(
            token: context.token,
            date: context.date,
            type: type,
            content: cleanContent
        )
        await meaningRuntime.track(
            eventType: "diary_entry",
            eventSource: "today",
            localDate: context.date,
            payload: [
                "entry_type": .string(type),
                "source": .string("ios_today_store")
            ]
        )
        await meaningRuntime.flush(token: context.token)
        await refreshIfNeeded()
    }

    /// Compatibility encyclopedia + dynamics learning events (web ↔ iOS parity).
    func trackCompatibilityEvent(
        eventType: String,
        qualityScore: Double = 1.0,
        payload: [String: JSONValue] = [:]
    ) async {
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        await meaningRuntime.track(
            eventType: eventType,
            eventSource: "compatibility",
            localDate: localDate,
            qualityScore: qualityScore,
            payload: payload
        )
        if let token = authSession?.token {
            await meaningRuntime.flush(token: token)
        }
    }

    /// Product events from premium Today surface (micro-question, habits, ring drilldown).
    func trackTodaySurfaceEvent(
        eventType: String,
        eventSource: String = "today_surface",
        qualityScore: Double = 1.0,
        generationLogId: Int? = nil,
        payload: [String: JSONValue] = [:]
    ) async {
        guard let token = authSession?.token else { return }
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        var merged = payload
        if let gid = generationLogId, gid > 0 {
            merged["generation_id"] = .number(Double(gid))
        }
        await meaningRuntime.track(
            eventType: eventType,
            eventSource: eventSource,
            localDate: localDate,
            qualityScore: qualityScore,
            payload: merged
        )
        await meaningRuntime.flush(token: token)
    }

    /// PIM meaning events with stable idempotency (profile_atom_correction, sphere_feedback confirm).
    func trackMeaningEventWithIdempotency(
        eventType: String,
        eventSource: String,
        idempotencyKey: String,
        qualityScore: Double = 0.88,
        payload: [String: JSONValue] = [:]
    ) async {
        guard let token = authSession?.token else { return }
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        await meaningRuntime.track(
            eventType: eventType,
            eventSource: eventSource,
            localDate: localDate,
            qualityScore: qualityScore,
            payload: payload,
            idempotencyKey: idempotencyKey
        )
        await meaningRuntime.flush(token: token)
    }

    /// Tarot question-first funnel events (web ↔ iOS parity).
    func trackTarotFlowEvent(
        eventType: String,
        idempotencyKey: String,
        payload: [String: JSONValue] = [:]
    ) async {
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        await meaningRuntime.track(
            eventType: eventType,
            eventSource: "flow",
            localDate: localDate,
            payload: payload,
            idempotencyKey: idempotencyKey
        )
        if let token = authSession?.token {
            await meaningRuntime.flush(token: token)
        }
    }

    func saveEveningReflection(
        reflection: String,
        noticed: String,
        hardest: String,
        easierThanExpected: String,
        markComplete: Bool
    ) async throws {
        let cleanReflection = reflection.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanNoticed = noticed.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanHardest = hardest.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanEasier = easierThanExpected.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !cleanReflection.isEmpty || !cleanNoticed.isEmpty || !cleanHardest.isEmpty || !cleanEasier.isEmpty else {
            throw APIError.server("Add at least one evening note.")
        }

        let context = try requireTodayContext()
        let eveningGenId = todayEveningNarrative?.generationID
        _ = try await TodayFlowAPIClient.shared.saveEveningReflection(
            token: context.token,
            date: context.date,
            reflection: cleanReflection.isEmpty ? nil : cleanReflection,
            observations: TodayEveningObservationsInput(
                noticed: cleanNoticed,
                hardest: cleanHardest,
                easierThanExpected: cleanEasier
            ),
            markComplete: markComplete
        )
        await trackTodaySurfaceEvent(
            eventType: "evening_reflection_submitted",
            eventSource: "today",
            qualityScore: markComplete ? 0.9 : 0.75,
            generationLogId: eveningGenId,
            payload: [
                "evening_completed": .bool(markComplete),
                "has_reflection": .bool(!cleanReflection.isEmpty),
                "day_key": .string(context.date),
            ]
        )
        await refreshIfNeeded()

        if let gid = eveningGenId {
            let noteForBody: String? = cleanReflection.isEmpty ? nil : String(cleanReflection.prefix(4000))
            let meta = LearningFeedbackMetadataPayload(
                profile_selector: todayEveningNarrative?.profileSelector,
                day_key: context.date,
                surface: "evening",
                evening_completed: markComplete
            )
            try? await submitLearningFeedback(
                generationLogId: gid,
                signal: markComplete ? "today_evening_closure_done" : "today_evening_closure_saved",
                note: noteForBody,
                metadata: meta
            )
        }

        TodayDayContinuitySync.recordEveningSave(
            dateISO: context.date,
            cycle: todayCycle,
            markComplete: markComplete,
            reflection: cleanReflection,
            noticed: cleanNoticed,
            hardest: cleanHardest,
            easierThanExpected: cleanEasier
        )
    }

    // MARK: - Tracker API

    func bootstrapTrackerIfNeeded() async {
        guard !didBootstrap else { return }
        await refreshAll()
    }

    func refreshAll() async {
        guard !isBootstrapping else { return }
        isBootstrapping = true
        lastError = nil

        async let todayError = captureBootstrapError { try await refreshTodayInternal() }
        async let calendarError = captureBootstrapError { try await refreshCalendarInternal() }
        async let goalsError = captureBootstrapError { try await refreshGoalsInternal() }

        let todayIssue = await todayError
        let calendarIssue = await calendarError
        let goalsIssue = await goalsError
        let errors = [todayIssue, calendarIssue, goalsIssue].compactMap { $0 }
        if errors.count < 3 {
            didBootstrap = true
        }
        if !errors.isEmpty {
            lastError = Self.joinedErrorMessage(errors)
        }

        isBootstrapping = false
    }

    func resetTrackerForLogout() {
        didBootstrap = false
        today = TodayDashboard.placeholder
        calendar = CalendarSnapshot.empty
        goals = []
        lastError = nil
        affirmationsCatalog = []
        affirmationDoneById = [:]
        diaryEntries = []
        selectedDiaryEntry = nil
        autoInsights = []
    }

    func refreshToday() async {
        do {
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func refreshCalendar() async {
        do {
            try await refreshCalendarInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func refreshGoals() async {
        do {
            try await refreshGoalsInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func refreshProgressSurfaces() async {
        async let diaryTask = refreshDiaryInternal()
        async let insightsTask = refreshInsightsInternal()

        do {
            _ = try await (diaryTask, insightsTask)
        } catch {
            lastError = readableError(error)
        }
    }

    func saveTrackerMorningIntention(_ text: String) async {
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        await saveDayConnection([
            "morning_intention": text,
            "morning_completed": true
        ])
    }

    func saveTrackerRitualFeedback(_ value: String) async {
        guard await saveDayConnection(["ritual_feedback": value]) else { return }
        await postTodayGuideLearningSignals(ritualFeedback: value)
    }

    func saveTrackerQuickDecision(_ value: String) async {
        guard await saveDayConnection(["quick_decision_answer": value]) else { return }
        await postTodayGuideLearningSignals(quickDecisionAnswer: value)
    }

    func saveTrackerQuestionAnswer(_ value: String) async {
        guard await saveDayConnection(["question_of_day_answer": value]) else { return }
        await postTodayGuideLearningSignals(questionOfDayAnswer: value)
    }

    func toggleTrackerExecutionAction(_ title: String, completed: Bool) async {
        let key = Self.actionTrackingKey(from: title)
        var items = today.completedExecutionActions
        if completed {
            if !items.contains(key) {
                items.append(key)
            }
        } else {
            items.removeAll { $0 == key }
        }
        await saveDayConnection(["execution_actions_done": items])
    }

    func toggleTrackerAvoidAction(_ title: String, respected: Bool) async {
        let key = Self.actionTrackingKey(from: title)
        var items = today.respectedAvoidActions
        if respected {
            if !items.contains(key) {
                items.append(key)
            }
        } else {
            items.removeAll { $0 == key }
        }
        await saveDayConnection(["avoid_actions_respected": items])
    }

    /// Паритет с подсчётом в `today/page.tsx` для `EntityCreateWizard` (`goalCountWeek` / `goalCountMonth`).
    var goalSlotCounts: (week: Int, month: Int) {
        let week = goals.filter { $0.scope != .month }.count
        let month = goals.filter { $0.scope == .month }.count
        return (week, month)
    }

    func canCreateGoal(scope: GoalScope) -> Bool {
        let c = goalSlotCounts
        switch scope {
        case .week: return c.week < 3
        case .month: return c.month < 3
        }
    }

    @discardableResult
    func createGoal(title: String, scope: GoalScope, anchorDateISO: String? = nil) async -> Bool {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return false }
        let refISO = (anchorDateISO?.trimmingCharacters(in: .whitespacesAndNewlines)).flatMap { $0.isEmpty ? nil : $0 } ?? selectedCalendarDateISO
        guard canCreateGoal(scope: scope) else {
            lastError = "Уже 3 цели на этот период — заверши или смени период."
            return false
        }
        isSaving = true
        defer { isSaving = false }

        let weekStart: String = {
            switch scope {
            case .week: return Self.weekStartMonday(fromLocalISO: refISO)
            case .month: return Self.monthAnchorIso(refISO)
            }
        }()

        do {
            let payload: [String: Any] = [
                "title": trimmed,
                "scope": scope.rawValue,
                "week_start": weekStart,
            ]
            _ = try await trackingHTTP.sendDictionary(path: "/tracking/weekly-goals", method: "POST", body: payload)
            try await refreshGoalsInternal()
            try await refreshCalendarInternal()
            return true
        } catch {
            lastError = readableError(error)
            return false
        }
    }

    func markGoalStep(goal: GoalTrack, dateISO: String) async {
        let trimmedDate = dateISO.trimmingCharacters(in: .whitespacesAndNewlines)
        guard goal.allowsStep(on: trimmedDate) else {
            if goal.scope == .week {
                let window = goal.weekSliceDayISOs().joined(separator: ", ")
                lastError = "Шаг по weekly goal можно отметить только в пределах недели цели: \(window)."
            } else {
                lastError = "Не удалось определить дату шага для цели."
            }
            return
        }

        isSaving = true
        defer { isSaving = false }

        do {
            try await postGoalStep(goalID: goal.id, dateISO: trimmedDate)
            try await refreshGoalsInternal()
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    private func postGoalStep(goalID: Int, dateISO: String) async throws {
        let payloads: [[String: Any]] = [
            ["date": dateISO],
            ["step_date": dateISO]
        ]
        var lastFailure: Error?

        for payload in payloads {
            do {
                _ = try await trackingHTTP.sendDictionary(
                    path: "/tracking/weekly-goals/\(goalID)/step",
                    method: "POST",
                    body: payload
                )
                return
            } catch {
                if case StoreError.http(400, _) = error {
                    lastFailure = error
                    continue
                }
                throw error
            }
        }

        throw lastFailure ?? StoreError.invalidResponse
    }

    func setGoalCompleted(goalID: Int, completed: Bool) async {
        isSaving = true
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/weekly-goals/\(goalID)",
                method: "PUT",
                body: ["completed": completed]
            )
            try await refreshGoalsInternal()
            try await refreshCalendarInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func createHabit(
        name: String,
        category: String? = nil,
        targetFrequency: String = "daily",
        targetPerPeriod: Int = 1
    ) async {
        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let freq = targetFrequency.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard freq == "daily" || freq == "weekly" else { return }
        let per = min(14, max(1, targetPerPeriod))
        isSaving = true
        defer { isSaving = false }

        do {
            var body: [String: Any] = [
                "name": trimmed,
                "target_frequency": freq,
                "target_per_period": freq == "daily" ? 1 : per,
            ]
            if let cat = category?.trimmingCharacters(in: .whitespacesAndNewlines), !cat.isEmpty {
                body["category"] = cat
            }
            _ = try await trackingHTTP.sendDictionary(
                path: "/habits",
                method: "POST",
                body: body
            )
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func fetchHabitMapRows(todayISO: String) async throws -> [HabitMapRowModel] {
        let habitsRaw = try await trackingHTTP.getArray(path: "/habits")
        let overviewRaw = try await trackingHTTP.getArray(
            path: "/habits/overview/summary",
            query: [URLQueryItem(name: "period_days", value: "30")]
        )
        let habits = try decodeJSONArray(habitsRaw, as: [HabitMapHabitAPI].self)
        let overview = try decodeJSONArray(overviewRaw, as: [HabitMapOverviewAPI].self)
        let fromDate = mapWindow(todayISO: todayISO, days: 35).first ?? todayISO

        var rows: [HabitMapRowModel] = []
        for habit in habits {
            let entriesRaw = try await trackingHTTP.getArray(
                path: "/habits/\(habit.id)/entries",
                query: [
                    URLQueryItem(name: "from_date", value: fromDate),
                    URLQueryItem(name: "to_date", value: todayISO),
                ]
            )
            let entries = try decodeJSONArray(entriesRaw, as: [HabitMapEntryAPI].self)
            let completedDates = Set(entries.filter(\.completed).map(\.date))
            let streak = overview.first(where: { $0.habitId == habit.id })?.currentStreakDays ?? 0
            let weave = habitWeaveColor(habitId: habit.id, category: habit.category)
            let cells = mapWindow(todayISO: todayISO).map { dateISO -> MapHeatmapCellModel in
                let done = completedDates.contains(dateISO)
                return MapHeatmapCellModel(
                    dateISO: dateISO,
                    color: done ? weave : Color(red: 248 / 255, green: 245 / 255, blue: 239 / 255),
                    hasMark: done,
                    isFuture: dateISO > todayISO,
                    title: dateISO
                )
            }
            rows.append(HabitMapRowModel(id: habit.id, name: habit.name, streakDays: streak, cells: cells))
        }
        return rows
    }

    func fetchCycleMapEntries(todayISO: String, windowDays: Int = 120) async throws -> [CycleMapEntryIn] {
        guard isAuthenticated else { return [] }
        let fromDate = mapWindow(todayISO: todayISO, days: windowDays).first ?? todayISO
        let raw = try await trackingHTTP.getArray(
            path: "/calendar/cycle",
            query: [
                URLQueryItem(name: "from_date", value: fromDate),
                URLQueryItem(name: "to_date", value: todayISO),
            ]
        )
        let entries = try decodeJSONArray(raw, as: [CycleMapEntryAPI].self)
        return entries.map(\.model)
    }

    func fetchAsceticMapRows(todayISO: String) async throws -> [AsceticMapRowModel] {
        let contractsRaw = try await trackingHTTP.getArray(path: "/tracking/ascetic-contracts")
        let contracts = try decodeJSONArray(contractsRaw, as: [AsceticContractMapAPI].self)
        let fromDate = mapWindow(todayISO: todayISO).first ?? todayISO
        _ = try await trackingHTTP.getDictionary(
            path: "/tracking/calendar",
            query: [
                URLQueryItem(name: "from_date", value: fromDate),
                URLQueryItem(name: "to_date", value: todayISO),
            ]
        )
        try await refreshCalendarInternal()

        let active = contracts.filter { $0.status.lowercased() == "active" }
        let pool = active.isEmpty ? contracts : active

        return pool.map { contract in
            let track = calendar.asceticTracks.first {
                $0.displayTitle == contract.title || $0.displayTitle.contains(String(contract.title.prefix(12)))
            }
            let completedDates = Set((track?.entries ?? []).filter(\.completed).map(\.dateISO))
            let cells = mapWindow(todayISO: todayISO).map { dateISO in
                let done = completedDates.contains(dateISO)
                return MapHeatmapCellModel(
                    dateISO: dateISO,
                    color: asceticMapCellColor(completed: done, isFuture: dateISO > todayISO),
                    hasMark: done,
                    isFuture: dateISO > todayISO,
                    title: dateISO
                )
            }
            return AsceticMapRowModel(id: contract.id, title: contract.title, streakDays: contract.streakDays, cells: cells)
        }
    }

    private func persistFusionForEnergyMap(fusion: FusionIndex?) {
        guard let fusion else { return }
        EnergyMapStore.save(
            dateISO: fusion.date,
            energyScore: fusion.scores.energy,
            focusScore: fusion.scores.focus,
            balanceScore: fusion.scores.emotionalBalance,
            source: "today_fusion"
        )
    }

    private func decodeJSONArray<T: Decodable>(_ raw: [[String: Any]], as type: T.Type) throws -> T {
        let data = try JSONSerialization.data(withJSONObject: raw)
        return try JSONDecoder().decode(T.self, from: data)
    }

    func logPractice(dateISO: String) async {
        if let day = calendar.days.first(where: { $0.dateISO == dateISO }),
           day.activities.contains(where: { $0.id == "practice" && $0.isComplete }) {
            lastError = "Практика уже отмечена. Снять отметку можно в разделе практик на сайте."
            return
        }

        isSaving = true
        lastError = nil
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/calendar/log",
                method: "POST",
                body: [
                    "date": dateISO,
                    "activity_type": "practice",
                    "completed": true
                ]
            )
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func toggleAscetic(asceticismId: String, dateISO: String, completed: Bool) async {
        isSaving = true
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/calendar/log",
                method: "POST",
                body: [
                    "date": dateISO,
                    "activity_type": "asceticism",
                    "activity_id": asceticismId,
                    "completed": completed
                ]
            )
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    /// `POST /tracking/ascetic-contracts` — как шаг создания в веб-мастере сущностей.
    @discardableResult
    func createAsceticContract(
        asceticismId: String,
        title: String,
        intention: String?,
        startDateISO: String,
        fixedDurationDays: Int?
    ) async -> Bool {
        let trimmedTitle = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedTitle.isEmpty else { return false }
        isSaving = true
        defer { isSaving = false }

        var body: [String: Any] = [
            "title": trimmedTitle,
            "asceticism_id": asceticismId,
            "start_date": startDateISO,
        ]
        if let intention = intention?.trimmingCharacters(in: .whitespacesAndNewlines), !intention.isEmpty {
            body["intention"] = String(intention.prefix(500))
        }
        if let days = fixedDurationDays, days > 0,
           let start = Self.date(from: startDateISO),
           let end = Calendar.current.date(byAdding: .day, value: days - 1, to: start)
        {
            body["end_date"] = Self.isoDate(from: end)
        }

        do {
            _ = try await trackingHTTP.sendDictionary(path: "/tracking/ascetic-contracts", method: "POST", body: body)
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
            return true
        } catch {
            lastError = readableError(error)
            return false
        }
    }

    func requestTrackerQuickCreate(_ kind: TrackerQuickCreateKind) {
        pendingTrackerQuickCreate = kind
    }

    func toggleHabit(habitID: Int, dateISO: String, completed: Bool) async {
        isSaving = true
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/habits/\(habitID)/entries",
                method: "POST",
                body: [
                    "date": dateISO,
                    "completed": completed
                ]
            )
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func selectCalendarDate(_ dateISO: String) {
        selectedCalendarDateISO = dateISO
    }

    func prepareAffirmationsForCalendar() async {
        await loadAffirmationsCatalogIfNeeded()
        await refreshAffirmationProgressForSelectedDay()
    }

    func loadAffirmationsCatalogIfNeeded() async {
        guard affirmationsCatalog.isEmpty else { return }
        do {
            let raw = try await trackingHTTP.getArray(path: "/practices/affirmations")
            affirmationsCatalog = raw.compactMap { Self.parseAffirmationCatalogItem(Self.dictionary($0)) }
        } catch {
            affirmationsCatalog = []
        }
    }

    func refreshAffirmationProgressForSelectedDay() async {
        let d = selectedCalendarDateISO
        do {
            let raw = try await trackingHTTP.getArray(
                path: "/tracking/progress",
                query: [
                    URLQueryItem(name: "from_date", value: d),
                    URLQueryItem(name: "to_date", value: d)
                ]
            )
            var map: [String: Bool] = [:]
            for item in raw {
                let dict = Self.dictionary(item)
                guard let aid = Self.string(dict["affirmation_id"]), !aid.isEmpty else { continue }
                let done = Self.bool(dict["completed"])
                map[aid] = (map[aid] == true) || done
            }
            affirmationDoneById = map
        } catch {
            affirmationDoneById = [:]
        }
    }

    func toggleAffirmation(affirmationId: String, dateISO: String, completed: Bool) async {
        isSaving = true
        lastError = nil
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/calendar/log",
                method: "POST",
                body: [
                    "date": dateISO,
                    "activity_type": "affirmation",
                    "activity_id": affirmationId,
                    "completed": completed
                ]
            )
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
            await refreshAffirmationProgressForSelectedDay()
        } catch {
            lastError = readableError(error)
        }
    }

    func saveObservationDiary(noticed: String, hardest: String, easierThanExpected: String) async {
        let cleanNoticed = noticed.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanHardest = hardest.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanEasier = easierThanExpected.trimmingCharacters(in: .whitespacesAndNewlines)

        guard !cleanNoticed.isEmpty || !cleanHardest.isEmpty || !cleanEasier.isEmpty else {
            lastError = "Заполни хотя бы одно поле дневника."
            return
        }

        isSaving = true
        lastError = nil
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/diary",
                method: "POST",
                body: [
                    "date": selectedCalendarDateISO,
                    "noticed": cleanNoticed,
                    "hardest": cleanHardest,
                    "easier_than_expected": cleanEasier
                ]
            )
            try await refreshDiaryInternal()
            try await refreshCalendarInternal()
            try await refreshTodayInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func generateInsightForSelectedDay() async {
        isGeneratingInsight = true
        lastError = nil
        defer { isGeneratingInsight = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/tracking/insights/generate",
                method: "POST",
                body: ["date": selectedCalendarDateISO]
            )
            try await refreshInsightsInternal()
        } catch {
            lastError = readableError(error)
        }
    }

    func shiftCalendarMonth(by months: Int) async {
        guard let base = Self.date(from: selectedCalendarDateISO) else { return }
        let cal = Calendar.current
        guard let shifted = cal.date(byAdding: .month, value: months, to: cal.startOfDay(for: base)) else { return }
        let comps = cal.dateComponents([.year, .month], from: shifted)
        guard let startOfMonth = cal.date(from: comps) else { return }
        selectedCalendarDateISO = Self.isoDate(from: startOfMonth)
        await refreshCalendar()
    }

    /// Паритет с веб `today/page.tsx` saveTodaySignal: после успешного `POST /day-connection/...` — сигналы `POST /learning/feedback` с тем же `metadata`, что на сайте.
    private func postTodayGuideLearningSignals(
        ritualFeedback: String? = nil,
        quickDecisionAnswer: String? = nil,
        questionOfDayAnswer: String? = nil
    ) async {
        guard let gid = todayGuideNarrative?.generationID, gid > 0 else { return }
        guard let token = authSession?.token, !token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        let dayKey = today.dateISO
        let ps = todayGuideNarrative?.profileSelector

        if let rf = ritualFeedback {
            let meta = LearningFeedbackMetadataPayload(
                profile_selector: ps,
                day_key: dayKey,
                surface: "guide"
            )
            try? await TodayFlowAPIClient.shared.submitLearningFeedback(
                token: token,
                body: LearningFeedbackRequestBody(
                    generation_log_id: gid,
                    signal: "today_guide_ritual_\(rf)",
                    metadata: meta
                )
            )
        }
        if let qd = quickDecisionAnswer {
            let meta = LearningFeedbackMetadataPayload(
                profile_selector: ps,
                day_key: dayKey
            )
            try? await TodayFlowAPIClient.shared.submitLearningFeedback(
                token: token,
                body: LearningFeedbackRequestBody(
                    generation_log_id: gid,
                    signal: "today_guide_quick_decision_\(qd)",
                    metadata: meta
                )
            )
        }
        if let qa = questionOfDayAnswer {
            let trimmed = qa.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !trimmed.isEmpty else { return }
            let meta = LearningFeedbackMetadataPayload(
                profile_selector: ps,
                day_key: dayKey
            )
            try? await TodayFlowAPIClient.shared.submitLearningFeedback(
                token: token,
                body: LearningFeedbackRequestBody(
                    generation_log_id: gid,
                    signal: "today_guide_question_answered",
                    note: String(trimmed.prefix(4000)),
                    metadata: meta
                )
            )
        }
    }

    @discardableResult
    private func saveDayConnection(_ body: [String: Any]) async -> Bool {
        isSaving = true
        defer { isSaving = false }

        do {
            _ = try await trackingHTTP.sendDictionary(
                path: "/day-connection/\(today.dateISO)",
                method: "POST",
                body: body
            )
            try await refreshTodayInternal()
            try await refreshCalendarInternal()
            return true
        } catch {
            lastError = readableError(error)
            return false
        }
    }

    private func refreshTodayInternal() async throws {
        isRefreshingToday = true
        defer { isRefreshingToday = false }

        async let openingTask = trackingHTTP.getDictionary(path: "/today/opening", query: [URLQueryItem(name: "target_date", value: selectedCalendarDateISO)])
        async let bundleTask = trackingHTTP.getDictionary(path: "/today/bundle", query: [URLQueryItem(name: "target_date", value: selectedCalendarDateISO)])
        async let stateTask = trackingHTTP.getDictionary(path: "/today/state-map", query: [URLQueryItem(name: "target_date", value: selectedCalendarDateISO)])
        async let promptTask = trackingHTTP.getDictionary(path: "/today/checkin-prompt", query: [URLQueryItem(name: "target_date", value: selectedCalendarDateISO)])
        let contractToken = authSession?.token
        let contractTargetDate = dateFromISO(selectedCalendarDateISO) ?? Date()
        async let contractTask: TodayContractV1? = {
            guard let token = contractToken else { return nil }
            return try? await TodayFlowAPIClient.shared.fetchTodayContract(
                token: token,
                targetDate: contractTargetDate
            )
        }()

        let opening = try await openingTask
        let bundle = try await bundleTask
        let state = try await stateTask
        let prompt = try await promptTask
        todayContract = await contractTask

        today = Self.buildTodayDashboard(
            opening: opening,
            bundle: bundle,
            state: state,
            prompt: prompt,
            fallbackDateISO: selectedCalendarDateISO,
            streakCount: calendar.streaks["state_phases"] ?? calendar.streaks["goal"] ?? 0,
            recentFusionHistory: fusionHistory,
            recentCalendar: calendar
        )
    }

    private func refreshCalendarInternal() async throws {
        isRefreshingCalendar = true
        defer { isRefreshingCalendar = false }

        let interval = Self.monthInterval(containing: selectedCalendarDateISO)
        let payload = try await trackingHTTP.getDictionary(
            path: "/tracking/calendar",
            query: [
                URLQueryItem(name: "from_date", value: interval.from),
                URLQueryItem(name: "to_date", value: interval.to)
            ]
        )

        calendar = Self.buildCalendarSnapshot(
            from: payload,
            displayedMonthDateISO: selectedCalendarDateISO
        )
        goals = calendar.goalTracks
        if !calendar.days.contains(where: { $0.dateISO == selectedCalendarDateISO }) {
            selectedCalendarDateISO = Self.isoDate(from: Date())
        }
    }

    private func refreshGoalsInternal() async throws {
        isRefreshingGoals = true
        defer { isRefreshingGoals = false }

        let weekly = try await trackingHTTP.getArray(path: "/tracking/weekly-goals")
        goals = weekly.compactMap(Self.parseGoalTrack)
        if !calendar.days.isEmpty {
            calendar.goalTracks = goals
        }
    }

    private func refreshDiaryInternal() async throws {
        isRefreshingDiary = true
        defer { isRefreshingDiary = false }

        let raw = try await trackingHTTP.getArray(
            path: "/tracking/diary",
            query: [URLQueryItem(name: "date", value: selectedCalendarDateISO)]
        )
        let entries = raw.compactMap(Self.parseObservationDiaryEntry)
        diaryEntries = entries
        selectedDiaryEntry = entries.first
    }

    private func refreshInsightsInternal() async throws {
        isRefreshingInsights = true
        defer { isRefreshingInsights = false }

        let raw = try await trackingHTTP.getArray(
            path: "/tracking/insights",
            query: [URLQueryItem(name: "date", value: selectedCalendarDateISO)]
        )
        autoInsights = raw.compactMap(Self.parseAutoInsightItem)
    }

    private func trackingBearer() -> String {
        let s = authSession?.token.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !s.isEmpty { return s }
        return AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Тот же приоритет, что у трекера: сессия в памяти, иначе токен из UserDefaults (после восстановления).
    private func effectiveBearerToken() -> String? {
        let s = authSession?.token.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !s.isEmpty { return s }
        let u = AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
        return u.isEmpty ? nil : u
    }

    private var trackingHTTP: TrackingAPIClient {
        TrackingAPIClient(bearer: trackingBearer())
    }

    func signOut() {
        AppConfig.clearAuthToken()
        resetTrackerForLogout()
        authSession = nil
        birthProfile = nil
        todayCycle = nil
        fusionIndex = nil
        fusionHistory = []
        accountSettings = nil
        coreProfile = nil
        profileSummary = nil
        profileBuildStatus = nil
        meaningRings = []
        natalChart = nil
        todayGuideNarrative = nil
        todayDayNarrative = nil
        todaySpheresNarrative = nil
        todayEveningNarrative = nil
        lastRitualNarrativeContext = nil
        lastRitualNarrativeContextDate = nil
        dailyFocus = .placeholder
        rituals = Ritual.placeholder
        user = .placeholder
        loadState = .idle
        hasSeenProfileSummary = false
        sessionRefreshState = .idle
        sessionWarningMessage = nil
        lastSessionValidatedAt = nil
        lastSnapshotSavedAt = nil
        lastSubmittedDraft = nil
        TodayFlowPersistence.shared.clear()
    }

    func loadAstroProfiles() async throws -> [StoredAstroProfile] {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        do {
            let profiles = try await TodayFlowAPIClient.shared.listAstroProfiles(token: token)
            if profiles.isEmpty, shouldAttemptCoreSetupRecovery() {
                await syncCoreSetupFromBirthProfileIfNeeded()
                return try await TodayFlowAPIClient.shared.listAstroProfiles(token: token)
            }
            return profiles
        } catch {
            if shouldAttemptCoreSetupRecovery(after: error) {
                await syncCoreSetupFromBirthProfileIfNeeded()
                return try await TodayFlowAPIClient.shared.listAstroProfiles(token: token)
            }
            throw error
        }
    }

    func answerQuestion(_ question: String, preferredLane: String?) async throws -> QuestionAnswerResult {
        let response = try await TodayFlowAPIClient.shared.answerQuestion(
            token: authSession?.token,
            question: question,
            preferredLane: preferredLane
        )
        if let token = authSession?.token {
            let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
            await meaningRuntime.track(
                eventType: "guidance_ask",
                eventSource: "insight",
                localDate: localDate,
                payload: [
                    "lane": .string(response.lane),
                    "question": .string(question)
                ]
            )
            await meaningRuntime.flush(token: token)
        }
        return response
    }

    /// Короткий контекст дня для `today_context_summary` в `POST /questions/reading` (паритет с вебом).
    func guidanceTodayContextSummaryForAPI(maxLength: Int = 400) -> String? {
        let d = today
        let h = d.headline.trimmingCharacters(in: .whitespacesAndNewlines)
        let g = d.guidanceSummary.trimmingCharacters(in: .whitespacesAndNewlines)
        var parts: [String] = []
        if !h.isEmpty { parts.append(h) }
        if !g.isEmpty, g != h { parts.append(g) }
        let joined = parts.joined(separator: " · ").trimmingCharacters(in: .whitespacesAndNewlines)
        if joined.isEmpty { return nil }
        if joined.count <= maxLength { return joined }
        let end = joined.index(joined.startIndex, offsetBy: maxLength - 1)
        return String(joined[..<end]) + "…"
    }

    func submitGuidanceReading(
        question: String,
        spreadId: String,
        selectedCards: [GuidanceSelectedCardBody],
        hubLaneHint: String?,
        topic: String?,
        desiredOutcome: String?,
        relationshipContext: String?,
        intimacyFocus: String?,
        userIntent: String? = nil,
        requestedDepth: String? = "normal",
        todayContextSummary: String? = nil
    ) async throws -> GuidanceReadingResult {
        guard let token = authSession?.token, !token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw StoreError.http(401, "Войди в аккаунт, чтобы получить расклад Guidance.")
        }
        let body = GuidanceReadingAPIRequestBody(
            question: question,
            spread_id: spreadId,
            selected_cards: selectedCards,
            hub_lane_hint: hubLaneHint,
            topic: topic,
            desired_outcome: desiredOutcome,
            relationship_context: relationshipContext,
            intimacy_focus: intimacyFocus,
            user_intent: userIntent,
            requested_depth: requestedDepth,
            today_context_summary: todayContextSummary
        )
        let response = try await TodayFlowAPIClient.shared.guidanceReading(token: token, payload: body)
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        await meaningRuntime.track(
            eventType: "guidance_ask",
            eventSource: "insight",
            localDate: localDate,
            payload: [
                "lane": .string(response.lane),
                "question": .string(question),
                "spread_id": .string(spreadId),
                "cards": .array(response.tarotCards.map { .string($0.name) })
            ]
        )
        await meaningRuntime.flush(token: token)
        return response
    }

    func submitGuidanceClarify(
        parentGenerationLogId: Int,
        clarificationGoal: String,
        selectedCards: [GuidanceSelectedCardBody]
    ) async throws -> GuidanceReadingResult {
        guard let token = authSession?.token, !token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw StoreError.http(401, "Войди в аккаунт, чтобы получить уточняющую карту.")
        }
        let body = GuidanceClarifyAPIRequestBody(
            parent_generation_log_id: parentGenerationLogId,
            clarification_goal: clarificationGoal,
            selected_cards: selectedCards
        )
        let response = try await TodayFlowAPIClient.shared.guidanceReadingClarify(token: token, payload: body)
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        await meaningRuntime.track(
            eventType: "guidance_clarify",
            eventSource: "insight",
            localDate: localDate,
            payload: [
                "parent_log_id": .number(Double(parentGenerationLogId)),
                "clarification_goal": .string(clarificationGoal),
                "lane": .string(response.lane),
                "cards": .array(response.tarotCards.map { .string($0.name) }),
            ]
        )
        await meaningRuntime.flush(token: token)
        return response
    }

    func loadGuidanceHistoryBundle(limit: Int = 60) async throws -> GuidanceHistoryBundle {
        guard let token = authSession?.token, !token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw StoreError.http(401, "Войди в аккаунт, чтобы видеть историю.")
        }
        async let questionsTask = TodayFlowAPIClient.shared.fetchQuestionsHistory(token: token, limit: limit)
        async let tarotHistoryTask = TarotClient.fetchTarotHistory()
        async let spreadHistoryTask = TarotClient.fetchSpreadHistory()
        let questions = try await questionsTask
        let tarotHistory = try await tarotHistoryTask
        let spreads = try await spreadHistoryTask
        return GuidanceHistoryBundle(
            questions: questions.history,
            tarotDaily: tarotHistory.history,
            spreads: spreads
        )
    }

    func submitLearningFeedback(
        generationLogId: Int,
        signal: String,
        note: String? = nil,
        metadata: LearningFeedbackMetadataPayload?
    ) async throws {
        guard let token = authSession?.token, !token.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw StoreError.http(401, "Войди в аккаунт.")
        }
        let body = LearningFeedbackRequestBody(generation_log_id: generationLogId, signal: signal, note: note, metadata: metadata)
        try await TodayFlowAPIClient.shared.submitLearningFeedback(token: token, body: body)
    }

    func createAstroProfile(_ input: AstroProfileInput) async throws -> StoredAstroProfile {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let response = try await TodayFlowAPIClient.shared.createAstroProfile(token: token, input: input)
        if let core = response.coreProfile {
            coreProfile = core
        }
        return response.storedSnapshot
    }

    func updateAstroProfile(profileID: Int, payload: AstroProfileUpdatePayload) async throws -> StoredAstroProfile {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let response = try await TodayFlowAPIClient.shared.updateAstroProfile(
            token: token,
            profileID: profileID,
            payload: payload
        )
        if let core = response.coreProfile {
            coreProfile = core
        }
        return response.storedSnapshot
    }

    func deleteAstroProfile(profileID: Int) async throws {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        try await TodayFlowAPIClient.shared.deleteAstroProfile(token: token, profileID: profileID)
    }

    func setPrimaryAstroProfile(profileID: Int) async throws {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let response = try await TodayFlowAPIClient.shared.setPrimaryAstroProfile(token: token, profileID: profileID)
        if let core = response.coreProfile {
            coreProfile = core
        }
    }

    func compareCompatibility(
        profileID1: Int,
        profileID2: Int,
        relationMode: String,
        type: CompatibilityRequestType,
        formatID: String? = nil
    ) async throws -> CompatibilityComparisonResponse {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let response = try await TodayFlowAPIClient.shared.compareCompatibility(
            token: token,
            profileID1: profileID1,
            profileID2: profileID2,
            relationMode: relationMode,
            type: type,
            formatID: formatID
        )
        let localDate = todayCycle?.date ?? Self.isoDate(from: Date())
        var payload: [String: JSONValue] = [
            "relation_mode": .string(relationMode),
            "request_type": .string(type == .deep ? "deep" : "quick"),
            "profile_1_id": .number(Double(profileID1)),
            "profile_2_id": .number(Double(profileID2)),
            "overall_score": .number(Double(response.scenarioContext?.displayScore ?? response.compatibility.overallScore)),
        ]
        if let formatID {
            payload["format_id"] = .string(formatID)
        }
        await meaningRuntime.track(
            eventType: "compatibility_view",
            eventSource: "compatibility",
            localDate: localDate,
            payload: payload
        )
        await meaningRuntime.flush(token: token)
        return response
    }

    func loadAccountSettings(force: Bool = false) async throws -> AccountSettings {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        if let accountSettings, !force {
            return accountSettings
        }
        let settings = try await TodayFlowAPIClient.shared.fetchAccountSettings(token: token)
        await MainActor.run {
            accountSettings = settings
        }
        return settings
    }

    func loadCoreProfile(force: Bool = false, astroProfileID: Int? = nil) async throws -> CoreProfileResponse {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        if let coreProfile, !force, astroProfileID == nil {
            return coreProfile
        }
        let profile: CoreProfileResponse
        do {
            profile = try await TodayFlowAPIClient.shared.fetchCoreProfile(token: token, astroProfileID: astroProfileID)
        } catch {
            guard astroProfileID == nil, shouldAttemptCoreSetupRecovery(after: error) else {
                throw error
            }
            await syncCoreSetupFromBirthProfileIfNeeded()
            profile = try await TodayFlowAPIClient.shared.fetchCoreProfile(token: token, astroProfileID: astroProfileID)
        }
        if astroProfileID == nil {
            await MainActor.run {
                coreProfile = profile
            }
        }
        return profile
    }

    func loadProfileSummary(force: Bool = false) async throws -> ProfileSummaryResponse {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        if let profileSummary, !force {
            return profileSummary
        }
        let summary = try await TodayFlowAPIClient.shared.fetchProfileSummary(token: token)
        let buildStatus = try? await TodayFlowAPIClient.shared.fetchProfileBuildStatus(token: token)
        let rings = await meaningRuntime.refreshRings(token: token)?.rings ?? []
        await MainActor.run {
            self.profileSummary = summary
            self.profileBuildStatus = buildStatus
            if !rings.isEmpty {
                self.meaningRings = rings
            }
        }
        return summary
    }

    func loadCompactUserModel(localDate: String? = nil, force: Bool = false) async throws -> CompactUserModelResponse {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let date = localDate ?? todayCycle?.date ?? Self.isoDate(from: Date())
        if let compactUserModel, !force, localDate == nil {
            return compactUserModel
        }
        let model = try await TodayFlowAPIClient.shared.fetchCompactUserModel(token: token, localDate: date)
        await MainActor.run {
            self.compactUserModel = model
        }
        return model
    }

    func loadCompactUserModelConfidenceHistory(
        localDate: String? = nil,
        windowDays: Int = 90,
        force: Bool = false
    ) async throws -> CompactUserModelConfidenceHistoryResponse {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let date = localDate ?? todayCycle?.date ?? Self.isoDate(from: Date())
        if let cumConfidenceHistory, !force, localDate == nil {
            return cumConfidenceHistory
        }
        let history = try await TodayFlowAPIClient.shared.fetchCompactUserModelConfidenceHistory(
            token: token,
            localDate: date,
            windowDays: windowDays
        )
        await MainActor.run {
            self.cumConfidenceHistory = history
        }
        return history
    }

    func updateAccountSettings(_ update: AccountSettingsUpdate) async throws -> AccountSettings {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let settings = try await TodayFlowAPIClient.shared.updateAccountSettings(token: token, payload: update)
        await MainActor.run {
            accountSettings = settings
            user = UserProfile(
                email: settings.email,
                firstName: settings.firstName ?? birthProfile?.firstName ?? user.firstName,
                location: birthProfile?.birthPlace ?? user.location,
                timezone: birthProfile?.timezone ?? user.timezone,
                membership: authSession?.membershipTitle ?? user.membership
            )
        }
        return settings
    }

    func updateTodayNarrativeDepthLevel(_ level: String) async throws -> AccountSettings {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        let settings = try await TodayFlowAPIClient.shared.patchTodayNarrativeDepthLevel(token: token, level: level)
        await MainActor.run {
            accountSettings = settings
        }
        return settings
    }

    func loadNatalChart(force: Bool = false, astroProfileID: Int? = nil) async throws -> NatalChartPreview {
        guard let token = authSession?.token else {
            throw APIError.server("You need to sign in first.")
        }
        if let natalChart, !force, astroProfileID == nil {
            return natalChart
        }
        let chart: NatalChartPreview
        do {
            chart = try await TodayFlowAPIClient.shared.fetchNatalChart(token: token, astroProfileID: astroProfileID)
        } catch {
            guard astroProfileID == nil, shouldAttemptCoreSetupRecovery(after: error) else {
                throw error
            }
            await syncCoreSetupFromBirthProfileIfNeeded()
            chart = try await TodayFlowAPIClient.shared.fetchNatalChart(token: token, astroProfileID: astroProfileID)
        }
        if astroProfileID == nil {
            await MainActor.run {
                natalChart = chart
            }
        }
        return chart
    }

    func loadTodayNarrative(
        surface: TodayNarrativeSurface,
        force: Bool = false,
        ritualContext: TodayNarrativeRitualContextPayload? = nil
    ) async throws -> TodayNarrativeResponse {
        guard let token = effectiveBearerToken() else {
            throw APIError.server("You need to sign in first.")
        }
        guard let date = todayCycle?.date else {
            throw APIError.server("Today flow is not loaded yet.")
        }

        let bypassCache = force || (surface == .guide && ritualContext != nil)
        if !bypassCache, let cached = cachedNarrative(for: surface) {
            return cached
        }

        let parentID = surface == .guide ? nil : todayGuideNarrative?.generationID
        let effectiveRitual: TodayNarrativeRitualContextPayload?
        if surface == .guide {
            effectiveRitual = ritualContext
        } else if let ritualContext {
            effectiveRitual = ritualContext
        } else if date == lastRitualNarrativeContextDate {
            effectiveRitual = lastRitualNarrativeContext
        } else {
            effectiveRitual = nil
        }
        do {
            let response = try await TodayFlowAPIClient.shared.fetchTodayNarrative(
                token: token,
                targetDate: date,
                surface: surface,
                parentGenerationID: parentID,
                ritualContext: effectiveRitual
            )
            await MainActor.run {
                switch surface {
                case .guide:
                    todayGuideNarrative = response
                case .dayLayer:
                    todayDayNarrative = response
                case .spheres:
                    todaySpheresNarrative = response
                case .evening:
                    todayEveningNarrative = response
                }
            }
            return response
        } catch {
            if shouldSignOutAfterSessionRefreshFailure(error) {
                signOut()
            }
            throw error
        }
    }

    /// После карты + числа + настроения: guide с `ritual_context`, затем day_layer / spheres / evening с новым parent id.
    func refreshTodayNarrativeAfterRitual(context: TodayNarrativeRitualContextPayload) async throws {
        if let d = todayCycle?.date {
            lastRitualNarrativeContextDate = d
            lastRitualNarrativeContext = context
        }
        await MainActor.run {
            todayDayNarrative = nil
            todaySpheresNarrative = nil
            todayEveningNarrative = nil
        }
        _ = try await loadTodayNarrative(surface: .guide, force: true, ritualContext: context)
        _ = try await loadTodayNarrative(surface: .dayLayer, force: true)
        _ = try await loadTodayNarrative(surface: .spheres, force: true)
        _ = try await loadTodayNarrative(surface: .evening, force: true)
    }

    private var currentSessionEmail: String? {
        authSession?.email.lowercased()
    }

    private func apply(_ payload: TodayFlowBootstrapPayload) {
        birthProfile = payload.profile
        todayCycle = payload.todayCycle
        coreProfile = nil
        fusionIndex = payload.fusionIndex
        fusionHistory = payload.fusionHistory
        persistFusionForEnergyMap(fusion: payload.fusionIndex)
        TodayDayContinuitySync.backfillFromCycle(payload.todayCycle)
        if let dateISO = payload.todayCycle?.date {
            TodayDayEngagementSync.backfillFromRitualExtras(email: authSession?.email, dateISO: dateISO)
        }
        user = UserProfile(
            email: authSession?.email ?? user.email,
            firstName: payload.profile.firstName,
            location: payload.profile.birthPlace,
            timezone: payload.profile.timezone,
            membership: authSession?.membershipTitle ?? "Founding member"
        )
        dailyFocus = payload.dailyFocus
        rituals = payload.rituals
        persistSnapshot()
    }

    private func applyAuthSession(_ session: AuthSession, resettingProfile: Bool) {
        authSession = session
        user = UserProfile(
            email: session.email,
            firstName: birthProfile?.firstName ?? user.firstName,
            location: birthProfile?.birthPlace ?? user.location,
            timezone: birthProfile?.timezone ?? user.timezone,
            membership: session.membershipTitle
        )
        TodayFlowPersistence.shared.saveSession(session)

        if resettingProfile {
            birthProfile = nil
            todayCycle = nil
            fusionIndex = nil
            fusionHistory = []
            accountSettings = nil
            coreProfile = nil
            profileSummary = nil
            profileBuildStatus = nil
            meaningRings = []
            natalChart = nil
            todayGuideNarrative = nil
            todayDayNarrative = nil
            todaySpheresNarrative = nil
            todayEveningNarrative = nil
            lastRitualNarrativeContext = nil
            lastRitualNarrativeContextDate = nil
            dailyFocus = .placeholder
            rituals = Ritual.placeholder
            loadState = .idle
            hasSeenProfileSummary = false
            sessionWarningMessage = nil
            lastSessionValidatedAt = nil
            lastSnapshotSavedAt = nil
            lastSubmittedDraft = nil
            TodayFlowPersistence.shared.clearSnapshot()
            TodayFlowPersistence.shared.clearProfileSummarySeen(for: session.email)
            TodayFlowPersistence.shared.clearLastAuthValidatedAt(for: session.email)
            TodayFlowPersistence.shared.clearLastSnapshotSavedAt(for: session.email)
        } else {
            hasSeenProfileSummary = TodayFlowPersistence.shared.hasProfileSummarySeen(for: session.email)
            lastSessionValidatedAt = TodayFlowPersistence.shared.loadLastAuthValidatedAt(for: session.email)
            lastSnapshotSavedAt = TodayFlowPersistence.shared.loadLastSnapshotSavedAt(for: session.email)
            persistSnapshot()
        }
        AppConfig.setAuthToken(session.token)
    }

    /// Если локальный профиль рождения очищен, но на сервере уже есть astro profile,
    /// восстанавливаем его, чтобы не отправлять пользователя в онбординг повторно.
    private func restoreBirthProfileFromServerIfNeeded() async {
        guard birthProfile == nil, let token = authSession?.token else { return }
        do {
            let profiles = try await TodayFlowAPIClient.shared.listAstroProfiles(token: token)
            guard let selected = profiles.first(where: { $0.isPrimary == true }) ?? profiles.first else { return }
            guard let restored = Self.birthProfile(from: selected) else { return }
            await MainActor.run {
                birthProfile = restored
                if loadState == .idle {
                    loadState = .loaded
                }
                user = UserProfile(
                    email: authSession?.email ?? user.email,
                    firstName: restored.firstName,
                    location: restored.birthPlace,
                    timezone: restored.timezone,
                    membership: authSession?.membershipTitle ?? user.membership
                )
                persistSnapshot()
            }
        } catch {
            // Тихо пропускаем: если профиля нет на сервере, пользователь действительно пойдет в онбординг.
        }
    }

    private func restorePersistedState() {
        authSession = TodayFlowPersistence.shared.loadSession()
        lastSubmittedDraft = TodayFlowPersistence.shared.loadDraft()

        guard let session = authSession else { return }
        hasSeenProfileSummary = TodayFlowPersistence.shared.hasProfileSummarySeen(for: session.email)
        lastSessionValidatedAt = TodayFlowPersistence.shared.loadLastAuthValidatedAt(for: session.email)
        lastSnapshotSavedAt = TodayFlowPersistence.shared.loadLastSnapshotSavedAt(for: session.email)
        AppConfig.setAuthToken(session.token)
        user = UserProfile(
            email: session.email,
            firstName: user.firstName,
            location: user.location,
            timezone: user.timezone,
            membership: session.membershipTitle
        )

        guard let snapshot = TodayFlowPersistence.shared.loadSnapshot(),
              snapshot.ownerEmail.caseInsensitiveCompare(session.email) == .orderedSame else {
            return
        }

        birthProfile = snapshot.profile
        todayCycle = snapshot.todayCycle
        fusionIndex = snapshot.fusionIndex
        fusionHistory = snapshot.fusionHistory
        dailyFocus = snapshot.dailyFocus
        rituals = snapshot.rituals
        user = snapshot.user
        loadState = .loaded
    }

    func markProfileSummarySeen() {
        hasSeenProfileSummary = true
        TodayFlowPersistence.shared.saveProfileSummarySeen(for: currentSessionEmail)
    }

    private func persistSnapshot() {
        guard let birthProfile, let session = authSession else { return }
        let snapshot = TodayFlowPersistedState(
            ownerEmail: session.email,
            profile: birthProfile,
            todayCycle: todayCycle,
            fusionIndex: fusionIndex,
            fusionHistory: fusionHistory,
            dailyFocus: dailyFocus,
            rituals: rituals,
            user: user
        )
        TodayFlowPersistence.shared.save(snapshot: snapshot, draft: lastSubmittedDraft)
        let now = Date()
        lastSnapshotSavedAt = now
        TodayFlowPersistence.shared.saveLastSnapshotSavedAt(for: session.email, date: now)
    }

    private func requireTodayContext() throws -> (token: String, date: String) {
        guard let token = effectiveBearerToken() else {
            throw APIError.server("You need to sign in first.")
        }
        guard let date = todayCycle?.date else {
            throw APIError.server("Today flow is not loaded yet.")
        }
        return (token, date)
    }

    private func cachedNarrative(for surface: TodayNarrativeSurface) -> TodayNarrativeResponse? {
        switch surface {
        case .guide:
            return todayGuideNarrative
        case .dayLayer:
            return todayDayNarrative
        case .spheres:
            return todaySpheresNarrative
        case .evening:
            return todayEveningNarrative
        }
    }

    private func shouldAttemptCoreSetupRecovery() -> Bool {
        guard birthProfile != nil, let email = currentSessionEmail else { return false }
        return !TodayFlowPersistence.shared.hasCoreSetupSyncMarker(for: email)
    }

    private func shouldAttemptCoreSetupRecovery(after error: Error) -> Bool {
        guard shouldAttemptCoreSetupRecovery() else { return false }
        let message = readableError(error).lowercased()
        return message.contains("no astro profile")
            || message.contains("profile not found")
            || message.contains("astro profile")
            || message.contains("no profile")
            || message.contains("not found")
    }

    private func captureBootstrapError(_ operation: () async throws -> Void) async -> String? {
        do {
            try await operation()
            return nil
        } catch {
            return readableError(error)
        }
    }

    private static func joinedErrorMessage(_ messages: [String]) -> String {
        var seen = Set<String>()
        let unique = messages.filter { seen.insert($0).inserted }
        return unique.joined(separator: "\n")
    }
}

extension TodayFlowStore {
    enum StoreError: LocalizedError {
        case invalidURL
        case invalidResponse
        case http(Int, String)

        var errorDescription: String? {
            switch self {
            case .invalidURL:
                return "Неверный адрес API"
            case .invalidResponse:
                return "Неожиданный ответ сервера"
            case let .http(code, message):
                if code == 401 {
                    return "Нет доступа (401). Выполни вход на экране авторизации — без токена день, карты и таро не загружаются."
                }
                return message
            }
        }
    }
}

private extension TodayFlowStore {
    static func birthProfile(from stored: StoredAstroProfile) -> BirthProfile? {
        guard let birthDate = parseServerDate(stored.birthDate) else { return nil }
        var draft = BirthProfileDraft()
        draft.firstName = stored.label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "Без имени" : stored.label
        draft.birthDate = birthDate
        draft.knowsBirthTime = !(stored.timeUnknown ?? false) && stored.birthTime != nil
        draft.birthTime = parseServerTime(stored.birthTime, on: birthDate) ?? birthDate
        draft.birthPlace = (stored.locationName ?? "Место не указано").trimmingCharacters(in: .whitespacesAndNewlines)
        draft.timezone = TimeZone.current.identifier
        draft.selectedCoordinates = {
            guard let lat = stored.latitude, let lon = stored.longitude else { return nil }
            return BirthCoordinates(latitude: lat, longitude: lon)
        }()
        return draft.resolved
    }

    static func parseServerDate(_ raw: String) -> Date? {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: raw)
    }

    static func parseServerTime(_ raw: String?, on baseDate: Date) -> Date? {
        guard let raw = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else { return nil }
        let fmts = ["HH:mm:ss", "HH:mm"]
        for format in fmts {
            let timeFormatter = DateFormatter()
            timeFormatter.calendar = Calendar(identifier: .gregorian)
            timeFormatter.locale = Locale(identifier: "en_US_POSIX")
            timeFormatter.timeZone = TimeZone.current
            timeFormatter.dateFormat = format
            guard let parsed = timeFormatter.date(from: raw) else { continue }
            let cal = Calendar(identifier: .gregorian)
            let date = cal.dateComponents([.year, .month, .day], from: baseDate)
            let time = cal.dateComponents([.hour, .minute, .second], from: parsed)
            var combined = DateComponents()
            combined.year = date.year
            combined.month = date.month
            combined.day = date.day
            combined.hour = time.hour
            combined.minute = time.minute
            combined.second = time.second
            return cal.date(from: combined)
        }
        return nil
    }

    struct TrackingAPIClient {
        let bearer: String

        func getDictionary(path: String, query: [URLQueryItem] = []) async throws -> [String: Any] {
            let result = try await send(path: path, method: "GET", query: query, body: nil)
            guard let dictionary = result as? [String: Any] else {
                throw StoreError.invalidResponse
            }
            return dictionary
        }

        func getArray(path: String, query: [URLQueryItem] = []) async throws -> [[String: Any]] {
            let result = try await send(path: path, method: "GET", query: query, body: nil)
            guard let array = result as? [[String: Any]] else {
                throw StoreError.invalidResponse
            }
            return array
        }

        func sendDictionary(path: String, method: String, body: [String: Any]) async throws -> [String: Any] {
            let result = try await send(path: path, method: method, query: [], body: body)
            guard let dictionary = result as? [String: Any] else {
                throw StoreError.invalidResponse
            }
            return dictionary
        }

        private func send(path: String, method: String, query: [URLQueryItem], body: [String: Any]?) async throws -> Any {
            guard var components = URLComponents(url: AppConfig.apiBaseURL, resolvingAgainstBaseURL: false) else {
                throw StoreError.invalidURL
            }
            let normalizedPath = path.hasPrefix("/") ? path : "/" + path
            components.path = components.path + normalizedPath
            if !query.isEmpty {
                components.queryItems = query
            }
            guard let url = components.url else {
                throw StoreError.invalidURL
            }

            var request = URLRequest(url: url)
            request.httpMethod = method
            request.timeoutInterval = 20
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.setValue(Locale.preferredLanguages.first ?? "en-US", forHTTPHeaderField: "Accept-Language")

            let token = bearer.trimmingCharacters(in: .whitespacesAndNewlines)
            if !token.isEmpty {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            }

            if let body {
                request.httpBody = try JSONSerialization.data(withJSONObject: body)
            }

            let data: Data
            let response: URLResponse
            do {
                (data, response) = try await URLSession.shared.data(for: request)
            } catch {
                throw networkAwareError(error, url: url)
            }
            guard let http = response as? HTTPURLResponse else {
                throw StoreError.invalidResponse
            }
            guard (200...299).contains(http.statusCode) else {
                let message = String(data: data, encoding: .utf8) ?? "HTTP \(http.statusCode)"
                throw StoreError.http(http.statusCode, message)
            }

            guard !data.isEmpty else { return [:] }
            return try JSONSerialization.jsonObject(with: data)
        }

        private func networkAwareError(_ error: Error, url: URL) -> StoreError {
            guard let urlError = error as? URLError else {
                return .http(-1, error.localizedDescription)
            }

            let hostLine = url.host ?? url.absoluteString
            switch urlError.code {
            case .notConnectedToInternet:
                return .http(-1, "Нет интернета. Не удалось подключиться к \(hostLine).")
            case .cannotConnectToHost, .cannotFindHost:
                return .http(-1, "Не удалось подключиться к \(hostLine). Проверь API host в Settings.")
            case .timedOut:
                return .http(-1, "Сервер слишком долго не отвечает (\(hostLine)).")
            default:
                return .http(-1, "Ошибка сети для \(hostLine): \(urlError.localizedDescription)")
            }
        }
    }

    static func buildTodayDashboard(
        opening: [String: Any],
        bundle: [String: Any],
        state: [String: Any],
        prompt: [String: Any],
        fallbackDateISO: String,
        streakCount: Int,
        recentFusionHistory: [FusionIndex],
        recentCalendar: CalendarSnapshot
    ) -> TodayDashboard {
        let core = dictionary(bundle["core"])
        let scenariosPayload = dictionary(bundle["scenarios"])
        let dayConnection = dictionary(opening["day_connection"])
        let scores = dictionary(state["scores"])
        let hero = dictionary(dictionary(core["decision_engine"])["hero"])
        let foundation = dictionary(core["daily_foundation"])
        let coreProfile = dictionary(core["core_profile"])
        let interpretation = dictionary(coreProfile["interpretation"])
        let dailyInterpretation = dictionary(coreProfile["daily_interpretation"])
        let dailyLenses = dictionary(dailyInterpretation["daily_lenses"])

        let dateISO = string(opening["date"]) ?? string(bundle["date"]) ?? fallbackDateISO
        let dateTitle = prettyDate(dateISO)
        let energy = int(scores["energy"])
        let focus = int(scores["focus"])
        let balance = int(scores["emotional_balance"])
        let fusionScoresSnapshot: FusionScores? = scores.isEmpty
            ? nil
            : FusionScores(
                energy: min(100, max(0, energy)),
                emotionalBalance: min(100, max(0, balance)),
                focus: min(100, max(0, focus))
            )
        let actionItems = strings(dictionary(core["decision_engine"])["actions"])
        let focusItems = strings(hero["focus"])
        let risk = string(hero["risk"]) ?? "Держи день уже, чем твои импульсы раздувают его."
        let profilePrism = string(foundation["profile_prism"])
            ?? string(interpretation["identity"])
            ?? string(dailyLenses["general"])
            ?? "Собираю разбор вокруг твоего живого профиля."

        let scenarioItems = array(scenariosPayload["scenarios"]).enumerated().compactMap { index, item in
            let payload = dictionary(item)
            let slug = string(payload["slug"]) ?? "scene-\(index)"
            let title = string(payload["title"]) ?? string(payload["name"]) ?? slug.capitalized
            let rawFocus = string(payload["focus"]) ?? ""
            let focusTrimmed = rawFocus.trimmingCharacters(in: .whitespacesAndNewlines)
            let focusField: String? = focusTrimmed.isEmpty ? nil : focusTrimmed
            let summary =
                string(payload["summary"]) ?? string(payload["focus"]) ?? string(payload["guidance"])
                    ?? "Сценарий дня уже собран, а расширенная интерпретация подтянется по мере загрузки."
            let href = string(dictionary(payload["route"])["href"]) ?? fallbackRoute(for: slug)
            return TodayScenario(
                id: slug,
                title: title,
                focus: focusField,
                summary: summary,
                accentHex: accentHex(for: slug),
                deepLinkPath: href
            )
        }

        let ritualFeedback = string(dayConnection["ritual_feedback"])
        let quickDecision = string(dayConnection["quick_decision_answer"])
        let questionAnswer = string(dayConnection["question_of_day_answer"]) ?? ""
        let morningIntention = string(dayConnection["morning_intention"]) ?? ""
        let completedExecutionActions = strings(dayConnection["execution_actions_done"])
        let respectedAvoidActions = strings(dayConnection["avoid_actions_respected"])
        let completedFlags = [
            bool(dayConnection["morning_completed"]),
            bool(dayConnection["day_completed"]),
            bool(dayConnection["evening_completed"])
        ]
        let completionProgress = Double(completedFlags.filter { $0 }.count) / 3.0
        let signalCount = [
            !morningIntention.isEmpty,
            ritualFeedback?.isEmpty == false,
            quickDecision?.isEmpty == false,
            !questionAnswer.isEmpty,
            string(dayConnection["evening_reflection"])?.isEmpty == false
        ]
        .filter { $0 }
        .count
        let signalProgress = Double(signalCount) / 5.0
        let trackerExecution = trackerExecutionScore(on: dateISO, from: recentCalendar)
        let actionExecution = min(Double(completedExecutionActions.count) / 3.0, 1.0)
        let avoidRespect = min(Double(respectedAvoidActions.count) / 2.0, 1.0)

        let executionScore = clampedScore((completionProgress * 0.35 + signalProgress * 0.2 + trackerExecution * 0.3 + actionExecution * 0.15) * 100.0)
        let awarenessScore = clampedScore(Double(balance) * 0.42 + signalProgress * 28.0 + trackerExecution * 20.0 + avoidRespect * 10.0)
        let alignmentScore = clampedScore(Double(focus) * 0.35 + Double(energy) * 0.2 + actionExecution * 20.0 + avoidRespect * 25.0 + completionProgress * 15.0)

        let metrics = [
            RingMetric(id: "execution", title: "Закрытие дня", value: executionScore, subtitle: executionSubtitle(executionScore)),
            RingMetric(id: "awareness", title: "Ясность", value: awarenessScore, subtitle: awarenessSubtitle(awarenessScore)),
            RingMetric(id: "alignment", title: "Согласованность", value: alignmentScore, subtitle: alignmentSubtitle(alignmentScore))
        ]
        let contour = buildLifeLevelContour(
            recentFusionHistory: recentFusionHistory,
            currentExecution: executionScore,
            currentAlignment: alignmentScore,
            streakCount: streakCount
        )

        return TodayDashboard(
            dateISO: dateISO,
            dateTitle: dateTitle,
            fusionScores: fusionScoresSnapshot,
            headline: string(foundation["headline"])
                ?? string(dictionary(core["tarot_explanation"])["summary"])
                ?? string(dictionary(core["numerology_explanation"])["summary"])
                ?? "День готов. Начни с одной ясной линии — остальное подтянется.",
            profilePrism: profilePrism,
            tarotTitle: string(dictionary(core["tarot_card"])["name"]) ?? "Карта дня",
            numerologyTitle: numerologyLine(from: dictionary(core["numerology_number"])),
            energyTitle: string(hero["energy_label"]) ?? "Ритм по отметкам",
            guidanceSummary: strings(dictionary(core["daily_recommendations"])["priorities"]).first
                ?? actionItems.first
                ?? "Открой день одним действием, которое убирает шум.",
            actionItems: actionItems.isEmpty ? ["Назови главную линию дня."] : actionItems,
            focusItems: focusItems.isEmpty ? ["темп", "ясность", "доведение"] : focusItems,
            riskNote: risk,
            morningIntention: morningIntention,
            checkinTitle: string(prompt["title"]) ?? "Одна строка на сегодня",
            checkinSubtitle: string(prompt["subtitle"]) ?? "Задай тон, пока день не начал тянуть в разные стороны.",
            checkinHint: string(prompt["input_hint"]) ?? "Что сегодня важнее всего?",
            ritualFeedback: ritualFeedback,
            quickDecisionAnswer: quickDecision,
            questionOfDayAnswer: questionAnswer,
            completedExecutionActions: completedExecutionActions,
            respectedAvoidActions: respectedAvoidActions,
            metrics: metrics,
            contour: contour,
            scenarios: scenarioItems,
            streakCount: streakCount,
            completionProgress: completionProgress
        )
    }

    /// Склонение для «ещё N дней» в подсказках уровня жизни.
    private static func ruDayPhrase(_ n: Int) -> String {
        let n100 = n % 100
        let n10 = n % 10
        if n100 >= 11 && n100 <= 14 { return "\(n) дней" }
        switch n10 {
        case 1: return "\(n) день"
        case 2, 3, 4: return "\(n) дня"
        default: return "\(n) дней"
        }
    }

    private static func buildLifeLevelContour(
        recentFusionHistory: [FusionIndex],
        currentExecution: Int,
        currentAlignment: Int,
        streakCount: Int
    ) -> LifeLevelContour {
        let history = Array(recentFusionHistory.orderedFusionHistory.suffix(7))
        let trackedDays = history.count

        let execution = if history.isEmpty {
            currentExecution
        } else {
            clampedScore(mean(history.map(executionScore(from:))))
        }

        let alignment = if history.isEmpty {
            currentAlignment
        } else {
            clampedScore(mean(history.map { Double($0.scores.average) }))
        }

        let consistency = consistencyScore(from: history, streakCount: streakCount)
        let score = clampedScore(Double(execution) * 0.4 + Double(alignment) * 0.4 + Double(consistency) * 0.2)
        let tier = lifeLevelTier(for: score)
        let nextTier = tier.next
        let previousFloor = thresholdFloor(for: tier)
        let nextFloor = nextTier.map { thresholdFloor(for: $0) } ?? 100
        let progressRange = max(1, nextFloor - previousFloor)
        let progressToNext = nextTier == nil ? 1.0 : min(1.0, Double(score - previousFloor) / Double(progressRange))
        let weakestAxis = [
            ("execution", execution),
            ("alignment", alignment),
            ("consistency", consistency)
        ]
        .min(by: { $0.1 < $1.1 })?.0 ?? "consistency"
        let gap = nextTier.map { max(0, thresholdFloor(for: $0) - score) }
        let daysHint = max(2, Int(ceil(Double(gap ?? 0) / 3.0)))

        let nextTierTitle = nextTier?.title ?? "следующий уровень"
        let guidanceLine: String
        switch weakestAxis {
        case "execution":
            guidanceLine = nextTier == nil
            ? "Продолжай закрывать дневной контур целиком — так уровень не «плывёт»."
            : "Чтобы выйти на «\(nextTierTitle)»: доводи дневные действия до конца ещё \(Self.ruDayPhrase(daysHint))."
        case "alignment":
            guidanceLine = nextTier == nil
            ? "Береги качество решений и избегай импульсивных переключений."
            : "Чтобы выйти на «\(nextTierTitle)»: меньше импульсивных решений и держи узкий фокус."
        default:
            guidanceLine = nextTier == nil
            ? "Держи ритм ровным — так система остаётся надёжной."
            : "Чтобы выйти на «\(nextTierTitle)»: сохраняй стабильность ещё \(Self.ruDayPhrase(daysHint))."
        }

        let alertLine: String?
        if let nextTier, let gap, gap <= 5 {
            alertLine = "Почти уровень «\(nextTier.title)»"
        } else if consistency < 52 {
            alertLine = "Ритм теряет стабильность"
        } else {
            alertLine = nil
        }

        return LifeLevelContour(
            tier: tier,
            score: score,
            execution: execution,
            alignment: alignment,
            consistency: consistency,
            trackedDays: trackedDays,
            progressToNext: progressToNext,
            statusLine: tier.meaning,
            guidanceLine: guidanceLine,
            alertLine: alertLine
        )
    }

    private static func executionScore(from item: FusionIndex) -> Double {
        let completedSignals = Double([
            item.activityContext.practiceCount > 0,
            item.activityContext.ritualCompleted,
            item.activityContext.diaryDone,
            item.activityContext.asceticCompleted,
            item.activityContext.affirmationCompleted
        ]
        .filter { $0 }
        .count)
        return (completedSignals / 5.0) * 100.0
    }

    private static func trackerExecutionScore(on dateISO: String, from calendar: CalendarSnapshot) -> Double {
        guard let day = calendar.days.first(where: { $0.dateISO == dateISO }), !day.activities.isEmpty else {
            return 0
        }

        let weightedTotal = day.activities.reduce(0.0) { partial, activity in
            partial + activityWeight(for: activity.id)
        }
        guard weightedTotal > 0 else { return 0 }

        let completedWeight = day.activities.reduce(0.0) { partial, activity in
            partial + (activity.isComplete ? activityWeight(for: activity.id) : 0)
        }
        return min(1.0, completedWeight / weightedTotal)
    }

    private static func activityWeight(for activityID: String) -> Double {
        switch activityID {
        case "goal":
            return 1.2
        case "habits":
            return 1.0
        case "asceticism":
            return 1.0
        case "practice":
            return 0.9
        case "diary":
            return 0.8
        case "affirmation":
            return 0.55
        case "state_phases", "daily_signals", "ritual":
            return 0.7
        default:
            return 0.6
        }
    }

    private static func consistencyScore(from history: [FusionIndex], streakCount: Int) -> Int {
        guard !history.isEmpty else {
            return clampedScore(min(Double(streakCount) * 12.0, 100.0))
        }

        let coverage = Double(history.count) / 7.0 * 100.0
        let trailingRun = trailingConsecutiveDays(in: history)
        let consecutive = Double(trailingRun) / 7.0 * 100.0
        let streakBoost = min(Double(streakCount) / 7.0 * 100.0, 100.0)
        return clampedScore(coverage * 0.35 + consecutive * 0.45 + streakBoost * 0.2)
    }

    private static func trailingConsecutiveDays(in history: [FusionIndex]) -> Int {
        let orderedDates = history.compactMap { date(from: $0.date) }.sorted()
        guard let last = orderedDates.last else { return 0 }
        var current = last
        var run = 1

        for candidate in orderedDates.dropLast().reversed() {
            let diff = Calendar.current.dateComponents([.day], from: candidate, to: current).day ?? 0
            guard diff == 1 else { break }
            run += 1
            current = candidate
        }

        return run
    }

    private static func lifeLevelTier(for score: Int) -> LifeLevelTier {
        switch score {
        case ..<45: return .bronze
        case ..<65: return .silver
        case ..<82: return .gold
        default: return .platinum
        }
    }

    private static func thresholdFloor(for tier: LifeLevelTier) -> Int {
        switch tier {
        case .bronze: return 0
        case .silver: return 45
        case .gold: return 65
        case .platinum: return 82
        }
    }

    private static func clampedScore(_ value: Double) -> Int {
        Int(min(max(value.rounded(), 0), 100))
    }

    private static func mean(_ values: [Double]) -> Double {
        guard !values.isEmpty else { return 0 }
        return values.reduce(0, +) / Double(values.count)
    }

    private static func actionTrackingKey(from title: String) -> String {
        let lowered = title
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let scalars = lowered.unicodeScalars.map { scalar -> Character in
            CharacterSet.alphanumerics.contains(scalar) ? Character(scalar) : "-"
        }
        let normalized = String(scalars)
            .replacingOccurrences(of: "--+", with: "-", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: "-"))
        return normalized.isEmpty ? UUID().uuidString.lowercased() : normalized
    }

    private static func executionSubtitle(_ value: Int) -> String {
        switch value {
        case 75...:
            return "Ты реально закрываешь день действием"
        case 55...74:
            return "День движется, но без полного «закрытия»"
        default:
            return "Слишком много остаётся висеть недоделанным"
        }
    }

    private static func awarenessSubtitle(_ value: Int) -> String {
        switch value {
        case 75...:
            return "Ты ясно видишь день"
        case 55...74:
            return "Часть сигналов ясна, часть ещё шумит"
        default:
            return "День всё ещё ведёт фоновый шум"
        }
    }

    private static func alignmentSubtitle(_ value: Int) -> String {
        switch value {
        case 75...:
            return "Выборы хорошо ложатся на день"
        case 55...74:
            return "Направление есть, но без полной точности"
        default:
            return "Решения могут уводить с курса"
        }
    }

    static func buildCalendarSnapshot(from payload: [String: Any], displayedMonthDateISO: String) -> CalendarSnapshot {
        let daysPayload = array(payload["days"])
        let goalTracks = array(payload["goal_tracks"]).compactMap { item in
            parseGoalTrack(dictionary(item))
        }
        let habitTracks = array(payload["habit_tracks"]).compactMap { item in
            parseHabitTrack(dictionary(item))
        }
        let asceticTracks = array(payload["ascetic_tracks"]).compactMap { item in
            parseAsceticTrack(dictionary(item))
        }
        let streaks = dictionary(payload["streaks"]).reduce(into: [String: Int]()) { partial, pair in
            partial[pair.key] = int(pair.value)
        }
        let monthSummary = dictionary(payload["month_summary"]).reduce(into: [String: Int]()) { partial, pair in
            partial[pair.key] = int(pair.value)
        }

        let monthAnchor = date(from: displayedMonthDateISO) ?? Date()
        let targetMonth = Calendar.current.component(.month, from: monthAnchor)
        let targetYear = Calendar.current.component(.year, from: monthAnchor)

        let days = daysPayload.compactMap { item -> TrackerDaySummary? in
            let day = dictionary(item)
            let dateISO = string(day["date"]) ?? ""
            guard !dateISO.isEmpty else { return nil }
            let activitiesPayload = dictionary(day["activities"])
            let activities = activitiesPayload.map { key, value in
                let payload = dictionary(value)
                let title = activityTitle(for: key)
                let count = int(payload["count"])
                let detail: String
                if count > 1 {
                    detail = "\(count) сделано"
                } else if let filled = payload["filled"] {
                    detail = "\(int(filled))/\(int(payload["of"])) фаз"
                } else if let titles = payload["titles"] as? [String], let first = titles.first, !first.isEmpty {
                    detail = first
                } else if let names = payload["names"] as? [String], let first = names.first, !first.isEmpty {
                    detail = first
                } else {
                    detail = payload["completed"] != nil ? "Отмечено" : "Доступно"
                }
                return TrackerActivitySummary(
                    id: key,
                    title: title,
                    detail: detail,
                    isComplete: bool(payload["completed"])
                )
            }
            .sorted { $0.title < $1.title }

            let currentDate = date(from: dateISO) ?? Date()
            return TrackerDaySummary(
                id: dateISO,
                dateISO: dateISO,
                dayNumber: dayNumber(from: currentDate),
                weekdayTitle: weekdaySymbol(from: currentDate),
                isToday: dateISO == isoDate(from: Date()),
                isInDisplayedMonth: Calendar.current.component(.month, from: currentDate) == targetMonth
                    && Calendar.current.component(.year, from: currentDate) == targetYear,
                completionCount: activities.filter(\.isComplete).count,
                activities: activities,
                moodScore: optionalInt(day["mood"])
            )
        }

        let title = monthTitle(from: monthAnchor)
        let fromDateISO = string(dictionary(payload["month_summary"])["from"]) ?? displayedMonthDateISO
        let toDateISO = string(dictionary(payload["month_summary"])["to"]) ?? displayedMonthDateISO
        return CalendarSnapshot(
            monthTitle: title,
            fromDateISO: fromDateISO,
            toDateISO: toDateISO,
            days: days,
            streaks: streaks,
            monthSummary: monthSummary,
            goalTracks: goalTracks,
            habitTracks: habitTracks,
            asceticTracks: asceticTracks
        )
    }

    static func parseAffirmationCatalogItem(_ item: [String: Any]) -> AffirmationCatalogItem? {
        let idPart: String?
        if let s = string(item["id"]) {
            idPart = s
        } else if let n = optionalInt(item["id"]) {
            idPart = "\(n)"
        } else {
            idPart = nil
        }
        guard let rawId = idPart?.trimmingCharacters(in: .whitespacesAndNewlines), !rawId.isEmpty else {
            return nil
        }
        let title = string(item["title"]) ?? ""
        let text = string(item["text"]) ?? ""
        return AffirmationCatalogItem(id: rawId, title: title, text: text)
    }

    static func parseAsceticTrack(_ item: [String: Any]) -> AsceticTrack? {
        guard let aid = string(item["asceticism_id"]), !aid.isEmpty else { return nil }
        let rawEntries = array(item["entries"])
        let entries = rawEntries.compactMap { raw -> AsceticTrackEntry? in
            let d = dictionary(raw)
            let dateISO = string(d["date"]) ?? ""
            guard !dateISO.isEmpty else { return nil }
            return AsceticTrackEntry(dateISO: dateISO, completed: bool(d["completed"]))
        }
        return AsceticTrack(
            asceticismId: aid,
            title: string(item["title"]),
            contractStatus: string(item["contract_status"]),
            entries: entries
        )
    }

    static func parseHabitTrack(_ item: [String: Any]) -> HabitTrack? {
        guard let id = optionalInt(item["id"]) else { return nil }
        return HabitTrack(
            id: id,
            name: string(item["name"]) ?? "Привычка",
            isActive: item["is_active"] == nil ? true : bool(item["is_active"]),
            completedDates: Set(strings(item["completed_dates"]))
        )
    }

    static func parseGoalTrack(_ item: [String: Any]) -> GoalTrack? {
        guard let id = optionalInt(item["id"]) else { return nil }
        let scope = GoalScope(rawValue: string(item["scope"]) ?? "week") ?? .week
        return GoalTrack(
            id: id,
            title: string(item["title"]) ?? "Цель",
            scope: scope,
            completed: bool(item["completed"]),
            weekStart: string(item["week_start"]) ?? isoDate(from: Date()),
            stepDates: Set(strings(item["step_dates"]))
        )
    }

    static func parseObservationDiaryEntry(_ item: [String: Any]) -> ObservationDiaryEntry? {
        guard let id = optionalInt(item["id"]) else { return nil }
        return ObservationDiaryEntry(
            id: id,
            dateISO: string(item["date"]) ?? isoDate(from: Date()),
            noticed: string(item["noticed"]) ?? "",
            hardest: string(item["hardest"]) ?? "",
            easierThanExpected: string(item["easier_than_expected"]) ?? "",
            createdAt: string(item["created_at"]),
            updatedAt: string(item["updated_at"])
        )
    }

    static func parseAutoInsightItem(_ item: [String: Any]) -> AutoInsightItem? {
        guard let id = string(item["id"]) else { return nil }
        let confidence = InsightConfidence(rawValue: string(item["confidence"]) ?? "medium") ?? .medium
        return AutoInsightItem(
            id: id,
            dateISO: string(item["date"]) ?? isoDate(from: Date()),
            type: string(item["type"]) ?? "pattern",
            text: string(item["insight_text"]) ?? "Инсайт собирается.",
            confidence: confidence,
            dataPoints: compactDisplayDataPoints(dictionary(item["data_points"])),
            createdAt: string(item["created_at"])
        )
    }

    static func monthInterval(containing dateISO: String) -> (from: String, to: String) {
        let base = date(from: dateISO) ?? Date()
        let calendar = Calendar.current
        let start = calendar.date(from: calendar.dateComponents([.year, .month], from: base)) ?? base
        let range = calendar.range(of: .day, in: .month, for: start) ?? 1..<29
        let end = calendar.date(byAdding: .day, value: range.count - 1, to: start) ?? start
        return (isoDate(from: start), isoDate(from: end))
    }

    static func isoDate(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }

    static func date(from iso: String) -> Date? {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: iso)
    }

    static func prettyDate(_ iso: String) -> String {
        guard let date = date(from: iso) else { return iso }
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("EEEEdMMMM")
        return formatter.string(from: date)
    }

    static func monthTitle(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("LLLL yyyy")
        return formatter.string(from: date)
    }

    static func dayNumber(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.dateFormat = "d"
        return formatter.string(from: date)
    }

    static func weekdaySymbol(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.dateFormat = "EE"
        return formatter.string(from: date)
    }

    static func dictionary(_ value: Any?) -> [String: Any] {
        value as? [String: Any] ?? [:]
    }

    static func array(_ value: Any?) -> [Any] {
        value as? [Any] ?? []
    }

    static func string(_ value: Any?) -> String? {
        if let value = value as? String {
            let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
            return trimmed.isEmpty ? nil : trimmed
        }
        if let number = value as? NSNumber {
            return number.stringValue
        }
        return nil
    }

    static func strings(_ value: Any?) -> [String] {
        if let array = value as? [String] {
            return array.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        }
        if let array = value as? [Any] {
            return array.compactMap(string)
        }
        return []
    }

    static func int(_ value: Any?) -> Int {
        optionalInt(value) ?? 0
    }

    static func optionalInt(_ value: Any?) -> Int? {
        if let value = value as? Int { return value }
        if let value = value as? Double { return Int(value) }
        if let value = value as? NSNumber { return value.intValue }
        if let value = value as? String { return Int(value) }
        return nil
    }

    static func bool(_ value: Any?) -> Bool {
        if let value = value as? Bool { return value }
        if let value = value as? NSNumber { return value.boolValue }
        if let value = value as? String {
            return ["true", "1", "yes"].contains(value.lowercased())
        }
        return false
    }

    static func compactDisplayDataPoints(_ payload: [String: Any]) -> [String: String] {
        var result: [String: String] = [:]
        let candidates: [(String, String)] = [
            ("days_reviewed", "Дней в анализе"),
            ("ritual_feedback_yes_days", "Собранных дней"),
            ("ritual_feedback_no_days", "Несобранных дней"),
            ("unclear_decision_days", "Неясных решений"),
            ("clear_decision_days", "Ясных решений"),
            ("dominant_focus", "Доминирующий фокус"),
            ("dominant_focus_count", "Повторов фокуса"),
            ("avg_mood", "Среднее состояние"),
            ("data_points_count", "Записей"),
            ("weekend_percentage", "Доля выходных"),
            ("total_entries", "Всего записей")
        ]

        for (key, title) in candidates {
            if let value = string(payload[key]) {
                result[title] = value
            } else if let value = optionalInt(payload[key]) {
                result[title] = "\(value)"
            }
        }

        return result
    }

    static func numerologyLine(from payload: [String: Any]) -> String {
        if let title = string(payload["title"]) {
            return title
        }
        if let value = optionalInt(payload["value"]) ?? optionalInt(payload["reduced_value"]) {
            return "Число \(value)"
        }
        return "Число дня"
    }

    static func energySubtitle(_ score: Int) -> String {
        switch score {
        case 0..<35: return "Ниже запланированной нагрузки — можно смягчить темп"
        case 35..<65: return "Береги темп — не разгоняйся"
        default: return "Сильный слот дня — используй осознанно"
        }
    }

    static func focusSubtitle(_ score: Int) -> String {
        switch score {
        case 0..<35: return "Меньше параллельных нитей"
        case 35..<65: return "Работай более короткими отрезками"
        default: return "Хорошие условия для глубины"
        }
    }

    static func balanceSubtitle(_ score: Int) -> String {
        switch score {
        case 0..<35: return "Береги границы"
        case 35..<65: return "Стабильность требует подпитки"
        default: return "Эмоциональная опора на месте"
        }
    }

    static func activityTitle(for key: String) -> String {
        switch key {
        case "goal": return "Цели"
        case "habits": return "Привычки"
        case "practice": return "Практики"
        case "state_phases": return "Чек-ины"
        case "daily_signals": return "Сигналы"
        case "ritual": return "Вечерний ритуал"
        case "diary": return "Дневник"
        case "asceticism": return "Аскезы"
        case "affirmation": return "Аффирмации"
        default: return key.capitalized
        }
    }

    static func accentHex(for slug: String) -> String {
        switch slug {
        case "love": return "#D26A8C"
        case "family": return "#2E8B7B"
        case "money": return "#A6804E"
        case "career": return "#E37A3F"
        default: return "#5B6F8F"
        }
    }

    static func fallbackRoute(for slug: String) -> String {
        switch slug {
        case "love":
            return "/questions/love"
        case "family":
            return "/journal"
        case "money", "career":
            return "/questions/money-career"
        default:
            return "/today"
        }
    }

    func readableError(_ error: Error) -> String {
        if let localized = error as? LocalizedError, let description = localized.errorDescription {
            return description
        }
        return error.localizedDescription
    }

    private func shouldSignOutAfterSessionRefreshFailure(_ error: Error) -> Bool {
        let message = readableError(error).lowercased()
        if message.contains("401")
            || message.contains("unauthorized")
            || message.contains("not authenticated")
            || message.contains("could not validate credentials")
            || message.contains("invalid token")
        {
            return true
        }
        return false
    }

    private func buildSessionWarningMessage(for error: Error) -> String {
        let base = "Сеть нестабильна: продолжаем с сохраненной сессией и локальными данными."
        if let last = lastSessionValidatedAt {
            return "\(base) Последняя успешная проверка входа: \(Self.prettyDateTime(last))."
        }
        let details = readableError(error)
        if details.isEmpty {
            return "\(base) Учетные данные сохранены на устройстве."
        }
        return "\(base) \(details)"
    }

    private static func prettyDateTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("d MMM, HH:mm")
        return formatter.string(from: date)
    }
}

extension TodayFlowStore {
    /// Паритет с `getWeekStart` (`frontend/src/components/today/todayPageUtils.ts`): начало недели — понедельник, локальный календарь.
    static func weekStartMonday(fromLocalISO iso: String) -> String {
        guard let base = date(from: iso) else { return iso }
        let cal = Calendar.current
        let weekday = cal.component(.weekday, from: base)
        let daysFromMonday: Int
        switch weekday {
        case 1: daysFromMonday = -6
        default: daysFromMonday = 2 - weekday
        }
        let startOfDay = cal.startOfDay(for: base)
        guard let monday = cal.date(byAdding: .day, value: daysFromMonday, to: startOfDay) else { return iso }
        return isoDate(from: monday)
    }

    /// Паритет с `monthAnchorIso` (`frontend/src/app/tracking/calendar/calendarHeatmapModel.ts`).
    static func monthAnchorIso(_ iso: String) -> String {
        let parts = iso.split(separator: "-")
        guard parts.count >= 2, let y = Int(parts[0]), let m = Int(parts[1]), (1...12).contains(m) else { return iso }
        return String(format: "%04d-%02d-01", y, m)
    }
}
