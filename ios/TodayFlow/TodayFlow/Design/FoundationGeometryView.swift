import SwiftUI

// MARK: - Foundation Geometry (TODAYFLOW_FOUNDATION_UI §3)

enum FoundationGeometryPreset {
    case profile
    case today
    case portal
}

enum FoundationGeometryEmphasis {
    case soft
    case strong
}

enum FoundationGeometryTone {
    case light
    case dark
}

struct FoundationGeometryView: View {
    var preset: FoundationGeometryPreset
    var emphasis: FoundationGeometryEmphasis = .soft
    var tone: FoundationGeometryTone = .light

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            let cx = w * 0.5
            let cy = h * (preset == .today ? 0.46 : preset == .portal ? 0.5 : 0.43)
            let scale = min(w, h) / 280

            ZStack {
                switch preset {
                case .profile:
                    profileLayers(cx: cx, cy: cy, scale: scale)
                case .today:
                    todayLayers(cx: cx, cy: cy, scale: scale)
                case .portal:
                    portalLayers(cx: cx, cy: cy, w: w, h: h, scale: scale)
                }
            }
        }
    }

    private var g1Stroke: Color {
        tone == .dark ? Color(red: 250 / 255, green: 248 / 255, blue: 245 / 255).opacity(0.14) : TodayFlowTheme.twilight.opacity(emphasis == .strong ? 0.2 : 0.14)
    }

    private var g2Stroke: Color {
        tone == .dark ? Color(red: 210 / 255, green: 195 / 255, blue: 255 / 255).opacity(0.2) : TodayFlowTheme.sunset.opacity(emphasis == .strong ? 0.24 : 0.14)
    }

    private var g4Stroke: Color {
        tone == .dark ? Color(red: 250 / 255, green: 248 / 255, blue: 245 / 255).opacity(0.1) : TodayFlowTheme.twilight.opacity(emphasis == .strong ? 0.14 : 0.1)
    }

    private var nodeFill: Color {
        tone == .dark ? Color(red: 210 / 255, green: 195 / 255, blue: 255 / 255).opacity(0.45) : TodayFlowTheme.sunset.opacity(emphasis == .strong ? 0.45 : 0.35)
    }

    @ViewBuilder
    private func profileLayers(cx: CGFloat, cy: CGFloat, scale: CGFloat) -> some View {
        Circle()
            .stroke(g1Stroke, lineWidth: 1)
            .frame(width: 96 * scale * 2, height: 96 * scale * 2)
            .position(x: cx, y: cy)
        Circle()
            .stroke(g1Stroke.opacity(0.85), lineWidth: 1)
            .frame(width: 64 * scale * 2, height: 64 * scale * 2)
            .position(x: cx, y: cy)
        Circle()
            .stroke(g1Stroke.opacity(0.7), style: StrokeStyle(lineWidth: 1, dash: [4, 6]))
            .frame(width: 36 * scale * 2, height: 36 * scale * 2)
            .position(x: cx, y: cy)
        Ellipse()
            .stroke(g2Stroke, lineWidth: 1)
            .frame(width: 120 * scale * 2, height: 44 * scale * 2)
            .rotationEffect(.degrees(-18))
            .position(x: cx, y: cy)
        Path { path in
            path.move(to: CGPoint(x: cx - 120 * scale, y: cy - 60 * scale))
            path.addLine(to: CGPoint(x: cx + 120 * scale, y: cy + 60 * scale))
        }
        .stroke(g4Stroke, lineWidth: 1.25)
        Circle()
            .fill(nodeFill)
            .frame(width: 6, height: 6)
            .position(x: cx + 96 * scale, y: cy - 48 * scale)
    }

    @ViewBuilder
    private func todayLayers(cx: CGFloat, cy: CGFloat, scale: CGFloat) -> some View {
        Ellipse()
            .stroke(g2Stroke, lineWidth: 1)
            .frame(width: 118 * scale * 2, height: 42 * scale * 2)
            .rotationEffect(.degrees(-14))
            .position(x: cx, y: cy)
        Ellipse()
            .stroke(g2Stroke.opacity(0.85), style: StrokeStyle(lineWidth: 1, dash: [3, 5]))
            .frame(width: 92 * scale * 2, height: 32 * scale * 2)
            .rotationEffect(.degrees(22))
            .position(x: cx, y: cy)
        Circle()
            .stroke(g1Stroke.opacity(0.7), style: StrokeStyle(lineWidth: 1, dash: [4, 6]))
            .frame(width: 28 * scale * 2, height: 28 * scale * 2)
            .position(x: cx, y: cy)
    }

    @ViewBuilder
    private func portalLayers(cx: CGFloat, cy: CGFloat, w: CGFloat, h: CGFloat, scale: CGFloat) -> some View {
        let gridStep: CGFloat = 20 * scale
        let cols = Int(w / gridStep) + 1
        let rows = Int(h / gridStep) + 1
        ForEach(0..<rows, id: \.self) { row in
            ForEach(0..<cols, id: \.self) { col in
                let x = CGFloat(col) * gridStep
                let y = CGFloat(row) * gridStep
                Path { path in
                    path.move(to: CGPoint(x: x + gridStep, y: y))
                    path.addLine(to: CGPoint(x: x, y: y))
                    path.addLine(to: CGPoint(x: x, y: y + gridStep))
                }
                .stroke(g4Stroke.opacity(0.55), lineWidth: 1)
            }
        }
        Circle()
            .stroke(g1Stroke, lineWidth: 1)
            .frame(width: 88 * scale * 2, height: 88 * scale * 2)
            .position(x: cx, y: cy)
        Ellipse()
            .stroke(g2Stroke, lineWidth: 1.25)
            .frame(width: 130 * scale * 2, height: 48 * scale * 2)
            .rotationEffect(.degrees(-12))
            .position(x: cx, y: cy)
        Path { path in
            path.move(to: CGPoint(x: w * 0.1, y: cy))
            path.addLine(to: CGPoint(x: w * 0.9, y: cy))
        }
        .stroke(g4Stroke, lineWidth: 1.25)
        Path { path in
            path.move(to: CGPoint(x: cx, y: h * 0.08))
            path.addLine(to: CGPoint(x: cx, y: h * 0.92))
        }
        .stroke(g4Stroke, lineWidth: 1.25)
        Circle()
            .fill(nodeFill)
            .frame(width: 6, height: 6)
            .position(x: cx + 100 * scale, y: cy - 72 * scale)
    }
}
