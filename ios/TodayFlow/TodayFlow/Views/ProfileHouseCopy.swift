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

    static let fallback: [Int: String] = [
        1: "Личность, самопрезентация, первый импульс действия.",
        2: "Ресурсы, деньги, ценности и чувство опоры.",
        3: "Общение, обучение, ближайшее окружение.",
        4: "Дом, семья, корни, внутреннее основание.",
        5: "Творчество, радость, самовыражение, романтика.",
        6: "Режим, работа, здоровье, дисциплина.",
        7: "Партнерство, договоренности, баланс с другими.",
        8: "Трансформация, глубина, доверие, общие ресурсы.",
        9: "Смыслы, мировоззрение, путешествия, расширение.",
        10: "Карьера, статус, социальная реализация.",
        11: "Сообщество, друзья, долгие цели и идеи.",
        12: "Подсознание, восстановление, духовная работа.",
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
