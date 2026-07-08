import Foundation

/// Сигналы «возможно / избегать / опоры» для ритуала Today. Паритет с `frontend/src/components/today/todayRitualSignals.ts`.
enum TodayRitualSignals {
    static let guidanceFallback = "Открой день одним действием, которое убирает шум."

    /// Паритет с `buildDayEnergySummary` в `todayPageUtils.ts` (поле `guidance`).
    static func dayEnergyGuidanceLine(score: Int) -> String {
        let s = min(100, max(0, score))
        if s <= 30 {
            return "Сбавь темп и двигайся короткими шагами."
        }
        if s <= 70 {
            return "Держи ровный темп и закрывай задачи по одной."
        }
        return "Ресурса больше обычного. Держи фокус на главном."
    }

    /// Паритет с `guideHeadline` на вебе: первый сегмент до `[.!?]\\s+`, иначе префикс 140 символов.
    static func guideHeadlineSegment(fromForecastSummary summary: String) -> String {
        let trimmed = summary.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return "" }
        guard let regex = try? NSRegularExpression(pattern: "[.!?]\\s+", options: []) else {
            return String(trimmed.prefix(140))
        }
        let range = NSRange(trimmed.startIndex ..< trimmed.endIndex, in: trimmed)
        guard let match = regex.firstMatch(in: trimmed, options: [], range: range), match.range.location > 0 else {
            return String(trimmed.prefix(140))
        }
        let head = (trimmed as NSString).substring(with: NSRange(location: 0, length: match.range.location))
        let h = head.trimmingCharacters(in: .whitespacesAndNewlines)
        return h.isEmpty ? String(trimmed.prefix(140)) : h
    }

    static func possible(from morning: TodayMorning?) -> [String] {
        var a: [String] = []
        let wtd = TodayRitualCueSanitizer.replaceQuotedEnSlugsForRuDisplay(
            morning?.dailyRecommendations?.whatToDo?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        )
        if !wtd.isEmpty, !TodayRitualCueSanitizer.isGarbageRitualActionCue(wtd) { a.append(wtd) }
        let fm = TodayRitualCueSanitizer.replaceQuotedEnSlugsForRuDisplay(
            morning?.dailyHoroscope?.spine?.firstMove?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        )
        if !fm.isEmpty, !TodayRitualCueSanitizer.isGarbageRitualActionCue(fm), !a.contains(fm) { a.append(fm) }
        let summary = TodayRitualCueSanitizer.replaceQuotedEnSlugsForRuDisplay(
            morning?.dailyForecastSummary?.summary?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        )
        if !summary.isEmpty, !TodayRitualCueSanitizer.isGarbageRitualActionCue(summary), a.count < 3 { a.append(summary) }
        return Array(a.prefix(3))
    }

    static func avoid(from morning: TodayMorning?) -> [String] {
        var a: [String] = []
        let wta = TodayRitualCueSanitizer.replaceQuotedEnSlugsForRuDisplay(
            morning?.dailyRecommendations?.whatToAvoid?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        )
        if !wta.isEmpty { a.append(wta) }
        let dneRaw = morning?.dailyHoroscope?.spine?.doNotEnter?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let dne = TodayRitualCueSanitizer.repairRitualDoNotEnterLine(dneRaw)
        if !dne.isEmpty, !a.contains(dne) { a.append(dne) }
        return a
    }

    /// При непустом `bestMode` — три строки; иначе одна опора (`guidanceSummary` с дашборда, как на вебе).
    static func support(bestMode: String, guidanceSummary: String) -> [String] {
        let b = bestMode.trimmingCharacters(in: .whitespacesAndNewlines)
        if !b.isEmpty { return [b, "Тишина", "Структура"] }
        let g = guidanceSummary.trimmingCharacters(in: .whitespacesAndNewlines)
        return [g.isEmpty ? Self.guidanceFallback : g]
    }
}

// MARK: - «Почему так?» — строки как на вебе (`TodayRitualFlow.tsx` → `buildWhyReasonLines`)

enum TodayRitualWhyReasonLines {
    /// Тот же порядок кандидатов и фильтры дубликатов, что в `frontend/.../TodayRitualFlow.tsx`.
    static func build(
        summaryTitle: String,
        possible: [String],
        guidePayload: [String: JSONValue]?,
        spineMainRisk: String?,
        spineBestMode: String?,
        numerologyDisplayValue: String,
        numerologyReduced: Int?,
        numerologyDetailLine: String?,
        morningFocus: String?,
        whyMoon: String?,
        whyLunar: String?,
        avoidLines: [String]
    ) -> (headline: String?, lines: [String]) {
        let rawHeadline = narrativeString(guidePayload, "headline") ?? narrativeString(guidePayload, "focus_line")
        let headline: String?
        if let h = rawHeadline, !TodayPersonalDayRhythm.lineRedundantWithAny(h, pool: avoidLines) {
            headline = h
        } else {
            headline = nil
        }

        var candidates: [String] = []

        let phaseLabel = TodayPersonalDayRhythm.normalizeLunarPhaseLabel(whyMoon)
        let themes = whyLunar?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        var moonBlock = ""
        if !themes.isEmpty, let p = phaseLabel, !p.isEmpty {
            moonBlock = "\(themes) · \(p)"
        } else if !themes.isEmpty {
            moonBlock = themes
        } else if let p = phaseLabel {
            moonBlock = p
        }

        let lunarInf = narrativeString(guidePayload, "lunar_influence")
        if let lunarInf, !moonBlock.isEmpty, TodayPersonalDayRhythm.lunarInfluenceRedundantWithAstronomy(lunarInf, moonBlock: moonBlock) {
            candidates.append(clipWhyLine(moonBlock, maxLen: 420))
        } else if let lunarInf, !moonBlock.isEmpty {
            candidates.append(clipWhyLine(moonBlock, maxLen: 420))
            if !TodayPersonalDayRhythm.lunarInfluenceRedundantWithAstronomy(lunarInf, moonBlock: moonBlock) {
                candidates.append(clipWhyLine(lunarInf, maxLen: 420))
            }
        } else if let lunarInf {
            candidates.append(clipWhyLine(lunarInf, maxLen: 420))
        } else if !moonBlock.isEmpty {
            candidates.append(clipWhyLine(moonBlock, maxLen: 420))
        }

        if let risk = spineMainRisk?.trimmingCharacters(in: .whitespacesAndNewlines), !risk.isEmpty {
            candidates.append("Напряжение дня сейчас в одном месте: \(risk)")
        }
        if let best = spineBestMode?.trimmingCharacters(in: .whitespacesAndNewlines), !best.isEmpty {
            candidates.append("Лучше всего день раскрывается через такой режим: \(best)")
        }
        if let transit = narrativeString(guidePayload, "transit_influence") {
            candidates.append(clipWhyLine(transit, maxLen: 420))
        }
        let detail = numerologyDetailLine?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if detail.count >= 36 {
            candidates.append(clipWhyLine(detail, maxLen: 420))
        } else {
            candidates.append(TodayPersonalDayRhythm.personalDayRhythmLine(reduced: numerologyReduced, displayValue: numerologyDisplayValue))
        }
        if let nextAction = narrativeString(guidePayload, "next_action") {
            candidates.append(nextAction)
        }
        if let focus = morningFocus?.trimmingCharacters(in: .whitespacesAndNewlines), !focus.isEmpty,
           !TodayPersonalDayRhythm.isDiscardableMorningFocus(focus) {
            candidates.append("Утренний фокус для дня: \(focus)")
        }
        if let nudge = narrativeString(guidePayload, "nudge_message") {
            candidates.append(nudge)
        }

        var seenNorms = Set<String>()
        var filtered: [String] = []
        let avoidPool = avoidLines.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        for line in candidates {
            let t = line.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !t.isEmpty else { continue }
            guard !isDuplicateWhyLine(line: t, summaryTitle: summaryTitle, possible: possible) else { continue }
            let norm = normalizeWhy(t)
            guard !seenNorms.contains(norm) else { continue }
            guard !TodayPersonalDayRhythm.lineRedundantWithAny(t, pool: avoidPool + filtered) else { continue }
            seenNorms.insert(norm)
            filtered.append(t)
        }

        var outHeadline = headline
        if let h = outHeadline, TodayPersonalDayRhythm.lineRedundantWithAny(h, pool: filtered) {
            outHeadline = nil
        }
        return (outHeadline, Array(filtered.prefix(5)))
    }

    private static func clipWhyLine(_ s: String, maxLen: Int) -> String {
        let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
        if t.count <= maxLen { return t }
        let idx = t.index(t.startIndex, offsetBy: max(0, maxLen - 1))
        return String(t[..<idx]) + "…"
    }

    private static func narrativeString(_ payload: [String: JSONValue]?, _ key: String) -> String? {
        guard let raw = payload?[key]?.stringValue else { return nil }
        let s = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return s.isEmpty ? nil : s
    }

    private static func normalizeWhy(_ s: String) -> String {
        let trimmed = s.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard let regex = try? NSRegularExpression(pattern: "\\s+", options: []) else {
            return trimmed
        }
        let range = NSRange(trimmed.startIndex ..< trimmed.endIndex, in: trimmed)
        return regex.stringByReplacingMatches(in: trimmed, options: [], range: range, withTemplate: " ")
    }

    private static func isDuplicateWhyLine(line: String, summaryTitle: String, possible: [String]) -> Bool {
        let n = normalizeWhy(line)
        guard n.count >= 14 else { return false }
        let sum = normalizeWhy(summaryTitle)
        if sum.count > 10 {
            let sumPrefixLen = min(52, sum.count)
            let nPrefixLen = min(52, n.count)
            let sumPrefix = String(sum.prefix(sumPrefixLen))
            let nPrefix = String(n.prefix(nPrefixLen))
            if n == sum || n.contains(sumPrefix) || sum.contains(nPrefix) {
                return true
            }
        }
        for p in possible {
            let pn = normalizeWhy(p)
            guard pn.count > 12 else { continue }
            if n == pn { return true }
            if pn.count > 20, n.contains(pn) { return true }
            if n.count > 20, pn.contains(n) { return true }
        }
        return false
    }
}
