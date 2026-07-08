import SwiftUI

struct PromiseMapView: View {
    @State private var records: [PromiseMapDayRecord] = []
    @State private var cells: [MapHeatmapCellModel] = []
    @State private var selectedDate: String?

    private var today: String { todayISO() ?? "" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                header
                heatmapCard
                if let text = PromiseMapModel.observation(records: records, locale: .ru) {
                    MapStorySection(eyebrow: "Наблюдение", text: text)
                }
                MapStorySection(
                    eyebrow: "История дня",
                    text: selectedStory ?? "Выбери день с обещанием на карте."
                )
                howToRead
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта обещаний")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: reload)
    }

    private var header: some View {
        Text(records.isEmpty
             ? "Дай обещание дня в Today и закрой вечер — здесь появится первая точка."
             : "Каждое обещание и вечернее закрытие оставляют след. Нажми на день — увидишь историю.")
            .font(.subheadline)
            .foregroundStyle(TodayFlowTheme.secondaryInk)
    }

    private var heatmapCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            MapHeatmapGridView(cells: cells, selectedDateISO: selectedDate) { dateISO in
                selectedDate = dateISO
            }
            MapLegendRow(items: [
                ("сделал", PromiseMapModel.cellColor(.done)),
                ("частично", PromiseMapModel.cellColor(.partial)),
                ("не сделал", PromiseMapModel.cellColor(.notDone)),
                ("открыто", PromiseMapModel.cellColor(.open)),
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
            text: "Цвет — исход обещания. Нажми на день — увидишь, что обещал и как закрылся вечер."
        )
    }

    private var selectedStory: String? {
        guard let selectedDate,
              let record = records.first(where: { $0.dateISO == selectedDate })
        else { return nil }
        return PromiseMapModel.dayStory(record, locale: .ru)
    }

    private func reload() {
        records = PromiseMapModel.scanRecords()
        cells = PromiseMapModel.buildCells(todayISO: today, records: records)
        if selectedDate == nil { selectedDate = records.first?.dateISO }
    }
}
