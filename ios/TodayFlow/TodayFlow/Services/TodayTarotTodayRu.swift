import Foundation

/// Локальный слой «Карты дня» в Today — паритет с `frontend/src/components/today/todayTarotCardsRu.ts`
/// и `today_tarot_today_ru.json` в бандле.
struct TodayTarotCardRuRecord: Codable, Equatable {
    let nameRu: String
    let leadRu: String
    let bodyRu: String
    let questionRu: String
    let sphereBump: SphereBump?
    let riskRu: String?
    let focusRu: String?
    let eveningRu: String?

    struct SphereBump: Codable, Equatable {
        var love: Int?
        var work: Int?
        var money: Int?
        var energy: Int?

        func asScores() -> [String: Int] {
            var d: [String: Int] = [:]
            if let love { d["love"] = love }
            if let work { d["work"] = work }
            if let money { d["money"] = money }
            if let energy { d["energy"] = energy }
            return d
        }
    }
}

enum TodayTarotTodayRuCatalog {
    static let shared: [Int: TodayTarotCardRuRecord] = {
        guard let url = Bundle.main.url(forResource: "today_tarot_today_ru", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let raw = try? JSONDecoder().decode([String: TodayTarotCardRuRecord].self, from: data)
        else {
            return [:]
        }
        var out: [Int: TodayTarotCardRuRecord] = [:]
        for (key, value) in raw {
            if let i = Int(key) { out[i] = value }
        }
        return out
    }()

    static func card(_ id: Int?) -> TodayTarotCardRuRecord? {
        guard let id else { return nil }
        if let c = shared[id] { return c }
        if id >= 22 && id <= 77 { return minorPlaceholder(deckIndex: id) }
        return nil
    }

    private static func minorPlaceholder(deckIndex: Int) -> TodayTarotCardRuRecord {
        let off = deckIndex - 22
        let suits = ["жезлов", "кубков", "мечей", "пентаклей"]
        let ranks = ["Туз", "Двойка", "Тройка", "Четвёрка", "Пятёрка", "Шестёрка", "Семёрка", "Восьмёрка", "Девятка", "Десятка", "Паж", "Рыцарь", "Королева", "Король"]
        let suit = suits[off / 14]
        let rank = ranks[off % 14]
        let nameRu = "\(rank) \(suit)"
        return TodayTarotCardRuRecord(
            nameRu: nameRu,
            leadRu: "Сегодня эта карта подсвечивает повседневный слой: действия, привычки и то, как ты проживаешь тему дня руками и выбором.",
            bodyRu: "Младшие арканы про конкретику: где ускориться, где замедлиться и где один честный шаг даст больше ясности, чем долгие размышления.",
            questionRu: "где сегодня один конкретный поступок сделает день понятнее — без геройства и без откладывания?",
            sphereBump: .init(love: nil, work: 3, money: nil, energy: 4),
            riskRu: "автопилот и срыв в спешку вместо одного выбранного шага",
            focusRu: "одно действие «в масть» дню — коротко и до конца",
            eveningRu: "Где младший аркан помог заметить быт и выбор — а где хотелось убежать в абстракции?"
        )
    }

    /// Запись для блока «Карта дня»: совпадение по имени из API или стабильный старший аркан по дате (0…21).
    static func record(forCardName name: String?, dateISO: String) -> TodayTarotCardRuRecord? {
        if let name {
            let needle = normalized(name)
            if !needle.isEmpty {
                for rec in shared.values where normalized(rec.nameRu) == needle {
                    return rec
                }
            }
        }
        return shared[stableMajorArcanaId(for: dateISO)]
    }

    /// Индекс карты в колоде 0…77 для PNG с `WEB_BASE_URL/images/cards/tarot/`.
    static func deckImageIdForDay(apiCardName: String?, dateISO: String) -> Int {
        if let id = englishMajorId(apiCardName) { return id }
        if let name = apiCardName {
            let needle = normalized(name)
            for (id, rec) in shared where normalized(rec.nameRu) == needle { return id }
        }
        return stableDeckIndex(for: dateISO)
    }

    private static func englishMajorId(_ raw: String?) -> Int? {
        guard let raw else { return nil }
        let key = normalized(raw)
        return EnglishMajor.nameToId[key]
    }

    private enum EnglishMajor {
        /// Имена как в `DATA/astrology_reference/tarot_major_arcana.json`.
        static let nameToId: [String: Int] = [
            "the fool": 0, "the magician": 1, "the high priestess": 2, "the empress": 3,
            "the emperor": 4, "the hierophant": 5, "the lovers": 6, "the chariot": 7,
            "strength": 8, "the hermit": 9, "wheel of fortune": 10, "justice": 11,
            "the hanged one": 12, "death": 13, "temperance": 14, "the devil": 15,
            "the tower": 16, "the star": 17, "the moon": 18, "the sun": 19,
            "judgement": 20, "the world": 21,
        ]
    }

    private static func normalized(_ s: String) -> String {
        s.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
    }

    private static func fnvBasis32(for dateISO: String) -> UInt32 {
        var h: UInt32 = 2_166_136_261
        for b in dateISO.utf8 {
            h ^= UInt32(b)
            h &*= 16_777_619
        }
        return h
    }

    /// Стабильный старший аркан 0…21 для текстов без имени из API (как раньше `h % 22`).
    private static func stableMajorArcanaId(for dateISO: String) -> Int {
        Int(fnvBasis32(for: dateISO) % 22)
    }

    /// Стабильный индекс полной колоды 0…77 для PNG, если API не дал карту.
    private static func stableDeckIndex(for dateISO: String) -> Int {
        Int(fnvBasis32(for: dateISO) % 78)
    }
}

enum TodayTarotDayDraw {
    /// Случайная карта колоды 0…77, исключая указанные id.
    static func randomDeckIndex(excluding: Set<Int>) -> Int {
        let pool = (0...77).filter { !excluding.contains($0) }
        return pool.randomElement() ?? 0
    }

    /// Основная карта + половина веса уточняющей — как `mergeTarotSphereBumps` на вебе.
    static func mergeSphereBumps(main: TodayTarotCardRuRecord.SphereBump?, clarifier: TodayTarotCardRuRecord.SphereBump?) -> [String: Int] {
        let m = main?.asScores() ?? [:]
        let c = clarifier?.asScores() ?? [:]
        var keys = Set(m.keys)
        keys.formUnion(c.keys)
        var out: [String: Int] = [:]
        for k in keys {
            let v = Double(m[k] ?? 0) + Double(c[k] ?? 0) * 0.5
            let rounded = Int(v.rounded())
            if rounded != 0 { out[k] = rounded }
        }
        return out
    }
}
