import SwiftUI

enum ProfilePortalCopy {
    static let kicker = "Следующий уровень"
    static let title = "Карта личности"
    static let sub = "Планеты, дома, аспекты — полный разбор натальной карты."
    static let enter = "Войти"
    static let collapse = "Свернуть"
}

struct ProfilePortalDeepSection<Content: View>: View {
    @Binding var isExpanded: Bool
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @ViewBuilder var content: () -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button {
                withAnimation(reduceMotion ? nil : TodayFlowTheme.Motion.cardSpring) {
                    isExpanded.toggle()
                }
            } label: {
                ZStack {
                    Color(red: 0.07, green: 0.06, blue: 0.11)

                    LinearGradient(
                        colors: [
                            Color(red: 0.04, green: 0.03, blue: 0.06).opacity(0.72),
                            Color.clear,
                            Color.clear,
                            Color(red: 0.04, green: 0.03, blue: 0.06).opacity(0.72),
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    )

                    Rectangle()
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color.clear,
                                    Color.white.opacity(0.12),
                                    Color.white.opacity(0.42),
                                    Color.white.opacity(0.12),
                                    Color.clear,
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .frame(width: 1)
                        .shadow(color: Color(red: 0.82, green: 0.76, blue: 1).opacity(0.22), radius: 12)

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
                            .frame(maxWidth: 280)

                        Text(isExpanded ? ProfilePortalCopy.collapse : ProfilePortalCopy.enter)
                            .font(.caption2.weight(.bold))
                            .tracking(1)
                            .textCase(.uppercase)
                            .foregroundStyle(Color.white.opacity(0.92))
                            .padding(.top, 8)
                    }
                    .padding(.vertical, 32)
                    .padding(.horizontal, 20)
                }
                .frame(minHeight: 200)
                .overlay(alignment: .top) {
                    Rectangle()
                        .fill(Color.white.opacity(0.08))
                        .frame(height: 1)
                }
                .overlay(alignment: .bottom) {
                    Rectangle()
                        .fill(Color.black.opacity(0.35))
                        .frame(height: 1)
                }
            }
            .buttonStyle(.plain)
            .accessibilityIdentifier("profile-portal-deep")

            if isExpanded {
                content()
                    .padding(.top, 12)
                    .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
        .animation(reduceMotion ? nil : TodayFlowTheme.Motion.revealEase, value: isExpanded)
    }
}
