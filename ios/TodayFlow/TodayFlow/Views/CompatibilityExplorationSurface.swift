import SwiftUI

// MARK: - Learning micro-echo (web ↔ iOS parity)

enum BlockEcho: String, CaseIterable {
    case yes
    case partial
    case no

    var label: String {
        switch self {
        case .yes: return CompatibilityScreenChrome.echoYes
        case .partial: return CompatibilityScreenChrome.echoPartial
        case .no: return CompatibilityScreenChrome.echoNo
        }
    }
}

private let compatibilityDeepBlockKeys: Set<String> = [
    "emotions", "communication", "conflicts", "sexuality", "long_term",
]

struct SignCompatibilityLearningContext {
    let store: TodayFlowStore
    let surface: String
    let formatId: String?
    let scenarioId: String?
    let fromSign: String?
    let toSign: String?
    let score: Double?
    var echoByTarget: Binding<[String: BlockEcho]>
    var blockFeedback: Binding<[String: BlockEcho]>
    var deepOpenTracked: Binding<Bool>
    var onRebuild: (() -> Void)?
    var isRebuilding: Bool = false

    func trackEcho(target: String, echo: BlockEcho) async {
        if target.hasPrefix("deep:") {
            let key = String(target.dropFirst("deep:".count))
            if compatibilityDeepBlockKeys.contains(key) {
                await MainActor.run {
                    blockFeedback.wrappedValue[key] = echo
                }
            }
        }
        await MainActor.run {
            echoByTarget.wrappedValue[target] = echo
        }
        var payload: [String: JSONValue] = [
            "surface": .string(surface),
            "target": .string(target),
            "echo": .string(echo.rawValue),
        ]
        if let formatId { payload["format_id"] = .string(formatId) }
        if let scenarioId { payload["scenario_id"] = .string(scenarioId) }
        if target.hasPrefix("deep:") {
            let key = String(target.dropFirst("deep:".count))
            if compatibilityDeepBlockKeys.contains(key) {
                payload["block_key"] = .string(key)
            }
        }
        if let fromSign { payload["from_sign"] = .string(fromSign) }
        if let toSign { payload["to_sign"] = .string(toSign) }
        if let score { payload["score"] = .number(score) }
        await store.trackCompatibilityEvent(eventType: "compatibility_echo", payload: payload)
    }

    func trackDeepOpen() async {
        guard !deepOpenTracked.wrappedValue else { return }
        await MainActor.run { deepOpenTracked.wrappedValue = true }
        var payload: [String: JSONValue] = ["surface": .string(surface)]
        if let formatId { payload["format_id"] = .string(formatId) }
        if let scenarioId { payload["scenario_id"] = .string(scenarioId) }
        await store.trackCompatibilityEvent(eventType: "compatibility_deep_open", payload: payload)
    }

    func trackScenarioSwitch(toScenarioId: String) async {
        var payload: [String: JSONValue] = [
            "surface": .string(surface),
            "from_scenario_id": .string(scenarioId ?? ""),
            "to_scenario_id": .string(toScenarioId),
            "format_id": .string(toScenarioId),
        ]
        await store.trackCompatibilityEvent(eventType: "compatibility_scenario_switch", payload: payload)
    }
}

struct CompatibilityMicroEchoView: View {
    let label: String
    let selected: BlockEcho?
    let onSelect: (BlockEcho) -> Void

    @State private var showGiveback = false

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            HStack(spacing: 8) {
                ForEach(BlockEcho.allCases, id: \.rawValue) { opt in
                    Button {
                        onSelect(opt)
                        showGiveback = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2.4) {
                            showGiveback = false
                        }
                    } label: {
                        Text(opt.label)
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                            .background(
                                Capsule()
                                    .fill(selected == opt ? TodayFlowTheme.sunset.opacity(0.18) : Color.white.opacity(0.55))
                            )
                            .overlay(
                                Capsule()
                                    .stroke(selected == opt ? TodayFlowTheme.sunset.opacity(0.75) : TodayFlowTheme.gold.opacity(0.28), lineWidth: 1)
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
            if showGiveback {
                Text(CompatibilityScreenChrome.echoGiveback)
                    .font(.caption2)
                    .foregroundStyle(Color.green.opacity(0.85))
            }
        }
    }
}

// MARK: - Scenario skins (mirrors web `compatibilityScenarioSkins.ts`)

enum CompatibilitySubscoreKey: String, CaseIterable {
    case attraction
    case stability
    case conflicts
    case sexuality
}

struct CompatibilityScenarioDimension {
    let key: CompatibilitySubscoreKey
    let emoji: String
    let label: String
}

struct CompatibilityScenarioSkin {
    let id: String
    let emoji: String
    let title: String
    let poster: String
    let posterSubtitle: String
    let tone: String
    let dimensionLabels: [CompatibilityScenarioDimension]
    let continuationIds: [String]

    var isPlayful: Bool { CompatibilityScenarioRegistry.playfulScenarioIds.contains(id) }
}

private enum CompatibilityExplorationChrome {
    static var isRu: Bool { CompatibilityScreenChrome.useRussian }

    static var investigation: String { CompatibilityScreenChrome.analyzeInvestigation }
    static var mainThought: String { isRu ? "Главная мысль" : "Main thought" }
    static var tomorrow: String {
        isRu ? "Что произойдёт, если сценарий случится завтра?" : "If this scenario happened tomorrow?"
    }
    static var strongestResource: String { isRu ? "💎 Самый сильный ресурс" : "💎 Strongest resource" }
    static var mainRisk: String { isRu ? "⚠ Главный риск" : "⚠ Main risk" }
    static var tipsTitle: String { isRu ? "Что поможет именно вам" : "What helps you two" }
    static var deepTitle: String { isRu ? "Глубокий разбор" : "Deep dive" }
    static var deepCta: String { isRu ? "Посмотреть глубже" : "Go deeper" }
    static var deepCtaHint: String {
        isRu ? "Длинный разбор — только если захочешь копать дальше." : "Long read — only if you want more."
    }
    static var continuationTitle: String {
        isRu ? "Попробуйте посмотреть вашу пару в других сценариях" : "Try your pair in other scenarios"
    }
    static var continuationLead: String {
        isRu ? "Это не конец — продолжение исследования." : "Not the end — keep exploring."
    }
    static var ringLabel: String { isRu ? "совместимость" : "match" }

    static func scoreLabel(_ score: Int) -> String {
        if score >= 82 { return isRu ? "Сильная связь" : "Strong bond" }
        if score >= 68 { return isRu ? "Хороший потенциал" : "Good potential" }
        if score >= 58 { return isRu ? "Нужна настройка" : "Needs tuning" }
        return isRu ? "Сложная динамика" : "Complex dynamic"
    }

    static func scenarioScoreLabel(scenarioId: String, score: Int) -> String {
        let band = score >= 82 ? "high" : score >= 68 ? "mid" : "low"
        let ru: [String: [String: String]] = [
            "love": ["high": "Сильная близость", "mid": "Хороший потенциал любви", "low": "Нужна настройка чувств"],
            "sex": ["high": "Сильная химия", "mid": "Химия с нюансами", "low": "Телесный слой требует внимания"],
            "office": ["high": "Сильная рабочая синергия", "mid": "Работаете, но с трением", "low": "Сложная командная динамика"],
            "living_together": ["high": "Быт держит", "mid": "Быт с настройкой", "low": "Дом может быть полем битвы"],
            "vacation": ["high": "Dream team в пути", "mid": "Отпуск выживете", "low": "Лучше раздельные маршруты"],
            "money_together": ["high": "Финансовый союз", "mid": "Деньги — зона договорённостей", "low": "Деньги — зона риска"],
            "parenting": ["high": "Сильная родительская команда", "mid": "Родительство с компромиссами", "low": "Разные модели воспитания"],
            "conflict_style": ["high": "Ссоры не застревают", "mid": "Конфликты управляемы", "low": "Жёсткий конфликтный цикл"],
            "apocalypse": ["high": "Держитесь в кризисе", "mid": "Кризис — стресс-тест", "low": "Под давлением — хрупко"],
        ]
        let en: [String: [String: String]] = [
            "love": ["high": "Strong closeness", "mid": "Good love potential", "low": "Feelings need tuning"],
            "office": ["high": "Strong work synergy", "mid": "Works, with friction", "low": "Tough team dynamic"],
        ]
        let table = isRu ? ru : en
        return table[scenarioId]?[band] ?? scoreLabel(score)
    }
}

enum CompatibilityScenarioRegistry {
    static let playfulScenarioIds: Set<String> = [
        "living_together", "vacation", "partner_in_crime", "after_wine",
        "home_renovation", "best_friends", "rule_breaker",
    ]

    private static let defaultDimensions: [CompatibilityScenarioDimension] = [
        .init(key: .attraction, emoji: "✨", label: CompatibilityExplorationChrome.isRu ? "Притяжение" : "Attraction"),
        .init(key: .stability, emoji: "🤝", label: CompatibilityExplorationChrome.isRu ? "Стабильность" : "Stability"),
        .init(key: .conflicts, emoji: "⚔", label: CompatibilityExplorationChrome.isRu ? "Конфликты" : "Conflicts"),
        .init(key: .sexuality, emoji: "🔥", label: CompatibilityExplorationChrome.isRu ? "Интимность" : "Intimacy"),
    ]

    private static let topicToScenario: [String: String] = [
        "love": "love",
        "living_together": "living_together",
        "living": "living_together",
        "work": "office",
        "sex": "sex",
        "money": "money_together",
        "parenting": "parenting",
        "travel": "vacation",
        "conflicts": "conflict_style",
        "communication": "conflict_style",
        "friendship": "best_friends",
        "emotional": "love",
        "growth": "love",
    ]

    private static let skins: [CompatibilityScenarioSkin] = [
        skin("love", "❤️", posterSub: CompatibilityExplorationChrome.isRu
            ? "Притяжение, нежность и то, что для каждого значит «быть рядом»."
            : "Attraction, tenderness, and what «being together» means.",
             dims: [("💫", "Притяжение"), ("🤍", "Близость"), ("🌊", "Эмоциональные волны"), ("🔥", "Страсть")],
             cont: ["living_together", "conflict_style", "sex", "vacation"]),
        skin("living_together", "🏡", posterSub: CompatibilityExplorationChrome.isRu
            ? "Быт, границы и ритм двоих — без иллюзий про «идеальный дом»."
            : "Daily life, boundaries, and rhythm — no perfect-home fantasy.",
             dims: [("🏠", "Быт"), ("🧦", "Мелкие войны"), ("☕", "Уют"), ("🛋", "Тепло")],
             cont: ["money_together", "conflict_style", "partner_in_crime", "love"]),
        skin("office", "💼", posterSub: CompatibilityExplorationChrome.isRu
            ? "Роли, темп и давление — когда вы не только пара, но и команда."
            : "Roles, pace, and pressure — when you're also a team.",
             dims: [("📋", "Надёжность"), ("📧", "Трения"), ("🎯", "Синергия"), ("⚡", "Энергия")],
             cont: ["conflict_style", "money_together", "love", "vacation"]),
        skin("sex", "🔥", posterSub: CompatibilityExplorationChrome.isRu
            ? "Химия, темп и то, что происходит между вами наедине — прямо и по делу."
            : "Chemistry, pace, and what happens between you in private — direct and useful.",
             dims: [("🔥", "Искра"), ("💫", "Притяжение"), ("🌙", "Ритм"), ("🤍", "Доверие")],
             cont: ["love", "living_together", "conflict_style", "vacation"]),
        skin("vacation", "✈️", posterSub: CompatibilityExplorationChrome.isRu
            ? "Отпуск как стресс-тест: кто планирует, кто импровизирует, кто устает первым."
            : "Vacation as stress test: planner vs improviser, who tires first.",
             dims: [("🧳", "Логистика"), ("🌴", "Отдых"), ("📸", "Впечатления"), ("😅", "Срывы")],
             cont: ["living_together", "partner_in_crime", "love", "after_wine"]),
        skin("money_together", "💰", posterSub: CompatibilityExplorationChrome.isRu
            ? "Деньги как зеркало ценностей — не табoo, а язык договорённостей."
            : "Money mirrors values — agreements, not taboo.",
             dims: [("💳", "Привычки"), ("📊", "План"), ("⚖", "Справедливость"), ("🎯", "Цели")],
             cont: ["living_together", "office", "conflict_style", "love"]),
        skin("parenting", "👶", posterSub: CompatibilityExplorationChrome.isRu
            ? "Роли родителей, усталость и поддержка — когда появляется третий «участник»."
            : "Parent roles, fatigue, and support — when a third joins.",
             dims: [("🍼", "Ритм"), ("🛏", "Сон"), ("🤝", "Команда"), ("💬", "Разговоры")],
             cont: ["living_together", "conflict_style", "love", "family"]),
        skin("conflict_style", "⚡", posterSub: CompatibilityExplorationChrome.isRu
            ? "Как вы ссоритесь, миритесь и возвращаетесь друг к другу."
            : "How you fight, repair, and come back.",
             dims: [("🌊", "Волны"), ("🧯", "Починка"), ("🤐", "Молчание"), ("🔥", "Вспышки")],
             cont: ["love", "living_together", "office", "sex"]),
        skin("partner_in_crime", "🎭", posterSub: CompatibilityExplorationChrome.isRu
            ? "Союз авантюристов — риск, драйв и «мы против мира»."
            : "Partners in adventure — risk, drive, us vs the world.",
             dims: [("🎲", "Риск"), ("😏", "Игра"), ("🚀", "Драйв"), ("🤝", "Лояльность")],
             cont: ["vacation", "after_wine", "rule_breaker", "love"]),
        skin("after_wine", "🍷", posterSub: CompatibilityExplorationChrome.isRu
            ? "Честность, флирт, споры и смешные решения — когда фильтры ослабевают."
            : "Honesty, flirt, spats, silly decisions — filters off.",
             dims: [("😏", "Флирт"), ("🙊", "Правда"), ("🍷", "Уют"), ("✨", "Искра")],
             cont: ["partner_in_crime", "best_friends", "rule_breaker", "love"]),
        skin("best_friends", "😂", posterSub: CompatibilityExplorationChrome.isRu
            ? "Дружба без романтики — но с химией и своими правилами."
            : "Friendship without romance — still chemistry and rules.",
             dims: [("🤝", "Опора"), ("😄", "Лёгкость"), ("👀", "Ревность"), ("🚫", "Граница")],
             cont: ["partner_in_crime", "after_wine", "vacation", "office"]),
        skin("rule_breaker", "🕵", posterSub: CompatibilityExplorationChrome.isRu
            ? "Игровой сценарий: ставки приняты, дисциплина под вопросом."
            : "Play mode: bets are on, discipline questionable.",
             dims: [("🎲", "Ставки"), ("😈", "Нарушение"), ("🤫", "Секрет"), ("😅", "Последствия")],
             cont: ["after_wine", "partner_in_crime", "living_together", "office"]),
        skin("apocalypse", "🌋", posterSub: CompatibilityExplorationChrome.isRu
            ? "Кризис как катализатор — кто держит, кто паникует, кто тащит."
            : "Crisis as catalyst — who holds, panics, carries.",
             dims: [("🛡", "Опора"), ("🏃", "Реакция"), ("🧭", "План"), ("💥", "Стресс")],
             cont: ["conflict_style", "living_together", "love", "office"]),
    ]

    private static let skinById: [String: CompatibilityScenarioSkin] = {
        Dictionary(uniqueKeysWithValues: skins.map { ($0.id, $0) })
    }()

    private static func skin(
        _ id: String,
        _ emoji: String,
        posterSub: String,
        dims: [(String, String)],
        cont: [String]
    ) -> CompatibilityScenarioSkin {
        let keys = CompatibilitySubscoreKey.allCases
        let dimensions = dims.enumerated().map { idx, pair in
            CompatibilityScenarioDimension(
                key: keys[min(idx, keys.count - 1)],
                emoji: pair.0,
                label: pair.1
            )
        }
        return CompatibilityScenarioSkin(
            id: id,
            emoji: emoji,
            title: id.replacingOccurrences(of: "_", with: " ").capitalized,
            poster: id == "love"
                ? (CompatibilityExplorationChrome.isRu ? "Любовь" : "Love")
                : id.replacingOccurrences(of: "_", with: " ").capitalized,
            posterSubtitle: posterSub,
            tone: id,
            dimensionLabels: dimensions.count == 4 ? dimensions : defaultDimensions,
            continuationIds: cont
        )
    }

    static func resolveScenarioId(topic: String?, series: String?, reading: String?) -> String {
        if let series, skinById[series] != nil { return series }
        if let topic, let mapped = topicToScenario[topic] { return mapped }
        return "love"
    }

    static func skin(for id: String) -> CompatibilityScenarioSkin {
        skinById[id] ?? skinById["love"]!
    }

    static func continuations(for id: String) -> [CompatibilityScenarioSkin] {
        skin(for: id).continuationIds.compactMap { skinById[$0] }.prefix(6).map { $0 }
    }

    static func formatFromRelationMode(_ mode: String, override: String?) -> String {
        if let override, skinById[override] != nil { return override }
        switch mode {
        case "business": return "office"
        case "parent_child": return "parenting"
        case "family": return "living_together"
        default: return "love"
        }
    }

    private static let attachmentBlockToSlot: [String: CompatibilitySubscoreKey] = [
        "emotions": .stability,
        "communication": .conflicts,
        "conflicts": .conflicts,
        "sexuality": .sexuality,
        "long_term": .attraction,
    ]

    private static let pairDeepSource: [CompatibilitySubscoreKey: [String]] = [
        .attraction: ["attraction", "long_term"],
        .stability: ["stability", "emotional"],
        .conflicts: ["communication", "emotional"],
        .sexuality: ["attraction", "long_term"],
    ]

    static func pairDeepSourceKeys(for key: CompatibilitySubscoreKey) -> [String] {
        pairDeepSource[key] ?? [key.rawValue]
    }

    static func orderedDimensionLabels(
        skin: CompatibilityScenarioSkin,
        deepBlockOrder: [String]?
    ) -> [CompatibilityScenarioDimension] {
        guard let order = deepBlockOrder, !order.isEmpty else {
            return skin.dimensionLabels
        }
        var slots: [CompatibilitySubscoreKey] = []
        for block in order {
            if let slot = attachmentBlockToSlot[block.lowercased()], !slots.contains(slot) {
                slots.append(slot)
            }
        }
        for dim in skin.dimensionLabels where !slots.contains(dim.key) {
            slots.append(dim.key)
        }
        return slots.compactMap { key in skin.dimensionLabels.first(where: { $0.key == key }) }
    }
}

// MARK: - Exploration model

struct CompatibilityExplorationDimension: Identifiable, Hashable {
    let id: String
    let emoji: String
    let label: String
    let score: Int
    var quip: String?
}

struct CompatibilityExplorationDeepSection: Identifiable, Hashable {
    let id: String
    let title: String
    let subtitle: String
    let takeaway: String
    let detail: String
    let risk: String
    let action: String
}

struct CompatibilityExplorationModel {
    let scenarioId: String
    let scenarioPoster: String
    let scenarioSubtitle: String
    let pairLine: String
    let score: Int
    let scoreLabel: String
    let mainThought: String
    let dimensions: [CompatibilityExplorationDimension]
    let narrative: [String]
    let strongestResource: String
    let mainRisk: String
    let tips: [String]
    let deepSections: [CompatibilityExplorationDeepSection]
    let continuations: [CompatibilityScenarioSkin]
    let isPlayful: Bool
    let playfulDisclaimer: String?
}

private enum CompatibilityPlayfulStats {
    static func scoreLabel(scenarioId: String, score: Int) -> String {
        let band = score >= 72 ? "high" : score >= 52 ? "mid" : "low"
        let labels: [String: [String: String]] = [
            "partner_in_crime": ["high": "Союз авантюристов", "mid": "Осторожные напарники", "low": "Лучше не в одной машине"],
            "after_wine": ["high": "Вечер точно запомнится", "mid": "Будет смешно — потом", "low": "Лучше без третьего бокала"],
            "rule_breaker": ["high": "Оба нарушите — вопрос кто первый", "mid": "Ставки приняты", "low": "Слишком правильные для сценария"],
        ]
        return labels[scenarioId]?[band] ?? (band == "high" ? "Статистика на вашей стороне" : band == "mid" ? "50 на 50" : "Цифры просят другой сценарий")
    }

    static func quip(scenarioId: String, key: CompatibilitySubscoreKey, score: Int) -> String {
        let band = score >= 72 ? "high" : score >= 52 ? "mid" : "low"
        let table: [String: [CompatibilitySubscoreKey: [String: String]]] = [
            "partner_in_crime": [
                .attraction: ["high": "Готовы к безумию без прогрева", "mid": "Риск есть, но кто-то спросит «точно?»", "low": "Скучнее очереди"],
                .stability: ["high": "План «Б» найдётся в 3 ночи", "mid": "Один тащит, второй «морально»", "low": "«Это был не я»"],
                .conflicts: ["high": "Спор, кто первым полез в огонь", "mid": "Чья идея была хуже", "low": "Даже спорить ленитесь"],
                .sexuality: ["high": "Адреналин + химия", "mid": "Искра не всегда вовремя", "low": "Больше напарники"],
            ],
            "after_wine": [
                .attraction: ["high": "Флирт после второго бокала", "mid": "Флирт через «ну ладно, один»", "low": "Awkward silence"],
                .conflicts: ["high": "Правда быстрее закуски", "mid": "Утром отрицаете", "low": "Фильтры держатся"],
            ],
        ]
        return table[scenarioId]?[key]?[band] ?? ""
    }
}

enum CompatibilityExplorationModelBuilder {
    static func fromDynamics(
        response: SignCompatibilityAPIResponse,
        selection: CompatibilityEncyclopediaAnalyzeSelection
    ) -> CompatibilityExplorationModel? {
        guard let surface = response.productSurface else { return nil }
        let scenarioId = CompatibilityScenarioRegistry.resolveScenarioId(
            topic: selection.topicId,
            series: selection.seriesId,
            reading: selection.readingId
        )
        let skin = CompatibilityScenarioRegistry.skin(for: scenarioId)
        let subs = surface.subscores

        let dimensions = skin.dimensionLabels.map { dim -> CompatibilityExplorationDimension in
            let score: Int
            switch dim.key {
            case .attraction: score = subs.attraction
            case .stability: score = subs.stability
            case .conflicts: score = subs.conflicts
            case .sexuality: score = subs.sexuality
            }
            let quip = skin.isPlayful ? CompatibilityPlayfulStats.quip(scenarioId: scenarioId, key: dim.key, score: score) : nil
            return CompatibilityExplorationDimension(
                id: dim.key.rawValue,
                emoji: dim.emoji,
                label: dim.label,
                score: score,
                quip: quip?.isEmpty == false ? quip : nil
            )
        }

        if skin.isPlayful {
            let sorted = dimensions.sorted { $0.score > $1.score }
            let top = sorted.first
            let low = sorted.last
            let disclaimer = CompatibilityExplorationChrome.isRu
                ? "Шуточная статистика — не серьёзный разбор отношений."
                : "Playful stats — not a serious relationship reading."
            return CompatibilityExplorationModel(
                scenarioId: scenarioId,
                scenarioPoster: skin.poster,
                scenarioSubtitle: skin.posterSubtitle,
                pairLine: "\(response.fromSignName) × \(response.toSignName)",
                score: response.score,
                scoreLabel: CompatibilityPlayfulStats.scoreLabel(scenarioId: scenarioId, score: response.score),
                mainThought: surface.scoreTagline,
                dimensions: dimensions,
                narrative: Array(surface.overviewParagraphs.prefix(1)),
                strongestResource: top.map { "\($0.emoji) \($0.label): \($0.score)% — \($0.quip ?? "")" } ?? "",
                mainRisk: low.map { "\($0.emoji) \($0.label): \($0.score)% — \($0.quip ?? "")" } ?? "",
                tips: [],
                deepSections: [],
                continuations: CompatibilityScenarioRegistry.continuations(for: scenarioId),
                isPlayful: true,
                playfulDisclaimer: disclaimer
            )
        }

        let strengthBlock = surface.blocks.first(where: { $0.key == "attraction" }) ?? surface.blocks.first
        let conflictBlock = surface.blocks.first(where: { $0.key == "conflicts" }) ?? surface.blocks.dropFirst().first

        var tips: [String] = []
        var seen = Set<String>()
        for block in surface.blocks {
            if block.key == "sexuality", !block.resolvedTips.isEmpty {
                for tip in block.resolvedTips {
                    let trimmed = tip.trimmingCharacters(in: .whitespacesAndNewlines)
                    guard !trimmed.isEmpty else { continue }
                    let key = trimmed.lowercased()
                    if seen.contains(key) { continue }
                    seen.insert(key)
                    tips.append(trimmed)
                }
            }
            let action = block.action.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !action.isEmpty else { continue }
            let key = action.lowercased()
            if seen.contains(key) { continue }
            seen.insert(key)
            tips.append(action)
            if tips.count >= 5 { break }
        }
        if tips.isEmpty {
            tips = CompatibilityExplorationChrome.isRu
                ? ["Проясняйте ожидания заранее.", "Договаривайтесь о ролях в стрессе.", "Возвращайтесь к разговору."]
                : ["Clarify expectations early.", "Agree on roles under stress.", "Return to talk, not silence."]
        }

        let deepSections = surface.blocks.map {
            CompatibilityExplorationDeepSection(
                id: $0.key,
                title: $0.title,
                subtitle: $0.subtitle,
                takeaway: $0.takeaway,
                detail: $0.detail,
                risk: $0.risk,
                action: $0.action
            )
        }

        return CompatibilityExplorationModel(
            scenarioId: scenarioId,
            scenarioPoster: skin.poster,
            scenarioSubtitle: skin.posterSubtitle,
            pairLine: "\(response.fromSignName) × \(response.toSignName)",
            score: response.score,
            scoreLabel: CompatibilityExplorationChrome.scenarioScoreLabel(scenarioId: scenarioId, score: response.score),
            mainThought: surface.scoreTagline,
            dimensions: dimensions,
            narrative: Array(surface.overviewParagraphs.prefix(3)),
            strongestResource: strengthBlock?.takeaway ?? (CompatibilityExplorationChrome.isRu
                ? "Есть зона, где контакт даётся естественнее — опирайтесь на неё."
                : "There is a zone where contact comes easier — lean on it."),
            mainRisk: conflictBlock?.risk ?? conflictBlock?.takeaway ?? (CompatibilityExplorationChrome.isRu
                ? "Главный риск — повторяющийся сценарий без проговаривания."
                : "Main risk — repeating the same loop without naming it."),
            tips: tips,
            deepSections: deepSections,
            continuations: CompatibilityScenarioRegistry.continuations(for: scenarioId),
            isPlayful: false,
            playfulDisclaimer: nil
        )
    }

    static func fromPairCompare(
        result: CompatibilityComparisonResponse,
        formatId: String
    ) -> CompatibilityExplorationModel {
        let scenarioId = result.scenarioContext?.formatId ?? formatId
        let skin = CompatibilityScenarioRegistry.skin(for: scenarioId)
        let comp = result.compatibility
        let deep = comp.deepDive
        let editorial = comp.editorial
        let displayScore = result.scenarioContext?.displayScore ?? comp.overallScore
        let subs = result.scenarioContext?.subscores ?? [:]

        func subscore(_ key: CompatibilitySubscoreKey, fallback: Int) -> Int {
            subs[key.rawValue] ?? fallback
        }

        let dimensions = skin.dimensionLabels.map { dim -> CompatibilityExplorationDimension in
            let deepScore = deep?.dimensions.first(where: { $0.key.lowercased() == dim.key.rawValue })?.score
            let score = subscore(dim.key, fallback: deepScore ?? displayScore)
            let quip = skin.isPlayful ? CompatibilityPlayfulStats.quip(scenarioId: scenarioId, key: dim.key, score: score) : nil
            return CompatibilityExplorationDimension(
                id: dim.key.rawValue,
                emoji: dim.emoji,
                label: dim.label,
                score: score,
                quip: quip?.isEmpty == false ? quip : nil
            )
        }

        let name1: String = {
            let trimmed = result.profile1?.label?.trimmingCharacters(in: .whitespacesAndNewlines)
            if let trimmed, !trimmed.isEmpty { return trimmed }
            return CompatibilityExplorationChrome.isRu ? "Профиль 1" : "Profile 1"
        }()
        let name2: String = {
            let trimmed = result.profile2?.label?.trimmingCharacters(in: .whitespacesAndNewlines)
            if let trimmed, !trimmed.isEmpty { return trimmed }
            return CompatibilityExplorationChrome.isRu ? "Профиль 2" : "Profile 2"
        }()
        let pairLine = "\(name1) × \(name2)"

        if skin.isPlayful {
            let sorted = dimensions.sorted { $0.score > $1.score }
            let top = sorted.first
            let low = sorted.last
            let disclaimer = CompatibilityExplorationChrome.isRu
                ? "Шуточная статистика — не серьёзный разбор отношений."
                : "Playful stats — not a serious relationship reading."
            return CompatibilityExplorationModel(
                scenarioId: scenarioId,
                scenarioPoster: skin.poster,
                scenarioSubtitle: skin.posterSubtitle,
                pairLine: pairLine,
                score: displayScore,
                scoreLabel: CompatibilityPlayfulStats.scoreLabel(scenarioId: scenarioId, score: displayScore),
                mainThought: editorial.flatMap({ $0.pairThesis.nilIfEmpty })
                    ?? comp.summary?.nilIfEmpty
                    ?? skin.posterSubtitle,
                dimensions: dimensions,
                narrative: [editorial?.modeFocus, comp.summary].compactMap { $0?.nilIfEmpty }.prefix(1).map { $0 },
                strongestResource: top.map { "\($0.emoji) \($0.label): \($0.score)% — \($0.quip ?? "")" } ?? "",
                mainRisk: low.map { "\($0.emoji) \($0.label): \($0.score)% — \($0.quip ?? "")" } ?? "",
                tips: [],
                deepSections: [],
                continuations: CompatibilityScenarioRegistry.continuations(for: scenarioId),
                isPlayful: true,
                playfulDisclaimer: disclaimer
            )
        }

        let mainThought = editorial.flatMap({ $0.pairThesis.nilIfEmpty })
            ?? comp.summary?.nilIfEmpty
            ?? deep?.relationshipArchetype?.nilIfEmpty
            ?? (CompatibilityExplorationChrome.isRu
                ? "Вы взаимно влияете друг на друга — главное увидеть живую динамику."
                : "You influence each other — see the live dynamic, not just one percent.")

        var narrative: [String] = []
        var seen = Set<String>()
        for candidate in [editorial?.modeFocus, deep?.relationshipArchetype, comp.summary] + (deep?.strengths.prefix(1).map { Optional($0) } ?? []) {
            guard let text = candidate?.nilIfEmpty else { continue }
            let key = text.lowercased()
            if seen.contains(key) { continue }
            seen.insert(key)
            narrative.append(text)
            if narrative.count >= 3 { break }
        }

        var tips: [String] = []
        seen.removeAll()
        for candidate in (deep?.guidance ?? []) + comp.recommendations + [editorial?.nextStep ?? ""] {
            let text = candidate.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !text.isEmpty else { continue }
            let key = text.lowercased()
            if seen.contains(key) { continue }
            seen.insert(key)
            tips.append(text)
            if tips.count >= 3 { break }
        }
        if tips.isEmpty {
            tips = CompatibilityExplorationChrome.isRu
                ? ["Проясняйте ожидания заранее.", "Договаривайтесь о ролях.", "Возвращайтесь к разговору."]
                : ["Clarify expectations early.", "Agree on roles.", "Return to talk."]
        }

        let deepSections: [CompatibilityExplorationDeepSection]
        let orderedLabels = CompatibilityScenarioRegistry.orderedDimensionLabels(
            skin: skin,
            deepBlockOrder: result.scenarioContext?.deepBlockOrder
        )
        if let dims = deep?.dimensions, !dims.isEmpty {
            deepSections = orderedLabels.compactMap { slot in
                let sources = CompatibilityScenarioRegistry.pairDeepSourceKeys(for: slot.key)
                let matched = sources.compactMap { key in
                    dims.first(where: { $0.key.lowercased() == key })
                }.first
                guard let m = matched, !m.summary.isEmpty else { return nil }
                return CompatibilityExplorationDeepSection(
                    id: slot.key.rawValue,
                    title: slot.label,
                    subtitle: "",
                    takeaway: m.summary,
                    detail: (m.indicators ?? []).joined(separator: " · "),
                    risk: "",
                    action: ""
                )
            }
        } else {
            deepSections = comp.aspects.prefix(4).map {
                CompatibilityExplorationDeepSection(
                    id: $0.type,
                    title: $0.type,
                    subtitle: "",
                    takeaway: $0.description,
                    detail: "",
                    risk: "",
                    action: ""
                )
            }
        }

        return CompatibilityExplorationModel(
            scenarioId: scenarioId,
            scenarioPoster: skin.poster,
            scenarioSubtitle: skin.posterSubtitle,
            pairLine: pairLine,
            score: displayScore,
            scoreLabel: CompatibilityExplorationChrome.scenarioScoreLabel(scenarioId: scenarioId, score: displayScore),
            mainThought: mainThought,
            dimensions: dimensions,
            narrative: narrative.isEmpty
                ? [CompatibilityExplorationChrome.isRu
                    ? "Посмотрите, как динамика проявляется в конкретных ситуациях."
                    : "See how the dynamic shows up in real situations."]
                : narrative,
            strongestResource: deep?.strengths.first
                ?? editorial?.strengths.first
                ?? deep?.strongestAxis?.nilIfEmpty
                ?? (CompatibilityExplorationChrome.isRu ? "Есть опора в сложные моменты." : "There is something to lean on."),
            mainRisk: deep?.challenges.first
                ?? editorial?.tensions.first
                ?? deep?.tensionAxis?.nilIfEmpty
                ?? (CompatibilityExplorationChrome.isRu ? "Главный риск — повторяющееся трение без разговора." : "Main risk — friction without a new talk."),
            tips: tips,
            deepSections: deepSections,
            continuations: CompatibilityScenarioRegistry.continuations(for: scenarioId),
            isPlayful: false,
            playfulDisclaimer: nil
        )
    }
}

private extension String {
    var nilIfEmpty: String? {
        let t = trimmingCharacters(in: .whitespacesAndNewlines)
        return t.isEmpty ? nil : t
    }
}

// MARK: - Exploration UI

private struct CompatibilityExplorationHeroRing: View {
    let score: Int

    var body: some View {
        let pct = min(100, max(0, score))
        ZStack {
            Circle()
                .stroke(Color.black.opacity(0.06), lineWidth: 11)
            Circle()
                .trim(from: 0, to: CGFloat(pct) / 100)
                .stroke(
                    LinearGradient(colors: [TodayFlowTheme.gold, TodayFlowTheme.sunset], startPoint: .topLeading, endPoint: .bottomTrailing),
                    style: StrokeStyle(lineWidth: 11, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
            Circle()
                .fill(Color(red: 1, green: 0.99, blue: 0.97))
                .padding(14)
            VStack(spacing: 2) {
                Text("\(pct)%")
                    .font(.system(size: 26, weight: .bold, design: .rounded))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(CompatibilityExplorationChrome.ringLabel.uppercased())
                    .font(.system(size: 8, weight: .bold))
                    .foregroundStyle(TodayFlowTheme.sand)
            }
        }
        .frame(width: 132, height: 132)
    }
}

private struct CompatibilityExplorationDimensionCard: View {
    let dimension: CompatibilityExplorationDimension
    let delay: Double
    @State private var visible = false

    var body: some View {
        let pct = min(100, max(0, dimension.score))
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Text(dimension.emoji).font(.title3)
                Text(dimension.label)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .lineLimit(2)
            }
            Text("\(dimension.score)%")
                .font(.title3.weight(.bold))
                .foregroundStyle(TodayFlowTheme.sunset)
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule().fill(Color.black.opacity(0.06))
                    Capsule()
                        .fill(TodayFlowTheme.sunset.opacity(0.85))
                        .frame(width: visible ? geo.size.width * CGFloat(pct) / 100 : 0)
                }
            }
            .frame(height: 6)
            if let quip = dimension.quip, !quip.isEmpty {
                Text(quip)
                    .font(.caption2)
                    .foregroundStyle(Color(red: 0.47, green: 0.21, blue: 0.06))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .opacity(visible ? 1 : 0)
        .offset(y: visible ? 0 : 8)
        .onAppear {
            withAnimation(.easeOut(duration: 0.45).delay(delay)) {
                visible = true
            }
        }
    }
}

struct CompatibilityExplorationResultView: View {
    let model: CompatibilityExplorationModel
    let store: TodayFlowStore
    var dynamicsResponse: SignCompatibilityAPIResponse? = nil
    var pairResponse: CompatibilityComparisonResponse? = nil
    var learning: SignCompatibilityLearningContext? = nil
    var onPairScenarioSwitch: ((String) -> Void)? = nil
    var onPairRefresh: (() -> Void)? = nil
    var pairRefreshing: Bool = false

    @State private var deepOpen = false
    @State private var expandedBlockKeys: Set<String> = []

    private var loc: String? { dynamicsResponse?.contentLocale }
    private var funnelArtifact: CompatibilityFunnelArtifact? {
        dynamicsResponse?.funnelArtifact ?? pairResponse?.funnelArtifact
    }

    private var attachmentReference: CompatibilityAttachmentReference? {
        dynamicsResponse?.attachmentReference ?? pairResponse?.scenarioContext?.attachmentReference
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            posterSection
            heroSection
            dimensionsGrid
            if model.isPlayful {
                if !model.narrative.isEmpty { playfulPunchlineSection }
                playfulInsightsSection
            } else {
                if !model.narrative.isEmpty { narrativeSection }
                insightsSection
                if !model.tips.isEmpty { tipsSection }
                personalizedSection
                if let funnel = funnelArtifact, !model.isPlayful {
                    compatibilityFunnelArtifactSection(funnel, locale: loc)
                }
                deepSection
            }
            if !model.continuations.isEmpty { continuationSection }
            if onPairRefresh != nil {
                Button {
                    onPairRefresh?()
                } label: {
                    Text(pairRefreshing
                         ? (CompatibilityExplorationChrome.isRu ? "Обновляю…" : "Refreshing…")
                         : (CompatibilityExplorationChrome.isRu ? "Обновить разбор" : "Refresh reading"))
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                }
                .buttonStyle(.bordered)
                .disabled(pairRefreshing)
            }
        }
        .padding(.top, 4)
        .onAppear {
            RelationshipMapStore.recordVisit(
                label: model.pairLine,
                scenarioId: model.scenarioId,
                pairLine: model.pairLine,
                theme: model.scenarioPoster
            )
        }
    }

    private var playfulPunchlineSection: some View {
        VStack(alignment: .leading, spacing: 6) {
            ForEach(Array(model.narrative.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Color(red: 0.47, green: 0.21, blue: 0.06))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(red: 1, green: 0.98, blue: 0.92).opacity(0.9))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.4), style: StrokeStyle(lineWidth: 1, dash: [4, 3]))
        )
    }

    private var playfulInsightsSection: some View {
        VStack(spacing: 10) {
            insightCard(title: "🏆 Лидер stat", body: model.strongestResource, tint: Color.green.opacity(0.12))
            insightCard(title: "📉 Слабое звено", body: model.mainRisk, tint: TodayFlowTheme.roseClay.opacity(0.12))
        }
    }

    private var posterSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(model.isPlayful ? "🎲 Эксперимент" : CompatibilityExplorationChrome.investigation)
                .font(.caption.weight(.semibold))
                .textCase(.uppercase)
                .tracking(0.6)
                .foregroundStyle(TodayFlowTheme.sand)
            Text(model.scenarioPoster)
                .font(.title2.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(model.scenarioSubtitle)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                .fixedSize(horizontal: false, vertical: true)
            if let disclaimer = model.playfulDisclaimer {
                Text(disclaimer)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.58, green: 0.25, blue: 0.05))
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.55))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var heroSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(model.pairLine.uppercased())
                .font(.caption.weight(.bold))
                .tracking(0.5)
                .foregroundStyle(TodayFlowTheme.sand)
            HStack(alignment: .top, spacing: 14) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(model.isPlayful ? "Вердикт" : CompatibilityExplorationChrome.mainThought)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                    Text(model.mainThought)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(model.scoreLabel)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset.opacity(0.9))
                }
                Spacer(minLength: 4)
                CompatibilityExplorationHeroRing(score: model.score)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color(red: 1, green: 0.99, blue: 0.97), Color.white.opacity(0.92)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
        )
    }

    private var dimensionsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
            ForEach(Array(model.dimensions.enumerated()), id: \.element.id) { idx, dim in
                CompatibilityExplorationDimensionCard(dimension: dim, delay: Double(idx) * 0.09 + 0.12)
            }
        }
    }

    private var narrativeSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(CompatibilityExplorationChrome.tomorrow)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(Array(model.narrative.enumerated()), id: \.offset) { _, line in
                Text(line)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var insightsSection: some View {
        VStack(spacing: 10) {
            insightCard(title: CompatibilityExplorationChrome.strongestResource, body: model.strongestResource, tint: Color.green.opacity(0.12))
            insightCard(title: CompatibilityExplorationChrome.mainRisk, body: model.mainRisk, tint: TodayFlowTheme.roseClay.opacity(0.12))
        }
    }

    private func insightCard(title: String, body: String, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title).font(.subheadline.weight(.semibold)).foregroundStyle(TodayFlowTheme.ink)
            Text(body)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(tint)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var tipsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(CompatibilityExplorationChrome.tipsTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(model.tips, id: \.self) { tip in
                HStack(alignment: .top, spacing: 8) {
                    Text("•").foregroundStyle(TodayFlowTheme.sunset)
                    Text(tip)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    @ViewBuilder
    private var personalizedSection: some View {
        if let dynamicsResponse,
           case let .object(dict) = dynamicsResponse.personalized,
           let headline = dict["headline"]?.stringValue,
           !headline.isEmpty {
            VStack(alignment: .leading, spacing: 6) {
                Text(CompatibilityScreenChrome.profileLensEyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Text(headline)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.5))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }

    @ViewBuilder
    private var deepSection: some View {
        if !deepOpen {
            VStack(alignment: .leading, spacing: 8) {
                Button {
                    deepOpen = true
                    if let learning {
                        Task { await learning.trackDeepOpen() }
                    }
                } label: {
                    Text(CompatibilityExplorationChrome.deepCta)
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 13)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
                Text(CompatibilityExplorationChrome.deepCtaHint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
            }
        } else {
            VStack(alignment: .leading, spacing: 12) {
                Text(CompatibilityExplorationChrome.deepTitle)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                ForEach(model.deepSections) { section in
                    DisclosureGroup(isExpanded: blockExpandedBinding(for: section.id)) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(section.takeaway).font(.subheadline.weight(.semibold))
                            if !section.detail.isEmpty {
                                Text(section.detail).font(.footnote).foregroundStyle(TodayFlowTheme.ink.opacity(0.75))
                            }
                            if !section.risk.isEmpty {
                                Text("⚠ \(section.risk)").font(.footnote).foregroundStyle(TodayFlowTheme.roseClay)
                            }
                            if !section.action.isEmpty {
                                Text("→ \(section.action)").font(.footnote).foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                            }
                        }
                        .padding(.top, 6)
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(section.title).font(.subheadline.weight(.semibold))
                            if !section.subtitle.isEmpty {
                                Text(section.subtitle).font(.caption).foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                            }
                        }
                    }
                    .padding(10)
                    .background(Color.white.opacity(0.45))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                }
            }
        }
    }

    private var continuationSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(CompatibilityExplorationChrome.continuationTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(CompatibilityExplorationChrome.continuationLead)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(model.continuations, id: \.id) { cont in
                        if let onPairScenarioSwitch {
                            Button {
                                onPairScenarioSwitch(cont.id)
                                Task {
                                    await store.trackCompatibilityEvent(
                                        eventType: "compatibility_scenario_switch",
                                        payload: [
                                            "surface": .string("pair_profiles"),
                                            "from_scenario_id": .string(model.scenarioId),
                                            "to_scenario_id": .string(cont.id),
                                            "format_id": .string(cont.id),
                                        ]
                                    )
                                }
                            } label: {
                                continuationCard(cont)
                            }
                            .buttonStyle(.plain)
                        } else {
                            NavigationLink {
                                CompatibilityEncyclopediaAnalyzeView(
                                    selection: CompatibilityEncyclopediaAnalyzeSelection(
                                        label: cont.poster,
                                        selectionKind: "series",
                                        selectionId: cont.id,
                                        topicId: nil,
                                        readingId: nil,
                                        seriesId: cont.id,
                                        introBlocks: [],
                                        scenarioBullets: []
                                    ),
                                    store: store
                                )
                            } label: {
                                continuationCard(cont)
                            }
                            .buttonStyle(.plain)
                            .simultaneousGesture(TapGesture().onEnded {
                                if let learning {
                                    Task { await learning.trackScenarioSwitch(toScenarioId: cont.id) }
                                }
                            })
                        }
                    }
                }
            }
        }
    }

    private func continuationCard(_ cont: CompatibilityScenarioSkin) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(cont.emoji).font(.title2)
            Text(cont.poster)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .multilineTextAlignment(.leading)
        }
        .padding(14)
        .frame(width: 148, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.25), lineWidth: 1)
        )
    }

    private func blockExpandedBinding(for key: String) -> Binding<Bool> {
        Binding(
            get: { expandedBlockKeys.contains(key) },
            set: { expanded in
                if expanded {
                    expandedBlockKeys.insert(key)
                    if let learning {
                        Task { await learning.trackDeepOpen() }
                    }
                } else {
                    expandedBlockKeys.remove(key)
                }
            }
        )
    }
}
