import SwiftUI

// MARK: - Visual identity registry (parity web `registry.ts`)

enum ArchetypeSlug: String, CaseIterable {
    case sage
    case explorer
    case architect
    case harmonizer
    case observer
    case creator
    case strategist
    case seeker
    case mentor
    case guardian
    case visionary
    case catalyst
    case unknown
}

enum VisualIdentityRegistry {
    static func resolveArchetypeSlug(_ seed: String?) -> ArchetypeSlug {
        let key = (seed ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .replacingOccurrences(of: "\\s+", with: "_", options: .regularExpression)
        switch key {
        case "sage", "мудрец":
            return .sage
        case "explorer", "исследователь":
            return .explorer
        case "architect", "архитектор", "правитель", "ruler":
            return .architect
        case "harmonizer", "гармонизатор", "любовник", "lover":
            return .harmonizer
        case "observer", "наблюдатель", "славный_малый", "everyman":
            return .observer
        case "creator", "создатель", "творец":
            return .creator
        case "strategist", "стратег", "герой", "hero":
            return .strategist
        case "seeker", "искатель", "initiate":
            return .seeker
        case "mentor", "наставник", "маг", "magician":
            return .mentor
        case "guardian", "хранитель", "заботливый", "caregiver":
            return .guardian
        case "visionary", "провидец", "невинный", "innocent":
            return .visionary
        case "catalyst", "катализатор", "alchemist", "бунтарь", "rebel", "outlaw":
            return .catalyst
        case "oracle":
            return .sage
        case "строитель":
            return .architect
        default:
            return .unknown
        }
    }
}

// MARK: - Archetype symbol (parity web `ArchetypeSymbol` + inline icons)

struct ArchetypeSymbolView: View {
    let seed: String
    var size: CGFloat = 56
    var stroke: Color = TodayFlowTheme.ink.opacity(0.82)

    private var slug: ArchetypeSlug {
        VisualIdentityRegistry.resolveArchetypeSlug(seed)
    }

    var body: some View {
        ZStack {
            switch slug {
            case .sage:
                sagePaths
            case .explorer:
                explorerPaths
            case .architect:
                architectPaths
            case .harmonizer:
                harmonizerPaths
            case .observer:
                observerPaths
            case .creator:
                creatorPaths
            case .strategist:
                strategistPaths
            case .seeker:
                seekerPaths
            case .mentor:
                mentorPaths
            case .guardian:
                guardianPaths
            case .visionary:
                visionaryPaths
            case .catalyst:
                catalystPaths
            case .unknown:
                unknownPaths
            }
        }
        .foregroundStyle(stroke)
        .frame(width: size, height: size)
        .accessibilityHidden(true)
    }

    private var strokeWidth: CGFloat { max(1.25, size / 56 * 1.5) }

    @ViewBuilder
    private var sagePaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.286, y: size * 0.679))
            p.addLine(to: CGPoint(x: size * 0.286, y: size * 0.321))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.214))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.321))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.679))
        }
        .stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.393, y: size * 0.571))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.571))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.679))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var explorerPaths: some View {
        Circle().stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.393))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.607))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.714))
            p.move(to: CGPoint(x: size * 0.286, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.5))
            p.move(to: CGPoint(x: size * 0.607, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.5))
        }
        .stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.429, y: size * 0.5))
            p.closeSubpath()
        }
        .fill(stroke.opacity(0.35))
    }

    @ViewBuilder
    private var architectPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.286, y: size * 0.714))
            p.addLine(to: CGPoint(x: size * 0.286, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.714))
        }
        .stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.286, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.5))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.714))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var harmonizerPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.321, y: size * 0.607))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.607))
        }
        .stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.393, y: size * 0.607))
            p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.464, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.536, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.607))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var observerPaths: some View {
        Circle().stroke(lineWidth: strokeWidth)
            .scaleEffect(0.714)
        Circle().stroke(lineWidth: strokeWidth)
            .scaleEffect(0.286)
    }

    @ViewBuilder
    private var creatorPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.25))
            p.addLine(to: CGPoint(x: size * 0.554, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.482))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.607))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.518))
            p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.607))
            p.addLine(to: CGPoint(x: size * 0.429, y: size * 0.482))
            p.addLine(to: CGPoint(x: size * 0.321, y: size * 0.393))
            p.addLine(to: CGPoint(x: size * 0.446, y: size * 0.393))
            p.closeSubpath()
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var strategistPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.357, y: size * 0.679))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.643, y: size * 0.679))
        }
        .stroke(lineWidth: strokeWidth)
        Path { p in
            p.move(to: CGPoint(x: size * 0.429, y: size * 0.536))
            p.addLine(to: CGPoint(x: size * 0.571, y: size * 0.536))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var unknownPaths: some View {
        Circle().stroke(lineWidth: strokeWidth)
            .scaleEffect(0.875)
        Path { p in
            p.move(to: CGPoint(x: size * 0.393, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.5))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var seekerPaths: some View {
        Circle().stroke(lineWidth: strokeWidth)
            .frame(width: size * 0.286, height: size * 0.286)
            .position(x: size * 0.429, y: size * 0.429)
        Path { p in
            p.move(to: CGPoint(x: size * 0.536, y: size * 0.536))
            p.addLine(to: CGPoint(x: size * 0.714, y: size * 0.714))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.25))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.321))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.679))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.75))
            p.move(to: CGPoint(x: size * 0.25, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.321, y: size * 0.5))
            p.move(to: CGPoint(x: size * 0.679, y: size * 0.5))
            p.addLine(to: CGPoint(x: size * 0.75, y: size * 0.5))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var mentorPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.321, y: size * 0.321))
            p.addLine(to: CGPoint(x: size * 0.321, y: size * 0.679))
            p.move(to: CGPoint(x: size * 0.679, y: size * 0.321))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.679))
            p.move(to: CGPoint(x: size * 0.321, y: size * 0.429))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.429))
            p.move(to: CGPoint(x: size * 0.321, y: size * 0.571))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.571))
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.25))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.321))
        }
        .stroke(lineWidth: strokeWidth)
        Circle().stroke(lineWidth: strokeWidth)
            .frame(width: size * 0.071, height: size * 0.071)
            .position(x: size * 0.5, y: size * 0.214)
    }

    @ViewBuilder
    private var guardianPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.214))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.286))
            p.addLine(to: CGPoint(x: size * 0.679, y: size * 0.5))
            p.addQuadCurve(to: CGPoint(x: size * 0.5, y: size * 0.714), control: CGPoint(x: size * 0.679, y: size * 0.643))
            p.addQuadCurve(to: CGPoint(x: size * 0.321, y: size * 0.5), control: CGPoint(x: size * 0.321, y: size * 0.643))
            p.addLine(to: CGPoint(x: size * 0.321, y: size * 0.286))
            p.closeSubpath()
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.357))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.571))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var visionaryPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.286, y: size * 0.5))
            p.addQuadCurve(to: CGPoint(x: size * 0.5, y: size * 0.25), control: CGPoint(x: size * 0.286, y: size * 0.321))
            p.addQuadCurve(to: CGPoint(x: size * 0.714, y: size * 0.5), control: CGPoint(x: size * 0.714, y: size * 0.321))
            p.addQuadCurve(to: CGPoint(x: size * 0.5, y: size * 0.75), control: CGPoint(x: size * 0.714, y: size * 0.679))
            p.addQuadCurve(to: CGPoint(x: size * 0.286, y: size * 0.5), control: CGPoint(x: size * 0.286, y: size * 0.679))
        }
        .stroke(lineWidth: strokeWidth)
        Circle().stroke(lineWidth: strokeWidth)
            .scaleEffect(0.143)
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.143))
            p.addLine(to: CGPoint(x: size * 0.5, y: size * 0.214))
            p.move(to: CGPoint(x: size * 0.357, y: size * 0.214))
            p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.268))
            p.move(to: CGPoint(x: size * 0.643, y: size * 0.214))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.268))
        }
        .stroke(lineWidth: strokeWidth)
    }

    @ViewBuilder
    private var catalystPaths: some View {
        Path { p in
            p.move(to: CGPoint(x: size * 0.5, y: size * 0.214))
            p.addLine(to: CGPoint(x: size * 0.393, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.464, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.429, y: size * 0.714))
            p.addLine(to: CGPoint(x: size * 0.607, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.536, y: size * 0.464))
            p.addLine(to: CGPoint(x: size * 0.643, y: size * 0.214))
        }
        .stroke(lineWidth: strokeWidth)
        Circle().fill(stroke).frame(width: size * 0.071, height: size * 0.071).position(x: size * 0.321, y: size * 0.679)
        Circle().fill(stroke).frame(width: size * 0.071, height: size * 0.071).position(x: size * 0.679, y: size * 0.679)
    }
}
