import SwiftUI

// MARK: - Profile Motion Kit (DS-4 · parity web design-system/motion + legacy profileMotion)

enum ProfileMotion {
    static let staggerStep = TodayFlowTheme.Motion.staggerCardPick

    static func staggerDelay(index: Int, base: Double = 0) -> Double {
        base + Double(index) * staggerStep
    }
}

struct ProfileMotionRevealModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let delay: Double
    @State private var visible = false

    func body(content: Content) -> some View {
        content
            .opacity(visible ? 1 : 0)
            .offset(y: visible ? 0 : 12)
            .onAppear {
                guard !reduceMotion else {
                    visible = true
                    return
                }
                withAnimation(TodayFlowTheme.Motion.revealEase.delay(delay)) {
                    visible = true
                }
            }
    }
}

struct ProfileMotionHeroSymbolModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var visible = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(visible ? 1 : 0.94)
            .opacity(visible ? 1 : 0)
            .onAppear {
                guard !reduceMotion else {
                    visible = true
                    return
                }
                withAnimation(TodayFlowTheme.Motion.cardSpring.delay(0.06)) {
                    visible = true
                }
            }
    }
}

/// Settle — slight drop + spring stop (FOUNDATION_UI §7 · web `MotionSettle`).
struct ProfileMotionSettleModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let delay: Double
    @State private var visible = false

    func body(content: Content) -> some View {
        content
            .opacity(visible ? 1 : 0)
            .offset(y: visible ? 0 : -10)
            .onAppear {
                guard !reduceMotion else {
                    visible = true
                    return
                }
                withAnimation(TodayFlowTheme.Motion.cardSpring.delay(delay)) {
                    visible = true
                }
            }
    }
}

extension View {
    func profileMotionReveal(delay: Double = 0) -> some View {
        modifier(ProfileMotionRevealModifier(delay: delay))
    }

    func profileMotionHeroSymbol() -> some View {
        modifier(ProfileMotionHeroSymbolModifier())
    }

    func profileMotionSettle(delay: Double = 0) -> some View {
        modifier(ProfileMotionSettleModifier(delay: delay))
    }
}
