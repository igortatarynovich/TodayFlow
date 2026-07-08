import Foundation

struct UserProfile: Codable {
    let email: String
    let firstName: String
    let location: String
    let timezone: String
    let membership: String
}

extension UserProfile {
    static let placeholder = UserProfile(
        email: "victoria@example.com",
        firstName: "Victoria",
        location: "Warsaw",
        timezone: "Europe/Warsaw",
        membership: "Founding member"
    )
}
