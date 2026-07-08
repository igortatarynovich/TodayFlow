import Foundation

enum PracticesClientError: LocalizedError {
    case invalidURL
    case badStatus(Int, String)
    case decodeFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Некорректный URL API"
        case let .badStatus(code, body):
            if code == 401 {
                return "Нет доступа (401). Войди в аккаунт."
            }
            if code == 403 {
                return body.isEmpty ? "Доступ запрещён (403)." : body
            }
            if code == 404 {
                return "Практика не найдена."
            }
            return "Ошибка сервера (\(code)): \(body)"
        case let .decodeFailed(msg):
            return msg
        }
    }
}

private struct EmptyJSONBody: Encodable {}

enum PracticesClient {
    private static let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        d.dateDecodingStrategy = .custom { dec in
            let container = try dec.singleValueContainer()
            let str = try container.decode(String.self)
            if let d = formatter.date(from: str) { return d }
            let f2 = ISO8601DateFormatter()
            f2.formatOptions = [.withInternetDateTime]
            if let d = f2.date(from: str) { return d }
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Invalid date: \(str)")
        }
        return d
    }()

    static func fetchPracticesList() async throws -> [PracticeSummaryDTO] {
        try await get(path: "/practices/")
    }

    /// Справочник категорий для фильтра; при ошибке — пустой список.
    static func fetchPracticeCategories() async -> [PracticeCategoryDTO] {
        do {
            let dto: PracticeCategoriesListDTO = try await get(path: "/practices/categories/list")
            return dto.categories
        } catch {
            return []
        }
    }

    /// Bundle смысла + практики по дню пользователя (как на веб-дашборде). При ошибке — `nil`.
    static func fetchInterpretationBundle(day: Int? = nil) async -> InterpretationBundleDTO? {
        do {
            var path = "/practices/interpretation-bundle"
            if let day {
                path += "?day=\(day)"
            }
            return try await get(path: path)
        } catch {
            return nil
        }
    }

    /// Персональная «сейчас» практика; при 404/ошибке — `nil` (как на вебе с `.catch(() => null)`).
    static func fetchCurrentPractice() async -> PracticeSummaryDTO? {
        do {
            return try await get(path: "/practices/current")
        } catch {
            return nil
        }
    }

    static func fetchPracticeDetail(id: String) async throws -> PracticeDetailDTO {
        let encoded = id.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? id
        return try await get(path: "/practices/\(encoded)")
    }

    static func completePractice(id: String) async throws -> PracticeUsageDTO {
        let encoded = id.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? id
        return try await post(path: "/practices/\(encoded)/complete", body: EmptyJSONBody())
    }

    static func fetchPracticeHistory(limit: Int = 100) async throws -> PracticeHistoryResponseDTO {
        try await get(path: "/practices/history?limit=\(limit)")
    }

    /// Как на вебе с `.catch(() => null)` — при ошибке возвращаем `nil`.
    static func fetchPracticeProgress() async -> PracticeProgressResponseDTO? {
        do {
            return try await get(path: "/practices/progress")
        } catch {
            return nil
        }
    }

    /// Лимиты персонализированных практик на неделю; при ошибке — `nil`.
    static func fetchPracticeLimits() async -> PracticeLimitsDTO? {
        do {
            return try await get(path: "/practices/limits")
        } catch {
            return nil
        }
    }

    /// Список guided sequences; при ошибке (в т.ч. 401) — пустой массив.
    static func fetchSequences() async -> [PracticeSummaryDTO] {
        do {
            return try await get(path: "/practices/sequences")
        } catch {
            return []
        }
    }

    /// Короткие альтернативные практики (fallback), как на вебе.
    static func fetchShortAlternatives() async -> [PracticeSummaryDTO] {
        do {
            return try await get(path: "/practices/short-alternatives")
        } catch {
            return []
        }
    }

    static func fetchAsceticisms() async -> [PracticeAsceticismDTO] {
        do {
            return try await get(path: "/practices/asceticisms")
        } catch {
            return []
        }
    }

    /// Лексикон или генерация (как query на бэкенде).
    static func fetchAffirmationsFromPracticesAPI(needs: String? = nil, generate: Bool = false) async -> [PracticeAffirmationListItemDTO] {
        do {
            var path = "/practices/affirmations"
            var parts: [String] = []
            if let needs, !needs.isEmpty,
               let enc = needs.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) {
                parts.append("needs=\(enc)")
            }
            if generate {
                parts.append("generate=true")
            }
            if !parts.isEmpty {
                path += "?" + parts.joined(separator: "&")
            }
            return try await get(path: path)
        } catch {
            return []
        }
    }

    static func fetchSequenceProgress(sequenceId: String) async throws -> SequenceProgressDTO {
        let enc = sequenceId.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? sequenceId
        return try await get(path: "/practices/sequences/\(enc)/progress")
    }

    static func completeSequenceStep(sequenceId: String, stepNumber: Int) async throws -> PracticeUsageDTO {
        let enc = sequenceId.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? sequenceId
        return try await post(path: "/practices/sequences/\(enc)/steps/\(stepNumber)/complete", body: EmptyJSONBody())
    }

    // MARK: - Transport

    private static func get<T: Decodable>(path: String) async throws -> T {
        let (data, http) = try await dataForRequest(path: path, method: "GET", body: nil as Data?)
        try throwIfNeeded(http, data)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw PracticesClientError.decodeFailed(error.localizedDescription)
        }
    }

    private static func post<T: Decodable, B: Encodable>(path: String, body: B) async throws -> T {
        let encoded = try JSONEncoder().encode(body)
        let (data, http) = try await dataForRequest(path: path, method: "POST", body: encoded)
        try throwIfNeeded(http, data)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw PracticesClientError.decodeFailed(error.localizedDescription)
        }
    }

    private static func dataForRequest(path: String, method: String, body: Data?) async throws -> (Data, HTTPURLResponse) {
        guard var components = URLComponents(url: AppConfig.apiBaseURL, resolvingAgainstBaseURL: false) else {
            throw PracticesClientError.invalidURL
        }
        let normalized = path.hasPrefix("/") ? path : "/" + path
        components.path = components.path + normalized
        guard let url = components.url else { throw PracticesClientError.invalidURL }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.timeoutInterval = 45
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(Locale.preferredLanguages.first ?? "en-US", forHTTPHeaderField: "Accept-Language")
        let token = AppConfig.authToken.trimmingCharacters(in: .whitespacesAndNewlines)
        if !token.isEmpty {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        request.httpBody = body

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: request)
        } catch {
            throw networkAwareError(error, url: url)
        }
        guard let http = response as? HTTPURLResponse else {
            throw PracticesClientError.badStatus(-1, "Нет HTTP-ответа")
        }
        return (data, http)
    }

    private static func networkAwareError(_ error: Error, url: URL) -> PracticesClientError {
        guard let urlError = error as? URLError else {
            return .badStatus(-1, error.localizedDescription)
        }
        let host = url.host ?? url.absoluteString
        switch urlError.code {
        case .notConnectedToInternet:
            return .badStatus(-1, "Нет интернета. Проверь соединение (\(host)).")
        case .cannotConnectToHost, .cannotFindHost:
            return .badStatus(-1, "Не удаётся подключиться к \(host). Проверь API_BASE_URL.")
        case .timedOut:
            return .badStatus(-1, "Таймаут при обращении к \(host).")
        default:
            return .badStatus(-1, urlError.localizedDescription)
        }
    }

    private static func throwIfNeeded(_ http: HTTPURLResponse, _ data: Data) throws {
        guard (200 ... 299).contains(http.statusCode) else {
            let text = String(data: data, encoding: .utf8) ?? ""
            throw PracticesClientError.badStatus(http.statusCode, text)
        }
    }
}
