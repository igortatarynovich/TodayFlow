import SwiftUI

/// Натальное колесо: паритет с веб `NatalChartWheel.tsx` — `degreeToAngle = (270 − λ) mod 360`,
/// куспиды домов из API или равные дома от ASC, линии аспектов по callouts.
enum NatalChartWheelLayout {
    case full
    /// Без аспектов, меньше подписей — для sheet и узких колонок.
    case compact
}

private struct NatalPlanetLayout: Identifiable {
    let id: String
    let symbol: String
    let tint: Color
    let eclipticLongitude: Double
    let radius: CGFloat

    func screenPoint(center: CGPoint) -> CGPoint {
        NatalChartWheelMath.point(center: center, radius: radius, eclipticLongitude: eclipticLongitude)
    }
}

private struct NatalPlanetDetailSelection: Identifiable, Hashable {
    let id: String
    let symbol: String
    let titleRu: String
    let sign: String?
    /// Дом из API, если есть.
    let houseFromApi: Int?
    /// Дом по куспидам колеса.
    let houseComputed: Int?
    let degreeInSign: Double?
    let longitude: Double?
}

struct NatalChartWheelView: View {
    let chart: NatalChartPreview
    var layout: NatalChartWheelLayout = .full
    /// Кнопка «развернуть» (полный экран + pinch) — уместно в профиле, не в компактном sheet.
    var allowsFullscreen: Bool = false

    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var planetDetail: NatalPlanetDetailSelection?
    @State private var fullscreenPresented = false

    private var typeScale: CGFloat {
        switch dynamicTypeSize {
        case .xSmall: return 0.9
        case .small: return 0.95
        case .medium: return 1
        case .large: return 1.06
        case .xLarge: return 1.12
        case .xxLarge: return 1.18
        case .xxxLarge: return 1.24
        case .accessibility1: return 1.3
        case .accessibility2: return 1.36
        case .accessibility3: return 1.42
        case .accessibility4: return 1.48
        case .accessibility5: return 1.54
        @unknown default: return 1.22
        }
    }

    /// Ограничиваем рост, чтобы колесо не разъезжалось на экстремальных размерах.
    private var visualScale: CGFloat {
        min(max(typeScale, 0.88), 1.42)
    }

    var body: some View {
        ZStack(alignment: .topTrailing) {
            GeometryReader { geo in
                let side = min(geo.size.width, geo.size.height)
                let center = CGPoint(x: geo.size.width / 2, y: geo.size.height / 2)
                let padBase: CGFloat = layout == .compact ? 10 : 14
                let pad = padBase * min(visualScale, 1.12)
                let outerR = side / 2 - pad
                let zodiacOuter = outerR
                let zodiacInner = outerR * 0.82
                let houseOuter = zodiacInner - 4
                let houseInner = outerR * 0.52
                let aspectR = houseInner - 10
                let planetBaseR = zodiacInner - 14
                let cusps = NatalChartWheelMath.houseCusps(chart: chart)
                let planets = NatalChartWheelMath.planetLayouts(chart: chart, baseRadius: planetBaseR, clusterDegrees: layout == .compact ? 14 : 10)
                let houseFont = CGFloat(layout == .compact ? 9 : 10) * visualScale
                let zodiacFont = CGFloat(layout == .compact ? 12 : 14) * visualScale
                let planetDot = CGFloat(layout == .compact ? 22 : 26) * visualScale
                let planetGlyph = CGFloat(layout == .compact ? 11 : 13) * visualScale
                let angleLbl = CGFloat(8) * visualScale

                ZStack {
                ForEach(0..<12, id: \.self) { i in
                    let lon0 = Double(i * 30)
                    let lon1 = Double((i + 1) * 30)
                    NatalAnnulusSector(lonStart: lon0, lonEnd: lon1, innerR: zodiacInner, outerR: zodiacOuter)
                        .fill(i.isMultiple(of: 2) ? TodayFlowTheme.paper.opacity(0.72) : Color.white.opacity(0.88))
                    NatalAnnulusSector(lonStart: lon0, lonEnd: lon1, innerR: zodiacInner, outerR: zodiacOuter)
                        .stroke(TodayFlowTheme.gold.opacity(0.16), lineWidth: 1)
                }

                Circle()
                    .stroke(TodayFlowTheme.twilight.opacity(0.14), lineWidth: layout == .compact ? 12 : 16)
                    .frame(width: (houseOuter + houseInner), height: (houseOuter + houseInner))

                ForEach(0..<12, id: \.self) { i in
                    let cusp = cusps[i]
                    NatalWheelLine(fromRadius: zodiacOuter - 6, toRadius: houseInner + 8, longitude: cusp)
                        .stroke(TodayFlowTheme.gold.opacity(0.2), lineWidth: 1)
                    let next = cusps[(i + 1) % 12]
                    let mid = NatalChartWheelMath.midLongitude(from: cusp, to: next)
                    let labelR = (houseOuter + houseInner) / 2
                    Text("\(i + 1)")
                        .font(.system(size: houseFont, weight: .bold, design: .rounded))
                        .foregroundStyle(TodayFlowTheme.sand)
                        .position(NatalChartWheelMath.point(center: center, radius: labelR, eclipticLongitude: mid))
                }

                ForEach(Array(NatalChartWheelMath.zodiacGlyphs.enumerated()), id: \.offset) { _, z in
                    let midLon = Double(z.index * 30 + 15)
                    Text(z.glyph)
                        .font(.system(size: zodiacFont, weight: .bold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.82))
                        .position(NatalChartWheelMath.point(center: center, radius: (zodiacOuter + zodiacInner) / 2, eclipticLongitude: midLon))
                }

                if layout == .full, let aspects = chart.aspects?.callouts, !aspects.isEmpty {
                    ForEach(Array(aspects.prefix(22).enumerated()), id: \.offset) { _, aspect in
                        if let line = NatalChartWheelMath.aspectLine(
                            aspect: aspect,
                            planets: planets,
                            center: center,
                            radius: aspectR
                        ) {
                            Path { p in
                                p.move(to: line.0)
                                p.addLine(to: line.1)
                            }
                            .stroke(aspectLineColor(for: aspect), lineWidth: aspectLineWidth(for: aspect))
                            .opacity(0.55)
                        }
                    }
                }

                ForEach(planets) { pl in
                    Button {
                        planetDetail = planetDetailSelection(for: pl, cusps: cusps)
                    } label: {
                        ZStack {
                            Circle()
                                .fill(pl.tint)
                                .frame(width: planetDot, height: planetDot)
                            Text(pl.symbol)
                                .font(.system(size: planetGlyph, weight: .bold, design: .rounded))
                                .foregroundStyle(.white)
                        }
                        .shadow(color: pl.tint.opacity(0.25), radius: 5, y: 2)
                        .contentShape(Circle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("\(Self.planetTitleRU(pl.id)), \(pl.symbol)")
                    .accessibilityHint("Показать знак и дом")
                    .position(pl.screenPoint(center: center))
                }

                angleMarker(center: center, outerR: outerR + 16, innerR: zodiacInner - 4, longitude: cusps[0], label: "ASC", color: TodayFlowTheme.twilight, labelFont: angleLbl)
                angleMarker(center: center, outerR: outerR + 16, innerR: zodiacInner - 4, longitude: cusps[3], label: "IC", color: TodayFlowTheme.sky, labelFont: angleLbl)
                angleMarker(center: center, outerR: outerR + 14, innerR: zodiacInner - 4, longitude: cusps[6], label: "DSC", color: TodayFlowTheme.roseClay, labelFont: angleLbl)
                angleMarker(center: center, outerR: outerR + 14, innerR: zodiacInner - 4, longitude: cusps[9], label: "MC", color: TodayFlowTheme.gold, labelFont: angleLbl)

                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color.white.opacity(0.94), TodayFlowTheme.paper.opacity(0.82)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: side * (layout == .compact ? 0.30 : 0.34), height: side * (layout == .compact ? 0.30 : 0.34))
                    .overlay {
                        VStack(spacing: 4) {
                            Text("Солнце")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(TodayFlowTheme.sand)
                            Text(chart.positions["sun"]?.sign ?? "—")
                                .font(layout == .compact ? .subheadline.weight(.bold) : .headline.weight(.bold))
                                .foregroundStyle(TodayFlowTheme.ink)
                                .minimumScaleFactor(0.8)
                                .lineLimit(1)
                            if let asc = chart.ascendant?.degree {
                                Text("ASC \(Int(asc.rounded()))°")
                                    .font(.caption2)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                            } else if let s = chart.ascendant?.sign {
                                Text("ASC \(s)")
                                    .font(.caption2)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.58))
                            }
                        }
                        .padding(6)
                    }
                }
                .frame(width: geo.size.width, height: geo.size.height)
            }

            if allowsFullscreen, layout == .full {
                Button {
                    fullscreenPresented = true
                } label: {
                    Image(systemName: "arrow.up.left.and.arrow.down.right")
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(TodayFlowTheme.ink.opacity(0.75))
                        .padding(10)
                        .background(.ultraThinMaterial, in: Circle())
                }
                .buttonStyle(.plain)
                .padding(10)
                .accessibilityLabel("Развернуть карту")
            }
        }
        .sheet(item: $planetDetail) { detail in
            NatalPlanetDetailSheet(selection: detail)
        }
        .fullScreenCover(isPresented: $fullscreenPresented) {
            NatalChartWheelFullscreenSheet(chart: chart)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Натальное колесо. Солнце в знаке \(chart.positions["sun"]?.sign ?? "неизвестно").")
    }

    private func planetDetailSelection(for pl: NatalPlanetLayout, cusps: [Double]) -> NatalPlanetDetailSelection {
        let pos = chart.positions[pl.id]
        let computed = NatalChartWheelMath.houseNumber(longitude: pl.eclipticLongitude, cusps: cusps)
        return NatalPlanetDetailSelection(
            id: pl.id,
            symbol: pl.symbol,
            titleRu: Self.planetTitleRU(pl.id),
            sign: pos?.sign,
            houseFromApi: pos?.house,
            houseComputed: computed,
            degreeInSign: pos?.degree,
            longitude: pos?.longitude ?? pl.eclipticLongitude
        )
    }

    private static func planetTitleRU(_ key: String) -> String {
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
        case "north_node": return "Северный узел"
        case "south_node": return "Южный узел"
        case "chiron": return "Хирон"
        case "lilith": return "Лилит"
        default: return key.replacingOccurrences(of: "_", with: " ")
        }
    }

    private func angleMarker(center: CGPoint, outerR: CGFloat, innerR: CGFloat, longitude: Double, label: String, color: Color, labelFont: CGFloat) -> some View {
        let outer = NatalChartWheelMath.point(center: center, radius: outerR, eclipticLongitude: longitude)
        let inner = NatalChartWheelMath.point(center: center, radius: innerR, eclipticLongitude: longitude)
        return ZStack {
            Path { p in
                p.move(to: outer)
                p.addLine(to: inner)
            }
            .stroke(color.opacity(0.65), lineWidth: 1.5)
            Text(label)
                .font(.system(size: labelFont, weight: .bold, design: .rounded))
                .foregroundStyle(color)
                .padding(3)
                .background(Capsule().fill(Color.white.opacity(0.82)))
                .position(
                    CGPoint(
                        x: outer.x + (outer.x - center.x) * 0.06,
                        y: outer.y + (outer.y - center.y) * 0.06
                    )
                )
        }
    }

    private func aspectLineColor(for aspect: NatalAspectCallout) -> Color {
        let id = (aspect.aspectID ?? aspect.label ?? "").lowercased()
        if id.contains("conjunction") { return Color(red: 0.29, green: 0.56, blue: 0.89) }
        if id.contains("opposition") { return Color(red: 0.85, green: 0.28, blue: 0.37) }
        if id.contains("square") { return Color(red: 0.94, green: 0.55, blue: 0.17) }
        if id.contains("trine") { return Color(red: 0.12, green: 0.62, blue: 0.45) }
        if id.contains("sextile") { return Color(red: 0.30, green: 0.53, blue: 1.0) }
        return TodayFlowTheme.ink.opacity(0.35)
    }

    private func aspectLineWidth(for aspect: NatalAspectCallout) -> CGFloat {
        let id = (aspect.aspectID ?? "").lowercased()
        if id.contains("opposition") { return 2.2 }
        if id.contains("square") { return 2 }
        return 1.5
    }
}

// MARK: - Geometry (паритет с веб)

private enum NatalChartWheelMath {
    struct ZodiacGlyph {
        let index: Int
        let glyph: String
    }

    static let zodiacGlyphs: [ZodiacGlyph] = [
        .init(index: 0, glyph: "♈"), .init(index: 1, glyph: "♉"), .init(index: 2, glyph: "♊"),
        .init(index: 3, glyph: "♋"), .init(index: 4, glyph: "♌"), .init(index: 5, glyph: "♍"),
        .init(index: 6, glyph: "♎"), .init(index: 7, glyph: "♏"), .init(index: 8, glyph: "♐"),
        .init(index: 9, glyph: "♑"), .init(index: 10, glyph: "♒"), .init(index: 11, glyph: "♓"),
    ]

    /// Экранный угол в радианах (0° эклиптики → совпадает с веб `degreeToAngle`).
    static func radians(_ eclipticLongitude: Double) -> CGFloat {
        var d = (270 - eclipticLongitude).truncatingRemainder(dividingBy: 360)
        if d < 0 { d += 360 }
        return CGFloat(d * .pi / 180)
    }

    static func point(center: CGPoint, radius: CGFloat, eclipticLongitude: Double) -> CGPoint {
        let a = radians(eclipticLongitude)
        return CGPoint(
            x: center.x + radius * CGFloat(Darwin.cos(Double(a))),
            y: center.y + radius * CGFloat(Darwin.sin(Double(a)))
        )
    }

    static func midLongitude(from a: Double, to b: Double) -> Double {
        let na = normalize(a)
        let nb = normalize(b)
        if nb >= na {
            return normalize((na + nb) / 2)
        }
        return normalize((na + (nb + 360)) / 2)
    }

    static func normalize(_ x: Double) -> Double {
        var v = x.truncatingRemainder(dividingBy: 360)
        if v < 0 { v += 360 }
        return v
    }

    /// Номер дома (1…12) по долготе и куспидам — как на вебе при поиске сектора.
    static func houseNumber(longitude: Double, cusps: [Double]) -> Int {
        guard cusps.count == 12 else { return 1 }
        let lon = normalize(longitude)
        for i in 0..<12 {
            let cusp = normalize(cusps[i])
            let next = normalize(cusps[(i + 1) % 12])
            if next > cusp {
                if lon >= cusp && lon < next { return i + 1 }
            } else {
                if lon >= cusp || lon < next { return i + 1 }
            }
        }
        return 1
    }

    static func houseCusps(chart: NatalChartPreview) -> [Double] {
        let ascLon =
            chart.ascendant?.longitude
            ?? chart.houses.first { $0.house == 1 }?.cuspLongitude
            ?? eclipticLongitude(sign: chart.ascendant?.sign, degreeInSign: chart.ascendant?.degree)
            ?? 0
        var byHouse: [Int: Double] = [:]
        for h in chart.houses {
            if let lon = h.cuspLongitude {
                byHouse[h.house] = normalize(lon)
            } else if let lon = eclipticLongitude(sign: h.sign, degreeInSign: h.degree) {
                byHouse[h.house] = lon
            }
        }
        var out: [Double] = []
        for i in 1...12 {
            if let c = byHouse[i] {
                out.append(c)
            } else {
                out.append(normalize(ascLon + Double(i - 1) * 30))
            }
        }
        return out
    }

    static func eclipticLongitude(sign: String?, degreeInSign: Double?) -> Double? {
        guard let sign, let deg = degreeInSign else { return nil }
        guard let idx = zodiacIndex(canonicalSign(sign)) else { return nil }
        let d = ((deg.truncatingRemainder(dividingBy: 30)) + 30).truncatingRemainder(dividingBy: 30)
        return normalize(Double(idx) * 30 + d)
    }

    private static let signOrder = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    ]

    private static let ruToEn: [String: String] = [
        "овен": "aries", "телец": "taurus", "близнецы": "gemini", "рак": "cancer",
        "лев": "leo", "дева": "virgo", "весы": "libra", "скорпион": "scorpio",
        "стрелец": "sagittarius", "козерог": "capricorn", "водолей": "aquarius", "рыбы": "pisces",
    ]

    private static func canonicalSign(_ raw: String) -> String {
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if signOrder.contains(t) { return t }
        return ruToEn[t] ?? t.replacingOccurrences(of: " ", with: "")
    }

    private static func zodiacIndex(_ id: String) -> Int? {
        signOrder.firstIndex(of: id)
    }

    static func planetLayouts(chart: NatalChartPreview, baseRadius: CGFloat, clusterDegrees: Double) -> [NatalPlanetLayout] {
        let order = [
            "sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
            "uranus", "neptune", "pluto", "north_node", "south_node", "chiron", "lilith",
        ]
        var raw: [(key: String, lon: Double)] = []
        for key in order {
            guard let p = chart.positions[key] else { continue }
            let lon = p.longitude ?? eclipticLongitude(sign: p.sign, degreeInSign: p.degree) ?? 0
            raw.append((key, lon))
        }
        guard !raw.isEmpty else { return [] }

        let sorted = raw.sorted { normalize($0.lon) < normalize($1.lon) }
        let variation: CGFloat = 20
        return sorted.enumerated().map { idx, item in
            let prevLon = sorted[idx == 0 ? sorted.count - 1 : idx - 1].lon
            let nextLon = sorted[(idx + 1) % sorted.count].lon
            let distPrev = angularDistance(item.lon, prevLon)
            let distNext = angularDistance(nextLon, item.lon)
            let minD = min(distPrev, distNext)
            var offset: CGFloat = 0
            if minD < clusterDegrees {
                offset = (idx % 2 == 0 ? 1 : -1) * variation * 0.55
            }
            return NatalPlanetLayout(
                id: item.key,
                symbol: symbol(for: item.key),
                tint: tint(for: item.key),
                eclipticLongitude: item.lon,
                radius: baseRadius + offset
            )
        }
    }

    private static func angularDistance(_ a: Double, _ b: Double) -> Double {
        let x = abs(normalize(a) - normalize(b))
        return min(x, 360 - x)
    }

    static func aspectLine(
        aspect: NatalAspectCallout,
        planets: [NatalPlanetLayout],
        center: CGPoint,
        radius: CGFloat
    ) -> (CGPoint, CGPoint)? {
        guard let pair = parseAspectBodies(aspect.bodies) else { return nil }
        guard let p1 = planets.first(where: { bodiesMatch($0.id, pair.0) }),
              let p2 = planets.first(where: { bodiesMatch($0.id, pair.1) }) else { return nil }
        let a1 = point(center: center, radius: radius, eclipticLongitude: p1.eclipticLongitude)
        let a2 = point(center: center, radius: radius, eclipticLongitude: p2.eclipticLongitude)
        return (a1, a2)
    }

    private static func parseAspectBodies(_ bodies: String?) -> (String, String)? {
        guard let bodies else { return nil }
        let t = bodies.trimmingCharacters(in: .whitespacesAndNewlines)
        if t.isEmpty { return nil }
        let splitters = [" – ", " — ", " - ", " · ", ", ", " AND ", " and "]
        for sep in splitters {
            if let range = t.range(of: sep, options: .caseInsensitive) {
                let a = String(t[..<range.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
                let b = String(t[range.upperBound...]).trimmingCharacters(in: .whitespacesAndNewlines)
                if !a.isEmpty, !b.isEmpty { return (a, b) }
            }
        }
        let parts = t.split(separator: "-").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
        if parts.count >= 2 { return (String(parts[0]), String(parts[1])) }
        return nil
    }

    private static func bodiesMatch(_ chartKey: String, _ aspectToken: String) -> Bool {
        let a = canonicalBody(chartKey)
        let b = canonicalBody(aspectToken)
        if a.isEmpty || b.isEmpty { return false }
        return a == b || a.hasPrefix(b) || b.hasPrefix(a)
    }

    private static func canonicalBody(_ raw: String) -> String {
        let t = raw.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let map: [String: String] = [
            "sun": "sun", "солнце": "sun", "moon": "moon", "луна": "moon",
            "mercury": "mercury", "меркурий": "mercury",
            "venus": "venus", "венера": "venus",
            "mars": "mars", "марс": "mars",
            "jupiter": "jupiter", "юпитер": "jupiter",
            "saturn": "saturn", "сатурн": "saturn",
            "uranus": "uranus", "уран": "uranus",
            "neptune": "neptune", "нептун": "neptune",
            "pluto": "pluto", "плутон": "pluto",
            "north node": "north_node", "north_node": "north_node", "узел": "north_node",
            "south node": "south_node", "south_node": "south_node",
            "chiron": "chiron", "хирон": "chiron",
            "lilith": "lilith", "лилит": "lilith",
        ]
        let compact = t.replacingOccurrences(of: " ", with: "_")
        return map[t] ?? map[compact.replacingOccurrences(of: "_", with: " ")] ?? compact
    }

    private static func symbol(for key: String) -> String {
        switch key {
        case "sun": return "☉"
        case "moon": return "☽"
        case "mercury": return "☿"
        case "venus": return "♀"
        case "mars": return "♂"
        case "jupiter": return "♃"
        case "saturn": return "♄"
        case "uranus": return "♅"
        case "neptune": return "♆"
        case "pluto": return "♇"
        case "north_node": return "☊"
        case "south_node": return "☋"
        case "chiron": return "⚷"
        case "lilith": return "⚸"
        default: return "✦"
        }
    }

    private static func tint(for key: String) -> Color {
        switch key {
        case "sun": return TodayFlowTheme.sunset
        case "moon": return TodayFlowTheme.twilight
        case "venus": return TodayFlowTheme.roseClay
        case "mars": return TodayFlowTheme.ember
        case "jupiter": return TodayFlowTheme.gold
        case "saturn": return TodayFlowTheme.moss
        case "uranus": return TodayFlowTheme.sky
        case "neptune": return TodayFlowTheme.twilight
        case "pluto": return TodayFlowTheme.ink
        case "north_node", "south_node": return TodayFlowTheme.gold
        case "chiron": return TodayFlowTheme.moss
        case "lilith": return TodayFlowTheme.ember
        default: return TodayFlowTheme.ink
        }
    }
}

private struct NatalAnnulusSector: Shape {
    let lonStart: Double
    let lonEnd: Double
    let innerR: CGFloat
    let outerR: CGFloat

    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let steps = 14
        var p = Path()
        let start = NatalChartWheelMath.point(center: center, radius: innerR, eclipticLongitude: lonStart)
        p.move(to: start)
        p.addLine(to: NatalChartWheelMath.point(center: center, radius: outerR, eclipticLongitude: lonStart))
        for i in 1...steps {
            let u = lonStart + (lonEnd - lonStart) * Double(i) / Double(steps)
            p.addLine(to: NatalChartWheelMath.point(center: center, radius: outerR, eclipticLongitude: u))
        }
        p.addLine(to: NatalChartWheelMath.point(center: center, radius: innerR, eclipticLongitude: lonEnd))
        for i in (0..<steps).reversed() {
            let u = lonStart + (lonEnd - lonStart) * Double(i) / Double(steps)
            p.addLine(to: NatalChartWheelMath.point(center: center, radius: innerR, eclipticLongitude: u))
        }
        p.closeSubpath()
        return p
    }
}

private struct NatalWheelLine: Shape {
    let fromRadius: CGFloat
    let toRadius: CGFloat
    let longitude: Double

    func path(in rect: CGRect) -> Path {
        let center = CGPoint(x: rect.midX, y: rect.midY)
        var p = Path()
        p.move(to: NatalChartWheelMath.point(center: center, radius: fromRadius, eclipticLongitude: longitude))
        p.addLine(to: NatalChartWheelMath.point(center: center, radius: toRadius, eclipticLongitude: longitude))
        return p
    }
}

// MARK: - Планета: детали и полноэкран

private struct NatalPlanetDetailSheet: View {
    let selection: NatalPlanetDetailSelection
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack(alignment: .top, spacing: 14) {
                        Text(selection.symbol)
                            .font(.system(size: 40, weight: .bold))
                            .foregroundStyle(TodayFlowTheme.sunset)
                        VStack(alignment: .leading, spacing: 8) {
                            Text(selection.titleRu)
                                .font(.title2.weight(.bold))
                                .foregroundStyle(TodayFlowTheme.ink)
                            if let sign = selection.sign {
                                Text("Знак: \(sign)")
                                    .font(.body)
                                    .foregroundStyle(TodayFlowTheme.ink.opacity(0.88))
                            }
                        }
                    }
                }
                if let line = houseSummary {
                    Section {
                        Text(line)
                            .font(.subheadline)
                    } header: {
                        Text("Дом")
                    }
                }
                if let d = selection.degreeInSign {
                    Section {
                        Text(formatDegree(d))
                            .font(.body)
                    } header: {
                        Text("Градус в знаке")
                    }
                }
                if let lon = selection.longitude {
                    Section {
                        Text("\(Int(lon.rounded()))°")
                            .font(.footnote)
                            .foregroundStyle(TodayFlowTheme.ink.opacity(0.72))
                    } header: {
                        Text("Эклиптическая долгота")
                    }
                }
            }
            .navigationTitle("Карта")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Готово") { dismiss() }
                }
            }
        }
    }

    private var houseSummary: String? {
        let api = selection.houseFromApi
        let comp = selection.houseComputed
        switch (api, comp) {
        case let (a?, c?) where a == c:
            return "Дом \(a)"
        case let (a?, c?):
            return "По данным карты: дом \(a). На колесе по куспидам: дом \(c)."
        case let (a?, nil):
            return "Дом \(a) (данные карты)"
        case let (nil, c?):
            return "Дом \(c) (по куспидам колеса)"
        default:
            return nil
        }
    }

    private func formatDegree(_ d: Double) -> String {
        let rounded = (d * 10).rounded() / 10
        if abs(rounded - rounded.rounded()) < 0.05 {
            return "\(Int(rounded.rounded()))°"
        }
        return String(format: "%.1f°", rounded)
    }
}

private struct NatalChartWheelFullscreenSheet: View {
    let chart: NatalChartPreview
    @Environment(\.dismiss) private var dismiss
    @GestureState private var pinch: CGFloat = 1
    @State private var committedScale: CGFloat = 1

    var body: some View {
        NavigationStack {
            ZStack {
                TodayFlowTheme.screenGradient
                    .ignoresSafeArea()
                GeometryReader { geo in
                    let side = min(geo.size.width, geo.size.height) - 28
                    NatalChartWheelView(chart: chart, layout: .full, allowsFullscreen: false)
                        .frame(width: side, height: side)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .scaleEffect(min(max(committedScale * pinch, 1), 5))
                        .gesture(
                            MagnificationGesture()
                                .updating($pinch) { value, state, _ in state = value }
                                .onEnded { value in
                                    committedScale = min(max(committedScale * value, 1), 5)
                                }
                        )
                        .onTapGesture(count: 2) {
                            committedScale = 1
                        }
                }
            }
            .navigationTitle("Натальная карта")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Закрыть") { dismiss() }
                }
            }
        }
    }
}
