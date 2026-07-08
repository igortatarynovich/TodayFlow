import SwiftUI

// MARK: - Foundation Hero Small (TODAYFLOW_FOUNDATION_UI §1.3)

struct HeroSmallView: View {
    let symbolSeed: String
    let title: String
    var kicker: String? = nil
    var meta: String? = nil
    var scorePercent: Int? = nil
    var embedded: Bool = false

    private let symbolSize: CGFloat = 48

    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            ArchetypeSymbolView(seed: symbolSeed, size: symbolSize)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))

            VStack(alignment: .leading, spacing: 4) {
                if let kicker {
                    Text(kicker)
                        .font(.caption.weight(.semibold))
                        .tracking(1.8)
                        .textCase(.uppercase)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }

                Text(title)
                    .font(.system(size: 20, weight: .semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .lineLimit(2)

                if let meta {
                    Text(meta)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .lineLimit(2)
                }
            }

            Spacer(minLength: 0)

            if let scorePercent {
                ZStack {
                    Circle()
                        .stroke(TodayFlowTheme.gold.opacity(0.35), lineWidth: 4)
                    Text("\(scorePercent)%")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.ink)
                }
                .frame(width: 56, height: 56)
            }
        }
        .padding(embedded ? EdgeInsets(top: 12, leading: 0, bottom: 12, trailing: 0) : EdgeInsets(top: 24, leading: 20, bottom: 24, trailing: 20))
        .frame(height: embedded ? nil : 200, alignment: .center)
        .background {
            if embedded {
                Color.clear
            } else {
                ZStack {
                    LinearGradient(
                        colors: [Color.white.opacity(0.9), TodayFlowTheme.paper.opacity(0.96)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    FoundationGeometryView(preset: .profile, emphasis: .soft)
                        .opacity(0.5)
                        .allowsHitTesting(false)
                }
            }
        }
        .accessibilityElement(children: .combine)
    }
}
