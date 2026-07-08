import SwiftUI

enum ProfilePortraitCopy {
    static let sectionLabel = "Кто я"
    static let sectionLead = "Архетип, паттерны и сферы — портрет, который почти не меняется."
}

struct ProfilePortraitSectionBand: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(ProfilePortraitCopy.sectionLabel)
                .font(.caption.weight(.bold))
                .foregroundStyle(TodayFlowTheme.twilight)
                .textCase(.uppercase)
                .tracking(1.2)

            Text(ProfilePortraitCopy.sectionLead)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
        }
        .accessibilityIdentifier("profile-portrait-section")
    }
}
