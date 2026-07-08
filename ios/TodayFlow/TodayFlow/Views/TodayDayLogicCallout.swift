import SwiftUI

/// Паритет с `TodayDayLogicCallout.tsx` на вебе: «Опора дня» + при необходимости «Логика дня» в одном визуальном блоке.
struct TodayDayLogicCallout: View {
    enum Style {
        case ritual
        case guideHero
    }

    let style: Style
    let engine: TodayGuideActionable.DayEngineBriefDisplay?
    let model: TodayGuideActionable.DayModelBriefDisplay?

    private var engineAnchorInk: Double {
        switch style {
        case .ritual: return 0.88
        case .guideHero: return 0.82
        }
    }

    private var secondaryInk: Double {
        switch style {
        case .ritual: return 0.72
        case .guideHero: return 0.68
        }
    }

    private var showGoldStroke: Bool {
        style == .ritual
    }

    var body: some View {
        if let eng = engine {
            engineBlock(eng)
        } else if let m = model {
            modelOnlyBlock(m)
        }
    }

    @ViewBuilder
    private func engineBlock(_ eng: TodayGuideActionable.DayEngineBriefDisplay) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(TodayRitualCopy.dayEngineBriefEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(eng.anchor)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(engineAnchorInk))
                .fixedSize(horizontal: false, vertical: true)
            ForEach(Array(eng.hints.enumerated()), id: \.offset) { _, hint in
                Text(hint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(secondaryInk))
                    .fixedSize(horizontal: false, vertical: true)
            }
            if let dm = model {
                if let vs = dm.vectorSummary, !vs.isEmpty {
                    Text(vs)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(secondaryInk))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text("\(TodayRitualCopy.dayModelOneFocusLabel): \(dm.oneFocus)")
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(secondaryInk))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.38))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .optionalGoldStroke(show: showGoldStroke)
    }

    @ViewBuilder
    private func modelOnlyBlock(_ dm: TodayGuideActionable.DayModelBriefDisplay) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(TodayRitualCopy.dayModelBriefEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            if let vs = dm.vectorSummary, !vs.isEmpty {
                Text(vs)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(engineAnchorInk))
                    .fixedSize(horizontal: false, vertical: true)
            }
            Text("\(TodayRitualCopy.dayModelOneFocusLabel): \(dm.oneFocus)")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(engineAnchorInk))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.38))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .optionalGoldStroke(show: showGoldStroke)
    }
}

private extension View {
    @ViewBuilder
    func optionalGoldStroke(show: Bool) -> some View {
        if show {
            overlay {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
            }
        } else {
            self
        }
    }
}
