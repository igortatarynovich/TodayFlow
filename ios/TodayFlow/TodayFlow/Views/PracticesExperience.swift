import AVKit
import SwiftUI

enum PracticesRoute: Hashable {
    case history
    case practice(String)
}

// MARK: - Корень таба (хаб + история + деталь в одном стеке)

struct PracticesRootView: View {
    @Binding var path: NavigationPath
    @Binding var openHistoryFromDeepLink: Bool
    @Binding var openPracticeIdFromDeepLink: String?
    /// `AuthSession.userID` — для `interpretation-bundle?day=` как на вебе (`useUserDay`).
    var userId: Int?
    /// Как `profile.is_paid` на вебе: bundle не запрашиваем без платного доступа.
    var isPaidSubscriber: Bool = false
    var isAuthenticated: Bool = true

    var body: some View {
        NavigationStack(path: $path) {
            PracticesHubView(
                navigationPath: $path,
                userId: userId,
                isPaidSubscriber: isPaidSubscriber
            )
                .navigationDestination(for: PracticesRoute.self) { route in
                    switch route {
                    case .history:
                        PracticesHistoryView(navigationPath: $path)
                    case .practice(let id):
                        PracticeDetailScreen(practiceId: id)
                    }
                }
        }
        .onChange(of: openHistoryFromDeepLink) { _, open in
            guard open else { return }
            path.append(PracticesRoute.history)
            openHistoryFromDeepLink = false
        }
        .onChange(of: openPracticeIdFromDeepLink) { _, id in
            guard let id, !id.isEmpty else { return }
            path = NavigationPath()
            path.append(PracticesRoute.practice(id))
            openPracticeIdFromDeepLink = nil
        }
    }
}

// MARK: - Hub (аналог веб `/practices`)

struct PracticesHubView: View {
    @Binding var navigationPath: NavigationPath
    var userId: Int?
    var isPaidSubscriber: Bool = false
    private enum PeriodicityFilter: String, CaseIterable, Identifiable {
        case all
        case daily
        case weekly
        case monthly
        case cycle

        var id: String { rawValue }

        var title: String {
            switch self {
            case .all: return PracticesExperienceChrome.filterAll
            case .daily: return PracticesExperienceChrome.filterDaily
            case .weekly: return PracticesExperienceChrome.filterWeekly
            case .monthly: return PracticesExperienceChrome.filterMonthly
            case .cycle: return PracticesExperienceChrome.filterCycle
            }
        }
    }

    private enum DurationFilter: String, CaseIterable, Identifiable {
        case any
        case short
        case medium
        case long

        var id: String { rawValue }

        var title: String {
            switch self {
            case .any: return PracticesExperienceChrome.durationAny
            case .short: return PracticesExperienceChrome.durationShort
            case .medium: return PracticesExperienceChrome.durationMedium
            case .long: return PracticesExperienceChrome.durationLong
            }
        }
    }

    @State private var practices: [PracticeSummaryDTO] = []
    @State private var currentPractice: PracticeSummaryDTO?
    @State private var sequences: [PracticeSummaryDTO] = []
    @State private var limits: PracticeLimitsDTO?
    @State private var loading = true
    @State private var errorMessage: String?
    @State private var periodicity: PeriodicityFilter = .all
    @State private var duration: DurationFilter = .any
    @State private var categories: [PracticeCategoryDTO] = []
    /// `nil` — все категории.
    @State private var selectedCategoryId: String?
    @State private var interpretationBundle: InterpretationBundleDTO?
    @State private var shortAlternatives: [PracticeSummaryDTO] = []
    @State private var asceticisms: [PracticeAsceticismDTO] = []
    @State private var practiceAffirmations: [PracticeAffirmationListItemDTO] = []

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    introBlock

                    if interpretationBundleHasContent, let b = interpretationBundle {
                        interpretationBundleCard(b)
                    }

                    if let limits {
                        limitsCard(limits)
                    }

                    filtersBlock

                    if loading && practices.isEmpty {
                        ProgressView(PracticesExperienceChrome.loadingPractices)
                            .tint(TodayFlowTheme.accent)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 24)
                    } else if let errorMessage {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.roseClay)
                            .padding(16)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .todayFlowCard()
                    }

                    if let currentPractice, !loading || !practices.isEmpty {
                        currentSection(currentPractice)
                    }

                    if !shortAlternatives.isEmpty {
                        shortAlternativesSection
                    }

                    if !sequencesFiltered.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text(PracticesExperienceChrome.sequencesTitle)
                                .font(.title3.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(PracticesExperienceChrome.sequencesSubtitle)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)

                            LazyVStack(spacing: 12) {
                                ForEach(sequencesFiltered) { item in
                                    Button {
                                        navigationPath.append(PracticesRoute.practice(item.id))
                                    } label: {
                                        PracticeListRow(practice: item, sequenceBadge: true)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }

                    if !catalogForGrid.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text(PracticesExperienceChrome.catalogSection)
                                .font(.title3.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)

                            LazyVStack(spacing: 12) {
                                ForEach(catalogForGrid) { item in
                                    Button {
                                        navigationPath.append(PracticesRoute.practice(item.id))
                                    } label: {
                                        PracticeListRow(practice: item)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }

                    if !asceticisms.isEmpty {
                        asceticismsSection
                    }

                    if !practiceAffirmations.isEmpty {
                        affirmationsFromPracticesAPISection
                    }

                    if !loading, catalogForGrid.isEmpty, sequencesFiltered.isEmpty, shortAlternatives.isEmpty, errorMessage == nil {
                        Text(PracticesExperienceChrome.emptyFiltered)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                            .todayFlowCard()
                    }
                }
                .padding(.horizontal, 18)
                .padding(.top, 12)
                .padding(.bottom, 28)
            }
        }
        .navigationTitle(PracticesExperienceChrome.navPractices)
        .todayflowNavigationBarTitleDisplayModeLarge()
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    navigationPath.append(PracticesRoute.history)
                } label: {
                    Image(systemName: "clock.arrow.circlepath")
                }
                .accessibilityLabel(PracticesExperienceChrome.a11yHistory)
            }
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await load(force: true) }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .accessibilityLabel(PracticesExperienceChrome.a11yRefresh)
            }
        }
        .task {
            await load(force: false)
        }
        .refreshable {
            await load(force: true)
        }
    }

    private var introBlock: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(PracticesExperienceChrome.nativeHubTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            Text(PracticesExperienceChrome.nativeHubBody)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .todayFlowCard()
    }

    private var filtersBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.filtersTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)

            Picker(PracticesExperienceChrome.pickerPeriodicity, selection: $periodicity) {
                ForEach(PeriodicityFilter.allCases) { p in
                    Text(p.title).tag(p)
                }
            }
            .pickerStyle(.segmented)

            Picker(PracticesExperienceChrome.pickerDuration, selection: $duration) {
                ForEach(DurationFilter.allCases) { d in
                    Text(d.title).tag(d)
                }
            }
            .pickerStyle(.segmented)

            if !categories.isEmpty {
                Text(PracticesExperienceChrome.categoryLabel)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .textCase(.uppercase)
                    .padding(.top, 4)

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        categoryChip(title: PracticesExperienceChrome.filterAll, selected: selectedCategoryId == nil) {
                            selectedCategoryId = nil
                        }
                        ForEach(categories) { cat in
                            categoryChip(title: "\(cat.icon) \(cat.name)", selected: selectedCategoryId == cat.id) {
                                selectedCategoryId = cat.id
                            }
                        }
                    }
                    .padding(.vertical, 2)
                }
            }
        }
        .padding(16)
        .todayFlowCard()
    }

    private func categoryChip(title: String, selected: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(
                    selected ? TodayFlowTheme.accent.opacity(0.22) : Color.black.opacity(0.06),
                    in: Capsule()
                )
                .foregroundStyle(selected ? TodayFlowTheme.accent : TodayFlowTheme.ink)
                .overlay(
                    Capsule()
                        .stroke(selected ? TodayFlowTheme.accent.opacity(0.45) : Color.clear, lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }

    private func currentSection(_ practice: PracticeSummaryDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.forYouNow)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            Button {
                navigationPath.append(PracticesRoute.practice(practice.id))
            } label: {
                PracticeListRow(practice: practice, emphasized: true)
            }
            .buttonStyle(.plain)
        }
    }

    private var shortAlternativesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.shortAlternatives)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(PracticesExperienceChrome.shortAlternativesSubtitle)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            LazyVStack(spacing: 12) {
                ForEach(shortAlternatives) { item in
                    Button {
                        navigationPath.append(PracticesRoute.practice(item.id))
                    } label: {
                        PracticeListRow(practice: item)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private var asceticismsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.asceticsBlock)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(PracticesExperienceChrome.asceticsSubtitle)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            LazyVStack(alignment: .leading, spacing: 10) {
                ForEach(Array(asceticisms.enumerated()), id: \.offset) { _, item in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(item.title ?? FlowTrackerChrome.asceticFallbackTitle)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                        if let d = item.description, !d.isEmpty {
                            Text(d)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(14)
                    .todayFlowCard()
                }
            }
        }
    }

    private var affirmationsFromPracticesAPISection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.affirmationsApi)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(PracticesExperienceChrome.affirmationsSubtitle)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            LazyVStack(alignment: .leading, spacing: 10) {
                ForEach(Array(practiceAffirmations.prefix(25).enumerated()), id: \.offset) { _, item in
                    VStack(alignment: .leading, spacing: 4) {
                        if let t = item.title, !t.isEmpty {
                            Text(t)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                        }
                        if let text = item.text, !text.isEmpty {
                            Text(text)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(14)
                    .todayFlowCard()
                }
            }
        }
    }

    private var filteredPractices: [PracticeSummaryDTO] {
        practices.filter { p in
            guard periodicityMatches(p) else { return false }
            guard durationMatches(p) else { return false }
            if let cur = currentPractice, cur.id == p.id { return false }
            if let cat = selectedCategoryId, p.category.lowercased() != cat.lowercased() { return false }
            return true
        }
    }

    private var sequencesFiltered: [PracticeSummaryDTO] {
        guard let cat = selectedCategoryId else { return sequences }
        return sequences.filter { $0.category.lowercased() == cat.lowercased() }
    }

    /// Серии показываем отдельным блоком — убираем из общего списка.
    private var catalogForGrid: [PracticeSummaryDTO] {
        filteredPractices.filter { $0.practiceType != "guided_sequence" }
    }

    private var interpretationBundleHasContent: Bool {
        guard let b = interpretationBundle else { return false }
        let text = b.interpretation?.text?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !text.isEmpty { return true }
        if let id = b.practice?.id, !id.isEmpty { return true }
        return false
    }

    private func interpretationBundleCard(_ b: InterpretationBundleDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.interpretationTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            if let day = b.day {
                Text(PracticesExperienceChrome.dayLine(day))
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            if let name = b.pattern?.name, !name.isEmpty {
                Text(name)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            if let text = b.interpretation?.text, !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                Text(text)
                    .font(.body)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let p = b.practice, let id = p.id, !id.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text(p.title ?? PracticesExperienceChrome.practiceFallbackTitle)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    if let d = p.description, !d.isEmpty {
                        Text(d)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                            .lineLimit(4)
                    }
                    Button(PracticesExperienceChrome.openPractice) {
                        navigationPath.append(PracticesRoute.practice(id))
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.accent)
                }
            }
        }
        .padding(18)
        .todayFlowCard()
    }

    private func limitsCard(_ l: PracticeLimitsDTO) -> some View {
        let unlimited = l.subscriptionLevel == "pro" || l.personalizedLimit >= 1000
        return VStack(alignment: .leading, spacing: 10) {
            Text(PracticesExperienceChrome.weeklyLimitTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            HStack {
                Text(PracticesExperienceChrome.planLabel)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                Spacer()
                Text(subscriptionLabel(l.subscriptionLevel))
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            HStack {
                Text(PracticesExperienceChrome.personalizedLine)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                Spacer()
                Text(unlimited ? PracticesExperienceChrome.usedCount(l.usedThisWeek) : "\(l.usedThisWeek) / \(l.personalizedLimit)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            HStack {
                Text(PracticesExperienceChrome.remainingLabel)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                Spacer()
                Text(unlimited ? PracticesExperienceChrome.unlimitedShort : "\(l.remainingThisWeek)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(l.remainingThisWeek == 0 && !unlimited ? TodayFlowTheme.roseClay : TodayFlowTheme.accent)
            }
            Text(PracticesExperienceChrome.weekWith(formatWeekStartDate(l.weekStart)))
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
        }
        .padding(18)
        .todayFlowCard()
    }

    private func subscriptionLabel(_ raw: String) -> String {
        switch raw.lowercased() {
        case "free": return "Free"
        case "lite": return "Lite"
        case "pro": return "Pro"
        default: return raw.capitalized
        }
    }

    private func formatWeekStartDate(_ raw: String) -> String {
        let input = DateFormatter()
        input.locale = Locale(identifier: "en_US_POSIX")
        input.dateFormat = "yyyy-MM-dd"
        guard let date = input.date(from: raw) else { return raw }
        let out = DateFormatter()
        out.locale = Locale(identifier: IOSAppLocale.prefersRussian ? "ru_RU" : "en_US_POSIX")
        out.dateStyle = .long
        out.timeStyle = .none
        return out.string(from: date)
    }

    private func periodicityMatches(_ practice: PracticeSummaryDTO) -> Bool {
        guard periodicity != .all else { return true }
        return periodicity(of: practice) == periodicity
    }

    private func periodicity(of practice: PracticeSummaryDTO) -> PeriodicityFilter {
        if practice.practiceType == "weekly_reflection" || practice.cycleType == "weekly" {
            return .weekly
        }
        if practice.cycleType == "monthly" { return .monthly }
        if practice.practiceType == "cycle_based" || practice.cycleType == "lunar" || practice.cycleType == "transition" {
            return .cycle
        }
        return .daily
    }

    private func durationMatches(_ practice: PracticeSummaryDTO) -> Bool {
        switch duration {
        case .any:
            return true
        case .short:
            let d = practice.durationMinutes
            return d == nil || d! <= 5
        case .medium:
            let d = practice.durationMinutes ?? 0
            return d >= 6 && d <= 10
        case .long:
            let d = practice.durationMinutes
            return d == nil || d! > 10 || practice.practiceType == "guided_sequence"
        }
    }

    private func interpretationBundleForHub() async -> InterpretationBundleDTO? {
        guard isPaidSubscriber, let uid = userId else { return nil }
        let day = PracticeUserDay.dayNumber(userId: uid)
        return await PracticesClient.fetchInterpretationBundle(day: day)
    }

    private func load(force: Bool) async {
        loading = true
        errorMessage = nil
        defer { loading = false }

        async let limitsTask = PracticesClient.fetchPracticeLimits()
        async let sequencesTask = PracticesClient.fetchSequences()
        async let categoriesTask = PracticesClient.fetchPracticeCategories()
        async let shortTask = PracticesClient.fetchShortAlternatives()
        async let ascTask = PracticesClient.fetchAsceticisms()
        async let affTask = PracticesClient.fetchAffirmationsFromPracticesAPI()
        async let bundleTask = interpretationBundleForHub()
        do {
            async let listTask = PracticesClient.fetchPracticesList()
            let cur = await PracticesClient.fetchCurrentPractice()
            let list = try await listTask
            let lim = await limitsTask
            let seq = await sequencesTask
            let cats = await categoriesTask
            let bundle = await bundleTask
            let short = await shortTask
            let asc = await ascTask
            let aff = await affTask
            await MainActor.run {
                practices = list
                currentPractice = cur
                limits = lim
                sequences = seq
                categories = cats
                interpretationBundle = bundle
                shortAlternatives = short
                asceticisms = asc
                practiceAffirmations = aff
            }
        } catch {
            let lim = await limitsTask
            let seq = await sequencesTask
            let cats = await categoriesTask
            let bundle = await bundleTask
            let short = await shortTask
            let asc = await ascTask
            let aff = await affTask
            await MainActor.run {
                practices = []
                currentPractice = nil
                limits = lim
                sequences = seq
                categories = cats
                interpretationBundle = bundle
                shortAlternatives = short
                asceticisms = asc
                practiceAffirmations = aff
                errorMessage = error.localizedDescription
            }
        }
    }
}

// MARK: - История и прогресс (аналог веб `/practices/history`)

struct PracticesHistoryView: View {
    @Binding var navigationPath: NavigationPath

    @State private var historyPayload: PracticeHistoryResponseDTO?
    @State private var progress: PracticeProgressResponseDTO?
    @State private var loading = true
    @State private var errorMessage: String?

    private static func completedAtFormatter() -> DateFormatter {
        let f = DateFormatter()
        f.locale = Locale(identifier: IOSAppLocale.prefersRussian ? "ru_RU" : "en_US_POSIX")
        f.dateStyle = .long
        f.timeStyle = .short
        return f
    }

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            if loading, historyPayload == nil, errorMessage == nil {
                ProgressView(PracticesExperienceChrome.loadingHistory)
                    .tint(TodayFlowTheme.accent)
            } else if let errorMessage {
                Text(errorMessage)
                    .font(.body)
                    .foregroundStyle(TodayFlowTheme.roseClay)
                    .padding(24)
            } else {
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 22) {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(PracticesExperienceChrome.historyProgressTitle)
                                .font(.title2.weight(.bold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(PracticesExperienceChrome.historyProgressSubtitle)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(.horizontal, 4)

                        if let progress {
                            progressCard(progress)
                        }

                        if let historyPayload, !historyPayload.history.isEmpty {
                            historyListCard(historyPayload)
                        } else {
                            emptyHistoryCard
                        }
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 16)
                }
            }
        }
        .navigationTitle(PracticesExperienceChrome.navHistory)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button {
                    Task { await load(force: true) }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
        .task {
            await load(force: false)
        }
        .refreshable {
            await load(force: true)
        }
    }

    private var emptyHistoryCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(PracticesExperienceChrome.emptyHistoryTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(PracticesExperienceChrome.emptyHistoryBody)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
            Button(PracticesExperienceChrome.toCatalog) {
                navigationPath = NavigationPath()
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.accent)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowCard()
    }

    private func progressCard(_ p: PracticeProgressResponseDTO) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(PracticesExperienceChrome.statistics)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 14) {
                statCell(title: PracticesExperienceChrome.statTotalDone, value: "\(p.totalCompleted)", accent: TodayFlowTheme.accent)
                statCell(title: PracticesExperienceChrome.statPersonalized, value: "\(p.personalizedCompleted)", accent: TodayFlowTheme.sunset)
                statCell(title: PracticesExperienceChrome.statCurrentStreak, value: PracticesExperienceChrome.daysStreak(p.currentStreakDays), accent: TodayFlowTheme.ember)
                statCell(title: PracticesExperienceChrome.statBestStreak, value: PracticesExperienceChrome.daysStreak(p.longestStreakDays), accent: TodayFlowTheme.ink)
                statCell(title: PracticesExperienceChrome.statWeeksActive, value: "\(p.weeksActive)", accent: TodayFlowTheme.ink)
            }

            if !p.byCategory.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text(PracticesExperienceChrome.byCategory)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    ForEach(p.byCategory) { cat in
                        VStack(alignment: .leading, spacing: 6) {
                            HStack {
                                Text(PracticesExperienceChrome.categoryDisplay(cat.category))
                                    .font(.subheadline.weight(.medium))
                                Spacer()
                                Text(PracticesExperienceChrome.practicesCount(cat.totalCompleted))
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                            GeometryReader { geo in
                                let maxTotal = max(p.totalCompleted, 1)
                                let width = geo.size.width * CGFloat(min(1, Double(cat.totalCompleted) / Double(maxTotal)))
                                ZStack(alignment: .leading) {
                                    Capsule()
                                        .fill(Color.black.opacity(0.08))
                                        .frame(height: 8)
                                    Capsule()
                                        .fill(TodayFlowTheme.accent.opacity(0.85))
                                        .frame(width: max(4, width), height: 8)
                                }
                            }
                            .frame(height: 8)
                        }
                    }
                }
            }
        }
        .padding(18)
        .todayFlowCard()
    }

    private func statCell(title: String, value: String, accent: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(value)
                .font(.title3.weight(.bold))
                .foregroundStyle(accent)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.black.opacity(0.04), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func historyListCard(_ payload: PracticeHistoryResponseDTO) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("\(PracticesExperienceChrome.completedPractices) (\(payload.total))")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            LazyVStack(spacing: 12) {
                ForEach(payload.history) { item in
                    HStack(alignment: .top, spacing: 12) {
                        VStack(alignment: .leading, spacing: 6) {
                            HStack(alignment: .firstTextBaseline, spacing: 8) {
                                Text(item.practiceTitle ?? item.practiceId)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                    .multilineTextAlignment(.leading)
                                if item.isPersonalized {
                                    Text(PracticesExperienceChrome.forYouBadge)
                                        .font(.caption2.weight(.semibold))
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(TodayFlowTheme.accent.opacity(0.18), in: Capsule())
                                        .foregroundStyle(TodayFlowTheme.accent)
                                }
                            }
                            if item.sequenceId != nil, let step = item.stepNumber {
                                Text(PracticesExperienceChrome.sequenceStep(step))
                                    .font(.caption2)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                            if let cat = item.category {
                                Text(PracticesExperienceChrome.categoryDisplay(cat))
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                            Text(Self.completedAtFormatter().string(from: item.completedAt))
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                        Spacer(minLength: 8)
                        Button(PracticesExperienceChrome.repeatCta) {
                            let base = basePracticeId(item.practiceId)
                            navigationPath.append(PracticesRoute.practice(base))
                        }
                        .font(.subheadline.weight(.semibold))
                        .buttonStyle(.bordered)
                    }
                    .padding(14)
                    .todayFlowCard()
                }
            }
        }
    }

    private func basePracticeId(_ raw: String) -> String {
        raw.components(separatedBy: "-step-").first ?? raw
    }

    private func load(force: Bool) async {
        loading = true
        errorMessage = nil
        defer { loading = false }

        async let progressTask = PracticesClient.fetchPracticeProgress()
        do {
            let hist = try await PracticesClient.fetchPracticeHistory(limit: 100)
            let prog = await progressTask
            await MainActor.run {
                historyPayload = hist
                progress = prog
            }
        } catch {
            await MainActor.run {
                historyPayload = nil
                progress = nil
                errorMessage = error.localizedDescription
            }
        }
    }
}

// MARK: - Строка списка

private struct PracticeListRow: View {
    let practice: PracticeSummaryDTO
    var emphasized: Bool = false
    var sequenceBadge: Bool = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(practice.title)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                    .multilineTextAlignment(.leading)
                Spacer()
                if sequenceBadge || practice.practiceType == "guided_sequence" {
                    Text(PracticesExperienceChrome.seriesBadge)
                        .font(.caption2.weight(.semibold))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(TodayFlowTheme.sunset.opacity(0.2), in: Capsule())
                        .foregroundStyle(TodayFlowTheme.ember)
                }
                if practice.isPersonalized {
                    Text(PracticesExperienceChrome.forYouBadge)
                        .font(.caption2.weight(.semibold))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(TodayFlowTheme.accent.opacity(0.18), in: Capsule())
                        .foregroundStyle(TodayFlowTheme.accent)
                }
            }
            Text(practice.description)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .lineLimit(3)
                .multilineTextAlignment(.leading)

            HStack(spacing: 8) {
                Text(PracticesExperienceChrome.categoryDisplay(practice.category))
                    .font(.caption2.weight(.medium))
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.black.opacity(0.06), in: Capsule())
                if let minutes = practice.durationMinutes {
                    Text("\(minutes) \(PracticesExperienceChrome.minutesShort)")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
                Text(PracticesExperienceChrome.difficultyDisplay(practice.difficulty))
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }

            if !practice.tags.isEmpty {
                FlowPracticeTags(tags: practice.tags)
            }
        }
        .padding(16)
        .background(
            emphasized
                ? LinearGradient(
                    colors: [TodayFlowTheme.accent.opacity(0.12), TodayFlowTheme.cardStrong],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                : LinearGradient(colors: [TodayFlowTheme.cardStrong, TodayFlowTheme.cardStrong], startPoint: .top, endPoint: .bottom),
            in: RoundedRectangle(cornerRadius: 20, style: .continuous)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(emphasized ? TodayFlowTheme.accent.opacity(0.35) : TodayFlowTheme.contour.opacity(0.9), lineWidth: 1)
        )
    }

}

private struct FlowPracticeTags: View {
    let tags: [String]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 6) {
                ForEach(tags, id: \.self) { tag in
                    Text(tag)
                        .font(.caption2.weight(.medium))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.black.opacity(0.05), in: Capsule())
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
            }
        }
    }
}

// MARK: - Аудио (как `<audio>` на вебе)

private struct PracticeAudioInlinePlayer: View {
    let url: URL
    @State private var player: AVPlayer?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(PracticesExperienceChrome.audioSection)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            if let player {
                VideoPlayer(player: player)
                    .frame(height: 52)
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            } else {
                ProgressView()
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
            }
        }
        .onAppear {
            if player == nil {
                player = AVPlayer(url: url)
            }
        }
        .onDisappear {
            player?.pause()
        }
    }
}

// MARK: - Деталь + завершение

struct PracticeDetailScreen: View {
    let practiceId: String

    @State private var detail: PracticeDetailDTO?
    @State private var sequenceProgress: SequenceProgressDTO?
    @State private var sequenceProgressError: String?
    @State private var loading = true
    @State private var errorMessage: String?
    @State private var completing = false
    @State private var completed = false
    @State private var completeError: String?

    private var isGuidedSequence: Bool {
        detail?.practiceType == "guided_sequence" && detail?.sequenceId != nil
    }

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            if loading, detail == nil {
                ProgressView()
            } else if let detail {
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 18) {
                        Text(detail.title)
                            .font(.title2.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.ink)

                        Text(detail.description)
                            .font(.body)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                            .fixedSize(horizontal: false, vertical: true)

                        if let reason = detail.personalizedReason, !reason.isEmpty, detail.isPersonalized {
                            Text(reason)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.accent)
                                .padding(14)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(TodayFlowTheme.accent.opacity(0.1), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                        }

                        if let audioURL = resolvedPracticeAudioURL(detail.audioUrl) {
                            PracticeAudioInlinePlayer(url: audioURL)
                        }

                        if isGuidedSequence, let sp = sequenceProgress {
                            sequenceProgressBlock(sp)
                        } else if isGuidedSequence, sequenceProgress == nil, loading == false, let err = sequenceProgressError {
                            Text(err)
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.roseClay)
                                .padding(12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .todayFlowCard()
                        }

                        if let prompt = detail.prompt, !prompt.isEmpty {
                            VStack(alignment: .leading, spacing: 6) {
                                Text(PracticesExperienceChrome.hintSection)
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                                Text(prompt)
                                    .font(.body)
                                    .foregroundStyle(TodayFlowTheme.ink)
                            }
                            .padding(16)
                            .todayFlowCard()
                        }

                        if let steps = detail.steps, !steps.isEmpty {
                            VStack(alignment: .leading, spacing: 12) {
                                Text(PracticesExperienceChrome.stepsSection)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                ForEach(steps) { step in
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text(PracticesExperienceChrome.stepLine(step.stepNumber, step.title))
                                            .font(.subheadline.weight(.semibold))
                                            .foregroundStyle(TodayFlowTheme.ink)
                                        Text(step.description)
                                            .font(.subheadline)
                                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                                        if let ins = step.instructions {
                                            ForEach(Array(ins.enumerated()), id: \.offset) { _, line in
                                                Text("· \(line)")
                                                    .font(.footnote)
                                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                                            }
                                        }
                                    }
                                    .padding(14)
                                    .todayFlowCard()
                                }
                            }
                        }

                        if let instructions = detail.instructions, !instructions.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Text(PracticesExperienceChrome.howToSection)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                ForEach(Array(instructions.enumerated()), id: \.offset) { index, line in
                                    HStack(alignment: .top, spacing: 10) {
                                        Text("\(index + 1)")
                                            .font(.caption.weight(.bold))
                                            .foregroundStyle(.white)
                                            .frame(width: 24, height: 24)
                                            .background(TodayFlowTheme.accent, in: Circle())
                                        Text(line)
                                            .font(.body)
                                            .foregroundStyle(TodayFlowTheme.ink)
                                            .fixedSize(horizontal: false, vertical: true)
                                    }
                                }
                            }
                            .padding(16)
                            .todayFlowCard()
                        }

                        if let questions = detail.questions, !questions.isEmpty {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(PracticesExperienceChrome.reflectionSection)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                ForEach(Array(questions.enumerated()), id: \.offset) { _, q in
                                    Text("· \(q)")
                                        .font(.subheadline)
                                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                                }
                            }
                            .padding(16)
                            .todayFlowCard()
                        }

                        if let related = detail.relatedPractices, !related.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Text(PracticesExperienceChrome.relatedSection)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                ForEach(related, id: \.self) { rid in
                                    NavigationLink {
                                        PracticeDetailScreen(practiceId: rid)
                                    } label: {
                                        HStack {
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(PracticesExperienceChrome.openPractice)
                                                    .font(.subheadline.weight(.semibold))
                                                    .foregroundStyle(TodayFlowTheme.ink)
                                                Text(rid)
                                                    .font(.caption2)
                                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                                                    .lineLimit(1)
                                            }
                                            Spacer()
                                            Image(systemName: "chevron.right")
                                                .font(.caption.weight(.semibold))
                                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                        }
                                        .padding(14)
                                        .todayFlowCard()
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }

                        if isGuidedSequence, let sp = sequenceProgress, sp.isCompleted {
                            HStack(spacing: 10) {
                                Image(systemName: "checkmark.seal.fill")
                                    .foregroundStyle(TodayFlowTheme.accent)
                                Text(PracticesExperienceChrome.sequenceComplete)
                                    .font(.subheadline.weight(.medium))
                                    .foregroundStyle(TodayFlowTheme.ink)
                            }
                            .padding(16)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(TodayFlowTheme.accent.opacity(0.12), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                        } else if isGuidedSequence, let sp = sequenceProgress, let step = sp.currentStep, !sp.isCompleted {
                            Button {
                                Task { await completeSequenceStep(step) }
                            } label: {
                                Label(completing ? PracticesExperienceChrome.saving : PracticesExperienceChrome.completeStep(step), systemImage: "checkmark.circle.fill")
                                    .font(.headline)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 16)
                            }
                            .buttonStyle(.plain)
                            .foregroundStyle(.white)
                            .background(
                                LinearGradient(
                                    colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                ),
                                in: RoundedRectangle(cornerRadius: 20, style: .continuous)
                            )
                            .disabled(completing)
                        } else if !isGuidedSequence, !completed {
                            Button {
                                Task { await markComplete() }
                            } label: {
                                Label(completing ? PracticesExperienceChrome.saving : PracticesExperienceChrome.markComplete, systemImage: "checkmark.circle.fill")
                                    .font(.headline)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 16)
                            }
                            .buttonStyle(.plain)
                            .foregroundStyle(.white)
                            .background(
                                LinearGradient(
                                    colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember],
                                    startPoint: .leading,
                                    endPoint: .trailing
                                ),
                                in: RoundedRectangle(cornerRadius: 20, style: .continuous)
                            )
                            .disabled(completing)
                        } else if !isGuidedSequence, completed {
                            HStack(spacing: 10) {
                                Image(systemName: "checkmark.seal.fill")
                                    .foregroundStyle(TodayFlowTheme.accent)
                                Text(PracticesExperienceChrome.savedToHistory)
                                    .font(.subheadline.weight(.medium))
                                    .foregroundStyle(TodayFlowTheme.ink)
                            }
                            .padding(16)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(TodayFlowTheme.accent.opacity(0.12), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                        }

                        if let completeError {
                            Text(completeError)
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.roseClay)
                        }
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 16)
                }
            } else if let errorMessage {
                Text(errorMessage)
                    .font(.body)
                    .foregroundStyle(TodayFlowTheme.roseClay)
                    .padding(24)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .navigationTitle(detail?.title ?? PracticesExperienceChrome.practiceFallbackTitle)
        .task {
            await loadDetail()
        }
    }

    private func sequenceProgressBlock(_ sp: SequenceProgressDTO) -> some View {
        let total = max(sp.totalSteps, 1)
        let ratio = CGFloat(sp.completedSteps) / CGFloat(total)
        return VStack(alignment: .leading, spacing: 10) {
            Text(PracticesExperienceChrome.sequenceProgressTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            HStack {
                Text(PracticesExperienceChrome.stepsDoneLabel)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                Spacer()
                Text("\(sp.completedSteps) / \(sp.totalSteps)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule()
                        .fill(Color.black.opacity(0.08))
                        .frame(height: 8)
                    Capsule()
                        .fill(TodayFlowTheme.accent)
                        .frame(width: max(6, geo.size.width * ratio), height: 8)
                }
            }
            .frame(height: 8)
            if let next = sp.currentStep, !sp.isCompleted {
                Text(PracticesExperienceChrome.nextStep("\(next)"))
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(16)
        .background(TodayFlowTheme.accent.opacity(0.06), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.accent.opacity(0.22), lineWidth: 1)
        )
    }

    private func loadDetail() async {
        loading = true
        errorMessage = nil
        sequenceProgressError = nil
        defer { loading = false }
        do {
            let d = try await PracticesClient.fetchPracticeDetail(id: practiceId)
            await MainActor.run {
                detail = d
            }
            if d.practiceType == "guided_sequence", let sid = d.sequenceId {
                do {
                    let sp = try await PracticesClient.fetchSequenceProgress(sequenceId: sid)
                    await MainActor.run {
                        sequenceProgress = sp
                        sequenceProgressError = nil
                    }
                } catch {
                    await MainActor.run {
                        sequenceProgress = nil
                        sequenceProgressError = error.localizedDescription
                    }
                }
            } else {
                await MainActor.run {
                    sequenceProgress = nil
                    sequenceProgressError = nil
                }
            }
        } catch {
            await MainActor.run {
                detail = nil
                sequenceProgress = nil
                errorMessage = practicesErrorDisplayMessage(error)
            }
        }
    }

    /// Единый текст для загрузки детали и для ошибок «завершить практику / шаг серии».
    private func practicesErrorDisplayMessage(_ error: Error) -> String {
        guard let err = error as? PracticesClientError else {
            return error.localizedDescription
        }
        if case let .badStatus(code, body) = err, code == 403 {
            let trimmed = body.trimmingCharacters(in: .whitespacesAndNewlines)
            let head = trimmed.isEmpty ? PracticesExperienceChrome.errorPractice403Head : trimmed
            return head + "\n\n" + PracticesExperienceChrome.errorPractice403Tail
        }
        return err.errorDescription ?? error.localizedDescription
    }

    private func resolvedPracticeAudioURL(_ raw: String?) -> URL? {
        guard let raw = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty else { return nil }
        if let u = URL(string: raw), u.scheme != nil { return u }
        return URL(string: raw, relativeTo: AppConfig.apiBaseURL)?.absoluteURL
    }

    private func completeSequenceStep(_ step: Int) async {
        guard let sid = detail?.sequenceId else { return }
        completing = true
        completeError = nil
        defer { completing = false }
        do {
            _ = try await PracticesClient.completeSequenceStep(sequenceId: sid, stepNumber: step)
            let sp = try await PracticesClient.fetchSequenceProgress(sequenceId: sid)
            await MainActor.run {
                sequenceProgress = sp
            }
        } catch {
            await MainActor.run {
                completeError = practicesErrorDisplayMessage(error)
            }
        }
    }

    private func markComplete() async {
        completing = true
        completeError = nil
        defer { completing = false }
        do {
            _ = try await PracticesClient.completePractice(id: practiceId)
            await MainActor.run {
                completed = true
            }
        } catch {
            await MainActor.run {
                completeError = practicesErrorDisplayMessage(error)
            }
        }
    }
}

#Preview("Practices hub") {
    _PracticesHubPreviewShell()
}

private struct _PracticesHubPreviewShell: View {
    @State private var path = NavigationPath()
    @State private var openHistory = false

    var body: some View {
        PracticesRootView(path: $path, openHistoryFromDeepLink: $openHistory, openPracticeIdFromDeepLink: .constant(nil), userId: nil)
    }
}
