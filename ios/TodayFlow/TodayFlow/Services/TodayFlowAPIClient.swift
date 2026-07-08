import Foundation

struct TodayFlowAPIClient {
    static let shared = TodayFlowAPIClient()

    /// Как у веб-клиента: бэкенд отдаёт тексты по `Accept-Language` (en | ru).
    private func preferredAPILanguageCode() -> String {
        if let preferred = Bundle.main.preferredLocalizations.first?.lowercased(), preferred.hasPrefix("ru") {
            return "ru"
        }
        if let code = Locale.current.language.languageCode?.identifier.lowercased(), code == "ru" {
            return "ru"
        }
        return "en"
    }

    private func applyAcceptLanguage(to request: inout URLRequest) {
        let code = preferredAPILanguageCode()
        if code == "ru" {
            request.setValue("ru,en;q=0.9", forHTTPHeaderField: "Accept-Language")
        } else {
            request.setValue("en,ru;q=0.9", forHTTPHeaderField: "Accept-Language")
        }
    }

    /// Тот же origin, что и у `TarotClient` / трекера (`Info.plist` → `API_BASE_URL`).
    private var backendBaseURL: URL { AppConfig.apiBaseURL }
    /// Онбординг `POST /chart` — см. `ASTRO_SERVICE_URL` в Info.plist.
    private var astroBaseURL: URL { AppConfig.astroServiceURL }

    private let session: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 90
        return URLSession(configuration: configuration)
    }()

    func signUp(email: String, password: String) async throws -> AuthSession {
        let payload = AuthCredentialsRequest(email: email, password: password)
        let response: AuthTokenResponse = try await send(
            path: "auth/signup",
            method: "POST",
            body: payload
        )
        return try await fetchCurrentUser(token: response.token)
    }

    func signIn(email: String, password: String) async throws -> AuthSession {
        let payload = AuthCredentialsRequest(email: email, password: password)
        let response: AuthTokenResponse = try await send(
            path: "auth/login",
            method: "POST",
            body: payload
        )
        return try await fetchCurrentUser(token: response.token)
    }

    func fetchCurrentUser(token: String) async throws -> AuthSession {
        let response: AuthMeResponse = try await send(
            path: "auth/me",
            token: token
        )
        return AuthSession(
            token: token,
            userID: response.user_id,
            email: response.email,
            isPaid: response.is_paid,
            hasLiteReport: response.has_lite_report,
            hasFullReport: response.has_full_report,
            insightDepthTier: response.insight_depth_tier
        )
    }

    func fetchTodayCycle(token: String, targetDate: Date = .now) async throws -> TodayCycle {
        var components = URLComponents(url: backendBaseURL.appending(path: "today"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "target_date", value: targetDate.apiDateString)
        ]
        return try await send(url: components.url!, token: token, timeout: 30)
    }

    func fetchTodayContract(token: String, targetDate: Date = .now) async throws -> TodayContractV1 {
        var components = URLComponents(url: backendBaseURL.appending(path: "today/contract"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "target_date", value: targetDate.apiDateString)
        ]
        return try await send(url: components.url!, token: token, timeout: 45)
    }

    func fetchFusionIndex(token: String, targetDate: Date = .now) async throws -> FusionIndex {
        try await send(
            path: "tracking/fusion/\(targetDate.apiDateString)",
            token: token
        )
    }

    func fetchFusionHistory(token: String, days: Int = 7, endingAt targetDate: Date = .now) async -> [FusionIndex] {
        let calendar = Calendar.current
        let dates = (0..<days).compactMap { offset in
            calendar.date(byAdding: .day, value: -offset, to: targetDate)
        }

        return await withTaskGroup(of: FusionIndex?.self) { group in
            for date in dates {
                group.addTask {
                    try? await fetchFusionIndex(token: token, targetDate: date)
                }
            }

            var items: [FusionIndex] = []
            for await item in group {
                if let item {
                    items.append(item)
                }
            }
            return items.sorted { $0.date < $1.date }
        }
    }

    func saveMorningIntention(token: String, date: String, intention: String) async throws -> TodayDayConnection {
        let payload = DayConnectionWriteRequest(
            morning_intention: intention,
            morning_focus: nil,
            evening_reflection: nil,
            evening_observations: nil,
            connection_thread: nil,
            morning_completed: true,
            day_completed: nil,
            evening_completed: nil
        )
        return try await send(
            path: "day-connection/\(date)",
            method: "POST",
            body: payload,
            token: token
        )
    }

    func savePulseCheck(token: String, payload: PulseCheckPayload) async throws -> TodayTracker {
        try await send(
            path: "tracking/progress",
            method: "POST",
            body: ProgressTrackerWriteRequest(
                date: payload.date,
                asceticism_id: nil,
                affirmation_id: nil,
                completed: true,
                state: payload.state,
                state_scale: payload.stateScale,
                note: payload.note
            ),
            token: token
        )
    }

    func saveJournalEntry(token: String, date: String, type: String, content: String) async throws -> TodayJournalEntry {
        try await send(
            path: "journal/entries",
            method: "POST",
            body: JournalEntryWriteRequest(
                type: type,
                content: content,
                practice_id: nil,
                tarot_card_id: nil,
                pattern_axis_id: nil,
                day: date
            ),
            token: token
        )
    }

    func saveEveningReflection(
        token: String,
        date: String,
        reflection: String?,
        observations: TodayEveningObservationsInput,
        markComplete: Bool
    ) async throws -> TodayDayConnection {
        let payload = DayConnectionWriteRequest(
            morning_intention: nil,
            morning_focus: nil,
            evening_reflection: reflection,
            evening_observations: observations.asDictionary,
            connection_thread: nil,
            morning_completed: nil,
            day_completed: true,
            evening_completed: markComplete
        )
        return try await send(
            path: "day-connection/\(date)",
            method: "POST",
            body: payload,
            token: token
        )
    }

    func requestPasswordReset(email: String) async throws -> String {
        let payload = ForgotPasswordRequest(email: email)
        let response: PasswordActionResponse = try await send(
            path: "auth/forgot-password",
            method: "POST",
            body: payload
        )
        return response.message
    }

    func fetchAccountSettings(token: String) async throws -> AccountSettings {
        try await send(
            path: "account/profile",
            token: token
        )
    }

    func fetchCoreProfile(token: String, astroProfileID: Int? = nil) async throws -> CoreProfileResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "account/core-profile"), resolvingAgainstBaseURL: false)!
        if let astroProfileID {
            components.queryItems = [URLQueryItem(name: "astro_profile_id", value: "\(astroProfileID)")]
        }
        return try await send(url: components.url!, token: token, timeout: 20)
    }

    func fetchProfileSummary(token: String) async throws -> ProfileSummaryResponse {
        try await send(
            path: "account/profile-summary",
            token: token
        )
    }

    func fetchProfileBuildStatus(token: String) async throws -> ProfileBuildStatusResponse {
        try await send(
            path: "account/profile-build-status",
            token: token
        )
    }

    func fetchCompactUserModel(token: String, localDate: String? = nil) async throws -> CompactUserModelResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "account/compact-user-model"), resolvingAgainstBaseURL: false)!
        if let localDate, !localDate.isEmpty {
            components.queryItems = [URLQueryItem(name: "local_date", value: localDate)]
        }
        return try await send(url: components.url!, token: token, timeout: 16)
    }

    func fetchCompactUserModelConfidenceHistory(
        token: String,
        localDate: String? = nil,
        windowDays: Int = 90
    ) async throws -> CompactUserModelConfidenceHistoryResponse {
        var components = URLComponents(
            url: backendBaseURL.appending(path: "account/compact-user-model/confidence-history"),
            resolvingAgainstBaseURL: false
        )!
        var items: [URLQueryItem] = [URLQueryItem(name: "window_days", value: String(windowDays))]
        if let localDate, !localDate.isEmpty {
            items.append(URLQueryItem(name: "local_date", value: localDate))
        }
        components.queryItems = items
        return try await send(url: components.url!, token: token, timeout: 16)
    }

    func updateAccountSettings(token: String, payload: AccountSettingsUpdate) async throws -> AccountSettings {
        try await send(
            path: "account/profile",
            method: "PUT",
            body: payload,
            token: token
        )
    }

    /// DE-8: частичный PUT — только `today_narrative_depth_level` (паритет веб `putJson` с одним полем).
    func patchTodayNarrativeDepthLevel(token: String, level: String) async throws -> AccountSettings {
        struct Body: Encodable {
            let today_narrative_depth_level: String
        }
        return try await send(
            path: "account/profile",
            method: "PUT",
            body: Body(today_narrative_depth_level: level),
            token: token
        )
    }

    func listAstroProfiles(token: String) async throws -> [StoredAstroProfile] {
        let response: AstroProfilesResponse = try await send(
            path: "account/astro-data",
            token: token
        )
        return response.profiles
    }

    /// Повторная отправка данных рождения на сервер (если онбординг прошёл без успешного core-setup).
    func pushCoreSetupToServer(draft: BirthProfileDraft, session: AuthSession) async throws {
        _ = try await upsertCoreSetup(for: draft, session: session)
    }

    func fetchNatalChart(token: String, astroProfileID: Int? = nil) async throws -> NatalChartPreview {
        var components = URLComponents(url: backendBaseURL.appending(path: "natal-chart/"), resolvingAgainstBaseURL: false)!
        var queryItems = [URLQueryItem(name: "include_interpretations", value: "true")]
        if let astroProfileID {
            queryItems.append(URLQueryItem(name: "astro_profile_id", value: "\(astroProfileID)"))
        }
        components.queryItems = queryItems
        return try await send(url: components.url!, token: token, timeout: 30)
    }

    func fetchTodayNarrative(
        token: String,
        targetDate: String,
        surface: TodayNarrativeSurface,
        parentGenerationID: Int? = nil,
        ritualContext: TodayNarrativeRitualContextPayload? = nil,
        /// Если `nil`, поле не отправляется — сервер берёт `user_settings.today_narrative_depth_level` (DE-8).
        depthLevel: String? = nil
    ) async throws -> TodayNarrativeResponse {
        try await send(
            path: "today/narrative",
            method: "POST",
            body: TodayNarrativeRequest(
                target_date: targetDate,
                surface: surface.rawValue,
                parent_generation_id: parentGenerationID,
                depth_level: depthLevel,
                policy_version: "clean-info-v1",
                voice_profile: "live-clean-supportive-v1",
                ritual_context: ritualContext
            ),
            token: token,
            timeout: surface == .guide ? 20 : 16
        )
    }

    func answerQuestion(token: String?, question: String, preferredLane: String?) async throws -> QuestionAnswerResult {
        let payload = QuestionAnswerRequest(
            question: question,
            preferred_lane: preferredLane
        )
        return try await send(
            path: "questions/answer",
            method: "POST",
            body: payload,
            token: token
        )
    }

    /// Guidance: разбор после того, как пользователь открыл все карты расклада.
    func guidanceReading(token: String, payload: GuidanceReadingAPIRequestBody) async throws -> GuidanceReadingResult {
        var request = URLRequest(url: backendBaseURL.appending(path: "questions/reading"))
        request.httpMethod = "POST"
        applyAcceptLanguage(to: &request)
        request.timeoutInterval = 55
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.httpBody = try JSONEncoder().encode(payload)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: request.url!)
        }
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(GuidanceReadingResult.self, from: data)
    }

    /// Одна уточняющая карта к успешному `POST /questions/reading` (не больше одного раза на parent log).
    func guidanceReadingClarify(token: String, payload: GuidanceClarifyAPIRequestBody) async throws -> GuidanceReadingResult {
        var request = URLRequest(url: backendBaseURL.appending(path: "questions/reading/clarify"))
        request.httpMethod = "POST"
        applyAcceptLanguage(to: &request)
        request.timeoutInterval = 55
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.httpBody = try JSONEncoder().encode(payload)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: request.url!)
        }
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(GuidanceReadingResult.self, from: data)
    }

    func fetchQuestionsHistory(token: String, limit: Int = 60) async throws -> QuestionsHistoryResponseDTO {
        var components = URLComponents(url: backendBaseURL.appending(path: "questions/history"), resolvingAgainstBaseURL: false)!
        let clamped = min(max(limit, 1), 100)
        components.queryItems = [URLQueryItem(name: "limit", value: "\(clamped)")]
        guard let url = components.url else { throw APIError.invalidResponse }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 25
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: url)
        }
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(QuestionsHistoryResponseDTO.self, from: data)
    }

    func submitLearningFeedback(token: String, body: LearningFeedbackRequestBody) async throws {
        var request = URLRequest(url: backendBaseURL.appending(path: "learning/feedback"))
        request.httpMethod = "POST"
        request.timeoutInterval = 20
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.httpBody = try JSONEncoder().encode(body)
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: request.url!)
        }
        try validate(response: response, data: data)
        _ = data
    }

    func createAstroProfile(token: String, input: AstroProfileInput) async throws -> AstroProfileMutationAPIResponse {
        try await send(
            path: "account/astro-data",
            method: "POST",
            body: AstroProfileCreateRequest(
                label: input.label,
                relation: input.relation,
                birth_date: input.birthDate,
                birth_time: input.timeUnknown ? nil : input.birthTime,
                time_unknown: input.timeUnknown,
                location_name: input.locationName,
                latitude: input.latitude,
                longitude: input.longitude,
                is_primary: input.isPrimary
            ),
            token: token
        )
    }

    func updateAstroProfile(token: String, profileID: Int, payload: AstroProfileUpdatePayload) async throws -> AstroProfileMutationAPIResponse {
        try await send(
            path: "account/astro-data/\(profileID)",
            method: "PUT",
            body: payload,
            token: token
        )
    }

    func deleteAstroProfile(token: String, profileID: Int) async throws {
        let _: DeleteStatusResponse = try await send(
            path: "account/astro-data/\(profileID)",
            method: "DELETE",
            token: token
        )
    }

    func setPrimaryAstroProfile(token: String, profileID: Int) async throws -> AstroProfileMutationAPIResponse {
        try await send(
            path: "account/astro-data/\(profileID)/primary",
            method: "POST",
            body: EmptyRequest(),
            token: token
        )
    }

    func compareCompatibility(
        token: String,
        profileID1: Int,
        profileID2: Int,
        relationMode: String,
        type: CompatibilityRequestType,
        formatID: String? = nil
    ) async throws -> CompatibilityComparisonResponse {
        let path = switch type {
        case .quick:
            "compatibility/compare"
        case .deep:
            "compatibility/synastry"
        }

        return try await send(
            path: path,
            method: "POST",
            body: CompatibilityRequestBody(
                profile_id_1: profileID1,
                profile_id_2: profileID2,
                relation_mode: relationMode,
                format_id: formatID
            ),
            token: token,
            timeout: type == .deep ? 30 : 12
        )
    }

    func postMeaningEvents(token: String, events: [MeaningEventInput]) async throws -> MeaningEventsResponse {
        try await send(
            path: "meaning/events",
            method: "POST",
            body: MeaningEventsRequest(events: events),
            token: token
        )
    }

    func fetchMeaningRings(token: String, windowDays: Int = 28) async throws -> MeaningRingsResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "meaning/rings"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "window_days", value: "\(windowDays)")
        ]
        return try await send(url: components.url!, token: token, timeout: 12)
    }

    /// Публичный расчёт по двум солнечным знакам (тот же контракт, что у веба `/compatibility/signs`).
    func fetchSignCompatibility(fromSign: String, toSign: String, relationshipContext: String? = nil) async throws -> SignCompatibilityAPIResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "compatibility/signs"), resolvingAgainstBaseURL: false)!
        var items: [URLQueryItem] = [
            URLQueryItem(name: "from", value: fromSign),
            URLQueryItem(name: "to", value: toSign),
            URLQueryItem(name: "include_personalized", value: "true"),
        ]
        if let relationshipContext, !relationshipContext.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            items.append(URLQueryItem(name: "relationship_context", value: relationshipContext))
        }
        components.queryItems = items
        guard let url = components.url else {
            throw APIError.invalidResponse
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        applyAcceptLanguage(to: &request)
        let token = AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
        if !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: url)
        }
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(SignCompatibilityAPIResponse.self, from: data)
    }

    /// Encyclopedia hub catalog (categories, readings, series) — parity with web `/compatibility`.
    func fetchCompatibilityEncyclopedia(locale: String? = nil) async throws -> CompatibilityEncyclopediaResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "compatibility/encyclopedia"), resolvingAgainstBaseURL: false)!
        if let locale, !locale.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            components.queryItems = [URLQueryItem(name: "locale", value: locale)]
        }
        guard let url = components.url else {
            throw APIError.invalidResponse
        }
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        applyAcceptLanguage(to: &request)
        let token = AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
        if !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        let (data, response) = try await session.data(for: request)
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(CompatibilityEncyclopediaResponse.self, from: data)
    }

    /// POST /compatibility/dynamics — encyclopedia-aware pair dynamics (parity with web analyze).
    func postCompatibilityDynamics(body: CompatibilityDynamicsRequestBody) async throws -> SignCompatibilityAPIResponse {
        var request = URLRequest(url: backendBaseURL.appending(path: "compatibility/dynamics"))
        request.httpMethod = "POST"
        applyAcceptLanguage(to: &request)
        request.timeoutInterval = body.generation == "llm" ? 30 : 12
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let token = AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
        if !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.httpBody = try JSONEncoder().encode(body)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: request.url!)
        }
        try validate(response: response, data: data)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(SignCompatibilityAPIResponse.self, from: data)
    }

    func resetPassword(token: String, newPassword: String) async throws -> String {
        let payload = ResetPasswordRequest(token: token, new_password: newPassword)
        let response: PasswordActionResponse = try await send(
            path: "auth/reset-password",
            method: "POST",
            body: payload
        )
        return response.message
    }

    func changePassword(token: String, currentPassword: String, newPassword: String) async throws -> String {
        let payload = ChangePasswordRequest(
            current_password: currentPassword,
            new_password: newPassword
        )
        let response: PasswordActionResponse = try await send(
            path: "auth/change-password",
            method: "POST",
            body: payload,
            token: token
        )
        return response.message
    }

    func bootstrap(from draft: BirthProfileDraft, session: AuthSession?) async throws -> TodayFlowBootstrapPayload {
        async let chartTask = fetchChart(for: draft)
        async let dayFlowTask = fetchDayFlow(for: .now, token: session?.token)

        let chart = try await chartTask
        let dayFlow = try await dayFlowTask
        let profile = draft.resolved(using: chart)

        // Создаёт AstroProfile в БД; без этого GET /natal-chart даёт 404 (noProfile).
        if let session {
            _ = try await upsertCoreSetup(for: draft, session: session)
        }

        return TodayFlowBootstrapPayload(
            profile: profile,
            dailyFocus: DailyFocus.personalized(for: profile, dayFlow: dayFlow),
            rituals: Ritual.personalized(for: profile, dayFlow: dayFlow),
            todayCycle: nil,
            fusionIndex: nil,
            fusionHistory: []
        )
    }

    func refreshDayFlow(for profile: BirthProfile, session: AuthSession?) async throws -> (dailyFocus: DailyFocus, rituals: [Ritual], todayCycle: TodayCycle?, fusionIndex: FusionIndex?, fusionHistory: [FusionIndex]) {
        let dayFlow = try await fetchDayFlow(for: .now, token: session?.token)
        let todayCycle = try await fetchTodayCycleIfAvailable(session: session)
        let fusionHistory = try await fetchFusionHistoryIfAvailable(session: session)
        return (
            dailyFocus: DailyFocus.personalized(for: profile, dayFlow: dayFlow),
            rituals: Ritual.personalized(for: profile, dayFlow: dayFlow),
            todayCycle: todayCycle,
            fusionIndex: fusionHistory.currentFusion,
            fusionHistory: fusionHistory
        )
    }

    func fetchLocationSuggestions(query: String) async throws -> [GeocodeSuggestion] {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.count >= 2 else { return [] }

        var components = URLComponents(url: backendBaseURL.appending(path: "astro/geocode/suggest"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "q", value: trimmed),
            URLQueryItem(name: "limit", value: "6")
        ]

        return try await send(url: components.url!)
    }

    private func fetchChart(for draft: BirthProfileDraft) async throws -> AstroChartResponse {
        let payload = AstroChartRequest(
            birth: AstroBirthData(
                date: draft.apiBirthDate,
                time: draft.knowsBirthTime ? draft.apiBirthTime : nil,
                location: draft.birthPlace.trimmingCharacters(in: .whitespacesAndNewlines)
            ),
            coordinates: draft.selectedCoordinates.map {
                AstroCoordinates(latitude: $0.latitude, longitude: $0.longitude)
            }
        )

        return try await send(
            url: astroBaseURL.appending(path: "chart"),
            method: "POST",
            body: payload,
            timeout: 60
        )
    }

    private func fetchDayFlow(for targetDate: Date, token: String?) async throws -> DayFlowAPIResponse {
        var components = URLComponents(url: backendBaseURL.appending(path: "day-flow/"), resolvingAgainstBaseURL: false)!
        components.queryItems = [
            URLQueryItem(name: "target_date", value: targetDate.apiDateString),
            URLQueryItem(name: "needs", value: "general"),
            URLQueryItem(name: "fast", value: "true")
        ]

        return try await send(url: components.url!, token: token, timeout: 30)
    }

    private func fetchTodayCycleIfAvailable(session: AuthSession?) async throws -> TodayCycle? {
        guard let token = session?.token else { return nil }
        return try await fetchTodayCycle(token: token)
    }

    private func fetchFusionIfAvailable(session: AuthSession?) async throws -> FusionIndex? {
        guard let token = session?.token else { return nil }
        return try await fetchFusionIndex(token: token)
    }

    private func fetchFusionHistoryIfAvailable(session: AuthSession?) async throws -> [FusionIndex] {
        guard let token = session?.token else { return [] }
        return await fetchFusionHistory(token: token)
    }

    private func upsertCoreSetup(for draft: BirthProfileDraft, session: AuthSession?) async throws -> CoreSetupResponse? {
        guard let session else { return nil }

        let payload = CoreSetupRequest(
            first_name: draft.firstName.trimmingCharacters(in: .whitespacesAndNewlines),
            last_name: nil,
            label: draft.firstName.trimmingCharacters(in: .whitespacesAndNewlines),
            birth_date: draft.apiBirthDate,
            birth_time: draft.knowsBirthTime ? draft.apiBirthTimeWithSeconds : nil,
            time_unknown: !draft.knowsBirthTime,
            timezone_offset_minutes: draft.timezoneOffsetMinutes,
            timezone_name: draft.timezone,
            location_name: draft.birthPlace.trimmingCharacters(in: .whitespacesAndNewlines),
            latitude: draft.selectedCoordinates?.latitude,
            longitude: draft.selectedCoordinates?.longitude,
            notes: nil,
            gender: draft.normalizedGenderForAPI
        )

        return try await send(
            path: "account/core-setup",
            method: "POST",
            body: payload,
            token: session.token
        )
    }

    private func send<Response: Decodable>(
        path: String,
        method: String = "GET",
        token: String? = nil
    ) async throws -> Response {
        try await send(
            url: backendBaseURL.appending(path: path),
            method: method,
            token: token
        )
    }

    private func send<RequestBody: Encodable, Response: Decodable>(
        path: String,
        method: String,
        body: RequestBody,
        token: String? = nil
    ) async throws -> Response {
        try await send(
            url: backendBaseURL.appending(path: path),
            method: method,
            body: body,
            token: token
        )
    }

    private func send<RequestBody: Encodable, Response: Decodable>(
        path: String,
        method: String,
        body: RequestBody,
        token: String? = nil,
        timeout: TimeInterval? = nil
    ) async throws -> Response {
        try await send(
            url: backendBaseURL.appending(path: path),
            method: method,
            body: body,
            token: token,
            timeout: timeout
        )
    }

    private func send<Response: Decodable>(
        url: URL,
        method: String = "GET",
        token: String? = nil,
        timeout: TimeInterval? = nil
    ) async throws -> Response {
        var request = URLRequest(url: url)
        request.httpMethod = method
        applyAcceptLanguage(to: &request)
        if let timeout {
            request.timeoutInterval = timeout
        }
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: url)
        }
        try validate(response: response, data: data)
        return try JSONDecoder().decode(Response.self, from: data)
    }

    private func send<RequestBody: Encodable, Response: Decodable>(
        url: URL,
        method: String,
        body: RequestBody,
        token: String? = nil,
        timeout: TimeInterval? = nil
    ) async throws -> Response {
        var request = URLRequest(url: url)
        request.httpMethod = method
        applyAcceptLanguage(to: &request)
        if let timeout {
            request.timeoutInterval = timeout
        }
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.httpBody = try JSONEncoder().encode(body)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            throw networkAwareError(error, url: url)
        }
        try validate(response: response, data: data)
        return try JSONDecoder().decode(Response.self, from: data)
    }

    private func networkAwareError(_ error: Error, url: URL) -> APIError {
        guard let urlError = error as? URLError else {
            return .server(error.localizedDescription)
        }

        let hostLine = url.host ?? url.absoluteString
        switch urlError.code {
        case .notConnectedToInternet:
            return .server("Нет интернета. Приложение не может подключиться к \(hostLine).")
        case .cannotConnectToHost, .cannotFindHost:
            return .server("Не удаётся подключиться к \(hostLine). Проверь API/astro host в Settings.")
        case .timedOut:
            return .server("Сервер \(hostLine) отвечает слишком долго. Проверь, жив ли backend и доступен ли этот host.")
        default:
            return .server("Сеть недоступна для \(hostLine): \(urlError.localizedDescription)")
        }
    }

    private func validate(response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            let message = parsedErrorMessage(from: data) ?? "Unexpected API error"
            if httpResponse.statusCode == 401 {
                throw APIError.server("401 Unauthorized: \(message)")
            }
            throw APIError.server(message)
        }
    }

    private func parsedErrorMessage(from data: Data) -> String? {
        if let apiError = try? JSONDecoder().decode(APIErrorEnvelope.self, from: data) {
            return apiError.detail ?? apiError.message
        }

        guard let raw = String(data: data, encoding: .utf8)?
            .trimmingCharacters(in: .whitespacesAndNewlines),
              !raw.isEmpty else {
            return nil
        }

        return raw
    }
}

enum APIError: LocalizedError {
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Server returned an invalid response."
        case let .server(message):
            return message
        }
    }
}

private struct AstroChartRequest: Encodable {
    let birth: AstroBirthData
    let coordinates: AstroCoordinates?
}

private struct AuthCredentialsRequest: Encodable {
    let email: String
    let password: String
}

private struct QuestionAnswerRequest: Encodable {
    let question: String
    let preferred_lane: String?
}

/// Тело `POST /questions/reading` (ключи как у бэкенда).
struct GuidanceReadingAPIRequestBody: Encodable {
    let question: String
    let spread_id: String
    let selected_cards: [GuidanceSelectedCardBody]
    let hub_lane_hint: String?
    let topic: String?
    let desired_outcome: String?
    let relationship_context: String?
    let intimacy_focus: String?
    let user_intent: String?
    let requested_depth: String?
    let today_context_summary: String?
}

struct GuidanceClarifyAPIRequestBody: Encodable {
    let parent_generation_log_id: Int
    let clarification_goal: String
    let selected_cards: [GuidanceSelectedCardBody]
}

struct GuidanceSelectedCardBody: Encodable {
    let card_id: Int
    let orientation: String
}

struct LearningFeedbackRequestBody: Encodable {
    let generation_log_id: Int
    let signal: String
    let note: String?
    let metadata: LearningFeedbackMetadataPayload?

    init(generation_log_id: Int, signal: String, note: String? = nil, metadata: LearningFeedbackMetadataPayload?) {
        self.generation_log_id = generation_log_id
        self.signal = signal
        self.note = note
        self.metadata = metadata
    }

    enum CodingKeys: String, CodingKey {
        case generation_log_id
        case signal
        case note
        case metadata
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(generation_log_id, forKey: .generation_log_id)
        try c.encode(signal, forKey: .signal)
        try c.encodeIfPresent(note, forKey: .note)
        try c.encodeIfPresent(metadata, forKey: .metadata)
    }
}

/// Поля опциональны: в теле JSON попадают только ненулевые ключи (паритет с веб `postJson` для today и guidance).
struct LearningFeedbackMetadataPayload: Encodable {
    let source_surface: String?
    let resonance: String?
    let spread_id: String?
    let lane: String?
    let comment: String?
    let match_chips: [String]?
    let question: String?
    let preferred_lane: String?
    /// Эхо среза с `POST /today/narrative` для того же `generation_log_id`.
    let profile_selector: [String: JSONValue]?
    /// Паритет с веб `today/page.tsx` для сигналов «Сегодня».
    let day_key: String?
    let surface: String?
    let evening_completed: Bool?

    init(
        source_surface: String? = nil,
        resonance: String? = nil,
        spread_id: String? = nil,
        lane: String? = nil,
        comment: String? = nil,
        match_chips: [String]? = nil,
        question: String? = nil,
        preferred_lane: String? = nil,
        profile_selector: [String: JSONValue]? = nil,
        day_key: String? = nil,
        surface: String? = nil,
        evening_completed: Bool? = nil
    ) {
        self.source_surface = source_surface
        self.resonance = resonance
        self.spread_id = spread_id
        self.lane = lane
        self.comment = comment
        self.match_chips = match_chips
        self.question = question
        self.preferred_lane = preferred_lane
        self.profile_selector = profile_selector
        self.day_key = day_key
        self.surface = surface
        self.evening_completed = evening_completed
    }

    enum CodingKeys: String, CodingKey {
        case source_surface
        case resonance
        case spread_id
        case lane
        case comment
        case match_chips
        case question
        case preferred_lane
        case profile_selector
        case day_key
        case surface
        case evening_completed
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encodeIfPresent(source_surface, forKey: .source_surface)
        try c.encodeIfPresent(resonance, forKey: .resonance)
        try c.encodeIfPresent(spread_id, forKey: .spread_id)
        try c.encodeIfPresent(lane, forKey: .lane)
        try c.encodeIfPresent(comment, forKey: .comment)
        try c.encodeIfPresent(match_chips, forKey: .match_chips)
        try c.encodeIfPresent(question, forKey: .question)
        try c.encodeIfPresent(preferred_lane, forKey: .preferred_lane)
        try c.encodeIfPresent(profile_selector, forKey: .profile_selector)
        try c.encodeIfPresent(day_key, forKey: .day_key)
        try c.encodeIfPresent(surface, forKey: .surface)
        try c.encodeIfPresent(evening_completed, forKey: .evening_completed)
    }
}

struct TodayNarrativeRitualContextPayload: Encodable {
    let tarot_main_id: Int?
    let tarot_name_ru: String?
    let numerology_value: String?
    let mood: String?
    /// id чипа «тема в голове» — в intent на бэке.
    let head_topic: String?
    let day_events: [String]
}

private struct TodayNarrativeRequest: Encodable {
    let target_date: String
    let surface: String
    let parent_generation_id: Int?
    /// DE-8: quick | normal | deep. `nil` — не кодировать ключ; сервер использует настройку аккаунта.
    let depth_level: String?
    let policy_version: String
    let voice_profile: String
    let ritual_context: TodayNarrativeRitualContextPayload?

    enum CodingKeys: String, CodingKey {
        case target_date
        case surface
        case parent_generation_id
        case depth_level
        case policy_version
        case voice_profile
        case ritual_context
    }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        try c.encode(target_date, forKey: .target_date)
        try c.encode(surface, forKey: .surface)
        try c.encodeIfPresent(parent_generation_id, forKey: .parent_generation_id)
        try c.encodeIfPresent(depth_level, forKey: .depth_level)
        try c.encode(policy_version, forKey: .policy_version)
        try c.encode(voice_profile, forKey: .voice_profile)
        try c.encodeIfPresent(ritual_context, forKey: .ritual_context)
    }
}

enum CompatibilityRequestType {
    case quick
    case deep
}

private struct CompatibilityRequestBody: Encodable {
    let profile_id_1: Int
    let profile_id_2: Int
    let relation_mode: String
    let format_id: String?
}

struct CompatibilityDynamicsRequestBody: Encodable {
    let mode: String
    let from_sign: String?
    let to_sign: String?
    let relationship_context: String?
    let generation: String
    let name_1: String?
    let name_2: String?
    let birth_date_1: String?
    let birth_date_2: String?
    let include_personalized: Bool
    let locale: String?
    let topic_id: String?
    let reading_id: String?
    let series_id: String?
    let block_feedback: [String: String]?
}

private struct AstroProfileCreateRequest: Encodable {
    let label: String
    let relation: String
    let birth_date: String
    let birth_time: String?
    let time_unknown: Bool
    let location_name: String
    let latitude: Double?
    let longitude: Double?
    let is_primary: Bool
}

private struct DeleteStatusResponse: Decodable {
    let status: String
}

private struct EmptyRequest: Encodable {}

private struct ForgotPasswordRequest: Encodable {
    let email: String
}

struct PulseCheckPayload {
    let date: String
    let state: String?
    let stateScale: Int?
    let note: String?
}

struct TodayEveningObservationsInput {
    let noticed: String
    let hardest: String
    let easierThanExpected: String

    var asDictionary: [String: String] {
        var result: [String: String] = [:]
        if !noticed.isEmpty {
            result["noticed"] = noticed
        }
        if !hardest.isEmpty {
            result["hardest"] = hardest
        }
        if !easierThanExpected.isEmpty {
            result["easier_than_expected"] = easierThanExpected
        }
        return result
    }
}

private struct ResetPasswordRequest: Encodable {
    let token: String
    let new_password: String
}

private struct ChangePasswordRequest: Encodable {
    let current_password: String
    let new_password: String
}

private struct DayConnectionWriteRequest: Encodable {
    let morning_intention: String?
    let morning_focus: String?
    let evening_reflection: String?
    let evening_observations: [String: String]?
    let connection_thread: String?
    let morning_completed: Bool?
    let day_completed: Bool?
    let evening_completed: Bool?
}

private struct ProgressTrackerWriteRequest: Encodable {
    let date: String
    let asceticism_id: String?
    let affirmation_id: String?
    let completed: Bool
    let state: String?
    let state_scale: Int?
    let note: String?
}

private struct JournalEntryWriteRequest: Encodable {
    let type: String
    let content: String
    let practice_id: String?
    let tarot_card_id: String?
    let pattern_axis_id: String?
    let day: String?
}

private struct CoreSetupRequest: Encodable {
    let first_name: String
    let last_name: String?
    let label: String
    let birth_date: String
    let birth_time: String?
    let time_unknown: Bool
    let timezone_offset_minutes: Int?
    let timezone_name: String?
    let location_name: String
    let latitude: Double?
    let longitude: Double?
    let notes: String?
    let gender: String
}

private struct AuthTokenResponse: Decodable {
    let user_id: Int
    let email: String
    let token: String
    let is_paid: Bool?
}

private struct AuthMeResponse: Decodable {
    let user_id: Int
    let email: String
    let is_admin: Bool
    let is_paid: Bool
    let has_lite_report: Bool
    let has_full_report: Bool
    let insight_depth_tier: String?
}

private struct PasswordActionResponse: Decodable {
    let message: String
}

private struct APIErrorEnvelope: Decodable {
    let detail: String?
    let message: String?
}

private struct CoreSetupResponse: Decodable {
    let status: String
}

private struct AstroBirthData: Encodable {
    let date: String
    let time: String?
    let location: String
}

private struct AstroCoordinates: Encodable {
    let latitude: Double
    let longitude: Double
}

struct AstroChartResponse: Decodable {
    let mode: String
    let positions: [AstroPosition]
}

struct GeocodeSuggestion: Decodable, Identifiable, Equatable {
    var id: String { "\(name)|\(country)|\(latitude)|\(longitude)" }

    let name: String
    let local_name: String?
    let display_name: String?
    let country: String
    let latitude: Double
    let longitude: Double

    var primaryLabel: String {
        display_name ?? "\(name), \(country)"
    }
}

struct AstroPosition: Decodable {
    let body: String
    let sign: String
}

struct DayFlowAPIResponse: Decodable {
    let date: String
    let affirmations: [Affirmation]
    let practice: Practice?
    let numerology: Numerology?
    let consistency: Consistency?
}

struct Affirmation: Decodable {
    let id: String?
    let text: String
}

struct Practice: Decodable {
    let id: String?
    let title: String?
    let description: String?
    let duration_minutes: Int?
}

struct Numerology: Decodable {
    let dayNumber: Int?
    let title: String?
    let summary: String?
    let meaning: String?
    let whatToDo: String?
    let whatToAvoid: String?
}

struct Consistency: Decodable {
    let do_focus: String?
    let avoid_focus: String?
}
