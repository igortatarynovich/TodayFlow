import SwiftUI

/// Паритет с web `/tracking/progress` — хаб ссылок на карты.
struct MapsHubView: View {
    let store: TodayFlowStore
    var onOpenRhythm: () -> Void

    private struct HubCard: Identifiable {
        let id: String
        let title: String
        let desc: String
        let destination: MapNavigationDestination?
        let opensRhythm: Bool
        let primary: Bool
    }

    private var cards: [HubCard] {
        [
            HubCard(
                id: "rhythm",
                title: FlowTrackerChromeCopy.trackingProgressCardMainCalendarTitle,
                desc: FlowTrackerChromeCopy.trackingProgressCardMainCalendarDesc,
                destination: nil,
                opensRhythm: true,
                primary: true
            ),
            HubCard(
                id: "mood",
                title: "Карта настроения",
                desc: "Утренние отметки и история дня.",
                destination: .mood,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "energy",
                title: "Карта энергии",
                desc: "Темп дня по fusion и Today.",
                destination: .energy,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "promise",
                title: "Карта обещаний",
                desc: "Обещание дня и вечернее закрытие.",
                destination: .promise,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "habits",
                title: FlowTrackerChromeCopy.trackingProgressCardHabitsListTitle,
                desc: FlowTrackerChromeCopy.trackingProgressCardHabitsListDesc,
                destination: .habits,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "ascetic",
                title: "Карта аскез",
                desc: "Тропа осознанной практики.",
                destination: .ascetic,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "wish",
                title: "Карта желаний",
                desc: "Якоря и маленькие шаги.",
                destination: .wish,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "relationship",
                title: "Карта связей",
                desc: "Круги внимания, не рейтинг.",
                destination: .relationship,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "tarot",
                title: "Карта таро",
                desc: "Архетипическое путешествие.",
                destination: .tarot,
                opensRhythm: false,
                primary: false
            ),
            HubCard(
                id: "affirmations",
                title: FlowTrackerChromeCopy.trackingProgressCardAffirmationsTitle,
                desc: FlowTrackerChromeCopy.trackingProgressCardAffirmationsDesc,
                destination: nil,
                opensRhythm: true,
                primary: false
            ),
        ]
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(FlowTrackerChromeCopy.trackingProgressHubEyebrow.uppercased())
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                Text(FlowTrackerChromeCopy.trackingProgressHubIntro)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .fixedSize(horizontal: false, vertical: true)

                ForEach(cards) { card in
                    hubCardView(card)
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle(FlowTrackerChromeCopy.trackingProgressHubTitle)
        .navigationBarTitleDisplayMode(.inline)
    }

    @ViewBuilder
    private func hubCardView(_ card: HubCard) -> some View {
        let content = VStack(alignment: .leading, spacing: 6) {
            Text(card.title)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(card.desc)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(card.primary ? TodayFlowTheme.todayHeroSurface : Color.white.opacity(0.92))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.borderRoseSubtle, lineWidth: 1)
        )

        if let destination = card.destination {
            NavigationLink(value: destination) { content }
                .buttonStyle(.plain)
        } else if card.opensRhythm {
            Button(action: onOpenRhythm) { content }
                .buttonStyle(.plain)
        } else {
            content
        }
    }
}

@MainActor
@ViewBuilder
func mapDestinationView(
    _ destination: MapNavigationDestination,
    store: TodayFlowStore,
    onOpenRhythm: @escaping () -> Void
) -> some View {
    switch destination {
    case .hub:
        MapsHubView(store: store, onOpenRhythm: onOpenRhythm)
    case .mood:
        MoodMapView(ritualEmail: store.authSession?.email)
    case .energy:
        EnergyMapView(store: store)
    case .promise:
        PromiseMapView()
    case .habits:
        HabitMapView(store: store)
    case .ascetic:
        AsceticMapView(store: store)
    case .wish:
        WishMapView(store: store)
    case .relationship:
        RelationshipMapView()
    case .tarot:
        TarotMapView()
    }
}
