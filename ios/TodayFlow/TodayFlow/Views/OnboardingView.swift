import SwiftUI

private enum OnboardingChrome {
    private static var ru: Bool { IOSAppLocale.prefersRussian }

    static var birthDataTitle: String { ru ? "Данные рождения" : "Birth details" }
    static var firstName: String { ru ? "Имя" : "First name" }
    static var genderPicker: String { ru ? "Обращение «ты» в текстах" : "Informal “you” in copy" }
    static var genderUnspecified: String { ru ? "Нейтральные формулировки" : "Neutral wording" }
    static var genderFemale: String { ru ? "Женский род" : "Feminine grammar" }
    static var genderMale: String { ru ? "Мужской род" : "Masculine grammar" }
    static var birthDate: String { ru ? "Дата рождения" : "Birth date" }
    static var knowsBirthTime: String { ru ? "Знаю время рождения" : "I know birth time" }
    static var birthTime: String { ru ? "Время рождения" : "Birth time" }
    static var birthPlace: String { ru ? "Место рождения" : "Birth place" }
    static var searchingPlaces: String { ru ? "Ищем места…" : "Searching places…" }
    static var timezone: String { ru ? "Часовой пояс" : "Time zone" }
    static var submitLoading: String { ru ? "Подключаюсь к сервисам…" : "Connecting…" }
    static var submitIdle: String { ru ? "Собрать мой дневной ритм" : "Set up my daily rhythm" }
    static var heroBrand: String { "TODAYFLOW" }
    static var heroTitle: String { ru ? "Спокойный дневной ритм из твоей карты." : "A calm daily rhythm from your chart." }
    static var heroBody: String {
        ru
            ? "Первая версия опирается на данные рождения: экран дня, ритуал и база профиля."
            : "This first version uses birth data: your day screen, ritual, and profile base."
    }
}

struct OnboardingView: View {
    let store: TodayFlowStore

    @State private var draft = BirthProfileDraft()
    @State private var birthPlaceQuery = ""
    @State private var suggestions: [GeocodeSuggestion] = []
    @State private var isSearchingLocations = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    OnboardingHero()

                    VStack(alignment: .leading, spacing: 18) {
                        Text(OnboardingChrome.birthDataTitle)
                            .font(.headline)
                            .foregroundStyle(TodayFlowTheme.ink)

                        TextField(OnboardingChrome.firstName, text: $draft.firstName)
                            .todayFlowSystemTextInput(words: true)
                            .textFieldStyle(.roundedBorder)

                        Picker(OnboardingChrome.genderPicker, selection: Binding(
                            get: { draft.gender ?? "unspecified" },
                            set: { draft.gender = $0 }
                        )) {
                            Text(OnboardingChrome.genderUnspecified).tag("unspecified")
                            Text(OnboardingChrome.genderFemale).tag("female")
                            Text(OnboardingChrome.genderMale).tag("male")
                        }
                        .pickerStyle(.menu)

                        DatePicker(OnboardingChrome.birthDate, selection: $draft.birthDate, displayedComponents: .date)
                            .datePickerStyle(.compact)

                        Toggle(OnboardingChrome.knowsBirthTime, isOn: $draft.knowsBirthTime)

                        if draft.knowsBirthTime {
                            DatePicker(OnboardingChrome.birthTime, selection: $draft.birthTime, displayedComponents: .hourAndMinute)
                                .datePickerStyle(.compact)
                        }

                        VStack(alignment: .leading, spacing: 10) {
                            TextField(OnboardingChrome.birthPlace, text: $birthPlaceQuery)
                                .todayFlowSystemTextInput(words: true)
                                .textFieldStyle(.roundedBorder)
                                .onChange(of: birthPlaceQuery) { _, newValue in
                                    let trimmed = newValue.trimmingCharacters(in: .whitespacesAndNewlines)
                                    if draft.selectedLocationName != trimmed {
                                        draft.clearResolvedLocation()
                                    }
                                }

                            if isSearchingLocations {
                                HStack(spacing: 8) {
                                    ProgressView()
                                        .controlSize(.small)
                                    Text(OnboardingChrome.searchingPlaces)
                                        .font(.footnote)
                                        .foregroundStyle(.secondary)
                                }
                            }

                            if !suggestions.isEmpty {
                                VStack(spacing: 8) {
                                    ForEach(suggestions) { suggestion in
                                        Button {
                                            selectSuggestion(suggestion)
                                        } label: {
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(suggestion.primaryLabel)
                                                    .foregroundStyle(TodayFlowTheme.ink)
                                                    .frame(maxWidth: .infinity, alignment: .leading)

                                                Text("\(suggestion.latitude.formatted(.number.precision(.fractionLength(2)))), \(suggestion.longitude.formatted(.number.precision(.fractionLength(2))))")
                                                    .font(.caption)
                                                    .foregroundStyle(.secondary)
                                                    .frame(maxWidth: .infinity, alignment: .leading)
                                            }
                                            .padding(.vertical, 6)
                                        }
                                        .buttonStyle(.plain)

                                        if suggestion.id != suggestions.last?.id {
                                            Divider()
                                        }
                                    }
                                }
                                .padding(14)
                                .background(.white.opacity(0.5))
                                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                            }
                        }

                        Picker(OnboardingChrome.timezone, selection: $draft.timezone) {
                            ForEach(Self.timezones, id: \.self) { timezone in
                                Text(timezone).tag(timezone)
                            }
                        }
                    }
                    .padding(24)
                    .background(TodayFlowTheme.card)
                    .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))

                    Button(action: completeOnboarding) {
                        HStack {
                            if store.loadState == .loading {
                                ProgressView()
                                    .tint(.white)
                            }

                            Text(store.loadState == .loading ? OnboardingChrome.submitLoading : OnboardingChrome.submitIdle)
                                .font(.headline)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.accent)
                    .disabled(!draft.isValid || store.loadState == .loading)

                    if case let .failed(message) = store.loadState {
                        Text(message)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .todayFlowHiddenNavigationBar()
            .task(id: birthPlaceQuery) {
                await refreshSuggestions(for: birthPlaceQuery)
            }
        }
        .onAppear {
            birthPlaceQuery = draft.birthPlace
        }
    }

    private func completeOnboarding() {
        guard draft.isValid, store.loadState != .loading else { return }
        Task {
            await store.completeOnboarding(with: draft)
        }
    }

    private func refreshSuggestions(for query: String) async {
        let trimmed = query.trimmingCharacters(in: .whitespacesAndNewlines)
        draft.birthPlace = trimmed

        guard trimmed.count >= 2 else {
            suggestions = []
            isSearchingLocations = false
            return
        }

        isSearchingLocations = true
        do {
            let fetched = try await TodayFlowAPIClient.shared.fetchLocationSuggestions(query: trimmed)
            if birthPlaceQuery.trimmingCharacters(in: .whitespacesAndNewlines) == trimmed {
                suggestions = fetched
            }
        } catch {
            if birthPlaceQuery.trimmingCharacters(in: .whitespacesAndNewlines) == trimmed {
                suggestions = []
            }
        }
        isSearchingLocations = false
    }

    private func selectSuggestion(_ suggestion: GeocodeSuggestion) {
        birthPlaceQuery = suggestion.name
        draft.birthPlace = suggestion.name
        draft.selectedLocationName = suggestion.name
        draft.selectedCoordinates = BirthCoordinates(
            latitude: suggestion.latitude,
            longitude: suggestion.longitude
        )
        suggestions = []
    }

    private static let timezones = [
        "Europe/Warsaw",
        "Europe/London",
        "America/New_York",
        "America/Los_Angeles",
        "Asia/Tokyo"
    ]
}

private struct OnboardingHero: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(OnboardingChrome.heroBrand)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            Text(OnboardingChrome.heroTitle)
                .font(.system(size: 36, weight: .bold, design: .rounded))
                .foregroundStyle(TodayFlowTheme.ink)

            Text(OnboardingChrome.heroBody)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.84))
        }
        .padding(28)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
    }
}

#Preview {
    OnboardingView(store: TodayFlowStore())
}

private extension View {
    @ViewBuilder
    func todayFlowHiddenNavigationBar() -> some View {
        #if os(iOS)
        if #available(iOS 18.0, *) {
            self.toolbarVisibility(.hidden, for: .navigationBar)
        } else {
            self.navigationBarHidden(true)
        }
        #else
        self
        #endif
    }
}
