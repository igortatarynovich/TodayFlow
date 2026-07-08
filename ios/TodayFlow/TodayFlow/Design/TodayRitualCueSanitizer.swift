import Foundation

/// Паритет с `frontend/src/components/today/ritualCueSanitizer.ts`: убираем рубрики вместо действий и шаблон с «линией 'general'».
enum TodayRitualCueSanitizer {
    private static let chaosLine =
        "Осторожнее, если день начинает скатываться в хаос, резкие реакции и потерю своего ритма — держи одну линию, не хватайся за всё сразу."

    /// Паритет `ritual_cue_sanitize._TOPIC_LABELS_NOT_ACTIONS` / `RU_TOPIC_LABELS_NOT_ACTIONS` (O3).
    private static let topicOnly: Set<String> = [
        "смысл и коммуникация",
        "смысл и коммуникации",
        "смысл и коммуникацию",
        "общий фокус дня",
        "общий фон дня",
        "общение и контакт",
        "смысл дня",
        "контекст дня",
        "рамка дня",
        "общая картина",
        "картина дня",
        "настрой на день",
        "тональность дня",
        "вектор дня",
        "форма дня",
        "сигнал дня",
        "паттерн дня",
    ]

    /// O3: заголовок слоя «День» не только рубрика (паритет `is_ru_abstract_topic_headline`).
    static func isRuAbstractTopicHeadline(_ text: String?) -> Bool {
        let t = (text ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if t.isEmpty { return true }
        return topicOnly.contains(t)
    }

    private static let slugTopicJunk: Set<String> = [
        "general", "overall", "dialogue", "communication", "mixed", "none", "other", "default",
    ]

    private static let slugToRu: [String: String] = [
        "general": "общий фон дня",
        "love": "любовь и близость",
        "relations": "отношения",
        "career": "работа и карьера",
        "work": "работа и карьера",
        "money": "деньги и границы",
        "family": "семья и дом",
        "home": "семья и дом",
        "body": "тело и восстановление",
        "health": "тело и восстановление",
        "dialogue": "общение и контакт",
        "communication": "общение и контакт",
        "decision": "решение, которое надо принять",
        "identity": "линия про себя",
        "self": "линия про себя",
    ]

    /// Паритет `day_narrative_brief_v0` / `ritual_cue_sanitize._HEAD_TOPIC_SLUG_RU` (O5).
    private static let headTopicSlugRu: [String: String] = [
        "general": "общий фон дня",
        "body": "тело и энергия",
        "money": "деньги",
        "dialogue": "общение и контакт",
        "family": "семья и дом",
        "career": "работа и дела",
        "love": "близость и отношения",
    ]

    /// Паритет `day_narrative_brief_v0._MOOD_ID_RU` (O5).
    private static let moodSlugRu: [String: String] = [
        "calm": "спокойно",
        "anxious": "тревожно",
        "tired": "устало",
        "driven": "в драйве",
        "irritated": "раздражённо",
        "other": "другое",
        "motivated": "в драйве",
        "confused": "неясно",
        "quiet_wish": "хочется тишины",
        "move_wish": "хочется движения",
        "heavy": "тяжело",
        "hopeful": "с надеждой",
        "distant": "на дистанции",
    ]

    private static let quotedServiceSlugRu: [String: String] = {
        var o: [String: String] = [:]
        slugToRu.forEach { o[$0.key] = $0.value }
        headTopicSlugRu.forEach { o[$0.key] = $0.value }
        moodSlugRu.forEach { o[$0.key] = $0.value }
        return o
    }()

    /// O5: не показываем сырые 'tired' / 'general' в кавычках в RU-тексте.
    static func replaceQuotedEnSlugsForRuDisplay(_ raw: String?) -> String {
        let t = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if t.isEmpty { return "" }
        guard let regex = try? NSRegularExpression(
            pattern: #"(?:['"]|«)([a-z][a-z0-9_]{0,31})(?:['"]|»)"#,
            options: .caseInsensitive
        ) else { return t }
        let ns = t as NSString
        let fullLen = ns.length
        let fullRange = NSRange(location: 0, length: fullLen)
        let matches = regex.matches(in: t, options: [], range: fullRange)
        if matches.isEmpty { return t }
        var result = ""
        var idx = 0
        for m in matches {
            if m.range.location > idx {
                result += ns.substring(with: NSRange(location: idx, length: m.range.location - idx))
            }
            if m.numberOfRanges > 1, let r = Range(m.range(at: 1), in: t) {
                let slug = String(t[r]).lowercased()
                if let label = quotedServiceSlugRu[slug] {
                    result += "«\(label)»"
                } else {
                    result += ns.substring(with: m.range)
                }
            } else {
                result += ns.substring(with: m.range)
            }
            idx = m.range.location + m.range.length
        }
        if idx < fullLen {
            result += ns.substring(with: NSRange(location: idx, length: fullLen - idx))
        }
        return result
    }

    static func humanizeFocusSlugForUi(_ slug: String) -> String {
        let k = slug.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if let ru = slugToRu[k] { return ru }
        if k.range(of: "^[a-z][a-z0-9_]{0,22}$", options: .regularExpression) != nil {
            return "узкая тема дня"
        }
        return slug.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    static func isGarbageRitualActionCue(_ line: String?) -> Bool {
        let raw = (line ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if raw.isEmpty { return true }
        if TodayPersonalDayRhythm.isDiscardableMorningFocus(raw) { return true }
        let t = raw.lowercased()
        if topicOnly.contains(t) { return true }
        if t.count <= 32, t.allSatisfy({ $0 == " " || $0 == "_" || ($0 >= "a" && $0 <= "z") }) {
            return true
        }
        return false
    }

    static func repairRitualDoNotEnterLine(_ raw: String?) -> String {
        let t = replaceQuotedEnSlugsForRuDisplay(raw)
        if t.isEmpty { return "" }
        let nsFull = t as NSString
        let fullRange = NSRange(location: 0, length: nsFull.length)
        if let regex = try? NSRegularExpression(pattern: "['«]([a-z][a-z0-9_]{0,24})['»]", options: .caseInsensitive),
           let m = regex.firstMatch(in: t, options: [], range: fullRange),
           m.numberOfRanges > 1,
           let r = Range(m.range(at: 1), in: t) {
            let slug = String(t[r]).lowercased()
            if TodayPersonalDayRhythm.isDiscardableMorningFocus(slug) || slugTopicJunk.contains(slug) {
                return chaosLine
            }
            let label = humanizeFocusSlugForUi(slug)
            return "Осторожнее с темой «\(label)», если она начинает проживаться как хаос, резкие реакции и потеря своего ритма."
        }
        if t.range(of: "general", options: .caseInsensitive) != nil,
           t.range(of: "линию", options: .caseInsensitive) != nil || t.range(of: "линия", options: .caseInsensitive) != nil {
            return chaosLine
        }
        return t
    }

    /// Паритет `ritual_cue_sanitize.strip_llm_meta_commentary` / `ritualCueSanitizer.ts`.
    private static let llmMetaNeedles: [String] = [
        "не дублирую", "не дублируем", "я не дублиру", "чтобы экран не перегруж", "экран не перегружа",
        "карта и число остаются", "не дублирую их", "не дублируем их", "в сводке и в", "чтобы не перегруж",
        "чтобы не дублировать", "не дублирую информацию", "не дублируем информацию", "не повторяю блок",
        "не повторяю уже сказанное", "как просили в промпте", "как указано в задании", "в рамках формата ответа",
        "по требованиям к ответу", "согласно инструкции для модели", "убираю дублирование",
        "исключил дублирование", "дублирование с предыдущим", "уже было в предыдущем блоке",
        "из предыдущего абзаца", "as per the prompt", "as instructed, i will not", "i won't repeat the",
        "to avoid duplication", "avoiding repeating", "not repeating the card", "not repeating the number",
    ]

    static func stripLlmMetaCommentary(_ text: String?) -> String {
        let raw = (text ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if raw.isEmpty { return "" }
        let lower = raw.lowercased()
        if !llmMetaNeedles.contains(where: { lower.contains($0) }) { return raw }

        let ns = raw as NSString
        let fullLen = ns.length
        guard let regex = try? NSRegularExpression(pattern: "(?<=[.!?])\\s+", options: []) else { return raw }

        let fullRange = NSRange(location: 0, length: fullLen)
        var loc = 0
        var kept: [String] = []
        regex.enumerateMatches(in: raw, options: [], range: fullRange) { match, _, _ in
            guard let match else { return }
            let endOfSentence = match.range.location
            let r = NSRange(location: loc, length: endOfSentence - loc)
            if r.length > 0 {
                let part = ns.substring(with: r).trimmingCharacters(in: .whitespacesAndNewlines)
                if !part.isEmpty {
                    let pl = part.lowercased()
                    if !llmMetaNeedles.contains(where: { pl.contains($0) }) {
                        kept.append(part)
                    }
                }
            }
            loc = match.range.location + match.range.length
        }
        if loc < fullLen {
            let r = NSRange(location: loc, length: fullLen - loc)
            let part = ns.substring(with: r).trimmingCharacters(in: .whitespacesAndNewlines)
            if !part.isEmpty {
                let pl = part.lowercased()
                if !llmMetaNeedles.contains(where: { pl.contains($0) }) {
                    kept.append(part)
                }
            }
        }
        return kept.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
