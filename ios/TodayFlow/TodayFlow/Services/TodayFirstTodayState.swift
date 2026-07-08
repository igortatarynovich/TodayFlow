import Foundation

/// Parity with web `firstTodayState.ts` — key `todayflow_first_today_v1`.
enum TodayFirstTodayState {
    private static let storageKey = "todayflow_first_today_v1"

    struct Payload: Codable {
        var completedAt: String?
        var dayKey: String?
        var profileDepthUnlocked: Bool?

        enum CodingKeys: String, CodingKey {
            case completedAt = "completed_at"
            case dayKey = "day_key"
            case profileDepthUnlocked = "profile_depth_unlocked"
        }
    }

    static func read() -> Payload {
        guard let data = UserDefaults.standard.data(forKey: storageKey),
              let payload = try? JSONDecoder().decode(Payload.self, from: data) else {
            return Payload()
        }
        return payload
    }

    private static func write(_ payload: Payload) {
        guard let data = try? JSONEncoder().encode(payload) else { return }
        UserDefaults.standard.set(data, forKey: storageKey)
    }

    static var hasCompletedFirstToday: Bool {
        !(read().completedAt?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ?? true)
    }

    static var hasProfileDepthUnlocked: Bool {
        read().profileDepthUnlocked == true
    }

    static var shouldShowProfileTeaser: Bool {
        hasCompletedFirstToday && !hasProfileDepthUnlocked
    }

    static func markFirstTodayCompleted(dayKey: String? = nil) {
        var payload = read()
        payload.completedAt = ISO8601DateFormatter().string(from: Date())
        payload.dayKey = dayKey
        write(payload)
    }

    static func markProfileDepthUnlocked() {
        var payload = read()
        payload.profileDepthUnlocked = true
        write(payload)
    }
}
