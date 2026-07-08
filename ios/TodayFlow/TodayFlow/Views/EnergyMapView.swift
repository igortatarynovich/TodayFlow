import SwiftUI

struct EnergyMapView: View {
    let store: TodayFlowStore

    @State private var records: [EnergyMapDayRecord] = []
    @State private var cells: [MapHeatmapCellModel] = []
    @State private var selectedDate: String?
    @State private var syncing = false

    private var today: String { todayISO() ?? "" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                if syncing {
                    ProgressView("Подтягиваю историю энергии…")
                        .tint(TodayFlowTheme.sunset)
                }
                heatmapCard
                if let text = EnergyMapModel.observation(records: records, locale: .ru) {
                    MapStorySection(eyebrow: "Наблюдение", text: text)
                }
                MapStorySection(
                    eyebrow: "История дня",
                    text: selectedStory ?? "Выбери день с отметкой на карте."
                )
                howToRead
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта энергии")
        .navigationBarTitleDisplayMode(.inline)
        .task { await reload(syncFusion: true) }
    }

    private var header: some View {
        Text(records.isEmpty
             ? "Поживи день в Today — отметки добавят первые точки на карте."
             : "Каждый день в Today оставляет след темпа. Нажми на день — увидишь историю, не цифры.")
            .font(.subheadline)
            .foregroundStyle(TodayFlowTheme.secondaryInk)
    }

    private var heatmapCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            MapHeatmapGridView(cells: cells, selectedDateISO: selectedDate) { dateISO in
                selectedDate = dateISO
            }
            MapLegendRow(items: [
                ("тихий", EnergyMapModel.cellColor(score: 30)),
                ("спокойный", EnergyMapModel.cellColor(score: 48)),
                ("ровный", EnergyMapModel.cellColor(score: 68)),
                ("подвижный", EnergyMapModel.cellColor(score: 85)),
                ("без отметки", MoodMapModel.emptyColor),
            ])
        }
        .padding(16)
        .background(Color.white.opacity(0.92))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var howToRead: some View {
        MapStorySection(
            eyebrow: "Как читать карту",
            text: "Один день — одна клетка. Цвет — темп дня: от тихого к подвижному."
        )
    }

    private var selectedStory: String? {
        guard let selectedDate,
              let record = records.first(where: { $0.dateISO == selectedDate })
        else { return nil }
        return EnergyMapModel.dayStory(record, locale: .ru)
    }

    @MainActor
    private func reload(syncFusion: Bool) async {
        if syncFusion {
            syncing = true
            if let fusion = store.fusionIndex, let date = store.todayCycle?.date {
                EnergyMapStore.save(
                    dateISO: date,
                    energyScore: fusion.scores.energy,
                    focusScore: fusion.scores.focus,
                    balanceScore: fusion.scores.emotionalBalance,
                    source: "today_fusion"
                )
            }
            await store.syncEnergyMapFusionBatch()
        }
        records = EnergyMapModel.scanRecordsWithMoodFallback()
        cells = EnergyMapModel.buildCells(todayISO: today, records: records)
        if selectedDate == nil { selectedDate = records.first?.dateISO }
        syncing = false
    }
}
