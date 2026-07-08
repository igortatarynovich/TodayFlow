import SwiftUI

// MARK: - Foundation Hero Medium (TODAYFLOW_FOUNDATION_UI §1.2)

struct HeroMediumPillar: Identifiable {
    let id: String
    let label: String
}

struct HeroMediumView: View {
    let symbolSeed: String
    let title: String
    var kicker: String? = nil
    var subline: String? = nil
    var pillars: [HeroMediumPillar] = []
    var loading: Bool = false
    var loadingText: String = "Загрузка…"
    var embedded: Bool = false

    private let symbolSize: CGFloat = 80

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            ArchetypeSymbolView(seed: symbolSeed, size: symbolSize)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                .padding(.bottom, 16)
                .profileMotionHeroSymbol()

            if let kicker {
                Text(kicker)
                    .font(.caption.weight(.semibold))
                    .tracking(2.2)
                    .textCase(.uppercase)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .padding(.bottom, 10)
            }

            if loading {
                Text(loadingText)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    .fixedSize(horizontal: false, vertical: true)
            } else {
                Text(title)
                    .font(.system(size: 26, design: .serif).weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)

                if let subline {
                    Text(subline)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .lineLimit(1)
                        .padding(.top, 8)
                }
            }

            if !loading, !pillars.isEmpty {
                HeroFlowLayout(spacing: 8) {
                    ForEach(pillars) { pillar in
                        Text(pillar.label)
                            .font(.caption2.weight(.bold))
                            .tracking(0.6)
                            .textCase(.uppercase)
                            .foregroundStyle(TodayFlowTheme.twilight)
                            .padding(.horizontal, 11)
                            .padding(.vertical, 6)
                            .background(Capsule().fill(Color.white.opacity(0.78)))
                            .overlay(Capsule().stroke(TodayFlowTheme.twilight.opacity(0.14), lineWidth: 1))
                    }
                }
                .padding(.top, 14)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(embedded ? EdgeInsets(top: 22, leading: 22, bottom: 18, trailing: 22) : EdgeInsets(top: 44, leading: 20, bottom: 40, trailing: 20))
        .frame(minHeight: embedded ? nil : min(UIScreen.main.bounds.height * 0.52, 420), alignment: .bottomLeading)
        .background {
            if embedded {
                Color.clear
            } else {
                ZStack {
                    LinearGradient(
                        colors: [Color.white.opacity(0.82), TodayFlowTheme.paper],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    FoundationGeometryView(preset: .today, emphasis: .soft)
                        .opacity(0.55)
                        .allowsHitTesting(false)
                }
            }
        }
        .accessibilityElement(children: .combine)
    }
}
