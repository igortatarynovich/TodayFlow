//
//  ContentView.swift
//  TodayFlow
//

import SwiftUI

enum AppTab: Hashable {
    case today
    case questions
    case compatibility
    case calendar
    case profile
    case practices
}

/// Разбор `href` из API (полный URL фронта или путь `/…`) для нативной маршрутизации без WebView.
private enum AppDeepLink {
    static func normalizedPath(from href: String) -> String? {
        let t = href.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty else { return nil }

        if let url = URL(string: t), let scheme = url.scheme?.lowercased(), scheme == "http" || scheme == "https" {
            guard let hrefHost = url.host?.lowercased() else { return nil }
            let baseHost = AppConfig.webBaseURL.host?.lowercased() ?? ""
            let hostsMatch = hrefHost == baseHost
                || (Set([hrefHost, baseHost]) == Set(["localhost", "127.0.0.1"]))
            guard hostsMatch else { return nil }

            var path = url.path
            if path.isEmpty { path = "/" }
            if let q = url.query, !q.isEmpty { path += "?\(q)" }
            return path
        }

        if t.hasPrefix("/") { return t }
        if t.contains("://") { return nil }
        return "/" + t
    }
}

struct ContentView: View {
    let store: TodayFlowStore
    @State private var initialTabAfterSummary: AppTab = .today

    var body: some View {
        Group {
            if !store.isAuthenticated {
                AuthView(store: store)
            } else if store.hasCompletedOnboarding {
                if store.hasSeenProfileSummary {
                    MainTabShellView(store: store, initialTab: initialTabAfterSummary)
                } else {
                    ProfileSummaryView(store: store) { targetTab in
                        initialTabAfterSummary = targetTab
                        store.markProfileSummarySeen()
                    }
                }
            } else {
                OnboardingView(store: store)
            }
        }
        .task {
            await store.resumeSessionIfNeeded()
        }
        // После онбординга `resume` уже мог отработать до появления birthProfile — добиваем AstroProfile на сервере.
        .task(id: store.hasCompletedOnboarding) {
            guard store.isAuthenticated, store.hasCompletedOnboarding else { return }
            await store.syncCoreSetupFromBirthProfileIfNeeded()
        }
    }
}

private struct MainTabShellView: View {
    let store: TodayFlowStore
    let initialTab: AppTab

    @State private var selectedTab: AppTab
    @State private var isProfileSummaryPresented = false
    @State private var practicesPath = NavigationPath()
    @State private var openPracticesHistory = false
    @State private var openPracticeIdFromDeepLink: String?

    init(store: TodayFlowStore, initialTab: AppTab = .today) {
        self.store = store
        self.initialTab = initialTab
        _selectedTab = State(initialValue: initialTab)
    }

    var body: some View {
        // Порядок как на веб: Сегодня → Flow → Профиль → Совместимость → Guidance
        TabView(selection: $selectedTab) {
            TodayView(
                store: store,
                onOpenProfileSummaryRoute: { tab in
                    selectedTab = tab
                },
                onSelectTab: { tab in
                    selectedTab = tab
                }
            )
                .tabItem {
                    Label(TodayMainTabCopy.today, systemImage: "sun.max.fill")
                }
                .tag(AppTab.today)

            NavigationStack {
                CalendarView(store: store, onOpenGoals: {
                    selectedTab = .calendar
                })
            }
            .tabItem {
                Label(TodayMainTabCopy.flow, systemImage: "calendar")
            }
            .tag(AppTab.calendar)

            ProfileView(
                store: store,
                onOpenCompatibility: {
                    selectedTab = .compatibility
                },
                onOpenProfileSummaryRoute: { tab in
                    selectedTab = tab
                }
            )
            .tabItem {
                Label(TodayMainTabCopy.profile, systemImage: "person.crop.circle.fill")
            }
            .tag(AppTab.profile)

            CompatibilityView(
                store: store,
                onOpenProfile: { selectedTab = .profile },
                onOpenGuidance: { selectedTab = .questions }
            )
            .tabItem {
                Label(TodayMainTabCopy.compatibility, systemImage: "person.2.fill")
            }
            .tag(AppTab.compatibility)

            TarotHubView(store: store)
            .tabItem {
                Label(TodayMainTabCopy.tarot, systemImage: "rectangle.on.rectangle.angled")
            }
            .tag(AppTab.questions)

            PracticesRootView(
                path: $practicesPath,
                openHistoryFromDeepLink: $openPracticesHistory,
                openPracticeIdFromDeepLink: $openPracticeIdFromDeepLink,
                userId: store.authSession?.userID,
                isPaidSubscriber: store.authSession?.isPaid ?? false,
                isAuthenticated: store.isAuthenticated
            )
            .tabItem {
                Label(TodayMainTabCopy.practices, systemImage: "figure.mind.and.body")
            }
            .tag(AppTab.practices)
        }
        .tint(TodayFlowTheme.accent)
        .task {
            async let trackerBootstrap: Void = store.bootstrapTrackerIfNeeded()
            async let coreSetupSync: Void = store.syncCoreSetupFromBirthProfileIfNeeded()
            _ = await (trackerBootstrap, coreSetupSync)
        }
        .onChange(of: store.pendingHrefRoute) { _, href in
            guard let href else { return }
            route(to: href)
            store.pendingHrefRoute = nil
        }
        .sheet(isPresented: $isProfileSummaryPresented) {
            ProfileSummaryView(store: store) { tab in
                isProfileSummaryPresented = false
                selectedTab = tab
            }
        }
    }

    /// Нативная навигация по тем же маршрутам, что на вебе; всё без `WKWebView`.
    private func route(to href: String) {
        guard let fullPath = AppDeepLink.normalizedPath(from: href) else {
            selectedTab = .today
            return
        }
        let path = fullPath.lowercased()

        if path == "/" || path.hasPrefix("/today") {
            selectedTab = .today
            return
        }
        if path.hasPrefix("/guidance") || path.hasPrefix("/tarot") || path.hasPrefix("/questions") {
            selectedTab = .questions
            return
        }
        if path.hasPrefix("/compatibility") || path.hasPrefix("/account/compatibility") {
            selectedTab = .compatibility
            return
        }
        if path.hasPrefix("/flow")
            || path.hasPrefix("/tracking/calendar") || path.hasPrefix("/calendar") || path.hasPrefix("/asceticisms/tracker")
            || path.hasPrefix("/affirmations/tracker") {
            selectedTab = .calendar
            return
        }
        if path.hasPrefix("/tracking/progress") || path.hasPrefix("/maps") || path.hasPrefix("/habits") {
            selectedTab = .profile
            if path.hasPrefix("/maps/mood") || path == "/maps/mood" {
                store.requestMapNavigation(.mood)
            } else if path.hasPrefix("/maps/energy") {
                store.requestMapNavigation(.energy)
            } else if path.hasPrefix("/maps/promise") {
                store.requestMapNavigation(.promise)
            } else if path.hasPrefix("/maps/ascetic") {
                store.requestMapNavigation(.ascetic)
            } else if path.hasPrefix("/maps/wish") {
                store.requestMapNavigation(.wish)
            } else if path.hasPrefix("/maps/relationship") {
                store.requestMapNavigation(.relationship)
            } else if path.hasPrefix("/maps/tarot") {
                store.requestMapNavigation(.tarot)
            } else if path.hasPrefix("/habits") {
                store.requestMapNavigation(.habits)
            } else {
                store.requestMapNavigation(.hub)
            }
            return
        }
        if path.hasPrefix("/tracking") {
            selectedTab = .calendar
            return
        }
        if path.hasPrefix("/natal-chart") || path.hasPrefix("/birth-chart") {
            selectedTab = .profile
            store.profileNatalScrollToken = UUID()
            return
        }
        if path.hasPrefix("/profile") {
            selectedTab = .profile
            if fullPath.contains("section=chart") {
                store.profileNatalScrollToken = UUID()
            }
            return
        }
        if path.hasPrefix("/profile-summary") {
            isProfileSummaryPresented = true
            return
        }
        if path.hasPrefix("/account") {
            selectedTab = .profile
            return
        }
        if path.hasPrefix("/weekly") || path.hasPrefix("/dashboard/weekly") || path.hasPrefix("/growth")
            || path.hasPrefix("/goals") {
            selectedTab = .calendar
            return
        }
        if path.hasPrefix("/practices") {
            selectedTab = .practices
            if path.contains("/history") {
                openPracticesHistory = true
            } else if let id = practiceIdFromPath(path) {
                openPracticeIdFromDeepLink = id
            }
            return
        }

        selectedTab = .today
    }

    private func practiceIdFromPath(_ path: String) -> String? {
        let trimmed = path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        let parts = trimmed.split(separator: "/").map(String.init)
        guard parts.count >= 2, parts[0] == "practices" else { return nil }
        let id = parts[1]
        if id == "history" { return nil }
        return id.isEmpty ? nil : id
    }
}

#Preview {
    ContentView(store: TodayFlowStore())
}
