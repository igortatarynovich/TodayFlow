import SwiftUI
#if canImport(UIKit) && !os(watchOS)
import UIKit
#endif

private struct TodayFocusTwentyBar: View {
    let deadline: Date
    let onStop: () -> Void

    var body: some View {
        TimelineView(.periodic(from: .now, by: 1)) { context in
            let left = max(0, deadline.timeIntervalSince(context.date))
            let totalSec = Int(left.rounded(.down))
            let m = totalSec / 60
            let s = totalSec % 60
            HStack(spacing: 12) {
                Text(TodayRitualCopy.FocusTimerChrome.chromeLine(timeLabel: "\(m):\(String(format: "%02d", s))"))
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer(minLength: 8)
                Button(TodayRitualCopy.FocusTimerChrome.stop, action: onStop)
                    .buttonStyle(.bordered)
                    .tint(TodayFlowTheme.sunset)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(.ultraThinMaterial)
            .overlay(alignment: .top) {
                Divider().opacity(0.35)
            }
        }
    }
}

private enum RitualHaptics {
    static func light() {
        #if os(iOS) && !os(watchOS)
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
        #endif
    }

    static func medium() {
        #if os(iOS) && !os(watchOS)
        UIImpactFeedbackGenerator(style: .medium).impactOccurred()
        #endif
    }
}

private protocol TodayChoiceOption {
    var title: String { get }
}

struct TodayView: View {
    enum Step: String, CaseIterable, Identifiable {
        case guide
        case morning
        case day
        case evening

        var id: String { rawValue }

        var title: String {
            switch self {
            case .guide: return TodayShellCopy.shellNativeStepGuideTitle
            case .morning: return TodayShellCopy.shellNativeStepMorningTitle
            case .day: return TodayShellCopy.shellNativeStepDayTitle
            case .evening: return TodayShellCopy.shellNativeStepEveningTitle
            }
        }

        var subtitle: String {
            switch self {
            case .guide: return TodayShellCopy.shellNativeStepGuideSubtitle
            case .morning: return TodayShellCopy.shellNativeStepMorningSubtitle
            case .day: return TodayShellCopy.shellNativeStepDaySubtitle
            case .evening: return TodayShellCopy.shellNativeStepEveningSubtitle
            }
        }

        var systemImage: String {
            switch self {
            case .guide: return "sparkles.rectangle.stack"
            case .morning: return "sun.horizon"
            case .day: return "bolt.heart"
            case .evening: return "moon.stars"
            }
        }
    }

    let store: TodayFlowStore
    var onOpenProfileSummaryRoute: ((AppTab) -> Void)? = nil
    /// Переключение таба (Сегодня / Flow / Профиль / …) без WebView.
    var onSelectTab: ((AppTab) -> Void)? = nil

    @State private var guideNarrativeLoading = false
    @State private var dayNarrativeLoading = false
    @State private var spheresNarrativeLoading = false
    @State private var eveningNarrativeLoading = false
    @State private var isProfileSummaryPresented = false
    @State private var focusTwentyEndsAt: Date?
    /// DE-8: глубина narrative на экране Today (сервер `today_narrative_depth_level`).
    @State private var todayNarrativeDepthPicker = "normal"
    @State private var lastSyncedNarrativeDepth = "normal"
    @State private var narrativeDepthBarReady = false
    @State private var narrativeDepthSaving = false

    private var canPickDeepNarrativeDepth: Bool {
        let t = (store.authSession?.insightDepthTier ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        return t == "pro" || t == "premium"
    }

    var body: some View {
        NavigationStack {
            // Внутри `TodayRitualFlowView` уже есть свой `ScrollView`. Внешний здесь давал
            // вложенные скроллы: в симуляторе жесты часто «зависали», тапы по колоде не доходили.
            VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s4) {
                if store.loadState == .loading || store.isRefreshingToday {
                    HStack(spacing: 12) {
                        ProgressView()
                            .tint(TodayFlowTheme.sunset)
                        Text(store.todayCycle == nil ? TodayRitualCopy.TodayPageShell.loadingDay : TodayRitualCopy.TodayPageShell.refreshingDay)
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                    }
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.72))
                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                }

                if let sessionWarning = store.sessionWarningMessage {
                    Label(sessionWarning, systemImage: "wifi.slash")
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .padding(14)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.orange.opacity(0.16))
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                }

                if let cycle = store.todayCycle {
                    if narrativeDepthBarReady, store.authSession != nil {
                        TodayNarrativeDepthInlineBar(
                            selection: $todayNarrativeDepthPicker,
                            canPickDeep: canPickDeepNarrativeDepth,
                            saving: narrativeDepthSaving
                        )
                        .onChange(of: todayNarrativeDepthPicker) { _, new in
                            Task { await commitNarrativeDepthChange(new) }
                        }
                    }
                    TodayCompositionSurfaceView(
                        store: store,
                        cycle: cycle,
                        onSelectTab: { tab in onSelectTab?(tab) },
                        onNavigateCalendarQuickCreate: { kind in
                            store.requestTrackerQuickCreate(kind)
                            onSelectTab?(.calendar)
                        },
                        onStartFocus20Minutes: {
                            focusTwentyEndsAt = Date().addingTimeInterval(20 * 60)
                        },
                        guideNarrativeLoading: guideNarrativeLoading,
                        eveningNarrativeLoading: eveningNarrativeLoading
                    )
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
                } else {
                    ScrollView {
                        TodayFallbackPanel(store: store)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
                }
            }
            .todayFlowContentContainer(maxWidth: 1240, horizontal: 20, top: 8, bottom: 12)
            .safeAreaInset(edge: .bottom, spacing: 0) {
                if let end = focusTwentyEndsAt {
                    TodayFocusTwentyBar(deadline: end) {
                        focusTwentyEndsAt = nil
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .navigationTitle(TodayWebGuideSectionCopy.guidePanelEyebrowToday)
            .todayflowNavigationBarTitleDisplayModeInline()
            .task {
                if store.todayCycle == nil {
                    await store.refreshIfNeeded()
                }
                _ = try? await store.loadProfileSummary()
                if store.authSession != nil {
                    if store.natalChart == nil {
                        _ = try? await store.loadNatalChart(force: false)
                    }
                    if store.coreProfile == nil {
                        _ = try? await store.loadCoreProfile(force: false)
                    }
                }
                await preloadGuideSurface(force: false)
            }
            .task(id: store.authSession?.userID) {
                await loadNarrativeDepthFromServerForToday()
            }
            .task(id: store.todayCycle?.date) {
                guard store.todayCycle != nil else { return }
                if !TodayFirstTodayState.hasCompletedFirstToday {
                    TodayFirstTodayState.markFirstTodayCompleted(dayKey: store.todayCycle?.date)
                }
                focusTwentyEndsAt = nil
                await preloadAllNarratives(force: false)
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        isProfileSummaryPresented = true
                    } label: {
                        Label(TodayShellCopy.shellToolbarOpenProfileSummary, systemImage: "person.text.rectangle")
                    }
                }
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        Task {
                            await store.refreshIfNeeded()
                            await preloadAllNarratives(force: true)
                        }
                    } label: {
                        Label(TodayShellCopy.shellToolbarRefresh, systemImage: "arrow.clockwise")
                    }
                }
            }
            .sheet(isPresented: $isProfileSummaryPresented) {
                ProfileSummaryView(store: store) { tab in
                    isProfileSummaryPresented = false
                    onOpenProfileSummaryRoute?(tab)
                }
            }
        }
    }

    private func loadNarrativeDepthFromServerForToday() async {
        await MainActor.run { narrativeDepthBarReady = false }
        guard store.authSession != nil else { return }
        do {
            let s = try await store.loadAccountSettings()
            let loaded = s.todayNarrativeDepthLevel ?? "normal"
            let effective = (loaded == "deep" && !canPickDeepNarrativeDepth) ? "normal" : loaded
            await MainActor.run {
                todayNarrativeDepthPicker = effective
                lastSyncedNarrativeDepth = effective
                narrativeDepthBarReady = true
            }
        } catch {
            await MainActor.run {
                narrativeDepthBarReady = true
            }
        }
    }

    @MainActor
    private func commitNarrativeDepthChange(_ newValue: String) async {
        guard narrativeDepthBarReady else { return }
        guard newValue != lastSyncedNarrativeDepth else { return }
        if newValue == "deep" && !canPickDeepNarrativeDepth {
            todayNarrativeDepthPicker = lastSyncedNarrativeDepth
            return
        }
        narrativeDepthSaving = true
        defer { narrativeDepthSaving = false }
        do {
            _ = try await store.updateTodayNarrativeDepthLevel(newValue)
            lastSyncedNarrativeDepth = newValue
            await store.trackTodaySurfaceEvent(
                eventType: "today_narrative_depth_changed",
                eventSource: "today",
                qualityScore: 0.55,
                payload: [
                    "depth_level": .string(newValue),
                    "source": .string("today_depth_strip"),
                ]
            )
            await preloadAllNarratives(force: true)
        } catch {
            todayNarrativeDepthPicker = lastSyncedNarrativeDepth
        }
    }

    private func preloadGuideSurface(force: Bool) async {
        guard store.todayCycle != nil else { return }
        if guideNarrativeLoading { return }
        guideNarrativeLoading = true
        defer { guideNarrativeLoading = false }
        _ = try? await store.loadTodayNarrative(surface: .guide, force: force)
    }

    private func preloadAllNarratives(force: Bool = false) async {
        await preloadGuideSurface(force: force)
        await preloadNarratives(for: .morning, force: force)
        await preloadNarratives(for: .guide, force: force)
        await preloadNarratives(for: .evening, force: force)
    }

    private func preloadNarratives(for step: Step, force: Bool = false) async {
        switch step {
        case .guide:
            await preloadGuideSurface(force: force)
            guard store.todayCycle != nil else { return }
            if !spheresNarrativeLoading {
                spheresNarrativeLoading = true
                _ = try? await store.loadTodayNarrative(surface: .spheres, force: force)
                spheresNarrativeLoading = false
            }
        case .morning, .day:
            await preloadGuideSurface(force: false)
            guard store.todayCycle != nil, !dayNarrativeLoading else { return }
            dayNarrativeLoading = true
            _ = try? await store.loadTodayNarrative(surface: .dayLayer, force: force)
            dayNarrativeLoading = false
        case .evening:
            await preloadGuideSurface(force: false)
            guard store.todayCycle != nil, !eveningNarrativeLoading else { return }
            eveningNarrativeLoading = true
            _ = try? await store.loadTodayNarrative(surface: .evening, force: force)
            eveningNarrativeLoading = false
        }
    }
}

/// DE-8: сегментированный выбор глубины на Today (паритет веб `TodayNarrativeDepthControl`).
private struct TodayNarrativeDepthInlineBar: View {
    @Binding var selection: String
    let canPickDeep: Bool
    let saving: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text(TodayRitualCopy.NarrativeDepthControl.eyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                if saving {
                    ProgressView()
                        .scaleEffect(0.85)
                        .tint(TodayFlowTheme.sunset)
                }
            }
            Picker("", selection: $selection) {
                Text(TodayRitualCopy.NarrativeDepthControl.optionQuick).tag("quick")
                Text(TodayRitualCopy.NarrativeDepthControl.optionNormal).tag("normal")
                if canPickDeep {
                    Text(TodayRitualCopy.NarrativeDepthControl.optionDeep).tag("deep")
                }
            }
            .pickerStyle(.segmented)
            .disabled(saving)
            Group {
                if saving {
                    Text(TodayRitualCopy.NarrativeDepthControl.saving)
                } else {
                    Text("\(TodayRitualCopy.NarrativeDepthControl.hint) \(TodayRitualCopy.NarrativeDepthControl.hintSettingsTail)")
                }
            }
            .font(.caption2)
            .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
            .fixedSize(horizontal: false, vertical: true)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
        }
    }
}

private struct TodayAdaptiveStack<Content: View>: View {
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

private struct TodayPolishedSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.caption.weight(.semibold))
                .textCase(.uppercase)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.6))
                .tracking(0.8)
            content()
        }
        .padding(12)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.82), TodayFlowTheme.paper.opacity(0.76)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
        }
        .shadow(color: TodayFlowTheme.gold.opacity(0.08), radius: 10, y: 4)
        .animation(.spring(response: 0.34, dampingFraction: 0.9), value: title)
    }
}

private func todayAdaptiveColumns(for horizontalSizeClass: UserInterfaceSizeClass?) -> [GridItem] {
    if horizontalSizeClass == .compact {
        return [GridItem(.flexible())]
    }
    return [GridItem(.flexible()), GridItem(.flexible())]
}

private struct TodayHeroSection: View {
    let cycle: TodayCycle
    let dashboard: TodayDashboard
    let fusionIndex: FusionIndex?
    let profile: BirthProfile?
    let natalChart: NatalChartPreview?
    let user: UserProfile
    let loadState: TodayFlowStore.LoadState
    @Binding var isOverviewExpanded: Bool
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            TodayAdaptiveStack(spacing: 14) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(cycle.formattedDateTitle.uppercased())
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)

                    Text(TodayWebGuideSectionCopy.guidePanelEyebrowToday)
                        .font(.system(size: 38, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.ink)

                    Text(headline)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)

                    Text(subheadline)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                        .padding(.top, 2)
                        .lineLimit(isOverviewExpanded ? nil : 3)
                        .fixedSize(horizontal: false, vertical: true)
                }

                VStack(alignment: horizontalSizeClass == .compact ? .leading : .trailing, spacing: 12) {
                    TodayStatePill(loadState: loadState)
                    if isOverviewExpanded {
                        TodayGlowBadge(text: displayName)
                        TodayLifeLevelOrb(contour: dashboard.contour, metrics: dashboard.metrics)
                    }
                }
            }

            if isOverviewExpanded {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(heroChips) { chip in
                            TodayHeroChip(title: chip.title, value: chip.value)
                        }
                    }
                }

                TodayAdaptiveStack(spacing: 14) {
                    TodayHeroSignalCard(
                        title: TodayRitualCopy.dayEngineBriefEyebrow,
                        value: cycle.morning?.dailyHoroscope?.spine?.firstMove ?? cycle.consistency?.doFocus ?? TodayShellCopy.shellHeroFirstMoveFallback,
                        tint: TodayFlowTheme.gold
                    )
                    TodayHeroSignalCard(
                        title: TodayShellCopy.shellHeroDoNotEnterTitle,
                        value: cycle.morning?.dailyHoroscope?.spine?.doNotEnter ?? cycle.consistency?.avoidFocus ?? TodayShellCopy.shellHeroAvoidFallback,
                        tint: TodayFlowTheme.roseClay
                    )
                }

                TodayAdaptiveStack(spacing: 12) {
                    ForEach(dashboard.metrics) { metric in
                        TodayAuraDot(
                            value: metric.value,
                            title: metric.title,
                            tint: tint(for: metric.id)
                        )
                    }
                }

                if let alertLine = dashboard.contour.alertLine {
                    TodayHeroSignalCard(
                        title: TodayShellCopy.shellHeroSignalDayTitle,
                        value: alertLine,
                        tint: dashboard.contour.tier == .platinum ? TodayFlowTheme.twilight : TodayFlowTheme.gold
                    )
                }
            }

            Button {
                withAnimation(.spring(response: 0.38, dampingFraction: 0.86)) {
                    isOverviewExpanded.toggle()
                }
            } label: {
                HStack(spacing: 8) {
                    Text(isOverviewExpanded ? TodayShellCopy.shellHeroOverviewCollapse : TodayShellCopy.shellHeroOverviewExpand)
                        .font(.subheadline.weight(.semibold))
                    Image(systemName: "chevron.down")
                        .font(.subheadline.weight(.semibold))
                        .rotationEffect(.degrees(isOverviewExpanded ? 180 : 0))
                }
                .foregroundStyle(TodayFlowTheme.sunset)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.vertical, 4)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(isOverviewExpanded ? TodayShellCopy.shellHeroOverviewA11yCollapse : TodayShellCopy.shellHeroOverviewA11yExpand)
        }
        .padding(24)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.92), TodayFlowTheme.paper.opacity(0.92), TodayFlowTheme.mist.opacity(0.78)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
        .overlay(alignment: .topTrailing) {
            if isOverviewExpanded, horizontalSizeClass != .compact {
                ZStack {
                    Circle()
                        .fill(TodayFlowTheme.sunset.opacity(0.16))
                        .frame(width: 142, height: 142)
                    Circle()
                        .stroke(TodayFlowTheme.gold.opacity(0.32), lineWidth: 1)
                        .frame(width: 98, height: 98)
                    Image(systemName: "sun.max.fill")
                        .font(.system(size: 34))
                        .foregroundStyle(TodayFlowTheme.sunset.opacity(0.55))
                }
                .padding(18)
                .allowsHitTesting(false)
            }
        }
    }

    private var heroChips: [TodayHeroChipItem] {
        var chips: [TodayHeroChipItem] = []
        if let c = natalChart, let sun = ZodiacSignRU.planetLine(c, body: "sun") {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipSun, value: sun))
        } else if let sign = cycle.coreProfile?.sunSign ?? profile?.sunSign, !sign.isEmpty {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipSun, value: ZodiacSignRU.title(sign)))
        }
        if let c = natalChart, let moon = ZodiacSignRU.planetLine(c, body: "moon") {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipMoon, value: moon))
        } else if let moon = profile?.moonSign, !moon.isEmpty {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipMoon, value: ZodiacSignRU.title(moon)))
        }
        if let c = natalChart, let asc = ZodiacSignRU.ascendantLine(c) {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipAscendant, value: asc))
        } else if let rising = profile?.risingSign, !rising.isEmpty {
            chips.append(TodayHeroChipItem(title: TodayShellCopy.shellHeroChipAscendant, value: ZodiacSignRU.title(rising)))
        }
        return chips
    }

    private var displayName: String {
        let first = cycle.coreProfile?.firstName ?? profile?.firstName ?? user.firstName
        return first.isEmpty ? user.firstName : first
    }

    private var headline: String {
        cycle.morning?.dailyHoroscope?.headline
        ?? cycle.morning?.dailyHoroscope?.spine?.bestMode
        ?? cycle.consistency?.summary
        ?? TodayShellCopy.shellHeroHeadlineFallback
    }

    private var subheadline: String {
        cycle.morning?.dailyForecastSummary?.summary
        ?? cycle.morning?.dailyHoroscope?.profilePrism
        ?? TodayShellCopy.shellHeroSubheadlineFallback
    }

    private func tint(for metricID: String) -> Color {
        switch metricID {
        case "execution":
            return TodayFlowTheme.sunset
        case "awareness":
            return TodayFlowTheme.moss
        case "alignment":
            return TodayFlowTheme.twilight
        default:
            return TodayFlowTheme.gold
        }
    }
}

private struct TodayLifeLevelOrb: View {
    let contour: LifeLevelContour
    let metrics: [RingMetric]
    @State private var isExpanded = false
    @State private var revealProgress = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Button {
                withAnimation(.spring(response: 0.38, dampingFraction: 0.86)) {
                    isExpanded.toggle()
                }
            } label: {
                ZStack {
                    Circle()
                        .stroke(
                            AngularGradient(
                                colors: metalColors,
                                center: .center
                            ),
                            style: StrokeStyle(lineWidth: 12, lineCap: .round)
                        )
                        .frame(width: 196, height: 196)
                        .shadow(color: contourShadow, radius: 16, x: 0, y: 8)

                    Circle()
                        .stroke(Color.white.opacity(0.7), lineWidth: 1)
                        .frame(width: 178, height: 178)

                    ForEach(Array(metrics.prefix(3).enumerated()), id: \.element.id) { index, metric in
                        TodayRingProgressCircle(
                            metric: metric,
                            tint: ringTint(for: metric.id),
                            size: [154.0, 128.0, 102.0][index],
                            lineWidth: [12.0, 10.0, 8.0][index],
                            revealProgress: revealProgress
                        )
                    }

                    VStack(spacing: 4) {
                        Text(TodayShellCopy.shellYourLevelLabel)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        Text(contour.tier.title)
                            .font(.system(size: 26, weight: .bold, design: .rounded))
                            .foregroundStyle(TodayFlowTheme.ink)
                        Text("\(contour.score)")
                            .font(.title3.weight(.semibold))
                            .foregroundStyle(contourAccent)
                    }
                }
            }
            .buttonStyle(.plain)

            Text(contour.tier.shortMeaning)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))

            if isExpanded {
                VStack(alignment: .leading, spacing: 8) {
                    Text(TodayShellCopy.formatYourLevelDetail(tierTitle: contour.tier.title))
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(contour.statusLine)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                    Text(contour.guidanceLine)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                    if let alertLine = contour.alertLine {
                        Text(alertLine)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(contourAccent)
                    }
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.58))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
        .frame(maxWidth: 220, alignment: .leading)
        .task {
            guard !revealProgress else { return }
            withAnimation(.easeOut(duration: 1.0)) {
                revealProgress = true
            }
        }
    }

    private var metalColors: [Color] {
        switch contour.tier {
        case .bronze:
            return [Color(red: 0.78, green: 0.60, blue: 0.48), Color(red: 0.53, green: 0.37, blue: 0.28), Color.white.opacity(0.85), Color(red: 0.78, green: 0.60, blue: 0.48)]
        case .silver:
            return [Color(red: 0.87, green: 0.88, blue: 0.90), Color(red: 0.58, green: 0.61, blue: 0.66), Color.white.opacity(0.92), Color(red: 0.87, green: 0.88, blue: 0.90)]
        case .gold:
            return [Color(red: 0.92, green: 0.82, blue: 0.58), Color(red: 0.68, green: 0.53, blue: 0.25), Color.white.opacity(0.92), Color(red: 0.92, green: 0.82, blue: 0.58)]
        case .platinum:
            return [Color(red: 0.88, green: 0.91, blue: 0.96), Color(red: 0.52, green: 0.58, blue: 0.70), Color.white.opacity(0.95), Color(red: 0.88, green: 0.91, blue: 0.96)]
        }
    }

    private var contourAccent: Color {
        switch contour.tier {
        case .bronze: return TodayFlowTheme.ember
        case .silver: return TodayFlowTheme.twilight
        case .gold: return TodayFlowTheme.gold
        case .platinum: return TodayFlowTheme.twilight
        }
    }

    private var contourShadow: Color {
        contourAccent.opacity(0.22)
    }

    private func ringTint(for metricID: String) -> Color {
        switch metricID {
        case "execution": return TodayFlowTheme.sunset
        case "awareness": return TodayFlowTheme.moss
        case "alignment": return TodayFlowTheme.twilight
        default: return TodayFlowTheme.gold
        }
    }
}

private struct TodayRingProgressCircle: View {
    let metric: RingMetric
    let tint: Color
    let size: Double
    let lineWidth: Double
    let revealProgress: Bool

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.32), lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: revealProgress ? metric.progress : 0.02)
                .stroke(
                    AngularGradient(
                        colors: [tint.opacity(0.24), tint, Color.white.opacity(0.9), tint.opacity(0.5)],
                        center: .center
                    ),
                    style: StrokeStyle(lineWidth: lineWidth, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
        }
        .frame(width: size, height: size)
    }
}

private struct TodayHeroChipItem: Identifiable {
    let id = UUID()
    let title: String
    let value: String
}

private struct TodayMeaningRingsStrip: View {
    let rings: [MeaningRingItem]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(TodayShellCopy.meaningRingsSectionTitle)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(rings.prefix(6)) { ring in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(ring.ring)
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            Text("\(ring.score)%")
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(ring.confidence)
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.sunset)
                        }
                        .padding(.vertical, 9)
                        .padding(.horizontal, 11)
                        .background(Color.white.opacity(0.68))
                        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                    }
                }
            }
        }
        .padding(14)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private struct TodayStepPicker: View {
    @Binding var selectedStep: TodayView.Step
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(TodayView.Step.allCases) { step in
                    Button {
                        withAnimation(.spring(response: 0.36, dampingFraction: 0.88)) {
                            selectedStep = step
                        }
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            Label(step.title, systemImage: step.systemImage)
                                .font(.subheadline.weight(.semibold))
                            Text(step.subtitle)
                                .font(.caption)
                                .foregroundStyle(selectedStep == step ? .white.opacity(0.8) : TodayFlowTheme.ink.opacity(0.56))
                        }
                        .padding(.horizontal, 16)
                        .padding(.vertical, 14)
                        .frame(width: horizontalSizeClass == .compact ? 132 : 150, alignment: .leading)
                        .background(
                            selectedStep == step
                            ? LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .topLeading, endPoint: .bottomTrailing)
                            : LinearGradient(colors: [Color.white.opacity(0.86), TodayFlowTheme.paper.opacity(0.92)], startPoint: .topLeading, endPoint: .bottomTrailing)
                        )
                        .foregroundStyle(selectedStep == step ? Color.white : TodayFlowTheme.ink)
                        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                        .overlay {
                            RoundedRectangle(cornerRadius: 22, style: .continuous)
                                .stroke(selectedStep == step ? Color.clear : TodayFlowTheme.gold.opacity(0.12), lineWidth: 1)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}

private struct TodayCurrentStepSection: View {
    let step: TodayView.Step
    let cycle: TodayCycle
    let fusionIndex: FusionIndex?
    let fusionHistory: [FusionIndex]
    let profile: BirthProfile?
    let store: TodayFlowStore
    let guideNarrative: TodayNarrativeResponse?
    let dayNarrative: TodayNarrativeResponse?
    let spheresNarrative: TodayNarrativeResponse?
    let eveningNarrative: TodayNarrativeResponse?
    let guideNarrativeLoading: Bool
    let dayNarrativeLoading: Bool
    let spheresNarrativeLoading: Bool
    let eveningNarrativeLoading: Bool
    @Binding var tarotSelection: Int?
    @Binding var tarotRevealed: Bool

    var body: some View {
        switch step {
        case .guide:
            TodayGuidePanel(
                cycle: cycle,
                fusionIndex: fusionIndex,
                fusionHistory: fusionHistory,
                store: store,
                guideNarrative: guideNarrative,
                spheresNarrative: spheresNarrative,
                isGuideLoading: guideNarrativeLoading,
                isSpheresLoading: spheresNarrativeLoading,
                tarotSelection: $tarotSelection,
                tarotRevealed: $tarotRevealed
            )
        case .morning:
            TodayMorningPanel(cycle: cycle, profile: profile, store: store, narrative: dayNarrative, isNarrativeLoading: dayNarrativeLoading)
        case .day:
            TodayDayPanel(cycle: cycle, fusionIndex: fusionIndex, store: store, narrative: dayNarrative, isNarrativeLoading: dayNarrativeLoading)
        case .evening:
            TodayEveningPanel(cycle: cycle, store: store, narrative: eveningNarrative, isNarrativeLoading: eveningNarrativeLoading)
        }
    }
}

private struct TodayGuidePanel: View {
    let cycle: TodayCycle
    let fusionIndex: FusionIndex?
    let fusionHistory: [FusionIndex]
    let store: TodayFlowStore
    let guideNarrative: TodayNarrativeResponse?
    let spheresNarrative: TodayNarrativeResponse?
    let isGuideLoading: Bool
    let isSpheresLoading: Bool
    @Binding var tarotSelection: Int?
    @Binding var tarotRevealed: Bool

    @State private var guideStep2Expanded = false
    @State private var guideDeepExpanded = false

    private let deckCount = 6

    /// O9: первый пункт — `best_move` / первый `action_option` / первый `do_item`; дальше до трёх строк без дубля.
    private var guideExecutionDoItems: [String] {
        let api = guideNarrative?.payload.narrativeStringArray("do_items") ?? []
        let fallbacks = fallbackDoItems
        let base = api.isEmpty ? fallbacks : api
        let trimmed = TodayGuideActionable.guideCanonicalPrimaryStepLine(
            payload: guideNarrative?.payload,
            doItems: base,
            fallback: TodayShellCopy.shellExecutionDoFallback1
        ).trimmingCharacters(in: .whitespacesAndNewlines)
        let effective = trimmed.isEmpty
            ? (base.first { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty } ?? TodayShellCopy.shellExecutionDoFallback1)
            : trimmed
        func norm(_ s: String) -> String {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            return t.replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
        }
        let nCanon = norm(effective)
        var rest = base.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        rest.removeAll { norm($0) == nCanon }
        var out: [String] = [effective]
        out.append(contentsOf: rest.prefix(2))
        return Array(out.prefix(3))
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            TodaySectionIntro(
                title: TodayShellCopy.guidePanelIntroTitle,
                text: TodayShellCopy.guidePanelIntroBody
            )

            TodayGuideNarrativeHero(
                cycle: cycle,
                narrative: guideNarrative,
                isLoading: isGuideLoading,
                fusionIndex: fusionIndex
            )

            DisclosureGroup(isExpanded: $guideStep2Expanded) {
                VStack(alignment: .leading, spacing: 16) {
                    TodayExecutionLoopSection(
                        store: store,
                        cycle: cycle,
                        doItems: guideExecutionDoItems,
                        avoidItems: guideNarrative?.payload.narrativeStringArray("avoid_items") ?? fallbackAvoidItems
                    )

                    TarotDrawSection(
                        cardName: cycle.morning?.tarotCard?.name ?? TodayShellCopy.shellTarotCardPreparing,
                        dateISO: cycle.date,
                        numerologyTitle: numerologyTitle,
                        selectedIndex: $tarotSelection,
                        isRevealed: $tarotRevealed,
                        deckCount: deckCount
                    )

                    TarotResonanceSection(
                        store: store,
                        currentValue: store.today.ritualFeedback
                    )
                }
                .padding(.top, 4)
            } label: {
                Text(TodayShellCopy.guideStepTwoDisclosureLabel)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            .tint(TodayFlowTheme.sunset)

            DisclosureGroup(isExpanded: $guideDeepExpanded) {
                VStack(alignment: .leading, spacing: 16) {
                    TodayFitSection(cycle: cycle, fusionIndex: fusionIndex, history: fusionHistory)

                    EnergySignatureSection(fusionIndex: fusionIndex, history: fusionHistory)

                    TodayWeekRhythmSection(cycle: cycle, fusionIndex: fusionIndex)

                    TodayAdaptiveStack(spacing: 12) {
                        TodayGuideInfoCard(
                            title: TodayShellCopy.shellGuideDayAxisTitle,
                            text: cycle.morning?.dailyHoroscope?.spine?.dayAxis ?? TodayShellCopy.shellGuideDayAxisFallback
                        )
                        TodayGuideInfoCard(
                            title: TodayShellCopy.shellGuideSupportsTitle,
                            text: cycle.morning?.dailyRecommendations?.whatToDo ?? cycle.consistency?.doFocus ?? TodayShellCopy.shellGuideSupportsFallback
                        )
                    }

                    TodayGuideProgressSection(cycle: cycle)

                    TodayGuideNextStepSection(cycle: cycle, narrative: guideNarrative)

                    TodayLifeSpheresPreviewSection(
                        payload: spheresNarrative?.payload,
                        isLoading: isSpheresLoading
                    )

                    if !fusionHistory.isEmpty {
                        TodayTrendInsightSection(history: fusionHistory)
                    }
                }
                .padding(.top, 8)
            } label: {
                Text(TodayShellCopy.guideStepThreeDisclosureLabel)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            .tint(TodayFlowTheme.sunset)
        }
        .modifier(TodayPanelShell())
    }

    private var numerologyTitle: String {
        if let title = cycle.morning?.numerologyNumber?.title, !title.isEmpty {
            return title
        }
        if let value = cycle.morning?.numerologyNumber?.value ?? cycle.morning?.numerologyNumber?.reducedValue {
            return TodayShellCopy.formatNumerologyValue(value)
        }
        return TodayShellCopy.shellNumerologyGathering
    }

    private var fallbackDoItems: [String] {
        [
            cycle.morning?.dailyRecommendations?.whatToDo,
            cycle.morning?.dailyHoroscope?.spine?.firstMove,
            cycle.consistency?.doFocus
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
    }

    private var fallbackAvoidItems: [String] {
        [
            cycle.morning?.dailyRecommendations?.whatToAvoid,
            cycle.morning?.dailyHoroscope?.spine?.doNotEnter,
            cycle.consistency?.avoidFocus
        ]
        .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
        .filter { !$0.isEmpty }
    }
}

private struct TodayGuideNextStepSection: View {
    let cycle: TodayCycle
    let narrative: TodayNarrativeResponse?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellNextStepSectionTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            TodayAdaptiveStack(spacing: 12) {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellNextStepDoTitle,
                    text: nextAction
                )
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellNextStepWhyTitle,
                    text: nextMessage
                )
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var nextAction: String {
        narrative?.payload.narrativeString("next_action")
        ?? cycle.morning?.dailyHoroscope?.spine?.firstMove
        ?? TodayShellCopy.shellNextStepActionFallback
    }

    private var nextMessage: String {
        cycle.morning?.dailyHoroscope?.spine?.bestMode
        ?? narrative?.payload.narrativeString("subline")
        ?? TodayShellCopy.nextStepWhyFallback
    }
}

private struct TodayFitSection: View {
    let cycle: TodayCycle
    let fusionIndex: FusionIndex?
    let history: [FusionIndex]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayShellCopy.shellFitSectionTitle)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(lead)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
                if let strongestAxis {
                    TodayAxisCapsule(
                        title: TodayShellCopy.shellFitStrongerAxisLabel,
                        value: strongestAxis.title,
                        tint: tint(for: strongestAxis)
                    )
                }
            }

            TodayAdaptiveStack(spacing: 12) {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellFitBestModeTitle,
                    text: cycle.morning?.dailyHoroscope?.spine?.bestMode ?? TodayShellCopy.shellFitBestModeFallback
                )
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellFitFragileAxisTitle,
                    text: weakAxisText
                )
            }

            if !history.isEmpty {
                HStack(spacing: 8) {
                    ForEach(FusionAxis.allCases) { axis in
                        TodayDeltaChip(
                            title: axis.title,
                            delta: history.scoreDelta(for: axis),
                            tint: tint(for: axis)
                        )
                    }
                }
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var lead: String {
        if let profilePrism = cycle.morning?.dailyHoroscope?.profilePrism, !profilePrism.isEmpty {
            return profilePrism
        }
        if let fusionIndex {
            return fusionIndex.encouragement
        }
        return TodayShellCopy.shellFitLeadFallback
    }

    private var strongestAxis: FusionAxis? {
        history.strongestAxis ?? fusionIndex.flatMap { scores in
            FusionAxis.allCases.max { lhs, rhs in
                scores.scores.value(for: lhs) < scores.scores.value(for: rhs)
            }
        }
    }

    private var weakestAxis: FusionAxis? {
        history.weakestAxis ?? fusionIndex.flatMap { scores in
            FusionAxis.allCases.min { lhs, rhs in
                scores.scores.value(for: lhs) < scores.scores.value(for: rhs)
            }
        }
    }

    private var weakAxisText: String {
        if let weakestAxis {
            let base = cycle.morning?.dailyHoroscope?.spine?.mainRisk ?? history.repeatedRiskPattern ?? ""
            return TodayShellCopy.formatWeakAxisLine(weakestAxisTitle: weakestAxis.title, base: base)
        }
        return cycle.morning?.dailyHoroscope?.spine?.mainRisk ?? TodayShellCopy.shellFitWeakAxisRiskFallback
    }

    private func tint(for axis: FusionAxis) -> Color {
        switch axis {
        case .energy:
            return TodayFlowTheme.sunset
        case .emotionalBalance:
            return TodayFlowTheme.moss
        case .focus:
            return TodayFlowTheme.twilight
        }
    }
}

private struct TodayGuideNarrativeHero: View {
    let cycle: TodayCycle
    let narrative: TodayNarrativeResponse?
    let isLoading: Bool
    let fusionIndex: FusionIndex?

    private var dayEngineBrief: TodayGuideActionable.DayEngineBriefDisplay? {
        TodayGuideActionable.dayEngineBriefDisplay(from: narrative?.payload)
    }

    private var dayModelBrief: TodayGuideActionable.DayModelBriefDisplay? {
        TodayGuideActionable.dayModelBriefDisplay(from: narrative?.payload)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(TodayShellCopy.guideHeroEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .textCase(.uppercase)
                .tracking(0.6)

            if isLoading && narrative == nil {
                ProgressView(TodayShellCopy.loadingGuideHero)
                    .tint(TodayFlowTheme.sunset)
            }

            Text(headline)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sunset)
            Text(subline)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                .lineLimit(5)
                .fixedSize(horizontal: false, vertical: true)

            TodayDayLogicCallout(style: .guideHero, engine: dayEngineBrief, model: dayModelBrief)

            TodayAdaptiveStack(spacing: 12) {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellNarrativeHeroEnergyTitle,
                    text: narrative?.payload.narrativeString("energy_line")
                    ?? fusionIndex.map {
                        "\(TodayRitualCopy.rhythmTierLabel(score: $0.scores.energy)). \($0.encouragement)"
                    }
                    ?? TodayShellCopy.guideEnergyLineFallback
                )
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellNarrativeHeroRiskTitle,
                    text: narrative?.payload.narrativeString("risk_detail")
                    ?? cycle.morning?.dailyHoroscope?.spine?.mainRisk
                    ?? TodayShellCopy.shellNarrativeHeroRiskFallback
                )
            }
        }
        .padding(20)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
    }

    private var headline: String {
        narrative?.payload.narrativeString("headline")
        ?? cycle.morning?.dailyHoroscope?.headline
        ?? cycle.morning?.dailyHoroscope?.spine?.bestMode
        ?? TodayShellCopy.shellNarrativeHeadlineFallback
    }

    private var subline: String {
        narrative?.payload.narrativeString("subline")
        ?? cycle.morning?.dailyForecastSummary?.summary
        ?? cycle.morning?.dailyHoroscope?.profilePrism
        ?? TodayShellCopy.shellNarrativeSublineFallback
    }
}

private struct TodayExecutionLoopSection: View {
    let store: TodayFlowStore
    let cycle: TodayCycle
    let doItems: [String]
    let avoidItems: [String]
    @State private var pendingExecutionAction: String?
    @State private var pendingAvoidAction: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellExecutionFocusHeading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            VStack(spacing: 10) {
                ForEach(primaryActions.indices, id: \.self) { index in
                    loopActionCard(
                        title: primaryActions[index],
                        tint: TodayFlowTheme.sunset,
                        index: index + 1,
                        isChecked: executionKeys.contains(actionKey(for: primaryActions[index])),
                        isDisabled: store.isSaving && pendingExecutionAction == primaryActions[index]
                    )
                    .onTapGesture {
                        let title = primaryActions[index]
                        let nextValue = !executionKeys.contains(actionKey(for: title))
                        pendingExecutionAction = title
                        Task {
                            await store.toggleTrackerExecutionAction(title, completed: nextValue)
                            await MainActor.run {
                                pendingExecutionAction = nil
                            }
                        }
                    }
                }
            }

            Text(TodayShellCopy.shellExecutionAvoidHeading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
                .padding(.top, 4)

            VStack(spacing: 10) {
                ForEach(avoidLines.indices, id: \.self) { index in
                    loopActionCard(
                        title: avoidLines[index],
                        tint: TodayFlowTheme.roseClay,
                        index: index + 1,
                        isChecked: avoidKeys.contains(actionKey(for: avoidLines[index])),
                        isDisabled: store.isSaving && pendingAvoidAction == avoidLines[index]
                    )
                    .onTapGesture {
                        let title = avoidLines[index]
                        let nextValue = !avoidKeys.contains(actionKey(for: title))
                        pendingAvoidAction = title
                        Task {
                            await store.toggleTrackerAvoidAction(title, respected: nextValue)
                            await MainActor.run {
                                pendingAvoidAction = nil
                            }
                        }
                    }
                }
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var primaryActions: [String] {
        let items = doItems.filter { !$0.isEmpty }
        if !items.isEmpty { return Array(items.prefix(3)) }
        return [
            cycle.morning?.dailyRecommendations?.whatToDo ?? TodayShellCopy.shellExecutionDoFallback1,
            cycle.morning?.dailyHoroscope?.spine?.firstMove ?? TodayShellCopy.shellExecutionDoFallback2,
            cycle.consistency?.doFocus ?? TodayShellCopy.shellExecutionDoFallback3
        ]
    }

    private var avoidLines: [String] {
        let items = avoidItems.filter { !$0.isEmpty }
        if !items.isEmpty { return Array(items.prefix(2)) }
        return [
            cycle.morning?.dailyRecommendations?.whatToAvoid ?? TodayShellCopy.shellExecutionAvoidFallback1,
            cycle.morning?.dailyHoroscope?.spine?.doNotEnter ?? TodayShellCopy.shellExecutionAvoidFallback2
        ]
    }

    private var executionKeys: Set<String> {
        Set(store.today.completedExecutionActions)
    }

    private var avoidKeys: Set<String> {
        Set(store.today.respectedAvoidActions)
    }

    private func loopActionCard(title: String, tint: Color, index: Int, isChecked: Bool, isDisabled: Bool) -> some View {
        HStack(alignment: .top, spacing: 12) {
            ZStack {
                Circle()
                    .fill(tint.opacity(0.14))
                    .frame(width: 28, height: 28)
                Text("\(index)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(tint)
            }

            Text(title)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink)

            Spacer()

            Image(systemName: isChecked ? "checkmark.circle.fill" : "circle")
                .font(.title3)
                .foregroundStyle(isChecked ? tint : TodayFlowTheme.ink.opacity(0.22))
        }
        .padding(14)
        .background(Color.white.opacity(0.62))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .opacity(isDisabled ? 0.72 : 1)
    }

    private func actionKey(for title: String) -> String {
        let lowered = title
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        let scalars = lowered.unicodeScalars.map { scalar -> Character in
            CharacterSet.alphanumerics.contains(scalar) ? Character(scalar) : "-"
        }
        return String(scalars)
            .replacingOccurrences(of: "--+", with: "-", options: .regularExpression)
            .trimmingCharacters(in: CharacterSet(charactersIn: "-"))
    }
}

private struct TarotResonanceSection: View {
    let store: TodayFlowStore
    let currentValue: String?

    @State private var isSaving = false
    @State private var statusMessage: String?

    private let options = [
        ("yes", TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerYes),
        ("partial", TodayShellCopy.shellTarotResonancePartial),
        ("no", TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerNo)
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellTarotResonanceTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            HStack(spacing: 10) {
                ForEach(options, id: \.0) { option in
                    Button {
                        save(option.0)
                    } label: {
                        Text(option.1)
                            .font(.subheadline.weight(.semibold))
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(buttonBackground(for: option.0))
                            .foregroundStyle(buttonForeground(for: option.0))
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    }
                    .buttonStyle(.plain)
                    .disabled(isSaving)
                }
            }

            if let currentValue, !currentValue.isEmpty {
                Text(feedbackLabel(for: currentValue))
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func feedbackLabel(for raw: String) -> String {
        let key = raw.lowercased()
        if let match = options.first(where: { $0.0 == key }) {
            return match.1
        }
        return raw
    }

    private func save(_ value: String) {
        isSaving = true
        statusMessage = nil

        Task {
            await store.saveTrackerRitualFeedback(value)
            await MainActor.run {
                isSaving = false
                statusMessage = TodayShellCopy.shellTarotResonanceSaved
            }
        }
    }

    private func buttonBackground(for value: String) -> Color {
        currentValue == value ? TodayFlowTheme.accent : Color.white.opacity(0.62)
    }

    private func buttonForeground(for value: String) -> Color {
        currentValue == value ? .white : TodayFlowTheme.ink
    }
}

private struct TodayGuideActionSection: View {
    let doItems: [String]
    let avoidItems: [String]

    var body: some View {
        TodayAdaptiveStack(spacing: 12) {
            TodayListCard(
                title: TodayShellCopy.shellListDoTitle,
                items: doItems.isEmpty ? [TodayShellCopy.shellListDoFallback] : doItems,
                tint: TodayFlowTheme.sunset
            )
            TodayListCard(
                title: TodayShellCopy.shellListAvoidTitle,
                items: avoidItems.isEmpty ? [TodayShellCopy.shellListAvoidFallback] : avoidItems,
                tint: TodayFlowTheme.roseClay
            )
        }
    }
}

private struct TodayGuideProgressSection: View {
    let cycle: TodayCycle

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            let steps = stepItems
            let completed = steps.filter(\.done).count
            let progress = Int((Double(completed) / Double(max(steps.count, 1))) * 100)

            Text(TodayShellCopy.shellDayProgressHeading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Text(TodayShellCopy.formatDayProgressBullets(percent: progress, completed: completed, total: steps.count))
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sunset)

            TodayFlowSphereSliderTrack(
                value: progress,
                tint: TodayFlowTheme.sunset,
                accessibilityTitle: TodayShellCopy.shellDayProgressHeading,
                density: .compact
            )

            HStack(spacing: 10) {
                ForEach(stepItems, id: \.title) { item in
                    VStack(alignment: .leading, spacing: 6) {
                        Text(item.done ? TodayShellCopy.shellDayProgressStepDone : TodayShellCopy.shellDayProgressStepNext)
                            .font(.caption2.weight(.bold))
                            .foregroundStyle(item.done ? TodayFlowTheme.moss : TodayFlowTheme.sand)
                        Text(item.title)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.56))
                    .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var stepItems: [(title: String, done: Bool)] {
        [
            (TodayShellCopy.shellProgressPhaseTodayComplete, true),
            (TodayWebFlowTabsCopy.todayFlowTabMorningLabel, cycle.morningCompleted),
            (TodayWebFlowTabsCopy.todayFlowTabDayLabel, cycle.dayCompleted),
            (TodayWebFlowTabsCopy.todayFlowTabEveningLabel, cycle.eveningCompleted)
        ]
    }
}

private struct TodayLifeSpheresPreviewSection: View {
    let payload: [String: JSONValue]?
    let isLoading: Bool
    @State private var expandedTitle: String? = TodayShellCopy.shellSphereLoveTitle

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayShellCopy.lifeSpheresSectionTitle)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(TodayShellCopy.lifeSpheresSubtitle)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
                if isLoading && payload == nil {
                    ProgressView()
                        .tint(TodayFlowTheme.sunset)
                }
            }

            VStack(spacing: 10) {
                ForEach(items, id: \.title) { item in
                    let isExpanded = expandedTitle == item.title
                    VStack(alignment: .leading, spacing: 0) {
                        Button {
                            withAnimation(.spring(response: 0.34, dampingFraction: 0.86)) {
                                expandedTitle = isExpanded ? nil : item.title
                            }
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(item.title)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(item.tint)
                                    Text(isExpanded ? TodayShellCopy.shellSphereForecastCollapse : TodayShellCopy.shellSphereForecastExpand)
                                        .font(.caption2)
                                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                                }
                                Spacer()
                                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.56))
                            }
                        }
                        .buttonStyle(.plain)

                        if isExpanded {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(item.text)
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            .padding(.top, 8)
                            .transition(.opacity.combined(with: .move(edge: .top)))
                        }
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .topLeading)
                    .background(
                        LinearGradient(
                            colors: isExpanded
                            ? [Color.white.opacity(0.9), TodayFlowTheme.paper.opacity(0.82)]
                            : [Color.white.opacity(0.62), TodayFlowTheme.paper.opacity(0.56)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .stroke(isExpanded ? item.tint.opacity(0.44) : TodayFlowTheme.gold.opacity(0.14), lineWidth: 1)
                    }
                    .shadow(color: isExpanded ? item.tint.opacity(0.14) : .clear, radius: 14, y: 6)
                }
            }
        }
        .padding(18)
        .background(
            LinearGradient(
                colors: [TodayFlowTheme.paper.opacity(0.95), Color.white.opacity(0.72)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.18), lineWidth: 1)
        }
    }

    private var items: [(title: String, text: String, tint: Color)] {
        let fallback = [
            (TodayShellCopy.shellSphereLoveTitle, TodayShellCopy.shellSphereLoveFallback, TodayFlowTheme.roseClay),
            (TodayShellCopy.shellSphereMoneyTitle, TodayShellCopy.shellSphereMoneyFallback, TodayFlowTheme.gold),
            (TodayShellCopy.shellSphereWorkTitle, TodayShellCopy.shellSphereWorkFallback, TodayFlowTheme.twilight),
            (TodayShellCopy.shellSphereFamilyTitle, TodayShellCopy.shellSphereFamilyFallback, TodayFlowTheme.moss)
        ]
        guard let payload else { return fallback }
        let keys = [
            (TodayShellCopy.shellSphereLoveTitle, ["love", "love_summary", "love_focus"], TodayFlowTheme.roseClay),
            (TodayShellCopy.shellSphereMoneyTitle, ["money", "money_summary", "money_focus"], TodayFlowTheme.gold),
            (TodayShellCopy.shellSphereWorkTitle, ["career", "career_summary", "career_focus"], TodayFlowTheme.twilight),
            (TodayShellCopy.shellSphereFamilyTitle, ["family", "family_summary", "family_focus"], TodayFlowTheme.moss)
        ]
        return keys.map { title, candidates, tint in
            let text = candidates.compactMap { payload.narrativeString($0) }.first ?? fallback.first(where: { $0.0 == title })!.1
            return (title, text, tint)
        }
    }
}

private struct TodayListCard: View {
    let title: String
    let items: [String]
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(tint)

            ForEach(items.prefix(3), id: \.self) { item in
                HStack(alignment: .top, spacing: 8) {
                    Circle()
                        .fill(tint)
                        .frame(width: 6, height: 6)
                        .padding(.top, 6)
                    Text(item)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct TodayMorningPanel: View {
    let cycle: TodayCycle
    let profile: BirthProfile?
    let store: TodayFlowStore
    let narrative: TodayNarrativeResponse?
    let isNarrativeLoading: Bool

    @State private var morningCoreExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            TodaySectionIntro(
                title: TodayShellCopy.morningPanelIntroTitle,
                text: TodayShellCopy.morningPanelIntroBody
            )

            TodayAdaptiveStack(spacing: 12) {
                TodayMetricTile(
                    title: TodayShellCopy.shellMorningDayModeTitle,
                    value: cycle.morning?.dailyHoroscope?.spine?.bestMode ?? TodayShellCopy.shellMorningDayModeFallback,
                    caption: TodayShellCopy.shellMorningDayModeCaption
                )
                TodayMetricTile(
                    title: TodayShellCopy.profileTileTitle,
                    value: profileSummary,
                    caption: TodayShellCopy.profileTileCaption
                )
            }

            if isNarrativeLoading && narrative == nil {
                ProgressView(TodayShellCopy.loadingMorningNarrative)
                    .tint(TodayFlowTheme.sunset)
            } else if let payload = narrative?.payload {
                TodayPromptNarrativeCard(
                    title: payload.narrativeString("headline") ?? TodayShellCopy.shellMorningNarrativeHeadlineFallback,
                    text: payload.narrativeString("subline")
                    ?? payload.narrativeString("day_question")
                    ?? TodayShellCopy.narrativeFallbackMorning,
                    bodyLineLimit: 6
                )
            }

            DisclosureGroup(isExpanded: $morningCoreExpanded) {
                TodayMorningCoreSection(cycle: cycle)
            } label: {
                Text(TodayShellCopy.morningStepTwoDisclosureLabel)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            .tint(TodayFlowTheme.sunset)

            TodayMorningComposer(store: store, cycle: cycle)
        }
        .modifier(TodayPanelShell())
    }

    private var profileSummary: String {
        let parts = [
            cycle.coreProfile?.sunSign ?? profile?.sunSign,
            profile?.moonSign,
            profile?.risingSign
        ].compactMap { $0 }.filter { !$0.isEmpty }

        return parts.isEmpty ? TodayShellCopy.shellProfileBuilding : parts.joined(separator: " · ")
    }
}

private struct TodayDayPanel: View {
    let cycle: TodayCycle
    let fusionIndex: FusionIndex?
    let store: TodayFlowStore
    let narrative: TodayNarrativeResponse?
    let isNarrativeLoading: Bool

    @State private var dayDetailsExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            TodaySectionIntro(
                title: TodayShellCopy.dayPanelIntroTitle,
                text: TodayShellCopy.dayPanelIntroBody
            )

            if let fusionIndex {
                DayEnergyRibbonSection(fusionIndex: fusionIndex)
            }

            TodayFocusProgressSection(store: store, cycle: cycle)

            if isNarrativeLoading && narrative == nil {
                ProgressView(TodayShellCopy.loadingDayNarrative)
                    .tint(TodayFlowTheme.sunset)
            } else if let payload = narrative?.payload {
                TodayWorkingLayerSection(payload: payload)
                DisclosureGroup(isExpanded: $dayDetailsExpanded) {
                    TodayDayNarrativeDetailsSection(payload: payload)
                } label: {
                    Text(TodayShellCopy.dayStepTwoDisclosureLabel)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                }
                .tint(TodayFlowTheme.sunset)
            }

            TodayQuickAnswerSection(store: store, cycle: cycle)
            TodayPulseCheckComposer(store: store, cycle: cycle)
            TodayJournalComposer(store: store, cycle: cycle)

            if !cycle.dayJournalEntries.isEmpty {
                TodayRecentJournalSection(entries: Array(cycle.dayJournalEntries.prefix(3)))
            }
        }
        .modifier(TodayPanelShell())
    }
}

private struct TodayEveningPanel: View {
    let cycle: TodayCycle
    let store: TodayFlowStore
    let narrative: TodayNarrativeResponse?
    let isNarrativeLoading: Bool

    @State private var eveningDetailsExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            TodaySectionIntro(
                title: TodayShellCopy.eveningPanelIntroTitle,
                text: TodayShellCopy.eveningPanelIntroBody
            )

            if let phrase = cycle.evening?.closingPhraseText, !phrase.isEmpty {
                TodayGuideInfoCard(title: TodayShellCopy.shellEveningClosingToneTitle, text: phrase)
            }

            if isNarrativeLoading && narrative == nil {
                ProgressView(TodayShellCopy.loadingEveningNarrative)
                    .tint(TodayFlowTheme.sunset)
            } else if let payload = narrative?.payload {
                TodayPromptNarrativeCard(
                    title: payload.narrativeString("headline") ?? TodayShellCopy.shellEveningNarrativeHeadlineFallback,
                    text: payload.narrativeString("subline")
                    ?? payload.narrativeString("closing_prompt")
                    ?? TodayShellCopy.narrativeFallbackEvening,
                    bodyLineLimit: 6
                )
                DisclosureGroup(isExpanded: $eveningDetailsExpanded) {
                    TodayEveningNarrativeDetailsSection(payload: payload)
                } label: {
                    Text(TodayShellCopy.eveningStepTwoDisclosureLabel)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                }
                .tint(TodayFlowTheme.sunset)
            }

            if let morningIntention = cycle.dayConnection?.morningIntention, !morningIntention.isEmpty {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellEveningMorningLinkTitle,
                    text: TodayShellCopy.formatMorningIntentionRecall(intention: morningIntention)
                )
            }

            TodayEveningComposer(store: store, cycle: cycle)
        }
        .modifier(TodayPanelShell())
    }
}

private struct TodayMorningCoreSection: View {
    let cycle: TodayCycle

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellMorningCoreTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            TodayAdaptiveStack(spacing: 12) {
                TodayMetricTile(
                    title: TodayShellCopy.shellTarotCardDayTitle,
                    value: cycle.morning?.tarotCard?.name ?? TodayShellCopy.shellCoreGathering,
                    caption: TodayShellCopy.shellTarotCardCaption
                )
                TodayMetricTile(
                    title: TodayShellCopy.shellNumerologyDayTitle,
                    value: numerologyValue,
                    caption: TodayShellCopy.shellNumerologyCaption
                )
            }

            if let forecast = cycle.morning?.dailyForecastSummary?.summary, !forecast.isEmpty {
                TodayGuideInfoCard(title: TodayShellCopy.shellForecastShortTitle, text: forecast)
            }

            TodayAdaptiveStack(spacing: 12) {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellWhatSupportsDayTitle,
                    text: cycle.morning?.dailyRecommendations?.whatToDo ?? cycle.morning?.dailyHoroscope?.spine?.firstMove ?? TodayShellCopy.shellWhatSupportsFallback
                )
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellWhatNotAmplifyTitle,
                    text: cycle.morning?.dailyRecommendations?.whatToAvoid ?? cycle.morning?.dailyHoroscope?.spine?.doNotEnter ?? TodayShellCopy.shellWhatNotAmplifyFallback
                )
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var numerologyValue: String {
        if let title = cycle.morning?.numerologyNumber?.title, !title.isEmpty {
            return title
        }
        if let value = cycle.morning?.numerologyNumber?.value ?? cycle.morning?.numerologyNumber?.reducedValue {
            return TodayShellCopy.formatNumerologyValue(value)
        }
        return TodayShellCopy.shellCoreGathering
    }
}

private struct TarotDrawSection: View {
    let cardName: String
    let dateISO: String
    let numerologyTitle: String
    @Binding var selectedIndex: Int?
    @Binding var isRevealed: Bool
    let deckCount: Int
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            TodayAdaptiveStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayShellCopy.shellTarotDaySectionTitle)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                }
                Spacer()
                Text(numerologyTitle)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.white.opacity(0.6))
                    .clipShape(Capsule())
            }

            if selectedIndex != nil && isRevealed {
                Button(TodayShellCopy.shellTarotAgainCta) {
                    withAnimation(.spring(response: 0.34, dampingFraction: 0.88)) {
                        isRevealed = false
                        selectedIndex = nil
                    }
                }
                .buttonStyle(.bordered)
                .tint(TodayFlowTheme.twilight)
            }

            ZStack {
                Circle()
                    .fill(TodayFlowTheme.sunset.opacity(0.10))
                    .frame(width: 230, height: 230)
                    .blur(radius: 8)
                    .opacity(selectedIndex == nil ? 0.6 : 1.0)
                ForEach(0..<deckCount, id: \.self) { index in
                    TarotBackCard(
                        isSelected: selectedIndex == index,
                        reveal: selectedIndex == index && isRevealed,
                        cardName: cardName,
                        dateISO: dateISO,
                        compact: horizontalSizeClass == .compact
                    )
                    .rotationEffect(.degrees(Double(index - deckCount / 2) * 7))
                    .offset(x: selectedIndex == index ? 0 : CGFloat(index - deckCount / 2) * (horizontalSizeClass == .compact ? 12 : 18), y: selectedIndex == index ? -10 : 0)
                    .scaleEffect(selectedIndex == index ? 1.0 : (horizontalSizeClass == .compact ? 0.86 : 0.94))
                    .zIndex(selectedIndex == index ? 10 : Double(index))
                    .onTapGesture {
                        guard selectedIndex == nil else { return }
                        RitualHaptics.light()
                        withAnimation(.spring(response: 0.46, dampingFraction: 0.8)) {
                            selectedIndex = index
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.42) {
                            RitualHaptics.medium()
                            withAnimation(.spring(response: 0.54, dampingFraction: 0.84)) {
                                isRevealed = true
                            }
                        }
                    }
                    .accessibilityLabel(selectedIndex == index && isRevealed ? TodayShellCopy.formatTarotA11yOpenCard(cardName: cardName) : TodayShellCopy.shellTarotA11yClosedCard)
                }
            }
            .frame(height: horizontalSizeClass == .compact ? 260 : 300)
            .padding(.horizontal, horizontalSizeClass == .compact ? 0 : 10)
            .padding(.vertical, 16)
            .background(
                LinearGradient(
                    colors: [Color.white.opacity(0.8), TodayFlowTheme.paper.opacity(0.68)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))

            if selectedIndex != nil && isRevealed {
                Text(TodayShellCopy.formatTarotDayLine(cardName: cardName))
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
            } else {
                Text(TodayShellCopy.shellTarotPickCardHint)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.56))
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TarotBackCard: View {
    let isSelected: Bool
    let reveal: Bool
    let cardName: String
    let dateISO: String
    let compact: Bool

    private var deckImageId: Int {
        TodayTarotTodayRuCatalog.deckImageIdForDay(apiCardName: cardName, dateISO: dateISO)
    }

    private var cardWidth: CGFloat {
        let unsel: CGFloat = compact ? 96 : 112
        let sel: CGFloat = compact ? 168 : 188
        return isSelected ? sel : unsel
    }

    private var cardHeight: CGFloat {
        TodayTarotDeckImageURLs.cardDisplayHeight(width: cardWidth)
    }

    private var cardCorner: CGFloat {
        min(18, max(10, cardWidth * 0.09))
    }

    var body: some View {
        ZStack {
            cardBack
                .opacity(reveal ? 0 : 1)

            cardFront
                .opacity(reveal ? 1 : 0)
                .rotation3DEffect(.degrees(180), axis: (x: 0, y: 1, z: 0))
        }
        .frame(width: cardWidth, height: cardHeight)
        .rotation3DEffect(.degrees(reveal ? 180 : 0), axis: (x: 0, y: 1, z: 0))
        .shadow(color: Color.black.opacity(0.12), radius: isSelected ? 22 : 12, y: 10)
        .overlay {
            if isSelected {
                RoundedRectangle(cornerRadius: cardCorner, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(reveal ? 0.55 : 0.22), lineWidth: reveal ? 2 : 1)
            }
        }
    }

    private var cardBack: some View {
        AsyncImage(url: TodayTarotDeckImageURLs.cardBackURL()) { phase in
            switch phase {
            case .success(let image):
                ZStack {
                    Color(red: 0.98, green: 0.96, blue: 0.93)
                    image
                        .resizable()
                        .scaledToFit()
                }
            case .failure:
                cardBackFallback
            case .empty:
                cardBackFallback
                    .overlay { ProgressView().tint(.white) }
            @unknown default:
                cardBackFallback
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: cardCorner, style: .continuous))
    }

    private var cardBackFallback: some View {
        RoundedRectangle(cornerRadius: cardCorner, style: .continuous)
            .fill(
                LinearGradient(
                    colors: [TodayFlowTheme.twilight.opacity(0.92), TodayFlowTheme.ember.opacity(0.72)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .overlay {
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
            }
    }

    @ViewBuilder
    private var cardFront: some View {
        if let faceURL = TodayTarotDeckImageURLs.deckFaceURL(cardId: deckImageId) {
            AsyncImage(url: faceURL) { phase in
                switch phase {
                case .success(let image):
                    ZStack {
                        Color(red: 0.98, green: 0.96, blue: 0.93)
                        image
                            .resizable()
                            .scaledToFit()
                    }
                case .failure:
                    cardFrontFallback
                case .empty:
                    cardFrontFallback
                        .overlay { ProgressView().tint(.white) }
                @unknown default:
                    cardFrontFallback
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: cardCorner, style: .continuous))
        } else {
            cardFrontFallback
        }
    }

    private var cardFrontFallback: some View {
        RoundedRectangle(cornerRadius: cardCorner, style: .continuous)
            .fill(
                LinearGradient(
                    colors: [TodayFlowTheme.sunset, TodayFlowTheme.gold.opacity(0.82), TodayFlowTheme.twilight.opacity(0.9)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .overlay {
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .stroke(Color.white.opacity(0.32), lineWidth: 1)
            }
            .overlay {
                VStack(spacing: compact ? 8 : 10) {
                    Text(TodayShellCopy.shellTarotCardDayTitle)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.paper.opacity(0.92))
                    Text(cardName)
                        .font(.system(size: compact ? 18 : 22, weight: .bold, design: .rounded))
                        .foregroundStyle(Color.white)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, compact ? 10 : 14)
                }
            }
    }
}

private struct EnergySignatureSection: View {
    let fusionIndex: FusionIndex?
    let history: [FusionIndex]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayShellCopy.shellEnergyStateSectionTitle)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(heading)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
                if let fusionIndex {
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
            }

            TodayAdaptiveStack(spacing: 12) {
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbEnergy, value: fusionIndex?.scores.energy ?? 0, tint: TodayFlowTheme.sunset)
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbBalance, value: fusionIndex?.scores.emotionalBalance ?? 0, tint: TodayFlowTheme.moss)
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbFocus, value: fusionIndex?.scores.focus ?? 0, tint: TodayFlowTheme.twilight)
            }

            if let fusionIndex {
                ProfileEnergyWave(scores: fusionIndex.scores)
            }

            if let insight = historyInsight {
                Text(insight)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var heading: String {
        guard let fusionIndex else {
            return TodayShellCopy.shellEnergySignatureEmpty
        }
        return fusionIndex.encouragement
    }

    private var historyInsight: String? {
        guard history.count > 1 else { return nil }
        return history.overallTrendHeadline
    }
}

private struct ProfileEnergyWave: View {
    let scores: FusionScores

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(Array(waves.enumerated()), id: \.offset) { _, wave in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(wave.title)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.85))
                        Spacer(minLength: 8)
                        Text("\(wave.value)")
                            .font(.caption.weight(.bold))
                            .monospacedDigit()
                            .foregroundStyle(wave.tint)
                    }
                    TodayFlowSphereSliderTrack(
                        value: wave.value,
                        tint: wave.tint,
                        accessibilityTitle: wave.title,
                        density: .compact
                    )
                }
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var waves: [(title: String, value: Int, tint: Color)] {
        [
            (TodayShellCopy.shellFusionOrbEnergy, scores.energy, TodayFlowTheme.sunset),
            (TodayShellCopy.shellFusionOrbBalance, scores.emotionalBalance, TodayFlowTheme.moss),
            (TodayShellCopy.shellFusionOrbFocus, scores.focus, TodayFlowTheme.twilight)
        ]
    }
}

private struct EnergyOrbCard: View {
    let title: String
    let value: Int
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer(minLength: 8)
                Text("\(value)")
                    .font(.caption.weight(.bold))
                    .monospacedDigit()
                    .foregroundStyle(tint)
            }
            TodayFlowSphereSliderTrack(value: value, tint: tint, accessibilityTitle: title)
            VStack(alignment: .leading, spacing: 4) {
                Text(TodayRitualCopy.rhythmTierLabel(score: value))
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
                Text(TodayRitualCopy.heroScoreFootnote(score: value))
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct TodayWeekRhythmSection: View {
    let cycle: TodayCycle
    let fusionIndex: FusionIndex?
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayShellCopy.shellWeekRhythmTitle)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(TodayShellCopy.weekRhythmCalendarSubtitle)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                }
                Spacer()
            }

            if horizontalSizeClass == .compact {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 10) {
                        ForEach(weekDays, id: \.date) { day in
                            dayCell(day)
                                .frame(width: 72)
                        }
                    }
                }
            } else {
                HStack(spacing: 10) {
                    ForEach(weekDays, id: \.date) { day in
                        dayCell(day)
                            .frame(maxWidth: .infinity)
                    }
                }
            }

            if let fusionIndex {
                Text(
                    "\(TodayRitualCopy.rhythmTierLabel(score: fusionIndex.scores.average)) \(TodayRitualCopy.heroScoreFootnote(score: fusionIndex.scores.average)) \(TodayShellCopy.weekRhythmSummaryTail)"
                )
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
            }

            Text(calendarFootnote)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var weekDays: [RhythmDay] {
        guard let base = TodayWeekRhythmSection.dateFormatter.date(from: cycle.date) else { return [] }
        let calendar = Calendar(identifier: .gregorian)
        let weekday = calendar.component(.weekday, from: base)
        let mondayOffset = (weekday + 5) % 7
        guard let start = calendar.date(byAdding: .day, value: -mondayOffset, to: base) else { return [] }

        return (0..<7).compactMap { offset in
            guard let day = calendar.date(byAdding: .day, value: offset, to: start) else { return nil }
            let isCurrent = calendar.isDate(day, inSameDayAs: base)
            return RhythmDay(
                date: day,
                label: TodayWeekRhythmSection.weekdayFormatter.string(from: day).uppercased(),
                dayNumber: TodayWeekRhythmSection.dayNumberFormatter.string(from: day),
                isCurrent: isCurrent,
                morningDone: isCurrent ? cycle.morningCompleted : false,
                dayDone: isCurrent ? cycle.dayCompleted : false,
                eveningDone: isCurrent ? cycle.eveningCompleted : false,
                tempoTitle: isCurrent ? currentTempo : "..."
            )
        }
    }

    private var currentTempo: String {
        if let fusionIndex {
            switch fusionIndex.scores.average {
            case 75...:
                return "full"
            case 55...74:
                return "steady"
            case 35...54:
                return "soft"
            default:
                return "low"
            }
        }

        if cycle.dayCompleted {
            return "done"
        }
        if cycle.morningCompleted {
            return "open"
        }
        return "start"
    }

    private var calendarFootnote: String {
        if cycle.morningCompleted || cycle.dayCompleted || cycle.eveningCompleted {
            return TodayShellCopy.shellWeekCalendarFootnoteActive
        }
        return TodayShellCopy.shellWeekCalendarFootnoteInactive
    }

    private func rhythmMark(isOn: Bool, tint: Color) -> some View {
        Circle()
            .fill(isOn ? tint : Color.black.opacity(0.08))
            .frame(width: 6, height: 6)
    }

    private func dayCell(_ day: RhythmDay) -> some View {
        VStack(spacing: 10) {
            Text(day.label)
                .font(.caption2.weight(.bold))
                .foregroundStyle(day.isCurrent ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.42))

            ZStack {
                Circle()
                    .fill(day.isCurrent ? TodayFlowTheme.sunset.opacity(0.18) : Color.white.opacity(0.54))
                    .frame(width: 44, height: 44)
                if day.isCurrent {
                    Circle()
                        .stroke(TodayFlowTheme.gold.opacity(0.5), lineWidth: 1)
                        .frame(width: 50, height: 50)
                }
                Text(day.dayNumber)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(day.isCurrent ? TodayFlowTheme.sunset : TodayFlowTheme.ink)
            }

            HStack(spacing: 4) {
                rhythmMark(isOn: day.morningDone, tint: TodayFlowTheme.sunset)
                rhythmMark(isOn: day.dayDone, tint: TodayFlowTheme.twilight)
                rhythmMark(isOn: day.eveningDone, tint: TodayFlowTheme.moss)
            }

            Text(day.tempoTitle)
                .font(.caption2)
                .foregroundStyle(day.isCurrent ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.42))
        }
    }

    private struct RhythmDay {
        let date: Date
        let label: String
        let dayNumber: String
        let isCurrent: Bool
        let morningDone: Bool
        let dayDone: Bool
        let eveningDone: Bool
        let tempoTitle: String
    }

    private static let dateFormatter: DateFormatter = {
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

    private static let dayNumberFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.dateFormat = "d"
        return formatter
    }()
}

private struct TodayGuideInfoCard: View {
    let title: String
    let text: String

    var bodyView: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.84))
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(TodayFlowTheme.todaySoftCard)
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    var body: some View { bodyView }
}

private struct TodayTrendInsightSection: View {
    let history: [FusionIndex]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellTrendInsightTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            TodayTrendLine(title: TodayShellCopy.shellTrendLineTrend, text: history.overallTrendHeadline, tint: TodayFlowTheme.sunset)
            TodayTrendLine(title: TodayShellCopy.shellTrendLineRisk, text: history.repeatedRiskPattern, tint: TodayFlowTheme.roseClay)
            TodayTrendLine(title: TodayShellCopy.shellTrendLineCorrelation, text: history.correlationInsight, tint: TodayFlowTheme.twilight)
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TodayAxisCapsule: View {
    let title: String
    let value: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title.uppercased())
                .font(.caption2.weight(.semibold))
                .foregroundStyle(tint.opacity(0.86))
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.56))
        .clipShape(Capsule())
    }
}

private struct TodayDeltaChip: View {
    let title: String
    let delta: Int
    let tint: Color

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: delta >= 0 ? "arrow.up.right" : "arrow.down.right")
                .font(.caption2.weight(.bold))
            Text(title)
                .font(.caption.weight(.semibold))
            Text(deltaLabel)
                .font(.caption.weight(.bold))
        }
        .foregroundStyle(tint)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.56))
        .clipShape(Capsule())
    }

    private var deltaLabel: String {
        delta == 0 ? "0" : (delta > 0 ? "+\(delta)" : "\(delta)")
    }
}

private struct TodayTrendLine: View {
    let title: String
    let text: String
    let tint: Color

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Circle()
                .fill(tint)
                .frame(width: 10, height: 10)
                .padding(.top, 5)
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text(text)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
            }
        }
    }
}

private struct TodayPromptNarrativeCard: View {
    let title: String
    let text: String
    var bodyLineLimit: Int?

    init(title: String, text: String, bodyLineLimit: Int? = nil) {
        self.title = title
        self.text = text
        self.bodyLineLimit = bodyLineLimit
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Group {
                if let bodyLineLimit {
                    Text(text)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                        .lineLimit(bodyLineLimit)
                        .fixedSize(horizontal: false, vertical: true)
                } else {
                    Text(text)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TodayWorkingLayerSection: View {
    let payload: [String: JSONValue]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(TodayShellCopy.shellWorkingLayerDayStepTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if let opening = payload.narrativeString("headline") ?? payload.narrativeString("focus_line") {
                TodayPromptNarrativeCard(
                    title: opening,
                    text: payload.narrativeString("subline")
                    ?? payload.narrativeString("day_question")
                    ?? TodayShellCopy.shellWorkingLayerOpeningFallback,
                    bodyLineLimit: 6
                )
            }

            TodayAdaptiveStack(spacing: 12) {
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellNextActionCardTitle,
                    text: payload.narrativeString("next_action")
                    ?? payload.narrativeString("next_step")
                    ?? TodayShellCopy.shellNextActionFallback
                )
                TodayGuideInfoCard(
                    title: TodayShellCopy.shellCriticalLimitTitle,
                    text: payload.narrativeString("critical_limit")
                    ?? payload.narrativeString("risk_line")
                    ?? TodayShellCopy.shellCriticalLimitFallback
                )
            }

            let actionItems = payload.narrativeStringArray("action_plan")
            if !actionItems.isEmpty {
                TodayListCard(
                    title: TodayShellCopy.shellActionPlanTitle,
                    items: actionItems,
                    tint: TodayFlowTheme.twilight
                )
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TodayDayNarrativeDetailsSection: View {
    let payload: [String: JSONValue]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellDayDetailsHeading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if let question = payload.narrativeString("question_of_day_prompt") ?? payload.narrativeString("day_question") {
                TodayGuideInfoCard(title: TodayShellCopy.shellQuestionOfDayCardTitle, text: question)
            }

            TodayAdaptiveStack(spacing: 12) {
                if let insight = payload.narrativeString("personal_insight_body") ?? payload.narrativeString("personal_insight") {
                    TodayGuideInfoCard(title: payload.narrativeString("personal_insight_title") ?? TodayShellCopy.shellPersonalInsightTitleFallback, text: insight)
                }
                if let weekly = payload.narrativeString("life_now_weekly") ?? payload.narrativeString("weekly_focus") {
                    TodayGuideInfoCard(title: TodayShellCopy.shellWeeklyFocusTitle, text: weekly)
                }
            }

            TodayAdaptiveStack(spacing: 12) {
                if let discipline = payload.narrativeString("life_now_discipline") ?? payload.narrativeString("discipline") {
                    TodayGuideInfoCard(title: TodayShellCopy.shellDisciplineTitle, text: discipline)
                }
                if let cta = payload.narrativeString("nudge_message") ?? payload.narrativeString("nudge_cta_label") {
                    TodayGuideInfoCard(title: TodayShellCopy.shellNudgeHintTitle, text: cta)
                }
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TodayEveningNarrativeDetailsSection: View {
    let payload: [String: JSONValue]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellEveningDetailsHeading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if let prompt = payload.narrativeString("closing_prompt") ?? payload.narrativeString("closure_invitation") {
                TodayGuideInfoCard(title: TodayShellCopy.shellEveningMainQuestionTitle, text: prompt)
            }

            TodayAdaptiveStack(spacing: 12) {
                if let intro = payload.narrativeString("panel_intro") {
                    TodayGuideInfoCard(title: TodayShellCopy.shellEveningBeforeCloseTitle, text: intro)
                }
                if let preamble = payload.narrativeString("outlook_preamble") {
                    TodayGuideInfoCard(title: TodayShellCopy.shellEveningWhatWeCaptureTitle, text: preamble)
                }
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct DayEnergyRibbonSection: View {
    let fusionIndex: FusionIndex

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(TodayShellCopy.shellDayEnergyRibbonTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(TodayShellCopy.shellDayEnergyRibbonSubtitle)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))

            TodayAdaptiveStack(spacing: 10) {
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbEnergy, value: fusionIndex.scores.energy, tint: TodayFlowTheme.sunset)
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbBalance, value: fusionIndex.scores.emotionalBalance, tint: TodayFlowTheme.moss)
                EnergyOrbCard(title: TodayShellCopy.shellFusionOrbFocus, value: fusionIndex.scores.focus, tint: TodayFlowTheme.twilight)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }
}

private struct TodayRecentJournalSection: View {
    let entries: [TodayJournalEntry]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(TodayShellCopy.shellRecentJournalTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            ForEach(entries) { entry in
                VStack(alignment: .leading, spacing: 6) {
                    Text(entry.typeTitle)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                    Text(entry.content)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.84))
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.56))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
    }
}

private struct TodayFocusProgressSection: View {
    let store: TodayFlowStore
    let cycle: TodayCycle

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayShellCopy.shellYourFocusTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if let goal = activeGoal {
                VStack(alignment: .leading, spacing: 10) {
                    Text(goal.title)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(goalHint)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)

                    HStack(spacing: 12) {
                        ProgressView(value: goal.displayProgress)
                            .tint(TodayFlowTheme.accent)
                        Text("\(Int(goal.displayProgress * 100))%")
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.accent)
                    }

                    Button {
                        Task {
                            await store.markGoalStep(goal: goal, dateISO: cycle.date)
                        }
                    } label: {
                        Label(TodayShellCopy.shellMarkProgressCta, systemImage: "scope")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.accent)
                    .disabled(store.isSaving || goal.isStepped(on: cycle.date) || !goal.allowsStep(on: cycle.date))
                }
                .padding(16)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
            } else {
                Text(TodayShellCopy.shellAddGoalHint)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var activeGoal: GoalTrack? {
        store.goals.first(where: { !$0.completed })
    }

    private var goalHint: String {
        if let average = store.fusionIndex?.scores.average, average >= 60 {
            return TodayShellCopy.shellGoalHintStrongDay
        }
        return TodayShellCopy.shellGoalHintCarefulDay
    }
}

private struct TodayQuickAnswerSection: View {
    let store: TodayFlowStore
    let cycle: TodayCycle

    @State private var answer: String?
    @State private var context: String?
    @State private var isSaving = false
    @State private var statusMessage: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            TodayComposerHeader(
                eyebrow: TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerEyebrow,
                title: TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerTitle,
                subtitle: TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerSubtitle
            )

            Text(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerToneLabel)
                .font(.footnote.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            HStack(spacing: 10) {
                answerButton(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerYes, value: "yes")
                answerButton(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerNo, value: "no")
                answerButton(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerUnclear, value: "unclear")
            }

            Text(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerContextLabel)
                .font(.footnote.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            HStack(spacing: 10) {
                contextButton(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerContextRelationships, value: "relationships")
                contextButton(TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerContextWork, value: "work")
            }

            TodayActionButton(
                title: isSaving ? TodayWebWorkingLayerCopy.workingLayerQuickDecisionSaving : TodayWebWorkingLayerCopy.workingLayerQuickDecisionSaveCta,
                systemImage: "bolt.fill",
                isDisabled: isSaving || answer == nil,
                action: save
            )

            if let saved = store.today.quickDecisionAnswer, !saved.isEmpty {
                TodaySavedBanner(text: "\(TodayWebWorkingLayerCopy.workingLayerQuickDecisionSavedBannerPrefix)\(saved)")
            }

            if !store.today.questionOfDayAnswer.isEmpty {
                TodaySavedBanner(text: "\(TodayWebWorkingLayerCopy.workingLayerQuestionOfDaySavedContextPrefix)\(store.today.questionOfDayAnswer)")
            }

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func answerButton(_ title: String, value: String) -> some View {
        Button {
            answer = value
        } label: {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(answer == value ? TodayFlowTheme.accent : Color.white.opacity(0.62))
                .foregroundStyle(answer == value ? Color.white : TodayFlowTheme.ink)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private func contextButton(_ title: String, value: String) -> some View {
        Button {
            context = value
        } label: {
            Text(title)
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(context == value ? TodayFlowTheme.twilight : Color.white.opacity(0.62))
                .foregroundStyle(context == value ? Color.white : TodayFlowTheme.ink)
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private func save() {
        guard let answer else { return }
        isSaving = true
        statusMessage = nil

        Task {
            await store.saveTrackerQuickDecision(answer)
            if let context, !context.isEmpty {
                await store.saveTrackerQuestionAnswer(context)
            }
            await MainActor.run {
                isSaving = false
                statusMessage = TodayWebWorkingLayerCopy.workingLayerCompactQuickAnswerSuccessStatus
            }
        }
    }
}

private struct TodayMorningComposer: View {
    let store: TodayFlowStore
    let cycle: TodayCycle

    @State private var intention: String
    @State private var isSaving = false
    @State private var statusMessage: String?

    init(store: TodayFlowStore, cycle: TodayCycle) {
        self.store = store
        self.cycle = cycle
        _intention = State(initialValue: cycle.dayConnection?.morningIntention ?? "")
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            TodayComposerHeader(
                eyebrow: TodayWebTodayViewComposerCopy.todayViewMorningComposerEyebrow,
                title: TodayWebTodayViewComposerCopy.todayViewMorningComposerTitle,
                subtitle: TodayWebTodayViewComposerCopy.todayViewMorningComposerSubtitle
            )

            TextField(TodayWebTodayViewComposerCopy.todayViewMorningComposerPlaceholder, text: $intention, axis: .vertical)
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(16)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            TodayActionButton(
                title: isSaving
                    ? TodayWebTodayViewComposerCopy.todayViewComposerSaving
                    : TodayWebTodayViewComposerCopy.todayViewMorningComposerSaveCta,
                systemImage: "checkmark.circle.fill",
                isDisabled: isSaving || intention.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                action: save
            )

            if let saved = cycle.dayConnection?.morningIntention, !saved.isEmpty {
                TodaySavedBanner(text: TodayWebTodayViewComposerCopy.formatMorningComposerSavedBanner(saved: saved))
            }

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func save() {
        let value = intention.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !value.isEmpty else { return }

        isSaving = true
        statusMessage = nil

        Task {
            do {
                try await store.saveMorningIntention(value)
                await MainActor.run {
                    isSaving = false
                    statusMessage = TodayWebTodayViewComposerCopy.todayViewMorningComposerSuccessStatus
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    statusMessage = error.localizedDescription
                }
            }
        }
    }
}

private struct TodayPulseCheckComposer: View {
    enum EnergyOption: String, CaseIterable, Identifiable, TodayChoiceOption {
        case low
        case medium
        case high

        var id: String { rawValue }
        var title: String {
            switch self {
            case .low: return TodayWebTodayViewComposerCopy.todayViewPulseEnergyLow
            case .medium: return TodayWebTodayViewComposerCopy.todayViewPulseEnergyMedium
            case .high: return TodayWebTodayViewComposerCopy.todayViewPulseEnergyHigh
            }
        }

        var scale: Int {
            switch self {
            case .low: return 2
            case .medium: return 3
            case .high: return 5
            }
        }
    }

    enum MoodOption: String, CaseIterable, Identifiable, TodayChoiceOption {
        case calm
        case open
        case tense

        var id: String { rawValue }
        var title: String {
            switch self {
            case .calm: return TodayWebTodayViewComposerCopy.todayViewPulseMoodCalm
            case .open: return TodayWebTodayViewComposerCopy.todayViewPulseMoodOpen
            case .tense: return TodayWebTodayViewComposerCopy.todayViewPulseMoodTense
            }
        }
    }

    enum StressOption: String, CaseIterable, Identifiable, TodayChoiceOption {
        case low
        case medium
        case high

        var id: String { rawValue }
        var title: String {
            switch self {
            case .low: return TodayWebTodayViewComposerCopy.todayViewPulseStressLow
            case .medium: return TodayWebTodayViewComposerCopy.todayViewPulseStressMedium
            case .high: return TodayWebTodayViewComposerCopy.todayViewPulseStressHigh
            }
        }

        var scale: Int {
            switch self {
            case .low: return 2
            case .medium: return 3
            case .high: return 5
            }
        }
    }

    let store: TodayFlowStore
    let cycle: TodayCycle

    @State private var energy: EnergyOption?
    @State private var mood: MoodOption?
    @State private var stress: StressOption?
    @State private var note = ""
    @State private var isSaving = false
    @State private var statusMessage: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            TodayComposerHeader(
                eyebrow: TodayWebTodayViewComposerCopy.todayViewPulseEyebrow,
                title: TodayWebTodayViewComposerCopy.todayViewPulseTitle,
                subtitle: TodayWebTodayViewComposerCopy.todayViewPulseSubtitle
            )

            TodayChoiceGroup(title: TodayWebEveningSectionCopy.eveningScaleEnergyLabel, options: EnergyOption.allCases, selection: $energy)
            TodayChoiceGroup(title: TodayWebEveningSectionCopy.eveningScaleMoodLabel, options: MoodOption.allCases, selection: $mood)
            TodayChoiceGroup(title: TodayWebEveningSectionCopy.eveningScaleStressLabel, options: StressOption.allCases, selection: $stress)

            TextField(TodayWebTodayViewComposerCopy.todayViewPulseNotePlaceholder, text: $note, axis: .vertical)
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(16)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            TodayActionButton(
                title: isSaving
                    ? TodayWebTodayViewComposerCopy.todayViewComposerSaving
                    : TodayWebTodayViewComposerCopy.todayViewPulseSaveCta,
                systemImage: "waveform.path.ecg",
                isDisabled: isSaving || !canSave,
                action: save
            )

            if let latest = cycle.dayTrackers.last?.state, !latest.isEmpty {
                TodaySavedBanner(
                    text: "\(TodayWebTodayViewComposerCopy.todayViewPulseLastSignalBannerPrefix)\(latest)"
                )
            }

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var canSave: Bool {
        energy != nil || mood != nil || stress != nil || !note.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private var composedState: String {
        [
            energy.map { "\(TodayWebTodayViewComposerCopy.todayViewPulseComposedEnergyPrefix)\($0.title.lowercased())" },
            mood.map { "\(TodayWebTodayViewComposerCopy.todayViewPulseComposedMoodPrefix)\($0.title.lowercased())" },
            stress.map { "\(TodayWebTodayViewComposerCopy.todayViewPulseComposedStressPrefix)\($0.title.lowercased())" }
        ]
        .compactMap { $0 }
        .joined(separator: TodayWebTodayViewComposerCopy.todayViewPulseComposedSeparator)
    }

    private var composedScale: Int? {
        stress?.scale ?? energy?.scale
    }

    private func save() {
        guard canSave else { return }

        isSaving = true
        statusMessage = nil

        Task {
            do {
                try await store.savePulseCheck(
                    state: composedState.isEmpty ? nil : composedState,
                    scale: composedScale,
                    note: note
                )
                await MainActor.run {
                    isSaving = false
                    statusMessage = TodayWebTodayViewComposerCopy.todayViewPulseSuccessStatus
                    note = ""
                    energy = nil
                    mood = nil
                    stress = nil
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    statusMessage = error.localizedDescription
                }
            }
        }
    }
}

private struct TodayJournalComposer: View {
    enum EntryType: String, CaseIterable, Identifiable {
        case observation
        case gratitude
        case insight

        var id: String { rawValue }

        var title: String {
            switch self {
            case .observation: return TodayWebDaySectionCopy.dayJournalTypeObservation
            case .gratitude: return TodayWebDaySectionCopy.dayJournalTypeGratitude
            case .insight: return TodayWebDaySectionCopy.dayJournalTypeInsight
            }
        }

        var prompt: String {
            switch self {
            case .observation: return TodayWebDaySectionCopy.dayJournalPromptObservation
            case .gratitude: return TodayWebDaySectionCopy.dayJournalPromptGratitude
            case .insight: return TodayWebDaySectionCopy.dayJournalPromptInsight
            }
        }
    }

    let store: TodayFlowStore
    let cycle: TodayCycle

    @State private var entryType: EntryType = .observation
    @State private var content = ""
    @State private var isSaving = false
    @State private var statusMessage: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            TodayComposerHeader(
                eyebrow: TodayWebTodayViewComposerCopy.todayViewJournalEyebrow,
                title: TodayWebTodayViewComposerCopy.todayViewJournalTitle,
                subtitle: TodayWebTodayViewComposerCopy.todayViewJournalSubtitle
            )

            Picker(TodayWebTodayViewComposerCopy.todayViewJournalPickerLabel, selection: $entryType) {
                ForEach(EntryType.allCases) { type in
                    Text(type.title).tag(type)
                }
            }
            .pickerStyle(.segmented)

            TextField(entryType.prompt, text: $content, axis: .vertical)
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(16)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            TodayActionButton(
                title: isSaving
                    ? TodayWebTodayViewComposerCopy.todayViewComposerSaving
                    : TodayWebTodayViewComposerCopy.todayViewJournalSaveCta,
                systemImage: "square.and.pencil",
                isDisabled: isSaving || content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
                action: save
            )

            if !cycle.dayJournalEntries.isEmpty {
                TodaySavedBanner(
                    text: TodayWebTodayViewComposerCopy.formatJournalSavedCountBanner(
                        count: cycle.dayJournalEntries.count
                    )
                )
            }

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private func save() {
        let value = content.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !value.isEmpty else { return }

        isSaving = true
        statusMessage = nil

        Task {
            do {
                try await store.saveJournalEntry(type: entryType.rawValue, content: value)
                await MainActor.run {
                    isSaving = false
                    statusMessage = TodayWebTodayViewComposerCopy.todayViewJournalSuccessStatus
                    content = ""
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    statusMessage = error.localizedDescription
                }
            }
        }
    }
}

struct TodayEveningComposer: View {
    let store: TodayFlowStore
    let cycle: TodayCycle

    @State private var reflection: String
    @State private var noticed: String
    @State private var hardest: String
    @State private var easierThanExpected: String
    @State private var markComplete: Bool
    @State private var isSaving = false
    @State private var statusMessage: String?

    init(store: TodayFlowStore, cycle: TodayCycle) {
        self.store = store
        self.cycle = cycle
        _reflection = State(initialValue: cycle.dayConnection?.eveningReflection ?? "")
        _noticed = State(initialValue: cycle.dayConnection?.eveningObservations?.noticed ?? "")
        _hardest = State(initialValue: cycle.dayConnection?.eveningObservations?.hardest ?? "")
        _easierThanExpected = State(initialValue: cycle.dayConnection?.eveningObservations?.easierThanExpected ?? "")
        _markComplete = State(initialValue: cycle.eveningCompleted)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            TodayComposerHeader(
                eyebrow: TodayWebTodayViewComposerCopy.todayViewEveningComposerEyebrow,
                title: TodayWebTodayViewComposerCopy.todayViewEveningComposerTitle,
                subtitle: TodayWebTodayViewComposerCopy.todayViewEveningComposerSubtitle
            )

            TextField(
                TodayWebTodayViewComposerCopy.todayViewEveningComposerReflectionPlaceholder,
                text: $reflection,
                axis: .vertical
            )
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(16)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            VStack(spacing: 10) {
                TodayPromptField(title: TodayWebTodayViewComposerCopy.todayViewEveningComposerNoticedTitle, text: $noticed)
                TodayPromptField(title: TodayWebTodayViewComposerCopy.todayViewEveningComposerHardestTitle, text: $hardest)
                TodayPromptField(title: TodayWebTodayViewComposerCopy.todayViewEveningComposerEasierTitle, text: $easierThanExpected)
            }

            Toggle(TodayWebTodayViewComposerCopy.todayViewEveningComposerMarkClosedToggle, isOn: $markComplete)
                .toggleStyle(.switch)
                .foregroundStyle(TodayFlowTheme.ink)

            TodayActionButton(
                title: isSaving
                    ? TodayWebTodayViewComposerCopy.todayViewComposerSaving
                    : TodayWebTodayViewComposerCopy.todayViewEveningComposerSaveCta,
                systemImage: "moon.stars.fill",
                isDisabled: isSaving || !canSave,
                action: save
            )

            if let statusMessage {
                TodayStatusLine(text: statusMessage)
            }
        }
        .padding(18)
        .background(TodayFlowTheme.todayHeroSurface)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var canSave: Bool {
        !reflection.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ||
        !noticed.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ||
        !hardest.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ||
        !easierThanExpected.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    private func save() {
        guard canSave else { return }

        isSaving = true
        statusMessage = nil

        Task {
            do {
                try await store.saveEveningReflection(
                    reflection: reflection,
                    noticed: noticed,
                    hardest: hardest,
                    easierThanExpected: easierThanExpected,
                    markComplete: markComplete
                )
                await MainActor.run {
                    isSaving = false
                    statusMessage = TodayWebTodayViewComposerCopy.todayViewEveningComposerSuccessStatus
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    statusMessage = error.localizedDescription
                }
            }
        }
    }
}

private struct TodayComposerHeader: View {
    let eyebrow: String
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(eyebrow.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(title)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
        }
    }
}

private struct TodayActionButton: View {
    let title: String
    let systemImage: String
    let isDisabled: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: systemImage)
                .font(.subheadline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            isDisabled
            ? LinearGradient(colors: [TodayFlowTheme.sunset.opacity(0.46), TodayFlowTheme.ember.opacity(0.42)], startPoint: .leading, endPoint: .trailing)
            : LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
        )
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .disabled(isDisabled)
    }
}

private struct TodaySavedBanner: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.footnote)
            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.54))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct TodayStatusLine: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.footnote)
            .foregroundStyle(.secondary)
    }
}

private struct TodayChoiceGroup<Option: Identifiable & Hashable & TodayChoiceOption>: View {
    let title: String
    let options: [Option]
    @Binding var selection: Option?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(options) { option in
                        Button {
                            selection = selection == option ? nil : option
                        } label: {
                            Text(option.title)
                                .font(.subheadline.weight(.medium))
                                .padding(.horizontal, 14)
                                .padding(.vertical, 10)
                                .background(selection == option ? TodayFlowTheme.sunset : Color.white.opacity(0.62))
                                .foregroundStyle(selection == option ? .white : TodayFlowTheme.ink)
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }
}

private struct TodayPromptField: View {
    let title: String
    @Binding var text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            TextField(title, text: $text, axis: .vertical)
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(14)
                .background(Color.white.opacity(0.62))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }
}

private struct TodaySectionIntro: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                .lineSpacing(3)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

private struct TodayMetricTile: View {
    let title: String
    let value: String
    let caption: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)

            Text(value)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            Text(caption)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.64))
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: 132, alignment: .topLeading)
        .background(Color.white.opacity(0.56))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct TodayAuraDot: View {
    let value: Int
    let title: String
    let tint: Color

    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(tint)
                .frame(width: 10, height: 10)
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            Text("\(value)")
                .font(.caption.weight(.bold))
                .foregroundStyle(tint)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.54))
        .clipShape(Capsule())
    }
}

private struct TodayHeroSignalCard: View {
    let title: String
    let value: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(tint)
            Text(value)
                .font(.subheadline.weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.86))
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

private struct TodayHeroChip: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title.uppercased())
                .font(.system(size: 10, weight: .semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.58))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct TodayGlowBadge: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.caption.weight(.semibold))
            .foregroundStyle(TodayFlowTheme.ink)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(TodayFlowTheme.gold.opacity(0.22))
            .clipShape(Capsule())
    }
}

private struct TodayPanelShell: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(TodayFlowTheme.todayPanelGradient)
            .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
            .shadow(color: Color.black.opacity(0.05), radius: 18, x: 0, y: 10)
    }
}

struct TodayBackground: View {
    var body: some View {
        ZStack {
            TodayFlowTheme.screenGradient
                .ignoresSafeArea()

            Circle()
                .fill(TodayFlowTheme.sunset.opacity(0.1))
                .frame(width: 380, height: 380)
                .blur(radius: 14)
                .offset(x: 170, y: -260)

            Circle()
                .fill(TodayFlowTheme.moss.opacity(0.1))
                .frame(width: 340, height: 340)
                .blur(radius: 24)
                .offset(x: -180, y: 220)
        }
    }
}

private struct TodayStatePill: View {
    let loadState: TodayFlowStore.LoadState

    var body: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(color)
                .frame(width: 8, height: 8)
            Text(text)
                .font(.caption.weight(.semibold))
        }
        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.58))
        .clipShape(Capsule())
    }

    private var color: Color {
        switch loadState {
        case .idle:
            return .gray
        case .loading:
            return TodayFlowTheme.gold
        case .loaded:
            return TodayFlowTheme.moss
        case .failed:
            return TodayFlowTheme.roseClay
        }
    }

    private var text: String {
        switch loadState {
        case .idle:
            return TodayShellCopy.shellLoadStateIdle
        case .loading:
            return TodayShellCopy.shellLoadStateLoading
        case .loaded:
            return TodayShellCopy.shellLoadStateDone
        case let .failed(message):
            return message
        }
    }
}

private struct TodayFallbackPanel: View {
    let store: TodayFlowStore

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(TodayShellCopy.shellFallbackPanelTitle)
                .font(.title2.weight(.bold))
                .foregroundStyle(TodayFlowTheme.ink)

            if store.loadState == .loading || store.isRefreshingToday {
                HStack(spacing: 12) {
                    ProgressView()
                        .tint(TodayFlowTheme.sunset)
                    Text(TodayShellCopy.shellFallbackPanelLoadingBody)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.76))
                }
            } else {
                Text(TodayShellCopy.shellFallbackPanelStaleHint)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.76))
            }

            Button {
                Task {
                    await store.refreshIfNeeded()
                }
            } label: {
                Label(TodayShellCopy.shellFallbackRefreshScreenCta, systemImage: "arrow.clockwise")
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.white)
            .background(
                LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
            )
            .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            if case let .failed(message) = store.loadState {
                Text(message)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(24)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.82))
        .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
    }
}

private extension TodayJournalEntry {
    var typeTitle: String {
        switch type {
        case "gratitude":
            return TodayWebDaySectionCopy.dayJournalTypeGratitude
        case "insight":
            return TodayWebDaySectionCopy.dayJournalTypeInsight
        default:
            return TodayWebDaySectionCopy.dayJournalTypeObservation
        }
    }
}

#Preview {
    TodayView(store: TodayFlowStore())
}
