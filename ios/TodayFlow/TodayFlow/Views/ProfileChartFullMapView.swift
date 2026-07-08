import SwiftUI

/// Parity with web `ProfileChartFullMap.tsx` — 12 houses, planet table, aspects.
struct ProfileChartFullMapView: View {
    let natalChart: NatalChartPreview?
    let onReload: () async -> Void

    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        if let natalChart {
            VStack(alignment: .leading, spacing: 16) {
                housesSection(chart: natalChart)
                planetsSection(chart: natalChart)
                aspectsSection(chart: natalChart)
            }
        } else {
            VStack(alignment: .leading, spacing: 10) {
                Text("Полная карта появится после построения натала. Нажми «Обновить», когда данные рождения сохранены.")
                    .font(.subheadline)
                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                Button("Обновить карту") {
                    Task { await onReload() }
                }
                .buttonStyle(.bordered)
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.58))
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }

    private func housesSection(chart: NatalChartPreview) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeading("12 домов")
            LazyVGrid(columns: profileAdaptiveColumns(for: horizontalSizeClass), spacing: 10) {
                ForEach(ProfileHouseCopy.ensureTwelveHouses(from: chart)) { house in
                    houseCard(house: house, chart: chart)
                }
            }
        }
    }

    private func houseCard(house: NatalHouse, chart: NatalChartPreview) -> some View {
        let interpretation = chart.interpretations?.houses?["\(house.house)"]
        let title = ProfileHouseCopy.layerTitle[house.house] ?? "Дом \(house.house)"
        let text = interpretation?.description?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
            ?? interpretation?.theme?.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty
            ?? ProfileHouseCopy.fallback[house.house]
            ?? ""
        let isKey = ProfileHouseCopy.keyHouses.contains(house.house)

        return VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("\(house.house) дом")
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(TodayFlowTheme.twilight)
                Spacer()
                if let sign = house.sign, !sign.isEmpty {
                    Text(formatSign(house))
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                }
            }
            Text(title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(TodayFlowTheme.ink)
            Text(text)
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            isKey
                ? LinearGradient(
                    colors: [Color.white.opacity(0.95), TodayFlowTheme.twilight.opacity(0.08)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                : LinearGradient(colors: [Color.white.opacity(0.88)], startPoint: .top, endPoint: .bottom)
        )
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(isKey ? TodayFlowTheme.twilight.opacity(0.22) : Color.black.opacity(0.06), lineWidth: 1)
        )
    }

    private func planetsSection(chart: NatalChartPreview) -> some View {
        let order = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
        let rows = order.compactMap { key -> (String, NatalChartPosition)? in
            guard let pos = chart.positions[key] else { return nil }
            return (planetLabel(key), pos)
        }

        return Group {
            if !rows.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    sectionHeading("Планеты в знаках")
                    VStack(spacing: 0) {
                        HStack {
                            Text("Планета").frame(maxWidth: .infinity, alignment: .leading)
                            Text("Знак").frame(width: 88, alignment: .leading)
                            Text("Дом").frame(width: 44, alignment: .trailing)
                        }
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(TodayFlowTheme.secondaryInk)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)

                        ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                            Divider().opacity(0.25)
                            HStack {
                                Text(row.0)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                Text(row.1.sign ?? "—")
                                    .frame(width: 88, alignment: .leading)
                                Text(row.1.house.map(String.init) ?? "—")
                                    .frame(width: 44, alignment: .trailing)
                            }
                            .font(.caption)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                        }
                    }
                    .background(Color.white.opacity(0.72))
                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                }
            }
        }
    }

    private func aspectsSection(chart: NatalChartPreview) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeading("Аспекты")
            if let callouts = chart.aspects?.callouts, !callouts.isEmpty {
                VStack(spacing: 10) {
                    ForEach(callouts) { aspect in
                        aspectCard(aspect)
                    }
                }
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Аспекты для этой карты пока не загружены. Попробуй обновить карту.")
                        .font(.caption)
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    Button("Обновить карту") {
                        Task { await onReload() }
                    }
                    .buttonStyle(.bordered)
                }
                .padding(12)
                .background(Color.white.opacity(0.58))
                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            }
        }
    }

    private func aspectCard(_ aspect: NatalAspectCallout) -> some View {
        let tension = (aspect.tensionLevel ?? "").lowercased()
        let tint: Color = tension == "high" ? TodayFlowTheme.roseClay : tension == "medium" ? TodayFlowTheme.sunset : TodayFlowTheme.moss

        return VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 8) {
                Text(aspect.label ?? "Аспект")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.ink)
                if let level = aspect.tensionLevel, !level.isEmpty {
                    Text(tensionLabel(level))
                        .font(.caption2.weight(.bold))
                        .foregroundStyle(tint)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(tint.opacity(0.12))
                        .clipShape(Capsule())
                }
            }
            if let bodies = aspect.bodies, !bodies.isEmpty {
                Text(bodies)
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(TodayFlowTheme.secondaryInk)
            }
            Text(aspect.description ?? aspect.integration ?? "")
                .font(.caption)
                .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                .fixedSize(horizontal: false, vertical: true)
            if let keywords = aspect.keywords, !keywords.isEmpty {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 72), spacing: 6)], alignment: .leading, spacing: 6) {
                    ForEach(keywords.prefix(5), id: \.self) { keyword in
                        Text(keyword)
                            .font(.caption2.weight(.semibold))
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.7))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(TodayFlowTheme.sand.opacity(0.35))
                            .clipShape(Capsule())
                    }
                }
            }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.white.opacity(0.82))
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(tint.opacity(0.18), lineWidth: 1)
        )
    }

    private func sectionHeading(_ text: String) -> some View {
        Text(text.uppercased())
            .font(.caption.weight(.bold))
            .foregroundStyle(TodayFlowTheme.secondaryInk)
            .tracking(1.2)
    }

    private func formatSign(_ house: NatalHouse) -> String {
        guard let sign = house.sign else { return "" }
        if let deg = house.degree {
            return "\(ZodiacSignRU.title(sign)) · \(Int(deg.rounded()))°"
        }
        return ZodiacSignRU.title(sign)
    }

    private func planetLabel(_ key: String) -> String {
        switch key {
        case "sun": return "Солнце"
        case "moon": return "Луна"
        case "mercury": return "Меркурий"
        case "venus": return "Венера"
        case "mars": return "Марс"
        case "jupiter": return "Юпитер"
        case "saturn": return "Сатурн"
        case "uranus": return "Уран"
        case "neptune": return "Нептун"
        case "pluto": return "Плутон"
        default: return key.capitalized
        }
    }

    private func tensionLabel(_ level: String) -> String {
        switch level.lowercased() {
        case "high": return "Высокое напряжение"
        case "medium": return "Среднее напряжение"
        case "low": return "Мягкий аспект"
        default: return level
        }
    }
}

private extension String {
    var nilIfEmpty: String? {
        trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : self
    }
}
