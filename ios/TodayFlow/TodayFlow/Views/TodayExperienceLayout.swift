import SwiftUI

// MARK: - Public entry: полный сценарий «Today» (продуктовый слой + данные)
// RU/EN chrome: `TodayExperienceChromeCopy` ⇄ `TODAY_EXPERIENCE_CHROME_*` в `todayRitualCopy.ts`.
// Kept in a dedicated file so TodayView can compose the product-level layout.

struct TodayExperienceLayout: View {
    let store: TodayFlowStore
    let cycle: TodayCycle
    var onSelectTab: (AppTab) -> Void

    @State private var heroInsightPresented = false
    @State private var tarotFlipped = false
    @State private var selectedRing: MeaningRingItem?
    @State private var microAnswer: String?
    @State private var showMicroReward = false
    @State private var habitKeys: Set<String> = []
    @State private var didLoadLocalState = false

    private var dashboard: TodayDashboard { store.today }

    var body: some View {
        VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s4) {
            block1EnergyHero
            block2Theme
            block3Tarot
            block4Number
            block5Rings
            block6Practices
            block7Ritual
            block8MicroQuestion
            block9Habits
            block10Compatibility
            block11Guidance
            block12Diary
            block13Tomorrow
        }
        .onAppear { loadLocalStateIfNeeded() }
        .sheet(isPresented: $heroInsightPresented) {
            TodayHeroInsightSheet(
                cycle: cycle,
                dashboard: dashboard,
                natalChart: store.natalChart,
                fusion: store.fusionIndex
            )
            .presentationDetents([.medium, .large])
            .presentationDragIndicator(.visible)
        }
        .sheet(item: $selectedRing) { ring in
            TodayRingDetailSheet(
                ring: ring,
                onOpenGuidance: { onSelectTab(.questions) }
            )
            .presentationDetents([.medium, .large])
        }
        .onChange(of: habitKeys) { _, _ in
            persistHabitKeys()
        }
        .onChange(of: microAnswer) { _, _ in
            persistMicroAnswer()
        }
    }

    // MARK: Block 1 — Hero (сводка + оси fusion, без орбиты)

    private var block1EnergyHero: some View {
        let score = todayEnergyScore
        let headline = todayDayTypeHeadline
        let fusionSnapshot = dashboard.fusionScores ?? store.fusionIndex?.scores
        return VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s2) {
            Text(TodayExperienceChromeCopy.todayEyebrow)
                .font(.todayFlowEyebrow)
                .foregroundStyle(TodayFlowTheme.sand)
                .tracking(1.1)
            Text(headline)
                .font(.todayFlowRitualHeroTitle)
                .foregroundStyle(TodayFlowTheme.ink)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityAddTraits(.isHeader)
            Text(heroSummaryLine)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                .fixedSize(horizontal: false, vertical: true)
            if let fs = fusionSnapshot {
                HStack(spacing: 10) {
                    fusionAxisChip(title: TodayExperienceChromeCopy.energy, value: fs.energy, tint: TodayFlowTheme.sunset)
                    fusionAxisChip(title: TodayExperienceChromeCopy.balance, value: fs.emotionalBalance, tint: TodayFlowTheme.moss)
                    fusionAxisChip(title: TodayExperienceChromeCopy.focus, value: fs.focus, tint: TodayFlowTheme.twilight)
                }
            }
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Text("\(score)")
                    .font(.todayFlowHeroMetric)
                    .foregroundStyle(TodayFlowTheme.ink)
                VStack(alignment: .leading, spacing: 2) {
                    Text(TodayExperienceChromeCopy.of100)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.55))
                    Text(TodayExperienceChromeCopy.rhythmSummary)
                        .font(.caption2)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.45))
                }
                Spacer(minLength: 0)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(TodayExperienceChromeCopy.a11yRhythm) \(score) \(TodayExperienceChromeCopy.of100)")
            Button {
                heroInsightPresented = true
            } label: {
                HStack {
                    Text(TodayExperienceChromeCopy.whyDayFeels)
                    Image(systemName: "chevron.right.circle.fill")
                }
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, TodayFlowTheme.Layout.s1)
            }
            .buttonStyle(.plain)
            .background(
                LinearGradient(
                    colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .accessibilityHint(TodayExperienceChromeCopy.a11yWhyHint)
        }
        .todayFlowInset()
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 28)
    }

    private func fusionAxisChip(title: String, value: Int, tint: Color) -> some View {
        let v = min(100, max(0, value))
        return VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(title)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                Spacer(minLength: 4)
                Text("\(v)")
                    .font(.caption.weight(.bold))
                    .monospacedDigit()
                    .foregroundStyle(tint)
            }
            TodayFlowSphereSliderTrack(value: v, tint: tint, accessibilityTitle: title, density: .compact)
        }
        .frame(maxWidth: .infinity)
        .padding(10)
        .background(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(Color.white.opacity(0.42))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.14), lineWidth: 1)
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title) \(v) \(TodayExperienceChromeCopy.of100)")
    }

    private var heroSummaryLine: String {
        let g = dashboard.guidanceSummary.trimmingCharacters(in: .whitespacesAndNewlines)
        if !g.isEmpty { return g }
        let h = dashboard.headline.trimmingCharacters(in: .whitespacesAndNewlines)
        if !h.isEmpty { return h }
        if let s = cycle.morning?.dailyForecastSummary?.summary?.trimmingCharacters(in: .whitespacesAndNewlines), !s.isEmpty {
            return s
        }
        return TodayExperienceChromeCopy.heroFallback
    }

    private var todayEnergyScore: Int {
        let s = dashboard.fusionScores ?? store.fusionIndex?.scores
        if let s {
            return min(100, max(0, s.average))
        }
        return min(100, max(0, dashboard.contour.score))
    }

    private var todayDayTypeHeadline: String {
        if let m = cycle.morning?.dailyHoroscope?.spine?.bestMode, !m.isEmpty { return m }
        if let h = cycle.morning?.dailyHoroscope?.headline, !h.isEmpty { return h }
        return TodayExperienceChromeCopy.dayHeadlineFallback
    }

    // MARK: Block 2 — Today Theme

    private var block2Theme: some View {
        let lesson = lessonTitle
        let sub = lessonSubtitle
        return VStack(alignment: .leading, spacing: TodayFlowTheme.Layout.s2) {
            Text(TodayExperienceChromeCopy.meaningToday)
                .font(.todayFlowEyebrow)
                .foregroundStyle(TodayFlowTheme.sand)
            Text(lesson)
                .font(.todayFlowSectionTitle)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(sub)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.75))
            Button {
                onSelectTab(.questions)
            } label: {
                HStack {
                    Text(TodayExperienceChromeCopy.lookDeeper)
                    Image(systemName: "arrow.right.circle.fill")
                }
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, TodayFlowTheme.Layout.s1)
            }
            .buttonStyle(.plain)
            .background(
                LinearGradient(
                    colors: [TodayFlowTheme.sunset, TodayFlowTheme.ember],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .todayFlowInset()
        .frame(maxWidth: .infinity, alignment: .leading)
        .todayFlowSurfacePrimary(cornerRadius: 24)
    }

    private var lessonTitle: String {
        let t = todayDayTypeHeadline
        if t.contains("?") { return t }
        return "\(TodayExperienceChromeCopy.todayPrefix)\(t)"
    }

    private var lessonSubtitle: String {
        if let spine = cycle.morning?.dailyHoroscope?.spine, let m = spine.mainRisk, !m.isEmpty { return m }
        return TodayExperienceChromeCopy.lessonSubtitleFallback
    }

    // MARK: Block 3 — Card of the Day

    private var block3Tarot: some View {
        let rawName = cycle.morning?.tarotCard?.name ?? dashboard.tarotTitle
        let record = TodayTarotTodayRuCatalog.record(forCardName: cycle.morning?.tarotCard?.name, dateISO: cycle.date)
        let displayName = record?.nameRu ?? rawName
        let deckImageId = TodayTarotTodayRuCatalog.deckImageIdForDay(
            apiCardName: cycle.morning?.tarotCard?.name,
            dateISO: cycle.date
        )
        let faceURL = TodayTarotDeckImageURLs.deckFaceURL(cardId: deckImageId)
        return VStack(alignment: .leading, spacing: 10) {
            Text(TodayExperienceChromeCopy.cardOfDay)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            ZStack {
                tarotDeckBackFace(cornerRadius: 20)
                    .rotation3DEffect(.degrees(tarotFlipped ? 180 : 0), axis: (x: 0, y: 1, z: 0), anchor: .center, perspective: 0.42)
                    .opacity(tarotFlipped ? 0 : 1)
                tarotRevealedSide(displayName: displayName, record: record, faceURL: faceURL)
                    .background(
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .fill(
                                LinearGradient(
                                    colors: [Color.white.opacity(0.97), TodayFlowTheme.paper.opacity(0.92)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 20, style: .continuous)
                            .stroke(TodayFlowTheme.gold.opacity(0.22), lineWidth: 1)
                    )
                    .rotation3DEffect(.degrees(tarotFlipped ? 0 : -180), axis: (x: 0, y: 1, z: 0), anchor: .center, perspective: 0.42)
                    .opacity(tarotFlipped ? 1 : 0)
            }
            .frame(maxWidth: .infinity, minHeight: 248, maxHeight: 300)
            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        }
        .contentShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .onTapGesture {
            withAnimation(.spring(response: 0.5, dampingFraction: 0.8)) { tarotFlipped.toggle() }
        }
        .accessibilityLabel(tarotFlipped ? TodayExperienceChromeCopy.tarotA11yFaceUp : TodayExperienceChromeCopy.tarotA11yBack)
        .accessibilityHint(TodayExperienceChromeCopy.tarotA11yFlip)
    }

    @ViewBuilder
    private func tarotDeckBackFace(cornerRadius: CGFloat) -> some View {
        AsyncImage(url: TodayTarotDeckImageURLs.cardBackURL()) { phase in
            switch phase {
            case .success(let image):
                ZStack {
                    Color(red: 0.98, green: 0.96, blue: 0.93)
                    image
                        .resizable()
                        .scaledToFit()
                }
            case .failure, .empty:
                TodayTarotCardBackView(cornerRadius: cornerRadius)
            @unknown default:
                TodayTarotCardBackView(cornerRadius: cornerRadius)
            }
        }
    }

    private func tarotRevealedSide(displayName: String, record: TodayTarotCardRuRecord?, faceURL: URL?) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 10) {
                if let faceURL {
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
                            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        case .failure, .empty:
                            Color.clear.frame(height: 0)
                        @unknown default:
                            Color.clear.frame(height: 0)
                        }
                    }
                }
                Text(displayName)
                    .font(.title3.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
                if let lead = record?.leadRu.trimmingCharacters(in: .whitespacesAndNewlines), !lead.isEmpty {
                    Text(lead)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .fixedSize(horizontal: false, vertical: true)
                }
                Text(TodayExperienceChromeCopy.deeper)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.sand)
                    .padding(.top, 4)
                Text(TodayExperienceChromeCopy.firstMove(cycle.morning?.dailyHoroscope?.spine?.firstMove ?? TodayExperienceChromeCopy.firstMoveFallback))
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                Text(TodayExperienceChromeCopy.caution(cycle.morning?.dailyHoroscope?.spine?.doNotEnter ?? TodayExperienceChromeCopy.cautionFallback))
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                Text(TodayExperienceChromeCopy.todayDo(cycle.morning?.dailyRecommendations?.whatToDo ?? TodayExperienceChromeCopy.todayDoFallback))
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.78))
                Button { onSelectTab(.questions) } label: {
                    Text(TodayExperienceChromeCopy.fullGuidanceCta)
                        .font(.footnote.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
            .todayFlowInset(TodayFlowTheme.Layout.insetTight)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    // MARK: Block 4 — Number of the Day

    private var block4Number: some View {
        let reduced = cycle.morning?.numerologyNumber?.reducedValue
        let raw = cycle.morning?.numerologyNumber?.value
        let titleLine = cycle.morning?.numerologyNumber?.title ?? dashboard.numerologyTitle
        let (luckyT, color, stone, sym) = luckyPicks
        return VStack(alignment: .leading, spacing: 10) {
            Text(TodayExperienceChromeCopy.numberOfDay)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            TodayNumerologyDayPosterView(
                reducedNumber: reduced,
                rawValue: raw,
                titleLine: titleLine,
                dateLabel: numerologyDateLabel,
                luckyTime: TodayExperienceChromeCopy.luckyWindow(luckyT),
                colorName: TodayExperienceChromeCopy.colorLine(color),
                stone: TodayExperienceChromeCopy.stoneLine(stone),
                symbol: TodayExperienceChromeCopy.elementLine(sym)
            )
        }
        .todayFlowInset()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color.white.opacity(0.88), TodayFlowTheme.mist.opacity(0.65)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
        )
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
        }
    }

    private var numerologyDateLabel: String {
        let inFmt = DateFormatter()
        inFmt.calendar = Calendar(identifier: .gregorian)
        inFmt.locale = Locale(identifier: "en_US_POSIX")
        inFmt.dateFormat = "yyyy-MM-dd"
        guard let d = inFmt.date(from: cycle.date) else { return cycle.date }
        let out = DateFormatter()
        out.locale = Locale(identifier: IOSAppLocale.prefersRussian ? "ru_RU" : "en_US")
        out.dateFormat = "EEEE, d MMMM"
        return out.string(from: d).capitalized
    }

    private var luckyPicks: (String, String, String, String) {
        let seed = abs(cycle.date.hashValue)
        let windows = TodayExperienceChromeCopy.luckyPresets
        return windows[seed % windows.count]
    }

    // MARK: Block 5 — 6 rings

    private var block5Rings: some View {
        let rings = normalizedSixRings
        return VStack(alignment: .leading, spacing: 10) {
            Text(TodayExperienceChromeCopy.ringsTitle)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(TodayExperienceChromeCopy.ringsSubtitle)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.65))
            SixRingsGrid(rings: rings) { ring in
                selectedRing = ring
                Task {
                    await store.trackTodaySurfaceEvent(
                        eventType: "today_ring_open",
                        payload: [
                            "ring": .string(ring.ring),
                            "score": .number(Double(ring.score)),
                        ]
                    )
                }
            }
        }
    }

    private var normalizedSixRings: [MeaningRingItem] {
        let spec: [(String, String)] = [
            ("love", TodayExperienceChromeCopy.ringLove),
            ("wealth", TodayExperienceChromeCopy.ringWealth),
            ("discipline", TodayExperienceChromeCopy.ringDiscipline),
            ("emotional_balance", TodayExperienceChromeCopy.ringEmotion),
            ("purpose", TodayExperienceChromeCopy.ringPurpose),
            ("self_worth", TodayExperienceChromeCopy.ringSelf),
        ]
        var out: [MeaningRingItem] = []
        for (idx, (key, ru)) in spec.enumerated() {
            if let hit = store.meaningRings.first(where: { $0.ring.lowercased() == key || $0.ring == key }) {
                out.append(hit)
            } else {
                let v = 50 + (abs(cycle.date.hashValue) + idx * 7) % 40
                out.append(MeaningRingItem(ring: key, score: v, trend7d: 0, confidence: "demo", topContributors: [ru]))
            }
        }
        return out
    }

    // MARK: Block 6 — Practices

    private var block6Practices: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(TodayExperienceChromeCopy.practicesTitle)
                .font(.subheadline.weight(.semibold))
            ForEach(Array(dashboard.actionItems.enumerated()), id: \.offset) { _, line in
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: "arrow.up.right.circle.fill")
                        .foregroundStyle(TodayFlowTheme.sunset.opacity(0.7))
                    VStack(alignment: .leading, spacing: 4) {
                        Text(line)
                            .font(.footnote.weight(.semibold))
                        Text(ringDeltaHint(for: line))
                            .font(.caption2)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.5))
                    }
                }
            }
        }
        .todayFlowInsetTight()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func ringDeltaHint(for line: String) -> String {
        let l = line.lowercased()
        if l.contains("вод") || l.contains("water") { return TodayExperienceChromeCopy.ringHintWater }
        if l.contains("тел") || l.contains("движ") || l.contains("move") || l.contains("body") { return TodayExperienceChromeCopy.ringHintBody }
        if l.contains("ден") || l.contains("трат") || l.contains("money") || l.contains("spend") { return TodayExperienceChromeCopy.ringHintMoney }
        return TodayExperienceChromeCopy.ringHintDefault
    }

    // MARK: Block 7 — Ritual

    private var block7Ritual: some View {
        VStack(alignment: .leading, spacing: 12) {
            ritualRow(TodayExperienceChromeCopy.ritualAffirmation, cycle.consistency?.summary ?? TodayExperienceChromeCopy.ritualAffirmationFallback, nil)
            ritualRow(TodayExperienceChromeCopy.ritualAscetic, TodayExperienceChromeCopy.ritualAsceticBody, nil)
            ritualRow(TodayExperienceChromeCopy.ritualPractice, TodayExperienceChromeCopy.ritualPracticeBody, nil)
            ritualRow(TodayExperienceChromeCopy.ritualJournal, TodayExperienceChromeCopy.ritualJournalBody, nil)
            ritualRow(TodayExperienceChromeCopy.ritualRite, TodayExperienceChromeCopy.ritualRiteBody, nil)
        }
        .todayFlowInsetTight()
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(LinearGradient(colors: [Color.white.opacity(0.9), TodayFlowTheme.paper.opacity(0.75)], startPoint: .top, endPoint: .bottom))
        )
        .overlay { RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(TodayFlowTheme.gold.opacity(0.18), lineWidth: 1) }
    }

    private func ritualRow(_ title: String, _ value: String, _ _: String?) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.sand)
            Text(value)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
        }
    }

    // MARK: Block 8 — Micro reflection

    private var block8MicroQuestion: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(TodayExperienceChromeCopy.microTitle)
                .font(.subheadline.weight(.semibold))
            Text(TodayExperienceChromeCopy.microPrompt)
                .font(.footnote)
            let opts = TodayExperienceChromeCopy.microOptions
            VStack(alignment: .leading, spacing: 8) {
                ForEach(opts, id: \.self) { o in
                    Button {
                        withAnimation(.spring) {
                            microAnswer = o
                            showMicroReward = true
                        }
                        DispatchQueue.main.asyncAfter(deadline: .now() + 1.2) { showMicroReward = false }
                        Task {
                            await store.trackTodaySurfaceEvent(
                                eventType: "today_micro_reflection",
                                payload: ["answer": .string(o)]
                            )
                        }
                    } label: {
                        HStack {
                            Text(o)
                            Spacer()
                            if microAnswer == o { Image(systemName: "checkmark.circle.fill").foregroundStyle(TodayFlowTheme.sunset) }
                        }
                        .padding(TodayFlowTheme.Layout.s1)
                        .background(
                            RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(microAnswer == o ? TodayFlowTheme.sunset.opacity(0.12) : Color.white.opacity(0.5))
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            if showMicroReward, microAnswer != nil {
                Text(TodayExperienceChromeCopy.microReward)
                    .font(.caption2)
                    .foregroundStyle(TodayFlowTheme.moss)
                    .transition(.opacity)
            }
        }
        .todayFlowInsetTight()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.66))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    // MARK: Block 9 — Quick habits

    private var block9Habits: some View {
        let items: [(String, String)] = [
            ("water", TodayExperienceChromeCopy.habitWater),
            ("move", TodayExperienceChromeCopy.habitMove),
            ("reflect", TodayExperienceChromeCopy.habitReflect),
            ("work", TodayExperienceChromeCopy.habitWork),
            ("spend", TodayExperienceChromeCopy.habitSpend),
        ]
        return VStack(alignment: .leading, spacing: 8) {
            Text(TodayExperienceChromeCopy.habitsTitle)
                .font(.subheadline.weight(.semibold))
            ForEach(items, id: \.0) { k, t in
                Button {
                    if habitKeys.contains(k) { habitKeys.remove(k) } else { habitKeys.insert(k) }
                    Task {
                        await store.trackTodaySurfaceEvent(
                            eventType: "today_habit_toggle",
                            qualityScore: 0.7,
                            payload: [
                                "habit": .string(k),
                                "enabled": .bool(habitKeys.contains(k)),
                                "progress": .number(Double(habitKeys.count) / 5.0),
                            ]
                        )
                    }
                } label: {
                    HStack {
                        Image(systemName: habitKeys.contains(k) ? "checkmark.square.fill" : "square")
                            .foregroundStyle(habitKeys.contains(k) ? TodayFlowTheme.sunset : TodayFlowTheme.ink.opacity(0.35))
                        Text(t)
                            .foregroundStyle(TodayFlowTheme.ink)
                        Spacer()
                    }
                    .padding(TodayFlowTheme.Layout.s1)
                }
                .buttonStyle(.plain)
            }
            ProgressView(value: Double(habitKeys.count), total: 5.0)
                .tint(TodayFlowTheme.sunset)
        }
        .padding(TodayFlowTheme.Layout.s1)
        .background(Color.white.opacity(0.64))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    // MARK: Block 10

    private var block10Compatibility: some View {
        CTAChipsCard(
            title: TodayExperienceChromeCopy.compatTitle,
            text: TodayExperienceChromeCopy.compatBody,
            cta: TodayExperienceChromeCopy.compatCta,
            action: { onSelectTab(.compatibility) }
        )
    }

    private var block11Guidance: some View {
        CTAChipsCard(
            title: TodayExperienceChromeCopy.guidTitle,
            text: TodayExperienceChromeCopy.guidBody,
            cta: TodayExperienceChromeCopy.guidCta,
            action: { onSelectTab(.questions) }
        )
    }

    private var block12Diary: some View {
        CTAChipsCard(
            title: TodayExperienceChromeCopy.diaryTitle,
            text: TodayExperienceChromeCopy.diaryBody,
            cta: TodayExperienceChromeCopy.diaryCta,
            action: { onSelectTab(.calendar) }
        )
    }

    private var block13Tomorrow: some View {
        CTAChipsCard(
            title: TodayExperienceChromeCopy.tomorrowTitle,
            text: TodayExperienceChromeCopy.tomorrowBody,
            cta: TodayExperienceChromeCopy.tomorrowCta,
            action: { onSelectTab(.today) }
        )
    }

    private func storageKey(_ suffix: String) -> String {
        "todayflow.today.surface.\(suffix).\(cycle.date)"
    }

    private func loadLocalStateIfNeeded() {
        guard !didLoadLocalState else { return }
        didLoadLocalState = true
        let defaults = UserDefaults.standard
        if let answer = defaults.string(forKey: storageKey("microAnswer")), !answer.isEmpty {
            microAnswer = answer
        }
        if let items = defaults.array(forKey: storageKey("habits")) as? [String] {
            habitKeys = Set(items)
        }
    }

    private func persistMicroAnswer() {
        let defaults = UserDefaults.standard
        let key = storageKey("microAnswer")
        if let microAnswer, !microAnswer.isEmpty {
            defaults.set(microAnswer, forKey: key)
        } else {
            defaults.removeObject(forKey: key)
        }
    }

    private func persistHabitKeys() {
        UserDefaults.standard.set(Array(habitKeys).sorted(), forKey: storageKey("habits"))
    }
}

// MARK: - Sheets

private struct TodayHeroInsightSheet: View {
    let cycle: TodayCycle
    let dashboard: TodayDashboard
    let natalChart: NatalChartPreview?
    let fusion: FusionIndex?
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    if let chart = natalChart {
                        Text(TodayExperienceChromeCopy.sheetNatal)
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.sand)
                        NatalChartWheelView(chart: chart, layout: .compact)
                            .frame(maxWidth: .infinity)
                            .frame(height: 240)
                            .padding(8)
                            .background(
                                RoundedRectangle(cornerRadius: 22, style: .continuous)
                                    .fill(Color.white.opacity(0.55))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 22, style: .continuous)
                                    .stroke(TodayFlowTheme.gold.opacity(0.18), lineWidth: 1)
                            )
                    }
                    item(TodayExperienceChromeCopy.sheetMeaning, dashboard.headline)
                    item(
                        TodayExperienceChromeCopy.sheetMoon,
                        natalChart.flatMap { ZodiacSignRU.planetLine($0, body: "moon") } ?? TodayExperienceChromeCopy.sheetMoonFallback
                    )
                    item(
                        TodayExperienceChromeCopy.sheetFirstMove,
                        cycle.morning?.dailyHoroscope?.spine?.firstMove ?? TodayExperienceChromeCopy.sheetFirstMoveFallback
                    )
                    item(TodayExperienceChromeCopy.sheetRisk, dashboard.riskNote)
                    item(TodayExperienceChromeCopy.sheetBody, fusion?.encouragement ?? TodayExperienceChromeCopy.sheetBodyFallback)
                }
                .todayFlowInset()
            }
            .navigationTitle(TodayExperienceChromeCopy.sheetWhyTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(TodayExperienceChromeCopy.sheetDone) { dismiss() }
                }
            }
        }
    }
    private func item(_ t: String, _ v: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(t).font(.caption2.weight(.semibold)).foregroundStyle(TodayFlowTheme.sand)
            Text(v).font(.body).foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
        }
    }
}

private struct TodayRingDetailSheet: View {
    let ring: MeaningRingItem
    var onOpenGuidance: () -> Void
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 12) {
                Text(TodayExperienceChromeCopy.ringSheetHeadline(ringGridLabel(for: ring.ring)))
                    .font(.headline)
                Text(
                    TodayExperienceChromeCopy.ringSheetBody(
                        ring.score,
                        ring.topContributors.isEmpty
                            ? TodayExperienceChromeCopy.ringSheetTailEmpty
                            : TodayExperienceChromeCopy.ringSheetTailFactors(ring.topContributors.joined(separator: ", "))
                    )
                )
                    .font(.subheadline)
                Button {
                    onOpenGuidance()
                    dismiss()
                } label: {
                    Text(TodayExperienceChromeCopy.ringAskGuidance)
                        .font(.subheadline.weight(.semibold))
                        .frame(maxWidth: .infinity)
                        .padding(TodayFlowTheme.Layout.s1)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.sunset)
            }
            .todayFlowInset()
            .frame(maxWidth: .infinity, alignment: .leading)
            .navigationTitle(TodayExperienceChromeCopy.ringSheetTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button(TodayExperienceChromeCopy.ringSheetClose) { dismiss() } } }
        }
    }
    private func ringGridLabel(for key: String) -> String {
        switch key.lowercased() {
        case "love", "romance", "closeness": return TodayExperienceChromeCopy.gridLove
        case "wealth", "money": return TodayExperienceChromeCopy.gridWealth
        case "discipline", "work": return TodayExperienceChromeCopy.gridDiscipline
        case "emotional_balance", "emotion", "mood": return TodayExperienceChromeCopy.gridEmotion
        case "purpose": return TodayExperienceChromeCopy.gridPurpose
        case "self_worth", "selfworth": return TodayExperienceChromeCopy.gridSelf
        default: return key
        }
    }
}

// MARK: - 6 rings grid

private struct SixRingsGrid: View {
    let rings: [MeaningRingItem]
    var onTap: (MeaningRingItem) -> Void

    var body: some View {
        let cols = [GridItem(.adaptive(minimum: 100), spacing: 12, alignment: .top)]
        LazyVGrid(columns: cols, spacing: 14) {
            ForEach(rings) { ring in
                Button { onTap(ring) } label: {
                    ringSliderCell(for: ring)
                }
                .buttonStyle(.plain)
            }
        }
    }

    @ViewBuilder
    private func ringSliderCell(for ring: MeaningRingItem) -> some View {
        let label = shortLabel(for: ring.ring)
        let tint = TodayFlowMeaningRingAccent.color(for: ring.ring)
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(label)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer(minLength: 6)
                Text("\(ring.score)%")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                    .monospacedDigit()
            }
            TodayFlowSphereSliderTrack(
                value: ring.score,
                tint: tint,
                accessibilityTitle: label,
                density: .compact
            )
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.42))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(TodayFlowTheme.gold.opacity(0.12), lineWidth: 1)
        )
    }

    private func shortLabel(for key: String) -> String {
        switch key.lowercased() {
        case "love", "romance", "closeness": return TodayExperienceChromeCopy.gridLove
        case "wealth", "money": return TodayExperienceChromeCopy.gridWealth
        case "discipline", "work", "order": return TodayExperienceChromeCopy.gridDiscipline
        case "emotional_balance", "emotion", "mood": return TodayExperienceChromeCopy.gridEmotion
        case "purpose", "path": return TodayExperienceChromeCopy.gridPurpose
        case "self_worth", "selfworth", "esteem": return TodayExperienceChromeCopy.gridSelf
        default: return String(key.prefix(4)).uppercased()
        }
    }
}

private struct CTAChipsCard: View {
    let title: String
    let text: String
    let cta: String
    let action: () -> Void
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.subheadline.weight(.semibold))
            Text(text)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
            Button(action: action) {
                Text(cta)
                    .font(.subheadline.weight(.semibold))
                    .frame(maxWidth: .infinity)
                    .padding(TodayFlowTheme.Layout.s1)
            }
            .buttonStyle(.bordered)
            .tint(TodayFlowTheme.sunset)
        }
        .todayFlowInsetTight()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.68))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }
}
