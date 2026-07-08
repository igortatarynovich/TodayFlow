import SwiftUI

enum ProfileCumInsightsCopy {
    static let sectionTitle = "Уверенность и следующий шаг"
    static let scoreCaption = "уверенность модели"
    static let primaryLabel = "Главный шаг"
    static let alternatesLabel = "Альтернативы"
    static let todayLink = "Открыть Today для уточнения"

    static func confidencePercent(_ overall: Double?) -> String {
        guard let overall else { return "—" }
        let clamped = min(max(overall, 0), 1)
        return "\(Int((clamped * 100).rounded()))%"
    }

    static func delta30Label(_ delta: Double?) -> String? {
        guard let delta else { return nil }
        let pct = Int((delta * 100).rounded())
        if pct == 0 { return "без изменений за 30 дн" }
        let sign = pct > 0 ? "+" : ""
        return "\(sign)\(pct) за 30 дн"
    }

    static func deltaWindowLabel(_ delta: Double?, windowDays: Int) -> String? {
        guard let delta else { return nil }
        let pct = Int((delta * 100).rounded())
        if pct == 0 { return "без изменений за \(windowDays) дн" }
        let sign = pct > 0 ? "+" : ""
        return "\(sign)\(pct) за \(windowDays) дн"
    }

    static func uncertaintyMessage(_ flag: String) -> String {
        switch flag {
        case "low_meaning_events":
            return "Мало событий за период — выводы предварительные."
        case "no_active_knowledge_atoms":
            return "Пока нет подтверждённых паттернов."
        case "no_explicit_state_today":
            return "Отметь настроение в Today — точность вырастет."
        default:
            return flag.replacingOccurrences(of: "_", with: " ")
        }
    }
}

struct ProfileCumInsightsSection: View {
    let store: TodayFlowStore
    @State private var history: CompactUserModelConfidenceHistoryResponse?

    private var cum: CompactUserModelResponse? { store.compactUserModel }

    private var shouldShow: Bool {
        guard let cum else { return false }
        if cum.confidence.overall != nil { return true }
        if let text = cum.recommendations?.primary.text.trimmingCharacters(in: .whitespacesAndNewlines), !text.isEmpty {
            return true
        }
        return false
    }

    var body: some View {
        Group {
            if shouldShow, let cum {
                content(cum: cum)
            }
        }
        .task(id: cum?.generatedAt) {
            guard shouldShow else {
                history = nil
                return
            }
            history = try? await store.loadCompactUserModelConfidenceHistory(windowDays: 90)
        }
    }

    @ViewBuilder
    private func content(cum: CompactUserModelResponse) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(ProfileCumInsightsCopy.sectionTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            HStack(alignment: .bottom) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(ProfileCumInsightsCopy.confidencePercent(cum.confidence.overall))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundStyle(TodayFlowTheme.ink)
                    Text(ProfileCumInsightsCopy.scoreCaption)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
                Spacer(minLength: 8)
                VStack(alignment: .trailing, spacing: 4) {
                    if let delta30 = ProfileCumInsightsCopy.delta30Label(cum.confidence.delta30d) {
                        Text(delta30)
                            .font(.caption.weight(.semibold))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(TodayFlowTheme.twilight.opacity(0.12))
                            .clipShape(Capsule())
                    }
                    if let window = ProfileCumInsightsCopy.deltaWindowLabel(history?.summary.deltaWindow, windowDays: history?.windowDays ?? 90),
                       window != ProfileCumInsightsCopy.delta30Label(cum.confidence.delta30d) {
                        Text(window)
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                    }
                }
            }

            if let points = history?.points, points.count >= 2 {
                sparkline(points: points)
                Text("\(history?.summary.pointCount ?? points.count) точек за \(history?.windowDays ?? 90) дн")
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }

            domainRows(cum: cum)

            if let primary = cum.recommendations?.primary {
                recommendationCard(label: ProfileCumInsightsCopy.primaryLabel, text: primary.text, timing: primary.timingHint)
            }

            if let alternates = cum.recommendations?.alternates, !alternates.isEmpty {
                Text(ProfileCumInsightsCopy.alternatesLabel)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                ForEach(alternates) { alt in
                    recommendationCard(label: nil, text: alt.text, timing: alt.timingHint)
                }
            }

            if let flags = cum.confidence.uncertaintyFlags, !flags.isEmpty {
                ForEach(flags, id: \.self) { flag in
                    Text("• \(ProfileCumInsightsCopy.uncertaintyMessage(flag))")
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
            }
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color.white.opacity(0.88), TodayFlowTheme.twilight.opacity(0.05)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
        )
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .accessibilityIdentifier("profile-cum-insights")
    }

    @ViewBuilder
    private func sparkline(points: [CompactUserModelConfidenceHistoryPoint]) -> some View {
        let values = points.map(\.overall)
        let minValue = values.min() ?? 0
        let maxValue = values.max() ?? 1
        let span = max(maxValue - minValue, 0.08)
        HStack(alignment: .bottom, spacing: 2) {
            ForEach(points) { point in
                let height = ((point.overall - minValue) / span) * 0.7 + 0.3
                RoundedRectangle(cornerRadius: 2, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [TodayFlowTheme.twilight.opacity(0.75), TodayFlowTheme.gold.opacity(0.55)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
                    .frame(maxWidth: .infinity)
                    .frame(height: max(8, CGFloat(height) * 44))
            }
        }
        .frame(height: 44)
    }

    @ViewBuilder
    private func domainRows(cum: CompactUserModelResponse) -> some View {
        if let domains = cum.confidence.byDomain {
            let rows: [(String, Double?)] = [
                ("Идентичность", domains.identity),
                ("Темы", domains.themes),
                ("Тайминг", domains.timing),
                ("Рекомендации", domains.recommendations),
            ].filter { $0.1 != nil }

            if !rows.isEmpty {
                VStack(spacing: 6) {
                    ForEach(rows.prefix(4), id: \.0) { label, value in
                        if let value {
                            HStack(spacing: 8) {
                                Text(label)
                                    .font(.caption2)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                                    .frame(width: 88, alignment: .leading)
                                GeometryReader { geo in
                                    ZStack(alignment: .leading) {
                                        Capsule().fill(TodayFlowTheme.gold.opacity(0.15))
                                        Capsule()
                                            .fill(TodayFlowTheme.twilight.opacity(0.55))
                                            .frame(width: geo.size.width * CGFloat(min(max(value, 0), 1)))
                                    }
                                }
                                .frame(height: 6)
                                Text(ProfileCumInsightsCopy.confidencePercent(value))
                                    .font(.caption2.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.75))
                                    .frame(width: 36, alignment: .trailing)
                            }
                        }
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func recommendationCard(label: String?, text: String, timing: String?) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            if let label {
                Text(label)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                .fixedSize(horizontal: false, vertical: true)
            if let timing, !timing.isEmpty {
                Text(timing)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .overlay(alignment: .leading) {
            Rectangle()
                .fill(TodayFlowTheme.twilight.opacity(0.45))
                .frame(width: 3)
        }
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}
