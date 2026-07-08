import Foundation

// MARK: - Триггеры дисклеймера безопасности вопроса (паритет `guidanceSafetyKeywords` в `frontend/src/lib/guidance/catalog.ts`)

enum GuidanceSafetyKeywords {
    /// Показывать ли баннер «не заменяет профессиональную помощь…» по тексту вопроса.
    static func matches(_ question: String) -> Bool {
        let q = question.lowercased()
        if ruNeedles.contains(where: { q.contains($0) }) { return true }
        if enNeedles.contains(where: { q.contains($0) }) { return true }
        for pattern in enRegexPatterns {
            if q.range(of: pattern, options: .regularExpression) != nil { return true }
        }
        return false
    }

    private static let ruNeedles: [String] = [
        "суицид",
        "самоубийств",
        "насили",
        "изнасилован",
        "беремен",
        "аборт",
        "онколог",
        "инфаркт",
        "юрист",
        "адвокат",
        "суд ",
        "иск ",
        "ипотек",
        "кредит",
        "долг миллион",
    ]

    private static let enNeedles: [String] = [
        "suicide",
        "suicidal",
        "kill myself",
        "end my life",
        "self-harm",
        "self harm",
        "hurt myself",
        "sexual assault",
        "domestic violence",
        "raped",
        "rapist",
        "pregnancy",
        "pregnant",
        "abortion",
        "miscarriage",
        "cancer",
        "oncology",
        "heart attack",
        "stroke",
        "lawyer",
        "attorney",
        "lawsuit",
        "malpractice",
        "court case",
        "restraining order",
        "foreclosure",
        "mortgage",
        "debt collector",
        "subpoena",
    ]

    private static let enRegexPatterns: [String] = [
        #"\brape\b"#,
        #"\braping\b"#,
    ]
}
