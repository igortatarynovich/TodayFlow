import Foundation

/// Паритет `frontend/src/components/today/todayRitualCopy.ts` — ритм числа дня и одна строка луны без дублей.
enum TodayPersonalDayRhythm {
    static func normalizeLunarPhaseLabel(_ moonLine: String?) -> String? {
        guard let raw = moonLine?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else { return nil }
        let lower = raw.lowercased()
        if lower.hasPrefix("фаза:") {
            let tail = raw.dropFirst(5).trimmingCharacters(in: .whitespacesAndNewlines)
            return tail.isEmpty ? raw : String(tail)
        }
        return raw
    }

    static func formatLunarRitualSummaryLine(
        whyMoon: String?,
        whyLunar: String?,
        lunarInfluence: String?,
        transitInfluence: String?,
        maxLen: Int
    ) -> String {
        let phase = normalizeLunarPhaseLabel(whyMoon)
        let themes = whyLunar?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let primary: String = {
            if !themes.isEmpty, let p = phase, !p.isEmpty { return "\(themes) · \(p)" }
            if !themes.isEmpty { return themes }
            if let p = phase { return p }
            return ""
        }()
        if !primary.isEmpty { return clip(primary, maxLen: maxLen) }
        if let li = lunarInfluence?.trimmingCharacters(in: .whitespacesAndNewlines), !li.isEmpty {
            return clip(li, maxLen: maxLen)
        }
        if let tr = transitInfluence?.trimmingCharacters(in: .whitespacesAndNewlines), !tr.isEmpty {
            return clip(tr, maxLen: maxLen)
        }
        return "—"
    }

    static func resolvePersonalDayRhythmKey(reduced: Int?, displayValue: String) -> Int {
        let digits = displayValue.filter(\.isNumber)
        if let raw = Int(digits) {
            if raw == 11 || raw == 22 || raw == 33 { return raw }
        }
        if let r = reduced, (1 ... 9).contains(r) { return r }
        if let raw = Int(digits), raw > 0 {
            return digitalRootPositive(raw)
        }
        return 1
    }

    static func personalDayRhythmLine(reduced: Int?, displayValue: String) -> String {
        let key = resolvePersonalDayRhythmKey(reduced: reduced, displayValue: displayValue)
        return rhythmFull[key] ?? rhythmFull[1]!
    }

    static func personalDayRhythmBridgeSuffix(reduced: Int?, displayValue: String) -> String {
        let key = resolvePersonalDayRhythmKey(reduced: reduced, displayValue: displayValue)
        return rhythmBridge[key] ?? rhythmBridge[1]!
    }

    static func lunarInfluenceRedundantWithAstronomy(_ influence: String, moonBlock: String) -> Bool {
        let a = normalizeLoose(influence)
        let b = normalizeLoose(moonBlock)
        if a.count < 14 || b.count < 8 { return false }
        if a.contains(b) || b.contains(a) { return true }
        let wordsB = b.split(separator: " ").map(String.init).filter { $0.count > 3 }
        if wordsB.isEmpty { return false }
        var hit = 0
        for w in wordsB where a.contains(w) { hit += 1 }
        return Double(hit) / Double(wordsB.count) >= 0.72
    }

    private static func digitalRootPositive(_ n: Int) -> Int {
        var x = abs(n)
        if x == 0 { return 1 }
        while x > 9 {
            x = String(x).compactMap { $0.wholeNumberValue }.reduce(0, +)
        }
        return max(1, x)
    }

    private static func clip(_ s: String, maxLen: Int) -> String {
        let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
        if t.count <= maxLen { return t }
        let idx = t.index(t.startIndex, offsetBy: max(0, maxLen - 1))
        return String(t[..<idx]) + "…"
    }

    private static func normalizeLoose(_ s: String) -> String {
        let mapped = s.lowercased().map { ch -> Character in
            if "·.,:;!?—–-".contains(ch) { return " " }
            return ch
        }
        let str = String(mapped)
        return str.split(whereSeparator: { $0.isWhitespace }).joined(separator: " ")
    }

    private static let rhythmFull: [Int: String] = [
        1: "Число дня с корнем 1 — ритм старта: один ясный первый шаг и инициатива, а не ожидание внешнего «разрешения начать».",
        2: "Корень 2 — ритм согласования: выдержанный темп, пауза перед ответом и опора на пару/договорённости, а не резкий рывок.",
        3: "Корень 3 — ритм лёгкости и коротких циклов: формулировать вслух, прояснять, не закапываться в перфекционизм.",
        4: "Корень 4 — ритм шага и опоры: измеримый прогресс, режим и дисциплина малыми порциями.",
        5: "Корень 5 — ритм смены и гибкости: адаптироваться к факту, не цепляясь за первый план любой ценой.",
        6: "Корень 6 — ритм заботы и баланса обязательств: держать одну зону ответственности честно, без перегруза «за всех».",
        7: "Корень 7 — ритм глубины: время на анализ и тишину, чтобы не путать шум с ясностью.",
        8: "Корень 8 — ритм результата и границ: ресурсы, договорённости и ответственность за итог, без лишней суеты.",
        9: "Корень 9 — ритм завершения: подводить смысл, отпускать лишнее, не цепляться за отжившее.",
        11: "Число 11 — ритм тонкого считывания: доверять интуиции, но закреплять инсайт одним простым действием.",
        22: "Число 22 — ритм структуры под масштаб: большой замысел через конкретные кирпичики, без перегруза всем сразу.",
        33: "Число 33 — ритм поддержки и ясности для других: забота, которая не обнуляет твои границы.",
    ]

    private static let rhythmBridge: [Int: String] = [
        1: "число с корнем 1 просит старта и первого шага без откладывания",
        2: "корень 2 просит ровного темпа и согласования, а не форсированной скорости",
        3: "корень 3 просит лёгких циклов и прояснений вслух",
        4: "корень 4 просит шагов и опоры, а не размытого многозадачия",
        5: "корень 5 просит гибкости и смены плана по факту",
        6: "корень 6 просит честного баланса заботы и границ",
        7: "корень 7 просит паузы на ясность, а не спешных выводов",
        8: "корень 8 просит фокуса на результате и договорённостях",
        9: "корень 9 просит завершать и отпускать лишнее",
        11: "число 11 просит связать интуицию с одним простым действием",
        22: "число 22 просит строить масштаб короткими опорами",
        33: "число 33 просит заботу без самопожертвования",
    ]

    // MARK: - Dedup (паритет `todayRitualCopy.ts`)

    static func textsSemanticallyRedundant(_ a: String, _ b: String, minTokenOverlap: Double = 0.56) -> Bool {
        let na = normalizeLoose(a)
        let nb = normalizeLoose(b)
        if na.isEmpty || nb.isEmpty { return false }
        if na == nb { return true }
        let minL = min(na.count, nb.count)
        let maxL = max(na.count, nb.count)
        if minL >= 22, maxL >= minL {
            if na.contains(nb) || nb.contains(na) { return true }
        }
        let ta = na.split(separator: " ").map(String.init).filter { $0.count > 2 }
        let tb = nb.split(separator: " ").map(String.init).filter { $0.count > 2 }
        if ta.count < 3 || tb.count < 3 {
            return minL >= 10 && (na.contains(nb) || nb.contains(na))
        }
        let setB = Set(tb)
        let setA = Set(ta)
        var inter = 0
        for w in setA where setB.contains(w) { inter += 1 }
        let denom = min(setA.count, setB.count)
        return denom > 0 && Double(inter) / Double(denom) >= minTokenOverlap
    }

    private static let whyPrefixPatternsLower: [String] = [
        "напряжение дня сейчас в одном месте:",
        "лучше всего день раскрывается через такой режим:",
        "утренний фокус для дня:",
    ]

    static func expansionVariantsForWhyDedup(_ line: String) -> [String] {
        let t = line.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty else { return [] }
        var out = Set<String>([t])
        let lower = t.lowercased()
        for p in whyPrefixPatternsLower where lower.hasPrefix(p) {
            let rest = String(t.dropFirst(p.count)).trimmingCharacters(in: .whitespacesAndNewlines)
            if rest.count >= 4 { out.insert(rest) }
        }
        return Array(out)
    }

    static func lineRedundantWithAny(_ line: String, pool: [String]) -> Bool {
        let variants = expansionVariantsForWhyDedup(line)
        for p in pool {
            let pt = p.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !pt.isEmpty else { continue }
            let pvars = expansionVariantsForWhyDedup(pt)
            for v in variants {
                for x in pvars where textsSemanticallyRedundant(v, x) { return true }
            }
        }
        return false
    }

    static func isDiscardableMorningFocus(_ focus: String?) -> Bool {
        let t = (focus ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if t.count < 2 { return true }
        let junk: Set<String> = ["general", "overall", "mixed", "none", "other", "default", "общее", "прочее", "другое", "без фокуса"]
        if junk.contains(t) { return true }
        if t.count <= 20, t.allSatisfy({ $0.isLetter || $0 == "_" }), t == t.lowercased() { return true }
        return false
    }

    static func pickFirstDistinctLine(candidates: [String], avoid: [String]) -> String {
        for c in candidates {
            let t = c.trimmingCharacters(in: .whitespacesAndNewlines)
            if t.isEmpty || t == "—" { continue }
            if !lineRedundantWithAny(t, pool: avoid) { return t }
        }
        if let fb = candidates.map({ $0.trimmingCharacters(in: .whitespacesAndNewlines) }).first(where: { !$0.isEmpty }) {
            return fb
        }
        return "—"
    }
}
