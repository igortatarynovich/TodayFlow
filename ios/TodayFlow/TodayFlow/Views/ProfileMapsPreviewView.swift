import SwiftUI

struct ProfileMapsPreviewView: View {
    let store: TodayFlowStore
    var onOpenRhythm: (() -> Void)? = nil
    var showSectionBand: Bool = true

    @State private var selectedMapId: String?
    @State private var selectedDate: String?
    @State private var habitRows: [HabitMapRowModel] = []
    @State private var habitRowsLoading = false
    @State private var cycleObservation: String?

    private let previewDays = 35

    private var closedDays: [DayContinuityRecord] {
        TodayDayContinuityStore.scanClosedRecords()
    }

    private var today: String { todayISO() ?? "" }

    private var moodRecords: [MoodMapDayRecord] {
        MoodMapModel.scanRecords()
    }

    private var energyRecords: [EnergyMapDayRecord] {
        EnergyMapModel.scanRecordsWithMoodFallback()
    }

    private var promiseRecords: [PromiseMapDayRecord] {
        PromiseMapModel.scanRecords()
    }

    private var hasHeatmapMarks: Bool {
        !moodRecords.isEmpty || !energyRecords.isEmpty || !promiseRecords.isEmpty
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if showSectionBand {
                ProfileLivingMapsSectionBand()
            }
            Text("Мои карты")
                .font(showSectionBand ? .headline.weight(.semibold) : .title3.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(closedDays.isEmpty
                 ? "Закрой день в Today — появится первая точка на личной карте."
                 : (closedDays.count == 1
                    ? "Один закрытый день уже на карте. Продолжай — история складывается сама."
                    : "\(closedDays.count) закрытых дней уже на карте. Каждый вечер добавляет новую точку."))
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)

            if let observation = cycleObservation ?? ProfileLivingMapsModel.localObservation() {
                Text(observation)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .fixedSize(horizontal: false, vertical: true)
            }

            if !closedDays.isEmpty {
                HStack(spacing: 8) {
                    ForEach(closedDays.prefix(7).reversed(), id: \.dateISO) { record in
                        Circle()
                            .fill(seedColor(record.outcome))
                            .frame(width: 12, height: 12)
                    }
                }
            }

            if hasHeatmapMarks {
                Text("35 дней — настроение, энергия и обещания дня. Нажми на день, чтобы увидеть историю.")
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .fixedSize(horizontal: false, vertical: true)

                profileHeatmapRow(
                    id: "mood",
                    title: "Настроение",
                    destination: .mood,
                    cells: previewCells(MoodMapModel.buildCells(todayISO: today, records: moodRecords))
                )
                profileHeatmapRow(
                    id: "energy",
                    title: "Энергия",
                    destination: .energy,
                    cells: previewCells(EnergyMapModel.buildCells(todayISO: today, records: energyRecords))
                )
                profileHeatmapRow(
                    id: "promise",
                    title: "Обещания дня",
                    destination: .promise,
                    cells: previewCells(PromiseMapModel.buildCells(todayISO: today, records: promiseRecords))
                )
            }

            if !habitRows.isEmpty {
                Text("Каждая привычка — свой цвет на карте за 35 дней. Нажми на отмеченный день.")
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .fixedSize(horizontal: false, vertical: true)

                Text("Привычки")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .textCase(.uppercase)

                ForEach(habitRows.prefix(3)) { row in
                    profileHabitWeaveRow(row)
                }
            } else if habitRowsLoading {
                ProgressView()
                    .tint(TodayFlowTheme.sunset)
            }

            ProfileMapExploreGrid(store: store, onOpenRhythm: onOpenRhythm)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.88))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(TodayFlowTheme.borderRoseSubtle, lineWidth: 1)
        )
        .task { await loadHabitWeave() }
        .task { await loadCycleObservation() }
    }

    @MainActor
    private func loadCycleObservation() async {
        guard store.isAuthenticated else {
            cycleObservation = nil
            return
        }
        do {
            let entries = try await store.fetchCycleMapEntries(todayISO: today)
            cycleObservation = CycleMapModel.observation(
                entries: entries,
                moodRecords: moodRecords,
                locale: .ru
            )
        } catch {
            cycleObservation = nil
        }
    }

    @MainActor
    private func loadHabitWeave() async {
        habitRowsLoading = true
        defer { habitRowsLoading = false }
        do {
            let rows = try await store.fetchHabitMapRows(todayISO: today)
            habitRows = rows
                .filter { $0.cells.contains(where: \.hasMark) }
                .sorted { $0.streakDays > $1.streakDays }
        } catch {
            habitRows = []
        }
    }

    private func mapLinkLabel(_ title: String) -> some View {
        Text(title)
            .font(.subheadline.weight(.semibold))
            .foregroundStyle(TodayFlowTheme.ink)
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func previewCells(_ cells: [MapHeatmapCellModel]) -> [MapHeatmapCellModel] {
        Array(cells.suffix(previewDays))
    }

    @ViewBuilder
    private func profileHeatmapRow(
        id: String,
        title: String,
        destination: MapNavigationDestination,
        cells: [MapHeatmapCellModel]
    ) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
                    .textCase(.uppercase)
                Spacer()
                NavigationLink(value: destination) {
                    Text("Открыть")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                }
            }
            MapHeatmapGridView(
                cells: cells,
                selectedDateISO: selectedMapId == id ? selectedDate : nil
            ) { dateISO in
                selectedMapId = id
                selectedDate = dateISO
            }
            if selectedMapId == id, let selectedDate, let story = drillStory(mapId: id, dateISO: selectedDate) {
                Text(story)
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 8)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(TodayFlowTheme.twilight.opacity(0.06))
                    .overlay(alignment: .leading) {
                        Rectangle()
                            .fill(TodayFlowTheme.twilight)
                            .frame(width: 3)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.55))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    @ViewBuilder
    private func profileHabitWeaveRow(_ row: HabitMapRowModel) -> some View {
        let mapId = "habit-\(row.id)"
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(row.name)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .textCase(.uppercase)
                    if row.streakDays > 0 {
                        Text("\(row.streakDays) дн. подряд")
                            .font(.caption2)
                            .foregroundStyle(TodayFlowTheme.secondaryInk.opacity(0.85))
                    }
                }
                Spacer()
                NavigationLink(value: MapNavigationDestination.habits) {
                    Text("Открыть")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.ink)
                }
            }
            MapHeatmapGridView(
                cells: previewCells(row.cells),
                selectedDateISO: selectedMapId == mapId ? selectedDate : nil
            ) { dateISO in
                selectedMapId = mapId
                selectedDate = dateISO
            }
            if selectedMapId == mapId, let selectedDate {
                Text(habitDrillStory(row: row, dateISO: selectedDate))
                    .font(.footnote)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                    .padding(.horizontal, 10)
                    .padding(.vertical, 8)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(TodayFlowTheme.twilight.opacity(0.06))
                    .overlay(alignment: .leading) {
                        Rectangle()
                            .fill(TodayFlowTheme.twilight)
                            .frame(width: 3)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
        }
        .padding(10)
        .background(Color.white.opacity(0.55))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func habitDrillStory(row: HabitMapRowModel, dateISO: String) -> String {
        guard row.cells.contains(where: { $0.dateISO == dateISO && $0.hasMark }) else {
            return "Выбери день с отметкой на карте."
        }
        return "\(dateISO) — «\(row.name)». Привычка отмечена — ещё один штрих на карте."
    }

    private func drillStory(mapId: String, dateISO: String) -> String? {
        switch mapId {
        case "mood":
            guard let record = moodRecords.first(where: { $0.dateISO == dateISO }) else { return nil }
            return MoodMapModel.dayStory(record, locale: .ru)
        case "energy":
            guard let record = energyRecords.first(where: { $0.dateISO == dateISO }) else { return nil }
            return EnergyMapModel.dayStory(record, locale: .ru)
        case "promise":
            guard let record = promiseRecords.first(where: { $0.dateISO == dateISO }) else { return nil }
            return PromiseMapModel.dayStory(record, locale: .ru)
        default:
            return nil
        }
    }

    private func seedColor(_ outcome: DayFocusOutcome?) -> Color {
        switch outcome {
        case .done: return Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255)
        case .partial: return TodayFlowTheme.mutedGold
        case .notDone, .none: return TodayFlowTheme.roseClay.opacity(0.75)
        }
    }
}

struct ProfileMapExploreGrid: View {
    let store: TodayFlowStore
    var onOpenRhythm: (() -> Void)?

    private let columns = [GridItem(.adaptive(minimum: 108), spacing: 8)]

    var body: some View {
        LazyVGrid(columns: columns, alignment: .leading, spacing: 8) {
            ForEach(ProfileLivingMapsModel.exploreCards) { card in
                exploreCardView(card)
            }
        }
        .padding(.top, 4)
        .accessibilityIdentifier("profile-maps-explore-grid")
    }

    @ViewBuilder
    private func exploreCardView(_ card: ProfileMapExploreCardModel) -> some View {
        let label = VStack(alignment: .leading, spacing: 4) {
            Text(card.title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(card.desc)
                .font(.caption2)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(card.primary ? TodayFlowTheme.todayHeroSurface : Color.white.opacity(0.72))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(TodayFlowTheme.borderRoseSubtle, lineWidth: 1)
        )

        if card.opensRhythm, let onOpenRhythm {
            Button(action: onOpenRhythm) { label }.buttonStyle(.plain)
        } else if let destination = card.destination {
            NavigationLink(value: destination) { label }.buttonStyle(.plain)
        } else {
            label
        }
    }
}

struct HabitMapView: View {
    let store: TodayFlowStore

    @State private var loading = true
    @State private var error: String?
    @State private var rows: [HabitMapRowModel] = []

    private var today: String { todayISO() ?? "" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(FlowTrackerChromeCopy.habitsMapHeroBody)
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                if loading {
                    ProgressView(FlowTrackerChromeCopy.habitsMapLoadErrorFallback)
                } else if let error {
                    Text(error).foregroundStyle(TodayFlowTheme.roseClay)
                } else if rows.isEmpty {
                    Text(FlowTrackerChromeCopy.habitsMapEmptyList)
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                } else {
                    ForEach(rows) { row in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(row.name)
                                .font(.headline)
                            Text(FlowTrackerChromeCopy.habitMapStatsLine(streakDays: row.streakDays))
                                .font(.subheadline)
                                .foregroundStyle(TodayFlowTheme.secondaryInk)
                            MapHeatmapGridView(cells: row.cells, selectedDateISO: nil) { _ in }
                        }
                        .padding(14)
                        .background(Color.white.opacity(0.92))
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    }
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle(FlowTrackerChromeCopy.habitsMapPageTitle)
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
    }

    @MainActor
    private func load() async {
        loading = true
        defer { loading = false }
        do {
            rows = try await store.fetchHabitMapRows(todayISO: today)
        } catch {
            self.error = FlowTrackerChromeCopy.habitsMapLoadErrorFallback
        }
    }
}

struct HabitMapRowModel: Identifiable {
    let id: Int
    let name: String
    let streakDays: Int
    let cells: [MapHeatmapCellModel]
}

struct HabitMapHabitAPI: Codable {
    let id: Int
    let name: String
    let category: String?
}

struct HabitMapOverviewAPI: Codable {
    let habitId: Int
    let currentStreakDays: Int

    enum CodingKeys: String, CodingKey {
        case habitId = "habit_id"
        case currentStreakDays = "current_streak_days"
    }
}

struct HabitMapEntryAPI: Codable {
    let habitId: Int
    let date: String
    let completed: Bool

    enum CodingKeys: String, CodingKey {
        case habitId = "habit_id"
        case date, completed
    }
}

struct CycleMapEntryAPI: Codable {
    let date: String
    let periodIntensity: String?
    let ovulation: Bool
    let fertileWindow: Bool

    enum CodingKeys: String, CodingKey {
        case date
        case periodIntensity = "period_intensity"
        case ovulation
        case fertileWindow = "fertile_window"
    }

    var model: CycleMapEntryIn {
        CycleMapEntryIn(
            date: date,
            periodIntensity: periodIntensity,
            ovulation: ovulation,
            fertileWindow: fertileWindow
        )
    }
}

func habitWeaveColor(habitId: Int, category: String?) -> Color {
    let key = category?.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
    switch key {
    case "body": return Color(red: 214 / 255, green: 179 / 255, blue: 122 / 255, opacity: 0.92)
    case "focus": return Color(red: 191 / 255, green: 151 / 255, blue: 95 / 255, opacity: 0.9)
    case "mind": return Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.88)
    default:
        let palette: [Color] = [
            Color(red: 214 / 255, green: 179 / 255, blue: 122 / 255, opacity: 0.92),
            Color(red: 191 / 255, green: 151 / 255, blue: 95 / 255, opacity: 0.9),
            Color(red: 155 / 255, green: 118 / 255, blue: 70 / 255, opacity: 0.88),
        ]
        return palette[abs(habitId) % palette.count]
    }
}
