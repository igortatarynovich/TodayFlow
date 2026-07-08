import Foundation

struct Ritual: Codable, Identifiable {
    let id: UUID
    let title: String
    let duration: String
    let purpose: String
    let isComplete: Bool
}

extension Ritual {
    static let placeholder: [Ritual] = [
        Ritual(
            id: UUID(),
            title: "Morning reset",
            duration: "5 min",
            purpose: "Name the one outcome that matters before messages take over.",
            isComplete: true
        ),
        Ritual(
            id: UUID(),
            title: "Midday breath check",
            duration: "3 min",
            purpose: "Interrupt mental drift and notice what is quietly draining momentum.",
            isComplete: false
        ),
        Ritual(
            id: UUID(),
            title: "Evening closure",
            duration: "7 min",
            purpose: "Review what moved, what stalled, and what should not follow you into tomorrow.",
            isComplete: false
        )
    ]

    static func personalized(for profile: BirthProfile, dayFlow: DayFlowAPIResponse? = nil) -> [Ritual] {
        var rituals = [
            Ritual(
                id: UUID(),
                title: "\(profile.risingSign) start",
                duration: "4 min",
                purpose: "Set the tone of the day with one visible action before you disappear into planning.",
                isComplete: false
            ),
            Ritual(
                id: UUID(),
                title: "\(profile.moonSign) check-in",
                duration: "3 min",
                purpose: "Notice what your emotional bandwidth can actually hold before you overcommit.",
                isComplete: false
            ),
            Ritual(
                id: UUID(),
                title: "\(profile.sunSign) close",
                duration: "6 min",
                purpose: "End the day by naming where your energy was strongest and what should continue tomorrow.",
                isComplete: false
            )
        ]

        if let practice = dayFlow?.practice {
            rituals.insert(
                Ritual(
                    id: UUID(),
                    title: practice.title ?? "Recommended practice",
                    duration: "\(practice.duration_minutes ?? 5) min",
                    purpose: practice.description ?? "Use today's recommended practice to stabilize the day.",
                    isComplete: false
                ),
                at: 1
            )
        }

        return rituals
    }
}
