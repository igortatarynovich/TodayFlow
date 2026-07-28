import Foundation

/// Parity with web `profileHouseConstants.ts` — house titles and fallbacks.
enum ProfileHouseCopy {
    static let layerTitle: [Int: String] = [
        1: "Как ты заходишь в мир",
        2: "Что для тебя ценно",
        3: "Как ты думаешь и общаешься",
        4: "Где ты настоящий",
        5: "Где ты живешь ради себя",
        6: "Как ты живешь каждый день",
        7: "Как ты строишь связь",
        8: "Где ты меняешься",
        9: "Как ты ищешь смысл",
        10: "Как ты хочешь выглядеть в мире",
        11: "С кем ты идешь в будущее",
        12: "Где ты теряешь или находишь себя",
    ]

    /// Short person-facing theses — parity with web `HOUSE_FALLBACK`. Never natal encyclopedia.
    static let fallback: [Int: String] = [
        1: "В первом контакте тебя считывают по темпу и дистанции.",
        2: "Самооценка читается через «это моё» — ресурсы и право не оправдываться.",
        3: "Ты думаешь вслух рядом — учёба, спор, факты для ближайшего круга.",
        4: "Дом и приватный ритм — чем ты заряжаешься и от чего прячешься.",
        5: "Игра и риск «ради себя» — не ради роли.",
        6: "Режим тела и мелочей либо держит тебя, либо копится как долг.",
        7: "Равные отношения — умеешь ли ты держать явные правила двоих.",
        8: "Совместные ресурсы и необратимые перемены — контроль спорит с уязвимостью.",
        9: "Нужна рамка смысла шире «как сделать».",
        10: "Публичная роль — по какому следу тебя судят о результате.",
        11: "Сеть и общее будущее — взаимный вектор, а не только поддержка контакта.",
        12: "Вне зрителей — либо восстанавливаешься, либо теряешь себя без свидетелей.",
    ]

    static let keyHouses: Set<Int> = [1, 4, 7, 10]

    static func ensureTwelveHouses(from chart: NatalChartPreview) -> [NatalHouse] {
        if !chart.houses.isEmpty { return chart.houses.sorted { $0.house < $1.house } }

        if let base = ascendantLongitude(chart.ascendant) {
            return (1...12).map { index in
                let cusp = (base + Double(index - 1) * 30).truncatingRemainder(dividingBy: 360)
                let normalized = cusp < 0 ? cusp + 360 : cusp
                let sign = ZodiacSignRU.englishSignFromLongitude(normalized)
                return NatalHouse(
                    house: index,
                    cuspLongitude: normalized,
                    sign: sign,
                    degree: normalized.truncatingRemainder(dividingBy: 30)
                )
            }
        }

        if !chart.positions.isEmpty {
            return (1...12).map { NatalHouse(house: $0, cuspLongitude: nil, sign: nil, degree: nil) }
        }

        return chart.houses
    }

    private static func ascendantLongitude(_ asc: NatalAscendant?) -> Double? {
        guard let asc else { return nil }
        if let lon = asc.longitude { return lon }
        guard let sign = asc.sign, let deg = asc.degree else { return nil }
        let normalizedSign = sign.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let english: String
        switch normalizedSign {
        case "aries", "овен": english = "Aries"
        case "taurus", "телец": english = "Taurus"
        case "gemini", "близнецы": english = "Gemini"
        case "cancer", "рак": english = "Cancer"
        case "leo", "лев": english = "Leo"
        case "virgo", "дева": english = "Virgo"
        case "libra", "весы": english = "Libra"
        case "scorpio", "скорпион": english = "Scorpio"
        case "sagittarius", "стрелец": english = "Sagittarius"
        case "capricorn", "козерог": english = "Capricorn"
        case "aquarius", "водолей": english = "Aquarius"
        case "pisces", "рыбы": english = "Pisces"
        default: english = sign
        }
        let signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        guard let idx = signs.firstIndex(where: { $0.caseInsensitiveCompare(english) == .orderedSame }) else { return nil }
        return Double(idx * 30) + deg.truncatingRemainder(dividingBy: 30)
    }
}
