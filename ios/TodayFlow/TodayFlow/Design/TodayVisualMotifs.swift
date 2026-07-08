import SwiftUI

// MARK: - Tarot: рубашка колоды (векторная отрисовка в теме приложения)

struct TodayTarotCardBackView: View {
    var cornerRadius: CGFloat = 20

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            let corner = cornerRadius
            ZStack {
                RoundedRectangle(cornerRadius: corner, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(red: 0.18, green: 0.12, blue: 0.28),
                                Color(red: 0.12, green: 0.10, blue: 0.22),
                                Color(red: 0.22, green: 0.14, blue: 0.20),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                RoundedRectangle(cornerRadius: corner, style: .continuous)
                    .stroke(
                        LinearGradient(
                            colors: [
                                TodayFlowTheme.gold.opacity(0.55),
                                TodayFlowTheme.sunset.opacity(0.35),
                                TodayFlowTheme.gold.opacity(0.25),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 2
                    )
                TarotBackRosette(points: 8, scale: 1)
                    .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                    .frame(width: w * 0.72, height: h * 0.72)
                TarotBackRosette(points: 8, scale: 0.58, rotationDeg: 22)
                    .stroke(TodayFlowTheme.sunset.opacity(0.18), lineWidth: 0.85)
                    .frame(width: w * 0.72, height: h * 0.72)
                VStack(spacing: 10) {
                    Image(systemName: "moon.stars.fill")
                        .font(.system(size: 28))
                        .symbolRenderingMode(.palette)
                        .foregroundStyle(TodayFlowTheme.gold, TodayFlowTheme.sunset.opacity(0.85))
                    Text(IOSAppLocale.prefersRussian ? "КАРТА ДНЯ" : "DAILY CARD")
                        .font(.caption.weight(.bold))
                        .tracking(2.2)
                        .foregroundStyle(TodayFlowTheme.gold.opacity(0.92))
                    Text(IOSAppLocale.prefersRussian ? "Нажми, чтобы перевернуть" : "Tap to flip")
                        .font(.caption2)
                        .foregroundStyle(Color.white.opacity(0.45))
                }
                .padding(.horizontal, 16)
            }
        }
    }
}

private struct TarotBackRosette: Shape {
    var points: Int
    var scale: CGFloat
    var rotationDeg: CGFloat = 0

    func path(in rect: CGRect) -> Path {
        var p = Path()
        let c = CGPoint(x: rect.midX, y: rect.midY)
        let r = min(rect.width, rect.height) / 2 * scale
        let rot = rotationDeg * .pi / 180
        guard points >= 3 else { return p }
        for i in 0..<points {
            let t = CGFloat(i) / CGFloat(points) * 2 * .pi + rot
            let pt = CGPoint(x: c.x + cos(t) * r, y: c.y + sin(t) * r)
            if i == 0 { p.move(to: pt) } else { p.addLine(to: pt) }
        }
        p.closeSubpath()
        return p
    }
}

// MARK: - Число дня: типографический «постер»

struct TodayNumerologyDayPosterView: View {
    let reducedNumber: Int?
    let rawValue: Int?
    let titleLine: String
    let dateLabel: String
    let luckyTime: String
    let colorName: String
    let stone: String
    let symbol: String

    var body: some View {
        HStack(alignment: .top, spacing: TodayFlowTheme.Layout.s2) {
            ZStack {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [
                                TodayFlowTheme.twilight.opacity(0.35),
                                TodayFlowTheme.sunset.opacity(0.22),
                                TodayFlowTheme.paper.opacity(0.5),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.35), lineWidth: 1)
                VStack(spacing: 4) {
                    Text(displayNumber)
                        .font(.system(size: 44, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .minimumScaleFactor(0.5)
                        .lineLimit(1)
                    if let rawValue, let reducedNumber, rawValue != reducedNumber {
                        Text("→ \(reducedNumber)")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                    }
                }
                .padding(.vertical, 12)
                .padding(.horizontal, 8)
            }
            .frame(width: 108, height: 112)
            VStack(alignment: .leading, spacing: 8) {
                Text(dateLabel.uppercased())
                    .font(.caption2.weight(.semibold))
                    .tracking(1)
                    .foregroundStyle(TodayFlowTheme.sand)
                Text(titleLine)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.92))
                    .fixedSize(horizontal: false, vertical: true)
                VStack(alignment: .leading, spacing: 6) {
                    posterRow(icon: "clock", text: luckyTime)
                    posterRow(icon: "paintpalette.fill", text: colorName)
                    posterRow(icon: "diamond.fill", text: stone)
                    posterRow(icon: "sparkles", text: symbol)
                }
                .padding(.top, 4)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var displayNumber: String {
        if let n = reducedNumber { return "\(n)" }
        if let v = rawValue { return "\(v)" }
        return "—"
    }

    private func posterRow(icon: String, text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: icon)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.sunset.opacity(0.75))
                .frame(width: 14, alignment: .center)
            Text(text)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

// MARK: - Сферы / метрики: горизонтальная шкала с «ползунком» (только отображение)

/// Плотность дорожки (узкие колонки и сетки — `compact`).
enum TodayFlowSphereSliderDensity {
    case regular
    case compact

    fileprivate var trackHeight: CGFloat {
        switch self {
        case .regular: return 10
        case .compact: return 8
        }
    }

    fileprivate func thumbDiameter(for dynamicTypeSize: DynamicTypeSize) -> CGFloat {
        switch self {
        case .regular:
            switch dynamicTypeSize {
            case .accessibility3, .accessibility4, .accessibility5: return 28
            case .accessibility1, .accessibility2: return 24
            default: return 22
            }
        case .compact:
            switch dynamicTypeSize {
            case .accessibility3, .accessibility4, .accessibility5: return 24
            case .accessibility1, .accessibility2: return 20
            default: return 18
            }
        }
    }
}

/// Акцентный цвет кольца осмысленности (для шкалы и текста).
enum TodayFlowMeaningRingAccent {
    static func color(for ringKey: String) -> Color {
        switch ringKey.lowercased() {
        case "love", "romance", "closeness":
            return TodayFlowTheme.sunset
        case "wealth", "money":
            return TodayFlowTheme.gold
        case "discipline", "work", "order":
            return TodayFlowTheme.twilight
        case "emotional_balance", "emotion", "mood":
            return TodayFlowTheme.sky
        case "purpose", "path":
            return TodayFlowTheme.ember
        case "self_worth", "selfworth", "esteem":
            return TodayFlowTheme.moss
        default:
            return TodayFlowTheme.sunset
        }
    }
}

/// Шкала 0…100 в виде слайдера: дорожка, заливка и круглый маркер по значению (без редактирования).
struct TodayFlowSphereSliderTrack: View {
    let value: Int
    let tint: Color
    /// Подпись для VoiceOver (например название сферы).
    var accessibilityTitle: String? = nil
    var density: TodayFlowSphereSliderDensity = .regular

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var resolvedTrackHeight: CGFloat { density.trackHeight }

    private var thumbDiameter: CGFloat {
        density.thumbDiameter(for: dynamicTypeSize)
    }

    private var clamped: CGFloat {
        max(0, min(CGFloat(value) / 100, 1))
    }

    var body: some View {
        GeometryReader { proxy in
            let w = proxy.size.width
            let trackH = resolvedTrackHeight
            let h = max(trackH, thumbDiameter)
            let midY = h / 2
            let fillW = w * clamped
            let thumbR = thumbDiameter / 2
            let thumbCenterX = min(max(fillW, thumbR), w - thumbR)
            let fillDisplay = max(fillW, clamped > 0 ? trackH * 0.45 : 0)

            ZStack {
                Capsule()
                    .fill(tint.opacity(0.13))
                    .frame(width: w, height: trackH)
                    .position(x: w / 2, y: midY)
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [tint.opacity(0.48), tint],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: fillDisplay, height: trackH)
                    .position(x: fillDisplay / 2, y: midY)
                Circle()
                    .fill(Color.white)
                    .overlay(Circle().stroke(tint, lineWidth: 2.5))
                    .frame(width: thumbDiameter, height: thumbDiameter)
                    .position(x: thumbCenterX, y: midY)
            }
            .frame(width: w, height: h)
        }
        .frame(height: max(resolvedTrackHeight, thumbDiameter))
        .allowsHitTesting(false)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(accessibilityTitle.map { "\($0), \(value) из 100" } ?? "Значение \(value) из 100")
    }
}
