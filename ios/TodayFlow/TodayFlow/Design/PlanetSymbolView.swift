import SwiftUI

// MARK: - Planet symbols (parity web `PlanetIcon` + DS-7 SVG set)

enum PlanetSlug: String, CaseIterable {
    case sun
    case moon
    case mercury
    case venus
    case mars
    case jupiter
    case saturn
    case uranus
    case neptune
    case pluto
}

extension VisualIdentityRegistry {
    static func resolvePlanetSlug(_ raw: String?) -> PlanetSlug? {
        let key = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch key {
        case "sun", "солнце":
            return .sun
        case "moon", "луна":
            return .moon
        case "mercury", "меркурий":
            return .mercury
        case "venus", "венера":
            return .venus
        case "mars", "марс":
            return .mars
        case "jupiter", "юпитер":
            return .jupiter
        case "saturn", "сатурн":
            return .saturn
        case "uranus", "уран":
            return .uranus
        case "neptune", "нептун":
            return .neptune
        case "pluto", "плутон":
            return .pluto
        default:
            return nil
        }
    }
}

struct PlanetSymbolView: View {
    let planet: String
    var size: CGFloat = 24
    var stroke: Color = TodayFlowTheme.ink.opacity(0.82)

    private var slug: PlanetSlug? {
        VisualIdentityRegistry.resolvePlanetSlug(planet)
    }

    var body: some View {
        Group {
            if let slug {
                planetPaths(slug)
            }
        }
        .foregroundStyle(stroke)
        .frame(width: size, height: size)
        .accessibilityHidden(true)
    }

    private var strokeWidth: CGFloat { max(1.25, size / 56 * 1.5) }

    @ViewBuilder
    private func planetPaths(_ slug: PlanetSlug) -> some View {
        switch slug {
        case .sun:
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.43)
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.14)
        case .moon:
            Path { p in
                p.addArc(center: CGPoint(x: size * 0.607, y: size * 0.321), radius: size * 0.214, startAngle: .degrees(-90), endAngle: .degrees(90), clockwise: false)
                p.addArc(center: CGPoint(x: size * 0.5, y: size * 0.5), radius: size * 0.179, startAngle: .degrees(90), endAngle: .degrees(-90), clockwise: true)
            }
            .stroke(lineWidth: strokeWidth)
        case .mercury:
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.357).offset(y: -size * 0.036)
            Path { p in
                p.move(to: CGPoint(x: size * 0.393, y: size * 0.286))
                p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.393))
                p.move(to: CGPoint(x: size * 0.607, y: size * 0.286))
                p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.393))
                p.move(to: CGPoint(x: size * 0.5, y: size * 0.643))
                p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.786))
                p.move(to: CGPoint(x: size * 0.429, y: size * 0.75))
                p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.75))
            }
            .stroke(lineWidth: strokeWidth)
        case .venus:
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.357).offset(y: -size * 0.071)
            Path { p in
                p.move(to: CGPoint(x: size * 0.5, y: size * 0.607))
                p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.893))
                p.move(to: CGPoint(x: size * 0.429, y: size * 0.75))
                p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.75))
            }
            .stroke(lineWidth: strokeWidth)
        case .mars:
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.357).offset(x: -size * 0.071, y: size * 0.071)
            Path { p in
                p.move(to: CGPoint(x: size * 0.571, y: size * 0.429))
                p.addLine(to: CGPoint(x: size * 0.893, y: size * 0.107))
                p.move(to: CGPoint(x: size * 0.821, y: size * 0.107))
                p.addLine(to: CGPoint(x: size * 0.893, y: size * 0.179))
            }
            .stroke(lineWidth: strokeWidth)
        case .jupiter:
            Path { p in
                p.move(to: CGPoint(x: size * 0.607, y: size * 0.286))
                p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.571))
                p.move(to: CGPoint(x: size * 0.393, y: size * 0.5))
                p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.5))
                p.move(to: CGPoint(x: size * 0.393, y: size * 0.357))
                p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.643))
            }
            .stroke(lineWidth: strokeWidth)
        case .saturn:
            Path { p in
                p.move(to: CGPoint(x: size * 0.393, y: size * 0.714))
                p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.357))
                p.move(to: CGPoint(x: size * 0.607, y: size * 0.714))
                p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.357))
                p.move(to: CGPoint(x: size * 0.321, y: size * 0.5))
                p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.5))
                p.move(to: CGPoint(x: size * 0.429, y: size * 0.714))
                p.addLine(to: CGPoint(x: size * 0.429, y: size * 0.821))
                p.move(to: CGPoint(x: size * 0.571, y: size * 0.714))
                p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.821))
            }
            .stroke(lineWidth: strokeWidth)
        case .uranus:
            Path { p in
                p.move(to: CGPoint(x: size * 0.393, y: size * 0.679))
                p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.321))
                p.move(to: CGPoint(x: size * 0.607, y: size * 0.679))
                p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.321))
                p.move(to: CGPoint(x: size * 0.321, y: size * 0.5))
                p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.5))
            }
            .stroke(lineWidth: strokeWidth)
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.179).offset(y: -size * 0.25)
        case .neptune:
            Path { p in
                p.move(to: CGPoint(x: size * 0.5, y: size * 0.75))
                p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.393))
                p.move(to: CGPoint(x: size * 0.357, y: size * 0.393))
                p.addLine(to: CGPoint(x: size * 0.357, y: size * 0.536))
                p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.429))
                p.addLine(to: CGPoint(x: size * 0.643, y: size * 0.536))
                p.addLine(to: CGPoint(x: size * 0.643, y: size * 0.393))
            }
            .stroke(lineWidth: strokeWidth)
        case .pluto:
            Circle().stroke(lineWidth: strokeWidth).scaleEffect(0.321).offset(x: -size * 0.071)
            Path { p in
                p.move(to: CGPoint(x: size * 0.589, y: size * 0.464))
                p.addLine(to: CGPoint(x: size * 0.821, y: size * 0.464))
                p.move(to: CGPoint(x: size * 0.661, y: size * 0.393))
                p.addLine(to: CGPoint(x: size * 0.661, y: size * 0.536))
            }
            .stroke(lineWidth: strokeWidth)
        }
    }
}
