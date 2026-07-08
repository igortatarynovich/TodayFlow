import SwiftUI

/// Guidance: тот же контракт, что у веба — расклад, вопрос, контекст и карты на одном скролле → `POST /questions/reading`.
struct QuestionsView: View {
    enum PrimaryFlow: String, CaseIterable, Identifiable {
        case tarotWizard
        case quickAnswer

        var id: String { rawValue }

        var title: String {
            switch self {
            case .tarotWizard: return GuidanceViewChrome.primaryTarot
            case .quickAnswer: return GuidanceViewChrome.primaryQuick
            }
        }
    }

    enum GuidanceSpreadSection: CaseIterable, Hashable {
        case quick
        case medium
        case deep

        var title: String {
            switch self {
            case .quick: return GuidanceViewChrome.spreadSectionQuick
            case .medium: return GuidanceViewChrome.spreadSectionMedium
            case .deep: return GuidanceViewChrome.spreadSectionDeep
            }
        }
    }

    struct GuidanceSpreadItem: Identifiable {
        let id: String
        let section: GuidanceSpreadSection
        let title: String
        let subtitle: String
    }

    struct QuickEntry: Identifiable {
        let id: String
        let icon: String
        let title: String
        let hint: String
        let prompt: String
    }

    enum Lane: String, CaseIterable, Identifiable {
        case daily
        case decision
        case pattern

        var id: String { rawValue }

        var title: String { GuidanceViewChrome.laneTitle(raw: rawValue) }

        var prompt: String { GuidanceViewChrome.lanePrompt(raw: rawValue) }

        var quickPrompts: [String] { GuidanceViewChrome.laneQuickPrompts(raw: rawValue) }
    }

    fileprivate static func makeGuidanceSpreads() -> [GuidanceSpreadItem] {
        let r = IOSAppLocale.prefersRussian
        func row(_ id: String, _ section: GuidanceSpreadSection, _ tRu: String, _ tEn: String, _ sRu: String, _ sEn: String) -> GuidanceSpreadItem {
            GuidanceSpreadItem(id: id, section: section, title: r ? tRu : tEn, subtitle: r ? sRu : sEn)
        }
        return [
            row("one_card", .quick, "Одна карта", "One card", "Короткий фокус на ситуацию.", "A tight focus on the situation."),
            row("guidance_yes_no", .quick, "Да / Нет", "Yes / No", "Что поддерживает, что мешает, где нюанс.", "What helps, what blocks, where the nuance is."),
            row("guidance_what_happening", .quick, "Что происходит?", "What’s happening?", "Когда много эмоций и мало ясности.", "When emotions run high and clarity is low."),
            row("three_cards", .medium, "Три карты", "Three cards", "Прошлое — настоящее — возможное развитие.", "Past — present — possible unfolding."),
            row("guidance_choice_two", .medium, "Выбор", "Choice", "Два варианта и практический шаг.", "Two paths and a practical step."),
            row("guidance_relationship_five", .medium, "Отношения", "Relationships", "Чувства, дистанция, динамика.", "Feelings, distance, dynamics."),
            row("guidance_sexual_five", .medium, "Сексуальная динамика", "Sexual dynamics", "Желание, границы и темп в паре.", "Desire, boundaries, and pace together."),
            row("guidance_inner_conflict", .deep, "Внутренний конфликт", "Inner conflict", "Когда части тебя хотят разного.", "When different parts of you want different things."),
            row("guidance_work_money", .deep, "Работа и деньги", "Work and money", "Решения по ресурсу и карьере.", "Choices about resources and career."),
            row("guidance_deep_eight", .deep, "Глубокий разбор", "Deep reading", "Сложная ситуация из нескольких слоёв.", "A layered, complex situation."),
        ]
    }

    private enum GuidanceTarotScrollID: Hashable {
        case spread, question, context, cards, result
    }

    let store: TodayFlowStore
    var onRouteSelected: ((String) -> Void)? = nil

    @State private var primaryFlow: PrimaryFlow = .tarotWizard

    // MARK: Quick answer (без карт)

    @State private var selectedLane: Lane = .daily
    @State private var quickQuestion = ""
    @State private var quickLoading = false
    @State private var quickResult: QuestionAnswerResult?
    @State private var quickError: String?

    // MARK: Tarot Guidance

    @State private var selectedSpreadId: String = "one_card"
    @State private var tarotQuestion = ""
    @State private var topicId: String?
    @State private var outcomeId: String?
    @State private var relationshipRoleId: String?
    @State private var intimacyFocusId: String?
    @State private var spreadDTO: TarotSpreadResultDTO?
    @State private var revealed: [Bool] = []
    @State private var drawing = false
    @State private var readingLoading = false
    @State private var guidanceResult: GuidanceReadingResult?
    @State private var tarotError: String?

    /// Одна уточняющая карта к последнему основному разбору (`POST /questions/reading/clarify`).
    @State private var clarifyMode = false
    @State private var clarifyParentLogId: Int?
    /// Снимок основного разбора до уточнения — для восстановления при 409.
    @State private var clarifyBackupResult: GuidanceReadingResult?
    @State private var guidanceClarifyConsumed = false
    @State private var clarificationGoalId: String = "next_step"

    @State private var showHistory = false

    @State private var guidanceResonanceChoice: String?
    @State private var guidanceResonanceSaved = false
    @State private var guidanceLegacyFeedback: String?
    @State private var guidanceFeedbackComment = ""
    @State private var guidanceFeedbackBusy = false
    @State private var guidanceFeedbackMessage: String?

    @State private var quickLegacyFeedback: String?
    @State private var quickFeedbackBusy = false

    private var tarotQuestionTrimmed: String {
        tarotQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var tarotQuestionOk: Bool {
        clarifyMode || tarotQuestionTrimmed.count >= 3
    }

    private var tarotAllRevealed: Bool {
        guard let spreadDTO else { return false }
        return revealed.count == spreadDTO.cards.count && revealed.allSatisfy { $0 }
    }

    private var tarotCanRequestReading: Bool {
        guard let spreadDTO, !spreadDTO.cards.isEmpty else { return false }
        guard tarotAllRevealed, !readingLoading else { return false }
        if clarifyMode {
            return clarifyParentLogId != nil && guidanceResult == nil
        }
        return guidanceResult == nil
    }

    private var topicChoices: [(id: String, label: String)] { GuidanceViewChrome.topicChoices }
    private var outcomeChoices: [(id: String, label: String)] { GuidanceViewChrome.outcomeChoices }
    private var relationshipRoles: [(id: String, label: String)] { GuidanceViewChrome.relationshipRoles }
    private var intimacyChoices: [(id: String, label: String)] { GuidanceViewChrome.intimacyChoices }

    private var quickEntries: [QuickEntry] {
        GuidanceViewChrome.quickEntryRows.map { QuickEntry(id: $0.0, icon: $0.1, title: $0.2, hint: $0.3, prompt: $0.4) }
    }

    /// Паритет с `GUIDANCE_CLARIFICATION_GOALS` (`frontend/src/lib/guidance/catalog.ts`).
    private var clarificationGoalChoices: [(id: String, label: String)] { GuidanceViewChrome.clarificationGoals }

    var body: some View {
        NavigationStack {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        heroHeader

                        Picker(GuidanceViewChrome.modePicker, selection: $primaryFlow) {
                            ForEach(PrimaryFlow.allCases) { flow in
                                Text(flow.title).tag(flow)
                            }
                        }
                        .pickerStyle(.segmented)

                        switch primaryFlow {
                        case .tarotWizard:
                            VStack(alignment: .leading, spacing: 14) {
                                tarotSectionJumpBar(proxy: proxy)
                                tarotGuidanceScrollStack
                            }
                        case .quickAnswer:
                            quickAnswerStack
                        }
                    }
                    .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 14)
                    .onChange(of: guidanceResult?.question) { _, newQuestion in
                        guard newQuestion != nil else { return }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) {
                            withAnimation(.easeInOut(duration: 0.35)) {
                                proxy.scrollTo(GuidanceTarotScrollID.result, anchor: UnitPoint(x: 0.5, y: 0.02))
                            }
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .navigationTitle(GuidanceViewChrome.navTitle)
            .toolbar {
                ToolbarItemGroup(placement: .topBarTrailing) {
                    if primaryFlow == .tarotWizard {
                        Button(GuidanceViewChrome.startOver) {
                            resetTarotFlow()
                        }
                    }
                    Button {
                        showHistory = true
                    } label: {
                        Image(systemName: "clock.arrow.circlepath")
                    }
                    .accessibilityLabel(GuidanceViewChrome.historyA11y)
                }
            }
            .sheet(isPresented: $showHistory) {
                GuidanceHistorySheet(store: store, onRouteSelected: onRouteSelected)
            }
            .onChange(of: store.guidanceHubCompatRouteToken) { _, _ in
                guard let payload = store.consumeGuidanceHubCompatPrefill() else { return }
                applyGuidanceHubCompatPrefill(payload)
            }
        }
    }

    private func applyGuidanceHubCompatPrefill(_ p: TodayFlowStore.GuidanceHubCompatPrefill) {
        primaryFlow = .tarotWizard
        resetTarotFlow()
        tarotQuestion = p.suggestedQuestion
        topicId = p.topicId
        outcomeId = p.outcomeId
        relationshipRoleId = p.relationshipRoleId
        selectedSpreadId = p.spreadId
    }

    private var heroHeader: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(GuidanceViewChrome.heroTitle)
                .font(.system(size: 28, weight: .bold, design: .rounded))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(GuidanceViewChrome.heroBody)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 28)
    }

    // MARK: Tarot guidance (single scroll)

    private func tarotSectionJumpBar(proxy: ScrollViewProxy) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(GuidanceViewChrome.jumpBarLabel)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.52))
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    tarotJumpChip(title: GuidanceViewChrome.jumpSpread) {
                        tarotScrollTo(proxy, GuidanceTarotScrollID.spread)
                    }
                    tarotJumpChip(title: GuidanceViewChrome.jumpQuestion) {
                        tarotScrollTo(proxy, GuidanceTarotScrollID.question)
                    }
                    tarotJumpChip(title: GuidanceViewChrome.jumpContext) {
                        tarotScrollTo(proxy, GuidanceTarotScrollID.context)
                    }
                    tarotJumpChip(title: GuidanceViewChrome.jumpCards) {
                        tarotScrollTo(proxy, GuidanceTarotScrollID.cards)
                    }
                    tarotJumpChip(title: GuidanceViewChrome.jumpReading, disabled: guidanceResult == nil) {
                        tarotScrollTo(proxy, GuidanceTarotScrollID.result)
                    }
                }
                .padding(.vertical, 2)
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel(GuidanceViewChrome.jumpBarA11y)
    }

    private func tarotScrollTo(_ proxy: ScrollViewProxy, _ id: GuidanceTarotScrollID) {
        withAnimation(.easeInOut(duration: 0.35)) {
            proxy.scrollTo(id, anchor: UnitPoint(x: 0.5, y: 0.02))
        }
    }

    private func tarotJumpChip(title: String, disabled: Bool = false, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(disabled ? TodayFlowTheme.ink.opacity(0.38) : TodayFlowTheme.ink.opacity(0.88))
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(disabled ? Color.white.opacity(0.45) : Color.white.opacity(0.78))
                .clipShape(Capsule())
                .overlay(
                    Capsule()
                        .stroke(disabled ? TodayFlowTheme.sand.opacity(0.15) : TodayFlowTheme.sand.opacity(0.32), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
        .disabled(disabled)
        .accessibilityHint(disabled && title == GuidanceViewChrome.jumpReading ? GuidanceViewChrome.jumpReadingHint : "")
    }

    private var tarotGuidanceScrollStack: some View {
        VStack(alignment: .leading, spacing: 20) {
            tarotSpreadSection
            if clarifyMode {
                tarotClarifyGoalSection
            }
            tarotQuestionSection
            tarotContextSection
            tarotCardsSection

            if readingLoading {
                tarotReadingLoadingPanel
            }

            if let tarotError {
                Text(tarotError)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.roseClay)
            }

            if let guidanceResult {
                guidanceResultSection(guidanceResult)
                    .id(GuidanceTarotScrollID.result)
            }
        }
    }

    @ViewBuilder
    private func guidanceTarotSectionChrome(number: Int, title: String, lead: String?) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text("\(number)")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.ember)
                    .frame(width: 28, height: 28)
                    .background(TodayFlowTheme.sunset.opacity(0.22))
                    .clipShape(Circle())
                Text(title)
                    .font(.title3.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            if let lead {
                Text(lead)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var tarotSpreadSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            guidanceTarotSectionChrome(
                number: 1,
                title: GuidanceViewChrome.secSpreadTitle,
                lead: GuidanceViewChrome.secSpreadLead
            )
            Picker(GuidanceViewChrome.spreadPicker, selection: $selectedSpreadId) {
                ForEach(GuidanceSpreadSection.allCases, id: \.self) { section in
                    Section(section.title) {
                        ForEach(Self.makeGuidanceSpreads().filter { $0.section == section }) { item in
                            Text(item.title).tag(item.id)
                        }
                    }
                }
            }
            .pickerStyle(.menu)
            .tint(TodayFlowTheme.sunset)
            .disabled(clarifyMode)
            if let picked = Self.makeGuidanceSpreads().first(where: { $0.id == selectedSpreadId }) {
                VStack(alignment: .leading, spacing: 6) {
                    Text(picked.subtitle)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .todayFlowSurfaceSoft(cornerRadius: 16)
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .id(GuidanceTarotScrollID.spread)
    }

    private var tarotClarifyGoalSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            guidanceTarotSectionChrome(
                number: 2,
                title: GuidanceViewChrome.secClarifyTitle,
                lead: GuidanceViewChrome.secClarifyLead
            )
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(clarificationGoalChoices, id: \.id) { item in
                        let selected = clarificationGoalId == item.id
                        Button {
                            clarificationGoalId = item.id
                        } label: {
                            Text(item.label)
                                .font(.caption.weight(.semibold))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(selected ? TodayFlowTheme.sunset.opacity(0.28) : Color.white.opacity(0.78))
                                .clipShape(Capsule())
                                .overlay(
                                    Capsule()
                                        .stroke(selected ? TodayFlowTheme.sunset.opacity(0.45) : TodayFlowTheme.sand.opacity(0.28), lineWidth: 1)
                                )
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
    }

    private var tarotQuestionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            guidanceTarotSectionChrome(
                number: clarifyMode ? 3 : 2,
                title: GuidanceViewChrome.secQuestionTitle,
                lead: clarifyMode
                    ? GuidanceViewChrome.secQuestionLeadClarify
                    : GuidanceViewChrome.secQuestionLeadNormal
            )
            TextField(GuidanceViewChrome.questionPlaceholder, text: $tarotQuestion, axis: .vertical)
                .todayFlowSystemTextInput()
                .textFieldStyle(.plain)
                .padding(16)
                .background(Color.white.opacity(0.85))
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                .disabled(clarifyMode)
                .opacity(clarifyMode ? 0.72 : 1)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .id(GuidanceTarotScrollID.question)
    }

    private var tarotContextSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            guidanceTarotSectionChrome(
                number: clarifyMode ? 4 : 3,
                title: GuidanceViewChrome.secContextTitle,
                lead: clarifyMode
                    ? GuidanceViewChrome.secContextLeadClarify
                    : GuidanceViewChrome.secContextLeadNormal
            )
            chipGroup(title: GuidanceViewChrome.chipTopic, choices: topicChoices, selection: $topicId) {
                relationshipRoleId = nil
                intimacyFocusId = nil
            }
            chipGroup(title: GuidanceViewChrome.chipOutcome, choices: outcomeChoices, selection: $outcomeId)
            if topicId == "relationships" {
                chipGroup(title: GuidanceViewChrome.chipWho, choices: relationshipRoles, selection: $relationshipRoleId)
            }
            if topicId == "intimacy" {
                chipGroup(title: GuidanceViewChrome.chipIntimacy, choices: intimacyChoices, selection: $intimacyFocusId)
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .opacity(clarifyMode ? 0.55 : 1)
        .disabled(clarifyMode)
        .id(GuidanceTarotScrollID.context)
    }

    private var tarotCardsSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            guidanceTarotSectionChrome(
                number: clarifyMode ? 5 : 4,
                title: GuidanceViewChrome.secCardsTitle,
                lead: clarifyMode
                    ? GuidanceViewChrome.secCardsLeadClarify
                    : GuidanceViewChrome.secCardsLeadNormal
            )
            if spreadDTO == nil {
                Text(GuidanceViewChrome.dealHint)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            }
            Button {
                Task { await drawSpread() }
            } label: {
                if drawing {
                    ProgressView()
                } else {
                    Text(spreadDTO == nil ? GuidanceViewChrome.dealCards : GuidanceViewChrome.reshuffle)
                }
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.sunset)
            .disabled(drawing || readingLoading || (guidanceResult != nil && !clarifyMode))

            if let spreadDTO {
                ForEach(Array(spreadDTO.cards.enumerated()), id: \.offset) { index, card in
                    cardRow(index: index, card: card)
                }

                if !tarotAllRevealed {
                    Text(GuidanceViewChrome.revealAllHint)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.65))
                        .padding(.top, 4)
                }

                if tarotCanRequestReading {
                    Button {
                        Task { await submitGuidanceReading() }
                    } label: {
                        Label(clarifyMode ? GuidanceViewChrome.getClarification : GuidanceViewChrome.getReading, systemImage: "sparkles")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(TodayFlowTheme.sunset)
                    .disabled(!tarotQuestionOk)

                    if !tarotQuestionOk {
                        Text(clarifyMode ? GuidanceViewChrome.needQuestionClarify : GuidanceViewChrome.needQuestionNormal)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                            .padding(.top, 4)
                    }
                }
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .id(GuidanceTarotScrollID.cards)
    }

    private var tarotReadingLoadingPanel: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(clarifyMode ? GuidanceViewChrome.loadingClarify : GuidanceViewChrome.loadingReading)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(clarifyMode
                ? GuidanceViewChrome.loadingClarifySub
                : GuidanceViewChrome.loadingReadingSub)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
            HStack {
                ProgressView()
                Spacer()
            }
            .padding(.top, 4)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 22)
    }

    private func cardRow(index: Int, card: TarotSpreadCardDTO) -> some View {
        let open = index < revealed.count && revealed[index]
        let revLabel = GuidanceViewChrome.orientationLabel(card.orientation)
        return HStack(alignment: .top, spacing: 14) {
            guidanceTarotThumb(deckIndex: card.card.id, orientation: card.orientation, showFace: open)
            VStack(alignment: .leading, spacing: 8) {
                Text(card.position.title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                if let prompt = card.position.prompt?.trimmingCharacters(in: .whitespacesAndNewlines), !prompt.isEmpty {
                    Text(prompt)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                }
                if open {
                    Text(card.card.name)
                        .font(.headline)
                    Text(revLabel)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.65))
                    if !card.card.keywordList.isEmpty {
                        Text(card.card.keywordList.prefix(8).joined(separator: " · "))
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.sand.opacity(0.95))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    Text(card.meaning)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                } else {
                    Button(GuidanceViewChrome.openCard) {
                        revealCard(at: index)
                    }
                    .buttonStyle(.bordered)
                }
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 16)
    }

    // MARK: Quick stack

    private var quickAnswerStack: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack(spacing: 8) {
                StageChip(title: GuidanceViewChrome.quickStage1, isActive: !trimmedQuickQuestion.isEmpty)
                StageChip(title: GuidanceViewChrome.quickStage2, isActive: quickResult != nil)
                StageChip(title: GuidanceViewChrome.quickStage3, isActive: quickResult?.suggestedRoute.href.isEmpty == false)
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(quickEntries) { entry in
                        Button {
                            quickQuestion = entry.prompt
                        } label: {
                            VStack(alignment: .leading, spacing: 6) {
                                Text("\(entry.icon) \(entry.title)")
                                    .font(.subheadline.weight(.semibold))
                                    .foregroundStyle(TodayFlowTheme.ink)
                                Text(entry.hint)
                                    .font(.caption)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.66))
                                    .multilineTextAlignment(.leading)
                            }
                            .padding(12)
                            .frame(width: 220, alignment: .leading)
                            .background(quickQuestion.trimmingCharacters(in: .whitespacesAndNewlines) == entry.prompt ? Color.white.opacity(0.9) : Color.white.opacity(0.72))
                            .overlay(
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .stroke(
                                        quickQuestion.trimmingCharacters(in: .whitespacesAndNewlines) == entry.prompt
                                            ? TodayFlowTheme.sand.opacity(0.7)
                                            : TodayFlowTheme.sand.opacity(0.28),
                                        lineWidth: 1
                                    )
                            )
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                        }
                        .buttonStyle(LuxeOptionCardButtonStyle())
                    }
                }
            }

            Picker(GuidanceViewChrome.lanePicker, selection: $selectedLane) {
                ForEach(Lane.allCases) { lane in
                    Text(lane.title).tag(lane)
                }
            }
            .pickerStyle(.segmented)

            VStack(alignment: .leading, spacing: 12) {
                Text(GuidanceViewChrome.yourQuestion)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)

                TextField(selectedLane.prompt, text: $quickQuestion, axis: .vertical)
                    .todayFlowSystemTextInput()
                    .textFieldStyle(.plain)
                    .padding(18)
                    .background(Color.white.opacity(0.82))
                    .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))

                Button {
                    submitQuick()
                } label: {
                    Label(quickLoading ? GuidanceViewChrome.quickLoadingCta : GuidanceViewChrome.quickOpenReading, systemImage: "sparkles")
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(LuxePrimaryCTAButtonStyle())
                .foregroundStyle(.white)
                .background(
                    LinearGradient(colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember], startPoint: .leading, endPoint: .trailing)
                )
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                .shadow(color: TodayFlowTheme.ember.opacity(0.32), radius: 12, x: 0, y: 6)
                .disabled(quickLoading || trimmedQuickQuestion.count < 3)
            }
            .padding(22)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.66))
            .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
            .shadow(color: Color.black.opacity(0.05), radius: 18, x: 0, y: 8)

            if let quickError {
                Text(quickError)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.roseClay)
                    .padding(.horizontal, 4)
            }

            if let quickResult {
                quickResultSection(quickResult)
            }
        }
    }

    private func quickResultSection(_ result: QuestionAnswerResult) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(result.laneTitle)
                        .font(.headline)
                    Text(result.question)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                }
                Spacer()
                Text(result.profileReady ? GuidanceViewChrome.badgeWithProfile : GuidanceViewChrome.badgeNoProfile)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.white.opacity(0.58))
                    .clipShape(Capsule())
            }
            QuestionAnswerCard(title: GuidanceViewChrome.ansClarity, text: result.answer.clarity)
            QuestionAnswerCard(title: GuidanceViewChrome.ansExplanation, text: stripTarotAppend(result.answer.explanation))
            QuestionAnswerCard(title: GuidanceViewChrome.ansToday, text: result.answer.today)
            QuestionAnswerCard(title: GuidanceViewChrome.ansDecision, text: result.answer.decision)
            QuestionAnswerCard(title: GuidanceViewChrome.ansForecast, text: result.answer.forecast)
            VStack(alignment: .leading, spacing: 6) {
                Text(GuidanceViewChrome.nextRoute)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Text(result.suggestedRoute.label)
                    .font(.headline)
                Text(result.suggestedRoute.reason)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                Button(GuidanceViewChrome.openNextStep) {
                    onRouteSelected?(result.suggestedRoute.href)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceSoft(cornerRadius: 20)

            quickFeedbackSection(result)
        }
        .padding(22)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 28)
    }

    private func guidanceResultSection(_ result: GuidanceReadingResult) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(result.laneTitle)
                        .font(.headline)
                    Text(result.question)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                }
                Spacer()
                Text(result.profileReady ? GuidanceViewChrome.badgeProfileShort : GuidanceViewChrome.badgeNoProfile)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.white.opacity(0.58))
                    .clipShape(Capsule())
            }
            if result.isClarification == true {
                Text(GuidanceViewChrome.clarifyingCard)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            Text(GuidanceViewChrome.spreadColon(spreadTitle(for: result.spreadId)))
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            if let goal = result.clarificationGoal,
               result.isClarification == true,
               let label = clarificationGoalChoices.first(where: { $0.id == goal })?.label {
                Text(GuidanceViewChrome.focusColon(label))
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            }

            if let qa = result.questionAssessment,
               qa.suggestion?.isEmpty == false || qa.weakReadingWarning?.isEmpty == false {
                VStack(alignment: .leading, spacing: 6) {
                    Text(GuidanceViewChrome.questionStrength)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    if let w = qa.weakReadingWarning, !w.isEmpty {
                        Text(w)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                    }
                    if let s = qa.suggestion, !s.isEmpty {
                        Text(s)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    }
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .todayFlowSurfaceSoft(cornerRadius: 16)
            }

            QuestionAnswerCard(
                title: GuidanceViewChrome.ansShort,
                text: result.interpretation?.summary ?? result.editorial?.currentFocus ?? result.answer.clarity
            )
            QuestionAnswerCard(title: GuidanceViewChrome.ansWhatsHappening, text: stripTarotAppend(result.answer.explanation))

            if !result.tarotCards.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Text(GuidanceViewChrome.ansCardByCard)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                    ForEach(Array(result.tarotCards.enumerated()), id: \.offset) { _, card in
                        guidanceResultTarotCardRow(card: card)
                    }
                }
            }

            if let bridge = result.interpretation?.profileBridge, !bridge.isEmpty {
                QuestionAnswerCard(title: GuidanceViewChrome.ansForYou, text: bridge)
            }

            QuestionAnswerCard(
                title: GuidanceViewChrome.ansCore,
                text: result.interpretation?.coreInsight ?? result.answer.forecast
            )

            if let why = result.interpretation?.whyOutline, !why.isEmpty {
                QuestionAnswerCard(title: GuidanceViewChrome.ansWhy, text: why)
                if let wn = result.interpretation?.positionWeightsNote, !wn.isEmpty {
                    Text(wn)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                }
            }

            if let cont = result.interpretation?.continueHint, !cont.isEmpty {
                QuestionAnswerCard(title: GuidanceViewChrome.ansContinue, text: cont)
            }

            if let avoid = result.interpretation?.avoid, !avoid.isEmpty {
                QuestionAnswerCard(title: GuidanceViewChrome.ansAvoid, text: avoid)
            }

            QuestionAnswerCard(title: GuidanceViewChrome.ansDo, text: result.answer.decision)
            QuestionAnswerCard(
                title: GuidanceViewChrome.ansNextStep,
                text: result.editorial?.nextStep ?? (result.interpretation?.action ?? result.answer.today)
            )

            VStack(alignment: .leading, spacing: 8) {
                Text(GuidanceViewChrome.route)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Text(result.suggestedRoute.label)
                    .font(.headline)
                Button(GuidanceViewChrome.openNextStep) {
                    onRouteSelected?(result.suggestedRoute.href)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
                if let fb = result.flowBridge {
                    Text(fb.reason)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .padding(.top, 6)
                    Button(fb.label) {
                        onRouteSelected?(fb.href)
                    }
                    .buttonStyle(.bordered)
                    .padding(.top, 4)
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceSoft(cornerRadius: 18)

            if result.generationLogId != nil,
               result.isClarification != true,
               !guidanceClarifyConsumed {
                Button {
                    beginGuidanceClarify(from: result)
                } label: {
                    Label(GuidanceViewChrome.pullClarifier, systemImage: "plus.circle")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }

            guidanceFeedbackSection(result)

            Button(GuidanceViewChrome.newSpread) {
                resetTarotFlow()
            }
            .buttonStyle(.bordered)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 26)
    }

    // MARK: Helpers

    private var trimmedQuickQuestion: String {
        quickQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private func preferredLaneRaw() -> String {
        switch selectedLane {
        case .daily: return "daily"
        case .decision: return "decision"
        case .pattern: return "pattern"
        }
    }

    private func hubLaneHint() -> String? {
        guard let topicId else { return nil }
        switch topicId {
        case "relationships", "family", "intimacy":
            return "love"
        case "work", "money":
            return "money_career"
        case "choice":
            return "decision"
        case "inner_state":
            return "state"
        default:
            return nil
        }
    }

    /// Паритет с `userIntentFromOutcome` на вебе (`frontend/src/lib/guidance/catalog.ts`).
    private func userIntentFromOutcome(_ outcome: String?) -> String? {
        guard let outcome else { return nil }
        switch outcome {
        case "clarity": return "understand_situation"
        case "decision", "next_step": return "choose_action"
        case "understand_other": return "understand_person"
        case "understand_self": return "clarify_feelings"
        case "warning": return "see_risk"
        case "confirmation": return "close_cycle"
        default: return nil
        }
    }

    private func spreadTitle(for id: String) -> String {
        Self.makeGuidanceSpreads().first(where: { $0.id == id })?.title ?? id
    }

    private func stripTarotAppend(_ text: String) -> String {
        if let range = text.range(of: " Расклад (", options: .backwards) {
            return String(text[..<range.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        if let range = text.range(of: " Spread (", options: .backwards) {
            return String(text[..<range.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        return text
    }

    private func resetTarotFlow() {
        tarotQuestion = ""
        topicId = nil
        outcomeId = nil
        relationshipRoleId = nil
        intimacyFocusId = nil
        spreadDTO = nil
        revealed = []
        guidanceResult = nil
        tarotError = nil
        readingLoading = false
        clarifyMode = false
        clarifyParentLogId = nil
        clarifyBackupResult = nil
        guidanceClarifyConsumed = false
        clarificationGoalId = "next_step"
        resetGuidanceFeedbackState()
    }

    private func beginGuidanceClarify(from result: GuidanceReadingResult) {
        guard let logId = result.generationLogId, result.isClarification != true, !guidanceClarifyConsumed else { return }
        clarifyBackupResult = result
        clarifyMode = true
        clarifyParentLogId = logId
        clarificationGoalId = "next_step"
        selectedSpreadId = "one_card"
        spreadDTO = nil
        revealed = []
        guidanceResult = nil
        tarotError = nil
        readingLoading = false
        resetGuidanceFeedbackState()
    }

    private func resetGuidanceFeedbackState() {
        guidanceResonanceChoice = nil
        guidanceResonanceSaved = false
        guidanceLegacyFeedback = nil
        guidanceFeedbackComment = ""
        guidanceFeedbackBusy = false
        guidanceFeedbackMessage = nil
    }

    private func drawSpread() async {
        tarotError = nil
        drawing = true
        guidanceResult = nil
        do {
            let dto = try await TarotClient.drawSpread(spreadId: selectedSpreadId)
            await MainActor.run {
                spreadDTO = dto
                revealed = Array(repeating: false, count: dto.cards.count)
                drawing = false
            }
        } catch {
            await MainActor.run {
                tarotError = error.localizedDescription
                drawing = false
            }
        }
    }

    private func revealCard(at index: Int) {
        guard let dto = spreadDTO else { return }
        guard index >= 0, index < dto.cards.count else { return }
        if revealed.count != dto.cards.count {
            revealed = Array(repeating: false, count: dto.cards.count)
        }
        revealed[index] = true
    }

    private func submitGuidanceReading() async {
        guard let spreadDTO else { return }
        guard revealed.count == spreadDTO.cards.count, revealed.allSatisfy({ $0 }) else { return }

        if clarifyMode {
            guard clarifyParentLogId != nil else { return }
            guard selectedSpreadId == "one_card", spreadDTO.cards.count == 1 else {
                await MainActor.run {
                    tarotError = GuidanceViewChrome.clarifyOneCardOnly
                }
                return
            }
        } else {
            let q = tarotQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
            guard q.count >= 3 else { return }
        }

        tarotError = nil
        readingLoading = true
        let picks: [GuidanceSelectedCardBody] = spreadDTO.cards.map {
            GuidanceSelectedCardBody(card_id: $0.card.id, orientation: $0.orientation)
        }

        if clarifyMode, let parentId = clarifyParentLogId {
            do {
                let res = try await store.submitGuidanceClarify(
                    parentGenerationLogId: parentId,
                    clarificationGoal: clarificationGoalId,
                    selectedCards: picks
                )
                await MainActor.run {
                    clarifyMode = false
                    clarifyParentLogId = nil
                    clarifyBackupResult = nil
                    guidanceClarifyConsumed = true
                    guidanceResult = res
                    readingLoading = false
                    resetGuidanceFeedbackState()
                }
            } catch {
                await MainActor.run {
                    readingLoading = false
                    if case TodayFlowStore.StoreError.http(409, let msg) = error {
                        let trimmed = msg.trimmingCharacters(in: .whitespacesAndNewlines)
                        tarotError = trimmed.isEmpty
                            ? GuidanceViewChrome.clarifyAlreadyUsed
                            : trimmed
                        guidanceResult = clarifyBackupResult
                        clarifyBackupResult = nil
                        clarifyMode = false
                        clarifyParentLogId = nil
                        guidanceClarifyConsumed = true
                    } else {
                        tarotError = error.localizedDescription
                    }
                }
            }
            return
        }

        let q = tarotQuestion.trimmingCharacters(in: .whitespacesAndNewlines)
        let rel = topicId == "relationships" ? relationshipRoleId : nil
        let inti = topicId == "intimacy" ? intimacyFocusId : nil

        do {
            let res = try await store.submitGuidanceReading(
                question: q,
                spreadId: selectedSpreadId,
                selectedCards: picks,
                hubLaneHint: hubLaneHint(),
                topic: topicId,
                desiredOutcome: outcomeId,
                relationshipContext: rel,
                intimacyFocus: inti,
                userIntent: userIntentFromOutcome(outcomeId),
                requestedDepth: "normal",
                todayContextSummary: store.guidanceTodayContextSummaryForAPI()
            )
            await MainActor.run {
                if res.isClarification != true {
                    guidanceClarifyConsumed = false
                }
                guidanceResult = res
                readingLoading = false
                resetGuidanceFeedbackState()
            }
        } catch {
            await MainActor.run {
                tarotError = error.localizedDescription
                readingLoading = false
            }
        }
    }

    private func submitQuick() {
        guard trimmedQuickQuestion.count >= 3 else { return }
        quickLoading = true
        quickError = nil
        Task {
            do {
                let answer = try await store.answerQuestion(trimmedQuickQuestion, preferredLane: preferredLaneRaw())
                await MainActor.run {
                    quickResult = answer
                    quickLoading = false
                    quickLegacyFeedback = nil
                }
            } catch {
                await MainActor.run {
                    quickError = error.localizedDescription
                    quickLoading = false
                }
            }
        }
    }

    @ViewBuilder
    private func guidanceFeedbackSection(_ result: GuidanceReadingResult) -> some View {
        if let logId = result.generationLogId {
            VStack(alignment: .leading, spacing: 12) {
                Text(GuidanceViewChrome.feedbackHow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)

                HStack(spacing: 8) {
                    guidanceResonanceChip(title: GuidanceViewChrome.resonanceHigh, value: "high")
                    guidanceResonanceChip(title: GuidanceViewChrome.resonancePartial, value: "partial")
                    guidanceResonanceChip(title: GuidanceViewChrome.resonanceLow, value: "none")
                }

                TextField(GuidanceViewChrome.feedbackComment, text: $guidanceFeedbackComment, axis: .vertical)
                    .todayFlowSystemTextInput()
                    .lineLimit(2 ... 4)
                    .padding(12)
                    .background(Color.white.opacity(0.85))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .disabled(guidanceResonanceSaved || guidanceFeedbackBusy)

                Button {
                    Task { await submitGuidanceResonanceFeedback(logId: logId, result: result) }
                } label: {
                    Group {
                        if guidanceFeedbackBusy {
                            ProgressView()
                        } else {
                            Text(guidanceResonanceSaved ? GuidanceViewChrome.saved : GuidanceViewChrome.sendFeedback)
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
                .disabled(guidanceResonanceSaved || guidanceResonanceChoice == nil || guidanceFeedbackBusy)

                Divider().opacity(0.35)

                Text(GuidanceViewChrome.shortMark)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)

                HStack(spacing: 10) {
                    Button(guidanceLegacyFeedback == "answer_helpful" ? GuidanceViewChrome.helpfulDone : GuidanceViewChrome.helpful) {
                        Task { await submitGuidanceLegacyFeedback(logId: logId, result: result, signal: "answer_helpful") }
                    }
                    .buttonStyle(.bordered)
                    .disabled(guidanceLegacyFeedback != nil || guidanceFeedbackBusy)

                    Button(guidanceLegacyFeedback == "still_unclear" ? GuidanceViewChrome.unclearDone : GuidanceViewChrome.unclear) {
                        Task { await submitGuidanceLegacyFeedback(logId: logId, result: result, signal: "still_unclear") }
                    }
                    .buttonStyle(.bordered)
                    .disabled(guidanceLegacyFeedback != nil || guidanceFeedbackBusy)
                }

                if let guidanceFeedbackMessage {
                    Text(guidanceFeedbackMessage)
                        .font(.footnote)
                        .foregroundStyle(TodayFlowTheme.sand)
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceSoft(cornerRadius: 18)
        }
    }

    private func guidanceResonanceChip(title: String, value: String) -> some View {
        let selected = guidanceResonanceChoice == value
        return Button {
            guidanceResonanceChoice = value
        } label: {
            Text(title)
                .font(.caption.weight(.semibold))
                .padding(.horizontal, 10)
                .padding(.vertical, 8)
                .frame(maxWidth: .infinity)
                .background(selected ? TodayFlowTheme.sunset.opacity(0.28) : Color.white.opacity(0.78))
                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        }
        .buttonStyle(.plain)
        .disabled(guidanceResonanceSaved || guidanceFeedbackBusy)
    }

    @ViewBuilder
    private func quickFeedbackSection(_ result: QuestionAnswerResult) -> some View {
        if result.generationLogID != nil {
            VStack(alignment: .leading, spacing: 10) {
                Text(GuidanceViewChrome.quickFeedbackTitle)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                HStack(spacing: 10) {
                    Button(quickLegacyFeedback == "answer_helpful" ? GuidanceViewChrome.helpfulDone : GuidanceViewChrome.helpful) {
                        Task { await submitQuickLegacyFeedback(result: result, signal: "answer_helpful") }
                    }
                    .buttonStyle(.bordered)
                    .disabled(quickLegacyFeedback != nil || quickFeedbackBusy)

                    Button(quickLegacyFeedback == "still_unclear" ? GuidanceViewChrome.unclearDone : GuidanceViewChrome.unclear) {
                        Task { await submitQuickLegacyFeedback(result: result, signal: "still_unclear") }
                    }
                    .buttonStyle(.bordered)
                    .disabled(quickLegacyFeedback != nil || quickFeedbackBusy)
                }
                if quickFeedbackBusy {
                    ProgressView()
                        .scaleEffect(0.85)
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceSoft(cornerRadius: 18)
        }
    }

    private func submitGuidanceResonanceFeedback(logId: Int, result: GuidanceReadingResult) async {
        guard let choice = guidanceResonanceChoice else {
            await MainActor.run { guidanceFeedbackMessage = GuidanceViewChrome.pickResonance }
            return
        }
        await MainActor.run {
            guidanceFeedbackBusy = true
            guidanceFeedbackMessage = nil
        }
        let trimmed = guidanceFeedbackComment.trimmingCharacters(in: .whitespacesAndNewlines)
        let meta = LearningFeedbackMetadataPayload(
            source_surface: "guidance_v2",
            resonance: choice,
            spread_id: result.spreadId,
            lane: result.lane,
            comment: trimmed.isEmpty ? nil : trimmed,
            match_chips: nil,
            question: nil,
            preferred_lane: nil
        )
        do {
            try await store.submitLearningFeedback(generationLogId: logId, signal: "guidance_resonance", metadata: meta)
            await MainActor.run {
                guidanceResonanceSaved = true
                guidanceFeedbackBusy = false
                guidanceFeedbackMessage = GuidanceViewChrome.thanksFeedback
            }
        } catch {
            await MainActor.run {
                guidanceFeedbackBusy = false
                guidanceFeedbackMessage = error.localizedDescription
            }
        }
    }

    private func submitGuidanceLegacyFeedback(logId: Int, result: GuidanceReadingResult, signal: String) async {
        await MainActor.run { guidanceFeedbackBusy = true }
        let meta = LearningFeedbackMetadataPayload(
            source_surface: "guidance_v2",
            resonance: nil,
            spread_id: result.spreadId,
            lane: result.lane,
            comment: nil,
            match_chips: nil,
            question: result.question,
            preferred_lane: nil
        )
        do {
            try await store.submitLearningFeedback(generationLogId: logId, signal: signal, metadata: meta)
            await MainActor.run {
                guidanceLegacyFeedback = signal
                guidanceFeedbackBusy = false
                guidanceFeedbackMessage =
                    signal == "answer_helpful" ? GuidanceViewChrome.signalSaved : GuidanceViewChrome.notedNeedClarity
            }
        } catch {
            await MainActor.run {
                guidanceFeedbackBusy = false
                guidanceFeedbackMessage = error.localizedDescription
            }
        }
    }

    private func submitQuickLegacyFeedback(result: QuestionAnswerResult, signal: String) async {
        guard let logId = result.generationLogID else { return }
        await MainActor.run { quickFeedbackBusy = true }
        let meta = LearningFeedbackMetadataPayload(
            source_surface: "guidance_quick",
            resonance: nil,
            spread_id: nil,
            lane: result.lane,
            comment: nil,
            match_chips: nil,
            question: result.question,
            preferred_lane: preferredLaneRaw()
        )
        do {
            try await store.submitLearningFeedback(generationLogId: logId, signal: signal, metadata: meta)
            await MainActor.run {
                quickLegacyFeedback = signal
                quickFeedbackBusy = false
            }
        } catch {
            await MainActor.run { quickFeedbackBusy = false }
        }
    }

    @ViewBuilder
    private func chipGroup(title: String, choices: [(id: String, label: String)], selection: Binding<String?>, onSelect: (() -> Void)? = nil) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption.weight(.semibold))
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(choices, id: \.id) { item in
                        Button {
                            if selection.wrappedValue == item.id {
                                selection.wrappedValue = nil
                            } else {
                                selection.wrappedValue = item.id
                                onSelect?()
                            }
                        } label: {
                            Text(item.label)
                                .font(.caption.weight(.medium))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(selection.wrappedValue == item.id ? TodayFlowTheme.sunset.opacity(0.25) : Color.white.opacity(0.75))
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }

    private func guidanceResultTarotCardRow(card: GuidanceTarotCardPreview) -> some View {
        let revLabel = GuidanceViewChrome.orientationLabel(card.orientation)
        let kws = (card.keywords ?? []).filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
        return HStack(alignment: .top, spacing: 14) {
            guidanceTarotThumb(deckIndex: card.cardId, orientation: card.orientation, showFace: true)
            VStack(alignment: .leading, spacing: 6) {
                Text(card.position)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                if let p = card.positionPrompt?.trimmingCharacters(in: .whitespacesAndNewlines), !p.isEmpty {
                    Text(p)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text("\(card.name) · \(revLabel)")
                    .font(.subheadline.weight(.semibold))
                if !kws.isEmpty {
                    Text(kws.prefix(8).joined(separator: " · "))
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.sand.opacity(0.95))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text(card.meaning)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 14)
    }

    private func guidanceTarotCornerRadius(width: CGFloat) -> CGFloat {
        min(16, max(8, width * 0.09))
    }

    private func guidanceTarotImagePlaceholder(corner: CGFloat) -> some View {
        RoundedRectangle(cornerRadius: corner, style: .continuous)
            .fill(
                LinearGradient(
                    colors: [TodayFlowTheme.twilight.opacity(0.85), TodayFlowTheme.ember.opacity(0.65)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .overlay {
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .stroke(Color.white.opacity(0.28), lineWidth: 1)
            }
    }

    @ViewBuilder
    private func guidanceTarotDeckImage(url: URL?, corner: CGFloat, rotateFaceWhenReversed: Bool) -> some View {
        Group {
            if let url {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        ZStack {
                            Color(red: 0.98, green: 0.96, blue: 0.93)
                            image
                                .resizable()
                                .scaledToFit()
                        }
                    case .failure:
                        guidanceTarotImagePlaceholder(corner: corner)
                    case .empty:
                        guidanceTarotImagePlaceholder(corner: corner)
                            .overlay { ProgressView().tint(.white) }
                    @unknown default:
                        guidanceTarotImagePlaceholder(corner: corner)
                    }
                }
                .clipShape(RoundedRectangle(cornerRadius: corner, style: .continuous))
            } else {
                guidanceTarotImagePlaceholder(corner: corner)
            }
        }
        .rotationEffect(.degrees(rotateFaceWhenReversed ? 180 : 0))
    }

    /// Рубашка или лицо колоды с `WEB_BASE_URL` (как `TodayTarotDeckImageURLs` на остальных экранах).
    private func guidanceTarotThumb(deckIndex: Int?, orientation: String, showFace: Bool) -> some View {
        let w: CGFloat = 104
        let corner = guidanceTarotCornerRadius(width: w)
        let reversed = orientation.lowercased() == "reversed"
        let backURL = TodayTarotDeckImageURLs.cardBackURL()
        let faceURL = deckIndex.flatMap { TodayTarotDeckImageURLs.deckFaceURL(cardId: $0) }
        let url = showFace ? faceURL : backURL
        let spinReversed = showFace && reversed && faceURL != nil
        return guidanceTarotDeckImage(url: url, corner: corner, rotateFaceWhenReversed: spinReversed)
            .frame(width: w, height: TodayTarotDeckImageURLs.cardDisplayHeight(width: w))
            .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)
    }
}

// MARK: - History sheet

private struct GuidanceHistorySheet: View {
    let store: TodayFlowStore
    var onRouteSelected: ((String) -> Void)?

    @Environment(\.dismiss) private var dismiss

    @State private var bundle: GuidanceHistoryBundle?
    @State private var loading = true
    @State private var errorText: String?
    @State private var filter: GuidanceHistoryFilter = .all

    private enum GuidanceHistoryFilter: CaseIterable, Identifiable {
        case all
        case guidance
        case question
        case decision
        case tarot

        var id: String { String(describing: self) }

        var label: String {
            switch self {
            case .all: return GuidanceViewChrome.filterAll
            case .guidance: return GuidanceViewChrome.filterGuidance
            case .question: return GuidanceViewChrome.filterQuestions
            case .decision: return GuidanceViewChrome.filterDecisions
            case .tarot: return GuidanceViewChrome.filterTarot
            }
        }
    }

    private enum MergedRow: Identifiable {
        case question(QuestionsHistoryItemDTO)
        case daily(TarotDailyDrawDTO)
        case spread(TarotSpreadRecordDTO)

        var id: String {
            switch self {
            case let .question(q): return "q-\(q.generationLogId)"
            case let .daily(d): return "d-\(d.date)-\(d.card.id)"
            case let .spread(s): return s.id
            }
        }

        var sortKey: String {
            switch self {
            case let .question(q): return q.createdAt
            case let .daily(d): return "\(d.date)T12:00:00Z"
            case let .spread(s): return s.createdAt ?? s.drawDate
            }
        }

        func matches(_ f: GuidanceHistoryFilter) -> Bool {
            switch f {
            case .all: return true
            case .guidance:
                if case let .question(q) = self { return q.mode == "guidance" || q.mode == "guidance_clarify" }
                return false
            case .question:
                if case let .question(q) = self { return q.mode == "question" }
                return false
            case .decision:
                if case let .question(q) = self { return q.mode == "decision" }
                return false
            case .tarot:
                switch self {
                case .question: return false
                case .daily, .spread: return true
                }
            }
        }

        static func merged(from bundle: GuidanceHistoryBundle) -> [MergedRow] {
            var rows: [MergedRow] = []
            rows.append(contentsOf: bundle.questions.map { .question($0) })
            rows.append(contentsOf: bundle.tarotDaily.map { .daily($0) })
            rows.append(contentsOf: bundle.spreads.map { .spread($0) })
            return rows.sorted { $0.sortKey > $1.sortKey }
        }
    }

    private var filteredRows: [MergedRow] {
        guard let bundle else { return [] }
        return MergedRow.merged(from: bundle).filter { $0.matches(filter) }
    }

    var body: some View {
        NavigationStack {
            Group {
                if loading {
                    ProgressView(GuidanceViewChrome.loading)
                } else if let errorText {
                    Text(errorText)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(TodayFlowTheme.roseClay)
                        .padding()
                } else {
                    historyContent
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(TodayBackground())
            .navigationTitle(GuidanceViewChrome.historyTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(GuidanceViewChrome.close) { dismiss() }
                }
            }
            .task {
                await load()
            }
        }
    }

    private var historyContent: some View {
        VStack(spacing: 0) {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(GuidanceHistoryFilter.allCases) { item in
                        Button {
                            filter = item
                        } label: {
                            Text(item.label)
                                .font(.caption.weight(.semibold))
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .background(filter == item ? TodayFlowTheme.sunset.opacity(0.28) : Color.white.opacity(0.78))
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
            }

            List {
                if filteredRows.isEmpty {
                    Text(GuidanceViewChrome.emptyHistory)
                        .foregroundStyle(.secondary)
                        .listRowSeparator(.hidden)
                } else {
                    ForEach(filteredRows) { row in
                        rowView(row)
                            .listRowBackground(Color.white.opacity(0.55))
                    }
                }
            }
            .listStyle(.plain)
        }
    }

    @ViewBuilder
    private func rowView(_ row: MergedRow) -> some View {
        switch row {
        case let .question(q):
            questionRow(q)
        case let .daily(d):
            dailyRow(d)
        case let .spread(s):
            spreadRow(s)
        }
    }

    private func questionRow(_ q: QuestionsHistoryItemDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(GuidanceViewChrome.modeTitle(q.mode))
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.sand)
                Spacer()
                Text(formatHistoryDate(q.createdAt))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            if q.mode == "guidance" || q.mode == "guidance_clarify" {
                if let topic = GuidanceViewChrome.topicHistoryLabel(q.topic) {
                    Text(GuidanceViewChrome.topicLine(topic))
                        .font(.caption)
                }
                if let sid = q.spreadId {
                    Text(GuidanceViewChrome.spreadColon(spreadTitle(sid)))
                        .font(.caption)
                }
                if let lead = q.leadCardName {
                    Text("\(lead) · \(GuidanceViewChrome.orientationLabel(q.leadCardOrientation))")
                        .font(.subheadline.weight(.semibold))
                }
            }
            Text(q.question)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
                .lineLimit(4)
            if let focus = q.focus, !focus.isEmpty {
                Text(focus)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
            }
            routeButton(for: q.mode)
        }
        .padding(.vertical, 6)
    }

    @ViewBuilder
    private func routeButton(for mode: String) -> some View {
        switch mode {
        case "guidance", "guidance_clarify":
            Button(GuidanceViewChrome.openGuidance) {
                onRouteSelected?("/guidance")
                dismiss()
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.sunset)
        case "decision":
            Button(GuidanceViewChrome.openDecisions) {
                onRouteSelected?("/questions/decision")
                dismiss()
            }
            .buttonStyle(.bordered)
        default:
            Button(GuidanceViewChrome.openQuestions) {
                onRouteSelected?("/questions")
                dismiss()
            }
            .buttonStyle(.bordered)
        }
    }

    private func dailyRow(_ d: TarotDailyDrawDTO) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(GuidanceViewChrome.dailyCard)
                    .font(.caption.weight(.bold))
                Spacer()
                Text(d.date)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            Text("\(d.card.name) · \(GuidanceViewChrome.orientationLabel(d.orientation))")
                .font(.subheadline.weight(.semibold))
            Button(GuidanceViewChrome.openTarot) {
                onRouteSelected?("/tarot")
                dismiss()
            }
            .buttonStyle(.bordered)
        }
        .padding(.vertical, 6)
    }

    private func spreadRow(_ s: TarotSpreadRecordDTO) -> some View {
        let summary = s.spread.cards.map { "\($0.card.name) (\(GuidanceViewChrome.orientationLabel($0.orientation)))" }.joined(separator: " · ")
        return VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(GuidanceViewChrome.spreadHeader)
                    .font(.caption.weight(.bold))
                Spacer()
                Text(formatHistoryDate(s.createdAt ?? s.drawDate))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            Text(s.spread.title ?? spreadTitle(s.spread.spreadId))
                .font(.subheadline.weight(.semibold))
            if !summary.isEmpty {
                Text(summary)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
            }
            Button(GuidanceViewChrome.openTarot) {
                onRouteSelected?("/tarot")
                dismiss()
            }
            .buttonStyle(.bordered)
        }
        .padding(.vertical, 6)
    }

    private func load() async {
        loading = true
        errorText = nil
        do {
            let b = try await store.loadGuidanceHistoryBundle()
            await MainActor.run {
                bundle = b
                loading = false
            }
        } catch {
            await MainActor.run {
                errorText = error.localizedDescription
                loading = false
            }
        }
    }

    private func spreadTitle(_ id: String) -> String {
        QuestionsView.makeGuidanceSpreads().first(where: { $0.id == id })?.title ?? id
    }

    private func formatHistoryDate(_ iso: String) -> String {
        let trimmed = iso.trimmingCharacters(in: .whitespacesAndNewlines)
        let f1 = ISO8601DateFormatter()
        f1.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let f2 = ISO8601DateFormatter()
        f2.formatOptions = [.withInternetDateTime]
        for formatter in [f1, f2] {
            if let date = formatter.date(from: trimmed) {
                let out = DateFormatter()
                out.locale = Locale(identifier: IOSAppLocale.prefersRussian ? "ru_RU" : "en_US")
                out.dateStyle = .medium
                out.timeStyle = .short
                return out.string(from: date)
            }
        }
        if trimmed.count >= 10 {
            return String(trimmed.prefix(10))
        }
        return trimmed
    }
}

// MARK: - Small UI pieces

private struct StageChip: View {
    let title: String
    let isActive: Bool

    var body: some View {
        Text(title)
            .font(.caption.weight(.semibold))
            .foregroundStyle(isActive ? TodayFlowTheme.ember : TodayFlowTheme.ink.opacity(0.55))
            .padding(.horizontal, 10)
            .padding(.vertical, 7)
            .background(isActive ? TodayFlowTheme.sunset.opacity(0.2) : Color.white.opacity(0.58))
            .overlay(
                Capsule()
                    .stroke(isActive ? TodayFlowTheme.sand.opacity(0.45) : TodayFlowTheme.sand.opacity(0.25), lineWidth: 1)
            )
            .clipShape(Capsule())
            .shadow(color: isActive ? TodayFlowTheme.sunset.opacity(0.14) : .clear, radius: 8, x: 0, y: 4)
    }
}

private struct LuxeOptionCardButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeOut(duration: 0.16), value: configuration.isPressed)
    }
}

private struct LuxePrimaryCTAButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.985 : 1)
            .opacity(configuration.isPressed ? 0.94 : 1)
            .animation(.easeOut(duration: 0.14), value: configuration.isPressed)
    }
}

private struct QuestionAnswerCard: View {
    let title: String
    let text: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title.uppercased())
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.84))
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 20)
        .shadow(color: Color.black.opacity(0.04), radius: 10, x: 0, y: 5)
    }
}

#Preview {
    QuestionsView(store: TodayFlowStore())
}
