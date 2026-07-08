import SwiftUI

private enum ProfileSummaryChrome {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var title: String { ru ? "Краткая сводка" : "Brief summary" }
    static var fallbackBody: String {
        ru
            ? "Сначала посмотри сводку, затем переходи к следующему шагу дня."
            : "Review your summary first, then move on to the next step of your day."
    }
    static var loading: String { ru ? "Обновляю сводку..." : "Refreshing summary..." }
    static var unavailable: String {
        ru
            ? "Сводка временно недоступна. Перейди в Today и обнови позже."
            : "Summary is temporarily unavailable. Open Today and try again later."
    }
    static var openToday: String { ru ? "Открыть Сегодня" : "Open Today" }
    static var openProfile: String { ru ? "Открыть профиль" : "Open profile" }
    static var coreTrio: String { ru ? "Базовая тройка" : "Core trio" }
    static var sun: String { ru ? "Солнце" : "Sun" }
    static var path: String { ru ? "Путь" : "Path" }
    static var status: String { ru ? "Статус" : "Status" }
    static var rings: String { ru ? "Кольца выравнивания" : "Alignment rings" }
}

struct ProfileSummaryView: View {
    let store: TodayFlowStore
    let onContinue: (AppTab) -> Void

    @State private var isLoading = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    Text(ProfileSummaryChrome.title)
                        .font(.largeTitle.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    Text(store.profileSummary?.livingSummary ?? ProfileSummaryChrome.fallbackBody)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)

                    if let summary = store.profileSummary {
                        summaryCoreBlock(summary: summary)
                        summaryRingsBlock(summary: summary, rings: store.meaningRings)
                    } else if isLoading {
                        ProgressView(ProfileSummaryChrome.loading)
                            .tint(TodayFlowTheme.sunset)
                    } else {
                        Text(ProfileSummaryChrome.unavailable)
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                    }

                    HStack(spacing: 10) {
                        Button(ProfileSummaryChrome.openToday) {
                            onContinue(.today)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(TodayFlowTheme.sunset)

                        Button(ProfileSummaryChrome.openProfile) {
                            onContinue(.profile)
                        }
                        .buttonStyle(.bordered)
                    }
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .task {
                guard !isLoading else { return }
                isLoading = true
                defer { isLoading = false }
                _ = try? await store.loadProfileSummary(force: true)
            }
        }
    }

    @ViewBuilder
    private func summaryCoreBlock(summary: ProfileSummaryResponse) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(ProfileSummaryChrome.coreTrio)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            HStack(spacing: 10) {
                chip(ProfileSummaryChrome.sun, summary.coreTrio.sunSign ?? "—")
                chip(ProfileSummaryChrome.path, summary.coreTrio.lifePath.map { "\($0)" } ?? "—")
                chip(ProfileSummaryChrome.status, store.profileBuildStatus?.status ?? (summary.isReady ? "ready" : "building"))
            }
        }
        .padding(16)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    @ViewBuilder
    private func summaryRingsBlock(summary: ProfileSummaryResponse, rings: [MeaningRingItem]) -> some View {
        let effectiveRings: [MeaningRingItem] = rings.isEmpty
            ? summary.ringsPreview.map { MeaningRingItem(ring: $0.key, score: $0.value, trend7d: 0, confidence: "low", topContributors: []) }
                .sorted { $0.ring < $1.ring }
            : rings
        VStack(alignment: .leading, spacing: 10) {
            Text(ProfileSummaryChrome.rings)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            ForEach(effectiveRings.prefix(6)) { ring in
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
        .padding(16)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func chip(_ title: String, _ value: String) -> some View {
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

#Preview {
    ProfileSummaryView(store: TodayFlowStore(), onContinue: { _ in })
}

