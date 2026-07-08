import Foundation

/// PNG колоды с фронта (`public/images/cards/tarot`) — тот же визуал, что в Next.
/// Требуется `WEB_BASE_URL` (например `http://127.0.0.1:3000` в симуляторе).
enum TodayTarotDeckImageURLs {
    /// Натуральный размер ассетов колоды (паритет с веб `tarotCardAssets`).
    static let cardPixelWidth: CGFloat = 192
    static let cardPixelHeight: CGFloat = 320

    /// Миниатюра лица рядом с числом в блоке «день готов» (паритет с веб `TAROT_SPINE_THUMB_WIDTH_PX`).
    static let ritualSpineThumbWidth: CGFloat = 76

    /// Макс. ширина раскрытой карты в мини-ритуале / экране раскрытия (паритет с веб `TAROT_RITUAL_REVEAL_MAX_WIDTH_PX`).
    static let ritualRevealMaxWidth: CGFloat = 220

    /// Высота прямоугольника карты при заданной ширине (сохраняем 192:320).
    static func cardDisplayHeight(width: CGFloat) -> CGFloat {
        width * cardPixelHeight / cardPixelWidth
    }

    private static var tarotFolder: URL {
        AppConfig.webBaseURL.appendingPathComponent("images/cards/tarot", isDirectory: true)
    }

    static func cardBackURL() -> URL {
        tarotFolder.appendingPathComponent("Back_web.png")
    }

    /// Лицо карты по индексу колоды 0…77 (масти: `Suit of *` / 1…14.png).
    static func deckFaceURL(cardId: Int) -> URL? {
        guard (0 ... 77).contains(cardId) else { return nil }
        if cardId <= 21 {
            return tarotFolder
                .appendingPathComponent("Major Arcana", isDirectory: true)
                .appendingPathComponent("\(cardId).png", isDirectory: false)
        }
        let n = cardId - 22
        let suitIndex = n / 14
        let rank = n % 14 + 1
        let folders = ["Suit of Wands", "Suit of Cups", "Suit of Swords", "Suit of Pentacles"]
        guard folders.indices.contains(suitIndex) else { return nil }
        return tarotFolder
            .appendingPathComponent(folders[suitIndex], isDirectory: true)
            .appendingPathComponent("\(rank).png", isDirectory: false)
    }
}
