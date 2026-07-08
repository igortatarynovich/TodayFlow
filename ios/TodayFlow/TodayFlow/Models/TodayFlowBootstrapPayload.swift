import Foundation

struct TodayFlowBootstrapPayload: Codable {
    let profile: BirthProfile
    let dailyFocus: DailyFocus
    let rituals: [Ritual]
    let todayCycle: TodayCycle?
    let fusionIndex: FusionIndex?
    let fusionHistory: [FusionIndex]
}
