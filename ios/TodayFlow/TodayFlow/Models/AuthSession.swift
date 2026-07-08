import Foundation

struct AuthSession: Codable, Equatable {
    let token: String
    let userID: Int
    let email: String
    let isPaid: Bool
    let hasLiteReport: Bool
    let hasFullReport: Bool
    /// `free` | `pro` | `premium` из `GET /auth/me` (гейт DE-8 для режима «Глубже» в настройках narrative).
    let insightDepthTier: String?

    var membershipTitle: String {
        if isPaid { return "Paid member" }
        if hasFullReport { return "Full report owner" }
        if hasLiteReport { return "Lite report owner" }
        return "Founding member"
    }
}
