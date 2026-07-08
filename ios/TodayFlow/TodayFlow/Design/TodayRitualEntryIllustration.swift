import UIKit

/// Иллюстрация входа в ритуал: файлы в бандле, папка `today-ritual-entry/`
/// (см. `Resources/today-ritual-entry/ASSET_SPEC.txt`).
enum TodayRitualEntryIllustration {
    static func timeSlot(for date: Date = Date(), calendar: Calendar = .current) -> String {
        let h = calendar.component(.hour, from: date)
        if (5 ..< 12).contains(h) { return "morning" }
        if (12 ..< 17).contains(h) { return "day" }
        return "evening"
    }

    static func energyBand(score: Int) -> String {
        let s = min(100, max(0, score))
        if s < 40 { return "soft" }
        if s < 70 { return "balanced" }
        return "vivid"
    }

    static func candidateFileNames(dateISO: String, energyScore: Int, now: Date = Date()) -> [String] {
        let slot = timeSlot(for: now)
        let band = energyBand(score: energyScore)
        let bases = [
            "\(dateISO)-\(slot)-\(band)",
            "\(dateISO)-\(slot)",
            dateISO,
            "default-\(slot)-\(band)",
            "default-\(slot)",
            "default",
        ]
        let exts = ["webp", "png", "jpg", "jpeg"]
        var out: [String] = []
        for b in bases {
            for e in exts {
                out.append("\(b).\(e)")
            }
        }
        return out
    }

    static func loadUIImage(dateISO: String, energyScore: Int) -> UIImage? {
        let sub = "today-ritual-entry"
        for name in candidateFileNames(dateISO: dateISO, energyScore: energyScore) {
            let ns = name as NSString
            let base = ns.deletingPathExtension
            let ext = ns.pathExtension
            if let url = Bundle.main.url(forResource: base, withExtension: ext, subdirectory: sub),
               let img = UIImage(contentsOfFile: url.path) {
                return img
            }
        }
        return nil
    }
}
