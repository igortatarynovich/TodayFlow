import SwiftUI

struct AsceticMapRowModel: Identifiable {
    let id: Int
    let title: String
    let streakDays: Int
    let cells: [MapHeatmapCellModel]
}

struct AsceticContractMapAPI: Codable {
    let id: Int
    let title: String
    let status: String
    let streakDays: Int

    enum CodingKeys: String, CodingKey {
        case id, title, status
        case streakDays = "streak_days"
    }
}

func asceticMapCellColor(completed: Bool, isFuture: Bool) -> Color {
    if isFuture { return MoodMapModel.emptyColor }
    if completed { return Color(red: 107 / 255, green: 143 / 255, blue: 90 / 255, opacity: 0.92) }
    return Color(red: 236 / 255, green: 228 / 255, blue: 214 / 255, opacity: 0.55)
}

struct AsceticMapView: View {
    let store: TodayFlowStore

    @State private var loading = true
    @State private var error: String?
    @State private var rows: [AsceticMapRowModel] = []
    @State private var selectedRowId: Int?
    @State private var selectedDate: String?

    private var today: String { todayISO() ?? "" }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Каждый отмеченный день — камень на тропе. Не проценты — история пути.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                if loading {
                    ProgressView("Загружаю тропу…")
                } else if let error {
                    Text(error).foregroundStyle(TodayFlowTheme.roseClay)
                } else if rows.isEmpty {
                    Text("Выбери аскезу в Flow — здесь появится первая тропа.")
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                } else {
                    if rows.count > 1 {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(rows) { row in
                                    Button(row.title) { selectRow(row) }
                                        .buttonStyle(.bordered)
                                        .tint(selectedRowId == row.id ? TodayFlowTheme.ink : TodayFlowTheme.secondaryInk)
                                }
                            }
                        }
                    }
                    if let row = selectedRow {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("\(row.title) · \(row.streakDays) дн. подряд")
                                .font(.headline)
                            MapHeatmapGridView(cells: row.cells, selectedDateISO: selectedDate) { dateISO in
                                selectedDate = dateISO
                            }
                        }
                        .padding(14)
                        .background(Color.white.opacity(0.92))
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                    }
                }

                if let story = selectedDayStory {
                    MapStorySection(eyebrow: "История дня", text: story)
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта аскез")
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
    }

    private var selectedRow: AsceticMapRowModel? {
        rows.first(where: { $0.id == selectedRowId }) ?? rows.first
    }

    private var selectedDayStory: String? {
        guard let row = selectedRow, let selectedDate else { return nil }
        let done = row.cells.first(where: { $0.dateISO == selectedDate })?.hasMark ?? false
        return "\(formatDate(selectedDate, locale: .ru)) — «\(row.title)»: \(done ? "день отмечен на тропе." : "пауза, без отметки.")"
    }

    @MainActor
    private func selectRow(_ row: AsceticMapRowModel) {
        selectedRowId = row.id
        selectedDate = row.cells.last(where: { $0.hasMark && !$0.isFuture })?.dateISO
            ?? row.cells.first(where: { !$0.isFuture })?.dateISO
    }

    @MainActor
    private func load() async {
        loading = true
        defer { loading = false }
        do {
            rows = try await store.fetchAsceticMapRows(todayISO: today)
            if let first = rows.first { selectRow(first) }
        } catch {
            self.error = "Не удалось загрузить карту аскез."
        }
    }
}

struct WishMapView: View {
    let store: TodayFlowStore

    @State private var anchors: [WishAnchorRecord] = []
    @State private var selectedId: String?
    @State private var draft = ""

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Желания — якоря, не чеклист. Маленький шаг важнее большого плана.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                ZStack {
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(Color.white.opacity(0.92))
                        .frame(minHeight: 200)
                    if anchors.isEmpty {
                        Text("Добавь месячную цель в Flow или якорь здесь.")
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                            .padding()
                    } else {
                        GeometryReader { geo in
                            ForEach(Array(anchors.enumerated()), id: \.element.id) { index, anchor in
                                let pos = wishConstellationPosition(id: anchor.id, index: index)
                                Circle()
                                    .fill(anchor.stepCount > 0 ? TodayFlowTheme.mutedGold : TodayFlowTheme.paper)
                                    .frame(width: selectedId == anchor.id ? 14 : 10, height: selectedId == anchor.id ? 14 : 10)
                                    .overlay(Circle().stroke(TodayFlowTheme.ink.opacity(0.35), lineWidth: 1))
                                    .position(x: geo.size.width * pos.x / 100, y: geo.size.height * pos.y / 100)
                                    .onTapGesture { selectedId = anchor.id }
                            }
                        }
                    }
                }

                HStack {
                    TextField("Новое желание…", text: $draft)
                        .textFieldStyle(.roundedBorder)
                    Button("Добавить") { addAnchor() }
                        .buttonStyle(.bordered)
                }

                if let anchor = selectedAnchor {
                    MapStorySection(
                        eyebrow: "История якоря",
                        text: wishAnchorStory(anchor)
                    )
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта желаний")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear(perform: reload)
    }

    private var selectedAnchor: WishAnchorRecord? {
        anchors.first(where: { $0.id == selectedId }) ?? anchors.first
    }

    private func reload() {
        anchors = WishMapStore.mergeFromGoals(store.calendar.goalTracks)
        if selectedId == nil { selectedId = anchors.first?.id }
    }

    private func addAnchor() {
        let trimmed = draft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        _ = WishMapStore.saveLocalAnchor(title: trimmed)
        draft = ""
        reload()
    }

    private func wishAnchorStory(_ anchor: WishAnchorRecord) -> String {
        if anchor.stepCount >= 5 {
            return "«\(anchor.title)» — \(anchor.stepCount) маленьких шагов уже на карте."
        }
        if anchor.stepCount >= 1 {
            return "«\(anchor.title)» — история только начинается, \(anchor.stepCount) отметки."
        }
        return "«\(anchor.title)» — якорь на карте. Следующий шаг может быть очень маленьким."
    }

    private func wishConstellationPosition(id: String, index: Int) -> (x: Double, y: Double) {
        var hash = index * 17
        for scalar in id.unicodeScalars {
            hash = (hash + Int(scalar.value) * 31) % 997
        }
        return (Double(12 + hash % 76), Double(10 + (hash * 7) % 72))
    }
}

struct RelationshipMapView: View {
    @State private var circles: [RelationshipCircleRecord] = []
    @State private var selectedId: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Круги — к кому и к каким темам возвращается внимание. Не рейтинг совместимости.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                if circles.isEmpty {
                    Text("Открой разбор в Совместимости — здесь появятся первые узлы сети.")
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                } else {
                    ForEach(circles) { circle in
                        Button {
                            selectedId = circle.id
                        } label: {
                            HStack {
                                Circle()
                                    .fill(TodayFlowTheme.mutedGold.opacity(0.45))
                                    .frame(width: relationshipCircleSize(circle.visitCount), height: relationshipCircleSize(circle.visitCount))
                                VStack(alignment: .leading) {
                                    Text(circle.label).font(.headline).foregroundStyle(TodayFlowTheme.ink)
                                    Text("Визитов на карте: \(circle.visitCount)")
                                        .font(.caption)
                                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                                }
                                Spacer()
                            }
                            .padding(12)
                            .background(selectedId == circle.id ? TodayFlowTheme.todayHeroSurface : Color.white.opacity(0.92))
                            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                        }
                        .buttonStyle(.plain)
                    }
                }

                if let circle = circles.first(where: { $0.id == selectedId }) ?? circles.first {
                    MapStorySection(
                        eyebrow: "История узла",
                        text: "«\(circle.label)» — \(formatDate(String(circle.lastSeenAt.prefix(10)), locale: .ru)). На карте: \(circle.visitCount >= 2 ? "есть повторные визиты" : "первый заход"), без процентов совместимости."
                    )
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта связей")
        .navigationBarTitleDisplayMode(.inline)
        .onAppear {
            circles = RelationshipMapStore.readCircles().sorted { $0.lastSeenAt > $1.lastSeenAt }
            selectedId = circles.first?.id
        }
    }

    private func relationshipCircleSize(_ visits: Int) -> CGFloat {
        min(44, 22 + CGFloat(sqrt(Double(max(1, visits)))) * 8)
    }
}

struct TarotMapView: View {
    private var summary: TarotJourneySummary {
        TarotJourneySummaryBuilder.build(entries: TarotJourneyStore.readEntries())
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Архетипическое путешествие — какие темы и карты сопровождали вопросы.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.secondaryInk)

                if TarotJourneyStore.shouldShowPanel() {
                    Text(summary.periodLabel.capitalized)
                        .font(.title3.weight(.semibold))
                    if let theme = summary.themes.first {
                        Text("Чаще всего: \(theme.emoji) \(theme.label)")
                            .font(.subheadline)
                    }
                    if let card = summary.frequentCards.first {
                        Text("Карта рядом: \(card.name)")
                            .font(.subheadline)
                            .foregroundStyle(TodayFlowTheme.secondaryInk)
                    }
                } else {
                    Text("Сделай несколько раскладов — появится личная линия, не отчёт.")
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
            }
            .padding()
        }
        .background(TodayFlowTheme.paper.ignoresSafeArea())
        .navigationTitle("Карта таро")
        .navigationBarTitleDisplayMode(.inline)
    }
}
