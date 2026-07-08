import SwiftUI

/// Один сценарий дня: герой → раскрытие → карта → число → check-in → «Твой день» → три сферы → шаг → поддержка → база.
/// Паритет с `frontend/.../TodayRitualFlow.tsx`.
struct TodayRitualFlowView: View {
    let store: TodayFlowStore
    let cycle: TodayCycle
    var onSelectTab: (AppTab) -> Void
    /// Чипы «Собрать день» → таб Flow + намерение (привычка / цель / аскеза), паритет с веб `EntityCreateWizard`.
    var onNavigateCalendarQuickCreate: ((TrackerQuickCreateKind) -> Void)? = nil
    /// Старт 20-минутного фокуса (таймер на экране «Сегодня»).
    var onStartFocus20Minutes: (() -> Void)? = nil
    var guideNarrativeLoading: Bool
    var eveningNarrativeLoading: Bool

    @State private var showRitualBody = false
    @State private var showNumberBody = false
    @State private var selectedMood: String?
    @State private var moodNote: String?
    @State private var expandedArea: String?
    @State private var essentials: Set<String> = []
    @State private var didRestoreDayState = false
    @State private var selectedProtection: DayProtectionOption?
    @State private var isSavingProtection = false
    @State private var protectionFeedback: String?
    @State private var headTopic: String?
    @State private var honestStep: String?
    @State private var numberRhythm: String?
    @State private var expandedPercentArea: String?
    @State private var selectedActionOption = 0
    @State private var focusSessionHint = false
    @State private var focusSavedAck = false
    /// Интерактивная карта дня (паритет с веб `TodayRitualFlow.tsx`).
    @State private var tarotMainId: Int?
    @State private var tarotClarifierId: Int?
    @State private var tarotApplied = false
    @State private var tarotContinueAck = false
    @State private var tarotMeaningPresented = false
    @State private var showTarotExtraSteps = false
    @State private var showNumberExtraSteps = false
    @State private var tarotProximityChoice: ProximityChoiceId?
    @State private var numberProximityChoice: ProximityChoiceId?
    @State private var checkInSubmitted = false
    @State private var sphereDetailArea: RitualFourArea?
    @State private var sphereSheetPresented = false
    @State private var daySummaryWhyExpanded = false
    /// Паритет веб `TodayGuideSection` `<details>`: вторичная сводка по умолчанию свёрнута.
    @State private var guideAdditionalExpanded = false
    /// DE-9 + §5.2: `today_day_history_first_visible` не чаще одного раза на размещение за сессию экрана.
    @State private var dayHistoryFirstVisibleLogged: Set<String> = []

    private var dashboard: TodayDashboard { store.today }

    /// O6: низкий ресурс настроения — компактнее фокус и меньше вторичных CTA (паритет веб `TodayRitualFlow` / `TodayResultView`).
    private var lowEnergyRitualMood: Bool {
        TodayRitualCopy.isLowEnergyRitualMood(selectedMood)
    }

    /// Паритет с веб `ritualAvoidHeadingForUserGender` — заголовок блока «не дожимать» в сводке после ритуала.
    private var daySummaryAvoidTitle: String {
        RuUserDeclension.ritualAvoidHeading(RuUserDeclension.parse(store.coreProfile?.person.gender))
    }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s4) {
                    if ritualSpineComplete {
                        dayReadyBlock(proxy: proxy)
                        spheresTriadBlock
                        focusBlock
                        if !lowEnergyRitualMood {
                            supportBlock
                        }
                        if !hasWeeklyStructure {
                            buildDayBlock
                        }
                        essentialsBlock
                        eveningHookBlock
                    } else {
                        heroBlock(proxy: proxy)
                        if showRitualBody {
                            cardBlock(proxy: proxy)
                            numberBlock(proxy: proxy)
                            if showNumberBody {
                                checkInBlock(proxy: proxy)
                            }
                        }
                    }
                }
            }
        }
        .sheet(isPresented: $sphereSheetPresented) {
            if let area = sphereDetailArea {
                NavigationStack {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 16) {
                            Text(area.title)
                                .font(.title2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            TodayFlowSphereSliderTrack(value: area.score, tint: area.tint, accessibilityTitle: area.title)
                            Text(TodayRitualCopy.areaTodayEyebrow)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.sand)
                            Text(area.todayHeadline.isEmpty ? area.insight : area.todayHeadline)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            if !area.todayDetail.isEmpty {
                                Text(area.todayDetail)
                                    .font(.subheadline)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                            }
                            Divider().opacity(0.25)
                            Text(TodayRitualCopy.sphereSheetWhyTitle)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.sand)
                            Text(area.reason)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                            Text(TodayRitualCopy.areaNuance)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.sand)
                                .padding(.top, 4)
                            Text(area.watch)
                                .font(.subheadline)
                                .foregroundStyle(area.tint)
                            Text(TodayRitualCopy.sphereSheetWebParityNote)
                                .font(.caption2)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                                .padding(.top, 8)
                        }
                        .padding(20)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .navigationTitle(TodayRitualCopy.sphereSheetNavTitle)
                    .navigationBarTitleDisplayMode(.inline)
                    .toolbar {
                        ToolbarItem(placement: .topBarTrailing) {
                            Button(TodayRitualCopy.sheetCloseCta) {
                                sphereSheetPresented = false
                            }
                        }
                    }
                }
            }
        }
        .onAppear {
            restoreDayStateIfNeeded()
            #if DEBUG
            let issues = TodayRitualSpinePhaseResolver.consistencyIssues(ritualSpineSnapshot)
            if !issues.isEmpty {
                print("TodayRitualSpine consistency: \(issues.joined(separator: ", "))")
            }
            #endif
        }
        .onChange(of: cycle.date) { _, _ in
            didRestoreDayState = false
            selectedMood = nil
            moodNote = nil
            headTopic = nil
            honestStep = nil
            numberRhythm = nil
            expandedPercentArea = nil
            selectedActionOption = 0
            focusSessionHint = false
            focusSavedAck = false
            essentials = []
            tarotMainId = nil
            tarotClarifierId = nil
            tarotApplied = false
            tarotContinueAck = false
            showTarotExtraSteps = false
            showNumberExtraSteps = false
            checkInSubmitted = false
            expandedArea = nil
            dayHistoryFirstVisibleLogged = []
            restoreDayStateIfNeeded()
        }
        .onChange(of: store.todayGuideNarrative?.generationID) { _, _ in
            selectedActionOption = 0
        }
        .onChange(of: selectedMood) { _, new in
            if TodayRitualCopy.isLowEnergyRitualMood(new), selectedActionOption > 0 {
                selectedActionOption = 0
            }
        }
        .sheet(isPresented: $tarotMeaningPresented) {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(TodayRitualCopy.cardMeaningPopoverBody)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.85))
                            .ritualMultilineFill()
                    }
                    .padding()
                }
                .navigationTitle(TodayRitualCopy.cardMeaningPopoverTitle)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button(TodayRitualCopy.cardMeaningAckCta) { tarotMeaningPresented = false }
                    }
                }
            }
            .presentationDetents([.medium])
            .presentationDragIndicator(.visible)
        }
    }

    // MARK: - Block 1 Hero

    private func heroBlock(proxy: ScrollViewProxy) -> some View {
        Group {
            if !showRitualBody {
                RitualDesertEntryCard(
                    formattedDate: formattedRUToday,
                    dateISO: cycle.date,
                    energyScore: energyScore
                ) {
                    openDay(proxy: proxy)
                }
                .padding(.horizontal, 0)
            } else {
                VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s3) {
                    Text(formattedRUToday)
                        .font(.todayFlowEyebrow)
                        .foregroundStyle(TodayFlowTheme.sand)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .fixedSize(horizontal: false, vertical: true)
                    Text(TodayRitualCopy.ritualProgressHint)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .fixedSize(horizontal: false, vertical: true)
                    ritualProgressStrip
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(20)
                .frame(maxWidth: .infinity, alignment: .center)
                .todayFlowSurfaceEthereal(cornerRadius: 28)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .id("ritualHero")
    }

    private var ritualProgressStrip: some View {
        HStack(spacing: 0) {
            ritualProgressPill(done: tarotMainId != nil, label: TodayRitualCopy.ritualStepCardShort)
            ritualProgressChevron
            ritualProgressPill(done: showNumberBody, label: TodayRitualCopy.ritualStepNumberShort)
            ritualProgressChevron
            ritualProgressPill(done: selectedMood != nil, label: TodayRitualCopy.ritualStepMoodShort)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 4)
    }

    private func ritualProgressPill(done: Bool, label: String) -> some View {
        Text(label)
            .font(.caption.weight(.semibold))
            .foregroundStyle(done ? TodayFlowTheme.ink : TodayFlowTheme.ink.opacity(0.45))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(done ? TodayFlowTheme.sunset.opacity(0.22) : Color.white.opacity(0.45))
            .clipShape(Capsule())
            .overlay {
                Capsule().stroke(TodayFlowTheme.gold.opacity(done ? 0.42 : 0.22), lineWidth: 1)
            }
    }

    private var ritualProgressChevron: some View {
        Image(systemName: "chevron.right")
            .font(.caption2.weight(.bold))
            .foregroundStyle(TodayFlowTheme.ink.opacity(0.35))
            .padding(.horizontal, 4)
    }

    /// Вторая строка героя: сводка дня + подстрочник (как основной текст под заголовком на вебе).
    private var heroSummaryBody: String {
        let g = dashboard.guidanceSummary.trimmingCharacters(in: .whitespacesAndNewlines)
        let sub = subtitleLine.trimmingCharacters(in: .whitespacesAndNewlines)
        if g.isEmpty { return sub }
        if g == sub { return sub }
        return "\(g)\n\n\(sub)"
    }

    /// Как на вебе: `core_message` строка или объект (Day Engine), иначе подстрочник дня.
    private var dayReadyNarrativeBody: String {
        if let story = store.todayContract?.dayStory?.story?.trimmingCharacters(in: .whitespacesAndNewlines), !story.isEmpty {
            return story
        }
        let core = TodayGuideActionable.coreMessageDisplayString(from: store.todayGuideNarrative?.payload)
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if !core.isEmpty {
            return core
        }
        let sub = subtitleLine.trimmingCharacters(in: .whitespacesAndNewlines)
        if !sub.isEmpty { return sub }
        return summaryTitle.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Компактная строка ритма под карточкой «Коротко о дне» — без круга, текст не наезжает на «сферу».
    private var heroRhythmStrip: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(TodayRitualCopy.heroRhythmCaption)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text("\(RitualFourAreaBuilder.rhythmTier(for: energyScore)) · \(dayTypeHeadline)")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
            Text(TodayRitualCopy.heroScoreFootnote(score: energyScore))
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 4)
    }

    private var energyRingsRow: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 10) {
                ForEach(heroEnergyMetrics) { metric in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack(alignment: .top, spacing: 8) {
                            Text(metric.title)
                                .font(.caption.weight(.semibold))
                                .multilineTextAlignment(.leading)
                                .fixedSize(horizontal: false, vertical: true)
                                .frame(maxWidth: .infinity, alignment: .leading)
                            Text("\(metric.value)")
                                .font(.caption.weight(.semibold))
                        }
                        TodayFlowSphereSliderTrack(value: metric.value, tint: metric.tint, accessibilityTitle: metric.title)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            }
            .foregroundStyle(TodayFlowTheme.ink.opacity(0.8))
            Text(
                IOSAppLocale.prefersRussian
                    ? TodayRitualCopy.ritualFlowHeroMetricsDisclaimerRu
                    : TodayRitualCopy.ritualFlowHeroMetricsDisclaimerEn
            )
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                .ritualMultilineFill()
        }
    }

    // MARK: - Card

    private var anchorTarotDeckId: Int {
        TodayTarotTodayRuCatalog.deckImageIdForDay(apiCardName: cycle.morning?.tarotCard?.name, dateISO: cycle.date)
    }

    private var anchorTarotTagLabels: [String] {
        guard let lead = TodayTarotTodayRuCatalog.card(anchorTarotDeckId)?.leadRu else { return [] }
        return TodayRitualCopy.anchorTarotTags(from: lead)
    }

    /// Карта + число + настроение + подтверждение чек-ина — дальше только сводка «Твой день» (как на макете).
    /// Паритет с веб `isRitualSpineComplete`: нужен и `tarotContinueAck`.
    private var ritualSpineComplete: Bool {
        tarotMainId != nil && drawnTarotMain != nil && tarotContinueAck && showNumberBody && selectedMood != nil && checkInSubmitted
    }

    private var ritualSpineSnapshot: TodayRitualSpineSnapshot {
        TodayRitualSpineSnapshot(
            dayOpened: showRitualBody,
            tarotContinueAck: tarotContinueAck,
            numberRevealed: showNumberBody,
            tarotMainId: tarotMainId,
            tarotMainResolved: drawnTarotMain != nil,
            selectedMoodId: selectedMood,
            checkInSubmitted: checkInSubmitted,
            guideNarrativeLoading: guideNarrativeLoading
        )
    }

    private func mergeSpineSnapshot(_ snap: TodayRitualSpineSnapshot) {
        showRitualBody = snap.dayOpened
        tarotContinueAck = snap.tarotContinueAck
        showNumberBody = snap.numberRevealed
        selectedMood = snap.selectedMoodId
        checkInSubmitted = snap.checkInSubmitted
    }

    private func applySpineEffects(
        _ effects: TodayRitualSpineEffects,
        proxy: ScrollViewProxy?,
        numerologyDigitForAnalytics: String? = nil
    ) {
        if effects.saveOpenedDay {
            TodayFlowPersistence.shared.saveOpenedDay(for: store.authSession?.email, dateISO: cycle.date)
        }
        if effects.saveNumberRevealed {
            TodayFlowPersistence.shared.saveNumberRevealed(for: store.authSession?.email, dateISO: cycle.date)
        }
        if effects.persistRitualExtras {
            persistRitualExtras()
        }
        switch effects.analyticsHint {
        case .none:
            break
        case .numberRevealed:
            guard let digit = numerologyDigitForAnalytics else { break }
            let gid = store.todayGuideNarrative?.generationID
            Task {
                await store.trackTodaySurfaceEvent(
                    eventType: "number_selected",
                    eventSource: "today",
                    qualityScore: 0.85,
                    generationLogId: gid,
                    payload: [
                        "revealed": .bool(true),
                        "numerology_value": .string(digit),
                    ]
                )
            }
        case .moodSelected(let id):
            let gid = store.todayGuideNarrative?.generationID
            Task {
                await store.trackTodaySurfaceEvent(
                    eventType: "mood_selected",
                    eventSource: "today",
                    qualityScore: 0.8,
                    generationLogId: gid,
                    payload: ["mood_id": .string(id), "source": .string("today_ritual")]
                )
            }
        }
        guard let proxy, let anchor = effects.scrollToAnchorId else { return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) {
            withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                proxy.scrollTo(anchor, anchor: .top)
            }
        }
    }

    private var drawnTarotMain: TodayTarotCardRuRecord? {
        tarotMainId.flatMap { TodayTarotTodayRuCatalog.card($0) }
    }

    private var drawnTarotClarifier: TodayTarotCardRuRecord? {
        tarotClarifierId.flatMap { TodayTarotTodayRuCatalog.card($0) }
    }

    @ViewBuilder
    private func ritualTarotTagsRow(tags: [String]) -> some View {
        if tags.isEmpty {
            EmptyView()
        } else {
            HStack(spacing: 6) {
                ForEach(Array(tags.enumerated()), id: \.offset) { _, tag in
                    Text(tag)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color(red: 1, green: 0.93, blue: 0.89).opacity(0.85))
                        .clipShape(Capsule())
                        .overlay {
                            Capsule().stroke(TodayFlowTheme.sunset.opacity(0.28), lineWidth: 1)
                        }
                }
            }
            .frame(maxWidth: .infinity)
            .multilineTextAlignment(.center)
        }
    }

    private func cardBlock(proxy: ScrollViewProxy) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayRitualCopy.cardEyebrow)
                .font(.todayFlowRitualHeroTitle)
                .foregroundStyle(TodayFlowTheme.ink)
                .frame(maxWidth: .infinity, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)
            Text(TodayRitualCopy.tarotCardSubhead)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .frame(maxWidth: .infinity, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)

            if !tarotContinueAck {
                VStack(alignment: .leading, spacing: 14) {
                    RitualTarotPickMiniFlow(
                        anchorCardId: anchorTarotDeckId,
                        committedMainId: tarotMainId,
                        cardTitleRu: drawnTarotMain?.nameRu
                            ?? TodayTarotTodayRuCatalog.card(anchorTarotDeckId)?.nameRu
                            ?? TodayRitualCopy.cardEyebrow,
                        tagLabels: drawnTarotMain.map { TodayRitualCopy.anchorTarotTags(from: $0.leadRu) } ?? anchorTarotTagLabels,
                        onCommitMain: { commitMainTarotFromPick() },
                        onContinue: {
                            guard let (after, effects) = TodayRitualSpineReducer.apply(
                                event: .continuedPastTarot,
                                to: ritualSpineSnapshot
                            ) else { return }
                            mergeSpineSnapshot(after)
                            applySpineEffects(effects, proxy: proxy)
                        }
                    )
                    .frame(maxWidth: .infinity)
                    if tarotMainId == nil {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(TodayRitualCopy.tarotClosedLead)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                                .fixedSize(horizontal: false, vertical: true)
                            Text(TodayRitualCopy.tarotDrawIntro)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(16)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            LinearGradient(
                                colors: [Color.white.opacity(0.97), TodayFlowTheme.paper.opacity(0.85), TodayFlowTheme.mist.opacity(0.5)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .overlay {
                            RoundedRectangle(cornerRadius: 20, style: .continuous)
                                .stroke(TodayFlowTheme.gold.opacity(0.35), lineWidth: 1)
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                    }
                }
            } else if !showNumberBody {
                Text(TodayRitualCopy.tarotBridgeToNumber)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .fixedSize(horizontal: false, vertical: true)
            } else if let card = drawnTarotMain, let mainId = tarotMainId, let faceURL = TodayTarotDeckImageURLs.deckFaceURL(cardId: mainId) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(TodayRitualCopy.tarotRevealScreenTitle)
                        .font(.todayFlowRitualHeroTitle)
                        .foregroundStyle(TodayFlowTheme.ink)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .multilineTextAlignment(.center)
                    AsyncImage(url: faceURL) { phase in
                        switch phase {
                        case .success(let image):
                            ZStack {
                                Color(red: 0.98, green: 0.96, blue: 0.93)
                                image
                                    .resizable()
                                    .scaledToFit()
                            }
                            .frame(maxWidth: .infinity)
                            .aspectRatio(
                                TodayTarotDeckImageURLs.cardPixelWidth / TodayTarotDeckImageURLs.cardPixelHeight,
                                contentMode: .fit
                            )
                            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .overlay {
                                RoundedRectangle(cornerRadius: 16, style: .continuous)
                                    .stroke(TodayFlowTheme.gold.opacity(0.28), lineWidth: 1)
                            }
                            .shadow(color: Color(red: 1, green: 0.82, blue: 0.65).opacity(0.55), radius: 22, y: 4)
                            .shadow(color: Color.black.opacity(0.08), radius: 14, y: 6)
                        case .failure, .empty:
                            Color.clear.frame(height: 0)
                        @unknown default:
                            Color.clear.frame(height: 0)
                        }
                    }
                    Text(card.nameRu)
                        .font(.system(size: 22, weight: .semibold, design: .serif))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity, alignment: .center)
                        .fixedSize(horizontal: false, vertical: true)
                    ritualTarotTagsRow(tags: TodayRitualCopy.anchorTarotTags(from: card.leadRu))
                    if showTarotExtraSteps {
                        Text(card.leadRu)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                            .fixedSize(horizontal: false, vertical: true)
                        Text(card.bodyRu)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                            .fixedSize(horizontal: false, vertical: true)
                    } else {
                        Text(card.leadRu)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    if showTarotExtraSteps, let clar = drawnTarotClarifier {
                        VStack(alignment: .leading, spacing: 6) {
                            Text("\(TodayRitualCopy.tarotClarifierEyebrow): \(clar.nameRu)")
                                .font(.caption.weight(.bold))
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .multilineTextAlignment(.leading)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .fixedSize(horizontal: false, vertical: true)
                            Text("\(clar.leadRu) \(clar.bodyRu)")
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.55))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        .overlay {
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                        }
                    }

                    if showTarotExtraSteps {
                        Text("\(TodayRitualCopy.tarotQuestionEyebrow): \(card.questionRu)")
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .fixedSize(horizontal: false, vertical: true)
                        Text(TodayRitualCopy.cardRevealedHint)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                            .fixedSize(horizontal: false, vertical: true)

                        VStack(alignment: .leading, spacing: 8) {
                            Button { tarotMeaningPresented = true } label: {
                                Text(TodayRitualCopy.cardWhatMeansButton)
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.bordered)
                            .tint(TodayFlowTheme.sunset)
                            Button {
                                guard let mainId = tarotMainId else { return }
                                tarotApplied = true
                                persistRitualExtras()
                                Task {
                                    var payload: [String: JSONValue] = [
                                        "applied_to_today": .bool(true),
                                        "main_card_index": .number(Double(mainId)),
                                    ]
                                    if let c = tarotClarifierId {
                                        payload["clarifier_card_index"] = .number(Double(c))
                                    }
                                    let gid = store.todayGuideNarrative?.generationID
                                    await store.trackTodaySurfaceEvent(
                                        eventType: "tarot_selected",
                                        eventSource: "today",
                                        qualityScore: 0.88,
                                        generationLogId: gid,
                                        payload: payload
                                    )
                                }
                            } label: {
                                Text(TodayRitualCopy.tarotApplyToTodayCta)
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(TodayFlowTheme.sunset)
                            .disabled(tarotApplied)
                            Button {
                                tarotMeaningPresented = false
                                let id = TodayTarotDayDraw.randomDeckIndex(excluding: Set([tarotMainId].compactMap { $0 }))
                                tarotClarifierId = id
                                persistRitualExtras()
                                Task {
                                    let gid = store.todayGuideNarrative?.generationID
                                    await store.trackTodaySurfaceEvent(
                                        eventType: "tarot_selected",
                                        eventSource: "today",
                                        qualityScore: 0.85,
                                        generationLogId: gid,
                                        payload: [
                                            "role": .string("clarifier"),
                                            "card_index": .number(Double(id)),
                                        ]
                                    )
                                }
                            } label: {
                                Text(TodayRitualCopy.tarotDrawAnotherCta)
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.bordered)
                            .tint(TodayFlowTheme.sunset)
                            .disabled(tarotClarifierId != nil)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)

                        if tarotClarifierId != nil {
                            Text(TodayRitualCopy.tarotDrawAnotherHint)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                                .ritualMultilineFill()
                        }
                        if tarotApplied {
                            Text(TodayRitualCopy.tarotAppliedAck)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .ritualMultilineFill()
                            PimInterpretationConfirmView(
                                target: .tarotImpact,
                                selectedChoiceId: tarotProximityChoice,
                                onSelect: { choiceId, resonance in
                                    tarotProximityChoice = choiceId
                                    persistRitualExtras()
                                    Task {
                                        await store.trackMeaningEventWithIdempotency(
                                            eventType: "sphere_feedback",
                                            eventSource: "today",
                                            idempotencyKey: "interpretation_confirm:tarot_impact:\(choiceId.rawValue):\(cycle.date)",
                                            qualityScore: 0.9,
                                            payload: [
                                                "surface": .string("today_ritual_flow"),
                                                "target": .string(InterpretationConfirmTarget.tarotImpact.rawValue),
                                                "echo": .string(resonance.rawValue),
                                                "proximity_choice": .string(choiceId.rawValue),
                                                "interpretation_confirm": .bool(true),
                                                "headline_preview": .string(drawnTarotMain?.focusRu ?? ""),
                                            ]
                                        )
                                    }
                                }
                            )
                            .padding(.top, 4)

                            if let mainId = tarotMainId {
                                Button {
                                    let question = "Как карта дня помогает увидеть мой вопрос глубже?"
                                    store.requestTarotDeepen(
                                        anchorCardId: mainId,
                                        anchorOrientation: "upright",
                                        question: question,
                                        source: "today"
                                    )
                                    Task {
                                        await store.trackTarotFlowEvent(
                                            eventType: "tarot_deepen_started",
                                            idempotencyKey: "tarot-deepen:today:\(mainId):\(cycle.date)",
                                            payload: [
                                                "card_id": .number(Double(mainId)),
                                                "orientation": .string("upright"),
                                                "source": .string("today"),
                                                "spread_id": .string("three_cards"),
                                            ]
                                        )
                                    }
                                    onSelectTab(.questions)
                                } label: {
                                    Text("Исследовать глубже →")
                                        .font(.subheadline.weight(.semibold))
                                        .frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.bordered)
                                .padding(.top, 8)
                            }
                        }

                        Divider().opacity(0.28)
                        Text(TodayRitualCopy.cardHonestStepQuestion)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                            .ritualMultilineFill()
                        LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], spacing: 8) {
                            ForEach(TodayRitualCopy.cardHonestStepChips, id: \.0) { id, label in
                                Button {
                                    honestStep = id
                                    persistRitualExtras()
                                    Task {
                                        await store.trackTodaySurfaceEvent(
                                            eventType: "sphere_feedback",
                                            eventSource: "today",
                                            qualityScore: 0.85,
                                            payload: ["tarot_honest_step": .string(id)]
                                        )
                                    }
                                } label: {
                                    Text(label)
                                        .font(.caption.weight(.medium))
                                        .multilineTextAlignment(.center)
                                        .fixedSize(horizontal: false, vertical: true)
                                        .padding(.horizontal, 10)
                                        .padding(.vertical, 8)
                                        .frame(maxWidth: .infinity)
                                        .background(honestStep == id ? TodayFlowTheme.sunset.opacity(0.22) : Color.white.opacity(0.55))
                                        .clipShape(Capsule())
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        Button {
                            focusSavedAck = true
                            persistRitualExtras()
                            Task {
                                await store.trackTodaySurfaceEvent(
                                    eventType: "focus_started",
                                    eventSource: "today",
                                    qualityScore: 0.75,
                                    payload: [
                                        "from_tarot_depth": .bool(true),
                                        "honest_step": .string(honestStep ?? "unset"),
                                    ]
                                )
                            }
                        } label: {
                            Text(TodayRitualCopy.cardSaveFocus)
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(TodayFlowTheme.sunset)
                        if focusSavedAck {
                            Text(TodayRitualCopy.cardSaveFocusDone)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    } else {
                        VStack(alignment: .leading, spacing: 10) {
                            Button {
                                withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                                    proxy.scrollTo("ritualNumber", anchor: .top)
                                }
                            } label: {
                                Text(TodayRitualCopy.ritualContinueCta)
                                    .font(.headline)
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(RitualRoseGoldProminentButtonStyle())
                            Button {
                                withAnimation(.easeInOut(duration: 0.25)) {
                                    showTarotExtraSteps = true
                                }
                            } label: {
                                Text(TodayRitualCopy.tarotExtraDetailToggle)
                                    .font(.subheadline.weight(.semibold))
                                    .frame(maxWidth: .infinity)
                            }
                            .buttonStyle(.bordered)
                            .tint(TodayFlowTheme.sunset)
                        }
                    }
                }
                .padding(16)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(
                    LinearGradient(
                        colors: [Color.white.opacity(0.98), TodayFlowTheme.paper.opacity(0.9), TodayFlowTheme.mist.opacity(0.55)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay {
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .stroke(TodayFlowTheme.gold.opacity(0.28), lineWidth: 1)
                }
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))

                if showTarotExtraSteps {
                    Button {
                        withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                            proxy.scrollTo("ritualNumber", anchor: .top)
                        }
                    } label: {
                        Text(TodayRitualCopy.ritualContinueCta)
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(RitualRoseGoldProminentButtonStyle())
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(20)
        .todayFlowSurfaceEthereal(cornerRadius: 28)
        .id("ritualDeck")
    }

    private func numberBlock(proxy: ScrollViewProxy) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(TodayRitualCopy.numberDayEyebrow)
                .font(.todayFlowRitualHeroTitle)
                .foregroundStyle(TodayFlowTheme.ink)
                .ritualMultilineFill()
            if showNumberBody {
                VStack(spacing: 14) {
                    ZStack {
                        Circle()
                            .fill(
                                RadialGradient(
                                    colors: [
                                        Color(red: 1, green: 0.88, blue: 0.72).opacity(0.55),
                                        Color(red: 1, green: 0.94, blue: 0.88).opacity(0.22),
                                        Color.clear,
                                    ],
                                    center: .center,
                                    startRadius: 8,
                                    endRadius: 110
                                )
                            )
                            .frame(width: 200, height: 200)
                            .blur(radius: 10)
                        Text(numerologyDigit)
                            .font(.system(size: 56, weight: .bold, design: .serif))
                            .foregroundStyle(TodayFlowTheme.ink)
                            .shadow(color: Color(red: 1, green: 0.82, blue: 0.62).opacity(0.65), radius: 18, y: 0)
                    }
                    .frame(maxWidth: .infinity)
                    Text(TodayRitualCopy.numberRevealScreenTitle)
                        .font(.todayFlowRitualHeroTitle)
                        .foregroundStyle(TodayFlowTheme.ink)
                        .frame(maxWidth: .infinity)
                        .multilineTextAlignment(.center)
                    Text(numerologyMeaning)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: .infinity)
                    PimInterpretationConfirmView(
                        target: .numberImpact,
                        selectedChoiceId: numberProximityChoice,
                        onSelect: { choiceId, resonance in
                            numberProximityChoice = choiceId
                            persistRitualExtras()
                            Task {
                                await store.trackMeaningEventWithIdempotency(
                                    eventType: "sphere_feedback",
                                    eventSource: "today",
                                    idempotencyKey: "interpretation_confirm:number_impact:\(choiceId.rawValue):\(cycle.date)",
                                    qualityScore: 0.9,
                                    payload: [
                                        "surface": .string("today_ritual_flow"),
                                        "target": .string(InterpretationConfirmTarget.numberImpact.rawValue),
                                        "echo": .string(resonance.rawValue),
                                        "proximity_choice": .string(choiceId.rawValue),
                                        "interpretation_confirm": .bool(true),
                                        "headline_preview": .string(String(numerologyDigit)),
                                    ]
                                )
                            }
                        }
                    )
                    .padding(.top, 2)
                    HStack(spacing: 6) {
                        ForEach(TodayRitualCopy.numberDayTagTriad(numerologyValue: numerologyDigit), id: \.self) { tag in
                            Text(tag)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(Color(red: 1, green: 0.93, blue: 0.89).opacity(0.85))
                                .clipShape(Capsule())
                                .overlay {
                                    Capsule().stroke(TodayFlowTheme.sunset.opacity(0.28), lineWidth: 1)
                                }
                        }
                    }
                    .frame(maxWidth: .infinity)
                    VStack(alignment: .leading, spacing: 8) {
                        premiumMetaLine(title: TodayRitualCopy.numerologyBestTimeLabel, value: lucky.time)
                        premiumMetaLine(title: TodayRitualCopy.numerologyColorLabel, value: lucky.color)
                        premiumMetaLine(title: TodayRitualCopy.numerologyStoneLabel, value: lucky.stone)
                    }
                    Button {
                        withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                            proxy.scrollTo("ritualCheckin", anchor: .top)
                        }
                    } label: {
                        Text(TodayRitualCopy.ritualContinueCta)
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(RitualRoseGoldProminentButtonStyle())
                    .padding(.top, 4)
                    if showNumberExtraSteps {
                        Text(bridgeLine)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .ritualMultilineFill()
                        VStack(alignment: .leading, spacing: 8) {
                            Divider().opacity(0.25)
                            Text(TodayRitualCopy.numberRhythmQuestion)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .ritualMultilineFill()
                            LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], spacing: 8) {
                                ForEach(TodayRitualCopy.numberRhythmChips, id: \.0) { id, label in
                                    Button {
                                        numberRhythm = id
                                        persistRitualExtras()
                                        Task {
                                            await store.trackTodaySurfaceEvent(
                                                eventType: "number_selected",
                                                eventSource: "today",
                                                qualityScore: 0.85,
                                                payload: ["rhythm_need": .string(id)]
                                            )
                                        }
                                    } label: {
                                        Text(label)
                                            .font(.caption.weight(.medium))
                                            .multilineTextAlignment(.center)
                                            .fixedSize(horizontal: false, vertical: true)
                                            .padding(.horizontal, 10)
                                            .padding(.vertical, 8)
                                            .frame(maxWidth: .infinity)
                                            .background(numberRhythm == id ? TodayFlowTheme.sunset.opacity(0.22) : Color.white.opacity(0.55))
                                            .clipShape(Capsule())
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                        .padding(.top, 6)
                    } else {
                        Button {
                            withAnimation(.easeInOut(duration: 0.25)) {
                                showNumberExtraSteps = true
                            }
                        } label: {
                            Text(TodayRitualCopy.numberExtraDetailToggle)
                                .font(.caption.weight(.semibold))
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .tint(TodayFlowTheme.sunset)
                        .padding(.top, 4)
                    }
                }
            } else {
                Text(TodayRitualCopy.numberDaySubPick)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    .ritualMultilineFill()
                RitualNumberFlowerPick(systemDigit: numerologyDigit) {
                    guard let (after, effects) = TodayRitualSpineReducer.apply(
                        event: .revealedNumber,
                        to: ritualSpineSnapshot
                    ) else { return }
                    withAnimation(.spring(response: 0.42, dampingFraction: 0.86)) {
                        mergeSpineSnapshot(after)
                        if effects.resetNumberExtraSteps {
                            showNumberExtraSteps = false
                        }
                    }
                    applySpineEffects(effects, proxy: proxy, numerologyDigitForAnalytics: numerologyDigit)
                }
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.ultraThinMaterial.opacity(0.9))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.45), lineWidth: 1)
        }
        .id("ritualNumber")
    }

    private func dayReadyBlock(proxy _: ScrollViewProxy) -> some View {
        let coreParas = TodayGuideActionable.coreMessageParagraphs(from: store.todayGuideNarrative?.payload)
        let dayEngineBrief = TodayGuideActionable.dayEngineBriefDisplay(from: store.todayGuideNarrative?.payload)
        let dayModelBrief = TodayGuideActionable.dayModelBriefDisplay(from: store.todayGuideNarrative?.payload)
        let thesisHeadline = guideNarrativeString("headline")
        let thesisSubline = guideNarrativeString("subline")
        let es = min(100, max(0, energyScore))
        let doText = displayDoText
        let dontText = daySummaryDontLine
        return VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 14) {
                Text(formattedRUToday)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .ritualMultilineFill()
                Text(TodayRitualCopy.ritualDayReadyTitle)
                    .font(.title2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .ritualMultilineFill()

                HStack(alignment: .center, spacing: 12) {
                    if let mainId = tarotMainId, let faceURL = TodayTarotDeckImageURLs.deckFaceURL(cardId: mainId) {
                        let thumbW: CGFloat = 52
                        let thumbH = TodayTarotDeckImageURLs.cardDisplayHeight(width: thumbW)
                        AsyncImage(url: faceURL) { phase in
                            switch phase {
                            case .success(let image):
                                ZStack {
                                    Color(red: 0.98, green: 0.96, blue: 0.93)
                                    image.resizable().scaledToFit()
                                }
                                .frame(width: thumbW, height: thumbH)
                                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                            case .failure, .empty:
                                RoundedRectangle(cornerRadius: 10, style: .continuous)
                                    .fill(Color.white.opacity(0.5))
                                    .frame(width: thumbW, height: thumbH)
                            @unknown default:
                                Color.clear.frame(width: thumbW, height: thumbH)
                            }
                        }
                    }
                    ZStack {
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [TodayFlowTheme.sunset.opacity(0.32), TodayFlowTheme.gold.opacity(0.18)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                        Text(numerologyDigit)
                            .font(.system(size: 20, weight: .bold, design: .rounded))
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    .frame(width: 44, height: 44)
                    .overlay { Circle().stroke(TodayFlowTheme.gold.opacity(0.32), lineWidth: 1) }
                    VStack(alignment: .leading, spacing: 6) {
                        Text(TodayRitualCopy.daySummaryMarkersEyebrow)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        dayMarkerRow(label: TodayRitualCopy.dayMarkerCard, value: dayMarkerCardName)
                        dayMarkerRow(label: TodayRitualCopy.dayMarkerNumber, value: numerologyDigit)
                        dayMarkerRow(label: TodayRitualCopy.dayMarkerMoon, value: dayMarkerMoonTransitLine)
                        dayMarkerRow(label: TodayRitualCopy.dayMarkerMood, value: dayMarkerMoodLabel)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.white.opacity(0.45))
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                }

                TodayDayLogicCallout(style: .ritual, engine: dayEngineBrief, model: dayModelBrief)

                fusionDayHistoryStrip(placement: "ritual_after_callout", includeWeekSummary: !lowEnergyRitualMood)

                if let h = thesisHeadline {
                    Text(h)
                        .font(.title3.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.94))
                        .fixedSize(horizontal: false, vertical: true)
                }
                if let sl = thesisSubline {
                    Text(sl)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }

                DisclosureGroup(isExpanded: $guideAdditionalExpanded) {
                    VStack(alignment: .leading, spacing: 12) {
                        Text(TodayRitualCopy.daySummaryShortEyebrow)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        if !coreParas.isEmpty {
                            ForEach(Array(coreParas.enumerated()), id: \.offset) { i, p in
                                Text(p)
                                    .font(.subheadline.weight(i == 0 ? .semibold : .medium))
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(i == 0 ? 0.92 : 0.82))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        } else {
                            Text(dayReadyNarrativeBody)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }

                        Text(TodayRitualCopy.daySummaryDoTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        Text(doText)
                            .font(.subheadline.weight(.medium))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.9))
                            .fixedSize(horizontal: false, vertical: true)

                        Text(daySummaryAvoidTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        Text(dontText)
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                            .fixedSize(horizontal: false, vertical: true)

                        Text(TodayRitualCopy.daySummaryPracticalEyebrow)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        VStack(alignment: .leading, spacing: 6) {
                            dayMarkerRow(label: TodayRitualCopy.numerologyBestTimeLabel, value: lucky.time)
                            dayMarkerRow(label: TodayRitualCopy.numerologyColorLabel, value: lucky.color)
                            dayMarkerRow(label: TodayRitualCopy.numerologyStoneLabel, value: lucky.stone)
                            dayMarkerRow(label: TodayRitualCopy.heroTempoLabel, value: TodayRitualCopy.tempoLabelForEnergyScore(score: energyScore))
                            if showPracticalFocusInSummary {
                                dayMarkerRow(label: TodayRitualCopy.heroFocusLabel, value: heroFocus)
                            }
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white.opacity(0.4))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                } label: {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(TodayRitualCopy.guideAdditionalDisclosureTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                            .textCase(.uppercase)
                            .tracking(0.6)
                        Text(TodayRitualCopy.guideAdditionalDisclosureSubtitleRitualCard)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 2)
                }
                .tint(TodayFlowTheme.sunset)

                Button {
                    withAnimation(.spring(response: 0.38, dampingFraction: 0.86)) {
                        let willOpen = !daySummaryWhyExpanded
                        daySummaryWhyExpanded.toggle()
                        if willOpen {
                            let gid = store.todayGuideNarrative?.generationID
                            Task {
                                await store.trackTodaySurfaceEvent(
                                    eventType: "today_guide_why_opened",
                                    eventSource: "today",
                                    qualityScore: 0.55,
                                    generationLogId: gid,
                                    payload: ["surface": .string("ritual_day_summary")]
                                )
                            }
                        }
                    }
                } label: {
                    HStack {
                        Text(daySummaryWhyExpanded ? TodayRitualCopy.daySummaryWhyCollapse : TodayRitualCopy.daySummaryWhyCta)
                            .font(.subheadline.weight(.semibold))
                        Spacer(minLength: 8)
                        Image(systemName: daySummaryWhyExpanded ? "chevron.up" : "chevron.down")
                            .font(.caption.weight(.bold))
                            .foregroundStyle(TodayFlowTheme.sunset)
                    }
                    .foregroundStyle(TodayFlowTheme.ink)
                    .padding(.vertical, 6)
                }
                .buttonStyle(.plain)

                if daySummaryWhyExpanded {
                    VStack(alignment: .leading, spacing: 10) {
                        if let h = reasonHeadline?.trimmingCharacters(in: .whitespacesAndNewlines), !h.isEmpty {
                            Text(h)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.92))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        ForEach(Array(reasonLines.enumerated()), id: \.offset) { _, line in
                            Text(line)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        if showBridgeInWhy {
                            Text(bridgeLine)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.5))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
                    }
                }

                Text(TodayRitualCopy.ritualDayReadyFootnote)
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                    .fixedSize(horizontal: false, vertical: true)

                Button {
                    Task {
                        await store.refreshIfNeeded()
                        await MainActor.run {
                            resetRitualForNewPass()
                        }
                    }
                } label: {
                    Text(TodayRitualCopy.refreshDayCta)
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
                .tint(TodayFlowTheme.sunset)
                Text("\(TodayRitualCopy.heroRhythmCaption): \(TodayRitualCopy.rhythmTierLabel(score: energyScore)) · \(TodayRitualCopy.heroScoreFootnote(score: es))")
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceEthereal(cornerRadius: 28)

            Divider().opacity(0.28).padding(.vertical, 6)
            Text(TodayRitualCopy.reloadDayPaidHeadline)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(TodayRitualCopy.reloadDayPaidBody)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                .fixedSize(horizontal: false, vertical: true)
        }
        .id("ritualYourDay")
    }

    private func dayMarkerRow(label: String, value: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(label)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .frame(width: 108, alignment: .leading)
            Text(value)
                .font(.caption.weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func guideNarrativeString(_ key: String) -> String? {
        guard let narrative = store.todayGuideNarrative else { return nil }
        guard let raw = narrative.payload[key]?.stringValue else { return nil }
        let t = raw.trimmingCharacters(in: CharacterSet.whitespacesAndNewlines)
        return t.isEmpty ? nil : t
    }

    private var dayMarkerCardName: String {
        drawnTarotMain?.nameRu ?? cycle.morning?.tarotCard?.name ?? "—"
    }

    private var dayMarkerMoodLabel: String {
        guard let id = selectedMood else { return "—" }
        return TodayRitualCopy.moodLabels.first(where: { $0.id == id })?.label ?? id
    }

    private var dayMarkerMoonTransitLine: String {
        let lunarLine = TodayPersonalDayRhythm.formatLunarRitualSummaryLine(
            whyMoon: ritualWhyMoonLine,
            whyLunar: ritualWhyLunarLine,
            lunarInfluence: guideNarrativeString("lunar_influence"),
            transitInfluence: guideNarrativeString("transit_influence"),
            maxLen: 160
        )
        if lunarLine != "—" { return lunarLine }
        if let m = store.natalChart?.positions["moon"]?.sign?.trimmingCharacters(in: .whitespacesAndNewlines), !m.isEmpty {
            return TodayRitualCopy.formatRitualFlowNatalMoon(sign: m)
        }
        return "—"
    }

    private var daySummaryDontLine: String {
        let rawParts = avoid.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        let parts = rawParts.map { TodayRitualCueSanitizer.repairRitualDoNotEnterLine($0) }
        if parts.isEmpty {
            let dne = cycle.morning?.dailyHoroscope?.spine?.doNotEnter?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            let repaired = TodayRitualCueSanitizer.repairRitualDoNotEnterLine(dne)
            return repaired.isEmpty ? "—" : repaired
        }
        return parts.joined(separator: " ")
    }

    private static func daySummaryClip(_ s: String, maxLen: Int) -> String {
        let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
        guard t.count > maxLen else { return t }
        let idx = t.index(t.startIndex, offsetBy: max(0, maxLen - 1))
        return String(t[..<idx]) + "…"
    }

    private func checkInBlock(proxy: ScrollViewProxy) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(TodayRitualCopy.checkInTitle)
                .font(.todayFlowRitualHeroTitle)
                .foregroundStyle(TodayFlowTheme.ink)
                .ritualMultilineFill()
            Text(TodayRitualCopy.moodCheckSub)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .ritualMultilineFill()
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
                ForEach(TodayRitualCopy.moodGridMockup, id: \.id) { item in
                    Button {
                        selectMood(id: item.id, label: item.label)
                    } label: {
                        VStack(spacing: 8) {
                            Image(systemName: item.systemImage)
                                .font(.title2.weight(.light))
                                .symbolRenderingMode(.hierarchical)
                                .foregroundStyle(selectedMood == item.id ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.5))
                            Text(item.label)
                                .font(.caption.weight(.semibold))
                                .multilineTextAlignment(.center)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                                .fixedSize(horizontal: false, vertical: true)
                        }
                        .frame(maxWidth: .infinity, minHeight: 92)
                        .padding(.vertical, 10)
                        .background(selectedMood == item.id ? TodayFlowTheme.sunset.opacity(0.18) : Color.white.opacity(0.55))
                        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        .overlay {
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .stroke(
                                    selectedMood == item.id ? TodayFlowTheme.sunset.opacity(0.45) : TodayFlowTheme.gold.opacity(0.28),
                                    lineWidth: selectedMood == item.id ? 1.5 : 1
                                )
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
            if let moodNote {
                Text(moodNote)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.85))
                    .ritualMultilineFill()
            }
            if selectedMood != nil {
                VStack(alignment: .leading, spacing: 8) {
                    Text(TodayRitualCopy.checkInMicroEyebrow)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                        .ritualMultilineFill()
                    Text(TodayRitualCopy.checkInMicroHint)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .ritualMultilineFill()
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 100), spacing: 8)], spacing: 8) {
                        ForEach(TodayRitualCopy.headTopicChips, id: \.0) { id, label in
                            Button {
                                headTopic = id
                                persistRitualExtras()
                                Task {
                                    await store.trackTodaySurfaceEvent(
                                        eventType: "head_topic_selected",
                                        eventSource: "today",
                                        qualityScore: 0.82,
                                        payload: ["topic_id": .string(id)]
                                    )
                                }
                                if checkInSubmitted, let ctx = narrativeRitualContextPayload(headTopicOverride: id) {
                                    Task {
                                        try? await store.refreshTodayNarrativeAfterRitual(context: ctx)
                                    }
                                }
                            } label: {
                                Text(label)
                                    .font(.caption.weight(.medium))
                                    .multilineTextAlignment(.center)
                                    .fixedSize(horizontal: false, vertical: true)
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 8)
                                    .frame(maxWidth: .infinity)
                                    .background(headTopic == id ? TodayFlowTheme.sunset.opacity(0.22) : Color.white.opacity(0.55))
                                    .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding(.top, 6)
                Button {
                    submitCheckInAndAdvance(proxy: proxy)
                } label: {
                    Text(TodayRitualCopy.ritualMoodDoneCta)
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(RitualRoseGoldProminentButtonStyle())
                .padding(.top, 8)
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 24)
        .id("ritualCheckin")
    }

    /// Контекст для `POST /today/narrative` (паритет с веб `TodayRitualNarrativePayload`).
    /// `headTopicOverride` — свежий id с чипа (в том же тике `@State` ещё может быть старым).
    private func narrativeRitualContextPayload(headTopicOverride: String? = nil) -> TodayNarrativeRitualContextPayload? {
        guard let mood = selectedMood, let tid = tarotMainId, let card = drawnTarotMain, showNumberBody else { return nil }
        let ht = headTopicOverride ?? headTopic
        return TodayNarrativeRitualContextPayload(
            tarot_main_id: tid,
            tarot_name_ru: card.nameRu,
            numerology_value: numerologyDigit,
            mood: mood,
            head_topic: ht,
            day_events: cycle.dayEventsForNarrative()
        )
    }

    private func submitCheckInAndAdvance(proxy: ScrollViewProxy) {
        guard let ctx = narrativeRitualContextPayload() else { return }
        guard let (after, effects) = TodayRitualSpineReducer.apply(
            event: .submittedCheckIn,
            to: ritualSpineSnapshot
        ) else { return }
        mergeSpineSnapshot(after)
        applySpineEffects(effects, proxy: nil)
        let scrollAfterNarrative = effects.scrollAfterNarrativeRefresh
        Task {
            try? await store.refreshTodayNarrativeAfterRitual(context: ctx)
            await MainActor.run {
                if let anchor = scrollAfterNarrative {
                    withAnimation(.spring(response: 0.45, dampingFraction: 0.86)) {
                        proxy.scrollTo(anchor, anchor: .top)
                    }
                }
            }
        }
    }

    /// DE-9: `fusion.day_history` — в сводке дня и повторно у блока сфер (паритет веб `TodayDayHistoryStrip` в `TodayResultView`).
    /// - Parameter placement: `ritual_after_callout` | `your_day_spheres` — для `today_day_history_first_visible`.
    @ViewBuilder
    private func fusionDayHistoryStrip(placement: String, includeWeekSummary: Bool = true) -> some View {
        if let histLine = TodayRitualCopy.formatFusionDayHistoryLine(store.fusionIndex?.dayHistory) {
            let weekLine = TodayRitualCopy.formatFusionDayHistoryWeekLine(store.fusionIndex?.dayHistory)
            let meaningLine = TodayRitualCopy.formatFusionDayHistoryMeaningLine(store.fusionIndex?.dayHistory)
            let reflectionLine = TodayRitualCopy.formatFusionDayHistoryReflectionLine(store.fusionIndex?.dayHistory)
            let showDayHistoryFooterHint = store.fusionIndex?.dayHistory?.fusionScoreDeltaTrustworthy != false
            VStack(alignment: .leading, spacing: 6) {
                Text(TodayRitualCopy.dayHistoryEyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .ritualMultilineFill()
                Text(histLine)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.86))
                    .fixedSize(horizontal: false, vertical: true)
                    .ritualMultilineFill()
                if let meaningLine {
                    Text(meaningLine)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                        .ritualMultilineFill()
                }
                if let reflectionLine {
                    Text(reflectionLine)
                        .font(.caption.weight(.medium))
                        .italic()
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                        .ritualMultilineFill()
                }
                if includeWeekSummary, let weekLine {
                    Text(weekLine)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                        .ritualMultilineFill()
                }
                if showDayHistoryFooterHint {
                    Text(TodayRitualCopy.dayHistoryHint)
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                        .ritualMultilineFill()
                }
            }
            .padding(12)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.42))
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
            }
            .onAppear {
                guard !dayHistoryFirstVisibleLogged.contains(placement) else { return }
                dayHistoryFirstVisibleLogged.insert(placement)
                let gid = store.todayGuideNarrative?.generationID
                Task {
                    await store.trackTodaySurfaceEvent(
                        eventType: "today_day_history_first_visible",
                        eventSource: "today",
                        qualityScore: 0.45,
                        generationLogId: gid,
                        payload: ["surface": .string(placement)]
                    )
                }
            }
        }
    }

    private var spheresTriadBlock: some View {
        let rows = sphereTriadRows
        return VStack(alignment: .leading, spacing: 10) {
            fusionDayHistoryStrip(placement: "your_day_spheres", includeWeekSummary: !lowEnergyRitualMood)
            Text(TodayRitualCopy.areasEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .ritualMultilineFill()
            Text(TodayRitualCopy.areasTitle)
                .font(.title3.weight(.semibold))
                .ritualMultilineFill()
            Text(TodayRitualCopy.areasIntroToday)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                .fixedSize(horizontal: false, vertical: true)
            if sphereScoresProvisional {
                Text(TodayRitualCopy.areasScoresProvisionalHint)
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                    .fixedSize(horizontal: false, vertical: true)
                    .ritualMultilineFill()
            }
            if areasAllFallback {
                Text(TodayRitualCopy.areasFallback)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                    .ritualMultilineFill()
            }
            Text(TodayRitualCopy.sphereDeckSwipeHint)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                .ritualMultilineFill()
            if rows.isEmpty {
                Text(TodayRitualCopy.areasFallback)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
            } else {
                VStack(alignment: .leading, spacing: 10) {
                    ForEach(rows, id: \.area) { row in
                        if let a = triadArea(for: row.area) {
                            sphereTriadRowCard(row: row, area: a, scoresProvisional: sphereScoresProvisional)
                        }
                    }
                }
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceEthereal(cornerRadius: 24)
        .padding(.top, 6)
        .id("ritualFourAreas")
    }

    @ViewBuilder
    private func sphereTriadRowCard(row: SphereTriadGuideRow, area: RitualFourArea, scoresProvisional: Bool) -> some View {
        let pct = min(100, max(0, area.score))
        let stanceMark = row.stance == "up" ? "↑" : (row.stance == "down" ? "↓" : "○")
        let stanceColor: Color = row.stance == "up"
            ? Color(red: 0.18, green: 0.48, blue: 0.28)
            : (row.stance == "down" ? Color(red: 0.64, green: 0.24, blue: 0.24) : TodayFlowTheme.ink.opacity(0.55))
        let titleLabel = row.area == "love" ? TodayRitualCopy.relationshipSphereLabel : area.title
        VStack(alignment: .leading, spacing: 10) {
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .top, spacing: 8) {
                    Text(titleLabel)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .multilineTextAlignment(.leading)
                    Text(stanceMark)
                        .font(.subheadline.weight(.bold))
                        .foregroundStyle(stanceColor)
                    Text(area.rhythmTier)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                        .multilineTextAlignment(.trailing)
                        .frame(maxWidth: 120, alignment: .trailing)
                }
                Text(row.line)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.9))
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .multilineTextAlignment(.leading)
                GeometryReader { g in
                    ZStack(alignment: .leading) {
                        Capsule().fill(TodayFlowTheme.gold.opacity(0.2))
                        Capsule()
                            .fill(TodayFlowTheme.gold.opacity(0.85))
                            .frame(width: max(4, g.size.width * CGFloat(pct) / 100))
                    }
                }
                .frame(height: 8)
                .accessibilityLabel(TodayRitualCopy.formatRitualFlowSphereRhythmA11y(title: titleLabel, pct: pct))
                Button {
                    expandedPercentArea = expandedPercentArea == row.area ? nil : row.area
                } label: {
                    Text(TodayRitualCopy.spherePercentPrompt(score: pct, provisional: scoresProvisional))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sunset)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .buttonStyle(.plain)
                if expandedPercentArea == row.area {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(TodayRitualCopy.spherePercentExplainerTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        Text(TodayRitualCopy.spherePercentExplainerBody)
                            .font(.caption2)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.55))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                }
                Text(TodayRitualCopy.areaTodayEyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                if area.hasDayScenario {
                    if !area.todayHeadline.isEmpty {
                        Text(area.todayHeadline)
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    if !area.todayDetail.isEmpty {
                        Text(area.todayDetail)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                    }
                } else {
                    Text(TodayRitualCopy.areasScenarioMissing)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    Text(area.insight)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                }
                if expandedArea == row.area {
                    Text("\(TodayRitualCopy.areaRhythmEyebrow). \(area.rhythmTier). \(TodayRitualCopy.areaRhythmExpanded) \(TodayRitualCopy.heroScoreFootnote(score: pct))")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                    Text("\(TodayRitualCopy.areaSignal) — \(area.reason)")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                        .fixedSize(horizontal: false, vertical: true)
                    Text("\(TodayRitualCopy.areaNuance) — \(area.watch)")
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .contentShape(Rectangle())
            .onTapGesture {
                withAnimation(.spring(response: 0.42, dampingFraction: 0.88)) {
                    expandedArea = expandedArea == row.area ? nil : row.area
                }
            }
            Button {
                sphereDetailArea = area
                sphereSheetPresented = true
                Task {
                    await store.trackTodaySurfaceEvent(
                        eventType: "sphere_opened",
                        eventSource: "today",
                        qualityScore: 0.78,
                        generationLogId: store.todayGuideNarrative?.generationID,
                        payload: ["sphere_id": .string(row.area)]
                    )
                }
            } label: {
                Text(TodayRitualCopy.sphereDeckOpenDetailCta)
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.sunset)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 18)
    }

    private var focusBlock: some View {
        let opts = actionOptionsForFocus
        let idxSel = opts.isEmpty ? 0 : min(max(0, selectedActionOption), opts.count - 1)
        return VStack(alignment: .leading, spacing: 10) {
            Text(TodayRitualCopy.focusEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .ritualMultilineFill()
            Text(TodayRitualCopy.focusTitle)
                .font(.title3.weight(.semibold))
                .ritualMultilineFill()
            Text(TodayRitualCopy.focusChooseOneHint)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
            if let gmc = store.fusionIndex?.activityContext.guideMeaningCompletionsToday, !lowEnergyRitualMood {
                GuideMeaningCompletionsFocusStrip(gmc: gmc)
            }
            ForEach(Array(opts.enumerated()), id: \.offset) { idx, line in
                Button {
                    selectedActionOption = idx
                } label: {
                    HStack {
                        Text(line)
                            .font(.subheadline.weight(.medium))
                            .multilineTextAlignment(.leading)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        if idxSel == idx {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundStyle(TodayFlowTheme.sunset)
                        }
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(idxSel == idx ? TodayFlowTheme.sunset.opacity(0.14) : Color.white.opacity(0.5))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(idxSel == idx ? TodayFlowTheme.sunset.opacity(0.45) : TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                    }
                }
                .buttonStyle(.plain)
            }
            HStack(spacing: 8) {
                if !lowEnergyRitualMood {
                    Button {
                        let label = opts.indices.contains(idxSel) ? opts[idxSel] : ""
                        onNavigateCalendarQuickCreate?(.goal)
                        Task {
                            await store.trackTodaySurfaceEvent(
                                eventType: "action_option_selected",
                                eventSource: "today",
                                qualityScore: 0.82,
                                generationLogId: store.todayGuideNarrative?.generationID,
                                payload: [
                                    "action_option_index": .number(Double(idxSel)),
                                    "action_option_title": .string(label),
                                ]
                            )
                        }
                    } label: {
                        Text(TodayRitualCopy.focusPickStep)
                    }
                    .buttonStyle(.bordered)
                    .tint(TodayFlowTheme.sunset)
                }
                Button {
                    focusSessionHint = true
                    let label = opts.indices.contains(idxSel) ? opts[idxSel] : ""
                    onStartFocus20Minutes?()
                    Task {
                        await store.trackTodaySurfaceEvent(
                            eventType: "focus_started",
                            eventSource: "today",
                            qualityScore: 0.72,
                            generationLogId: store.todayGuideNarrative?.generationID,
                            payload: [
                                "duration_minutes": .number(20),
                                "action_option_index": .number(Double(idxSel)),
                                "action_option_title": .string(label),
                            ]
                        )
                    }
                } label: {
                    Text(TodayRitualCopy.focusStart20)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
                if !lowEnergyRitualMood {
                    Button {
                        onSelectTab(.calendar)
                    } label: {
                        Text(TodayMainTabCopy.flow)
                    }
                    .buttonStyle(.bordered)
                    .tint(TodayFlowTheme.sunset)
                }
            }
            .font(.caption.weight(.semibold))
            if focusSessionHint {
                Text(TodayRitualCopy.focusStart20Hint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    .ritualMultilineFill()
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfaceSoft(cornerRadius: 24)
        .id("ritualFocus")
    }

    @ViewBuilder
    private var supportBlock: some View {
        let hooks = supportHooksList
        let hasGoals = hasWeeklyStructure
        if hooks.isEmpty && !hasGoals {
            EmptyView()
        } else {
            VStack(alignment: .leading, spacing: 10) {
                Text(TodayRitualCopy.supportEyebrow)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .ritualMultilineFill()
                Text(TodayRitualCopy.supportSectionTitle)
                    .font(.title3.weight(.semibold))
                    .ritualMultilineFill()
                if !hasGoals {
                    Text(TodayRitualCopy.supportIntroNoStructure)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .fixedSize(horizontal: false, vertical: true)
                }
                if !hooks.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(hooks, id: \.self) { line in
                            HStack(alignment: .top, spacing: 8) {
                                Text("•")
                                    .foregroundStyle(TodayFlowTheme.sunset)
                                Text(line)
                                    .font(.subheadline)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                    }
                }
                if hasGoals {
                    VStack(alignment: .leading, spacing: 6) {
                        ForEach(Array(store.goals.prefix(4)), id: \.id) { g in
                            Text(g.title)
                                .font(.subheadline.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.ink)
                        }
                    }
                    Button {
                        onSelectTab(.calendar)
                    } label: {
                        Text(TodayMainTabCopy.flow)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .tint(TodayFlowTheme.sunset)
                }
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
            .todayFlowSurfaceEthereal(cornerRadius: 24)
        }
    }

    private var buildDayBlock: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(TodayRitualCopy.buildDayEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .ritualMultilineFill()
            Text(TodayRitualCopy.buildDayTitle)
                .font(.title3.weight(.semibold))
                .ritualMultilineFill()
            Text(TodayRitualCopy.buildDayBody)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.8))
                .ritualMultilineFill()
            Text(TodayRitualCopy.buildDayIdeasTitle)
                .font(.subheadline.weight(.semibold))
                .padding(.top, 4)
                .ritualMultilineFill()
            Text(TodayRitualCopy.buildDayIdeasIntro)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .ritualMultilineFill()
            VStack(alignment: .leading, spacing: 8) {
                ForEach(goalSuggestions) { suggestion in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(suggestion.title)
                            .font(.caption.weight(.semibold))
                            .ritualMultilineFill()
                        Text(suggestion.reason)
                            .font(.caption2)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.7))
                            .ritualMultilineFill()
                    }
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.38))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                }
            }
            Text(TodayRitualCopy.buildDayCalendarHint)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                .ritualMultilineFill()
            if !lowEnergyRitualMood {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 104), spacing: 8)], spacing: 8) {
                    ForEach(buildDayQuickChips, id: \.id) { chip in
                        Button {
                            if let onNavigateCalendarQuickCreate {
                                onNavigateCalendarQuickCreate(chip.kind)
                            } else {
                                onSelectTab(.calendar)
                            }
                        } label: {
                            Text(chip.title)
                                .font(.subheadline.weight(.medium))
                                .multilineTextAlignment(.center)
                                .fixedSize(horizontal: false, vertical: true)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 8)
                                .frame(maxWidth: .infinity)
                                .background(Color.white.opacity(0.5))
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
                ForEach(dayProtectionOptions) { option in
                    Button {
                        withAnimation(.spring(response: 0.36, dampingFraction: 0.88)) {
                            selectedProtection = option
                            protectionFeedback = nil
                        }
                    } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            Text(option.title)
                                .font(.subheadline.weight(.semibold))
                                .ritualMultilineFill()
                            Text(option.reason)
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                                .ritualMultilineFill()
                        }
                        .padding(14)
                        .frame(maxWidth: .infinity, minHeight: 108, alignment: .topLeading)
                        .background(selectedProtection == option ? TodayFlowTheme.sunset.opacity(0.14) : Color.white.opacity(0.44))
                        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
            }
            if let selectedProtection {
                Text(selectedProtection.prompt)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                    .ritualMultilineFill()
            }
            Button {
                saveProtectionChoice()
            } label: {
                Text(isSavingProtection ? TodayRitualCopy.ritualFlowProtectionSaving : TodayRitualCopy.ritualFlowProtectionSaveCta)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.sunset)
            .disabled(selectedProtection == nil || isSavingProtection)
            if let protectionFeedback {
                Text(protectionFeedback)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.moss)
                    .ritualMultilineFill()
            }
        }
        .padding(20)
        .todayFlowSurfaceEthereal(cornerRadius: 24)
    }

    private var essentialsBlock: some View {
        let itemsFull = TodayRitualCopy.essentialsForMood(selectedMood)
        let items = lowEnergyRitualMood ? Array(itemsFull.prefix(1)) : itemsFull
        let done = Double(items.filter { essentials.contains($0.id) }.count)
        return VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .center, spacing: 16) {
                EssentialsRing(done: Int(done), total: items.count)
                VStack(alignment: .leading, spacing: 4) {
                    Text(TodayRitualCopy.essentialsEyebrow)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.sand)
                        .ritualMultilineFill()
                    Text(TodayRitualCopy.essentialsTitle)
                        .font(.title3.weight(.semibold))
                        .ritualMultilineFill()
                    Text(TodayRitualCopy.essentialsSub)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .ritualMultilineFill()
                    Text(TodayRitualCopy.essentialsPurposeHint)
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                        .ritualMultilineFill()
                    if essentialsMoodAdapted(selectedMood) {
                        Text(TodayRitualCopy.essentialsMoodAdaptHint)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                            .ritualMultilineFill()
                    }
                    Text(TodayRitualCopy.essentialsProgressLabel(done: Int(done), total: items.count))
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                        .ritualMultilineFill()
                    Text(TodayRitualCopy.essentialsProgressExplain)
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.62))
                        .ritualMultilineFill()
                }
            }
            ForEach(items) { item in
                Button {
                    let on: Bool
                    if essentials.contains(item.id) {
                        essentials.remove(item.id)
                        on = false
                    } else {
                        essentials.insert(item.id)
                        on = true
                    }
                    persistRitualExtras()
                    Task {
                        await store.trackTodaySurfaceEvent(
                            eventType: "consistency_bonus",
                            eventSource: "today",
                            qualityScore: 0.6,
                            generationLogId: store.todayGuideNarrative?.generationID,
                            payload: ["habit": .string(item.id), "on": .bool(on)]
                        )
                    }
                } label: {
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Image(systemName: essentials.contains(item.id) ? "checkmark.square.fill" : "square")
                                .foregroundStyle(essentials.contains(item.id) ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.38))
                            Text(item.title)
                                .ritualMultilineFill()
                            Spacer(minLength: 0)
                        }
                        Text(item.explanation)
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.68))
                            .ritualMultilineFill()
                    }
                    .padding(.vertical, 8)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(20)
        .todayFlowSurfaceEthereal(cornerRadius: 24)
    }

    private var eveningHookBlock: some View {
        VStack(alignment: .center, spacing: 8) {
            Text(TodayRitualCopy.eveningHookTitle)
                .font(.title3.weight(.semibold))
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity)
            Text(TodayRitualCopy.eveningHookBody)
                .font(.subheadline)
                .multilineTextAlignment(.center)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
                .frame(maxWidth: .infinity)
            if let t = eveningTarotLine {
                Text(t)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .padding(.top, 4)
                    .ritualMultilineFill()
            }
            eveningFoldBlock
                .padding(.top, 6)
        }
        .frame(maxWidth: .infinity)
        .padding(20)
        .todayFlowSurfaceEthereal(cornerRadius: 24)
        .id("ritualEvening")
    }

    private var eveningFoldBlock: some View {
        DisclosureGroup {
            VStack(alignment: .leading, spacing: 12) {
                if eveningNarrativeLoading && store.todayEveningNarrative == nil {
                    ProgressView(TodayRitualCopy.ritualFlowEveningNarrativeLoading)
                        .tint(TodayFlowTheme.sunset)
                } else if let p = store.todayEveningNarrative?.payload {
                    Text(p.narrativeString("headline") ?? p.narrativeString("subline") ?? TodayRitualCopy.ritualFlowEveningHeadlineFallback)
                        .font(.subheadline)
                        .ritualMultilineFill()
                }
                TodayEveningComposer(store: store, cycle: cycle)
            }
        } label: {
            Text(TodayRitualCopy.eveningDetails)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sunset)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
        }
        .tint(TodayFlowTheme.sunset)
    }

    // MARK: - Derived

    private var hasWeeklyStructure: Bool { !store.goals.isEmpty }

    private var buildDayQuickChips: [(id: String, title: String, kind: TrackerQuickCreateKind)] {
        TodayRitualCopy.BuildDayQuickChips.rows
    }

    /// Энергия для подписей ритма: те же числа, что кольца (state-map с дашборда → fusion в сторе → hero → контур).
    private var heroFusionScores: FusionScores? {
        dashboard.fusionScores ?? store.fusionIndex?.scores
    }

    private var energyScore: Int {
        if let e = heroFusionScores?.energy { return min(100, max(0, e)) }
        if let h = cycle.morning?.decisionEngine?.hero?.energyScore {
            return min(100, max(0, h))
        }
        return min(100, max(0, dashboard.contour.score))
    }

    private var dayTypeHeadline: String {
        if let m = cycle.morning?.dailyHoroscope?.spine?.bestMode, !m.isEmpty { return m }
        if let h = cycle.morning?.dailyHoroscope?.headline, !h.isEmpty { return h }
        let e = dashboard.energyTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        return e.isEmpty ? TodayRitualCopy.ritualGuideDayLabelFallback : e
    }

    private var subtitleLine: String {
        if let fm = cycle.morning?.dailyHoroscope?.spine?.firstMove, !fm.isEmpty { return fm }
        if !dashboard.headline.isEmpty { return dashboard.headline }
        return TodayRitualCopy.ritualFlowHeroSubtitleFallback
    }

    private var heroRiskBase: String {
        let r = cycle.morning?.dailyHoroscope?.spine?.mainRisk?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !r.isEmpty { return r }
        if let a = avoid.first {
            let t = a.trimmingCharacters(in: .whitespacesAndNewlines)
            if !t.isEmpty { return t }
        }
        return "—"
    }

    /// Паритет веб `dayFocusLine`: таро → best_mode → заголовок сводки (без headline narrative в «фокусе»).
    private var heroFocus: String {
        if tarotApplied, let x = drawnTarotMain?.focusRu?.trimmingCharacters(in: .whitespacesAndNewlines), !x.isEmpty {
            return x
        }
        let bm = cycle.morning?.dailyHoroscope?.spine?.bestMode?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        if !bm.isEmpty { return bm }
        let st = summaryTitle.trimmingCharacters(in: .whitespacesAndNewlines)
        return st.isEmpty ? "—" : st
    }

    private var heroRisk: String {
        if tarotApplied, let x = drawnTarotMain?.riskRu?.trimmingCharacters(in: .whitespacesAndNewlines), !x.isEmpty {
            return x
        }
        return heroRiskBase
    }

    private var numerologyValueLine: String {
        TodayRitualCopy.formatRitualFlowNumerologyLine(
            value: cycle.morning?.numerologyNumber?.value ?? cycle.morning?.numerologyNumber?.reducedValue
        )
    }

    private var numerologyMeaning: String {
        let raw = cycle.morning?.numerologyNumber?.title ?? dashboard.numerologyTitle
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        return t.isEmpty ? TodayRitualCopy.numerologyMeaningFallbackShort : t
    }

    private var numerologyDigit: String {
        if let v = cycle.morning?.numerologyNumber?.value ?? cycle.morning?.numerologyNumber?.reducedValue {
            return "\(v)"
        }
        return "—"
    }

    private var bridgeLine: String {
        if let m = tarotMainId, let card = TodayTarotTodayRuCatalog.card(m) {
            let rhythm = TodayPersonalDayRhythm.personalDayRhythmBridgeSuffix(
                reduced: cycle.morning?.numerologyNumber?.reducedValue,
                displayValue: numerologyDigit
            )
            return TodayRitualCopy.formatRitualCardNumberBridgeWithTarotPicked(
                cardNameRu: card.nameRu,
                numerologyDigit: numerologyDigit,
                rhythmSuffix: rhythm,
                clarifierNameRu: drawnTarotClarifier?.nameRu
            )
        }
        let fallback = cycle.morning?.tarotCard?.name ?? dashboard.tarotTitle
        return TodayRitualCopy.formatRitualCardNumberBridgePageFallback(cardName: fallback, numerologyDigit: numerologyDigit)
    }

    /// Тот же приоритет, что `guideHeadline` на `/today` (`today/page.tsx`): ось дня → первый фрагмент прогноза → guidance по энергии.
    private var summaryTitle: String {
        if let headline = TodayContractMapper.themeHeadline(from: store.todayContract), !headline.isEmpty {
            return headline
        }
        if let a = cycle.morning?.dailyHoroscope?.spine?.dayAxis?.trimmingCharacters(in: .whitespacesAndNewlines), !a.isEmpty {
            return a
        }
        if let raw = cycle.morning?.dailyForecastSummary?.summary?.trimmingCharacters(in: .whitespacesAndNewlines), !raw.isEmpty {
            let seg = TodayRitualSignals.guideHeadlineSegment(fromForecastSummary: raw)
            if !seg.isEmpty { return seg }
        }
        return TodayRitualSignals.dayEnergyGuidanceLine(score: energyScore)
    }

    private var possible: [String] {
        TodayRitualSignals.possible(from: cycle.morning)
    }

    private var avoid: [String] {
        TodayRitualSignals.avoid(from: cycle.morning)
    }

    private var support: [String] {
        let bm = cycle.morning?.dailyHoroscope?.spine?.bestMode ?? ""
        return TodayRitualSignals.support(bestMode: bm, guidanceSummary: dashboard.guidanceSummary)
    }

    private var actionLines: [String] {
        var lines = dashboard.actionItems
        if tarotApplied, let f = drawnTarotMain?.focusRu?.trimmingCharacters(in: .whitespacesAndNewlines), !f.isEmpty {
            lines = [f] + lines
        }
        return lines
    }

    private var areasAllBase: [RitualFourArea] {
        RitualFourAreaBuilder.build(
            meaningRings: store.meaningRings,
            fusion: store.fusionIndex,
            spine: cycle.morning?.dailyHoroscope?.spine,
            narrative: store.todaySpheresNarrative?.payload,
            recommendations: cycle.morning?.dailyRecommendations,
            headline: cycle.morning?.dailyHoroscope?.headline,
            mood: selectedMood,
            scenarios: dashboard.scenarios,
            possible: possible,
            support: support
        )
    }

    private var tarotBumpMerged: [String: Int] {
        guard tarotApplied else { return [:] }
        let mainBump = drawnTarotMain?.sphereBump
        let clarBump = drawnTarotClarifier?.sphereBump
        return TodayTarotDayDraw.mergeSphereBumps(main: mainBump, clarifier: clarBump)
    }

    private var areasAll: [RitualFourArea] {
        let built = areasAllBase
        let bump = tarotBumpMerged
        guard tarotApplied, !bump.isEmpty else { return built }
        return RitualFourAreaBuilder.applyTarotSphereBias(built, bump: bump)
    }

    private var sphereTriadRows: [SphereTriadGuideRow] {
        if let rows = TodayGuideActionable.parseSphereTriad(from: store.todayGuideNarrative?.payload) {
            return rows
        }
        return sphereTriadFallback()
    }

    private func triadArea(for id: String) -> RitualFourArea? {
        areasAll.first { $0.id == id }
    }

    private func sphereTriadFallback() -> [SphereTriadGuideRow] {
        let triple = ["work", "love", "money"].compactMap { id in areasAll.first { $0.id == id } }
        guard triple.count == 3 else { return [] }
        let sorted = triple.sorted { $0.score > $1.score }
        let strong = sorted[0]
        let weak = sorted[2]
        let mid = sorted[1]
        func line(_ a: RitualFourArea, stance: String) -> String {
            let head = a.id == "love" ? TodayRitualCopy.relationshipSphereLabel : a.title
            let tail = a.todayHeadline.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                ? a.insight.trimmingCharacters(in: .whitespacesAndNewlines)
                : a.todayHeadline.trimmingCharacters(in: .whitespacesAndNewlines)
            return TodayRitualCopy.formatRitualFlowTriadLine(head: head, tail: tail, stance: stance)
        }
        return [
            SphereTriadGuideRow(area: strong.id, stance: "up", line: line(strong, stance: "up")),
            SphereTriadGuideRow(area: weak.id, stance: "down", line: line(weak, stance: "down")),
            SphereTriadGuideRow(area: mid.id, stance: "neutral", line: line(mid, stance: "neutral")),
        ]
    }

    private var actionOptionsForFocus: [String] {
        let fromGuide = TodayGuideActionable.parseActionOptions(from: store.todayGuideNarrative?.payload)
        let base: [String] = {
            if fromGuide.count >= 3 { return Array(fromGuide.prefix(3)) }
            var lines = actionLines
            while lines.count < 3 {
                lines.append(TodayRitualCopy.focusFallbackLine)
            }
            return Array(lines.prefix(3))
        }()
        if lowEnergyRitualMood {
            return Array(base.prefix(1))
        }
        return base
    }

    private var supportHooksList: [String] {
        TodayGuideActionable.parseSupportHooks(from: store.todayGuideNarrative?.payload)
    }

    private var areasAllFallback: Bool {
        areasAll.allSatisfy(\.isFallback)
    }

    /// O11: паритет `computeSphereScoresProvisional` на вебе (`todayFourAreas.ts`).
    private var sphereScoresProvisional: Bool {
        if store.meaningRings.contains(where: { $0.score > 0 }) { return false }
        guard let rc = store.fusionIndex?.rhythmContext else { return true }
        var categories = 0
        if !rc.goals.isEmpty { categories += 1 }
        if !rc.habits.isEmpty { categories += 1 }
        if !rc.ascetics.isEmpty { categories += 1 }
        if rc.diary.hasEntryToday || rc.diary.entriesLast7Days > 0 { categories += 1 }
        return categories < 2
    }

    private var lucky: (time: String, color: String, stone: String) {
        let seed = abs(cycle.date.hashValue)
        let w = TodayRitualCopy.NumerologyLuckyDayPresets.rows
        return w[seed % w.count]
    }

    private var eveningTarotLine: String? {
        guard tarotApplied, let m = drawnTarotMain?.eveningRu, !m.isEmpty else { return nil }
        if let c = drawnTarotClarifier?.eveningRu, !c.isEmpty { return "\(m) \(c)" }
        return m
    }

    private var heroEnergyMetrics: [HeroEnergyMetric] {
        let scores = heroFusionScores
        let e = scores.map { min(100, max(0, $0.energy)) } ?? energyScore
        let b = scores.map { min(100, max(0, $0.emotionalBalance)) } ?? min(100, max(0, e - 4))
        let f = scores.map { min(100, max(0, $0.focus)) } ?? min(100, max(0, e - 2))
        return [
            HeroEnergyMetric(title: TodayShellCopy.shellFusionOrbEnergy, value: e, tint: TodayFlowTheme.sunset),
            HeroEnergyMetric(title: TodayShellCopy.shellFusionOrbBalance, value: b, tint: TodayFlowTheme.moss),
            HeroEnergyMetric(title: TodayShellCopy.shellFusionOrbFocus, value: f, tint: TodayFlowTheme.twilight),
        ]
    }

    private var ritualWhyMoonLine: String? {
        guard let name = cycle.morning?.celestialEvents?.lunarPhase?.name?
            .trimmingCharacters(in: .whitespacesAndNewlines), !name.isEmpty else { return nil }
        return name
    }

    private var ritualWhyLunarLine: String? {
        guard let t = cycle.morning?.celestialEvents?.lunarPhase?.themes?
            .trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty else { return nil }
        return t
    }

    private var numerologyDetailForWhy: String? {
        let ex = cycle.morning?.numerologyExplanation
        let candidates = [ex?.whyThisNumber, ex?.howDayLooks, ex?.meaning, ex?.summary]
        let raw = candidates.compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }.first { !$0.isEmpty } ?? ""
        return raw.count >= 36 ? raw : nil
    }

    private var coreParagraphsForRitualAvoid: [String] {
        TodayGuideActionable.coreMessageParagraphs(from: store.todayGuideNarrative?.payload)
    }

    private var displayDoText: String {
        var cands: [String] = []
        for p in possible {
            let t = p.trimmingCharacters(in: .whitespacesAndNewlines)
            if !t.isEmpty, !TodayRitualCueSanitizer.isGarbageRitualActionCue(t) { cands.append(t) }
        }
        if let fm = cycle.morning?.dailyHoroscope?.spine?.firstMove?.trimmingCharacters(in: .whitespacesAndNewlines), !fm.isEmpty,
           !TodayRitualCueSanitizer.isGarbageRitualActionCue(fm) {
            cands.append(fm)
        }
        let sub = subtitleLine.trimmingCharacters(in: .whitespacesAndNewlines)
        if !sub.isEmpty, !TodayRitualCueSanitizer.isGarbageRitualActionCue(sub) { cands.append(sub) }
        var avoid: [String] = [heroFocus, summaryTitle, subtitleLine]
        avoid.append(contentsOf: coreParagraphsForRitualAvoid)
        avoid.append(contentsOf: possible)
        return TodayPersonalDayRhythm.pickFirstDistinctLine(candidates: cands, avoid: avoid)
    }

    private var ritualNarrativeAvoidLines: [String] {
        var acc: [String] = [summaryTitle, subtitleLine, displayDoText, daySummaryDontLine, heroFocus]
        acc.append(contentsOf: possible)
        acc.append(contentsOf: avoid)
        acc.append(contentsOf: support)
        if let r = cycle.morning?.dailyHoroscope?.spine?.mainRisk?.trimmingCharacters(in: .whitespacesAndNewlines), !r.isEmpty {
            acc.append(r)
        }
        if let b = cycle.morning?.dailyHoroscope?.spine?.bestMode?.trimmingCharacters(in: .whitespacesAndNewlines), !b.isEmpty {
            acc.append(b)
        }
        if let f = cycle.morning?.dailyHoroscope?.spine?.firstMove?.trimmingCharacters(in: .whitespacesAndNewlines), !f.isEmpty {
            acc.append(f)
        }
        if let d = cycle.morning?.dailyHoroscope?.spine?.doNotEnter?.trimmingCharacters(in: .whitespacesAndNewlines), !d.isEmpty {
            acc.append(d)
        }
        acc.append(contentsOf: coreParagraphsForRitualAvoid)
        var seen = Set<String>()
        var out: [String] = []
        for s in acc {
            let t = s.trimmingCharacters(in: .whitespacesAndNewlines)
            if t.count < 2 { continue }
            let k = t.lowercased()
            if seen.contains(k) { continue }
            seen.insert(k)
            out.append(t)
        }
        return out
    }

    private var whyGuideParsed: (headline: String?, lines: [String]) {
        TodayRitualWhyReasonLines.build(
            summaryTitle: summaryTitle,
            possible: possible,
            guidePayload: store.todayGuideNarrative?.payload,
            spineMainRisk: cycle.morning?.dailyHoroscope?.spine?.mainRisk,
            spineBestMode: cycle.morning?.dailyHoroscope?.spine?.bestMode,
            numerologyDisplayValue: numerologyDigit,
            numerologyReduced: cycle.morning?.numerologyNumber?.reducedValue,
            numerologyDetailLine: numerologyDetailForWhy,
            morningFocus: cycle.dayConnection?.morningFocus,
            whyMoon: ritualWhyMoonLine,
            whyLunar: ritualWhyLunarLine,
            avoidLines: ritualNarrativeAvoidLines
        )
    }

    private var reasonHeadline: String? { whyGuideParsed.headline }

    private var reasonLines: [String] { whyGuideParsed.lines }

    private var showPracticalFocusInSummary: Bool {
        let f = heroFocus.trimmingCharacters(in: .whitespacesAndNewlines)
        if f.isEmpty || f == "—" { return false }
        return !TodayPersonalDayRhythm.lineRedundantWithAny(f, pool: [displayDoText] + coreParagraphsForRitualAvoid)
    }

    private var showBridgeInWhy: Bool {
        var pool = ritualNarrativeAvoidLines + reasonLines
        if let h = reasonHeadline { pool.append(h) }
        return !TodayPersonalDayRhythm.lineRedundantWithAny(bridgeLine, pool: pool)
    }

    private var guidanceLead: GuidanceLead {
        let combined = ([dashboard.headline, dashboard.guidanceSummary] + actionLines).joined(separator: " ").lowercased()
        if combined.contains("отнош") || combined.contains("люб") || combined.contains("близ") {
            return .love
        }
        if combined.contains("работ") || combined.contains("деньг") || combined.contains("карьер") {
            return .work
        }
        return .neutral
    }

    private var dayProtectionOptions: [DayProtectionOption] {
        [
            DayProtectionOption(
                key: "discipline",
                title: TodayRitualCopy.ritualFlowProtectionDisciplineTitle,
                reason: TodayRitualCopy.ritualFlowProtectionDisciplineReason,
                prompt: TodayRitualCopy.ritualFlowProtectionDisciplinePrompt
            ),
            DayProtectionOption(
                key: "money",
                title: TodayRitualCopy.fourAreaLabelMoney,
                reason: TodayRitualCopy.ritualFlowProtectionMoneyReason,
                prompt: TodayRitualCopy.ritualFlowProtectionMoneyPrompt
            ),
            DayProtectionOption(
                key: "love",
                title: TodayRitualCopy.fourAreaLabelLove,
                reason: TodayRitualCopy.ritualFlowProtectionLoveReason,
                prompt: TodayRitualCopy.ritualFlowProtectionLovePrompt
            ),
            DayProtectionOption(
                key: "emotional_balance",
                title: TodayRitualCopy.ritualFlowProtectionBalanceTitle,
                reason: TodayRitualCopy.ritualFlowProtectionBalanceReason,
                prompt: TodayRitualCopy.ritualFlowProtectionBalancePrompt
            )
        ]
    }

    private var goalSuggestions: [GoalSuggestion] {
        if guidanceLead == .love {
            return [
                GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalLoveHonestTalkTitle, reason: TodayRitualCopy.ritualFlowGoalLoveHonestTalkReason),
                GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalLovePauseReplyTitle, reason: TodayRitualCopy.ritualFlowGoalLovePauseReplyReason),
            ]
        }
        if guidanceLead == .work {
            return [
                GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalWorkCalmBlockTitle, reason: TodayRitualCopy.ritualFlowGoalWorkCalmBlockReason),
                GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalWorkPauseSpendTitle, reason: TodayRitualCopy.ritualFlowGoalWorkPauseSpendReason),
            ]
        }
        return [
            GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalNeutralMorningTitle, reason: TodayRitualCopy.ritualFlowGoalNeutralMorningReason),
            GoalSuggestion(title: TodayRitualCopy.ritualFlowGoalNeutralOneStepTitle, reason: TodayRitualCopy.ritualFlowGoalNeutralOneStepReason),
        ]
    }

    private var formattedRUToday: String {
        let p = cycle.date.split(separator: "-")
        guard p.count == 3, let y = Int(p[0]), let m = Int(p[1]), let d = Int(p[2]) else { return cycle.date }
        var c = DateComponents()
        c.year = y; c.month = m; c.day = d
        let cal = Calendar(identifier: .gregorian)
        guard let date = cal.date(from: c) else { return cycle.date }
        let f = DateFormatter()
        f.locale = Locale(identifier: "ru_RU")
        f.dateFormat = "EEEE, d MMMM"
        return f.string(from: date)
    }

    @ViewBuilder
    private func summaryList(title: String, items: [String], tint: Color) -> some View {
        if !items.isEmpty {
            VStack(alignment: .leading, spacing: 8) {
                Text(title)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(tint)
                    .ritualMultilineFill()
                ForEach(items, id: \.self) { x in
                    HStack(alignment: .top, spacing: 8) {
                        Circle()
                            .fill(tint)
                            .frame(width: 5, height: 5)
                            .padding(.top, 7)
                        Text(x)
                            .font(.subheadline)
                            .ritualMultilineFill()
                    }
                }
            }
        }
    }

    private func premiumMetaLine(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.56))
            Text(value)
                .fontWeight(.semibold)
                .ritualMultilineFill()
        }
        .font(.caption)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func saveProtectionChoice() {
        guard let selectedProtection else { return }
        isSavingProtection = true
        protectionFeedback = nil
        Task {
            do {
                try await store.saveMorningIntention(selectedProtection.prompt)
                await MainActor.run {
                    protectionFeedback = TodayRitualCopy.formatRitualFlowProtectionSaved(
                        titleLowercased: selectedProtection.title.lowercased()
                    )
                    isSavingProtection = false
                }
            } catch {
                await MainActor.run {
                    protectionFeedback = TodayRitualCopy.ritualFlowProtectionSaveError
                    isSavingProtection = false
                }
            }
        }
    }

    private func essentialsMoodAdapted(_ mood: String?) -> Bool {
        guard let mood else { return false }
        return ["tired", "anxious", "quiet_wish", "heavy", "motivated", "move_wish", "driven", "other"].contains(mood)
    }

    private func pruneEssentialsForCurrentMood() {
        let allowed = Set(TodayRitualCopy.essentialsForMood(selectedMood).map(\.id))
        essentials = essentials.intersection(allowed)
    }

    private func persistRitualExtras() {
        guard let email = store.authSession?.email else { return }
        TodayFlowPersistence.shared.saveRitualDayExtras(
            for: email,
            dateISO: cycle.date,
            extras: RitualDayExtras(
                mood: selectedMood,
                headTopic: headTopic,
                honestStep: honestStep,
                numberRhythm: numberRhythm,
                essentials: Array(essentials).sorted(),
                tarotMainId: tarotMainId,
                tarotClarifierId: tarotClarifierId,
                tarotApplied: tarotApplied,
                tarotContinueAck: tarotContinueAck,
                checkInSubmitted: checkInSubmitted
            )
        )
    }

    private func commitMainTarotFromPick() {
        tarotMeaningPresented = false
        showTarotExtraSteps = false
        let id = TodayTarotTodayRuCatalog.deckImageIdForDay(
            apiCardName: cycle.morning?.tarotCard?.name,
            dateISO: cycle.date
        )
        tarotMainId = id
        persistRitualExtras()
        Task {
            let gid = store.todayGuideNarrative?.generationID
            await store.trackTodaySurfaceEvent(
                eventType: "tarot_selected",
                eventSource: "today",
                qualityScore: 0.85,
                generationLogId: gid,
                payload: [
                    "role": .string("main"),
                    "card_index": .number(Double(id)),
                ]
            )
        }
    }

    private func resetRitualForNewPass() {
        let email = store.authSession?.email
        let dateISO = cycle.date
        TodayFlowPersistence.shared.clearOpenedDay(for: email, dateISO: dateISO)
        TodayFlowPersistence.shared.clearNumberRevealed(for: email, dateISO: dateISO)
        TodayFlowPersistence.shared.clearRitualDayExtras(for: email, dateISO: dateISO)
        showRitualBody = false
        showNumberBody = false
        selectedMood = nil
        moodNote = nil
        headTopic = nil
        honestStep = nil
        numberRhythm = nil
        expandedPercentArea = nil
        selectedActionOption = 0
        focusSessionHint = false
        focusSavedAck = false
        essentials = []
        tarotMainId = nil
        tarotClarifierId = nil
        tarotApplied = false
        tarotContinueAck = false
        expandedArea = nil
        showTarotExtraSteps = false
        showNumberExtraSteps = false
        checkInSubmitted = false
        didRestoreDayState = false
        dayHistoryFirstVisibleLogged = []
        restoreDayStateIfNeeded()
    }

    private func selectMood(id: String, label _: String) {
        guard let (after, effects) = TodayRitualSpineReducer.apply(
            event: .selectedMood(id),
            to: ritualSpineSnapshot
        ) else { return }
        mergeSpineSnapshot(after)
        applySpineEffects(effects, proxy: nil)
        switch id {
        case "motivated", "move_wish", "driven":
            moodNote = TodayRitualCopy.moodAckDrive
        case "other":
            moodNote = nil
        default:
            moodNote = TodayRitualCopy.moodAck
        }
        pruneEssentialsForCurrentMood()
        TodayDayEngagementSync.syncMorningMood(dateISO: cycle.date, moodId: id)
    }

    private func openDay(proxy: ScrollViewProxy) {
        guard let (after, effects) = TodayRitualSpineReducer.apply(
            event: .openedDay,
            to: ritualSpineSnapshot
        ) else { return }
        mergeSpineSnapshot(after)
        applySpineEffects(effects, proxy: proxy)
    }

    private func restoreDayStateIfNeeded() {
        guard !didRestoreDayState else { return }
        didRestoreDayState = true
        let email = store.authSession?.email
        let alreadyOpened = TodayFlowPersistence.shared.hasOpenedDay(for: email, dateISO: cycle.date)
        showRitualBody = alreadyOpened
        showNumberBody = TodayFlowPersistence.shared.hasNumberRevealed(for: email, dateISO: cycle.date)
        if let extras = TodayFlowPersistence.shared.loadRitualDayExtras(for: email, dateISO: cycle.date) {
            selectedMood = extras.mood
            headTopic = extras.headTopic
            honestStep = extras.honestStep
            numberRhythm = extras.numberRhythm
            essentials = Set(extras.essentials)
            tarotMainId = extras.tarotMainId
            tarotClarifierId = extras.tarotClarifierId
            tarotApplied = extras.tarotApplied ?? false
            let numberDone = TodayFlowPersistence.shared.hasNumberRevealed(for: email, dateISO: cycle.date)
            tarotContinueAck = extras.tarotContinueAck ?? ((extras.tarotMainId != nil) && numberDone)
            checkInSubmitted = extras.checkInSubmitted ?? false
            showTarotExtraSteps = (extras.tarotClarifierId != nil) || (extras.honestStep != nil) || (extras.tarotApplied == true)
            showNumberExtraSteps = extras.numberRhythm != nil
            if let m = extras.mood {
                switch m {
                case "motivated", "move_wish", "driven":
                    moodNote = TodayRitualCopy.moodAckDrive
                case "other":
                    moodNote = nil
                default:
                    moodNote = TodayRitualCopy.moodAck
                }
            } else {
                moodNote = nil
            }
            pruneEssentialsForCurrentMood()
        }
    }
}

// MARK: - Four areas

private struct RitualFourArea: Identifiable {
    let id: String
    let title: String
    let score: Int
    let rhythmTier: String
    let todayHeadline: String
    let todayDetail: String
    let hasDayScenario: Bool
    let insight: String
    let reason: String
    let watch: String
    let tint: Color
    let isFallback: Bool
}

private struct DayProtectionOption: Identifiable, Equatable {
    let key: String
    let title: String
    let reason: String
    let prompt: String

    var id: String { key }
}

/// Четыре сферы: формулы, clamp и ключи нарратива должны совпадать с `frontend/src/components/today/todayFourAreas.ts`.
private enum RitualFourAreaBuilder {
    static func rhythmTier(for score: Int) -> String {
        TodayRitualCopy.rhythmTierLabel(score: score)
    }

    private static func clampAreaScore(_ value: Int) -> Int {
        min(96, max(28, value))
    }

    /// Паритет с `applyTarotSphereBias` в `frontend/src/components/today/todayFourAreas.ts`.
    static func applyTarotSphereBias(_ areas: [RitualFourArea], bump: [String: Int]) -> [RitualFourArea] {
        guard !bump.isEmpty else { return areas }
        return areas.map { a in
            guard let add = bump[a.id] else { return a }
            let score = clampAreaScore(a.score + add)
            return RitualFourArea(
                id: a.id,
                title: a.title,
                score: score,
                rhythmTier: rhythmTier(for: score),
                todayHeadline: a.todayHeadline,
                todayDetail: a.todayDetail,
                hasDayScenario: a.hasDayScenario,
                insight: a.insight,
                reason: a.reason,
                watch: a.watch,
                tint: a.tint,
                isFallback: a.isFallback
            )
        }
    }

    private static func pickScenario(_ scenarios: [TodayScenario], slugs: [String]) -> TodayScenario? {
        for slug in slugs {
            if let hit = scenarios.first(where: { $0.id == slug }) { return hit }
        }
        return nil
    }

    private static func parts(from scenario: TodayScenario?) -> (has: Bool, headline: String, detail: String) {
        guard let scenario else { return (false, "", "") }
        let focus = scenario.focus?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let title = scenario.title.trimmingCharacters(in: .whitespacesAndNewlines)
        let summary = scenario.summary.trimmingCharacters(in: .whitespacesAndNewlines)
        let headline = (!focus.isEmpty ? focus : nil) ?? title
        let detail: String
        if summary.isEmpty {
            detail = ""
        } else if !focus.isEmpty {
            detail = summary != focus ? summary : ""
        } else {
            detail = summary
        }
        let has = !(headline.isEmpty && detail.isEmpty)
        return (has, headline, detail)
    }

    private static func energyToday(spine: TodayDailySpine?, possible: [String], support: [String]) -> (has: Bool, headline: String, detail: String) {
        let best = spine?.bestMode?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let risk = spine?.mainRisk?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let sup0 = support.first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let pos0 = possible.first?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let headline = (!best.isEmpty ? best : nil) ?? (!sup0.isEmpty ? sup0 : nil) ?? (!pos0.isEmpty ? pos0 : nil)
            ?? TodayRitualCopy.fourAreaEnergyHeadlineFallback
        var chunks: [String] = []
        if !pos0.isEmpty, pos0 != headline {
            chunks.append(pos0)
        }
        if !risk.isEmpty {
            chunks.append(TodayRitualCopy.formatFourAreaEnergyRiskChunk(risk: risk))
        }
        let detail = chunks.joined(separator: " ")
        let has = !best.isEmpty || !risk.isEmpty || (!pos0.isEmpty && pos0 != headline) || !sup0.isEmpty
        return (has, headline, detail)
    }

    static func build(
        meaningRings: [MeaningRingItem],
        fusion: FusionIndex?,
        spine: TodayDailySpine?,
        narrative: [String: JSONValue]?,
        recommendations: TodayDailyRecommendations?,
        headline: String?,
        mood: String?,
        scenarios: [TodayScenario],
        possible: [String],
        support: [String]
    ) -> [RitualFourArea] {
        func ring(_ candidates: [String]) -> Int? {
            for c in candidates {
                if let h = meaningRings.first(where: { $0.ring == c || $0.ring.lowercased() == c.lowercased() }) {
                    return h.score > 0 ? h.score : nil
                }
            }
            return nil
        }
        func narrativeReason(_ keys: [String]) -> String? {
            for key in keys {
                if let value = narrative?.narrativeString(key), !value.isEmpty {
                    return value
                }
            }
            return nil
        }
        func clamp(_ value: Int) -> Int {
            min(96, max(28, value))
        }
        func moodSuffix() -> String {
            TodayRitualCopy.fourAreaMoodSuffix(mood: mood)
        }
        let love = ring(["Love", "love"]) ?? fusion.map { min(100, $0.scores.energy + 4) } ?? 72
        let work = ring(["Purpose", "purpose"]) ?? fusion.map { min(100, Int(Double($0.scores.focus) * 0.7 + 25)) } ?? 68
        let money = ring(["Wealth", "wealth"]) ?? fusion.map { min(100, ($0.scores.energy + $0.scores.focus) / 2 + 8) } ?? 64
        let eAvg: Double? = fusion.map { Double($0.scores.energy + $0.scores.emotionalBalance + $0.scores.focus) / 3.0 }
        let energy = ring(["Energy", "energy"]) ?? (eAvg.map { min(100, Int($0 + 0.5)) } ?? 74)
        let bm = spine?.bestMode?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        let energyInsight = bm.isEmpty ? TodayRitualCopy.fourAreaEnergyInsightSoftDay : bm
        let hasRings = !meaningRings.isEmpty

        let loveSc = parts(from: pickScenario(scenarios, slugs: ["love", "family"]))
        let workSc = parts(from: pickScenario(scenarios, slugs: ["career"]))
        let moneySc = parts(from: pickScenario(scenarios, slugs: ["money"]))
        let energySc = energyToday(spine: spine, possible: possible, support: support)

        return [
            .init(
                id: "love",
                title: TodayRitualCopy.fourAreaLabelLove,
                score: clamp(love),
                rhythmTier: rhythmTier(for: clamp(love)),
                todayHeadline: loveSc.headline,
                todayDetail: loveSc.detail,
                hasDayScenario: loveSc.has,
                insight: narrativeReason(["love_insight", "relationships_insight"]) ?? TodayRitualCopy.fourAreaLoveInsightFallback,
                reason: narrativeReason(["love_reason", "relationship_reason", "relationships_reason"])
                    ?? TodayRitualCopy.fourAreaLoveReasonBase + moodSuffix(),
                watch: TodayRitualCopy.fourAreaLoveWatch,
                tint: TodayFlowTheme.roseClay,
                isFallback: !hasRings
            ),
            .init(
                id: "work",
                title: TodayRitualCopy.fourAreaLabelWork,
                score: clamp(work),
                rhythmTier: rhythmTier(for: clamp(work)),
                todayHeadline: workSc.headline,
                todayDetail: workSc.detail,
                hasDayScenario: workSc.has,
                insight: narrativeReason(["work_insight", "career_insight", "purpose_insight"]) ?? TodayRitualCopy.fourAreaWorkInsightFallback,
                reason: narrativeReason(["work_reason", "career_reason", "purpose_reason"])
                    ?? (spine?.firstMove ?? TodayRitualCopy.fourAreaWorkReasonNoFirstMoveFallback),
                watch: TodayRitualCopy.fourAreaWorkWatch,
                tint: TodayFlowTheme.twilight,
                isFallback: !hasRings
            ),
            .init(
                id: "money",
                title: TodayRitualCopy.fourAreaLabelMoney,
                score: clamp(money),
                rhythmTier: rhythmTier(for: clamp(money)),
                todayHeadline: moneySc.headline,
                todayDetail: moneySc.detail,
                hasDayScenario: moneySc.has,
                insight: narrativeReason(["money_insight", "wealth_insight", "resource_insight"]) ?? TodayRitualCopy.fourAreaMoneyInsightFallback,
                reason: narrativeReason(["money_reason", "wealth_reason", "resource_reason"])
                    ?? (recommendations?.whatToAvoid ?? TodayRitualCopy.fourAreaMoneyReasonNoAvoidFallback),
                watch: TodayRitualCopy.fourAreaMoneyWatch,
                tint: TodayFlowTheme.gold,
                isFallback: !hasRings
            ),
            .init(
                id: "energy",
                title: TodayRitualCopy.fourAreaLabelEnergy,
                score: clamp(energy),
                rhythmTier: rhythmTier(for: clamp(energy)),
                todayHeadline: energySc.headline,
                todayDetail: energySc.detail,
                hasDayScenario: energySc.has,
                insight: bm.isEmpty ? TodayRitualCopy.fourAreaEnergyInsightNoBestModeFallback : energyInsight,
                reason: narrativeReason(["energy_reason", "body_reason", "state_reason"]) ?? TodayRitualCopy.fourAreaEnergyReasonFallback,
                watch: TodayRitualCopy.fourAreaEnergyWatch,
                tint: TodayFlowTheme.moss,
                isFallback: !hasRings
            ),
        ]
    }

}

// MARK: - Ritual text layout (паритет переносов с веб `ritualTextWrap`)

private extension View {
    /// Текст заполняет ширину контейнера и переносится на узких экранах.
    func ritualMultilineFill(_ alignment: TextAlignment = .leading) -> some View {
        self
            .multilineTextAlignment(alignment)
            .frame(maxWidth: .infinity, alignment: alignment == .center ? .center : .leading)
            .fixedSize(horizontal: false, vertical: true)
    }
}

private struct EssentialsRing: View {
    let done: Int
    let total: Int

    private var progress: Double {
        guard total > 0 else { return 0 }
        return Double(done) / Double(total)
    }

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.34), lineWidth: 8)
            Circle()
                .trim(from: 0, to: max(0.02, min(progress, 1)))
                .stroke(
                    LinearGradient(
                        colors: [TodayFlowTheme.sunset.opacity(0.45), TodayFlowTheme.sunset, TodayFlowTheme.gold],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    style: StrokeStyle(lineWidth: 8, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
            Text("\(done)/\(total)")
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .frame(width: 62, height: 62)
    }
}

/// DE-7: чипы `guide_meaning_completions_today` у блока главного шага (паритет веб `TodayResultView`).
private struct GuideMeaningCompletionsFocusStrip: View {
    let gmc: [String: Int]

    var body: some View {
        let chips = TodayRitualCopy.guideMeaningCompletionChipItems(gmc)
        return VStack(alignment: .leading, spacing: 6) {
            Text(TodayRitualCopy.guideMeaningCompletionsEyebrow)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
                .ritualMultilineFill()
            if chips.isEmpty {
                Text(TodayRitualCopy.guideMeaningCompletionsEmpty)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    .fixedSize(horizontal: false, vertical: true)
                    .ritualMultilineFill()
            } else {
                LazyVGrid(
                    columns: [GridItem(.adaptive(minimum: 96), spacing: 6)],
                    alignment: .leading,
                    spacing: 6
                ) {
                    ForEach(chips, id: \.key) { chip in
                        Text("\(chip.label) · \(chip.count)")
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(Color.white.opacity(0.45))
                            .clipShape(RoundedRectangle(cornerRadius: 999, style: .continuous))
                            .overlay {
                                RoundedRectangle(cornerRadius: 999, style: .continuous)
                                    .stroke(TodayFlowTheme.gold.opacity(0.28), lineWidth: 1)
                            }
                    }
                }
            }
        }
    }
}

private enum GuidanceLead {
    case love
    case work
    case neutral
}

private struct GoalSuggestion: Identifiable {
    let title: String
    let reason: String
    var id: String { title }
}

private struct HeroEnergyMetric: Identifiable {
    let id = UUID()
    let title: String
    let value: Int
    let tint: Color
}

