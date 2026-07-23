import UIKit
import SwiftUI

// MARK: - Archetype illustrations (parity web `registry.ts` SEED_TO_ILLUSTRATION)

enum ArchetypeIllustrationSlug: String, CaseIterable {
    case pravitel
    case tvorets
    case mudrets
    case geroi
    case buntar
    case liubovnik
    case liubovnikF = "liubovnik_f"
    case liubovnikM = "liubovnik_m"
    case iskatel
    case zabotlivyi
    case nevinnyi
    case shut
    case mag
    case slavnyiMalyi = "slavnyi_malyi"
}

enum ArchetypeIllustration {
    /// Product seed → Pearson portrait slug (semantic bridge, not a rename).
    private static let seedToIllustration: [ArchetypeSlug: ArchetypeIllustrationSlug] = [
        .architect: .pravitel,
        .creator: .tvorets,
        .sage: .mudrets,
        .strategist: .geroi,
        .catalyst: .buntar,
        .harmonizer: .liubovnik,
        .seeker: .iskatel,
        .explorer: .iskatel,
        .guardian: .zabotlivyi,
        .mentor: .mag,
        .visionary: .nevinnyi,
        .observer: .slavnyiMalyi,
    ]

    private static let pearsonAlias: [String: ArchetypeIllustrationSlug] = [
        "правитель": .pravitel,
        "творец": .tvorets,
        "мудрец": .mudrets,
        "герой": .geroi,
        "бунтарь": .buntar,
        "любовник": .liubovnik,
        "искатель": .iskatel,
        "заботливый": .zabotlivyi,
        "невинный": .nevinnyi,
        "шут": .shut,
        "маг": .mag,
        "славный_малый": .slavnyiMalyi,
        "ruler": .pravitel,
        "hero": .geroi,
        "rebel": .buntar,
        "outlaw": .buntar,
        "lover": .liubovnik,
        "caregiver": .zabotlivyi,
        "innocent": .nevinnyi,
        "jester": .shut,
        "magician": .mag,
        "everyman": .slavnyiMalyi,
    ]

    static func resolveSlug(_ seed: String?) -> ArchetypeIllustrationSlug? {
        let key = (seed ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
            .replacingOccurrences(of: "\\s+", with: "_", options: .regularExpression)
        guard !key.isEmpty else { return nil }
        if let direct = ArchetypeIllustrationSlug(rawValue: key) { return direct }
        if let alias = pearsonAlias[key] { return alias }
        let machine = VisualIdentityRegistry.resolveArchetypeSlug(seed)
        guard machine != .unknown else { return nil }
        return seedToIllustration[machine]
    }

    static func loadUIImage(seed: String?) -> UIImage? {
        guard let slug = resolveSlug(seed) else { return nil }
        let sub = "archetypes"
        if let url = Bundle.main.url(forResource: slug.rawValue, withExtension: "webp", subdirectory: sub),
           let img = UIImage(contentsOfFile: url.path) {
            return img
        }
        // Fallback without subdirectory (folder-flattened copies).
        if let url = Bundle.main.url(forResource: slug.rawValue, withExtension: "webp"),
           let img = UIImage(contentsOfFile: url.path) {
            return img
        }
        return nil
    }
}

/// Profile Hero visual: premium WebP when mapped + present, else ArchetypeSymbolView.
struct ArchetypeHeroVisual: View {
    let seed: String
    var symbolSize: CGFloat = 120
    var portraitMaxHeight: CGFloat = 260

    var body: some View {
        Group {
            if let uiImage = ArchetypeIllustration.loadUIImage(seed: seed) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFill()
                    .frame(maxWidth: 220, maxHeight: portraitMaxHeight)
                    .clipped()
                    .clipShape(
                        UnevenRoundedRectangle(
                            topLeadingRadius: 110,
                            bottomLeadingRadius: 28,
                            bottomTrailingRadius: 28,
                            topTrailingRadius: 110,
                            style: .continuous
                        )
                    )
                    .overlay {
                        UnevenRoundedRectangle(
                            topLeadingRadius: 110,
                            bottomLeadingRadius: 28,
                            bottomTrailingRadius: 28,
                            topTrailingRadius: 110,
                            style: .continuous
                        )
                        .stroke(Color.white.opacity(0.12), lineWidth: 1)
                        .allowsHitTesting(false)
                    }
                    .overlay(alignment: .bottom) {
                        LinearGradient(
                            colors: [Color.clear, Color.black.opacity(0.35)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                        .frame(height: 72)
                        .clipShape(
                            UnevenRoundedRectangle(
                                topLeadingRadius: 0,
                                bottomLeadingRadius: 28,
                                bottomTrailingRadius: 28,
                                topTrailingRadius: 0,
                                style: .continuous
                            )
                        )
                        .allowsHitTesting(false)
                    }
                    .accessibilityHidden(true)
                    .accessibilityIdentifier("archetype-hero-portrait")
            } else {
                ArchetypeSymbolView(seed: seed, size: symbolSize)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .accessibilityIdentifier("archetype-hero-symbol")
            }
        }
        .accessibilityIdentifier("archetype-hero-visual")
    }
}
