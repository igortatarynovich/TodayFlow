import SwiftUI

/// Паритет с `profileSections.ts` на вебе: порядок и короткие подписи для быстрых переходов.
private enum ProfileHubAnchor: String, CaseIterable, Identifiable {
    case portrait
    case chart
    case spheres
    case patterns
    case pulse
    case circle
    case accuracy

    var id: String { rawValue }

    var shortTitle: String {
        switch self {
        case .portrait: return "Портрет"
        case .chart: return "Карта"
        case .spheres: return "Сферы"
        case .patterns: return "Паттерны"
        case .pulse: return "Живой слой"
        case .circle: return "Круг"
        case .accuracy: return "Точность"
        }
    }
}

private struct ProfileHubQuickNav: View {
    let onJump: (String) -> Void

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(ProfileHubAnchor.allCases) { anchor in
                    Button {
                        onJump(anchor.rawValue)
                    } label: {
                        Text(anchor.shortTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(Color.white.opacity(0.78))
                            .clipShape(Capsule())
                            .overlay(
                                Capsule()
                                    .stroke(TodayFlowTheme.sunset.opacity(0.22), lineWidth: 1)
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.vertical, 2)
        }
    }
}

private struct ProfileEditSheetItem: Identifiable {
    let id: Int
    let profile: StoredAstroProfile
}

struct ProfileView: View {
    let store: TodayFlowStore
    var onOpenCompatibility: (() -> Void)? = nil
    var onOpenProfileSummaryRoute: ((AppTab) -> Void)? = nil
    @State private var profiles: [StoredAstroProfile] = []
    @State private var isLoadingProfiles = false
    @State private var profileError: String?
    @State private var isAddProfilePresented = false
    @State private var profileEditSheet: ProfileEditSheetItem?
    @State private var isSettingsPresented = false
    @State private var coreProfileError: String?
    @State private var isLoadingCoreProfile = false
    @State private var natalError: String?
    @State private var isLoadingNatal = false
    @State private var isProfileSummaryPresented = false
    @State private var chartDeepExpanded = false
    @State private var mapsPath = NavigationPath()
    @State private var showProfileTeaser = TodayFirstTodayState.shouldShowProfileTeaser
    
    private static let statusDateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = .current
        formatter.setLocalizedDateFormatFromTemplate("d MMM, HH:mm")
        return formatter
    }()

    var body: some View {
        NavigationStack(path: $mapsPath) {
            ScrollViewReader { scrollProxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                    if let warning = AppConfig.runtimeConnectionWarning {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Подключение")
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(warning)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                        .padding(18)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.66))
                        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                    }

                    #if DEBUG
                    if store.authSession != nil {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("Сессия и данные (отладка)")
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(sessionStatusLine)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            Text(snapshotStatusLine)
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.secondaryInk.opacity(0.9))
                        }
                        .padding(14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.66))
                        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                    }
                    #endif

                    if showProfileTeaser {
                        ProfileFirstDayTeaserView(
                            coreProfile: store.coreProfile,
                            store: store,
                            onOpenFullPortrait: {
                                TodayFirstTodayState.markProfileDepthUnlocked()
                                showProfileTeaser = false
                            }
                        )
                    } else {
                    ProfileQuickMapView(
                        model: ProfileQuickMapBuilder.build(
                            coreProfile: store.coreProfile,
                            natalChart: store.natalChart,
                            cum: store.compactUserModel
                        ),
                        store: store,
                        chartDeepExpanded: $chartDeepExpanded,
                        natalChart: store.natalChart,
                        coreProfile: store.coreProfile,
                        isLoadingNatal: isLoadingNatal,
                        natalError: natalError,
                        onOpenBirthData: {
                            if let primary = profiles.first(where: { $0.isPrimary == true }) ?? profiles.first {
                                profileEditSheet = ProfileEditSheetItem(id: primary.id, profile: primary)
                            } else {
                                isAddProfilePresented = true
                            }
                        },
                        onReloadNatal: { await loadNatalChart(force: true) },
                        onOpenToday: nil,
                        onOpenRhythm: {
                            onOpenProfileSummaryRoute?(.calendar)
                        }
                    )
                    }

                    if isLoadingCoreProfile {
                        ProgressView("Собираю профиль...")
                            .tint(TodayFlowTheme.sunset)
                            .padding(.horizontal, 8)
                    } else if let coreProfileError {
                        Text(coreProfileError)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.roseClay)
                            .padding(.horizontal, 8)
                    }

                    if let coreProfile = store.coreProfile {
                        ProfileLifeSections(coreProfile: coreProfile, natalChart: store.natalChart)
                            .id(ProfileHubAnchor.spheres.rawValue)
                    }

                    if let coreProfile = store.coreProfile {
                        ProfilePatternsStubSection(coreProfile: coreProfile)
                            .id(ProfileHubAnchor.patterns.rawValue)
                    }

                    VStack(alignment: .leading, spacing: 18) {
                        if let living = store.coreProfile?.living {
                            ProfilePulseSection(living: living)
                        }
                        if let todayCycle = store.todayCycle {
                            ProfileTodayMirrorSection(cycle: todayCycle)
                        }
                        if !store.fusionHistory.isEmpty {
                            ProfileRhythmCalendarSection(history: store.fusionHistory)
                        }
                    }
                    .id(ProfileHubAnchor.pulse.rawValue)

                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text("Круг людей")
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                Text("Здесь хранится твой круг для совместимости и дальнейших персональных разборов.")
                                    .font(.subheadline)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                            }
                            Spacer()
                            Button("Добавить профиль") {
                                isAddProfilePresented = true
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(TodayFlowTheme.sunset)
                        }

                        if profiles.count >= 2 {
                            Button("Открыть совместимость") {
                                onOpenCompatibility?()
                            }
                            .buttonStyle(.bordered)
                        }

                        if isLoadingProfiles {
                            ProgressView("Загружаю профили...")
                                .tint(TodayFlowTheme.sunset)
                        } else if profiles.isEmpty {
                            Text("Пока есть только твой основной профиль. Добавь второго человека, чтобы открыть совместимость прямо из iOS.")
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .padding(16)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.white.opacity(0.58))
                                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                        } else {
                            ForEach(profiles) { profile in
                                ProfileCircleCard(
                                    profile: profile,
                                    onMakePrimary: { await makePrimary(profile.id) },
                                    onDelete: { await deleteProfile(profile.id) },
                                    onRefine: {
                                        profileEditSheet = ProfileEditSheetItem(id: profile.id, profile: profile)
                                    }
                                )
                            }
                        }

                        if let profileError {
                            Text(profileError)
                                .font(.footnote)
                                .foregroundStyle(TodayFlowTheme.roseClay)
                        }
                    }
                    .padding(22)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.66))
                    .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                    .id(ProfileHubAnchor.circle.rawValue)

                    if let rewards = store.todayCycle?.rewards {
                        ProfileGrowthSection(
                            rewards: rewards,
                            milestones: store.todayCycle?.rewardMilestones ?? []
                        )
                        .id(ProfileHubAnchor.accuracy.rawValue)
                    }
                    }
                    .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(TodayBackground())
                .onChange(of: store.profileNatalScrollToken) { _, token in
                    guard token != nil else { return }
                    chartDeepExpanded = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.06) {
                        withAnimation(.easeInOut(duration: 0.45)) {
                            scrollProxy.scrollTo("profileNatalChartAnchor", anchor: .top)
                        }
                        store.profileNatalScrollToken = nil
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .navigationTitle("Профиль")
            .todayflowNavigationBarTitleDisplayModeInline()
            .task {
                async let profilesTask: Void = loadProfiles()
                async let coreTask: Void = loadCoreProfile()
                async let natalTask: Void = loadNatalChart()
                async let summaryTask: Void = loadProfileSummary()
                async let cumTask: Void = loadCompactUserModel()
                _ = await (profilesTask, coreTask, natalTask, summaryTask, cumTask)
            }
            .sheet(isPresented: $isAddProfilePresented) {
                AddProfileView(store: store) {
                    await loadProfiles(force: true)
                    await loadCoreProfile(force: true)
                    await loadNatalChart(force: true)
                }
            }
            .sheet(item: $profileEditSheet) { item in
                EditAstroProfileView(store: store, profile: item.profile) {
                    await loadProfiles(force: true)
                    await loadCoreProfile(force: true)
                    await loadNatalChart(force: true)
                }
            }
            .sheet(isPresented: $isSettingsPresented) {
                ProfileSettingsView(store: store)
            }
            .sheet(isPresented: $isProfileSummaryPresented) {
                ProfileSummaryView(store: store) { tab in
                    isProfileSummaryPresented = false
                    onOpenProfileSummaryRoute?(tab)
                }
            }
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        isSettingsPresented = true
                    } label: {
                        Label("Настройки", systemImage: "slider.horizontal.3")
                    }
                }
            }
            .navigationDestination(for: MapNavigationDestination.self) { destination in
                mapDestinationView(destination, store: store, onOpenRhythm: {
                    onOpenProfileSummaryRoute?(.calendar)
                })
            }
            .onChange(of: store.pendingMapNavigation) { _, destination in
                guard let destination else { return }
                mapsPath.append(destination)
                store.pendingMapNavigation = nil
            }
        }
    }

    private var sessionStatusLine: String {
        if let validatedAt = store.lastSessionValidatedAt {
            return "Последняя проверка входа: \(Self.statusDateFormatter.string(from: validatedAt))"
        }
        return "Проверка входа еще не выполнялась в этой сессии."
    }

    private var snapshotStatusLine: String {
        if let savedAt = store.lastSnapshotSavedAt {
            return "Локальный снимок данных сохранен: \(Self.statusDateFormatter.string(from: savedAt))"
        }
        return "Локальный снимок данных пока не создан."
    }

    private func loadProfiles(force: Bool = false) async {
        if isLoadingProfiles { return }
        if !force, !profiles.isEmpty { return }

        isLoadingProfiles = true
        profileError = nil
        do {
            let loaded = try await store.loadAstroProfiles()
            await MainActor.run {
                profiles = loaded
                isLoadingProfiles = false
            }
        } catch {
            await MainActor.run {
                profileError = error.localizedDescription
                isLoadingProfiles = false
            }
        }
    }

    private func makePrimary(_ profileID: Int) async {
        do {
            try await store.setPrimaryAstroProfile(profileID: profileID)
            await loadProfiles(force: true)
            await loadCoreProfile(force: true)
            await loadNatalChart(force: true)
        } catch {
            await MainActor.run {
                profileError = error.localizedDescription
            }
        }
    }

    private func deleteProfile(_ profileID: Int) async {
        do {
            try await store.deleteAstroProfile(profileID: profileID)
            await loadProfiles(force: true)
            await loadCoreProfile(force: true)
        } catch {
            await MainActor.run {
                profileError = error.localizedDescription
            }
        }
    }

    private func loadNatalChart(force: Bool = false) async {
        if isLoadingNatal { return }
        if store.natalChart != nil, !force { return }

        isLoadingNatal = true
        natalError = nil
        do {
            _ = try await store.loadNatalChart(force: force)
            await MainActor.run {
                isLoadingNatal = false
            }
        } catch {
            await MainActor.run {
                natalError = error.localizedDescription
                isLoadingNatal = false
            }
        }
    }

    private func loadProfileSummary(force: Bool = false) async {
        do {
            _ = try await store.loadProfileSummary(force: force)
        } catch {
            // Non-blocking layer.
        }
    }

    private func loadCoreProfile(force: Bool = false) async {
        if isLoadingCoreProfile { return }
        if store.coreProfile != nil, !force { return }

        isLoadingCoreProfile = true
        coreProfileError = nil
        do {
            _ = try await store.loadCoreProfile(force: force)
            await MainActor.run {
                isLoadingCoreProfile = false
            }
        } catch {
            await MainActor.run {
                coreProfileError = error.localizedDescription
                isLoadingCoreProfile = false
            }
        }
    }

    private func loadCompactUserModel(force: Bool = false) async {
        do {
            _ = try await store.loadCompactUserModel(force: force)
        } catch {
            // Non-blocking enrichment for Quick Map.
        }
    }
}

private struct ProfileAdaptiveStack<Content: View>: View {
    let spacing: CGFloat
    let alignment: HorizontalAlignment
    @ViewBuilder let content: () -> Content

    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    init(
        spacing: CGFloat = 12,
        alignment: HorizontalAlignment = .leading,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.spacing = spacing
        self.alignment = alignment
        self.content = content
    }

    var body: some View {
        if horizontalSizeClass == .compact {
            VStack(alignment: alignment, spacing: spacing) {
                content()
            }
        } else {
            HStack(alignment: .top, spacing: spacing) {
                content()
            }
        }
    }
}

func profileAdaptiveColumns(for horizontalSizeClass: UserInterfaceSizeClass?) -> [GridItem] {
    if horizontalSizeClass == .compact {
        return [GridItem(.flexible())]
    }
    return [GridItem(.flexible()), GridItem(.flexible())]
}

private struct ProfileSignatureHero: View {
    let user: UserProfile
    let birthProfile: BirthProfile?
    let todayCycle: TodayCycle?
    let fusionIndex: FusionIndex?
    let coreProfile: CoreProfileResponse?
    let natalChart: NatalChartPreview?
    let contour: LifeLevelContour
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            ProfileAdaptiveStack(spacing: 16) {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Профиль")
                        .font(.system(size: 30, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(titleLine)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                    Text("Твой профиль в одном месте: видно, как меняется день и что тебе помогает.")
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                        .fixedSize(horizontal: false, vertical: true)

                    FlowLayout(spacing: 8, items: summaryChips) { chip in
                        ProfileSummaryChip(title: chip.title, value: chip.value, tint: chip.tint)
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Контур")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(rewardTitle)
                        .font(.title3.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(rewardSubtitle)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(16)
                .frame(maxWidth: horizontalSizeClass == .compact ? .infinity : 220, alignment: .leading)
                .background(Color.white.opacity(0.72))
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            }

            ProfileAdaptiveStack(spacing: 12) {
                ProfileSignatureCard(title: "Солнце", value: sunValue)
                ProfileSignatureCard(title: "Луна", value: moonValue)
                ProfileSignatureCard(title: "Асцендент", value: risingValue)
            }

            ProfileAdaptiveStack(spacing: 12) {
                ProfileHeaderSignalCard(
                    title: "Дата и место",
                    text: birthMetaLine
                )
                ProfileHeaderSignalCard(
                    title: "Ритм",
                    text: coreProfile?.baseline.rhythmStyle ?? "Ритм будет уточняться по дням и закрытиям"
                )
                ProfileHeaderSignalCard(
                    title: "Срез «кто я»",
                    text: "Профиль собирает ведущую линию, слабое место и следующий внутренний шаг. Это же тянется в Today и в вопросы, когда задаёшь вопрос дню."
                )
            }

        }
        .padding(24)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.92), TodayFlowTheme.paper.opacity(0.88), TodayFlowTheme.mist.opacity(0.82)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 30, style: .continuous))
    }

    private var titleLine: String {
        let firstName = birthProfile?.firstName ?? user.firstName
        if let prism = todayCycle?.morning?.dailyHoroscope?.profilePrism, !prism.isEmpty {
            return firstName.isEmpty ? prism : "\(firstName), \(prism)"
        }
        if let identity = coreProfile?.interpretation?.identity, !identity.isEmpty {
            return firstName.isEmpty ? identity : "\(firstName), \(identity)"
        }
        if let focus = birthProfile?.focusTitle, !focus.isEmpty {
            return firstName.isEmpty ? focus : "\(firstName), \(focus)"
        }
        return firstName.isEmpty ? "Твоя карта состояния и ритма" : "\(firstName), твоя карта состояния и ритма"
    }

    private var rewardTitle: String {
        "\(contour.tier.title) · \(contour.score)"
    }

    private var rewardSubtitle: String {
        contour.statusLine
    }

    private var sunValue: String {
        if let c = natalChart, let line = ZodiacSignRU.planetLine(c, body: "sun") {
            return line
        }
        if let s = coreProfile?.astro.sunSign, !s.isEmpty { return ZodiacSignRU.title(s) }
        if let s = birthProfile?.sunSign, !s.isEmpty { return ZodiacSignRU.title(s) }
        return "Собирается"
    }

    private var moonValue: String {
        if let c = natalChart, let line = ZodiacSignRU.planetLine(c, body: "moon") {
            return line
        }
        if let s = birthProfile?.moonSign, !s.isEmpty { return ZodiacSignRU.title(s) }
        return "Нужен расчёт натала"
    }

    private var risingValue: String {
        if let c = natalChart, let line = ZodiacSignRU.ascendantLine(c) {
            return line
        }
        if let s = birthProfile?.risingSign, !s.isEmpty { return ZodiacSignRU.title(s) }
        return "Нужен расчёт натала"
    }

    private var birthMetaLine: String {
        let date = birthProfile?.formattedBirthSummary ?? coreProfile?.astro.birthDate
        let place = birthProfile?.birthPlace ?? coreProfile?.astro.locationName
        return [date, place].compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: " · ")
    }

    private var summaryChips: [ProfileChipItem] {
        var items: [ProfileChipItem] = []
        if let lifePath = coreProfile?.numerology.lifePath {
            items.append(ProfileChipItem(title: "Путь", value: "\(lifePath)", tint: TodayFlowTheme.gold))
        }
        if let expression = coreProfile?.numerology.expression {
            items.append(ProfileChipItem(title: "Имя", value: "\(expression)", tint: TodayFlowTheme.ember))
        }
        if let soul = coreProfile?.numerology.soulUrge {
            items.append(ProfileChipItem(title: "Суть", value: "\(soul)", tint: TodayFlowTheme.twilight))
        }
        if let personality = coreProfile?.numerology.personality {
            items.append(ProfileChipItem(title: "Подача", value: "\(personality)", tint: TodayFlowTheme.moss))
        }
        if let year = personalYearChipValue() {
            items.append(ProfileChipItem(title: "Год", value: "\(year)", tint: TodayFlowTheme.roseClay))
        }
        if let archetype = coreProfile?.baseline.archetypeSeed, !archetype.isEmpty {
            items.append(ProfileChipItem(title: "Архетип", value: archetype, tint: TodayFlowTheme.sunset))
        }
        if let average = fusionIndex?.scores.average {
            items.append(ProfileChipItem(title: "Состояние", value: "\(average)", tint: TodayFlowTheme.twilight))
        }
        if let element = coreProfile?.astro.sunElement, !element.isEmpty {
            items.append(ProfileChipItem(title: "Элемент", value: element, tint: TodayFlowTheme.moss))
        }
        if let modality = coreProfile?.astro.sunModality, !modality.isEmpty {
            items.append(ProfileChipItem(title: "Модальность", value: modality, tint: TodayFlowTheme.roseClay))
        }
        return items
    }

    private func personalYearChipValue() -> Int? {
        guard let birth = coreProfile?.numerology.birthDate else { return nil }
        let refYear = Calendar.current.component(.year, from: Date())
        return Self.personalYear(from: birth, refYear: refYear)
    }

    private static func personalYear(from birthDate: String, refYear: Int) -> Int? {
        guard birthDate.count >= 10 else { return nil }
        let head = String(birthDate.prefix(10))
        let segs = head.split(separator: "-")
        guard segs.count == 3,
              let m = Int(segs[1]),
              let d = Int(segs[2]),
              m > 0, m <= 12, d > 0, d <= 31
        else { return nil }
        return digitalRoot1to9(m + d + refYear)
    }

    private static func digitalRoot1to9(_ n: Int) -> Int {
        var x = abs(n)
        while x > 9 {
            var t = 0
            var v = x
            while v > 0 {
                t += v % 10
                v /= 10
            }
            x = t
        }
        if x == 0 { return 1 }
        return x
    }
}

private struct ProfileLifeLevelSection: View {
    let contour: LifeLevelContour
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text("Уровень профиля")
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text("Контур показывает не активность ради активности, а качество того, как ты держишь фокус и ритм в жизни.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
            }

            ProfileAdaptiveStack(spacing: 14) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(contour.tier.title.uppercased())
                        .font(.caption.weight(.bold))
                        .foregroundStyle(levelTint)
                    Text("\(contour.score)")
                        .font(.system(size: 42, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(contour.statusLine)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(18)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))

                VStack(alignment: .leading, spacing: 10) {
                    Text("Следующий шаг")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(contour.guidanceLine)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    if let alertLine = contour.alertLine {
                        Text(alertLine)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(levelTint)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(18)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            }

            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text("Прогресс до следующего контура")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Spacer()
                    Text(contour.tier.next?.title ?? "Максимум")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)
                }

                TodayFlowSphereSliderTrack(
                    value: Int(round(contour.progressToNext * 100)),
                    tint: levelTint,
                    accessibilityTitle: "Прогресс до следующего контура",
                    density: .compact
                )
            }
            .padding(18)
            .background(Color.white.opacity(0.56))
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 10) {
                ProfileScoreChip(title: "Действие", value: contour.execution, tint: TodayFlowTheme.sunset)
                ProfileScoreChip(title: "Согласованность", value: contour.alignment, tint: TodayFlowTheme.twilight)
                ProfileScoreChip(title: "Стабильность", value: contour.consistency, tint: TodayFlowTheme.moss)
                ProfileScoreChip(title: "Дней в трекинге", value: contour.trackedDays, tint: levelTint)
            }

            HStack(spacing: 10) {
                ForEach(LifeLevelTier.allCases, id: \.self) { tier in
                    VStack(spacing: 8) {
                        Circle()
                            .fill(levelFill(for: tier))
                            .overlay {
                                Circle()
                                    .stroke(levelStroke(for: tier), lineWidth: contour.tier == tier ? 2 : 1)
                            }
                            .frame(width: 34, height: 34)
                        Text(tier.title)
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(contour.tier == tier ? TodayFlowTheme.ink : TodayFlowTheme.ink.opacity(0.56))
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .padding(18)
            .background(Color.white.opacity(0.56))
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.92), TodayFlowTheme.paper.opacity(0.84), levelTint.opacity(0.14)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var levelTint: Color {
        switch contour.tier {
        case .bronze: return TodayFlowTheme.ember
        case .silver: return TodayFlowTheme.twilight
        case .gold: return TodayFlowTheme.gold
        case .platinum: return TodayFlowTheme.moss
        }
    }

    private func levelFill(for tier: LifeLevelTier) -> Color {
        if contour.tier == tier {
            return levelStroke(for: tier).opacity(0.82)
        }
        if LifeLevelTier.allCases.firstIndex(of: tier) ?? 0 < LifeLevelTier.allCases.firstIndex(of: contour.tier) ?? 0 {
            return levelStroke(for: tier).opacity(0.42)
        }
        return Color.white.opacity(0.62)
    }

    private func levelStroke(for tier: LifeLevelTier) -> Color {
        switch tier {
        case .bronze: return TodayFlowTheme.ember
        case .silver: return TodayFlowTheme.twilight
        case .gold: return TodayFlowTheme.gold
        case .platinum: return TodayFlowTheme.moss
        }
    }
}

private struct ProfileChipItem: Identifiable {
    let id = UUID()
    let title: String
    let value: String
    let tint: Color
}

private struct ProfileSummaryChip: View {
    let title: String
    let value: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(tint)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct ProfileHeaderSignalCard: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(text.isEmpty ? "Собирается" : text)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.8))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 108, alignment: .topLeading)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct ProfileHeroChip: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title.uppercased())
                .font(.caption2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.7))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct RewardRingTier: Identifiable {
    let id: String
    let title: String
    let minIndex: Int
    let grants: [String]
}

private let profileRewardRingTiers: [RewardRingTier] = [
    RewardRingTier(id: "ember", title: "Искра", minIndex: 0, grants: ["Первый контур дня", "Базовый ритм"]),
    RewardRingTier(id: "spark", title: "Огонь", minIndex: 14, grants: ["Больше точности в Today", "Живые сигналы состояния"]),
    RewardRingTier(id: "current", title: "Поток", minIndex: 28, grants: ["Стабильный check-in", "Первые повторяющиеся паттерны"]),
    RewardRingTier(id: "mirror", title: "Зеркало", minIndex: 42, grants: ["Глубже profile fit", "Яснее риски и опоры"]),
    RewardRingTier(id: "weave", title: "Сплетение", minIndex: 56, grants: ["Связка карты и поведения", "Точнее life lenses"]),
    RewardRingTier(id: "oracle", title: "Оракул", minIndex: 72, grants: ["Сильнее персональные сценарии", "Быстрее ответы системы"]),
    RewardRingTier(id: "architect", title: "Архитектор", minIndex: 88, grants: ["Максимальная глубина reading", "Контур зрелого профиля"]),
]

private struct ProfileGrowthSection: View {
    let rewards: TodayRewardsSnapshot
    let milestones: [TodayRewardMilestone]
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text("Точность профиля")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .textCase(.uppercase)
                Text("Прогресс и кольца")
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text("Сначала смысл — насколько полно система может опираться на твои данные и живые сигналы. Ниже — кольца и индекс, как на сайте.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                Text(rewards.message)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
            }

            VStack(alignment: .leading, spacing: 12) {
                ProfileAdaptiveStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text((rewards.archetypeProgress?.current ?? rewards.archetypeLevel).uppercased())
                            .font(.caption.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        Text("\(rewards.evolutionIndex)")
                            .font(.system(size: 40, weight: .bold, design: .rounded))
                            .foregroundStyle(TodayFlowTheme.sunset)
                        Text("Прогресс")
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                    }

                    VStack(alignment: horizontalSizeClass == .compact ? .leading : .trailing, spacing: 6) {
                        if let peak = rewards.rewardEvolutionIndexPeak {
                            ProfileHeroChip(title: "Пик", value: "\(peak)")
                        }
                        ProfileHeroChip(title: "День", value: "\(rewards.streaks.dailyCurrent)")
                        ProfileHeroChip(title: "Неделя", value: "\(rewards.streaks.weeklyCurrent)")
                    }
                }

                ProfileGrowthMeter(progress: segmentProgress, nextTitle: nextRing?.title)

                LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 10) {
                    ProfileScoreChip(title: "Mind", value: rewards.scores.mind, tint: TodayFlowTheme.twilight)
                    ProfileScoreChip(title: "Energy", value: rewards.scores.energy, tint: TodayFlowTheme.sunset)
                    ProfileScoreChip(title: "Discipline", value: rewards.scores.discipline, tint: TodayFlowTheme.gold)
                    ProfileScoreChip(title: "Reflection", value: rewards.scores.reflection, tint: TodayFlowTheme.moss)
                }
            }
            .padding(18)
            .background(Color.white.opacity(0.56))
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))

            ProfileRewardRingsLadder(
                evolutionIndex: rewards.evolutionIndex,
                earnedRingIDs: rewards.rewardRingsEarned ?? []
            )

            ProfileRewardsContourCard(rewards: rewards, milestones: milestones)

            ProfileStreaksSection(rewards: rewards)
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.92), TodayFlowTheme.paper.opacity(0.84), TodayFlowTheme.gold.opacity(0.14)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var currentTier: RewardRingTier {
        profileRewardRingTiers.last(where: { rewards.evolutionIndex >= $0.minIndex || (rewards.rewardRingsEarned ?? []).contains($0.id) }) ?? profileRewardRingTiers[0]
    }

    private var nextRing: RewardRingTier? {
        profileRewardRingTiers.first(where: { rewards.evolutionIndex < $0.minIndex && !(rewards.rewardRingsEarned ?? []).contains($0.id) })
    }

    private var segmentProgress: Double {
        guard let nextRing else { return 1 }
        let previousThreshold = currentTier.minIndex
        let distance = max(1, nextRing.minIndex - previousThreshold)
        let progressed = max(0, rewards.evolutionIndex - previousThreshold)
        return min(1, Double(progressed) / Double(distance))
    }
}

private struct ProfileGrowthMeter: View {
    let progress: Double
    let nextTitle: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("До следующего шага")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Spacer()
                Text(nextTitle ?? "Максимум")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }

            TodayFlowSphereSliderTrack(
                value: Int(round(progress * 100)),
                tint: TodayFlowTheme.sunset,
                accessibilityTitle: nextTitle.map { "До следующего шага, цель \($0)" } ?? "До следующего шага",
                density: .compact
            )
        }
    }
}

private struct ProfileScoreChip: View {
    let title: String
    let value: Int
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(tint)
            Text("\(value)")
                .font(.subheadline.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink)
            if (0 ... 100).contains(value) {
                TodayFlowSphereSliderTrack(
                    value: value,
                    tint: tint,
                    accessibilityTitle: title,
                    density: .compact
                )
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.7))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct ProfileRewardRingsLadder: View {
    let evolutionIndex: Int
    let earnedRingIDs: [String]
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Этапы прогресса")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            if horizontalSizeClass == .compact {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(alignment: .top, spacing: 10) {
                        ForEach(profileRewardRingTiers) { tier in
                            ringCell(tier)
                                .frame(width: 76)
                        }
                    }
                }
            } else {
                HStack(alignment: .top, spacing: 10) {
                    ForEach(profileRewardRingTiers) { tier in
                        ringCell(tier)
                            .frame(maxWidth: .infinity, alignment: .top)
                    }
                }
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }

    private func isEarned(_ tier: RewardRingTier) -> Bool {
        earnedRingIDs.contains(tier.id) || evolutionIndex >= tier.minIndex
    }

    private func isNext(_ tier: RewardRingTier) -> Bool {
        !isEarned(tier) && tier.id == profileRewardRingTiers.first(where: { !isEarned($0) })?.id
    }

    private func circleFill(for tier: RewardRingTier) -> some ShapeStyle {
        if isEarned(tier) {
            return AnyShapeStyle(
                RadialGradient(
                    colors: [Color.white, TodayFlowTheme.gold.opacity(0.7), TodayFlowTheme.sunset.opacity(0.9)],
                    center: .topLeading,
                    startRadius: 2,
                    endRadius: 22
                )
            )
        }
        return AnyShapeStyle(Color.white.opacity(0.62))
    }

    private func circleStroke(for tier: RewardRingTier) -> Color {
        if isEarned(tier) {
            return TodayFlowTheme.gold.opacity(0.72)
        }
        return isNext(tier) ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.16)
    }

    private func ringCell(_ tier: RewardRingTier) -> some View {
        VStack(spacing: 8) {
            Circle()
                .fill(circleFill(for: tier))
                .overlay {
                    Circle()
                        .stroke(circleStroke(for: tier), lineWidth: isNext(tier) ? 2 : 1)
                }
                .frame(width: 34, height: 34)
            Text(tier.title)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(isEarned(tier) ? TodayFlowTheme.ink : TodayFlowTheme.ink.opacity(0.56))
                .multilineTextAlignment(.center)
                .lineLimit(2)
        }
    }
}

private struct ProfileRewardsContourCard: View {
    let rewards: TodayRewardsSnapshot
    let milestones: [TodayRewardMilestone]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Контур профиля")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text("Этот прогресс показывает, насколько точнее становятся подсказки для тебя.")
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.7))

            if !rewards.seals.isEmpty {
                FlowLayout(spacing: 8, items: rewards.seals) { seal in
                    Text("\(seal.title) · \(seal.strength)%")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.white.opacity(0.7))
                        .clipShape(Capsule())
                }
            }

            if !milestones.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Ближайшие вехи")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    ForEach(milestones.prefix(3)) { milestone in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(milestone.name)
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.ink)
                                Text(milestone.status == "done" ? "Уже достигнуто" : "Осталось \(milestone.daysLeft) дн.")
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                            }
                            Spacer()
                            Text("\(milestone.targetDays)")
                                .font(.caption.weight(.bold))
                                .foregroundStyle(TodayFlowTheme.sunset)
                        }
                        .padding(12)
                        .background(Color.white.opacity(0.62))
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    }
                }
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }
}

private struct ProfileStreaksSection: View {
    let rewards: TodayRewardsSnapshot

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Стрики и печати")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            FlowLayout(spacing: 8, items: streakItems) { item in
                Text("\(item.title): \(item.value)")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.white.opacity(0.7))
                    .clipShape(Capsule())
            }

            if !rewards.seals.isEmpty {
                FlowLayout(spacing: 8, items: rewards.seals) { seal in
                    Text("\(seal.title) · \(seal.strength)%")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(TodayFlowTheme.paper.opacity(0.92))
                        .clipShape(Capsule())
                }
            }
        }
        .padding(18)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
    }

    private var streakItems: [ProfileMetricBadge] {
        [
            ProfileMetricBadge(title: "День", value: rewards.streaks.dailyCurrent),
            ProfileMetricBadge(title: "Неделя", value: rewards.streaks.weeklyCurrent),
            ProfileMetricBadge(title: "Привычка", value: rewards.streaks.habitBest),
            ProfileMetricBadge(title: "Аскеза", value: rewards.streaks.asceticBest),
            ProfileMetricBadge(title: "Таро", value: rewards.streaks.tarotCurrent)
        ]
    }
}

private struct ProfileMetricBadge: Identifiable {
    let id = UUID()
    let title: String
    let value: Int
}

private func profileSunElementLabelRU(_ raw: String?) -> String {
    guard let s = raw?.trimmingCharacters(in: .whitespacesAndNewlines), !s.isEmpty else { return "Собирается" }
    switch s.lowercased() {
    case "air": return "воздух"
    case "fire": return "огонь"
    case "earth": return "земля"
    case "water": return "вода"
    default: return s
    }
}

private struct ProfileOverviewSection: View {
    let coreProfile: CoreProfileResponse
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Портрет")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Text(coreProfile.interpretation?.identity ?? fallbackIdentity)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                OverviewAccentCard(title: "Солнце", text: coreProfile.astro.sunSign ?? "Определяется", tint: TodayFlowTheme.sunset)
                OverviewAccentCard(title: "Путь", text: coreProfile.numerology.lifePath.map(String.init) ?? "Собирается", tint: TodayFlowTheme.gold)
                OverviewAccentCard(title: "Ритм", text: coreProfile.baseline.rhythmStyle ?? "Проявится через ответы", tint: TodayFlowTheme.moss)
            }

            if hasAstroDetailRow {
                LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                    OverviewAccentCard(title: "Стихия Солнца", text: profileSunElementLabelRU(coreProfile.astro.sunElement), tint: TodayFlowTheme.ember)
                    OverviewAccentCard(title: "Модальность", text: coreProfile.astro.sunModality ?? "Собирается", tint: TodayFlowTheme.twilight)
                }
            }

            if !(coreProfile.interpretation?.strengths ?? []).isEmpty || !(coreProfile.interpretation?.watchouts ?? []).isEmpty {
                ProfileAdaptiveStack(spacing: 12) {
                    ProfileBulletCard(
                        title: "Сильные стороны",
                        items: coreProfile.interpretation?.strengths ?? []
                    )
                    ProfileBulletCard(
                        title: "Зоны внимания",
                        items: coreProfile.interpretation?.watchouts ?? []
                    )
                }
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var fallbackIdentity: String {
        let sunSign = coreProfile.astro.sunSign ?? "твой знак"
        let archetype = coreProfile.baseline.archetypeSeed ?? "текущий архетип"
        return "Через \(sunSign.lowercased()) и \(archetype.lowercased()) уже виден твой базовый способ входить в день, держать ритм и собирать себя в решениях."
    }

    private var hasAstroDetailRow: Bool {
        coreProfile.astro.sunElement != nil
            || coreProfile.astro.sunModality != nil
    }
}

private struct OverviewAccentCard: View {
    let title: String
    let text: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(tint)
            Text(text)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .lineLimit(3)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct ProfileBulletCard: View {
    let title: String
    let items: [String]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(items.prefix(3), id: \.self) { item in
                Text("• \(item)")
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct ProfilePulseSection: View {
    let living: CoreProfileLiving
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Живой слой")
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.sand)
                .textCase(.uppercase)

            Text(living.summary ?? "Здесь собирается то, что система видит по твоим ответам, вечерней фиксации и действиям — не общие фразы, а сигналы с опорой на поведение.")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                OverviewAccentCard(
                    title: "Сигналы дня",
                    text: "\(living.signalProfile?.signalsDays ?? 0) дней с живым откликом за последние две недели.",
                    tint: TodayFlowTheme.sunset
                )
                OverviewAccentCard(title: "Собранность", text: closureLabel(living.signalProfile?.closureState), tint: TodayFlowTheme.gold)
                OverviewAccentCard(title: "Ясность решений", text: clarityLabel(living.signalProfile?.clarityState), tint: TodayFlowTheme.twilight)
                OverviewAccentCard(
                    title: "Что сейчас чаще всплывает",
                    text: living.signalProfile?.dominantFocus ?? "Эта тема проявится, когда накопится больше ответов дня.",
                    tint: TodayFlowTheme.moss
                )
            }

            if let weekly = living.weeklyState?.integrationText, !weekly.isEmpty || !(living.recentInsights ?? []).isEmpty {
                ProfileAdaptiveStack(spacing: 12) {
                    if let weekly = living.weeklyState?.integrationText, !weekly.isEmpty {
                        OverviewAccentCard(title: "Неделя", text: weekly, tint: TodayFlowTheme.roseClay)
                    }
                    if let insight = living.recentInsights?.first?.text, !insight.isEmpty {
                        OverviewAccentCard(title: "Последний сигнал", text: insight, tint: TodayFlowTheme.sunset)
                    }
                }
            }

            if let context = living.learningContext {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Как тебе лучше давать подсказки")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(context.summary ?? "Этот слой станет точнее после следующих ответов и закрытий дня.")
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.7))

                    ProfileAdaptiveStack(spacing: 12) {
                        OverviewAccentCard(title: "Стиль ответа", text: context.responseStyle ?? "Сейчас определяется", tint: TodayFlowTheme.gold)
                        OverviewAccentCard(title: "Стиль поддержки", text: context.supportStyle ?? "Станет яснее по истории", tint: TodayFlowTheme.roseClay)
                    }

                    if !(context.dominantLanes ?? []).isEmpty || !(context.dominantDiaryTopics ?? []).isEmpty {
                        ProfileAdaptiveStack(spacing: 12) {
                            OverviewAccentCard(
                                title: "Повторяющиеся линии",
                                text: !(context.dominantLanes ?? []).isEmpty ? (context.dominantLanes ?? []).joined(separator: ", ") : "Пока не проявились",
                                tint: TodayFlowTheme.moss
                            )
                            OverviewAccentCard(
                                title: "Темы дневника",
                                text: !(context.dominantDiaryTopics ?? []).isEmpty ? (context.dominantDiaryTopics ?? []).joined(separator: ", ") : "Пока не проявились",
                                tint: TodayFlowTheme.twilight
                            )
                        }
                    }
                }
                .padding(16)
                .background(Color.white.opacity(0.56))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }

            if let insights = living.recentInsights, !insights.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Последние сигналы")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    ForEach(insights.prefix(3)) { insight in
                        Text("• \(insight.text)")
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    }
                }
                .padding(16)
                .background(Color.white.opacity(0.56))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private func closureLabel(_ state: String?) -> String {
        switch state {
        case "stable":
            return "день чаще собирается"
        case "fragile":
            return "дню часто не хватает завершения"
        case "building":
            return "собранность только выстраивается"
        case "mixed":
            return "собранность пока неровная"
        default:
            return "мало данных за последние дни — слой уточнится после ответов в Today"
        }
    }

    private func clarityLabel(_ state: String?) -> String {
        switch state {
        case "growing":
            return "решения становятся яснее"
        case "unclear":
            return "неясность решений повторяется"
        case "mixed":
            return "ясность и зависание чередуются"
        default:
            return "нужно больше закрытий дня, чтобы увидеть ясность решений"
        }
    }
}

private struct ProfileSynthesisSection: View {
    let coreProfile: CoreProfileResponse
    let natalChart: NatalChartPreview?
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Планеты и синтез")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Text("Одна связная линия: не перечень планет, а то, как качества складываются в поведение и выбор.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))

            Text(weaveIntro)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                ForEach(placements, id: \.title) { item in
                    WeavePillCard(title: item.title, value: item.value)
                }
            }

            if !signatureLines.isEmpty {
                FlowLayout(spacing: 8, items: signatureLines) { line in
                    Text(line.value)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(Color.white.opacity(0.68))
                        .clipShape(Capsule())
                }
            }

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                WeaveCard(title: "Узнавание", text: coreProfile.interpretation?.identity ?? weaveIntro)
                WeaveCard(title: "Синтез", text: coreProfile.natalSummary?.overview ?? manifestationText)
                WeaveCard(title: "Где внутренний конфликт", text: tensionLine)
                WeaveCard(title: "Где сила", text: strengthLine)
                WeaveCard(title: "Как это проявляется в жизни", text: manifestationText)
                WeaveCard(title: "Через что ты это живёшь", text: lifeVectorLine)
                WeaveCard(title: "Как это видно снаружи", text: expressionLine)
                WeaveCard(title: "Где рост", text: growthLine)
                WeaveCard(title: "Что ограничивает", text: constraintLine)
                WeaveCard(title: "Где риск", text: riskLine)
            }

            if !aspectLines.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Аспекты")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    ForEach(aspectLines, id: \.self) { line in
                        Text("• \(line)")
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(16)
                .background(Color.white.opacity(0.56))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var placements: [(title: String, value: String)] {
        [
            ("Sun", natalChart?.positions["sun"]?.sign ?? coreProfile.astro.sunSign ?? "Собирается"),
            ("Moon", natalChart?.positions["moon"]?.sign ?? "Собирается"),
            ("Venus", natalChart?.positions["venus"]?.sign ?? "Собирается"),
            ("Mars", natalChart?.positions["mars"]?.sign ?? "Собирается"),
        ]
    }

    private var weaveIntro: String {
        let sun = natalChart?.positions["sun"]?.sign ?? coreProfile.astro.sunSign ?? "твоё солнце"
        let moon = natalChart?.positions["moon"]?.sign ?? "твоя луна"
        let rhythm = coreProfile.baseline.rhythmStyle ?? "твой ритм"
        return "Profile должен объяснять не отдельные значения, а сочетание \(sun), \(moon) и того, как ты проживаешь \(rhythm.lowercased())."
    }

    private var manifestationText: String {
        let natalLine = coreProfile.natalSummary?.overview ?? coreProfile.natalSummary?.chartTone
        return natalLine ?? "Главная сила раскрывается не отдельно в карте или привычках, а в том, как твоя база переносится в обычные решения дня."
    }

    private var tensionLine: String {
        let watchouts = coreProfile.interpretation?.watchouts ?? []
        if !watchouts.isEmpty {
            return watchouts.prefix(2).joined(separator: " ")
        }
        return "Напряжение обычно появляется там, где твой внутренний ритм расходится с внешним темпом и ты начинаешь действовать не из своей оси."
    }

    private var strengthLine: String {
        let strengths = coreProfile.interpretation?.strengths ?? []
        if !strengths.isEmpty {
            return strengths.prefix(2).joined(separator: " ")
        }
        return "Сила проявляется там, где личная карта, ритм и реальные ответы начинают совпадать, а не спорить между собой."
    }

    private var growthLine: String {
        if let first = coreProfile.interpretation?.strengths?.first {
            return first
        }
        if let pattern = coreProfile.natalSummary?.patterns?.first {
            return pattern
        }
        return "Рост идет там, где ты действуешь в своём темпе, а не только отвечаешь на внешнее давление."
    }

    private var riskLine: String {
        coreProfile.interpretation?.watchouts?.first ?? "Риск появляется, когда ритм дня расходится с твоей внутренней конфигурацией и энергия начинает утекать в фон."
    }

    private var lifeVectorLine: String {
        let parts = [
            coreProfile.baseline.rhythmStyle,
            coreProfile.baseline.elementFocus,
            coreProfile.natalSummary?.chartTone
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
        if !parts.isEmpty {
            return parts.joined(separator: " · ")
        }
        return "Главный вектор жизни проявится яснее, когда карта и накопленные сигналы перестанут противоречить друг другу."
    }

    private var expressionLine: String {
        let parts = [
            coreProfile.living?.learningContext?.responseStyle,
            coreProfile.living?.learningContext?.supportStyle
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
        if !parts.isEmpty {
            return parts.joined(separator: " · ")
        }
        return "Внешне это читается по тому, как ты отвечаешь дню, держишь внимание и запрашиваешь поддержку."
    }

    private var constraintLine: String {
        if let closure = coreProfile.living?.signalProfile?.closureState, !closure.isEmpty {
            return "Сейчас главный ограничитель — слой закрытия дня: \(closure)."
        }
        if let clarity = coreProfile.living?.signalProfile?.clarityState, !clarity.isEmpty {
            return "Ограничение часто связано с ясностью сигналов: \(clarity)."
        }
        return "Ограничения становятся заметны там, где ответы редкие, а день проживается без фиксации и закрытия."
    }

    private var signatureLines: [ProfileSignatureToken] {
        let values = (coreProfile.natalSummary?.signature ?? []) + (coreProfile.natalSummary?.patterns ?? [])
        return Array(values.prefix(6)).map { ProfileSignatureToken(value: $0) }
    }

    private var aspectLines: [String] {
        natalChart?.aspects?.callouts?
            .prefix(4)
            .map {
                [$0.label, $0.integration, $0.description]
                    .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
                    .filter { !$0.isEmpty }
                    .joined(separator: " — ")
            } ?? []
    }
}

private struct WeaveCard: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(text)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .lineLimit(6)
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 140, alignment: .topLeading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct WeavePillCard: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .lineLimit(2)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct ProfileSignatureToken: Identifiable {
    let id = UUID()
    let value: String
}

/// Паритет с веб-вкладкой «Паттерны»: короткий синтез до полной нативной разметки сфер/блоков.
private struct ProfilePatternsStubSection: View {
    let coreProfile: CoreProfileResponse

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Паттерны")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text("Не натальная карта, а как качества складываются в решения, стресс и контакт. Полная версия — на сайте; здесь — короткий срез из ядра профиля.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

            if let identity = coreProfile.interpretation?.identity, !identity.isEmpty {
                Text(identity)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            if let s = coreProfile.interpretation?.strengths?.first, !s.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("На что опираться")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(s)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                }
            }

            if let w = coreProfile.interpretation?.watchouts?.first, !w.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Где чаще теряешь себя")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(w)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                }
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }
}

private struct ProfileLifeSections: View {
    let coreProfile: CoreProfileResponse
    let natalChart: NatalChartPreview?
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 6) {
                Text("Сферы жизни")
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text("Постоянные темы: отношения, деньги, работа, дом, дети, тело, друзья, решения и отдельно — сексуальность как важная ось (как карьера или совместимость). При наличии карты текст сферы может собираться из нескольких домов и планет. Линзы дня — в Today, не в профиле.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            }

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                LifeAreaCard(
                    title: "Любовь и отношения",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.love,
                        fallback: "Здесь видно, как ты входишь в близость, где тебе нужна ясность, а где связь начинает забирать слишком много сил.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 7),
                            planetSummary(chart: natalChart, body: "venus"),
                            planetSummary(chart: natalChart, body: "moon"),
                        ]
                    ),
                    tint: TodayFlowTheme.roseClay
                )
                LifeAreaCard(
                    title: "Карьера и реализация",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.career,
                        fallback: "Этот слой показывает, в какой роли ты становишься заметной, на что реально можно опереться в работе и где не стоит жить только в режиме обслуживания чужих задач.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 10),
                            planetSummary(chart: natalChart, body: "sun"),
                            planetSummary(chart: natalChart, body: "saturn"),
                        ]
                    ),
                    tint: TodayFlowTheme.twilight
                )
                LifeAreaCard(
                    title: "Деньги и ресурсы",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.money,
                        fallback: "Через этот слой читается не только тема денег, но и чувство ценности себя, устойчивости и того, на чем тебе действительно безопасно строить рост.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 2),
                            chartHouseSummary(chart: natalChart, house: 8),
                            planetSummary(chart: natalChart, body: "jupiter"),
                            planetSummary(chart: natalChart, body: "saturn"),
                        ]
                    ),
                    tint: TodayFlowTheme.gold
                )
                LifeAreaCard(
                    title: "Семья и дом",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.family,
                        fallback: "Здесь видно, что для тебя значит дом, откуда идет внутреннее восстановление и какие форматы близости дают опору, а не перегруз.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 4),
                            planetSummary(chart: natalChart, body: "moon"),
                        ]
                    ),
                    tint: TodayFlowTheme.moss
                )
            }

            VStack(alignment: .leading, spacing: 10) {
                Text("Секс и сексуальность")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text("Про желание, границы и темп — открыто и практично.")
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))

                VStack(alignment: .leading, spacing: 8) {
                    Text("Срез по карте (8 дом, Плутон, Венера, Марс)")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(Color(red: 0.71, green: 0.33, blue: 0.04))
                        .textCase(.uppercase)
                    Text(intimacySphereText)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.56))
                .overlay(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(Color(red: 0.71, green: 0.33, blue: 0.04).opacity(0.18), lineWidth: 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                LifeAreaCard(
                    title: "Дети и родительство",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.kids,
                        fallback: "Если тема актуальна, она проявится в сфере дома и ответственности; иначе блок остаётся нейтральным якорем.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 5),
                            planetSummary(chart: natalChart, body: "moon"),
                        ]
                    ),
                    tint: TodayFlowTheme.sky
                )
                LifeAreaCard(
                    title: "Тело и энергия",
                    text: bodySphereText,
                    tint: TodayFlowTheme.moss
                )
                LifeAreaCard(
                    title: "Дружба и окружение",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.friends,
                        fallback: "Когда Меркурий в карте читается устойчиво, здесь появится срез дружбы и сети поддержки.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 11),
                            planetSummary(chart: natalChart, body: "mercury"),
                        ]
                    ),
                    tint: Color(red: 0.66, green: 0.33, blue: 0.97)
                )
                LifeAreaCard(
                    title: "Решения и дисциплина",
                    text: composedLifeAreaText(
                        api: coreProfile.interpretation?.lifeAreas?.decisions,
                        fallback: "Сатурн в карте покажет, где ты взрослеешь через структуру и честные ограничения.",
                        pieces: [
                            chartHouseSummary(chart: natalChart, house: 9),
                            planetSummary(chart: natalChart, body: "saturn"),
                            planetSummary(chart: natalChart, body: "mercury"),
                        ]
                    ),
                    tint: Color(red: 0.39, green: 0.45, blue: 0.55)
                )
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    /// Паритет с `profileLifeSpheres.ts`: срез карты, иначе `life_areas.body`, иначе префикс + Луна, иначе дефолт.
    private var bodySphereText: String {
        let pieces: [String?] = [
            chartHouseSummary(chart: natalChart, house: 6),
            planetSummary(chart: natalChart, body: "mars"),
            planetSummary(chart: natalChart, body: "moon"),
            planetSummary(chart: natalChart, body: "saturn"),
        ]
        let flat = pieces.compactMap { $0 }.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        if !flat.isEmpty {
            let joined = flat.joined(separator: " ")
            return joined.count > 520 ? String(joined.prefix(519)) + "…" : joined
        }
        if let api = coreProfile.interpretation?.lifeAreas?.body?.trimmingCharacters(in: .whitespacesAndNewlines), !api.isEmpty {
            return api
        }
        if let moon = planetSummary(chart: natalChart, body: "moon"), !moon.isEmpty {
            return "Эмоциональный фон и восстановление сильнее всего читаются через Луну: \(moon)"
        }
        return "Когда Луна в карте стабильна, здесь появится конкретика про сон, накопление и срывы."
    }

    private var intimacySphereText: String {
        composedLifeAreaText(
            api: coreProfile.interpretation?.lifeAreas?.sex,
            fallback: "Когда в карте появятся срезы по 8 дому и планетам, здесь будет короткий разбор желания, границ и темпа — опора для Guidance и Compatibility.",
            pieces: [
                chartHouseSummary(chart: natalChart, house: 8),
                planetSummary(chart: natalChart, body: "pluto"),
                planetSummary(chart: natalChart, body: "venus"),
                planetSummary(chart: natalChart, body: "mars"),
            ]
        )
    }

    private func chartHouseSummary(chart: NatalChartPreview?, house: Int) -> String? {
        guard let houses = chart?.interpretations?.houses else { return nil }
        let key = String(house)
        guard let h = houses[key] else { return nil }
        let theme = (h.theme ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        let desc = (h.description ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        if !theme.isEmpty, !desc.isEmpty {
            let full = "\(theme): \(desc)"
            return full.count > 320 ? String(full.prefix(319)) + "…" : full
        }
        if !desc.isEmpty { return desc }
        if !theme.isEmpty { return theme }
        return nil
    }

    private func composedLifeAreaText(api: String?, fallback: String, pieces: [String?]) -> String {
        let flat = pieces.compactMap { $0 }.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        if !flat.isEmpty {
            let joined = flat.joined(separator: " ")
            if joined.count > 520 { return String(joined.prefix(519)) + "…" }
            return joined
        }
        if let api = api?.trimmingCharacters(in: .whitespacesAndNewlines), !api.isEmpty { return api }
        return fallback
    }

    private func planetSummary(chart: NatalChartPreview?, body: String) -> String? {
        guard let chart else { return nil }
        let lower = body.lowercased()
        let position = chart.positions[lower]
            ?? chart.positions.first { $0.key.lowercased() == lower }?.value
        let signLine = ZodiacSignRU.planetLine(chart, body: body)
        guard signLine != nil || position != nil else { return nil }
        var parts: [String] = []
        if let signLine, !signLine.isEmpty {
            parts.append(signLine)
        }
        if let house = position?.house {
            parts.append("дом \(house)")
        }
        let joined = parts.joined(separator: " · ")
        return joined.isEmpty ? nil : joined
    }
}

private struct LifeAreaCard: View {
    let title: String
    let text: String
    let tint: Color

    var body: some View {
        DisclosureGroup {
            Text(text)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.top, 4)
        } label: {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(tint)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 88, alignment: .topLeading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct FlowLayout<Data: RandomAccessCollection, Content: View>: View where Data.Element: Identifiable {
    let spacing: CGFloat
    let items: Data
    let content: (Data.Element) -> Content

    init(spacing: CGFloat, items: Data, @ViewBuilder content: @escaping (Data.Element) -> Content) {
        self.spacing = spacing
        self.items = items
        self.content = content
    }

    var body: some View {
        VStack(alignment: .leading, spacing: spacing) {
            let rows = stride(from: 0, to: items.count, by: 3).map { index in
                Array(items.dropFirst(index).prefix(3))
            }
            ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                HStack(spacing: spacing) {
                    ForEach(row) { item in
                        content(item)
                    }
                }
            }
        }
    }
}

private struct ProfileStateMapSection: View {
    let fusionIndex: FusionIndex
    let history: [FusionIndex]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Карта состояния")
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(fusionIndex.encouragement)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 4) {
                    Text(TodayRitualCopy.rhythmTierLabel(score: fusionIndex.scores.average))
                        .font(.title3.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                        .multilineTextAlignment(.trailing)
                    Text(TodayRitualCopy.heroScoreFootnote(score: fusionIndex.scores.average))
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                }
            }

            ProfileStateRail(title: "Энергия", value: fusionIndex.scores.energy, tint: TodayFlowTheme.sunset)
            ProfileStateRail(title: "Баланс", value: fusionIndex.scores.emotionalBalance, tint: TodayFlowTheme.moss)
            ProfileStateRail(title: "Фокус", value: fusionIndex.scores.focus, tint: TodayFlowTheme.twilight)

            if !history.isEmpty {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Что уже видно по твоим дням")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(history.repeatedRiskPattern)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    Text(history.correlationInsight)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.56))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }
}

private struct ProfileStateRail: View {
    let title: String
    let value: Int
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .top) {
                Text(title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                VStack(alignment: .trailing, spacing: 2) {
                    Text(TodayRitualCopy.rhythmTierLabel(score: value))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(tint)
                        .multilineTextAlignment(.trailing)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(TodayRitualCopy.heroScoreFootnote(score: value))
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                }
            }

            TodayFlowSphereSliderTrack(
                value: min(100, max(0, value)),
                tint: tint,
                accessibilityTitle: title,
                density: .compact
            )
        }
        .padding(14)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct ProfileTodayMirrorSection: View {
    let cycle: TodayCycle
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Сегодня через твою карту")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                ProfileMirrorCard(
                    title: "Таро",
                    value: cycle.morning?.tarotCard?.name ?? "Собирается",
                    caption: "Образ дня"
                )
                ProfileMirrorCard(
                    title: "Число дня",
                    value: numerologyValue,
                    caption: "Числовая ось"
                )
                ProfileMirrorCard(
                    title: "Ось дня",
                    value: cycle.morning?.dailyHoroscope?.spine?.dayAxis ?? "Формируется",
                    caption: "Главная ось"
                )
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private var numerologyValue: String {
        if let title = cycle.morning?.numerologyNumber?.title, !title.isEmpty {
            return title
        }
        if let reduced = cycle.morning?.numerologyNumber?.reducedValue {
            return "Число \(reduced)"
        }
        if let value = cycle.morning?.numerologyNumber?.value {
            return "Число \(value)"
        }
        return "Собирается"
    }
}

private struct ProfileMirrorCard: View {
    let title: String
    let value: String
    let caption: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .lineLimit(3)
            Spacer()
            Text(caption)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 134, alignment: .topLeading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct ProfileRhythmCalendarSection: View {
    let history: [FusionIndex]
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Календарь ритма")
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text("Это не просто лог дат. Календарный слой должен показывать, как меняется качество твоего дня в динамике.")
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
                Text(history.overallTrendHeadline)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .multilineTextAlignment(.trailing)
            }

            if horizontalSizeClass == .compact {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(Array(history.orderedFusionHistory.suffix(7)), id: \.date) { item in
                            rhythmCell(item)
                                .frame(width: 62)
                        }
                    }
                }
            } else {
                HStack(spacing: 10) {
                    ForEach(Array(history.orderedFusionHistory.suffix(7)), id: \.date) { item in
                        rhythmCell(item)
                            .frame(maxWidth: .infinity)
                    }
                }
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private func weekdayLabel(for date: String) -> String {
        guard let parsed = Self.apiFormatter.date(from: date) else { return "DAY" }
        return Self.weekdayFormatter.string(from: parsed).uppercased()
    }

    private func shortDay(for date: String) -> String {
        guard let parsed = Self.apiFormatter.date(from: date) else { return "--" }
        return Self.dayFormatter.string(from: parsed)
    }

    private func rhythmCell(_ item: FusionIndex) -> some View {
        VStack(spacing: 8) {
            Text(weekdayLabel(for: item.date))
                .font(.caption2.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.52))

            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.54))
                    .frame(height: 96)

                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [TodayFlowTheme.sunset.opacity(0.35), TodayFlowTheme.twilight.opacity(0.72)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .frame(height: max(26, CGFloat(item.scores.average) * 0.9))
            }

            Text(shortDay(for: item.date))
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
    }

    private static let apiFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()

    private static let weekdayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("EE")
        return formatter
    }()

    private static let dayFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("d")
        return formatter
    }()
}

private struct ProfileInfoRow: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.84))
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct ProfileSignatureCard: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 108, alignment: .topLeading)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct ProfileCircleCard: View {
    let profile: StoredAstroProfile
    let onMakePrimary: () async -> Void
    let onDelete: () async -> Void
    let onRefine: () -> Void

    @State private var isSubmitting = false

    private var birthFactsCooldownSeconds: Int {
        profile.birthFactsCooldownRemainingSeconds ?? 0
    }

    private var birthFactsQuotaLocked: Bool {
        let remaining = profile.birthFactsCorrectionsRemaining ?? 3
        return remaining <= 0
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(profile.label)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(detail)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
                }
                Spacer()
                if profile.isPrimary == true {
                    Text("Основной")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(TodayFlowTheme.sunset.opacity(0.12))
                        .clipShape(Capsule())
                }
            }

            HStack(spacing: 10) {
                Button("Уточнить данные") {
                    onRefine()
                }
                .buttonStyle(.bordered)
                .tint(TodayFlowTheme.twilight)

                if profile.isPrimary != true {
                    Button("Сделать основным") {
                        isSubmitting = true
                        Task {
                            await onMakePrimary()
                            await MainActor.run { isSubmitting = false }
                        }
                    }
                    .buttonStyle(.bordered)
                    .disabled(isSubmitting)
                }

                Button("Удалить", role: .destructive) {
                    isSubmitting = true
                    Task {
                        await onDelete()
                        await MainActor.run { isSubmitting = false }
                    }
                }
                .buttonStyle(.bordered)
                .disabled(isSubmitting)
            }

            if birthFactsCooldownSeconds > 0 {
                let minutes = max(1, (birthFactsCooldownSeconds + 59) / 60)
                Text(
                    "Дата, время и место недавно менялись — повтори попытку примерно через \(minutes) мин. Название и роль можно править."
                )
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
            } else if let rem = profile.birthFactsCorrectionsRemaining, let max = profile.birthFactsCorrectionsMax {
                Text(
                    birthFactsQuotaLocked
                        ? "Дату, время и место рождения для этого профиля больше нельзя менять (лимит уточнений). Можно обновить название и роль."
                        : "Осталось уточнений данных рождения: \(rem) из \(max)."
                )
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var detail: String {
        let parts = [profile.relation, profile.locationName, profile.birthDate]
            .compactMap { $0 }
            .filter { !$0.isEmpty }
        return parts.joined(separator: " · ")
    }
}

struct AddProfileView: View {
    let store: TodayFlowStore
    let onSaved: () async -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var label = ""
    @State private var relation = "close_person"
    @State private var birthDate = Date.now
    @State private var knowsBirthTime = false
    @State private var birthTime = Date.now
    @State private var locationName = ""
    @State private var suggestions: [GeocodeSuggestion] = []
    @State private var isSearching = false
    @State private var selectedCoordinates: BirthCoordinates?
    @State private var isSaving = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text("Добавить человека")
                        .font(.title2.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    TextField("Имя или label", text: $label)
                        .todayFlowSystemTextInput(words: true)
                        .textFieldStyle(.roundedBorder)

                    Picker("Связь", selection: $relation) {
                        Text("Партнер").tag("partner")
                        Text("Ребенок").tag("child")
                        Text("Близкий человек").tag("close_person")
                    }
                    .pickerStyle(.segmented)

                    DatePicker("Дата рождения", selection: $birthDate, displayedComponents: .date)
                        .datePickerStyle(.compact)

                    Toggle("Я знаю время рождения", isOn: $knowsBirthTime)

                    if knowsBirthTime {
                        DatePicker("Время рождения", selection: $birthTime, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        TextField("Место рождения", text: $locationName)
                            .todayFlowSystemTextInput(words: true)
                            .textFieldStyle(.roundedBorder)

                        if isSearching {
                            ProgressView("Ищу локации...")
                                .controlSize(.small)
                        }

                        if !suggestions.isEmpty {
                            VStack(spacing: 8) {
                                ForEach(suggestions) { suggestion in
                                    Button {
                                        locationName = suggestion.name
                                        selectedCoordinates = BirthCoordinates(
                                            latitude: suggestion.latitude,
                                            longitude: suggestion.longitude
                                        )
                                        suggestions = []
                                    } label: {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(suggestion.primaryLabel)
                                                .frame(maxWidth: .infinity, alignment: .leading)
                                            Text("\(suggestion.latitude.formatted(.number.precision(.fractionLength(2)))), \(suggestion.longitude.formatted(.number.precision(.fractionLength(2))))")
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                                .frame(maxWidth: .infinity, alignment: .leading)
                                        }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(14)
                            .background(Color.white.opacity(0.6))
                            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                        }
                    }

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.roseClay)
                    }

                    Button {
                        save()
                    } label: {
                        Text(isSaving ? "Сохраняю..." : "Сохранить профиль")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.sunset)
                    .disabled(isSaving || !isValid)
                }
                .padding(20)
            }
            .navigationTitle("Новый профиль")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") {
                        dismiss()
                    }
                }
            }
            .task(id: locationName) {
                await refreshSuggestions()
            }
        }
    }

    private var isValid: Bool {
        !label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !locationName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private func refreshSuggestions() async {
        let trimmed = locationName.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count < 2 {
            suggestions = []
            isSearching = false
            return
        }

        isSearching = true
        do {
            let fetched = try await TodayFlowAPIClient.shared.fetchLocationSuggestions(query: trimmed)
            if locationName.trimmingCharacters(in: .whitespacesAndNewlines) == trimmed {
                suggestions = fetched
            }
        } catch {
            suggestions = []
        }
        isSearching = false
    }

    private func save() {
        guard isValid else { return }
        isSaving = true
        errorMessage = nil

        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "HH:mm:ss"

        let input = AstroProfileInput(
            label: label.trimmingCharacters(in: .whitespacesAndNewlines),
            relation: relation,
            birthDate: birthDate.apiDateString,
            birthTime: knowsBirthTime ? formatter.string(from: birthTime) : nil,
            timeUnknown: !knowsBirthTime,
            locationName: locationName.trimmingCharacters(in: .whitespacesAndNewlines),
            latitude: selectedCoordinates?.latitude,
            longitude: selectedCoordinates?.longitude,
            isPrimary: false
        )

        Task {
            do {
                _ = try await store.createAstroProfile(input)
                await onSaved()
                await MainActor.run {
                    isSaving = false
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isSaving = false
                }
            }
        }
    }
}

private struct EditAstroProfileView: View {
    let store: TodayFlowStore
    let profile: StoredAstroProfile
    let onSaved: () async -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var label: String
    @State private var relation: String
    @State private var birthDate: Date
    @State private var knowsBirthTime: Bool
    @State private var birthTime: Date
    @State private var locationName: String
    @State private var suggestions: [GeocodeSuggestion] = []
    @State private var isSearching = false
    @State private var selectedCoordinates: BirthCoordinates?
    @State private var isSaving = false
    @State private var errorMessage: String?

    private let birthFactsFieldsLocked: Bool

    init(store: TodayFlowStore, profile: StoredAstroProfile, onSaved: @escaping () async -> Void) {
        self.store = store
        self.profile = profile
        self.onSaved = onSaved
        let bd = Date(apiBirthDateString: profile.birthDate) ?? .now
        _label = State(initialValue: profile.label)
        let initialRelation = profile.isPrimary == true ? "self" : (profile.relation ?? "close_person")
        _relation = State(initialValue: initialRelation)
        _birthDate = State(initialValue: bd)
        let timeUnknown = profile.timeUnknown ?? true
        _knowsBirthTime = State(initialValue: !timeUnknown)
        _birthTime = State(initialValue: Self.mergeTime(fromApi: profile.birthTime, onto: bd))
        _locationName = State(initialValue: profile.locationName ?? "")
        if let lat = profile.latitude, let lon = profile.longitude {
            _selectedCoordinates = State(initialValue: BirthCoordinates(latitude: lat, longitude: lon))
        } else {
            _selectedCoordinates = State(initialValue: nil)
        }
        let remaining = profile.birthFactsCorrectionsRemaining ?? 3
        let cooldown = profile.birthFactsCooldownRemainingSeconds ?? 0
        self.birthFactsFieldsLocked = remaining <= 0 || cooldown > 0
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text("Уточнить профиль")
                        .font(.title2.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    Text(birthFactsFieldsLocked
                        ? "Дату, время и место сейчас нельзя менять (лимит уточнений или пауза после последнего сохранения). Название и роль можно обновить."
                        : "Данные рождения можно уточнить только несколько раз — проверь всё перед сохранением.")
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

                    TextField("Имя или label", text: $label)
                        .todayFlowSystemTextInput(words: true)
                        .textFieldStyle(.roundedBorder)

                    if profile.isPrimary == true {
                        Text("Роль: основной личный профиль")
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    } else {
                        Picker("Связь", selection: $relation) {
                            Text("Партнер").tag("partner")
                            Text("Ребенок").tag("child")
                            Text("Близкий человек").tag("close_person")
                        }
                        .pickerStyle(.segmented)
                    }

                    DatePicker("Дата рождения", selection: $birthDate, displayedComponents: .date)
                        .datePickerStyle(.compact)
                        .disabled(birthFactsFieldsLocked)

                    Toggle("Я знаю время рождения", isOn: $knowsBirthTime)
                        .disabled(birthFactsFieldsLocked)

                    if knowsBirthTime {
                        DatePicker("Время рождения", selection: $birthTime, displayedComponents: .hourAndMinute)
                            .datePickerStyle(.compact)
                            .disabled(birthFactsFieldsLocked)
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        TextField("Место рождения", text: $locationName)
                            .todayFlowSystemTextInput(words: true)
                            .textFieldStyle(.roundedBorder)
                            .disabled(birthFactsFieldsLocked)

                        if isSearching {
                            ProgressView("Ищу локации...")
                                .controlSize(.small)
                        }

                        if !birthFactsFieldsLocked, !suggestions.isEmpty {
                            VStack(spacing: 8) {
                                ForEach(suggestions) { suggestion in
                                    Button {
                                        locationName = suggestion.name
                                        selectedCoordinates = BirthCoordinates(
                                            latitude: suggestion.latitude,
                                            longitude: suggestion.longitude
                                        )
                                        suggestions = []
                                    } label: {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(suggestion.primaryLabel)
                                                .frame(maxWidth: .infinity, alignment: .leading)
                                            Text("\(suggestion.latitude.formatted(.number.precision(.fractionLength(2)))), \(suggestion.longitude.formatted(.number.precision(.fractionLength(2))))")
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                                .frame(maxWidth: .infinity, alignment: .leading)
                                        }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(14)
                            .background(Color.white.opacity(0.6))
                            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                        }
                    }

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.roseClay)
                    }

                    Button {
                        save()
                    } label: {
                        Text(isSaving ? "Сохраняю..." : "Сохранить изменения")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.sunset)
                    .disabled(isSaving || !isValid)
                }
                .padding(20)
            }
            .navigationTitle("Редактирование")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") {
                        dismiss()
                    }
                }
            }
            .task(id: locationName) {
                guard !birthFactsFieldsLocked else {
                    suggestions = []
                    isSearching = false
                    return
                }
                await refreshSuggestions()
            }
        }
    }

    private var isValid: Bool {
        !label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !locationName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private func refreshSuggestions() async {
        let trimmed = locationName.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.count < 2 {
            suggestions = []
            isSearching = false
            return
        }

        isSearching = true
        do {
            let fetched = try await TodayFlowAPIClient.shared.fetchLocationSuggestions(query: trimmed)
            if locationName.trimmingCharacters(in: .whitespacesAndNewlines) == trimmed {
                suggestions = fetched
            }
        } catch {
            suggestions = []
        }
        isSearching = false
    }

    private func save() {
        guard isValid else { return }
        isSaving = true
        errorMessage = nil

        let timeFormatter = DateFormatter()
        timeFormatter.calendar = Calendar(identifier: .gregorian)
        timeFormatter.locale = Locale(identifier: "en_US_POSIX")
        timeFormatter.timeZone = TimeZone(secondsFromGMT: 0)
        timeFormatter.dateFormat = "HH:mm:ss"

        let relationOut = profile.isPrimary == true ? "self" : relation
        let payload = AstroProfileUpdatePayload(
            label: label.trimmingCharacters(in: .whitespacesAndNewlines),
            relation: relationOut,
            birth_date: birthDate.apiDateString,
            birth_time: knowsBirthTime ? timeFormatter.string(from: birthTime) : nil,
            time_unknown: !knowsBirthTime,
            location_name: locationName.trimmingCharacters(in: .whitespacesAndNewlines),
            latitude: selectedCoordinates?.latitude,
            longitude: selectedCoordinates?.longitude
        )

        Task {
            do {
                _ = try await store.updateAstroProfile(profileID: profile.id, payload: payload)
                await onSaved()
                await MainActor.run {
                    isSaving = false
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isSaving = false
                }
            }
        }
    }

    private static func mergeTime(fromApi apiTime: String?, onto birthDay: Date) -> Date {
        guard let apiTime, !apiTime.isEmpty else { return birthDay }
        let tf = DateFormatter()
        tf.calendar = Calendar(identifier: .gregorian)
        tf.locale = Locale(identifier: "en_US_POSIX")
        tf.timeZone = TimeZone(secondsFromGMT: 0)
        tf.dateFormat = "HH:mm:ss"
        var segment = tf.date(from: apiTime)
        if segment == nil {
            tf.dateFormat = "HH:mm"
            segment = tf.date(from: apiTime)
        }
        guard let segment else { return birthDay }
        let cal = Calendar(identifier: .gregorian)
        var dc = cal.dateComponents([.year, .month, .day], from: birthDay)
        let tc = cal.dateComponents([.hour, .minute, .second], from: segment)
        dc.hour = tc.hour
        dc.minute = tc.minute
        dc.second = tc.second
        return cal.date(from: dc) ?? birthDay
    }
}

struct ProfileChartSection: View {
    let natalChart: NatalChartPreview?
    let coreProfile: CoreProfileResponse?
    let isLoading: Bool
    let error: String?
    var fullChartOpen: Bool = false
    let onReload: () async -> Void
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @State private var natalExpanded = true
    @State private var lifeMapExpanded = false
    @State private var fullMapExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            chartDisclosure(
                title: "Натальная карта",
                subtitle: "Сигнатура, личные числа и колесо.",
                isExpanded: $natalExpanded
            ) {
                natalContent
            }

            if natalChart != nil {
                chartDisclosure(
                    title: "Моя карта жизни",
                    subtitle: "Четыре опорных дома: кто ты, где дом, связь и проявление в мире.",
                    isExpanded: $lifeMapExpanded
                ) {
                    if let natalChart {
                        ProfileLifeMapInlineSection(natalChart: natalChart)
                    }
                }
            }

            chartDisclosure(
                title: "Полная карта",
                subtitle: "12 домов, планеты в знаках и аспекты.",
                isExpanded: $fullMapExpanded
            ) {
                ProfileChartFullMapView(natalChart: natalChart, onReload: onReload)
            }
        }
        .onAppear { syncDeepExpand(fullChartOpen) }
        .onChange(of: fullChartOpen) { _, open in syncDeepExpand(open) }
    }

    @ViewBuilder
    private func chartDisclosure<Content: View>(
        title: String,
        subtitle: String,
        isExpanded: Binding<Bool>,
        @ViewBuilder content: @escaping () -> Content
    ) -> some View {
        DisclosureGroup(isExpanded: isExpanded) {
            content()
                .padding(.top, 8)
        } label: {
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(subtitle)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(14)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private func syncDeepExpand(_ open: Bool) {
        guard open else { return }
        natalExpanded = true
        fullMapExpanded = true
    }

    @ViewBuilder
    private var natalContent: some View {
        if isLoading {
            ProgressView("Собираю карту...")
                .tint(TodayFlowTheme.sunset)
        } else if let natalChart {
            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                ForEach(signatureRows(chart: natalChart)) { row in
                    ProfilePlanetPositionCard(row: row)
                }
            }

            if let coreProfile {
                LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                    ForEach(numerologyMinis(from: coreProfile), id: \.id) { item in
                        numerologyCard(item: item)
                    }
                }
            }

            ProfileNatalWheel(chart: natalChart)
                .padding(.vertical, 6)

            if let summary = dominantSignatureSummary(for: natalChart) {
                Text(summary)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
            }

            Button("Обновить карту") {
                Task { await onReload() }
            }
            .buttonStyle(.bordered)
        } else {
            Text("Карта ещё не построена. Нажми обновить, чтобы подтянуть wheel, дома и аспекты.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.58))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }

        if let error {
            Text(error)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.roseClay)
        }
    }

    private func dominantSignatureSummary(for chart: NatalChartPreview) -> String? {
        let topBodies = ["sun", "moon", "mercury", "venus", "mars"].compactMap { key -> String? in
            guard let sign = chart.positions[key]?.sign, !sign.isEmpty else { return nil }
            return "\(key.capitalized) in \(sign)"
        }
        guard !topBodies.isEmpty else { return nil }
        return topBodies.joined(separator: " · ")
    }

    private var planetRows: [PlanetRow] {
        guard let natalChart else { return [] }
        let order = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        return order.compactMap { key in
            guard let position = natalChart.positions[key] else { return nil }
            return PlanetRow(
                title: title(for: key),
                glyph: glyph(for: key),
                sign: position.sign ?? "—",
                house: position.house,
                degree: position.longitude ?? position.degree
            )
        }
    }

    private func title(for key: String) -> String {
        switch key {
        case "sun": return "Солнце"
        case "moon": return "Луна"
        case "mercury": return "Меркурий"
        case "venus": return "Венера"
        case "mars": return "Марс"
        case "jupiter": return "Юпитер"
        case "saturn": return "Сатурн"
        case "uranus": return "Уран"
        case "neptune": return "Нептун"
        case "pluto": return "Плутон"
        default: return key.capitalized
        }
    }

    private func glyph(for key: String) -> String {
        switch key {
        case "sun": return "☉"
        case "moon": return "☽"
        case "mercury": return "☿"
        case "venus": return "♀"
        case "mars": return "♂"
        case "jupiter": return "♃"
        case "saturn": return "♄"
        case "uranus": return "♅"
        case "neptune": return "♆"
        case "pluto": return "♇"
        default: return "✦"
        }
    }

    private func signatureRows(chart: NatalChartPreview) -> [PlanetRow] {
        let ascSign = ascendantSign(for: chart)
        let ascDegree = chart.ascendant?.longitude ?? chart.ascendant?.degree
        let ascRow = PlanetRow(
            title: "Асцендент",
            glyph: "ASC",
            sign: ascSign,
            house: 1,
            degree: ascDegree
        )

        let core = ["sun", "moon"].compactMap { key -> PlanetRow? in
            guard let position = chart.positions[key] else { return nil }
            return PlanetRow(
                title: title(for: key),
                glyph: glyph(for: key),
                sign: position.sign ?? "—",
                house: position.house,
                degree: position.longitude ?? position.degree
            )
        }

        return core + [ascRow]
    }

    private func ascendantSign(for chart: NatalChartPreview) -> String {
        if let s = chart.ascendant?.sign, !s.isEmpty {
            return ZodiacSignRU.title(s)
        }
        if let longitude = chart.ascendant?.longitude ?? chart.ascendant?.degree {
            return ZodiacSignRU.title(ZodiacSignRU.englishSignFromLongitude(longitude))
        }
        if let s = chart.houses.first?.sign, !s.isEmpty {
            return ZodiacSignRU.title(s)
        }
        return "—"
    }

    private struct ProfileNumerologyItem: Identifiable {
        let id: String
        let label: String
        let value: String
        let hint: String?
    }

    @ViewBuilder
    private func numerologyCard(item: ProfileNumerologyItem) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(item.label.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.5))
            Text(item.value)
                .font(.subheadline.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink)
            if let hint = item.hint, !hint.isEmpty {
                Text(hint)
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.6))
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.9), Color(red: 0.98, green: 0.95, blue: 1.0).opacity(0.55)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
        }
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func numerologyMinis(from core: CoreProfileResponse) -> [ProfileNumerologyItem] {
        let n = core.numerology
        let cal = Calendar.current
        let refYear = cal.component(.year, from: Date())
        var items: [ProfileNumerologyItem] = []
        if let lp = n.lifePath {
            let hint: String
            if n.isMasterLifePath == true {
                hint = "главный сценарий · мастер-линия"
            } else {
                hint = "главный сценарий"
            }
            items.append(ProfileNumerologyItem(id: "lp", label: "Число пути", value: "\(lp)", hint: hint))
        }
        if let ex = n.expression {
            items.append(ProfileNumerologyItem(id: "ex", label: "Имя", value: "\(ex)", hint: "как ты проживаешь полное имя"))
        }
        if let su = n.soulUrge {
            items.append(ProfileNumerologyItem(id: "su", label: "Суть", value: "\(su)", hint: "внутренняя мотивация"))
        }
        if let pe = n.personality {
            items.append(ProfileNumerologyItem(id: "pe", label: "Подача", value: "\(pe)", hint: "как тебя встречают снаружи"))
        }
        if let py = personalYear(from: n.birthDate, refYear: refYear) {
            items.append(ProfileNumerologyItem(id: "py", label: "Личный год", value: "\(py)", hint: "для \(refYear) по дате рождения"))
        }
        return items
    }

    private func personalYear(from birthDate: String?, refYear: Int) -> Int? {
        guard let birthDate, birthDate.count >= 10 else { return nil }
        let head = String(birthDate.prefix(10))
        let segs = head.split(separator: "-")
        guard segs.count == 3, let m = Int(segs[1]), let d = Int(segs[2]), m > 0, m <= 12, d > 0, d <= 31 else { return nil }
        let sum = m + d + refYear
        return digitalRoot1to9(sum)
    }

    private func digitalRoot1to9(_ n: Int) -> Int {
        var x = abs(n)
        while x > 9 {
            var t = 0
            var v = x
            while v > 0 {
                t += v % 10
                v /= 10
            }
            x = t
        }
        if x == 0 { return 1 }
        return x
    }
}

private struct PlanetRow: Identifiable {
    let id = UUID()
    let title: String
    let glyph: String
    let sign: String
    let house: Int?
    let degree: Double?
}

private struct ProfilePlanetPositionCard: View {
    let row: PlanetRow

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(row.glyph)
                .font(.title3)
                .foregroundStyle(TodayFlowTheme.sunset)
            VStack(alignment: .leading, spacing: 4) {
                Text(row.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(summary)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
            }
            Spacer()
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var summary: String {
        var parts = [row.sign]
        if let house = row.house {
            parts.append("\(house) дом")
        }
        if let degree = row.degree {
            parts.append("\(Int(degree.rounded()))°")
        }
        return parts.joined(separator: " · ")
    }
}

private struct ProfileNatalWheel: View {
    let chart: NatalChartPreview
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        NatalChartWheelView(chart: chart, layout: .full, allowsFullscreen: true)
            .frame(height: horizontalSizeClass == .compact ? 300 : 348)
            .padding(10)
            .background(
                LinearGradient(
                    colors: [Color.white.opacity(0.88), TodayFlowTheme.paper.opacity(0.68)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }
}

private struct ProfileLifeMapInlineSection: View {
    let natalChart: NatalChartPreview
    private let highlightedHouses = [1, 4, 7, 10]
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
            ForEach(highlightedHouses, id: \.self) { house in
                let entry = houseEntry(house)
                VStack(alignment: .leading, spacing: 8) {
                    Text("\(house) дом")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(entry.tint)
                    Text(entry.title)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(entry.summary)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(14)
                .frame(maxWidth: .infinity, minHeight: 120, alignment: .topLeading)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
        }
    }

    private func houseEntry(_ houseNumber: Int) -> (title: String, summary: String, tint: Color) {
        let title: String
        let tint: Color
        switch houseNumber {
        case 1: title = "Кто ты"; tint = TodayFlowTheme.sunset
        case 4: title = "Где твой дом"; tint = TodayFlowTheme.moss
        case 7: title = "Как ты входишь в связь"; tint = TodayFlowTheme.twilight
        default: title = "Как ты проявляешься в мире"; tint = TodayFlowTheme.gold
        }
        let interpretation = natalChart.interpretations?.houses?["\(houseNumber)"]
        let house = natalChart.houses.first { $0.house == houseNumber }
        let summary = interpretation?.description
            ?? interpretation?.theme
            ?? house?.sign.map { "Тема дома окрашена знаком \($0)." }
            ?? ProfileHouseCopy.fallback[houseNumber]
            ?? "Этот слой карты станет частью основного профиля."
        return (title, summary, tint)
    }
}

private struct ProfileLifeMapSection: View {
    let natalChart: NatalChartPreview

    private let highlightedHouses = [1, 4, 7, 10]
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Четыре опорных дома")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Text("Быстрый срез по 1, 4, 7 и 10 дому. Тематические сферы жизни (любовь, деньги, тело и т. д.) в профиле собираются из нескольких элементов карты — это не копия только этих четырёх ячеек; дневные формулировки — в Today.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 12) {
                ForEach(highlightedHouses, id: \.self) { house in
                    let entry = houseEntry(house)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("\(house) дом")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(entry.tint)
                        Text(entry.title)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                        Text(entry.summary)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                            .lineLimit(5)
                    }
                    .padding(16)
                    .frame(maxWidth: .infinity, minHeight: 132, alignment: .topLeading)
                    .background(Color.white.opacity(0.56))
                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                }
            }
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
    }

    private func houseEntry(_ houseNumber: Int) -> (title: String, summary: String, tint: Color) {
        let title: String
        let tint: Color
        switch houseNumber {
        case 1:
            title = "Кто ты"
            tint = TodayFlowTheme.sunset
        case 4:
            title = "Где твой дом"
            tint = TodayFlowTheme.moss
        case 7:
            title = "Как ты входишь в связь"
            tint = TodayFlowTheme.twilight
        default:
            title = "Как ты проявляешься в мире"
            tint = TodayFlowTheme.gold
        }

        let interpretation = natalChart.interpretations?.houses?["\(houseNumber)"]
        let house = natalChart.houses.first { $0.house == houseNumber }
        let summary = interpretation?.description
        ?? interpretation?.theme
        ?? house?.sign.map { "Тема дома сейчас окрашена знаком \($0)." }
        ?? "Этот слой карты ещё не интерпретирован, но он должен стать частью основного профиля."
        return (title, summary, tint)
    }
}

private enum ProfileSettingsScreenChrome {
    static var useRussian: Bool {
        if let code = Locale.current.language.languageCode?.identifier.lowercased() {
            if code == "ru" { return true }
            if code == "en" { return false }
        }
        return Bundle.main.preferredLocalizations.first?.lowercased().hasPrefix("ru") == true
    }

    /// Подпись к выбору рода обращения в текстах (не смешивать с системным языком интерфейса).
    static var genderPickerLabel: String {
        useRussian ? "Обращение «ты» в текстах" : "Informal “you” in copy"
    }
}

private struct ProfileSettingsView: View {
    let store: TodayFlowStore

    @Environment(\.dismiss) private var dismiss
    @State private var email = ""
    @State private var greeting = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var country = ""
    @State private var language = ""
    @State private var locale = ""
    @State private var astrologyLevel = "beginner"
    @State private var textPreference = "detailed"
    @State private var todayNarrativeDepthLevel = "normal"
    /// Последнее значение с сервера — для meaning-события при смене только в форме настроек.
    @State private var serverSyncedNarrativeDepth = "normal"
    @State private var gender = "unspecified"

    private var canPickDeepNarrativeDepth: Bool {
        let t = (store.authSession?.insightDepthTier ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return t == "pro" || t == "premium"
    }
    @State private var stayLoggedIn = true
    @State private var newsletterOptIn = false
    @State private var pushOptIn = false
    @State private var apiBaseURL = ""
    @State private var astroServiceURL = ""
    @State private var webBaseURL = ""
    @State private var isChangePasswordPresented = false
    @State private var isLoading = false
    @State private var isSaving = false
    @State private var message: String?

    var body: some View {
        NavigationStack {
            Form {
                Section("Аккаунт") {
                    TextField("Эл. почта", text: $email)
                        .todayFlowEmailInput()
                    TextField("Приветствие", text: $greeting)
                        .todayFlowSystemTextInput()
                    TextField("Имя", text: $firstName)
                        .todayFlowSystemTextInput(words: true)
                    TextField("Фамилия", text: $lastName)
                        .todayFlowSystemTextInput(words: true)
                    TextField("Страна", text: $country)
                        .todayFlowSystemTextInput(words: true)
                    TextField("Язык", text: $language)
                        .todayFlowCodeInput()
                    TextField("Локаль", text: $locale)
                        .todayFlowCodeInput()
                    Picker(ProfileSettingsScreenChrome.genderPickerLabel, selection: $gender) {
                        Text("Нейтрально").tag("unspecified")
                        Text("Женский род").tag("female")
                        Text("Мужской род").tag("male")
                    }
                }

                Section("Стиль текстов") {
                    Picker("Уровень астрологии", selection: $astrologyLevel) {
                        Text("Начальный").tag("beginner")
                        Text("Средний").tag("intermediate")
                        Text("Продвинутый").tag("advanced")
                    }
                    Picker("Объём текстов", selection: $textPreference) {
                        Text("Коротко").tag("brief")
                        Text("Подробнее").tag("detailed")
                        Text("Развёрнуто").tag("comprehensive")
                    }
                    Picker("Глубина текстов «Сегодня»", selection: $todayNarrativeDepthLevel) {
                        Text(TodayRitualCopy.NarrativeDepthControl.optionQuick).tag("quick")
                        Text(TodayRitualCopy.NarrativeDepthControl.optionNormal).tag("normal")
                        if canPickDeepNarrativeDepth {
                            Text(TodayRitualCopy.NarrativeDepthControl.optionDeep).tag("deep")
                        }
                    }
                }

                Section("Предпочтения") {
                    Toggle("Оставаться в системе", isOn: $stayLoggedIn)
                    Toggle("Рассылка", isOn: $newsletterOptIn)
                    Toggle("Push-уведомления", isOn: $pushOptIn)
                }

                Section("Подключение") {
                    TextField("Базовый URL API", text: $apiBaseURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    TextField("URL астро-сервиса", text: $astroServiceURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    TextField("Базовый URL веба", text: $webBaseURL)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    Button("Сохранить адреса подключения") {
                        saveConnectionOverrides()
                    }

                    Button("Сбросить на значения проекта", role: .destructive) {
                        AppConfig.clearNetworkOverrides()
                        apiBaseURL = AppConfig.apiBaseURLString
                        astroServiceURL = AppConfig.astroServiceURLString
                        webBaseURL = AppConfig.webBaseURLString
                        message = "Адреса подключения сброшены."
                    }
                }

                Section("Безопасность") {
                    Button("Сменить пароль") {
                        isChangePasswordPresented = true
                    }
                    Button("Выйти", role: .destructive) {
                        store.signOut()
                        dismiss()
                    }
                }

                if let message {
                    Section {
                        Text(message)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Настройки")
            .task {
                await load()
            }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(isSaving ? "Сохраняю..." : "Сохранить") {
                        save()
                    }
                    .disabled(isSaving || isLoading || email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
            .sheet(isPresented: $isChangePasswordPresented) {
                ChangePasswordView(store: store)
            }
        }
    }

    private func load() async {
        if isLoading { return }
        isLoading = true
        await store.resumeSessionIfNeeded()
        await MainActor.run {
            apiBaseURL = AppConfig.apiBaseURLString
            astroServiceURL = AppConfig.astroServiceURLString
            webBaseURL = AppConfig.webBaseURLString
        }
        do {
            let settings = try await store.loadAccountSettings()
            await MainActor.run {
                email = settings.email
                greeting = settings.greeting ?? ""
                firstName = settings.firstName ?? ""
                lastName = settings.lastName ?? ""
                country = settings.country ?? ""
                language = settings.language ?? ""
                locale = settings.locale ?? ""
                astrologyLevel = settings.astrologyLevel ?? "beginner"
                textPreference = settings.textPreference ?? "detailed"
                let loadedDepth = settings.todayNarrativeDepthLevel ?? "normal"
                let effectiveDepth = (loadedDepth == "deep" && !canPickDeepNarrativeDepth) ? "normal" : loadedDepth
                todayNarrativeDepthLevel = effectiveDepth
                serverSyncedNarrativeDepth = effectiveDepth
                gender = settings.gender ?? "unspecified"
                stayLoggedIn = settings.stayLoggedIn ?? true
                newsletterOptIn = settings.newsletterOptIn ?? false
                pushOptIn = settings.pushOptIn ?? false
                isLoading = false
            }
        } catch {
            await MainActor.run {
                message = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func saveConnectionOverrides() {
        AppConfig.setAPIBaseURLOverride(apiBaseURL)
        AppConfig.setAstroServiceURLOverride(astroServiceURL)
        AppConfig.setWebBaseURLOverride(webBaseURL)
        apiBaseURL = AppConfig.apiBaseURLString
        astroServiceURL = AppConfig.astroServiceURLString
        webBaseURL = AppConfig.webBaseURLString
        message = "Адреса подключения сохранены."
    }

    private func save() {
        isSaving = true
        message = nil
        let narrativeDepthBeforeSave = serverSyncedNarrativeDepth
        let payload = AccountSettingsUpdate(
            email: email.trimmingCharacters(in: .whitespacesAndNewlines),
            greeting: greeting.nilIfBlank,
            firstName: firstName.nilIfBlank,
            lastName: lastName.nilIfBlank,
            country: country.nilIfBlank,
            language: language.nilIfBlank,
            locale: locale.nilIfBlank,
            stayLoggedIn: stayLoggedIn,
            newsletterOptIn: newsletterOptIn,
            pushOptIn: pushOptIn,
            astrologyLevel: astrologyLevel,
            textPreference: textPreference,
            todayNarrativeDepthLevel: todayNarrativeDepthLevel,
            gender: gender
        )
        Task {
            do {
                _ = try await store.updateAccountSettings(payload)
                if todayNarrativeDepthLevel != narrativeDepthBeforeSave {
                    await store.trackTodaySurfaceEvent(
                        eventType: "today_narrative_depth_changed",
                        eventSource: "today",
                        qualityScore: 0.55,
                        payload: [
                            "depth_level": .string(todayNarrativeDepthLevel),
                            "source": .string("profile_settings"),
                        ]
                    )
                }
                await MainActor.run {
                    serverSyncedNarrativeDepth = todayNarrativeDepthLevel
                }
                _ = try? await store.loadCoreProfile(force: true)
                _ = try? await store.loadProfileSummary(force: true)
                await MainActor.run {
                    isSaving = false
                    message = "Настройки сохранены."
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    message = error.localizedDescription
                }
            }
        }
    }
}

private struct ChangePasswordView: View {
    let store: TodayFlowStore

    @Environment(\.dismiss) private var dismiss
    @State private var currentPassword = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var isSubmitting = false
    @State private var message: String?

    var body: some View {
        NavigationStack {
            Form {
                SecureField("Текущий пароль", text: $currentPassword)
                    .todayFlowSecureInput()
                SecureField("Новый пароль", text: $newPassword)
                    .todayFlowSecureInput()
                SecureField("Повтори новый пароль", text: $confirmPassword)
                    .todayFlowSecureInput()

                if let message {
                    Text(message)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Button("Обновить пароль") {
                    submit()
                }
                .disabled(isSubmitting || !canSubmit)
            }
            .navigationTitle("Смена пароля")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") {
                        dismiss()
                    }
                }
            }
        }
    }

    private var canSubmit: Bool {
        currentPassword.count >= 8 && newPassword.count >= 8 && newPassword == confirmPassword
    }

    private func submit() {
        guard canSubmit else { return }
        isSubmitting = true
        message = nil

        Task {
            do {
                let result = try await store.changePassword(
                    currentPassword: currentPassword,
                    newPassword: newPassword
                )
                await MainActor.run {
                    isSubmitting = false
                    message = result
                    currentPassword = ""
                    newPassword = ""
                    confirmPassword = ""
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    message = error.localizedDescription
                }
            }
        }
    }
}

private struct ProfileSummaryQuickSection: View {
    let summary: ProfileSummaryResponse
    let buildStatus: ProfileBuildStatusResponse?
    let rings: [MeaningRingItem]
    var onOpenSettings: (() -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Сводка профиля")
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(summary.livingSummary ?? "Короткая сводка перед Today уже собрана.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            if summary.missingFields.contains("gender") {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Чтобы подсказки на «ты» звучали естественно, выбери обращение в настройках.")
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .fixedSize(horizontal: false, vertical: true)
                    if let onOpenSettings {
                        Button("Настройки") {
                            onOpenSettings()
                        }
                        .buttonStyle(.bordered)
                        .tint(TodayFlowTheme.sunset)
                    }
                }
                .padding(.top, 4)
            }

            HStack(spacing: 10) {
                summaryChip("Солнце", summary.coreTrio.sunSign ?? "—")
                summaryChip("Путь", summary.coreTrio.lifePath.map { "\($0)" } ?? "—")
                summaryChip("Статус", profileBuildStatusDisplay(buildStatus?.status ?? (summary.isReady ? "ready" : "building")))
            }

            if !ringData.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Кольца осмысленности")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    ForEach(ringData.prefix(6), id: \.ring) { ring in
                        VStack(alignment: .leading, spacing: 4) {
                            HStack {
                                Text(ring.ring)
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.ink)
                                Spacer()
                                Text("\(ring.score)%")
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                            TodayFlowSphereSliderTrack(
                                value: ring.score,
                                tint: TodayFlowMeaningRingAccent.color(for: ring.ring),
                                accessibilityTitle: ring.ring,
                                density: .compact
                            )
                        }
                    }
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func profileBuildStatusDisplay(_ raw: String?) -> String {
        let s = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch s {
        case "ready": return "Готово"
        case "building": return "Собирается"
        default:
            let t = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            return t.isEmpty ? "—" : t
        }
    }

    private var ringData: [MeaningRingItem] {
        if !rings.isEmpty { return rings }
        return summary.ringsPreview.map { MeaningRingItem(ring: $0.key, score: $0.value, trend7d: 0, confidence: "low", topContributors: []) }
            .sorted { $0.ring < $1.ring }
    }

    private func summaryChip(_ title: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(value)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 10)
        .background(Color.white.opacity(0.62))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

private extension String {
    var nilIfBlank: String? {
        let trimmed = trimmingCharacters(in: .whitespacesAndNewlines)
        return trimmed.isEmpty ? nil : trimmed
    }
}

#Preview {
    ProfileView(store: TodayFlowStore())
}
