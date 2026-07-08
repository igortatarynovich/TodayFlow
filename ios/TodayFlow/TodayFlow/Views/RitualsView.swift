import SwiftUI

struct CalendarView: View {
    let store: TodayFlowStore
    var onOpenGoals: (() -> Void)? = nil

    @State private var newHabitTitle = ""
    @State private var habitTemplateCategoryId = HabitTemplateCatalog.groups.first?.category.id ?? "morning"
    @State private var habitCadenceIsDaily = true
    @State private var habitWeeklyTarget = 4
    @State private var diaryNoticed = ""
    @State private var diaryHardest = ""
    @State private var diaryEasier = ""
    @FocusState private var habitCreateFieldFocused: Bool
    @State private var showGoalQuickSheet = false
    @State private var goalQuickTitle = ""
    @State private var goalQuickScope: GoalScope = .week
    @State private var showAsceticQuickSheet = false

    private let streakPresentationOrder = [
        "goal",
        "state_phases",
        "practice",
        "habits",
        "daily_signals",
        "ritual",
        "diary",
        "affirmation"
    ]

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollViewReader { scrollProxy in
                ScrollView(showsIndicators: false) {
                    VStack(spacing: 18) {
                    if let warning = AppConfig.runtimeConnectionWarning {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(FlowTrackerChrome.connectionHeader)
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(warning)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                        }
                        .padding(18)
                        .todayFlowCard()
                    }

                    if store.isBootstrapping && store.calendar.days.isEmpty {
                        HStack(spacing: 12) {
                            ProgressView()
                                .tint(TodayFlowTheme.accent)
                            Text(FlowTrackerChrome.loadingBootstrap)
                                .font(.subheadline.weight(.medium))
                                .foregroundStyle(TodayFlowTheme.ink.opacity(0.74))
                        }
                        .padding(18)
                        .todayFlowCard()
                    }

                    if let error = store.lastError, store.calendar.days.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            Text(FlowTrackerChrome.calendarFailed)
                                .font(.headline)
                                .foregroundStyle(TodayFlowTheme.ink)
                            Text(error)
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            Button(FlowTrackerChrome.retry) {
                                Task { await store.refreshAll() }
                            }
                            .buttonStyle(.borderedProminent)
                            .tint(TodayFlowTheme.accent)
                        }
                        .padding(18)
                        .todayFlowCard()
                    }

                    monthNavigator
                    streakRibbon
                    calendarHero
                    calendarGrid
                    selectedDayDetails
                    trackingFooter
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 22)
                }
                .onAppear {
                    flushPendingTrackerQuickCreate(scrollProxy: scrollProxy)
                }
                .onChange(of: store.pendingTrackerQuickCreate) { _, kind in
                    guard kind != nil else { return }
                    flushPendingTrackerQuickCreate(scrollProxy: scrollProxy)
                }
            }
        }
        .navigationTitle(FlowTrackerChrome.navFlow)
        .todayflowNavigationBarTitleDisplayModeLarge()
        .toolbar {
            ToolbarItem(placement: TodayFlowToolbar.trailing) {
                if store.isRefreshingCalendar {
                    ProgressView()
                } else {
                    Button {
                        Task { await store.refreshCalendar() }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .refreshable {
            await store.refreshCalendar()
            await store.refreshAffirmationProgressForSelectedDay()
            await store.refreshProgressSurfaces()
        }
        .task {
            if store.calendar.days.isEmpty && !store.isRefreshingCalendar && !store.isBootstrapping {
                await store.refreshCalendar()
            }
            if store.goals.isEmpty && !store.isRefreshingGoals {
                await store.refreshGoals()
            }
            await store.prepareAffirmationsForCalendar()
            await store.refreshProgressSurfaces()
        }
        .task(id: store.selectedCalendarDateISO) {
            await store.refreshAffirmationProgressForSelectedDay()
            await store.refreshProgressSurfaces()
            populateDiaryDraft()
        }
        .alert(FlowTrackerChrome.trackerAlertTitle, isPresented: Binding(
            get: { store.lastError != nil },
            set: { newValue in
                if !newValue { store.lastError = nil }
            }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(store.lastError ?? "")
        }
        .sheet(isPresented: $showGoalQuickSheet) {
            NavigationStack {
                GoalQuickCreateForm(
                    store: store,
                    title: $goalQuickTitle,
                    scope: $goalQuickScope,
                    onDismiss: { showGoalQuickSheet = false }
                )
                .navigationTitle(FlowTrackerChrome.goalSheetTitle)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button(FlowTrackerChrome.close) { showGoalQuickSheet = false }
                    }
                }
            }
            .presentationDetents([.medium, .large])
        }
        .sheet(isPresented: $showAsceticQuickSheet) {
            AsceticQuickCreateSheet(store: store, startDateISO: store.selectedCalendarDateISO) {
                showAsceticQuickSheet = false
            }
            .presentationDetents([.medium, .large])
        }
    }

    /// Intent может быть выставлен до появления вкладки Flow — обрабатываем и в `onAppear`, и в `onChange`.
    private func flushPendingTrackerQuickCreate(scrollProxy: ScrollViewProxy) {
        guard let kind = store.pendingTrackerQuickCreate else { return }
        store.pendingTrackerQuickCreate = nil
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            switch kind {
            case .habit:
                withAnimation(.easeInOut(duration: 0.35)) {
                    scrollProxy.scrollTo("flowQuickHabit", anchor: .center)
                }
                habitCreateFieldFocused = true
            case .goal:
                goalQuickTitle = ""
                goalQuickScope = .week
                showGoalQuickSheet = true
            case .ascetic:
                showAsceticQuickSheet = true
            }
        }
    }

    private var monthNavigator: some View {
        HStack(spacing: 16) {
            Button {
                Task { await store.shiftCalendarMonth(by: -1) }
            } label: {
                Image(systemName: "chevron.left.circle.fill")
                    .font(.title2)
                    .symbolRenderingMode(.hierarchical)
                    .foregroundStyle(TodayFlowTheme.accent)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text(store.calendar.monthTitle)
                    .font(.system(size: 22, weight: .bold, design: .rounded))
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(FlowTrackerChrome.monthSubtitle)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Button {
                Task { await store.shiftCalendarMonth(by: 1) }
            } label: {
                Image(systemName: "chevron.right.circle.fill")
                    .font(.title2)
                    .symbolRenderingMode(.hierarchical)
                    .foregroundStyle(TodayFlowTheme.accent)
            }
        }
        .padding(18)
        .todayFlowCard()
        .shadow(color: Color.black.opacity(0.07), radius: 18, x: 0, y: 10)
    }

    private var streakRibbon: some View {
        let items = streakPresentationOrder.compactMap { key -> StreakItem? in
            guard let value = store.calendar.streaks[key], value > 0 else { return nil }
            return StreakItem(key: key, count: value, title: FlowTrackerChrome.streakTitle(for: key), symbol: streakSymbol(for: key))
        }

        return Group {
            if !items.isEmpty {
                VStack(alignment: .leading, spacing: 12) {
                    Text(FlowTrackerChrome.streaksNow)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .textCase(.uppercase)
                        .tracking(0.5)

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(items) { item in
                                StreakRingCard(item: item)
                            }
                        }
                    }
                }
                .padding(18)
                .todayFlowCard()
                .shadow(color: Color.black.opacity(0.06), radius: 16, x: 0, y: 8)
            }
        }
    }

    private var calendarHero: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.monthStatsTitle)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            HStack(spacing: 12) {
                statCard(title: FlowTrackerChrome.statGoalDays, value: store.calendar.monthSummary["days_with_goal_step"] ?? 0)
                statCard(title: FlowTrackerChrome.statHabitDays, value: store.calendar.monthSummary["days_with_habits"] ?? 0)
                statCard(title: FlowTrackerChrome.statFullCheckins, value: store.calendar.monthSummary["days_full_state_checkins"] ?? 0)
            }
        }
        .padding(20)
        .todayFlowCard()
        .shadow(color: Color.black.opacity(0.06), radius: 16, x: 0, y: 8)
    }

    private var calendarGrid: some View {
        let columns = Array(repeating: GridItem(.flexible(), spacing: 10), count: 7)
        return VStack(alignment: .leading, spacing: 14) {
            Text(FlowTrackerChrome.monthMapTitle)
                .font(.title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)

            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(weekdayHeaders, id: \.self) { header in
                    Text(header)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .frame(maxWidth: .infinity)
                }

                ForEach(gridCells) { cell in
                    if let day = cell.day {
                        dayCell(day)
                    } else {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(Color.white.opacity(0.2))
                            .frame(minHeight: 52)
                    }
                }
            }
        }
        .padding(18)
        .todayFlowCard()
        .shadow(color: Color.black.opacity(0.05), radius: 14, x: 0, y: 7)
    }

    private func dayCell(_ day: TrackerDaySummary) -> some View {
        Button {
            store.selectCalendarDate(day.dateISO)
        } label: {
            VStack(spacing: 6) {
                Text(day.dayNumber)
                    .font(.system(size: 16, weight: .semibold, design: .rounded))
                ZStack {
                    Circle()
                        .stroke(TodayFlowTheme.contour, lineWidth: 1.5)
                        .frame(width: 22, height: 22)
                    Circle()
                        .trim(from: 0, to: max(0.02, dayRingProgress(day)))
                        .stroke(
                            day.completionCount >= 3 ? TodayFlowTheme.accent : TodayFlowTheme.sage,
                            style: StrokeStyle(lineWidth: 3, lineCap: .round)
                        )
                        .rotationEffect(.degrees(-90))
                        .frame(width: 22, height: 22)
                    if day.completionCount == 0 {
                        Circle()
                            .fill(Color.clear)
                            .frame(width: 6, height: 6)
                    }
                }
            }
            .foregroundStyle(day.isToday ? Color.white : TodayFlowTheme.ink)
            .frame(maxWidth: .infinity, minHeight: 52)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(backgroundColor(for: day))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(day.dateISO == store.selectedCalendarDateISO ? TodayFlowTheme.accent : Color.clear, lineWidth: 2)
            )
        }
        .buttonStyle(LuxeCalendarDayButtonStyle())
    }

    private var gridCells: [CalendarGridCell] {
        let days = store.calendar.days.sorted { $0.dateISO < $1.dateISO }
        guard let first = days.first, let firstDate = parseISODate(first.dateISO) else {
            return days.map { CalendarGridCell(id: $0.dateISO, day: $0) }
        }
        let cal = Calendar.current
        let weekday = cal.component(.weekday, from: firstDate)
        let firstWeekday = cal.firstWeekday
        let padding = (weekday - firstWeekday + 7) % 7
        var cells: [CalendarGridCell] = (0..<padding).map { CalendarGridCell(id: "pad-\($0)", day: nil) }
        for d in days {
            cells.append(CalendarGridCell(id: d.dateISO, day: d))
        }
        while cells.count % 7 != 0 {
            cells.append(CalendarGridCell(id: "trail-\(cells.count)", day: nil))
        }
        return cells
    }

    private var selectedDayDetails: some View {
        let selected = store.calendar.days.first(where: { $0.dateISO == store.selectedCalendarDateISO })
        return VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text(FlowTrackerChrome.selectedDay)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                Text(FlowTrackerChrome.dayTracker)
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.accent)
            }

            if let selected {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(selected.weekdayTitle)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                        Text(prettySelectedDate(selected.dateISO))
                            .font(.headline)
                            .foregroundStyle(TodayFlowTheme.ink)
                    }
                    Spacer()
                    if let mood = selected.moodScore {
                        Label("\(mood)/5", systemImage: "waveform.path.ecg")
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.accent)
                    }
                }

                if selected.activities.isEmpty {
                    Text(FlowTrackerChrome.noMarksDay)
                        .font(.subheadline)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                } else {
                    ForEach(selected.activities) { activity in
                        HStack(alignment: .top, spacing: 10) {
                            Image(systemName: activity.isComplete ? "checkmark.circle.fill" : "circle")
                                .foregroundStyle(activity.isComplete ? TodayFlowTheme.accent : TodayFlowTheme.secondaryInk)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(activity.title)
                                    .font(.headline)
                                    .foregroundStyle(TodayFlowTheme.ink)
                                Text(activity.detail)
                                    .font(.subheadline)
                                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                            }
                            Spacer()
                        }
                        .padding(.vertical, 4)
                    }
                }

                habitsBlock
                asceticsBlock
                practiceBlock
                affirmationsBlock
                diaryBlock
                insightsBlock
                weeklyPulseBlock
            } else {
                Text(FlowTrackerChrome.pickDayOnMap)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(18)
        .todayFlowCard()
    }

    private var habitsBlock: some View {
        let active = store.calendar.habitTracks
            .filter(\.isActive)
            .sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }

        return VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.habitsTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(FlowTrackerChrome.habitsSyncNote)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            if active.isEmpty {
                Text(FlowTrackerChrome.habitsEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                ForEach(active) { habit in
                    Toggle(isOn: Binding(
                        get: {
                            store.calendar.habitTracks.first(where: { $0.id == habit.id })?
                                .isDone(on: store.selectedCalendarDateISO) ?? false
                        },
                        set: { completed in
                            Task {
                                await store.toggleHabit(
                                    habitID: habit.id,
                                    dateISO: store.selectedCalendarDateISO,
                                    completed: completed
                                )
                            }
                        }
                    )) {
                        Text(habit.name)
                            .font(.subheadline)
                    }
                    .tint(TodayFlowTheme.accent)
                    .disabled(store.isSaving)
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text(FlowTrackerChrome.newHabit)
                    .font(.footnote.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                let templateGroups = HabitTemplateCatalog.groups
                let activeGroup =
                    templateGroups.first(where: { $0.category.id == habitTemplateCategoryId }) ?? templateGroups[0]

                Text(FlowTrackerChrome.habitCategory)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk.opacity(0.9))
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(templateGroups) { group in
                            Button {
                                habitTemplateCategoryId = group.category.id
                            } label: {
                                Text(group.category.label)
                                    .font(.caption.weight(.semibold))
                            }
                            .buttonStyle(.bordered)
                            .tint(habitTemplateCategoryId == group.category.id ? TodayFlowTheme.accent : Color.secondary)
                        }
                    }
                }

                Text(FlowTrackerChrome.habitIdeas)
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk.opacity(0.9))
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(activeGroup.items) { item in
                            Button {
                                newHabitTitle = item.title
                            } label: {
                                VStack(alignment: .leading, spacing: 2) {
                                    Text(item.title)
                                        .font(.caption.weight(.semibold))
                                        .multilineTextAlignment(.leading)
                                    if let hint = item.hint {
                                        Text(hint)
                                            .font(.caption2)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                                .frame(maxWidth: 220, alignment: .leading)
                            }
                            .buttonStyle(.bordered)
                        }
                    }
                }

                Picker(FlowTrackerChrome.habitCadence, selection: $habitCadenceIsDaily) {
                    Text(FlowTrackerChrome.habitDaily).tag(true)
                    Text(FlowTrackerChrome.habitWeekly).tag(false)
                }
                .pickerStyle(.segmented)
                if !habitCadenceIsDaily {
                    Stepper(value: $habitWeeklyTarget, in: 2...7) {
                        Text(FlowTrackerChrome.habitWeekTarget(habitWeeklyTarget))
                            .font(.caption)
                    }
                }

                TextField(FlowTrackerChrome.nameFieldPlaceholder, text: $newHabitTitle)
                    .textFieldStyle(.plain)
                    .focused($habitCreateFieldFocused)
                    .padding(14)
                    .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .stroke(TodayFlowTheme.contour.opacity(0.55), lineWidth: 1)
                    )
                Button {
                    Task {
                        let cat = activeGroup.category.label
                        await store.createHabit(
                            name: newHabitTitle,
                            category: cat,
                            targetFrequency: habitCadenceIsDaily ? "daily" : "weekly",
                            targetPerPeriod: habitCadenceIsDaily ? 1 : habitWeeklyTarget
                        )
                        newHabitTitle = ""
                    }
                } label: {
                    Label(FlowTrackerChrome.create, systemImage: "plus.circle.fill")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.accent)
                .disabled(newHabitTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || store.isSaving)
            }
            .padding(.top, 4)
        }
        .padding(.top, 6)
        .id("flowQuickHabit")
    }

    private var asceticsBlock: some View {
        let loggable = store.calendar.asceticTracks
            .filter(\.allowsLogging)
            .sorted { $0.displayTitle.localizedCaseInsensitiveCompare($1.displayTitle) == .orderedAscending }

        return VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.asceticsTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(FlowTrackerChrome.asceticsSyncNote)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            if loggable.isEmpty {
                Text(FlowTrackerChrome.asceticsEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                ForEach(loggable) { track in
                    Toggle(isOn: Binding(
                        get: {
                            store.calendar.asceticTracks.first(where: { $0.asceticismId == track.asceticismId })?
                                .isDone(on: store.selectedCalendarDateISO) ?? false
                        },
                        set: { completed in
                            Task {
                                await store.toggleAscetic(
                                    asceticismId: track.asceticismId,
                                    dateISO: store.selectedCalendarDateISO,
                                    completed: completed
                                )
                            }
                        }
                    )) {
                        Text(track.displayTitle)
                            .font(.subheadline)
                    }
                    .tint(TodayFlowTheme.accent)
                    .disabled(store.isSaving)
                }
            }
        }
        .padding(.top, 10)
        .id("flowQuickAscetic")
    }

    private var practiceBlock: some View {
        let selected = store.calendar.days.first(where: { $0.dateISO == store.selectedCalendarDateISO })
        let practiceDone = selected?.activities.first(where: { $0.id == "practice" })?.isComplete ?? false

        return VStack(alignment: .leading, spacing: 10) {
            Text(FlowTrackerChrome.practiceTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if practiceDone {
                Label(FlowTrackerChrome.practiceDoneLabel, systemImage: "checkmark.circle.fill")
                    .font(.subheadline.weight(.medium))
                    .foregroundStyle(TodayFlowTheme.sage)
            } else {
                Text(FlowTrackerChrome.practiceHint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                Button {
                    Task {
                        await store.logPractice(dateISO: store.selectedCalendarDateISO)
                    }
                } label: {
                    Label(FlowTrackerChrome.logPractice, systemImage: "sparkles")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.ink)
                .disabled(store.isSaving)
            }
        }
        .padding(.top, 10)
    }

    private var affirmationsBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.affirmationsTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)
            Text(FlowTrackerChrome.affirmationsSyncNote)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            if store.affirmationsCatalog.isEmpty {
                Text(FlowTrackerChrome.affirmationsCatalogEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                ForEach(store.affirmationsCatalog) { item in
                    Toggle(isOn: Binding(
                        get: {
                            store.affirmationDoneById[item.id] ?? false
                        },
                        set: { completed in
                            Task {
                                await store.toggleAffirmation(
                                    affirmationId: item.id,
                                    dateISO: store.selectedCalendarDateISO,
                                    completed: completed
                                )
                            }
                        }
                    )) {
                        Text(item.displayLine)
                            .font(.subheadline)
                            .lineLimit(4)
                            .multilineTextAlignment(.leading)
                    }
                    .tint(TodayFlowTheme.accent)
                    .disabled(store.isSaving)
                }
            }
        }
        .padding(.top, 10)
    }

    private var diaryBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(FlowTrackerChrome.diaryTitle)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                if store.isRefreshingDiary {
                    ProgressView()
                        .tint(TodayFlowTheme.accent)
                }
            }

            Text(FlowTrackerChrome.diaryIntro)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            diaryField(title: FlowTrackerChrome.diaryNoticedTitle, text: $diaryNoticed, prompt: FlowTrackerChrome.diaryNoticedPrompt)
            diaryField(title: FlowTrackerChrome.diaryHardestTitle, text: $diaryHardest, prompt: FlowTrackerChrome.diaryHardestPrompt)
            diaryField(title: FlowTrackerChrome.diaryEasierTitle, text: $diaryEasier, prompt: FlowTrackerChrome.diaryEasierPrompt)

            Button {
                Task {
                    await store.saveObservationDiary(
                        noticed: diaryNoticed,
                        hardest: diaryHardest,
                        easierThanExpected: diaryEasier
                    )
                }
            } label: {
                Label(FlowTrackerChrome.saveDiary, systemImage: "square.and.arrow.down.fill")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.accent)
            .disabled(store.isSaving)

            if let entry = store.selectedDiaryEntry, entry.hasContent {
                VStack(alignment: .leading, spacing: 8) {
                    Text(FlowTrackerChrome.savedForDay)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .textCase(.uppercase)
                    diaryEntrySummary(entry)
                }
                .padding(.top, 4)
            }
        }
        .padding(.top, 10)
    }

    private var insightsBlock: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(FlowTrackerChrome.insightsTitle)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                if store.isRefreshingInsights {
                    ProgressView()
                        .tint(TodayFlowTheme.accent)
                }
            }

            Text(FlowTrackerChrome.insightsIntro)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)

            Button {
                Task {
                    await store.generateInsightForSelectedDay()
                }
            } label: {
                Label(store.isGeneratingInsight ? FlowTrackerChrome.generatingInsight : FlowTrackerChrome.generateInsight, systemImage: "sparkles.rectangle.stack.fill")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.bordered)
            .tint(TodayFlowTheme.ink)
            .disabled(store.isGeneratingInsight)

            if store.autoInsights.isEmpty {
                Text(FlowTrackerChrome.insightsEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                ForEach(store.autoInsights) { insight in
                    insightCard(insight)
                }
            }
        }
        .padding(.top, 10)
    }

    private var weeklyPulseBlock: some View {
        let slice = Array(store.fusionHistory.suffix(7))

        return VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.weeklyPulseTitle)
                .font(.headline)
                .foregroundStyle(TodayFlowTheme.ink)

            if slice.isEmpty {
                Text(FlowTrackerChrome.weeklyPulseEmpty)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                HStack(spacing: 10) {
                    rhythmMetric(title: FlowTrackerChrome.energy, value: slice.map(\.scores.energy).reduce(0, +) / slice.count, tint: TodayFlowTheme.sunset)
                    rhythmMetric(title: FlowTrackerChrome.balance, value: slice.map(\.scores.emotionalBalance).reduce(0, +) / slice.count, tint: TodayFlowTheme.moss)
                    rhythmMetric(title: FlowTrackerChrome.focus, value: slice.map(\.scores.focus).reduce(0, +) / slice.count, tint: TodayFlowTheme.twilight)
                }

                Text(slice.last?.encouragement ?? FlowTrackerChrome.rhythmEncouragementFallback)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
        }
        .padding(.top, 10)
    }

    private var trackingFooter: some View {
        HStack(spacing: 12) {
            Button {
                onOpenGoals?()
            } label: {
                Label(FlowTrackerChrome.openGoals, systemImage: "scope")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.ink)
            .disabled(onOpenGoals == nil)

            Text(FlowTrackerChrome.trackingFooter)
                .font(.footnote)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func statCard(title: String, value: Int) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text("\(value)")
                .font(.title2.bold())
                .foregroundStyle(TodayFlowTheme.ink)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.contour.opacity(0.6), lineWidth: 1)
        )
    }

    private func backgroundColor(for day: TrackerDaySummary) -> Color {
        if day.isToday {
            return TodayFlowTheme.accent
        }
        if day.dateISO == store.selectedCalendarDateISO {
            return TodayFlowTheme.accentSoft.opacity(0.55)
        }
        if !day.isInDisplayedMonth {
            return Color.white.opacity(0.35)
        }
        return TodayFlowTheme.cardStrong
    }

    private func dayRingProgress(_ day: TrackerDaySummary) -> Double {
        let c = day.completionCount
        if c <= 0 { return 0.08 }
        return min(1, Double(c) / 5)
    }

    private var weekdayHeaders: [String] {
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        guard let symbols = formatter.shortStandaloneWeekdaySymbols, symbols.count >= 7 else {
            return FlowTrackerChrome.weekdayFallback
        }
        let cal = Calendar.current
        let rotate = cal.firstWeekday - 1
        guard rotate > 0 else { return Array(symbols.prefix(7)) }
        let head = Array(symbols[rotate..<7])
        let tail = Array(symbols[0..<rotate])
        return head + tail
    }

    private func streakSymbol(for key: String) -> String {
        switch key {
        case "goal": return "scope"
        case "state_phases": return "sun.horizon.fill"
        case "practice": return "sparkles"
        case "habits": return "leaf.fill"
        case "daily_signals": return "dot.radiowaves.left.and.right"
        case "ritual": return "moon.stars.fill"
        case "diary": return "book.fill"
        case "affirmation": return "quote.bubble.fill"
        default: return "flame.fill"
        }
    }

    private func parseISODate(_ iso: String) -> Date? {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: iso)
    }

    private func prettySelectedDate(_ iso: String) -> String {
        guard let date = parseISODate(iso) else { return iso }
        let formatter = DateFormatter()
        formatter.locale = Locale.current
        formatter.setLocalizedDateFormatFromTemplate("EEEEdMMMM yyyy")
        return formatter.string(from: date)
    }

    private func populateDiaryDraft() {
        diaryNoticed = store.selectedDiaryEntry?.noticed ?? ""
        diaryHardest = store.selectedDiaryEntry?.hardest ?? ""
        diaryEasier = store.selectedDiaryEntry?.easierThanExpected ?? ""
    }

    private func diaryField(title: String, text: Binding<String>, prompt: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.footnote.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            TextField(prompt, text: text, axis: .vertical)
                .textFieldStyle(.plain)
                .lineLimit(2...4)
                .padding(14)
                .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .stroke(TodayFlowTheme.contour.opacity(0.55), lineWidth: 1)
                )
        }
    }

    private func diaryEntrySummary(_ entry: ObservationDiaryEntry) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            if !entry.noticed.isEmpty {
                summaryLine(title: FlowTrackerChrome.summaryNoticed, text: entry.noticed)
            }
            if !entry.hardest.isEmpty {
                summaryLine(title: FlowTrackerChrome.summaryHardest, text: entry.hardest)
            }
            if !entry.easierThanExpected.isEmpty {
                summaryLine(title: FlowTrackerChrome.summaryEasier, text: entry.easierThanExpected)
            }
        }
        .padding(14)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(TodayFlowTheme.contour.opacity(0.55), lineWidth: 1)
        )
    }

    private func summaryLine(title: String, text: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)
        }
    }

    private func insightCard(_ insight: AutoInsightItem) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(insight.typeTitle)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(confidenceColor(insight.confidence))
                    .textCase(.uppercase)
                Spacer()
                Text(insight.confidence.title)
                    .font(.caption2.weight(.medium))
                    .foregroundStyle(confidenceColor(insight.confidence))
            }

            Text(insight.text)
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.ink)

            if !insight.dataPoints.isEmpty {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                    ForEach(insight.dataPoints.keys.sorted(), id: \.self) { key in
                        VStack(alignment: .leading, spacing: 2) {
                            Text(key)
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            Text(insight.dataPoints[key] ?? "")
                                .font(.caption)
                                .foregroundStyle(TodayFlowTheme.ink)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(10)
                        .background(Color.white.opacity(0.65), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    }
                }
            }
        }
        .padding(14)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(confidenceColor(insight.confidence).opacity(0.35), lineWidth: 1)
        )
    }

    private func rhythmMetric(title: String, value: Int, tint: Color) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ZStack {
                Circle()
                    .stroke(tint.opacity(0.18), lineWidth: 6)
                Circle()
                    .trim(from: 0, to: max(0.05, min(1, Double(value) / 100)))
                    .stroke(tint, style: StrokeStyle(lineWidth: 6, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                Text("\(value)")
                    .font(.headline.monospacedDigit())
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            .frame(width: 64, height: 64)

            Text(title)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private func confidenceColor(_ confidence: InsightConfidence) -> Color {
        switch confidence {
        case .low: return TodayFlowTheme.sunset
        case .medium: return TodayFlowTheme.accent
        case .high: return TodayFlowTheme.moss
        }
    }
}

private struct LuxeCalendarDayButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
            .animation(.easeOut(duration: 0.14), value: configuration.isPressed)
    }
}

private struct CalendarGridCell: Identifiable, Hashable {
    let id: String
    let day: TrackerDaySummary?
}

private struct StreakItem: Identifiable, Hashable {
    let key: String
    let count: Int
    let title: String
    let symbol: String

    var id: String { key }
}

private struct StreakRingCard: View {
    let item: StreakItem

    private var ringAmount: Double {
        min(1, Double(item.count) / 14)
    }

    var body: some View {
        VStack(spacing: 10) {
            ZStack {
                Circle()
                    .stroke(TodayFlowTheme.accentSoft.opacity(0.5), lineWidth: 6)
                    .frame(width: 56, height: 56)
                Circle()
                    .trim(from: 0, to: max(0.05, ringAmount))
                    .stroke(TodayFlowTheme.accent, style: StrokeStyle(lineWidth: 6, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                    .frame(width: 56, height: 56)
                Image(systemName: item.symbol)
                    .font(.body.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
            }
            Text("\(item.count)")
                .font(.headline.monospacedDigit())
                .foregroundStyle(TodayFlowTheme.ink)
            Text(item.title)
                .font(.caption2.weight(.medium))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .frame(width: 88)
        }
        .padding(.vertical, 10)
        .padding(.horizontal, 8)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(TodayFlowTheme.contour, lineWidth: 1)
        )
    }
}

// MARK: - Goals (weekly / monthly steps)

struct GoalsView: View {
    let store: TodayFlowStore
    var onOpenCalendar: (() -> Void)? = nil

    @State private var newGoalTitle = ""
    @State private var goalScope: GoalScope = .week

    var body: some View {
        ZStack {
            TodayFlowScreenBackground()

            ScrollView(showsIndicators: false) {
                VStack(spacing: 18) {
                    selectedDayBanner
                    createGoalCard
                    goalsList
                    footer
                }
                .todayFlowContentContainer(maxWidth: 780, horizontal: 20, top: 10, bottom: 22)
            }
        }
        .navigationTitle(FlowTrackerChrome.goalsNavTitle)
        .todayflowNavigationBarTitleDisplayModeLarge()
        .toolbar {
            ToolbarItem(placement: TodayFlowToolbar.trailing) {
                if store.isRefreshingGoals {
                    ProgressView()
                } else {
                    Button {
                        Task { await store.refreshGoals() }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .refreshable {
            await store.refreshGoals()
        }
        .alert(FlowTrackerChrome.syncIssueTitle, isPresented: Binding(
            get: { store.lastError != nil },
            set: { newValue in
                if !newValue { store.lastError = nil }
            }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(store.lastError ?? "")
        }
    }

    private var selectedDayBanner: some View {
        HStack(alignment: .top, spacing: 14) {
            ZStack {
                Circle()
                    .stroke(TodayFlowTheme.sky.opacity(0.9), lineWidth: 3)
                    .frame(width: 48, height: 48)
                Image(systemName: "calendar.circle.fill")
                    .font(.title2)
                    .foregroundStyle(TodayFlowTheme.accent)
            }
            VStack(alignment: .leading, spacing: 6) {
                Text(FlowTrackerChrome.stepsForDay)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .textCase(.uppercase)
                Text(prettyDate(store.selectedCalendarDateISO))
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Text(FlowTrackerChrome.goalsPickDateHint)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .padding(16)
        .todayFlowCard()
    }

    private var createGoalCard: some View {
        let ref = store.selectedCalendarDateISO
        let weekStart = TodayFlowStore.weekStartMonday(fromLocalISO: ref)
        let monthStart = TodayFlowStore.monthAnchorIso(ref)
        let blocked = !store.canCreateGoal(scope: goalScope)
        return VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.newGoal)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            Text(goalScope == .week ? FlowTrackerChrome.weekFrom(weekStart) : FlowTrackerChrome.monthFrom(monthStart))
                .font(.caption.weight(.medium))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.75))
            if blocked {
                Text(FlowTrackerChrome.goalLimitReached)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            TextField(FlowTrackerChrome.nameFieldPlaceholder, text: $newGoalTitle)
                .textFieldStyle(.roundedBorder)
            Picker(FlowTrackerChrome.horizonPicker, selection: $goalScope) {
                ForEach(GoalScope.allCases) { scope in
                    Text(scope.title).tag(scope)
                }
            }
            .pickerStyle(.segmented)
            Button {
                Task {
                    let ok = await store.createGoal(title: newGoalTitle, scope: goalScope)
                    if ok { newGoalTitle = "" }
                }
            } label: {
                Text(FlowTrackerChrome.create)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.accent)
            .disabled(newGoalTitle.trimmingCharacters(in: .whitespacesAndNewlines).count < 2 || store.isSaving || blocked)
        }
        .padding(16)
        .todayFlowCard()
    }

    private var goalsList: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(FlowTrackerChrome.yourGoals)
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            if store.goals.isEmpty {
                Text(FlowTrackerChrome.noGoalsYet)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            } else {
                ForEach(store.goals) { goal in
                    goalRow(goal)
                }
            }
        }
        .padding(16)
        .todayFlowCard()
    }

    private func goalRow(_ goal: GoalTrack) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(goal.title)
                    .font(.headline)
                    .foregroundStyle(TodayFlowTheme.ink)
                Spacer()
                if goal.completed {
                    Text(FlowTrackerChrome.done)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.accent)
                }
            }
            ProgressView(value: goal.displayProgress)
                .tint(TodayFlowTheme.accent)
            HStack {
                Button {
                    Task {
                        await store.markGoalStep(goal: goal, dateISO: store.selectedCalendarDateISO)
                    }
                } label: {
                    Label(FlowTrackerChrome.markStep, systemImage: "checkmark.circle")
                }
                .buttonStyle(.bordered)
                .disabled(goal.completed || store.isSaving || goal.isStepped(on: store.selectedCalendarDateISO) || !goal.allowsStep(on: store.selectedCalendarDateISO))
                Spacer()
                Button {
                    Task {
                        await store.setGoalCompleted(goalID: goal.id, completed: !goal.completed)
                    }
                } label: {
                    Text(goal.completed ? FlowTrackerChrome.reopenGoal : FlowTrackerChrome.completeGoal)
                }
                .buttonStyle(.borderedProminent)
                .tint(TodayFlowTheme.ink)
                .disabled(store.isSaving)
            }
        }
        .padding(14)
        .background(TodayFlowTheme.cardStrong, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }

    private var footer: some View {
        Button {
            onOpenCalendar?()
        } label: {
            Label(FlowTrackerChrome.openCalendarForDay, systemImage: "calendar")
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
        .disabled(onOpenCalendar == nil)
    }

    private func prettyDate(_ iso: String) -> String {
        let parser = DateFormatter()
        parser.calendar = Calendar(identifier: .gregorian)
        parser.locale = Locale(identifier: "en_US_POSIX")
        parser.timeZone = TimeZone.current
        parser.dateFormat = "yyyy-MM-dd"
        guard let date = parser.date(from: iso) else { return iso }
        let out = DateFormatter()
        out.locale = Locale.current
        out.setLocalizedDateFormatFromTemplate("EEEEdMMMM yyyy")
        return out.string(from: date)
    }
}

// MARK: - Цель: быстрое создание (паритет с веб `EntityCreateWizard`)

private struct GoalQuickCreateForm: View {
    let store: TodayFlowStore
    @Binding var title: String
    @Binding var scope: GoalScope
    var onDismiss: () -> Void

    private var refISO: String { store.selectedCalendarDateISO }
    private var weekStart: String { TodayFlowStore.weekStartMonday(fromLocalISO: refISO) }
    private var monthStart: String { TodayFlowStore.monthAnchorIso(refISO) }
    private var goalBlocked: Bool { !store.canCreateGoal(scope: scope) }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(FlowTrackerChrome.newGoal)
                .font(.title3.weight(.semibold))
            Text(FlowTrackerChrome.goalQuickPeriodNote)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
            Text(scope == .week ? FlowTrackerChrome.weekFrom(weekStart) : FlowTrackerChrome.monthFrom(monthStart))
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
            if goalBlocked {
                Text(FlowTrackerChrome.goalLimitReached)
                    .font(.caption)
                    .foregroundStyle(TodayFlowTheme.sunset)
            }
            TextField(FlowTrackerChrome.nameFieldPlaceholder, text: $title)
                .textFieldStyle(.roundedBorder)
            Picker(FlowTrackerChrome.horizonPicker, selection: $scope) {
                ForEach(GoalScope.allCases) { s in
                    Text(s.title).tag(s)
                }
            }
            .pickerStyle(.segmented)
            Button {
                Task {
                    let ok = await store.createGoal(title: title, scope: scope, anchorDateISO: refISO)
                    if ok {
                        title = ""
                        onDismiss()
                    }
                }
            } label: {
                Text(FlowTrackerChrome.create)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(TodayFlowTheme.accent)
            .disabled(title.trimmingCharacters(in: .whitespacesAndNewlines).count < 2 || store.isSaving || goalBlocked)
            Spacer(minLength: 0)
        }
        .padding(20)
        .task {
            await store.refreshGoals()
        }
    }
}

// MARK: - Аскеза: быстрое создание контракта (паритет с веб `EntityCreateWizard`)

private struct AsceticQuickCreateSheet: View {
    let store: TodayFlowStore
    let startDateISO: String
    var onDismiss: () -> Void

    private enum DurationChoice: String, CaseIterable, Identifiable {
        case open
        case d7, d14, d21, d30

        var id: String { rawValue }

        var title: String { FlowTrackerChrome.asceticDurationTitle(for: rawValue) }

        var fixedDays: Int? {
            switch self {
            case .open: return nil
            case .d7: return 7
            case .d14: return 14
            case .d21: return 21
            case .d30: return 30
            }
        }
    }

    @State private var items: [PracticeAsceticismDTO] = []
    @State private var isLoading = true
    @State private var selectedId: String?
    @State private var duration = DurationChoice.d14

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView(FlowTrackerChrome.asceticLoadingCatalog)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if items.isEmpty {
                    Text(FlowTrackerChrome.asceticCatalogEmpty)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .padding()
                } else {
                    VStack(alignment: .leading, spacing: 14) {
                        Text(FlowTrackerChrome.asceticDurationSection)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                        Picker(FlowTrackerChrome.asceticDurationPicker, selection: $duration) {
                            ForEach(DurationChoice.allCases) { choice in
                                Text(choice.title).tag(choice)
                            }
                        }
                        .pickerStyle(.menu)

                        Text(FlowTrackerChrome.asceticPracticeSection)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                        ScrollView {
                            LazyVStack(alignment: .leading, spacing: 10) {
                                ForEach(displayRows) { row in
                                    Button {
                                        selectedId = row.id
                                    } label: {
                                        HStack(alignment: .top, spacing: 10) {
                                            Image(systemName: selectedId == row.id ? "largecircle.fill.circle" : "circle")
                                                .foregroundStyle(selectedId == row.id ? TodayFlowTheme.accent : TodayFlowTheme.secondaryInk)
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(row.title)
                                                    .font(.subheadline.weight(.semibold))
                                                    .foregroundStyle(TodayFlowTheme.ink)
                                                    .multilineTextAlignment(.leading)
                                                if let desc = row.subtitle, !desc.isEmpty {
                                                    Text(desc)
                                                        .font(.caption)
                                                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                                                        .multilineTextAlignment(.leading)
                                                }
                                            }
                                            Spacer(minLength: 0)
                                        }
                                        .padding(12)
                                        .background(
                                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                .fill(selectedId == row.id ? TodayFlowTheme.accentSoft.opacity(0.35) : TodayFlowTheme.cardStrong)
                                        )
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }

                        Button {
                            Task { await submit() }
                        } label: {
                            Text(FlowTrackerChrome.createContract)
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(TodayFlowTheme.accent)
                        .disabled(selectedId == nil || store.isSaving)
                    }
                    .padding(16)
                }
            }
            .navigationTitle(FlowTrackerChrome.asceticNavTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(FlowTrackerChrome.close) { onDismiss() }
                }
            }
            .task { await load() }
        }
    }

    private struct DisplayRow: Identifiable {
        let id: String
        let title: String
        let subtitle: String?
        let dto: PracticeAsceticismDTO
    }

    private var displayRows: [DisplayRow] {
        items.compactMap { dto in
            guard let rawId = dto.id?.trimmingCharacters(in: .whitespacesAndNewlines), !rawId.isEmpty else { return nil }
            let titleRaw = dto.title?.trimmingCharacters(in: .whitespacesAndNewlines)
            let title = (titleRaw?.isEmpty == false) ? titleRaw! : FlowTrackerChrome.asceticFallbackTitle
            let desc = dto.description?.trimmingCharacters(in: .whitespacesAndNewlines)
            let subtitle = (desc?.isEmpty == false) ? desc : nil
            return DisplayRow(id: rawId, title: title, subtitle: subtitle, dto: dto)
        }
    }

    private func load() async {
        await MainActor.run {
            isLoading = true
        }
        let list = await PracticesClient.fetchAsceticisms()
        await MainActor.run {
            items = list
            isLoading = false
        }
    }

    private func submit() async {
        guard let sid = selectedId, let row = displayRows.first(where: { $0.id == sid }) else { return }
        let ok = await store.createAsceticContract(
            asceticismId: sid,
            title: row.title,
            intention: row.dto.description,
            startDateISO: startDateISO,
            fixedDurationDays: duration.fixedDays
        )
        if ok {
            onDismiss()
        }
    }
}

#Preview {
    NavigationStack {
        CalendarView(store: TodayFlowStore())
    }
}
