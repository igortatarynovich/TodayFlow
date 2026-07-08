import SwiftUI

// MARK: - Element symbols (parity web `ElementIcon` + DS-11 SVG set)

enum ElementSlug: String, CaseIterable {
    case fire
    case earth
    case air
    case water
}

extension VisualIdentityRegistry {
    static func resolveElementSlug(_ raw: String?) -> ElementSlug? {
        let key = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch key {
        case "fire", "огонь":
            return .fire
        case "earth", "земля":
            return .earth
        case "air", "воздух":
            return .air
        case "water", "вода":
            return .water
        default:
            return ElementSlug(rawValue: key)
        }
    }
}

struct ElementSymbolView: View {
    let element: String
    var size: CGFloat = 24
    var stroke: Color = TodayFlowTheme.ink.opacity(0.82)

    private var slug: ElementSlug? {
        VisualIdentityRegistry.resolveElementSlug(element)
    }

    var body: some View {
        Group {
            if let slug {
                elementPaths(slug)
            }
        }
        .foregroundStyle(stroke)
        .frame(width: size, height: size)
        .accessibilityHidden(true)
    }

    private var strokeWidth: CGFloat { max(1.25, size / 28 * 1.5) }
    private var unit: CGFloat { size / 28 }

    private func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
        CGPoint(x: x * unit, y: y * unit)
    }

    @ViewBuilder
    private func elementPaths(_ slug: ElementSlug) -> some View {
        switch slug {
        case .fire:
            Path { path in
                path.move(to: p(14, 23))
                path.addLine(to: p(14, 9))
                path.move(to: p(10, 21))
                path.addQuadCurve(to: p(14, 12), control: p(12, 16))
                path.move(to: p(18, 21))
                path.addQuadCurve(to: p(14, 12), control: p(16, 16))
                path.move(to: p(11, 11))
                path.addLine(to: p(17, 11))
                path.addLine(to: p(14, 7))
                path.closeSubpath()
            }
            .stroke(lineWidth: strokeWidth)
        case .earth:
            ZStack {
                Circle()
                    .stroke(lineWidth: strokeWidth)
                    .frame(width: 12 * unit, height: 12 * unit)
                    .position(p(14, 14))
                Path { path in
                    path.move(to: p(14, 8))
                    path.addLine(to: p(14, 20))
                    path.move(to: p(8, 14))
                    path.addLine(to: p(20, 14))
                }
                .stroke(lineWidth: strokeWidth)
            }
        case .air:
            Path { path in
                path.move(to: p(6, 10))
                path.addLine(to: p(22, 10))
                path.move(to: p(8, 14))
                path.addLine(to: p(20, 14))
                path.move(to: p(6, 18))
                path.addLine(to: p(22, 18))
                path.move(to: p(20, 10))
                path.addLine(to: p(22, 8))
                path.move(to: p(20, 18))
                path.addLine(to: p(22, 20))
            }
            .stroke(lineWidth: strokeWidth)
        case .water:
            Path { path in
                path.move(to: p(6, 12))
                path.addQuadCurve(to: p(14, 12), control: p(10, 10))
                path.addQuadCurve(to: p(22, 12), control: p(18, 14))
                path.move(to: p(6, 17))
                path.addQuadCurve(to: p(14, 17), control: p(10, 19))
                path.addQuadCurve(to: p(22, 17), control: p(18, 15))
                path.move(to: p(14, 8))
                path.addLine(to: p(14, 20))
            }
            .stroke(lineWidth: strokeWidth)
        }
    }
}
