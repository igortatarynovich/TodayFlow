import SwiftUI

// MARK: - Zodiac symbols (parity web `ZodiacIcon` + DS-9 SVG set)

enum ZodiacSlug: String, CaseIterable {
    case aries
    case taurus
    case gemini
    case cancer
    case leo
    case virgo
    case libra
    case scorpio
    case sagittarius
    case capricorn
    case aquarius
    case pisces
}

extension VisualIdentityRegistry {
    static func resolveZodiacSlug(_ raw: String?) -> ZodiacSlug? {
        let key = (raw ?? "").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        switch key {
        case "aries", "овен":
            return .aries
        case "taurus", "телец":
            return .taurus
        case "gemini", "близнецы":
            return .gemini
        case "cancer", "рак":
            return .cancer
        case "leo", "лев":
            return .leo
        case "virgo", "дева":
            return .virgo
        case "libra", "весы":
            return .libra
        case "scorpio", "скорпион":
            return .scorpio
        case "sagittarius", "стрелец":
            return .sagittarius
        case "capricorn", "козерог":
            return .capricorn
        case "aquarius", "водолей":
            return .aquarius
        case "pisces", "рыбы":
            return .pisces
        default:
            return ZodiacSlug(rawValue: key)
        }
    }
}

struct ZodiacSymbolView: View {
    let sign: String
    var size: CGFloat = 28
    var stroke: Color = TodayFlowTheme.ink.opacity(0.82)

    private var slug: ZodiacSlug? {
        VisualIdentityRegistry.resolveZodiacSlug(sign)
    }

    var body: some View {
        Group {
            if let slug {
                zodiacPaths(slug)
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
    private func zodiacPaths(_ slug: ZodiacSlug) -> some View {
        switch slug {
        case .aries:
            Path { path in
                path.move(to: p(8, 20))
                path.addQuadCurve(to: p(14, 10), control: p(10, 12))
                path.move(to: p(20, 20))
                path.addQuadCurve(to: p(14, 10), control: p(18, 12))
                path.move(to: p(14, 10))
                path.addLine(to: p(14, 6))
                path.move(to: p(11, 8))
                path.addLine(to: p(17, 8))
            }
            .stroke(lineWidth: strokeWidth)
        case .taurus:
            ZStack {
                Circle().stroke(lineWidth: strokeWidth).frame(width: 12 * unit, height: 12 * unit).position(p(14, 15))
                Path { path in
                    path.move(to: p(10, 9))
                    path.addQuadCurve(to: p(18, 9), control: p(14, 5))
                }
                .stroke(lineWidth: strokeWidth)
            }
        case .gemini:
            Path { path in
                path.move(to: p(10, 6))
                path.addLine(to: p(10, 22))
                path.move(to: p(18, 6))
                path.addLine(to: p(18, 22))
                path.move(to: p(10, 10))
                path.addLine(to: p(18, 10))
                path.move(to: p(10, 18))
                path.addLine(to: p(18, 18))
            }
            .stroke(lineWidth: strokeWidth)
        case .cancer:
            Path { path in
                path.move(to: p(9, 16))
                path.addQuadCurve(to: p(17, 14), control: p(14, 20))
                path.move(to: p(19, 12))
                path.addQuadCurve(to: p(11, 14), control: p(14, 8))
            }
            .stroke(lineWidth: strokeWidth)
        case .leo:
            ZStack {
                Circle().stroke(lineWidth: strokeWidth).frame(width: 10 * unit, height: 10 * unit).position(p(14, 14))
                Path { path in
                    path.move(to: p(14, 9))
                    path.addLine(to: p(14, 5))
                    path.move(to: p(10, 7))
                    path.addLine(to: p(8, 5))
                    path.move(to: p(18, 7))
                    path.addLine(to: p(20, 5))
                }
                .stroke(lineWidth: strokeWidth)
            }
        case .virgo:
            Path { path in
                path.move(to: p(10, 8))
                path.addLine(to: p(10, 20))
                path.move(to: p(14, 8))
                path.addLine(to: p(14, 16))
                path.addQuadCurve(to: p(18, 20), control: p(18, 16))
                path.move(to: p(18, 8))
                path.addLine(to: p(18, 12))
            }
            .stroke(lineWidth: strokeWidth)
        case .libra:
            Path { path in
                path.move(to: p(8, 18))
                path.addLine(to: p(20, 18))
                path.move(to: p(10, 14))
                path.addLine(to: p(18, 14))
                path.move(to: p(14, 8))
                path.addLine(to: p(14, 14))
            }
            .stroke(lineWidth: strokeWidth)
        case .scorpio:
            Path { path in
                path.move(to: p(10, 8))
                path.addLine(to: p(10, 18))
                path.move(to: p(14, 8))
                path.addLine(to: p(14, 14))
                path.addQuadCurve(to: p(18, 18), control: p(18, 14))
                path.move(to: p(18, 18))
                path.addLine(to: p(21, 21))
            }
            .stroke(lineWidth: strokeWidth)
        case .sagittarius:
            Path { path in
                path.move(to: p(8, 20))
                path.addLine(to: p(18, 10))
                path.move(to: p(12, 10))
                path.addLine(to: p(18, 10))
                path.addLine(to: p(18, 16))
            }
            .stroke(lineWidth: strokeWidth)
        case .capricorn:
            Path { path in
                path.move(to: p(9, 8))
                path.addLine(to: p(9, 18))
                path.addQuadCurve(to: p(15, 20), control: p(15, 18))
                path.move(to: p(15, 8))
                path.addQuadCurve(to: p(19, 13), control: p(19, 8))
                path.addLine(to: p(19, 18))
            }
            .stroke(lineWidth: strokeWidth)
        case .aquarius:
            Path { path in
                path.move(to: p(7, 10))
                path.addLine(to: p(11, 10))
                path.addLine(to: p(13, 8))
                path.addLine(to: p(15, 10))
                path.addLine(to: p(19, 10))
                path.move(to: p(7, 16))
                path.addLine(to: p(11, 16))
                path.addLine(to: p(13, 14))
                path.addLine(to: p(15, 16))
                path.addLine(to: p(19, 16))
            }
            .stroke(lineWidth: strokeWidth)
        case .pisces:
            Path { path in
                path.move(to: p(10, 8))
                path.addQuadCurve(to: p(10, 20), control: p(7, 14))
                path.move(to: p(18, 8))
                path.addQuadCurve(to: p(18, 20), control: p(21, 14))
                path.move(to: p(14, 8))
                path.addLine(to: p(14, 20))
            }
            .stroke(lineWidth: strokeWidth)
        }
    }
}
