import SwiftUI

enum ProfileLivingMapsCopy {
    static let sectionLabel = "Как меняется моя жизнь"
    static let sectionLead = "Узоры из Today — карты рисуются сами, без ручной статистики."
}

struct ProfileLivingMapsSectionBand: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Rectangle()
                .fill(
                    LinearGradient(
                        colors: [
                            Color.clear,
                            TodayFlowTheme.gold.opacity(0.35),
                            TodayFlowTheme.twilight.opacity(0.28),
                            TodayFlowTheme.gold.opacity(0.35),
                            Color.clear,
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )
                )
                .frame(height: 1)
                .padding(.vertical, 4)

            Text(ProfileLivingMapsCopy.sectionLabel)
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.twilight)
                .textCase(.uppercase)
                .tracking(1.2)

            Text(ProfileLivingMapsCopy.sectionLead)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
        }
        .accessibilityIdentifier("profile-living-maps-section")
    }
}
