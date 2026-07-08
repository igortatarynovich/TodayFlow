import SwiftUI

struct ProfileRelationshipInsightsSection: View {
    let store: TodayFlowStore

    @State private var insights: [CompactUserModelRelationshipInsight] = []

    var body: some View {
        Group {
            if !insights.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text("Отношения")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    Text("Ты подтвердил")
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)

                    ForEach(insights) { item in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(item.kind == "attachment_lens" ? "Паттерн привязанности" : "Наблюдение")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.sand)
                            Text(item.label)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                                .fixedSize(horizontal: false, vertical: true)
                            if let summary = item.summary, summary != item.label {
                                Text(summary)
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.66))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.55))
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                .accessibilityIdentifier("profile_relationship_insights")
            }
        }
        .task {
            if let model = try? await store.loadCompactUserModel(force: true) {
                insights = (model.relationshipInsightsTopK ?? []).filter {
                    !$0.label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                }
            }
        }
    }
}
