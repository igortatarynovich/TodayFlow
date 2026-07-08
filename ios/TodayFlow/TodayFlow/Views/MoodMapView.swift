import SwiftUI

struct MoodMapView: View {
    var ritualEmail: String? = nil

    @State private var records: [MoodMapDayRecord] = []
    @State private var cells: [MapHeatmapCellModel] = []
    @State private var selectedDate: String?

    private var today: String { todayISO() ?? "" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                heatmapCard
                if let text = MoodMapModel.observation(records: records, locale: .ru) {
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
        .navigationTitle("Карта настроения")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: reload)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Карты")
                .font(.caption.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .textCase(.uppercase)
            Text(records.isEmpty
                 ? "Отметь настроение в Today — здесь появится первая точка на карте."
                 : "Каждая отметка в Today добавляет точку. Нажми на день — увидишь историю, не цифры.")
                .font(.subheadline)
                .foregroundStyle(TodayFlowTheme.secondaryInk)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var heatmapCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            MapHeatmapGridView(cells: cells, selectedDateISO: selectedDate) { dateISO in
                selectedDate = dateISO
            }
            MapLegendRow(items: TodayRitualCopy.moodGridMockup.map { item in
                (item.label, MoodMapModel.moodColorsPublic(item.id))
            } + [("без отметки", MoodMapModel.emptyColor)])
        }
        .padding(16)
        .background(Color.white.opacity(0.92))
        .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
    }

    private var howToRead: some View {
        MapStorySection(
            eyebrow: "Как читать карту",
            text: "Один день — одна клетка. Цвет — утреннее состояние. Нажми на день — увидишь фокус, обещание и итог вечера."
        )
    }

    private var selectedStory: String? {
        guard let selectedDate,
              let record = records.first(where: { $0.dateISO == selectedDate })
        else { return nil }
        return MoodMapModel.dayStory(record, locale: .ru)
    }

    private func reload() {
        records = MoodMapModel.scanRecords(ritualEmail: ritualEmail)
        cells = MoodMapModel.buildCells(todayISO: today, records: records)
        if selectedDate == nil { selectedDate = records.first?.dateISO }
    }
}

extension MoodMapModel {
    static func moodColorsPublic(_ moodId: String) -> Color {
        let map: [String: Color] = [
            "calm": Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.88),
            "driven": Color(red: 155 / 255, green: 118 / 255, blue: 70 / 255, opacity: 0.92),
            "tired": Color(red: 154 / 255, green: 132 / 255, blue: 104 / 255, opacity: 0.72),
            "anxious": Color(red: 180 / 255, green: 120 / 255, blue: 100 / 255, opacity: 0.78),
            "irritated": Color(red: 180 / 255, green: 120 / 255, blue: 100 / 255, opacity: 0.78),
        ]
        return map[moodId] ?? Color(red: 191 / 255, green: 151 / 255, blue: 95 / 255, opacity: 0.62)
    }
}
