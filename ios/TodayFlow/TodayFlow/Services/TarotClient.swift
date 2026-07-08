import Foundation

enum TarotClientError: LocalizedError {
    case invalidURL
    case badStatus(Int, String)
    case decodeFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL"
        case let .badStatus(code, body):
            if code == 401 {
                return "Нет доступа (401). Войди в аккаунт на экране входа."
            }
            return "Server error (\(code)): \(body)"
        case let .decodeFailed(msg):
            return msg
        }
    }
}

enum TarotClient {
    private static let decoder: JSONDecoder = {
        let d = JSONDecoder()
        d.keyDecodingStrategy = .convertFromSnakeCase
        return d
    }()

    private static let encoder: JSONEncoder = {
        let e = JSONEncoder()
        e.keyEncodingStrategy = .convertToSnakeCase
        return e
    }()

    static func fetchDailyDraw() async throws -> TarotDailyDrawDTO {
        try await get(path: "/tarot/daily")
    }

    static func fetchTarotHistory() async throws -> TarotHistoryResponseDTO {
        try await get(path: "/tarot/history")
    }

    static func drawDeck(count: Int) async throws -> [TarotCardDTO] {
        try await post(path: "/tarot/deck/draw", body: TarotDeckDrawRequest(count: count))
    }

    static func spreadContext(
        spreadId: String,
        question: String?,
        concernDomain: String? = nil,
        selected: [(cardId: Int, orientation: String)]
    ) async throws -> TarotSpreadContextDTO {
        let payload = TarotSpreadContextRequest(
            spreadId: spreadId,
            question: question?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty,
            concernDomain: concernDomain?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty,
            selectedCards: selected.map { TarotSelectedCardRequest(cardId: $0.cardId, orientation: $0.orientation) }
        )
        return try await post(path: "/tarot/spread/context", body: payload)
    }

    static func fetchFavoriteIds() async throws -> [Int] {
        let response: TarotFavoritesResponse = try await get(path: "/tarot/favorites")
        return response.favorites
    }

    static func toggleFavorite(cardId: Int) async throws -> [Int] {
        let body = TarotFavoriteToggleRequest(cardId: cardId, favorite: true)
        let response: TarotFavoritesResponse = try await post(path: "/tarot/favorites/toggle", body: body)
        return response.favorites
    }

    static func fetchSpreadHistory() async throws -> [TarotSpreadRecordDTO] {
        let response: TarotSpreadHistoryDTO = try await get(path: "/tarot/spread/history")
        return response.history
    }

    /// Раздать карты для выбранного шаблона (`POST /tarot/spread`).
    static func drawSpread(spreadId: String) async throws -> TarotSpreadResultDTO {
        try await post(path: "/tarot/spread", body: TarotSpreadDrawRequest(spread_id: spreadId))
    }

    /// Справочник аркана по id (публичный `GET /tarot/cards/{card_id}`).
    static func fetchTarotCard(cardId: Int) async throws -> TarotCardDTO {
        try await get(path: "/tarot/cards/\(cardId)")
    }

    // MARK: - Transport

    private static func get<T: Decodable>(path: String) async throws -> T {
        let (data, http) = try await dataForRequest(path: path, method: "GET", body: nil as Data?)
        try throwIfNeeded(http, data)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw TarotClientError.decodeFailed(error.localizedDescription)
        }
    }

    private static func post<T: Decodable, B: Encodable>(path: String, body: B) async throws -> T {
        let encoded = try encoder.encode(body)
        let (data, http) = try await dataForRequest(path: path, method: "POST", body: encoded)
        try throwIfNeeded(http, data)
        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw TarotClientError.decodeFailed(error.localizedDescription)
        }
    }

    private static func dataForRequest(path: String, method: String, body: Data?) async throws -> (Data, HTTPURLResponse) {
        guard var components = URLComponents(url: AppConfig.apiBaseURL, resolvingAgainstBaseURL: false) else {
            throw TarotClientError.invalidURL
        }
        let normalized = path.hasPrefix("/") ? path : "/" + path
        components.path = components.path + normalized
        guard let url = components.url else { throw TarotClientError.invalidURL }

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
            throw TarotClientError.badStatus(-1, "No HTTP response")
        }
        return (data, http)
    }

    private static func networkAwareError(_ error: Error, url: URL) -> TarotClientError {
        guard let urlError = error as? URLError else {
            return .badStatus(-1, error.localizedDescription)
        }

        let hostLine = url.host ?? url.absoluteString
        switch urlError.code {
        case .notConnectedToInternet:
            return .badStatus(-1, "Нет интернета. Tarot не может подключиться к \(hostLine).")
        case .cannotConnectToHost, .cannotFindHost:
            return .badStatus(-1, "Tarot не может подключиться к \(hostLine). Проверь API host в Settings.")
        case .timedOut:
            return .badStatus(-1, "Tarot ждёт слишком долго ответ от \(hostLine).")
        default:
            return .badStatus(-1, "Ошибка сети для \(hostLine): \(urlError.localizedDescription)")
        }
    }

    private static func throwIfNeeded(_ http: HTTPURLResponse, _ data: Data) throws {
        guard (200...299).contains(http.statusCode) else {
            let text = String(data: data, encoding: .utf8) ?? ""
            throw TarotClientError.badStatus(http.statusCode, text)
        }
    }
}

private extension String {
    var nilIfEmpty: String? {
        let t = trimmingCharacters(in: .whitespacesAndNewlines)
        return t.isEmpty ? nil : t
    }
}
