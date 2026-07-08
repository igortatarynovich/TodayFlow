import Foundation

/// Паритет с `frontend/src/components/today/todayGuideActionable.ts` — поля guide narrative после ритуала.
struct SphereTriadGuideRow: Equatable {
    let area: String
    let stance: String
    let line: String
}

enum TodayGuideActionable {
    /// O2: паритет бэка `narrative_hierarchy` в guide payload (`primary_anchor` = `day_engine_brief`).
    struct NarrativeHierarchyDisplay: Equatable {
        let contractVersion: String
        let primaryAnchorKey: String
    }

    static func narrativeHierarchyDisplay(from payload: [String: JSONValue]?) -> NarrativeHierarchyDisplay? {
        guard let payload, case let .object(h) = payload["narrative_hierarchy"] ?? .null else { return nil }
        guard h["contract_version"]?.stringValue == "narrative_hierarchy_v0" else { return nil }
        guard h["primary_anchor"]?.stringValue == "day_engine_brief" else { return nil }
        return NarrativeHierarchyDisplay(contractVersion: "narrative_hierarchy_v0", primaryAnchorKey: "day_engine_brief")
    }

    /// DE-13 v5: паритет `guide_pipeline` / `guide_contract_v2`.
    struct GuidePipelineDisplay: Equatable {
        let contractVersion: String
        let generationMode: String
        let coreSource: String?
    }

    static func guidePipelineDisplay(from payload: [String: JSONValue]?) -> GuidePipelineDisplay? {
        guard let payload, payload["contract_version"]?.stringValue == "guide_contract_v2" else { return nil }
        guard case let .object(p) = payload["guide_pipeline"] ?? .null else { return nil }
        guard p["contract_version"]?.stringValue == "guide_pipeline_v0" else { return nil }
        let mode = p["generation_mode"]?.stringValue ?? ""
        guard mode == "funnel" || mode == "monolith" else { return nil }
        var coreSource: String?
        if case let .object(steps) = p["steps"] ?? .null,
           case let .object(core) = steps["core_text"] ?? .null {
            coreSource = core["source"]?.stringValue?.trimmingCharacters(in: .whitespacesAndNewlines)
            if coreSource?.isEmpty == true { coreSource = nil }
        }
        return GuidePipelineDisplay(contractVersion: "guide_pipeline_v0", generationMode: mode, coreSource: coreSource)
    }

    /// Паритет с веб `guidePayload.day_engine_brief`: якорь и подсказки для блока «Опора дня».
    struct DayEngineBriefDisplay: Equatable {
        let anchor: String
        let hints: [String]
    }

    static func dayEngineBriefDisplay(from payload: [String: JSONValue]?) -> DayEngineBriefDisplay? {
        guard let payload, case let .object(b) = payload["day_engine_brief"] ?? .null else { return nil }
        let anchor = (b["anchor_summary"]?.stringValue ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !anchor.isEmpty else { return nil }
        var hints: [String] = []
        for key in ["do_hint", "avoid_hint", "tempo_hint"] {
            if let s = b[key]?.stringValue?.trimmingCharacters(in: .whitespacesAndNewlines), !s.isEmpty {
                hints.append(s)
            }
        }
        return DayEngineBriefDisplay(anchor: anchor, hints: hints)
    }

    /// Паритет с веб `parseDayModelBriefFromGuide` — `day_model` (`day_model_v0`), поле `strategy.one_focus`.
    struct DayModelBriefDisplay: Equatable {
        let oneFocus: String
        let vectorSummary: String?
    }

    static func dayModelBriefDisplay(from payload: [String: JSONValue]?) -> DayModelBriefDisplay? {
        guard let payload, case let .object(dm) = payload["day_model"] ?? .null else { return nil }
        guard dm["contract_version"]?.stringValue == "day_model_v0" else { return nil }
        let vectorSummary: String?
        if case let .object(v) = dm["vector"] ?? .null {
            let s = (v["summary"]?.stringValue ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            vectorSummary = s.isEmpty ? nil : s
        } else {
            vectorSummary = nil
        }
        let oneFocus: String
        if case let .object(st) = dm["strategy"] ?? .null {
            let s = (st["one_focus"]?.stringValue ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            guard !s.isEmpty else { return nil }
            oneFocus = s
        } else {
            return nil
        }
        return DayModelBriefDisplay(oneFocus: oneFocus, vectorSummary: vectorSummary)
    }

    /// Паритет с веб `parseCoreMessageForUi`: строка или объект `{ body, risk?, best_move?, headline? }`.
    static func coreMessageDisplayString(from payload: [String: JSONValue]?) -> String {
        guard let raw = payload?["core_message"] else { return "" }
        if case let .string(s) = raw {
            return s.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        if case let .object(o) = raw {
            let body = (o["body"]?.stringValue ?? o["main_text"]?.stringValue ?? o["message"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            guard !body.isEmpty else { return "" }
            var headline = (o["headline"]?.stringValue ?? o["title"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            if headline.isEmpty { headline = "" }
            var risk = (o["risk"]?.stringValue ?? o["main_risk"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            var bestMove = (o["best_move"]?.stringValue ?? o["first_move"]?.stringValue ?? o["action_hint"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            if !headline.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(headline, body) { headline = "" }
            if !risk.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(risk, body) { risk = "" }
            if !bestMove.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(bestMove, body) { bestMove = "" }
            if !risk.isEmpty, !bestMove.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(risk, bestMove) { risk = "" }
            if !bestMove.isEmpty, !headline.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(bestMove, headline) { bestMove = "" }
            var parts: [String] = []
            if !headline.isEmpty { parts.append(headline) }
            parts.append(body)
            if !risk.isEmpty { parts.append("\(TodayRitualCopy.heroRiskLabel): \(risk)") }
            if !bestMove.isEmpty { parts.append("\(TodayRitualCopy.heroBestMoveLabel): \(bestMove)") }
            return parts.joined(separator: "\n\n")
        }
        return ""
    }

    static func coreMessageParagraphs(from payload: [String: JSONValue]?) -> [String] {
        let flat = coreMessageDisplayString(from: payload)
        if flat.isEmpty { return [] }
        return flat
            .components(separatedBy: "\n\n")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .prefix(4)
            .map { String($0) }
    }

    static func parseActionOptions(from payload: [String: JSONValue]?) -> [String] {
        guard let payload, case let .array(items) = payload["action_options"] ?? .null else { return [] }
        var out: [String] = []
        for item in items.prefix(3) {
            if let s = item.stringValue, !s.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                out.append(s.trimmingCharacters(in: .whitespacesAndNewlines))
            } else if case let .object(o) = item {
                let title = (o["title"]?.stringValue ?? o["label"]?.stringValue ?? o["text"]?.stringValue ?? "")
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                if !title.isEmpty { out.append(title) }
            }
        }
        return out
    }

    /// O9: один канонический «главный шаг» — `best_move` → первый `action_options` → первый `do_items` (паритет веб `guideCanonicalPrimaryStepLine`).
    static func guideCanonicalPrimaryStepLine(payload: [String: JSONValue]?, doItems: [String], fallback: String) -> String {
        if let payload, case let .object(o) = payload["core_message"] ?? .null {
            let body = (o["body"]?.stringValue ?? o["main_text"]?.stringValue ?? o["message"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            var bm = (o["best_move"]?.stringValue ?? o["first_move"]?.stringValue ?? o["action_hint"]?.stringValue ?? "")
                .trimmingCharacters(in: .whitespacesAndNewlines)
            if !bm.isEmpty, !body.isEmpty, TodayPersonalDayRhythm.textsSemanticallyRedundant(bm, body) { bm = "" }
            if !bm.isEmpty { return bm }
        }
        let opts = parseActionOptions(from: payload)
        if let f = opts.first { return f }
        if let d = doItems.first(where: { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }) { return d }
        let t = fallback.trimmingCharacters(in: .whitespacesAndNewlines)
        return t.isEmpty ? TodayWebGuideSectionCopy.guidePrimaryDoFallback : t
    }

    static func parseSupportHooks(from payload: [String: JSONValue]?) -> [String] {
        guard let payload, case let .array(items) = payload["support_hooks"] ?? .null else { return [] }
        return items.compactMap { $0.stringValue }.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }.prefix(3).map { String($0) }
    }

    static func parseSphereTriad(from payload: [String: JSONValue]?) -> [SphereTriadGuideRow]? {
        guard let payload, case let .array(items) = payload["sphere_triad"] ?? .null, items.count == 3 else { return nil }
        var rows: [SphereTriadGuideRow] = []
        for item in items {
            guard case let .object(o) = item else { return nil }
            let area = (o["area"]?.stringValue ?? "").lowercased()
            let stance = (o["stance"]?.stringValue ?? "").lowercased()
            let line = o["line"]?.stringValue?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            guard ["work", "love", "money"].contains(area), ["up", "down", "neutral"].contains(stance), line.count > 4 else { return nil }
            rows.append(SphereTriadGuideRow(area: area, stance: stance, line: line))
        }
        guard Set(rows.map(\.area)).count == 3 else { return nil }
        return rows
    }
}
