import Foundation

actor MeaningRuntime {
    private let persistence = TodayFlowPersistence.shared
    private let maxBatch = 50
    private let maxOutbox = 500

    func track(
        eventType: String,
        eventSource: String,
        localDate: String,
        qualityScore: Double = 1.0,
        payload: [String: JSONValue] = [:],
        idempotencyKey: String? = nil
    ) {
        var outbox = persistence.loadMeaningOutbox()
        let event = MeaningEventInput(
            eventID: nil,
            eventType: eventType,
            eventSource: eventSource,
            eventTime: Self.isoDateTime(Date()),
            localDate: localDate,
            qualityScore: qualityScore,
            payload: payload.isEmpty ? nil : payload,
            idempotencyKey: idempotencyKey ?? "ios-\(UUID().uuidString.lowercased())"
        )
        outbox.append(event)
        if outbox.count > maxOutbox {
            outbox = Array(outbox.suffix(maxOutbox))
        }
        persistence.saveMeaningOutbox(outbox)
    }

    func flush(token: String) async {
        var outbox = persistence.loadMeaningOutbox()
        guard !outbox.isEmpty else { return }

        while !outbox.isEmpty {
            let batch = Array(outbox.prefix(maxBatch))
            do {
                _ = try await TodayFlowAPIClient.shared.postMeaningEvents(token: token, events: batch)
                outbox.removeFirst(min(maxBatch, outbox.count))
                persistence.saveMeaningOutbox(outbox)
            } catch {
                return
            }
        }
    }

    func refreshRings(token: String, windowDays: Int = 28) async -> MeaningRingsResponse? {
        do {
            let response = try await TodayFlowAPIClient.shared.fetchMeaningRings(token: token, windowDays: windowDays)
            persistence.saveMeaningRingsCache(response)
            return response
        } catch {
            return persistence.loadMeaningRingsCache()
        }
    }

    private static func isoDateTime(_ date: Date) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter.string(from: date)
    }
}

