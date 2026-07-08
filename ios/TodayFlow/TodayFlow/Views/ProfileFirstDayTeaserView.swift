import SwiftUI

struct ProfileFirstDayTeaserView: View {
    let coreProfile: CoreProfileResponse?
    let store: TodayFlowStore
    let onOpenFullPortrait: () -> Void
    var onOpenToday: (() -> Void)?

    private var archetype: String {
        coreProfile?.baseline.archetypeSeed?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
            ?? "Личный архетип"
    }

    private var identityLine: String? {
        let parts = [
            ZodiacSignRU.title(coreProfile?.astro.sunSign),
            coreProfile?.numerology.lifePath.map { "число пути \($0)" },
        ].compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        return parts.isEmpty ? nil : parts.joined(separator: " · ")
    }

    private var teaserLine: String {
        let intro = coreProfile?.interpretation?.identity?.trimmingCharacters(in: .whitespacesAndNewlines)
        let overview = coreProfile?.natalSummary?.overview?.trimmingCharacters(in: .whitespacesAndNewlines)
        return intro?.nilIfEmpty ?? overview?.nilIfEmpty
            ?? "Карта уже собрана — ниже короткий вход в портрет. Полный разбор откроется, когда будешь готов(а) углубиться."
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            portraitBand

            teaserHeroCard

            ProfileLivingMapsSectionBand()

            ProfileMapsPreviewView(store: store, showSectionBand: false)

            ProfileMyDaysTeaserSection()

            portalButton

            if let onOpenToday {
                Button(action: onOpenToday) {
                    Text("Вернуться в Today")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
        }
        .accessibilityIdentifier("profile-first-day-teaser")
    }

    private var portraitBand: some View {
        ProfilePortraitSectionBand()
    }

    private var teaserHeroCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            HeroLargeView(
                symbolSeed: archetype,
                title: archetype,
                kicker: "Портрет · день 1",
                metaLine: identityLine,
                digest: teaserLine,
                edgeToEdge: false
            )
        }
    }

    private var portalButton: some View {
        Button(action: onOpenFullPortrait) {
            VStack(spacing: 8) {
                Text(ProfilePortalCopy.kicker)
                    .font(.caption2.weight(.semibold))
                    .tracking(1.6)
                    .textCase(.uppercase)
                    .foregroundStyle(Color.white.opacity(0.45))

                Text(ProfilePortalCopy.title)
                    .font(.title2.weight(.semibold))
                    .foregroundStyle(Color.white.opacity(0.96))

                Text(ProfilePortalCopy.sub)
                    .font(.footnote)
                    .foregroundStyle(Color.white.opacity(0.62))
                    .multilineTextAlignment(.center)

                Text("Открыть полную карту →")
                    .font(.caption2.weight(.bold))
                    .tracking(1)
                    .textCase(.uppercase)
                    .foregroundStyle(Color.white.opacity(0.92))
                    .padding(.top, 8)
            }
            .padding(.vertical, 32)
            .padding(.horizontal, 20)
            .frame(maxWidth: .infinity)
            .background(Color(red: 0.07, green: 0.06, blue: 0.11))
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("profile-first-day-portal")
    }
}

private struct ProfileMyDaysTeaserSection: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Мои дни")
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text("Заверши день в Today — здесь появятся фокус и итог последних дней.")
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}

private extension String {
    var nilIfEmpty: String? {
        isEmpty ? nil : self
    }
}
