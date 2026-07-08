import SwiftUI

// MARK: - Copy (parity with web profileQuickMapCopy.ts)

enum ProfileQuickMapCopy {
    static let pageKicker = "Профиль"
    static let birthData = "Данные рождения"
    static let whoTitle = "Кто ты"
    static let strengthensTitle = "Что тебя усиливает"
    static let drainsTitle = "Что быстрее всего забирает силы"
    static let decisionsTitle = "Как ты принимаешь решения"
    static let perceivedTitle = "Как тебя обычно воспринимают"
    static let thriveTitle = "Где проще всего реализоваться"
    static let missionTitle = "Главная задача жизни"
    static let frameworkTitle = "Почему система так решила"
    static let frameworkAnchorsLead = "Основу твоей карты формируют"
    static let portalKicker = "Следующий уровень"
    static let portalTitle = "Карта личности"
    static let portalSub = "Планеты, дома, аспекты — полный разбор натальной карты."
    static let portalEnter = "Войти"
    static let portalCollapse = "Свернуть"
    static let deepTitle = "Карта личности"
    static let deepSubtitle = "Планеты, дома, аспекты — полный разбор натальной карты."
    static let todayLink = "Перейти в Today"
}

// MARK: - View model

struct ProfileFrameworkCardModel: Identifiable {
    let id: String
    let title: String
    let anchor: String?
    let body: String
}

struct ProfileFrameworkAnchorModel: Identifiable {
    let id: String
    let label: String
}

struct ProfileQuickMapViewModel {
    let archetype: String
    let identitySummary: String?
    let strengthens: [String]
    let drains: [String]
    let decisionStyle: String?
    let perceivedAs: [String]
    let thriveAreas: [String]
    let lifeMission: String?
    let frameworkLead: String?
    let frameworkAnchors: [ProfileFrameworkAnchorModel]
    let frameworkCards: [ProfileFrameworkCardModel]
}

enum ProfileQuickMapBuilder {
    static func build(
        coreProfile: CoreProfileResponse?,
        natalChart: NatalChartPreview?,
        cum: CompactUserModelResponse? = nil
    ) -> ProfileQuickMapViewModel {
        let interpretation = coreProfile?.interpretation
        let baseline = coreProfile?.baseline
        let lifeAreas = interpretation?.lifeAreas

        let archetype = baseline?.archetypeSeed?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty ?? "Личный архетип"
        let identity = interpretation?.identity?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
            ?? coreProfile?.natalSummary?.overview?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty

        let strengthens = uniqueNonEmpty([
            interpretation?.strengths?.first,
            lifeAreas?.career.map { "Карьера: \($0)" },
            baseline?.rhythmStyle,
        ], limit: 4)

        let drains = uniqueNonEmpty([
            interpretation?.watchouts?.first,
            interpretation?.watchouts?.dropFirst().first,
            lifeAreas?.money.map { "Деньги: \($0)" },
        ], limit: 4)

        let perceived = uniqueNonEmpty(
            (interpretation?.strengths ?? []).map { Optional($0) },
            limit: 5
        ).filter { item in
            guard let identity else { return true }
            return !profileTextsOverlap(item, identity)
        }

        let thrive = uniqueNonEmpty([
            lifeAreas?.career != nil ? Optional("Карьера") : nil,
            lifeAreas?.money != nil ? Optional("Реализация") : nil,
            lifeAreas?.love != nil ? Optional("Близость") : nil,
            coreProfile?.numerology.lifePath != nil ? Optional("Стратегия") : nil,
        ], limit: 5)

        let frameworkLeadCandidate = baseline?.rhythmStyle?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
        let frameworkLead = frameworkLeadCandidate.flatMap { candidate -> String? in
            guard let identity else { return candidate }
            return profileTextsOverlap(candidate, identity) ? nil : candidate
        }

        let sunSign = natalChart.flatMap { ZodiacSignRU.planetLine($0, body: "sun") }
            ?? ZodiacSignRU.title(coreProfile?.astro.sunSign)
        let risingSign = natalChart.flatMap { ZodiacSignRU.ascendantLine($0) }
        let mcSign = mcSignLabel(from: natalChart)
        let moonSign = natalChart.flatMap { ZodiacSignRU.planetLine($0, body: "moon") }
        let lifePath = coreProfile?.numerology.lifePath

        var anchors: [ProfileFrameworkAnchorModel] = []
        if sunSign != "—" {
            anchors.append(.init(id: "sun", label: "Солнце в \(sunSign)"))
        }
        if let risingSign, risingSign != "—" {
            anchors.append(.init(id: "rising", label: "Асцендент в \(risingSign)"))
        }
        if let mcSign {
            anchors.append(.init(id: "mc", label: "MC в \(mcSign)"))
        }
        if let lifePath {
            anchors.append(.init(id: "lp", label: "Число пути \(lifePath)"))
        }
        anchors.append(.init(id: "archetype", label: "Архетип \(archetype)"))

        let cards = frameworkCards(
            sunSign: sunSign,
            risingSign: risingSign,
            moonSign: moonSign,
            mcSign: mcSign,
            lifePath: lifePath,
            archetype: archetype,
            identity: identity,
            coreProfile: coreProfile
        )

        return mergeCumIntoQuickMap(
            ProfileQuickMapViewModel(
                archetype: archetype,
                identitySummary: identity,
                strengthens: strengthens,
                drains: drains,
                decisionStyle: lifeAreas?.decisions,
                perceivedAs: perceived,
                thriveAreas: thrive,
                lifeMission: interpretation?.lifeAreas?.career ?? baseline?.rhythmStyle,
                frameworkLead: frameworkLead,
                frameworkAnchors: anchors,
                frameworkCards: cards
            ),
            cum: cum
        )
    }

    private static func mergeCumIntoQuickMap(
        _ base: ProfileQuickMapViewModel,
        cum: CompactUserModelResponse?
    ) -> ProfileQuickMapViewModel {
        guard let cum else { return base }

        let atomSummaries = (cum.knowledgeAtomsTopK)
            .compactMap { atom -> String? in
                let summary = atom.claimSummary?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
                let claim = atom.claim?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
                return summary ?? claim
            }

        let patternWorks = cum.behavioralPatterns.works ?? []
        let patternAvoid = cum.behavioralPatterns.doesNotWork ?? []
        let identityStrengths = cum.identity.strengths ?? []
        let identityConstraints = cum.identity.constraints ?? []

        let strengthens = mergeBullets(
            max: 4,
            sources: patternWorks + identityStrengths + base.strengthens + Array(atomSummaries.prefix(2))
        )
        let drains = mergeBullets(max: 4, sources: patternAvoid + identityConstraints + base.drains)

        let perceivedAs = base.perceivedAs.isEmpty ? Array(atomSummaries.prefix(5)) : base.perceivedAs
        let thriveAreas = base.thriveAreas.isEmpty
            ? profileCopyToTags(cum.activeThemes.map(\.themeID), max: 5)
            : base.thriveAreas

        let archetype = resolvedArchetype(base: base.archetype, cum: cum)
        let identitySummary = base.identitySummary ?? cum.identity.summary?.nilIfEmpty

        return ProfileQuickMapViewModel(
            archetype: archetype,
            identitySummary: identitySummary,
            strengthens: strengthens,
            drains: drains,
            decisionStyle: base.decisionStyle,
            perceivedAs: perceivedAs,
            thriveAreas: thriveAreas,
            lifeMission: base.lifeMission,
            frameworkLead: base.frameworkLead,
            frameworkAnchors: enrichFrameworkAnchors(base.frameworkAnchors, cum: cum),
            frameworkCards: base.frameworkCards
        )
    }

    private static func enrichFrameworkAnchors(
        _ anchors: [ProfileFrameworkAnchorModel],
        cum: CompactUserModelResponse
    ) -> [ProfileFrameworkAnchorModel] {
        let labels = anchors.map { $0.label.lowercased() }
        let hasMoon = labels.contains { $0.contains("луна") }
        let hasRising = labels.contains { $0.contains("асцендент") }
        var additions: [ProfileFrameworkAnchorModel] = []

        if let moon = cum.identity.moonSign?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty, !hasMoon {
            additions.append(.init(id: "moon", label: "Луна в \(moon)"))
        }
        if let rising = cum.identity.risingSign?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty, !hasRising {
            additions.append(.init(id: "rising", label: "Асцендент в \(rising)"))
        }
        guard !additions.isEmpty else { return anchors }

        if let sunIndex = anchors.firstIndex(where: { $0.id == "sun" }) {
            var out = anchors
            out.insert(contentsOf: additions, at: sunIndex + 1)
            return out
        }
        return additions + anchors
    }

    private static func resolvedArchetype(base: String, cum: CompactUserModelResponse) -> String {
        let trimmed = base.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty, trimmed != "Личный архетип" {
            return trimmed
        }
        return cum.identity.archetype?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty ?? trimmed
    }

    private static func profileTextsOverlap(_ a: String, _ b: String) -> Bool {
        let left = a.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let right = b.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !left.isEmpty, !right.isEmpty else { return false }

        let probe = min(40, left.count, right.count)
        guard probe >= 16 else { return false }

        let slice = String(left.prefix(probe))
        if right.contains(slice) || left.contains(String(right.prefix(probe))) {
            return true
        }

        let wordsA = Set(left.split(whereSeparator: \.isWhitespace).map(String.init).filter { $0.count > 4 })
        let wordsB = right.split(whereSeparator: \.isWhitespace).map(String.init).filter { $0.count > 4 }
        guard !wordsA.isEmpty, !wordsB.isEmpty else { return false }

        let shared = wordsB.filter { wordsA.contains($0) }.count
        return shared >= 3
    }

    private static func mergeBullets(max: Int, sources: [String]) -> [String] {
        var seen = Set<String>()
        var out: [String] = []
        for source in sources {
            for bullet in profileCopyToBullets(source, max: max) {
                let key = bullet.lowercased()
                guard !seen.contains(key) else { continue }
                seen.insert(key)
                out.append(bullet)
                if out.count >= max { return out }
            }
        }
        return out
    }

    private static func profileCopyToBullets(_ text: String?, max: Int) -> [String] {
        guard let raw = text?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else { return [] }
        if raw.contains("•") {
            return Array(raw.split(separator: "•").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }.prefix(max))
        }
        if raw.contains("\n") {
            return Array(raw.split(separator: "\n").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }.prefix(max))
        }
        if raw.contains(";") {
            return Array(raw.split(separator: ";").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }.prefix(max))
        }
        return [raw]
    }

    private static func profileCopyToTags(_ texts: [String], max: Int) -> [String] {
        var tags: [String] = []
        for text in texts {
            for bullet in profileCopyToBullets(text, max: 2) {
                let candidate = bullet.split(whereSeparator: { ",—–-".contains($0) }).first.map(String.init)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? bullet
                guard !candidate.isEmpty, candidate.count <= 48 else { continue }
                guard !tags.contains(candidate) else { continue }
                tags.append(candidate)
                if tags.count >= max { return tags }
            }
        }
        return tags
    }

    private static func frameworkCards(
        sunSign: String?,
        risingSign: String?,
        moonSign: String?,
        mcSign: String?,
        lifePath: Int?,
        archetype: String,
        identity: String?,
        coreProfile: CoreProfileResponse?
    ) -> [ProfileFrameworkCardModel] {
        var cards: [ProfileFrameworkCardModel] = [
            .init(
                id: "sun",
                title: "Солнце",
                anchor: sunSign.flatMap { $0 == "—" ? nil : "в \($0)" },
                body: coreProfile?.natalSummary?.chartTone ?? "Солнце показывает, как ты проявляешь себя в мире."
            ),
            .init(
                id: "rising",
                title: "Асцендент",
                anchor: risingSign.flatMap { $0 == "—" ? nil : "в \($0)" },
                body: "Асцендент описывает первый контакт с миром и стиль входа в новые процессы."
            ),
            .init(
                id: "moon",
                title: "Луна",
                anchor: moonSign.flatMap { $0 == "—" ? nil : "в \($0)" },
                body: "Луна описывает, как ты чувствуешь и восстанавливаешься."
            ),
            .init(
                id: "mc",
                title: "MC",
                anchor: mcSign.flatMap { "в \($0)" },
                body: mcSign != nil
                    ? "MC показывает, как ты реализуешь себя в карьере и публичной роли."
                    : "MC уточняется по времени рождения — линия достижений и видимого пути."
            ),
            .init(
                id: "archetype",
                title: "Архетип",
                anchor: archetype,
                body: identity ?? "Архетип собирает повторяющийся сценарий личности."
            ),
        ]

        if let lifePath {
            cards.append(
                .init(
                    id: "life_path",
                    title: "Число пути",
                    anchor: String(lifePath),
                    body: coreProfile?.baseline.rhythmStyle ?? "Число пути задаёт долгий ритм развития и главную тему."
                )
            )
        }

        return cards
    }

    private static func mcSignLabel(from chart: NatalChartPreview?) -> String? {
        guard let chart else { return nil }
        if let house10 = chart.houses.first(where: { $0.house == 10 }), let sign = house10.sign, !sign.isEmpty {
            return ZodiacSignRU.title(sign)
        }
        return nil
    }

    private static func uniqueNonEmpty(_ items: [String?], limit: Int) -> [String] {
        var seen = Set<String>()
        var out: [String] = []
        for raw in items {
            guard let text = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty else { continue }
            let key = text.lowercased()
            guard !seen.contains(key) else { continue }
            seen.insert(key)
            out.append(text)
            if out.count >= limit { break }
        }
        return out
    }
}

private extension String {
    var nilIfEmpty: String? {
        isEmpty ? nil : self
    }
}

// MARK: - View

struct ProfileQuickMapView: View {
    let model: ProfileQuickMapViewModel
    let store: TodayFlowStore
    @Binding var chartDeepExpanded: Bool
    let natalChart: NatalChartPreview?
    let coreProfile: CoreProfileResponse?
    let isLoadingNatal: Bool
    let natalError: String?
    let onOpenBirthData: () -> Void
    let onReloadNatal: () async -> Void
    var onOpenToday: (() -> Void)?
    var onOpenRhythm: (() -> Void)?

    var body: some View {
        VStack(alignment: .leading, spacing: 28) {
            portraitSection
            ProfileRelationshipInsightsSection(store: store)
            ProfileCumInsightsSection(store: store)
            livingMapsSection
            deepSection
            if let onOpenToday {
                Button(action: onOpenToday) {
                    Text(ProfileQuickMapCopy.todayLink)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private var portraitSection: some View {
        VStack(alignment: .leading, spacing: 20) {
            ProfilePortraitSectionBand()
            headerSection

            if !model.strengthens.isEmpty || !model.drains.isEmpty {
                resumeGrid
            }

            if let decision = model.decisionStyle {
                tintedPanel(title: ProfileQuickMapCopy.decisionsTitle, body: decision, tint: TodayFlowTheme.twilight)
            }

            if !model.perceivedAs.isEmpty { tagSection(title: ProfileQuickMapCopy.perceivedTitle, items: model.perceivedAs) }
            if !model.thriveAreas.isEmpty { tagSection(title: ProfileQuickMapCopy.thriveTitle, items: model.thriveAreas) }
            if let mission = model.lifeMission { missionSection(mission) }
            frameworkSection
        }
    }

    private var headerSection: some View {
        HeroLargeView(
            symbolSeed: model.archetype,
            title: model.archetype,
            kicker: ProfileQuickMapCopy.pageKicker,
            sectionLabel: ProfileQuickMapCopy.whoTitle,
            digest: model.identitySummary,
            pillars: Array(model.frameworkAnchors.prefix(4).enumerated()).map { index, anchor in
                HeroLargePillar(id: anchor.id, label: anchor.label, accent: index == 0)
            },
            topActionTitle: ProfileQuickMapCopy.birthData,
            topAction: onOpenBirthData
        )
    }

    private var resumeGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            if !model.strengthens.isEmpty {
                resumePanel(
                    title: ProfileQuickMapCopy.strengthensTitle,
                    items: model.strengthens,
                    positive: true
                )
            }
            if !model.drains.isEmpty {
                resumePanel(
                    title: ProfileQuickMapCopy.drainsTitle,
                    items: model.drains,
                    positive: false
                )
            }
        }
    }

    private func resumePanel(title: String, items: [String], positive: Bool) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            ForEach(items, id: \.self) { item in
                HStack(alignment: .top, spacing: 8) {
                    Text("•")
                    Text(item)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: positive
                    ? [TodayFlowTheme.moss.opacity(0.12), Color.white.opacity(0.82)]
                    : [TodayFlowTheme.roseClay.opacity(0.1), Color.white.opacity(0.82)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func tintedPanel(title: String, body: String, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(body)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(tint.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func missionSection(_ mission: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(ProfileQuickMapCopy.missionTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(mission)
                .font(.system(.title3, design: .serif).weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.vertical, 12)
                .padding(.horizontal, 14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.72))
                .overlay(alignment: .leading) {
                    Rectangle()
                        .fill(TodayFlowTheme.gold)
                        .frame(width: 3)
                }
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }

    private func bulletSection(title: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel(title)
            ForEach(items, id: \.self) { item in
                HStack(alignment: .top, spacing: 8) {
                    Text("•")
                    Text(item)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }

    private func textSection(title: String, body: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel(title)
            Text(body)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private func tagSection(title: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionLabel(title)
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 88), spacing: 8)], alignment: .leading, spacing: 8) {
                ForEach(items, id: \.self) { item in
                    Text(item)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.white.opacity(0.72))
                        .clipShape(Capsule())
                }
            }
        }
    }

    private var frameworkSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionLabel(ProfileQuickMapCopy.frameworkTitle)
            if let lead = model.frameworkLead {
                Text(lead)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
            }
            Text(ProfileQuickMapCopy.frameworkAnchorsLead)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 120), spacing: 8)], alignment: .leading, spacing: 8) {
                ForEach(model.frameworkAnchors) { anchor in
                    Text(anchor.label)
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(TodayFlowTheme.sunset.opacity(0.1))
                        .clipShape(Capsule())
                }
            }
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                ForEach(model.frameworkCards) { card in
                    VStack(alignment: .leading, spacing: 6) {
                        Text(card.title.uppercased())
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                        if let anchor = card.anchor {
                            Text(anchor)
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                        }
                        Text(card.body)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.76))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.78))
                    .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                }
            }
        }
    }

    private var livingMapsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            ProfileMapsPreviewView(store: store, onOpenRhythm: onOpenRhythm, showSectionBand: true)
            if let observation = coreProfile?.living?.summary?.trimmingCharacters(in: .whitespacesAndNewlines),
               !observation.isEmpty {
                Text(observation)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(TodayFlowTheme.twilight.opacity(0.06))
                    .overlay(alignment: .leading) {
                        Rectangle()
                            .fill(TodayFlowTheme.twilight)
                            .frame(width: 3)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            }
        }
    }

    private var deepSection: some View {
        ProfilePortalDeepSection(isExpanded: $chartDeepExpanded) {
            ProfileChartSection(
                natalChart: natalChart,
                coreProfile: coreProfile,
                isLoading: isLoadingNatal,
                error: natalError,
                fullChartOpen: chartDeepExpanded,
                onReload: onReloadNatal
            )
        }
        .id("profileNatalChartAnchor")
    }

    private func sectionLabel(_ text: String) -> some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .foregroundStyle(TodayFlowTheme.secondaryInk)
    }
}
