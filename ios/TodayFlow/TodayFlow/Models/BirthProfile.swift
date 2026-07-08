import Foundation

struct BirthCoordinates: Codable, Equatable {
    let latitude: Double
    let longitude: Double
}

struct BirthProfile: Codable {
    let firstName: String
    let birthDate: Date
    let knowsBirthTime: Bool
    let birthTime: Date
    let birthPlace: String
    let timezone: String
    let sunSign: String
    let moonSign: String
    let risingSign: String

    var formattedBirthSummary: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .long
        return formatter.string(from: birthDate)
    }

    var focusTitle: String {
        "\(sunSign) drive, \(moonSign) pacing"
    }

    /// Черновик для `POST /account/core-setup`, если сохранён только `BirthProfile` без последнего `BirthProfileDraft`.
    func asBirthProfileDraft() -> BirthProfileDraft {
        var draft = BirthProfileDraft()
        draft.firstName = firstName
        draft.birthDate = birthDate
        draft.knowsBirthTime = knowsBirthTime
        draft.birthTime = birthTime
        draft.birthPlace = birthPlace
        draft.timezone = timezone
        return draft
    }
}

struct BirthProfileDraft: Codable {
    var firstName = ""
    /// Сервер: `female`, `male`, `unspecified`; по умолчанию при онбординге — нейтральные формулировки.
    var gender: String?
    var birthDate = Date.now
    var knowsBirthTime = false
    var birthTime = Date.now
    var birthPlace = ""
    var timezone = TimeZone.current.identifier
    var selectedCoordinates: BirthCoordinates?
    var selectedLocationName: String?

    /// Значение для `POST /account/core-setup`.
    var normalizedGenderForAPI: String {
        let g = gender?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() ?? ""
        switch g {
        case "female", "male", "unspecified":
            return g
        default:
            return "unspecified"
        }
    }

    var isValid: Bool {
        !firstName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !birthPlace.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var apiBirthDate: String {
        birthDate.apiDateString
    }

    var apiBirthTime: String {
        formattedBirthTime("HH:mm")
    }

    var apiBirthTimeWithSeconds: String {
        formattedBirthTime("HH:mm:ss")
    }

    var timezoneOffsetMinutes: Int? {
        guard let timezone = TimeZone(identifier: timezone) else { return nil }
        return timezone.secondsFromGMT(for: birthDate) / 60
    }

    private func formattedBirthTime(_ format: String) -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = format
        return formatter.string(from: birthTime)
    }

    var resolved: BirthProfile {
        resolved(using: nil)
    }

    mutating func clearResolvedLocation() {
        selectedCoordinates = nil
        selectedLocationName = nil
    }

    func resolved(using chart: AstroChartResponse?) -> BirthProfile {
        let cleanName = firstName.trimmingCharacters(in: .whitespacesAndNewlines)
        let cleanPlace = birthPlace.trimmingCharacters(in: .whitespacesAndNewlines)
        let sunSign = chart?.positions.first(where: { $0.body == "sun" })?.sign ?? zodiacSign(for: birthDate)
        let moonSign = chart?.positions.first(where: { $0.body == "moon" })?.sign ?? pseudoMoonSign(for: birthDate)
        let risingSign = chart?.positions.first(where: { $0.body == "rising" })?.sign ?? pseudoRisingSign(for: birthDate)

        return BirthProfile(
            firstName: cleanName,
            birthDate: birthDate,
            knowsBirthTime: knowsBirthTime,
            birthTime: birthTime,
            birthPlace: cleanPlace,
            timezone: timezone,
            sunSign: sunSign,
            moonSign: moonSign,
            risingSign: risingSign
        )
    }

    private func zodiacSign(for date: Date) -> String {
        let calendar = Calendar(identifier: .gregorian)
        let components = calendar.dateComponents([.month, .day], from: date)
        let month = components.month ?? 1
        let day = components.day ?? 1

        switch (month, day) {
        case (3, 21...), (4, ..<20): return "Aries"
        case (4, 20...), (5, ..<21): return "Taurus"
        case (5, 21...), (6, ..<21): return "Gemini"
        case (6, 21...), (7, ..<23): return "Cancer"
        case (7, 23...), (8, ..<23): return "Leo"
        case (8, 23...), (9, ..<23): return "Virgo"
        case (9, 23...), (10, ..<23): return "Libra"
        case (10, 23...), (11, ..<22): return "Scorpio"
        case (11, 22...), (12, ..<22): return "Sagittarius"
        case (12, 22...), (1, ..<20): return "Capricorn"
        case (1, 20...), (2, ..<19): return "Aquarius"
        default: return "Pisces"
        }
    }

    private func pseudoMoonSign(for date: Date) -> String {
        let signs = zodiacOrder
        let day = Calendar(identifier: .gregorian).component(.day, from: date)
        return signs[day % signs.count]
    }

    private func pseudoRisingSign(for date: Date) -> String {
        let signs = zodiacOrder
        let month = Calendar(identifier: .gregorian).component(.month, from: birthDate)
        return signs[(month + 3) % signs.count]
    }

    private var zodiacOrder: [String] {
        [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
    }
}

extension Date {
    var apiDateString: String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: self)
    }

    /// Парсинг `yyyy-MM-dd` из API astro-профиля.
    init?(apiBirthDateString string: String) {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        guard let parsed = formatter.date(from: string) else { return nil }
        self = parsed
    }

    var dayHeaderTitle: String {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("EEEE, MMMM d")
        return formatter.string(from: self)
    }
}
