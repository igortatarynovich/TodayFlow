import SwiftUI

/// Векторный fallback для входа «Твой день»: дюны и солнце на горизонте (макет), если в `today-ritual-entry/` нет PNG/WebP.
struct RitualDesertEntryVectorHero: View {
    var energyScore: Int = 50

    var body: some View {
        GeometryReader { geo in
            let w = geo.size.width
            let h = geo.size.height
            let warmth = CGFloat(min(100, max(0, energyScore))) / 100
            ZStack {
                skyGradient(width: w, height: h, warmth: warmth)
                sunGlow(width: w, height: h, warmth: warmth)
                sunDisc(width: w, height: h, warmth: warmth)
                DesertDuneLayer(offset: 0, phase: 0)
                    .fill(Color(red: 0.86, green: 0.72, blue: 0.58))
                    .opacity(0.98)
                DesertDuneLayer(offset: 0.08, phase: 0.12)
                    .fill(Color(red: 0.78, green: 0.62, blue: 0.48))
                    .opacity(0.94)
                DesertDuneLayer(offset: -0.05, phase: 0.22)
                    .fill(Color(red: 0.72, green: 0.56, blue: 0.44))
                    .opacity(0.9)
                foregroundDuneRidge(width: w, height: h)
                sparkles(width: w, height: h)
            }
            .frame(width: w, height: h)
        }
    }

    private func skyGradient(width w: CGFloat, height h: CGFloat, warmth: CGFloat) -> some View {
        let top = Color(red: 0.99, green: 0.97, blue: 0.94)
        let mid = Color(red: 1, green: 0.93, blue: 0.84 + warmth * 0.04)
        let horizon = Color(red: 0.98, green: 0.88, blue: 0.72 + warmth * 0.06)
        return LinearGradient(
            colors: [top, mid, horizon],
            startPoint: .top,
            endPoint: .bottom
        )
    }

    private func sunGlow(width w: CGFloat, height h: CGFloat, warmth: CGFloat) -> some View {
        let cx = w * 0.62
        let cy = h * 0.52
        let glow = Color(red: 1, green: 0.92 + warmth * 0.05, blue: 0.72)
        return RadialGradient(
            colors: [glow.opacity(0.55), glow.opacity(0.12), Color.clear],
            center: UnitPoint(x: 0.5, y: 0.5),
            startRadius: w * 0.04,
            endRadius: w * 0.42
        )
        .frame(width: w * 0.88, height: w * 0.5)
        .position(x: cx, y: cy)
    }

    private func sunDisc(width w: CGFloat, height h: CGFloat, warmth: CGFloat) -> some View {
        let cx = w * 0.62
        let cy = h * 0.56
        let core = Color(red: 1, green: 0.96, blue: 0.78 + warmth * 0.08)
        let rim = Color(red: 1, green: 0.82, blue: 0.52 + warmth * 0.1)
        return Circle()
            .fill(
                RadialGradient(
                    colors: [core, rim],
                    center: .center,
                    startRadius: 0,
                    endRadius: w * 0.14
                )
            )
            .frame(width: w * 0.2, height: w * 0.2)
            .shadow(color: Color(red: 1, green: 0.75, blue: 0.45).opacity(0.55), radius: w * 0.06, y: w * 0.01)
            .position(x: cx, y: cy)
    }

    private func foregroundDuneRidge(width w: CGFloat, height h: CGFloat) -> some View {
        Path { p in
            let y0 = h * 0.62
            p.move(to: CGPoint(x: 0, y: y0))
            p.addCurve(
                to: CGPoint(x: w, y: y0 + h * 0.04),
                control1: CGPoint(x: w * 0.28, y: h * 0.48),
                control2: CGPoint(x: w * 0.72, y: h * 0.58)
            )
            p.addLine(to: CGPoint(x: w, y: h))
            p.addLine(to: CGPoint(x: 0, y: h))
            p.closeSubpath()
        }
        .fill(
            LinearGradient(
                colors: [
                    Color(red: 0.94, green: 0.78, blue: 0.62),
                    Color(red: 0.88, green: 0.68, blue: 0.52),
                ],
                startPoint: .top,
                endPoint: .bottom
            )
        )
    }

    private func sparkles(width w: CGFloat, height h: CGFloat) -> some View {
        ForEach(0..<12, id: \.self) { i in
            let seed = CGFloat((i * 17 + 3) % 100) / 100
            let x = w * (0.12 + seed * 0.76)
            let y = h * (0.12 + CGFloat(i % 5) * 0.08 + seed * 0.18)
            Circle()
                .fill(Color.white.opacity(0.25 + Double(i % 3) * 0.12))
                .frame(width: w * (0.008 + seed * 0.01), height: w * (0.008 + seed * 0.01))
                .position(x: x, y: y)
        }
    }
}

/// Волнистый слой песка; `phase` сдвигает кривые по X в долях ширины.
private struct DesertDuneLayer: Shape {
    var offset: CGFloat
    var phase: CGFloat

    func path(in rect: CGRect) -> Path {
        let w = rect.width
        let h = rect.height
        let baseY = h * (0.58 + offset * 0.08)
        var p = Path()
        p.move(to: CGPoint(x: 0, y: baseY))
        p.addCurve(
            to: CGPoint(x: w * 0.5, y: baseY - h * 0.06),
            control1: CGPoint(x: w * (0.12 + phase), y: baseY - h * 0.18),
            control2: CGPoint(x: w * (0.38 + phase * 0.5), y: baseY - h * 0.02)
        )
        p.addCurve(
            to: CGPoint(x: w, y: baseY + h * 0.02),
            control1: CGPoint(x: w * (0.62 - phase * 0.3), y: baseY + h * 0.04),
            control2: CGPoint(x: w * (0.88 - phase), y: baseY - h * 0.1)
        )
        p.addLine(to: CGPoint(x: w, y: h))
        p.addLine(to: CGPoint(x: 0, y: h))
        p.closeSubpath()
        return p
    }
}
