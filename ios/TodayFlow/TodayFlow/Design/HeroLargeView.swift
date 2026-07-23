import SwiftUI

// MARK: - Foundation Hero Large (TODAYFLOW_FOUNDATION_UI §1.1)

struct HeroLargePillar: Identifiable {
    let id: String
    let label: String
    var accent: Bool = false
}

struct HeroLargeTrait: Identifiable {
    let id: String
    let title: String
    let subtitle: String
}

struct HeroLargeView: View {
    let symbolSeed: String
    let title: String
    var kicker: String? = nil
    var sectionLabel: String? = nil
    var metaLine: String? = nil
    var digest: String? = nil
    var poeticCaption: String? = nil
    var pillars: [HeroLargePillar] = []
    var traits: [HeroLargeTrait] = []
    var topActionTitle: String? = nil
    var topAction: (() -> Void)? = nil
    var edgeToEdge: Bool = true

    private let symbolSize: CGFloat = 120
    private let innerMaxWidth: CGFloat = 336

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            heroBackground
            HeroLargeSacredGeometryBackdrop()
                .opacity(0.85)
                .allowsHitTesting(false)

            LinearGradient(
                colors: [Color.clear, TodayFlowTheme.paper],
                startPoint: .top,
                endPoint: .bottom
            )
            .frame(height: 180)
            .frame(maxHeight: .infinity, alignment: .bottom)
            .allowsHitTesting(false)

            VStack(alignment: .leading, spacing: 0) {
                if kicker != nil || topActionTitle != nil {
                    HStack {
                        if let kicker {
                            Text(kicker)
                                .font(.caption.weight(.semibold))
                                .tracking(2.2)
                                .textCase(.uppercase)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                        Spacer()
                        if let topActionTitle, let topAction {
                            Button(topActionTitle, action: topAction)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                                .underline(true, color: TodayFlowTheme.secondaryInk.opacity(0.5))
                        }
                    }
                    .padding(.bottom, 12)
                }

                ArchetypeHeroVisual(seed: symbolSeed, symbolSize: symbolSize)
                    .padding(.bottom, 22)
                    .profileMotionHeroSymbol()

                if !pillars.isEmpty {
                    HeroFlowLayout(spacing: 8) {
                        ForEach(Array(pillars.enumerated()), id: \.element.id) { index, pillar in
                            Text(pillar.label)
                                .font(.caption2.weight(.bold))
                                .tracking(0.8)
                                .textCase(.uppercase)
                                .foregroundStyle(TodayFlowTheme.twilight)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(
                                    Capsule()
                                        .fill(
                                            pillar.accent
                                                ? TodayFlowTheme.twilight.opacity(0.1)
                                                : Color.white.opacity(0.76)
                                        )
                                )
                                .overlay(
                                    Capsule()
                                        .stroke(
                                            TodayFlowTheme.twilight.opacity(pillar.accent ? 0.26 : 0.14),
                                            lineWidth: 1
                                        )
                                )
                                .profileMotionReveal(delay: ProfileMotion.staggerDelay(index: index, base: 0.12))
                        }
                    }
                    .padding(.bottom, 16)
                }

                if let sectionLabel {
                    Text(sectionLabel)
                        .font(.caption.weight(.semibold))
                        .tracking(2.2)
                        .textCase(.uppercase)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .padding(.bottom, 6)
                }

                Text(title.uppercased())
                    .font(.system(size: 33, design: .serif).weight(.bold))
                    .tracking(1)
                    .foregroundStyle(TodayFlowTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)

                if let poeticCaption {
                    Text(poeticCaption)
                        .font(.system(.title3, design: .serif))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .padding(.top, 10)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let metaLine {
                    Text(metaLine)
                        .font(.body)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .padding(.top, 8)
                        .fixedSize(horizontal: false, vertical: true)
                }

                if let digest {
                    Text(digest)
                        .font(.body)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .lineLimit(3)
                        .padding(.vertical, 16)
                        .padding(.horizontal, 16)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.68))
                        .overlay(alignment: .leading) {
                            Rectangle()
                                .fill(TodayFlowTheme.twilight)
                                .frame(width: 3)
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                        .padding(.top, 18)
                }

                if !traits.isEmpty {
                    VStack(alignment: .leading, spacing: 10) {
                        ForEach(Array(traits.enumerated()), id: \.element.id) { index, trait in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(trait.title)
                                    .font(.caption.weight(.bold))
                                    .tracking(0.8)
                                    .textCase(.uppercase)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                                Text(trait.subtitle)
                                    .font(.body)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                            .profileMotionReveal(delay: ProfileMotion.staggerDelay(index: index, base: 0.18))
                        }
                    }
                    .padding(.top, 16)
                }
            }
            .profileMotionReveal()
            .frame(maxWidth: innerMaxWidth, alignment: .leading)
            .padding(.horizontal, TodayFlowTheme.Layout.s4)
            .padding(.bottom, 64)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity)
        .frame(minHeight: min(UIScreen.main.bounds.height * 0.88, 720))
        .padding(.horizontal, edgeToEdge ? -TodayFlowTheme.Layout.s4 : 0)
        .clipShape(
            UnevenRoundedRectangle(
                topLeadingRadius: 0,
                bottomLeadingRadius: 36,
                bottomTrailingRadius: 36,
                topTrailingRadius: 0,
                style: .continuous
            )
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("hero-large")
    }

    private var heroBackground: some View {
        ZStack {
            RadialGradient(
                colors: [TodayFlowTheme.twilight.opacity(0.11), Color.clear],
                center: UnitPoint(x: 0.18, y: 0),
                startRadius: 0,
                endRadius: 280
            )
            RadialGradient(
                colors: [Color(red: 198 / 255, green: 166 / 255, blue: 119 / 255).opacity(0.2), Color.clear],
                center: UnitPoint(x: 0.88, y: 0.06),
                startRadius: 0,
                endRadius: 240
            )
            LinearGradient(
                colors: [Color.white.opacity(0.72), TodayFlowTheme.paper],
                startPoint: .top,
                endPoint: .bottom
            )
        }
    }
}

struct HeroLargeInsightPanel<Content: View>: View {
    let eyebrow: String
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(eyebrow)
                .font(.caption.weight(.semibold))
                .tracking(1.8)
                .textCase(.uppercase)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            content()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(red: 255 / 255, green: 253 / 255, blue: 249 / 255).opacity(0.88))
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
        .shadow(color: Color(red: 91 / 255, green: 67 / 255, blue: 35 / 255).opacity(0.06), radius: 24, y: 14)
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(Color(red: 201 / 255, green: 168 / 255, blue: 115 / 255).opacity(0.18), lineWidth: 1)
        )
    }
}

struct HeroLargeChipRow: View {
    let items: [String]

    var body: some View {
        HeroFlowLayout(spacing: 8) {
            ForEach(items, id: \.self) { item in
                Text(item)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(Color.white.opacity(0.92))
                    .clipShape(Capsule())
                    .overlay(
                        Capsule()
                            .stroke(Color(red: 201 / 255, green: 168 / 255, blue: 115 / 255).opacity(0.28), lineWidth: 1)
                    )
            }
        }
    }
}

// MARK: - Sacred geometry backdrop (soft)

private struct HeroLargeSacredGeometryBackdrop: View {
    var body: some View {
        FoundationGeometryView(preset: .profile, emphasis: .soft)
    }
}

// MARK: - Simple flow layout for pillar/chip rows

struct HeroFlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        let width = proposal.width ?? rows.map(\.width).max() ?? 0
        let height = rows.reduce(0) { $0 + $1.height } + CGFloat(max(0, rows.count - 1)) * spacing
        return CGSize(width: width, height: height)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let rows = computeRows(proposal: proposal, subviews: subviews)
        var y = bounds.minY
        for row in rows {
            var x = bounds.minX
            for index in row.indices {
                let size = subviews[index].sizeThatFits(.unspecified)
                subviews[index].place(at: CGPoint(x: x, y: y), proposal: ProposedViewSize(size))
                x += size.width + spacing
            }
            y += row.height + spacing
        }
    }

    private struct Row {
        var indices: [Int]
        var width: CGFloat
        var height: CGFloat
    }

    private func computeRows(proposal: ProposedViewSize, subviews: Subviews) -> [Row] {
        let maxWidth = proposal.width ?? .infinity
        var rows: [Row] = []
        var current = Row(indices: [], width: 0, height: 0)

        for (index, subview) in subviews.enumerated() {
            let size = subview.sizeThatFits(.unspecified)
            let nextWidth = current.indices.isEmpty ? size.width : current.width + spacing + size.width
            if !current.indices.isEmpty, nextWidth > maxWidth {
                rows.append(current)
                current = Row(indices: [index], width: size.width, height: size.height)
            } else {
                current.indices.append(index)
                current.width = nextWidth
                current.height = max(current.height, size.height)
            }
        }
        if !current.indices.isEmpty { rows.append(current) }
        return rows
    }
}
