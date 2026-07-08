import Foundation

/// Конфигурация окружения: тот же бэкенд и тот же веб-фронт, что и у Next.js-клиента.
enum AppConfig {
    /// Тот же ключ, что и для `@AppStorage` в SwiftUI.
    static let authTokenUserDefaultsKey = "TodayFlow.authToken"
    static let apiBaseURLOverrideUserDefaultsKey = "TodayFlow.apiBaseURLOverride"
    static let astroServiceURLOverrideUserDefaultsKey = "TodayFlow.astroServiceURLOverride"
    static let webBaseURLOverrideUserDefaultsKey = "TodayFlow.webBaseURLOverride"

    /// Ключ `API_BASE_URL` в Info.plist — как `NEXT_PUBLIC_API_BASE_URL` (порт бэкенда).
    static var apiBaseURL: URL {
        urlOverrideOrInfoPlist(
            overrideKey: apiBaseURLOverrideUserDefaultsKey,
            infoKey: "API_BASE_URL",
            fallback: "http://127.0.0.1:8080"
        )
    }

    /// Микросервис расчёта карты (`astro`, порт 8081 локально). На устройстве укажи LAN-хост Mac, если astro не в Docker-сети.
    static var astroServiceURL: URL {
        urlOverrideOrInfoPlist(
            overrideKey: astroServiceURLOverrideUserDefaultsKey,
            infoKey: "ASTRO_SERVICE_URL",
            fallback: "http://127.0.0.1:8081"
        )
    }

    /// Ключ `WEB_BASE_URL` — origin Next.js (`npm run dev` обычно :3000). Нужен для WKWebView.
    static var webBaseURL: URL {
        urlOverrideOrInfoPlist(
            overrideKey: webBaseURLOverrideUserDefaultsKey,
            infoKey: "WEB_BASE_URL",
            fallback: "http://127.0.0.1:3000"
        )
    }

    static var apiBaseURLString: String { apiBaseURL.absoluteString }
    static var astroServiceURLString: String { astroServiceURL.absoluteString }
    static var webBaseURLString: String { webBaseURL.absoluteString }

    static var runtimeConnectionWarning: String? {
        guard !isRunningOnSimulator else { return nil }
        let localHosts = Set(["127.0.0.1", "localhost"])
        let endpoints = [
            ("API", apiBaseURL),
            ("Astro", astroServiceURL),
            ("Web", webBaseURL)
        ]

        let blocked = endpoints.compactMap { label, url -> String? in
            guard let host = url.host?.lowercased(), localHosts.contains(host) else { return nil }
            return "\(label): \(url.absoluteString)"
        }

        guard !blocked.isEmpty else { return nil }
        return "Сейчас приложение смотрит в localhost endpoints. На реальном iPhone это не работает. Укажи LAN-адрес Mac в Settings → Connection.\n" + blocked.joined(separator: "\n")
    }

    /// Совпадает с `localStorage.todayflow_token` на вебе (`frontend/src/lib/useAuth.ts`).
    static var authToken: String {
        UserDefaults.standard.string(forKey: authTokenUserDefaultsKey) ?? ""
    }

    static func setAuthToken(_ token: String) {
        let t = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty else { return }
        UserDefaults.standard.set(t, forKey: authTokenUserDefaultsKey)
    }

    static func clearAuthToken() {
        UserDefaults.standard.removeObject(forKey: authTokenUserDefaultsKey)
    }

    static func setAPIBaseURLOverride(_ raw: String) {
        saveURLOverride(raw, key: apiBaseURLOverrideUserDefaultsKey)
    }

    static func setAstroServiceURLOverride(_ raw: String) {
        saveURLOverride(raw, key: astroServiceURLOverrideUserDefaultsKey)
    }

    static func setWebBaseURLOverride(_ raw: String) {
        saveURLOverride(raw, key: webBaseURLOverrideUserDefaultsKey)
    }

    static func clearNetworkOverrides() {
        UserDefaults.standard.removeObject(forKey: apiBaseURLOverrideUserDefaultsKey)
        UserDefaults.standard.removeObject(forKey: astroServiceURLOverrideUserDefaultsKey)
        UserDefaults.standard.removeObject(forKey: webBaseURLOverrideUserDefaultsKey)
    }

    private static var isRunningOnSimulator: Bool {
#if targetEnvironment(simulator)
        return true
#else
        return false
#endif
    }

    private static func urlOverrideOrInfoPlist(overrideKey: String, infoKey: String, fallback: String) -> URL {
        if let raw = UserDefaults.standard.string(forKey: overrideKey) {
            let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if !trimmed.isEmpty, let url = URL(string: trimmed) {
                return url
            }
        }
        return urlFromInfoPlist(key: infoKey, fallback: fallback)
    }

    private static func saveURLOverride(_ raw: String, key: String) {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            UserDefaults.standard.removeObject(forKey: key)
        } else {
            UserDefaults.standard.set(trimmed, forKey: key)
        }
    }

    private static func urlFromInfoPlist(key: String, fallback: String) -> URL {
        if let raw = Bundle.main.object(forInfoDictionaryKey: key) as? String {
            let t = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if !t.isEmpty, let u = URL(string: t) { return u }
        }
        return URL(string: fallback)!
    }
}
