import Foundation

struct DailyFocus: Codable, Identifiable {
    let id: UUID
    let dateTitle: String
    let energyTitle: String
    let summary: String
    let guidance: [String]
    let reflectionPrompt: String
}

extension DailyFocus {
    static let placeholder = DailyFocus(
        id: UUID(),
        dateTitle: "Saturday, March 28",
        energyTitle: "Quiet traction",
        summary: "Today works better when your attention narrows. The less you scatter yourself, the more the day begins to respond.",
        guidance: [
            "Finish one neglected thing before you start a new one.",
            "Protect a slower pace around midday so you can think clearly.",
            "Choose continuity over novelty if the path already feels sound."
        ],
        reflectionPrompt: "What deserves a calmer and more disciplined yes today?"
    )

    static func personalized(for profile: BirthProfile, dayFlow: DayFlowAPIResponse? = nil) -> DailyFocus {
        let guidance: [String]
        if let consistency = dayFlow?.consistency {
            guidance = [
                consistency.do_focus ?? "Return to one meaningful priority whenever the day starts fragmenting.",
                dayFlow?.numerology?.whatToDo ?? "Use your day rhythm for observable progress, not reactive motion.",
                dayFlow?.numerology?.whatToAvoid ?? "Notice what depletes your pace before it turns into drift."
            ]
        } else if let affirmations = dayFlow?.affirmations, !affirmations.isEmpty {
            guidance = Array(affirmations.prefix(3).map(\.text))
        } else {
            guidance = [
                "Use your \(profile.sunSign) side for visible action and your \(profile.moonSign) side for pacing.",
                "Let \(profile.risingSign) rising shape the first impression of the day: clear, direct, and deliberate.",
                "Return to one meaningful priority whenever the day starts fragmenting."
            ]
        }

        let dateTitle: String
        if let rawDate = dayFlow?.date, let parsedDate = Self.apiDateFormatter.date(from: rawDate) {
            dateTitle = parsedDate.dayHeaderTitle
        } else {
            dateTitle = Date.now.dayHeaderTitle
        }

        return DailyFocus(
            id: UUID(),
            dateTitle: dateTitle,
            energyTitle: dayFlow?.numerology?.title ?? profile.focusTitle,
            summary: dayFlow?.numerology?.summary
                ?? "Ритм становится ровнее, когда решения совпадают с естественным темпом. \(profile.firstName), опирайся сегодня на устойчивость, а не на давление.",
            guidance: guidance,
            reflectionPrompt: dayFlow?.numerology?.meaning ?? "Где твоему естественному ритму сегодня нужно больше доверия?"
        )
    }

    private static let apiDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()
}
