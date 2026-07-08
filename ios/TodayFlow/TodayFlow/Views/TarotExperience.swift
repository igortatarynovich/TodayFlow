import SwiftUI

private enum TarotExperienceChrome {
    static var ru: Bool { IOSAppLocale.prefersRussian }

    static var dailyCardTitle: String { ru ? "Карта дня" : "Daily card" }
    static var dailyLoadFailed: String {
        ru ? "Не удалось загрузить. Потяни для обновления." : "Couldn’t load. Pull to refresh."
    }
    static var spreadsTitle: String { ru ? "Расклады" : "Spreads" }
    static var oneCardTitle: String { ru ? "Одна карта" : "One card" }
    static var oneCardSubtitle: String { ru ? "Один вопрос — один ответ" : "One question—one answer" }
    static var threeCardsTitle: String { ru ? "Три карты" : "Three cards" }
    static var threeCardsSubtitle: String {
        ru ? "Линия: прошлое · сейчас · шаг" : "Line: past · now · next step"
    }
    static var favoritesTitle: String { ru ? "Избранное" : "Favorites" }
    static var favoritesEmpty: String {
        ru ? "Избранное появится после нажатия на сердце у карты." : "Favorites appear after you tap the heart on a card."
    }
    static var recentSpreadsTitle: String { ru ? "Недавние расклады" : "Recent spreads" }
    static var seeAll: String { ru ? "Все" : "All" }
    static var historyEmpty: String {
        ru ? "Сохранённые расклады появятся здесь." : "Saved spreads will appear here."
    }
    static var spreadTitleThree: String { threeCardsTitle }
    static var spreadTitleGeneric: String { ru ? "Расклад" : "Spread" }
    static var interpretationTitle: String { ru ? "Интерпретация" : "Reading" }
    static var readingCore: String { ru ? "Суть" : "Core" }
    static var readingManifestation: String { ru ? "Проявление" : "Manifestation" }
    static var readingRisk: String { ru ? "Риск" : "Caution" }
    static var readingStep: String { ru ? "Шаг" : "Next step" }
    static var readingWhy: String { ru ? "Почему именно такой вывод" : "Why this conclusion" }
    static var readingCards: String { ru ? "Что говорят карты" : "What the cards say" }
    static var readingMainAnswer: String { ru ? "Главный ответ" : "Main answer" }
    static var readingInsightHolding: String { ru ? "Сейчас самое сложное" : "What's hardest now" }
    static var readingInsightShifting: String { ru ? "То, что уже начинает меняться" : "What's already shifting" }
    static var readingInsightAttention: String { ru ? "Попробуй заметить" : "Try to notice" }
    static var readingToday: String { ru ? "Что можно сделать сегодня" : "One thing for today" }
    static var followUpThanks: String { ru ? "Спасибо — это помогает точнее слышать тебя" : "Thank you — this helps us listen better" }
    static var questionEyebrow: String { ru ? "Твой вопрос" : "Your question" }
    static var a11yRemoveFavorite: String { ru ? "Убрать из избранного" : "Remove from favorites" }
    static var a11yAddFavorite: String { ru ? "В избранное" : "Add to favorites" }
    static var historyNavTitle: String { ru ? "История" : "History" }
    static var spreadDetailNavTitle: String { spreadTitleGeneric }
    static var alertSpreadTitle: String { spreadTitleGeneric }
    static var questionPlaceholder: String {
        ru ? "Тема вопроса — по желанию" : "Question theme—optional"
    }
    static var deckTitle: String { ru ? "Колода" : "Deck" }
    static var deckEmpty: String { ru ? "Колода пуста — обнови." : "Deck is empty—refresh." }
    static var stepReadyForReading: String {
        ru ? "Готово — открой интерпретацию." : "Done—open the reading."
    }
    static var pickACard: String { ru ? "Выбери карту" : "Pick a card" }
    static var slotMainAnswer: String { ru ? "Главный ответ" : "Main answer" }
    static var slotPast: String { ru ? "Что тянется из прошлого" : "What carries from the past" }
    static var slotNow: String { ru ? "Что главное сейчас" : "What matters now" }
    static var slotNext: String { ru ? "Ближайший ход" : "Nearest move" }
    static var yourPick: String { ru ? "Твой выбор" : "Your picks" }
    static var cardFallback: String { ru ? "Карта" : "Card" }
    static var reset: String { ru ? "Сбросить" : "Reset" }
    static var openReading: String { ru ? "Открыть интерпретацию" : "Open reading" }
    static var leadCard: String { ru ? "Ведущая карта" : "Lead card" }
    static var newSpread: String { ru ? "Новый расклад" : "New spread" }
    static var cardReferenceTitle: String { ru ? "Карта" : "Card" }
    static var orientationUpright: String { ru ? "Прямая" : "Upright" }
    static var orientationReversed: String { ru ? "Перевёрнутая" : "Reversed" }
    static var resonanceTitle: String { ru ? "Насколько откликается?" : "How much does this resonate?" }
    static var resonanceVery: String { ru ? "Очень" : "Very" }
    static var resonancePartial: String { ru ? "Частично" : "Partially" }
    static var resonanceNone: String { ru ? "Не очень" : "Not much" }
    static var anchorLabel: String { ru ? "Якорь" : "Anchor" }
    static var deepenPickHint: String { ru ? "Добери карты к якорю" : "Add cards to the anchor" }
}

// MARK: - Hub

struct TarotHubView: View {
    let store: TodayFlowStore

    @State private var daily: TarotDailyDrawDTO?
    @State private var dailyLoading = false
    @State private var dailyError: String?
    @State private var favoriteIds: Set<Int> = []
    @State private var history: [TarotSpreadRecordDTO] = []
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.07, green: 0.08, blue: 0.11),
                        Color(red: 0.10, green: 0.11, blue: 0.15),
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                ScrollView(showsIndicators: false) {
                    VStack(spacing: 18) {
                        TarotQuestionFlowView(store: store) { config in
                            path.append(TarotHubDestination.spreadRitual(config))
                        } onOpenDailyCard: {
                            if let daily {
                                path.append(TarotHubDestination.cardReference(daily.card.id))
                            }
                        }

                        if shouldShowJourneyHint {
                            TarotJourneyPanelView(compact: true)
                        }

                        utilitiesSection
                    }
                    .padding(.horizontal, 18)
                    .padding(.top, 12)
                    .padding(.bottom, 28)
                }
            }
            .navigationTitle("Tarot")
            .todayflowNavigationBarTitleDisplayModeLarge()
            .navigationDestination(for: TarotHubDestination.self) { route in
                switch route {
                case let .spreadRitual(config):
                    TarotSpreadRitualView(store: store, config: config)
                case .history:
                    TarotSpreadHistoryListView()
                case let .historyRecord(record):
                    TarotSpreadRecordDetailView(record: record)
                case let .cardReference(cardId):
                    TarotCardReferenceScreen(cardId: cardId)
                }
            }
            .task {
                await loadHub()
            }
            .onAppear {
                tryOpenPendingDeepen()
            }
            .onChange(of: store.tarotDeepenRouteToken) { _, _ in
                tryOpenPendingDeepen()
            }
            .refreshable {
                await loadHub()
            }
            .alert("Tarot", isPresented: Binding(
                get: { dailyError != nil },
                set: { if !$0 { dailyError = nil } }
            )) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(dailyError ?? "")
            }
        }
    }

    private var shouldShowJourneyHint: Bool {
        TarotJourneyStore.shouldShowPanel()
    }

    private func tryOpenPendingDeepen() {
        guard store.tarotDeepenRouteToken != nil, let req = store.consumePendingTarotDeepen() else { return }
        openDeepenRitual(req)
    }

    private func openDeepenRitual(_ req: TodayFlowStore.TarotDeepenRequest) {
        let offer = TarotQuestionFlowCanon.spreadOffer(for: req.spreadId)
        let config = TarotSpreadRitualConfig(
            spreadId: req.spreadId,
            title: offer?.title ?? req.spreadId,
            question: req.question,
            concernDomain: nil,
            refinementId: nil,
            cardCount: offer?.cardCount ?? 3,
            positionLabels: offer?.positionLabels ?? ["Прошлое", "Настоящее", "Будущее"],
            anchorCardId: req.anchorCardId,
            anchorOrientation: req.anchorOrientation
        )
        path.append(TarotHubDestination.spreadRitual(config))
    }

    private var utilitiesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            dailyCard
            favoritesSection
            historySection
        }
    }

    private var dailyCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text(TarotExperienceChrome.dailyCardTitle)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                if let daily {
                    TarotFavoriteHeartButton(cardId: daily.card.id, favoriteIds: $favoriteIds)
                }
                if dailyLoading {
                    ProgressView()
                } else {
                    Button {
                        Task { await loadHub() }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }

            if let daily {
                NavigationLink(value: TarotHubDestination.cardReference(daily.card.id)) {
                    TarotCardFace(
                        name: daily.card.name,
                        orientation: daily.orientation,
                        keywords: daily.card.keywordList,
                        meaning: daily.card.meaning(for: daily.orientation)
                    )
                }
                .buttonStyle(.plain)
                if let mantra = daily.mantra, mantraBody(mantra) != nil || mantra.title != nil {
                    VStack(alignment: .leading, spacing: 4) {
                        if let t = mantra.title {
                            Text(t)
                                .font(.footnote.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.accent)
                        }
                        if let body = mantraBody(mantra) {
                            Text(body)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                    }
                    .padding(.top, 6)
                }
                Text(daily.date)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else if !dailyLoading {
                Text(TarotExperienceChrome.dailyLoadFailed)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(20)
        .todayFlowCard()
    }

    private var favoritesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TarotExperienceChrome.favoritesTitle)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            if favoriteIds.isEmpty {
                Text(TarotExperienceChrome.favoritesEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .todayFlowCard()
            } else {
                VStack(spacing: 14) {
                    ForEach(Array(favoriteIds).sorted(), id: \.self) { cardId in
                        HStack(spacing: 12) {
                            NavigationLink(value: TarotHubDestination.cardReference(cardId)) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(displayName(forCardId: cardId))
                                        .font(.headline)
                                        .foregroundStyle(TodayFlowTheme.ink)
                                }
                            }
                            .buttonStyle(.plain)
                            Spacer()
                            TarotFavoriteHeartButton(cardId: cardId, favoriteIds: $favoriteIds)
                        }
                    }
                }
                .padding(16)
                .todayFlowCard()
            }
        }
    }

    private var historySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(TarotExperienceChrome.recentSpreadsTitle)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                NavigationLink(value: TarotHubDestination.history) {
                    Text(TarotExperienceChrome.seeAll)
                        .font(.subheadline.weight(.semibold))
                }
            }

            if history.isEmpty {
                Text(TarotExperienceChrome.historyEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .todayFlowCard()
            } else {
                VStack(spacing: 10) {
                    ForEach(Array(history.prefix(5))) { record in
                        NavigationLink(value: TarotHubDestination.historyRecord(record)) {
                            historyRow(record)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }

    private func historyRow(_ record: TarotSpreadRecordDTO) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(record.drawDate)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(record.spread.title ?? spreadTitleFallback(record.spread.spreadId))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(record.spread.cards.map(\.card.name).joined(separator: " · "))
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .todayFlowCard()
    }

    private func spreadTitleFallback(_ spreadId: String) -> String {
        spreadId == "three_cards" ? TarotExperienceChrome.spreadTitleThree : TarotExperienceChrome.spreadTitleGeneric
    }

    private func displayName(forCardId cardId: Int) -> String {
        if let daily, daily.card.id == cardId {
            return daily.card.name
        }
        for record in history {
            if let match = record.spread.cards.first(where: { $0.card.id == cardId }) {
                return match.card.name
            }
        }
        return "Карта #\(cardId)"
    }

    private func loadHub() async {
        dailyLoading = true
        dailyError = nil
        defer { dailyLoading = false }
        do {
            daily = try await TarotClient.fetchDailyDraw()
        } catch {
            daily = nil
            dailyError = error.localizedDescription
        }
        do {
            favoriteIds = Set(try await TarotClient.fetchFavoriteIds())
        } catch {
            favoriteIds = []
        }
        do {
            history = try await TarotClient.fetchSpreadHistory()
        } catch {
            history = []
        }
    }

    private func mantraBody(_ m: TarotMantraDTO) -> String? {
        let parts = [m.mantra, m.humanText, m.guidance, m.intention].compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        return parts.first
    }
}

private enum TarotHubDestination: Hashable {
    case spreadRitual(TarotSpreadRitualConfig)
    case history
    case historyRecord(TarotSpreadRecordDTO)
    case cardReference(Int)
}

// MARK: - Favorites & history screens

private struct TarotFavoriteHeartButton: View {
    let cardId: Int
    @Binding var favoriteIds: Set<Int>

    @State private var busy = false

    private var isFavorite: Bool {
        favoriteIds.contains(cardId)
    }

    var body: some View {
        Button {
            Task {
                busy = true
                defer { busy = false }
                do {
                    let list = try await TarotClient.toggleFavorite(cardId: cardId)
                    favoriteIds = Set(list)
                } catch {}
            }
        } label: {
            Image(systemName: isFavorite ? "heart.fill" : "heart")
                .font(.body.weight(.semibold))
                .foregroundStyle(isFavorite ? TodayFlowTheme.accent : TodayFlowTheme.secondaryInk)
        }
        .buttonStyle(.plain)
        .disabled(busy)
        .accessibilityLabel(isFavorite ? TarotExperienceChrome.a11yRemoveFavorite : TarotExperienceChrome.a11yAddFavorite)
    }
}

private struct TarotSpreadHistoryListView: View {
    @State private var history: [TarotSpreadRecordDTO] = []
    @State private var loading = true

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()
            if loading && history.isEmpty {
                ProgressView()
            } else {
                ScrollView(showsIndicators: false) {
                    LazyVStack(spacing: 12) {
                        ForEach(history) { record in
                            NavigationLink(value: TarotHubDestination.historyRecord(record)) {
                                TarotHistoryRow(record: record)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 16)
                }
            }
        }
        .navigationTitle(TarotExperienceChrome.historyNavTitle)
        .todayflowNavigationBarTitleDisplayModeInline()
        .task {
            await load()
        }
    }

    private func load() async {
        loading = true
        defer { loading = false }
        do {
            history = try await TarotClient.fetchSpreadHistory()
        } catch {
            history = []
        }
    }
}

private struct TarotHistoryRow: View {
    let record: TarotSpreadRecordDTO

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(record.drawDate)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(record.spread.title ?? (record.spread.spreadId == "three_cards" ? TarotExperienceChrome.spreadTitleThree : TarotExperienceChrome.spreadTitleGeneric))
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(record.spread.cards.map(\.card.name).joined(separator: " · "))
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .lineLimit(3)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .todayFlowCard()
    }
}

private struct TarotSpreadRecordDetailView: View {
    let record: TarotSpreadRecordDTO

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(record.drawDate)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                        if let created = record.createdAt, !created.isEmpty {
                            Text(created)
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                    }
                    .padding(.horizontal, 4)

                    TarotSpreadSnapshotView(spread: record.spread, reading: nil)
                }
                .padding(.horizontal, 18)
                .padding(.vertical, 16)
            }
        }
        .navigationTitle(TarotExperienceChrome.spreadDetailNavTitle)
        .todayflowNavigationBarTitleDisplayModeInline()
    }
}

private struct TarotSpreadSnapshotView: View {
    let spread: TarotSpreadResultDTO
    var reading: TarotSpreadReadingDTO?

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if let t = spread.title, !t.isEmpty {
                Text(t)
                    .font(.title2.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            if let d = spread.description, !d.isEmpty {
                Text(d)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }

            ForEach(Array(spread.cards.enumerated()), id: \.offset) { _, item in
                VStack(alignment: .leading, spacing: 10) {
                    Text(item.position.title)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.accent)
                    TarotCardFace(
                        name: item.card.name,
                        orientation: item.orientation,
                        keywords: item.card.keywordList,
                        meaning: item.meaning
                    )
                }
                .padding(14)
                .todayFlowCard()
            }

            if let reading {
                tarotReadingBlock(reading)
            }
        }
    }

    private func tarotReadingBlock(_ r: TarotSpreadReadingDTO) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if let m = r.meaning, !m.isEmpty {
                tarotLabeledBlock(TarotExperienceChrome.readingMainAnswer, m)
            }
            if let why = r.synthesisWhy, !why.isEmpty {
                tarotLabeledBlock(TarotExperienceChrome.readingWhy, why)
            }
            if let holding = r.insightHolding, !holding.isEmpty {
                tarotLabeledBlock(TarotExperienceChrome.readingInsightHolding, holding)
            }
            if let today = r.todaySuggestion ?? r.actionsToday?.first, !today.isEmpty {
                tarotLabeledBlock(TarotExperienceChrome.readingToday, today)
            }
        }
        .padding(18)
        .todayFlowCard()
    }

    private func tarotLabeledBlock(_ title: String, _ body: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.footnote.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(body)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

// MARK: - Question-first reading surface (web `TarotReadingStorySurface`)

private struct TarotReadingStorySurfaceView: View {
    let question: String
    let reading: TarotSpreadReadingDTO
    let concernDomain: String?
    let store: TodayFlowStore
    let spreadId: String
    let generationLogId: Int?
    @Binding var selectedChipId: String?
    @Binding var followUpSaved: Bool

    private var chips: [TarotFollowUpChipDTO] {
        if let fromApi = reading.followUpChips, !fromApi.isEmpty {
            return fromApi
        }
        return Self.defaultChips(for: concernDomain)
    }

    static func defaultChips(for concernDomain: String?) -> [TarotFollowUpChipDTO] {
        let domain = (concernDomain ?? "").lowercased()
        switch domain {
        case "relationships":
            return [
                TarotFollowUpChipDTO(id: "let_go", label: "Отпустить"),
                TarotFollowUpChipDTO(id: "understand", label: "Понять, что произошло"),
                TarotFollowUpChipDTO(id: "clarity_feelings", label: "Понять свои чувства"),
                TarotFollowUpChipDTO(id: "stop_waiting", label: "Перестать ждать"),
                TarotFollowUpChipDTO(id: "unsure", label: "Пока не знаю"),
            ]
        case "work":
            return [
                TarotFollowUpChipDTO(id: "stay_clarity", label: "Понять, стоит ли оставаться"),
                TarotFollowUpChipDTO(id: "change_direction", label: "Сменить направление"),
                TarotFollowUpChipDTO(id: "rest_first", label: "Сначала восстановиться"),
                TarotFollowUpChipDTO(id: "one_step", label: "Сделать один шаг"),
                TarotFollowUpChipDTO(id: "unsure", label: "Пока не знаю"),
            ]
        case "money":
            return [
                TarotFollowUpChipDTO(id: "keep", label: "Сохранить то, что уже есть"),
                TarotFollowUpChipDTO(id: "income", label: "Увеличить доход"),
                TarotFollowUpChipDTO(id: "worry_less", label: "Перестать постоянно переживать из-за денег"),
                TarotFollowUpChipDTO(id: "delayed_step", label: "Сделать шаг, который давно откладываю"),
                TarotFollowUpChipDTO(id: "unsure", label: "Пока не могу определить"),
            ]
        case "decision":
            return [
                TarotFollowUpChipDTO(id: "choose_a", label: "Ближе вариант А"),
                TarotFollowUpChipDTO(id: "choose_b", label: "Ближе вариант Б"),
                TarotFollowUpChipDTO(id: "need_time", label: "Нужно время"),
                TarotFollowUpChipDTO(id: "fear_named", label: "Назвать страх"),
                TarotFollowUpChipDTO(id: "unsure", label: "Пока не знаю"),
            ]
        default:
            return [
                TarotFollowUpChipDTO(id: "clarity", label: "Стало понятнее"),
                TarotFollowUpChipDTO(id: "same", label: "Пока без изменений"),
                TarotFollowUpChipDTO(id: "new_questions", label: "Появились новые вопросы"),
                TarotFollowUpChipDTO(id: "need_time", label: "Нужно время"),
            ]
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            storyCard {
                Text(TarotExperienceChrome.questionEyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                Text("«\(question)»")
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.88))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if let main = reading.meaning, !main.isEmpty {
                storyCard(highlight: true) {
                    Text(TarotExperienceChrome.readingMainAnswer)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                    Text(main)
                        .font(.body.weight(.medium))
                        .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if let story = reading.synthesisWhy, !story.isEmpty {
                storyCard {
                    Text(TarotExperienceChrome.readingWhy)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                    Text(story)
                        .font(.subheadline)
                        .foregroundStyle(Color(red: 0.88, green: 0.84, blue: 0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if let cards = reading.cardInsights, !cards.isEmpty {
                storyCard {
                    Text(TarotExperienceChrome.readingCards)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(cards) { card in
                            HStack(alignment: .top, spacing: 12) {
                                tarotStoryCardThumb(cardId: card.cardId, orientation: card.orientation)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("\(card.positionLabel) · \(card.cardNameRu)")
                                        .font(.caption.weight(.bold))
                                        .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                                    Text(card.line)
                                        .font(.subheadline)
                                        .foregroundStyle(Color(red: 0.88, green: 0.84, blue: 0.78))
                                        .fixedSize(horizontal: false, vertical: true)
                                }
                            }
                        }
                    }
                }
            }

            insightGrid

            if let today = reading.todaySuggestion ?? reading.actionsToday?.first, !today.isEmpty {
                storyCard(dashed: true) {
                    Text(TarotExperienceChrome.readingToday)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(Color(red: 0.79, green: 0.66, blue: 0.45))
                    Text(today)
                        .font(.subheadline)
                        .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }

            if !chips.isEmpty {
                storyCard {
                    Text(reading.followUpPrompt ?? (TarotExperienceChrome.ru ? "Что сейчас сложнее всего?" : "What do you want most right now?"))
                        .font(.headline)
                        .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.88))
                    FlowLayoutChipsInteractive(
                        chips: chips,
                        selectedId: selectedChipId,
                        disabled: followUpSaved,
                        onSelect: { chip in
                            guard !followUpSaved else { return }
                            selectedChipId = chip.id
                            followUpSaved = true
                            Task {
                                var payload: [String: JSONValue] = [
                                    "chip_id": .string(chip.id),
                                    "chip_label": .string(chip.label),
                                    "spread_id": .string(spreadId),
                                    "question_text": .string(question),
                                ]
                                if let concernDomain, !concernDomain.isEmpty {
                                    payload["concern_domain"] = .string(concernDomain)
                                }
                                if let generationLogId, generationLogId > 0 {
                                    payload["generation_id"] = .number(Double(generationLogId))
                                }
                                await store.trackTarotFlowEvent(
                                    eventType: "tarot_reading_follow_up",
                                    idempotencyKey: "tarot-follow-up:\(spreadId):\(chip.id):\(generationLogId ?? 0)",
                                    payload: payload
                                )
                            }
                        }
                    )
                    if followUpSaved {
                        Text(TarotExperienceChrome.followUpThanks)
                            .font(.caption)
                            .foregroundStyle(Color(red: 0.68, green: 0.64, blue: 0.58))
                    }
                }
            }
        }
    }

    @ViewBuilder
    private var insightGrid: some View {
        let items: [(String, String?)] = [
            (TarotExperienceChrome.readingInsightHolding, reading.insightHolding),
            (TarotExperienceChrome.readingInsightShifting, reading.insightShifting),
            (TarotExperienceChrome.readingInsightAttention, reading.insightAttention),
        ].filter { !($0.1 ?? "").isEmpty }

        if !items.isEmpty {
            VStack(spacing: 8) {
                ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                    storyCard {
                        Text(item.0)
                            .font(.caption.weight(.bold))
                            .foregroundStyle(Color(red: 0.91, green: 0.83, blue: 0.66))
                        Text(item.1 ?? "")
                            .font(.subheadline)
                            .foregroundStyle(Color(red: 0.88, green: 0.84, blue: 0.78))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
            }
        }
    }

    @ViewBuilder
    private func storyCard(highlight: Bool = false, dashed: Bool = false, @ViewBuilder content: () -> some View) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            content()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            Color.white.opacity(highlight ? 0.08 : 0.05),
            in: RoundedRectangle(cornerRadius: 18, style: .continuous)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(
                    Color(red: 0.79, green: 0.66, blue: 0.45).opacity(highlight ? 0.42 : (dashed ? 0.28 : 0.18)),
                    style: dashed ? StrokeStyle(lineWidth: 1, dash: [5, 4]) : StrokeStyle(lineWidth: 1)
                )
        )
    }

    @ViewBuilder
    private func tarotStoryCardThumb(cardId: Int, orientation: String) -> some View {
        let thumbW: CGFloat = 56
        let thumbH = TodayTarotDeckImageURLs.cardDisplayHeight(width: thumbW)
        let reversed = orientation.lowercased() == "reversed"
        let faceURL = TodayTarotDeckImageURLs.deckFaceURL(cardId: cardId)
        let url = faceURL ?? TodayTarotDeckImageURLs.cardBackURL()
        AsyncImage(url: url) { phase in
            switch phase {
            case .success(let image):
                image
                    .resizable()
                    .scaledToFit()
            default:
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(Color.white.opacity(0.06))
            }
        }
        .frame(width: thumbW, height: thumbH)
        .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .stroke(Color(red: 0.79, green: 0.66, blue: 0.45).opacity(0.28), lineWidth: 1)
        )
        .rotationEffect(.degrees(reversed && faceURL != nil ? 180 : 0))
    }
}

private struct FlowLayoutChipsInteractive: View {
    let chips: [TarotFollowUpChipDTO]
    let selectedId: String?
    let disabled: Bool
    let onSelect: (TarotFollowUpChipDTO) -> Void

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(chips) { chip in
                    Button {
                        onSelect(chip)
                    } label: {
                        Text(chip.label)
                            .font(.footnote.weight(.semibold))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(
                                selectedId == chip.id
                                    ? Color(red: 0.79, green: 0.66, blue: 0.45).opacity(0.22)
                                    : Color.white.opacity(0.06),
                                in: Capsule()
                            )
                            .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
                    }
                    .buttonStyle(.plain)
                    .disabled(disabled && selectedId != chip.id)
                    .opacity(disabled && selectedId != chip.id ? 0.45 : 1)
                }
            }
        }
        .padding(.top, 4)
    }
}

// MARK: - Interactive spread (question-first ritual)

private struct PickedDeckCard: Identifiable, Hashable {
    let id: Int
    let deckIndex: Int
    let card: TarotCardDTO
    let orientation: String
}

private struct TarotSpreadRitualView: View {
    let store: TodayFlowStore
    let config: TarotSpreadRitualConfig

    @State private var deck: [TarotCardDTO] = []
    @State private var deckPicks: [PickedDeckCard] = []
    @State private var usedIndices: Set<Int> = []
    @State private var deckLoading = false
    @State private var anchorCard: TarotCardDTO?
    @State private var anchorLoading = false
    @State private var resultContext: TarotSpreadContextDTO?
    @State private var resultLoading = false
    @State private var errorMessage: String?
    @State private var favoriteIds: Set<Int> = []
    @State private var selectedFollowUpChipId: String?
    @State private var followUpSaved = false
    @State private var synthesisTracked = false

    private var requiredPicks: Int { config.requiredFromDeck }
    private var selectionLabels: [String] { config.deckSelectionLabels }

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollView(showsIndicators: false) {
                VStack(spacing: 18) {
                    if resultContext == nil {
                        questionBlock
                        if config.anchorCardId != nil {
                            anchorBlock
                        }
                        deckBlock
                        picksSummary
                        revealButton
                    } else if let ctx = resultContext {
                        resultBlock(ctx)
                    }
                }
                .padding(.horizontal, 18)
                .padding(.vertical, 16)
                .padding(.bottom, 28)
            }
        }
        .navigationTitle(config.title)
        .todayflowNavigationBarTitleDisplayModeInline()
        .task {
            await loadAnchorIfNeeded()
            await loadDeck()
            await loadFavorites()
        }
        .alert(TarotExperienceChrome.alertSpreadTitle, isPresented: Binding(
            get: { errorMessage != nil },
            set: { if !$0 { errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage ?? "")
        }
    }

    private var questionBlock: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(TarotQuestionFlowCopy.composedQuestionLabel)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text("«\(config.question)»")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .todayFlowCard()
    }

    private var anchorBlock: some View {
        Group {
            if anchorLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
                    .padding()
                    .todayFlowCard()
            } else if let anchorCard, let orient = config.anchorOrientation {
                VStack(alignment: .leading, spacing: 8) {
                    Text(config.positionLabels.first ?? TarotExperienceChrome.anchorLabel)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                    TarotCardFace(
                        name: anchorCard.name,
                        orientation: orient,
                        keywords: anchorCard.keywordList,
                        meaning: anchorCard.meaning(for: orient)
                    )
                }
                .padding(18)
                .todayFlowCard()
            }
        }
    }

    private var deckBlock: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text(TarotExperienceChrome.deckTitle)
                    .font(.title3.weight(.semibold))
                Spacer()
                if deckLoading {
                    ProgressView()
                } else {
                    Button {
                        Task { await loadDeck() }
                    } label: {
                        Image(systemName: "shuffle")
                    }
                }
            }
            .foregroundStyle(TodayFlowTheme.ink)

            Text(stepHint)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            if deck.isEmpty && !deckLoading {
                Text(TarotExperienceChrome.deckEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 72), spacing: 10)], spacing: 10) {
                    ForEach(deck.indices, id: \.self) { idx in
                        deckSlot(index: idx)
                    }
                }
            }
        }
        .padding(18)
        .todayFlowCard()
    }

    private var stepHint: String {
        let n = deckPicks.count
        if n >= requiredPicks {
            return TarotExperienceChrome.stepReadyForReading
        }
        if config.anchorCardId != nil, n == 0 {
            return TarotExperienceChrome.deepenPickHint
        }
        if n < selectionLabels.count {
            return selectionLabels[n]
        }
        return TarotExperienceChrome.pickACard
    }

    private func deckSlot(index: Int) -> some View {
        let taken = usedIndices.contains(index)
        return Button {
            guard !taken, deckPicks.count < requiredPicks else { return }
            let orientation = Bool.random() ? "upright" : "reversed"
            let card = deck[index]
            usedIndices.insert(index)
            deckPicks.append(PickedDeckCard(id: deckPicks.count, deckIndex: index, card: card, orientation: orientation))
        } label: {
            ZStack {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: taken
                                ? [TodayFlowTheme.cardStrong.opacity(0.35), TodayFlowTheme.cardStrong.opacity(0.2)]
                                : [
                                    Color(red: 0.14, green: 0.12, blue: 0.24),
                                    Color(red: 0.22, green: 0.18, blue: 0.32),
                                ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .aspectRatio(0.62, contentMode: .fit)
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(
                                taken ? TodayFlowTheme.contour.opacity(0.3) : Color(red: 0.78, green: 0.66, blue: 0.35).opacity(0.5),
                                lineWidth: 1.2
                            )
                    )
                if taken {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                        .foregroundStyle(TodayFlowTheme.accent.opacity(0.85))
                } else {
                    Text("✶")
                        .font(.title2)
                        .foregroundStyle(Color(red: 0.85, green: 0.72, blue: 0.45))
                }
            }
        }
        .buttonStyle(.plain)
        .disabled(taken || deckPicks.count >= requiredPicks)
    }

    private var allPicksForDisplay: [(label: String, card: TarotCardDTO, orientation: String)] {
        var rows: [(String, TarotCardDTO, String)] = []
        if let anchorCard, let orient = config.anchorOrientation {
            let label = config.positionLabels.first ?? TarotExperienceChrome.anchorLabel
            rows.append((label, anchorCard, orient))
        }
        for (idx, pick) in deckPicks.enumerated() {
            let offset = config.anchorCardId != nil ? idx + 1 : idx
            let label = offset < config.positionLabels.count
                ? config.positionLabels[offset]
                : TarotExperienceChrome.cardFallback
            rows.append((label, pick.card, pick.orientation))
        }
        return rows
    }

    private var picksSummary: some View {
        Group {
            if !deckPicks.isEmpty || anchorCard != nil {
                VStack(alignment: .leading, spacing: 12) {
                    Text(TarotExperienceChrome.yourPick)
                        .font(.headline)
                        .foregroundStyle(TodayFlowTheme.ink)
                    ForEach(Array(allPicksForDisplay.enumerated()), id: \.offset) { _, row in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(row.label)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            TarotCardFace(
                                name: row.card.name,
                                orientation: row.orientation,
                                keywords: row.card.keywordList,
                                meaning: row.card.meaning(for: row.orientation)
                            )
                        }
                    }
                    Button(TarotExperienceChrome.reset) {
                        deckPicks = []
                        usedIndices = []
                        resultContext = nil
                        synthesisTracked = false
                        selectedFollowUpChipId = nil
                        followUpSaved = false
                    }
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.accent)
                }
                .padding(18)
                .todayFlowCard()
            }
        }
    }

    private var revealButton: some View {
        let anchorReady = config.anchorCardId == nil || (anchorCard != nil && !anchorLoading)
        let picksReady = deckPicks.count == requiredPicks
        return Button {
            Task { await fetchResult() }
        } label: {
            if resultLoading {
                ProgressView()
                    .frame(maxWidth: .infinity)
            } else {
                Label(TarotExperienceChrome.openReading, systemImage: "sparkles")
                    .frame(maxWidth: .infinity)
            }
        }
        .buttonStyle(.borderedProminent)
        .tint(TodayFlowTheme.ink)
        .disabled(!anchorReady || !picksReady || resultLoading)
    }

    private func resultBlock(_ ctx: TarotSpreadContextDTO) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            if let reading = ctx.reading {
                TarotReadingStorySurfaceView(
                    question: config.question,
                    reading: reading,
                    concernDomain: config.concernDomain,
                    store: store,
                    spreadId: ctx.spread.spreadId,
                    generationLogId: ctx.generationLogId,
                    selectedChipId: $selectedFollowUpChipId,
                    followUpSaved: $followUpSaved
                )
            }

            Button {
                deckPicks = []
                usedIndices = []
                resultContext = nil
                synthesisTracked = false
                selectedFollowUpChipId = nil
                followUpSaved = false
                Task { await loadDeck() }
            } label: {
                Label(TarotExperienceChrome.newSpread, systemImage: "arrow.counterclockwise")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
        }
        .onAppear {
            trackSynthesisIfNeeded(ctx)
        }
    }

    private func trackSynthesisIfNeeded(_ ctx: TarotSpreadContextDTO) {
        guard !synthesisTracked else { return }
        synthesisTracked = true
        let spreadId = ctx.spread.spreadId
        Task {
            var payload: [String: JSONValue] = ["spread_id": .string(spreadId)]
            if let gid = ctx.generationLogId, gid > 0 {
                payload["generation_id"] = .number(Double(gid))
            }
            await store.trackTarotFlowEvent(
                eventType: "first_synthesis_viewed",
                idempotencyKey: "tarot-synthesis:\(spreadId):\(ctx.generationLogId ?? 0)",
                payload: payload
            )
            await store.trackTarotFlowEvent(
                eventType: "tarot_spread_done",
                idempotencyKey: "tarot-spread-done:\(spreadId):\(ctx.generationLogId ?? 0)",
                payload: payload
            )
            TarotJourneyStore.append(
                question: config.question,
                concernDomain: config.concernDomain,
                spreadId: spreadId,
                spreadTitle: config.title,
                cardIds: ctx.spread.cards.map(\.card.id),
                cardNames: ctx.spread.cards.map(\.card.name)
            )
        }
    }

    private func loadAnchorIfNeeded() async {
        guard let anchorId = config.anchorCardId else {
            anchorCard = nil
            return
        }
        anchorLoading = true
        defer { anchorLoading = false }
        do {
            anchorCard = try await TarotClient.fetchTarotCard(cardId: anchorId)
        } catch {
            anchorCard = nil
            errorMessage = error.localizedDescription
        }
    }

    private func loadDeck() async {
        deckLoading = true
        errorMessage = nil
        defer { deckLoading = false }
        do {
            deck = try await TarotClient.drawDeck(count: config.deckCount)
            deckPicks = []
            usedIndices = []
            resultContext = nil
        } catch {
            deck = []
            errorMessage = error.localizedDescription
        }
    }

    private func fetchResult() async {
        resultLoading = true
        defer { resultLoading = false }
        var selected: [(Int, String)] = deckPicks.map { ($0.card.id, $0.orientation) }
        if let anchorId = config.anchorCardId, let orient = config.anchorOrientation {
            selected.insert((anchorId, orient), at: 0)
        }
        do {
            resultContext = try await TarotClient.spreadContext(
                spreadId: config.spreadId,
                question: config.question,
                concernDomain: config.concernDomain,
                selected: selected
            )
            await loadFavorites()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func loadFavorites() async {
        do {
            favoriteIds = Set(try await TarotClient.fetchFavoriteIds())
        } catch {
            favoriteIds = []
        }
    }
}

// MARK: - Card reference (GET /tarot/cards/{id})

private struct TarotCardReferenceScreen: View {
    let cardId: Int

    @State private var card: TarotCardDTO?
    @State private var errorMessage: String?
    @State private var loading = true

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()
            if loading, card == nil {
                ProgressView()
            } else if let card {
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: 18) {
                        Text(card.name)
                            .font(.title2.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.ink)

                        TarotCardFace(
                            name: card.name,
                            orientation: "upright",
                            keywords: card.keywordList,
                            meaning: card.meaning(for: "upright")
                        )

                        TarotCardFace(
                            name: card.name,
                            orientation: "reversed",
                            keywords: card.keywordList,
                            meaning: card.meaning(for: "reversed")
                        )
                    }
                    .padding(.horizontal, 18)
                    .padding(.vertical, 16)
                }
            } else if let errorMessage {
                Text(errorMessage)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.roseClay)
                    .padding(18)
            }
        }
        .navigationTitle(TarotExperienceChrome.cardReferenceTitle)
        .todayflowNavigationBarTitleDisplayModeInline()
        .task {
            await load()
        }
    }

    private func load() async {
        loading = true
        errorMessage = nil
        defer { loading = false }
        do {
            card = try await TarotClient.fetchTarotCard(cardId: cardId)
        } catch {
            card = nil
            errorMessage = error.localizedDescription
        }
    }
}

// MARK: - Card chrome

private struct TarotCardFace: View {
    let name: String
    let orientation: String
    let keywords: [String]
    let meaning: String

    private var orientationLabel: String {
        orientation == "reversed" ? TarotExperienceChrome.orientationReversed : TarotExperienceChrome.orientationUpright
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(name)
                    .font(.title3.weight(.bold))
                    .foregroundStyle(Color(red: 0.96, green: 0.94, blue: 0.88))
                Spacer()
                Text(orientationLabel)
                    .font(.caption.weight(.bold))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.white.opacity(0.12), in: Capsule())
                    .foregroundStyle(Color(red: 0.92, green: 0.82, blue: 0.55))
            }
            if !keywords.isEmpty {
                FlowKeywordRow(keywords: keywords)
            }
            Text(meaning)
                .font(.subheadline)
                .foregroundStyle(Color.white.opacity(0.88))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(18)
        .background(
            LinearGradient(
                colors: [
                    Color(red: 0.15, green: 0.13, blue: 0.28),
                    Color(red: 0.10, green: 0.10, blue: 0.16)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ),
            in: RoundedRectangle(cornerRadius: 24, style: .continuous)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color(red: 0.78, green: 0.64, blue: 0.38).opacity(0.42), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.2), radius: 16, x: 0, y: 10)
    }
}

private struct FlowKeywordRow: View {
    let keywords: [String]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(keywords, id: \.self) { kw in
                    Text(kw)
                        .font(.caption2.weight(.medium))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.white.opacity(0.1), in: Capsule())
                        .foregroundStyle(Color.white.opacity(0.85))
                }
            }
        }
    }
}

private struct TarotJourneyPanelView: View {
    var compact: Bool = false

    private var summary: TarotJourneySummary {
        TarotJourneySummaryBuilder.build(entries: TarotJourneyStore.readEntries())
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Твоё путешествие через карты")
                .font(.caption.weight(.semibold))
                .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))
            Text(summary.periodLabel.prefix(1).uppercased() + summary.periodLabel.dropFirst())
                .font(.headline)
                .foregroundStyle(Color(red: 0.92, green: 0.88, blue: 0.82))
            Text("Не статистика — история: какие темы и карты сопровождали твои вопросы.")
                .font(.subheadline)
                .foregroundStyle(Color(red: 0.72, green: 0.68, blue: 0.62))

            if !summary.themes.isEmpty {
                Text("Чаще всего встречались темы")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.68, green: 0.64, blue: 0.58))
                FlowLayoutChips(items: summary.themes.map { "\($0.emoji) \($0.label)" })
            }

            if !compact, !summary.frequentCards.isEmpty {
                Text("Карты, которые приходили чаще")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(Color(red: 0.68, green: 0.64, blue: 0.58))
                FlowLayoutChips(items: summary.frequentCards.map { card in
                    card.count > 1 ? "\(card.name) · \(card.count)" : card.name
                })
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.06), in: RoundedRectangle(cornerRadius: 16))
    }
}

private struct FlowLayoutChips: View {
    let items: [String]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(items, id: \.self) { item in
                    Text(item)
                        .font(.caption.weight(.medium))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.white.opacity(0.08), in: Capsule())
                        .foregroundStyle(Color(red: 0.88, green: 0.84, blue: 0.78))
                }
            }
        }
    }
}

#Preview("Tarot hub") {
    TarotHubView(store: TodayFlowStore())
}
