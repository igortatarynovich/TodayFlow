import SwiftUI

@main
struct TodayFlowApp: App {
    @State private var store = TodayFlowStore()

    var body: some Scene {
        WindowGroup {
            ContentView(store: store)
                .onOpenURL { url in
                    store.openHref(url.absoluteString)
                }
        }
    }
}
