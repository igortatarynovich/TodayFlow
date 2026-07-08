import SwiftUI

/// Canonical Today surface — foundation (contract) + ritual spine + personalized day.
/// Паритет с веб `TodayCompositionSurface.tsx`.
struct TodayCompositionSurfaceView: View {
    let store: TodayFlowStore
    let cycle: TodayCycle
    var onSelectTab: (AppTab) -> Void
    var onNavigateCalendarQuickCreate: ((TrackerQuickCreateKind) -> Void)? = nil
    var onStartFocus20Minutes: (() -> Void)? = nil
    var guideNarrativeLoading: Bool
    var eveningNarrativeLoading: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            if let contract = store.todayContract {
                TodayCompositionFoundationZone(contract: contract, cycle: cycle)
                    .padding(.horizontal, 20)
                    .padding(.top, 8)
                    .padding(.bottom, 4)
            }
            TodayRitualFlowView(
                store: store,
                cycle: cycle,
                onSelectTab: onSelectTab,
                onNavigateCalendarQuickCreate: onNavigateCalendarQuickCreate,
                onStartFocus20Minutes: onStartFocus20Minutes,
                guideNarrativeLoading: guideNarrativeLoading,
                eveningNarrativeLoading: eveningNarrativeLoading
            )
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        }
    }
}

private struct TodayCompositionFoundationZone: View {
    let contract: TodayContractV1
    let cycle: TodayCycle

    private var headline: String {
        TodayContractMapper.themeHeadline(from: contract) ?? cycle.morning?.dailyHoroscope?.headline ?? "Сегодня"
    }

    private var storyExcerpt: String? {
        guard let story = contract.dayStory?.story?.trimmingCharacters(in: .whitespacesAndNewlines), !story.isEmpty else {
            return nil
        }
        if story.count <= 280 { return story }
        let prefix = String(story.prefix(277))
        return prefix.trimmingCharacters(in: .whitespacesAndNewlines) + "…"
    }

    private var primaryMove: String? {
        TodayContractMapper.primaryAction(from: contract)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayWebGuideSectionCopy.guidePanelEyebrowToday.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(headline)
                .font(.title2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            if let direction = contract.dayStory?.direction?.trimmingCharacters(in: .whitespacesAndNewlines), !direction.isEmpty {
                Text(direction)
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let storyExcerpt {
                Text(storyExcerpt)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let primaryMove {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Главный шаг")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text(primaryMove)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            TodayCompositionDomainGlance(domains: contract.domains)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(TodayFlowTheme.surface.opacity(0.92))
        )
    }
}

private struct TodayCompositionDomainGlance: View {
    let domains: TodayContractDomains

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Три сферы")
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            glanceRow(title: "Отношения", line: domains.relationships.action)
            glanceRow(title: "Работа и деньги", line: domains.moneyWork.action)
            glanceRow(title: "Семья", line: domains.family.action)
        }
    }

    @ViewBuilder
    private func glanceRow(title: String, line: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
            Text(line)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.85))
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}
